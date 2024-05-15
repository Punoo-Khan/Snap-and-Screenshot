import pyaudio
import scipy.fftpack as sf
import numpy as np
import time
from screen_shot import take_screenshot, show_notification, generate_filename

FORMAT = pyaudio.paInt16 #uses a 16 digit system to communicate
CHANNELS = 1 #number of audio channels
RATE = 48000 #  the number of samples per second.
CHUNK = 2**10 # bytes of sound it will take from actual audio
class SnappingDetector(object):
    def __init__(self):
        self.x = sf.fftfreq(CHUNK, 1.0/RATE)[:int(CHUNK/2)] #this will take chunck bytes at 1/rate seconds and we are only taking the first half since second one is mirror to first acc fourier theorem
        self.audio = pyaudio.PyAudio() #create an instance pyaudio class to access audio input
        self.preDetect = -1 #used to detect snap
        self.lastMeans = [0] #used to have mean amplitude for smoothing
        self.i = 0

    def start(self, device):
        self.stream = self.audio.open(
            input=True,
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input_device_index=device,
            frames_per_buffer=CHUNK,
            stream_callback=self.callback)
        print("Starting detection...")
        self.stream.start_stream()

    def getDevices(self):
        devices = []
        for i in range(self.audio.get_device_count()):
            devices.append(self.audio.get_device_info_by_index(i))
        return devices

    def on_snap_detected(self):
        filename = generate_filename()
        take_screenshot(filename)
        show_notification("Snap Screenshot", f"Screenshot taken: {filename}")

    def callback(self, in_data, frame_count, time_info, status):
        result = sf.fft(np.frombuffer(in_data, dtype=np.int16)) #converts the data at first in int16 then fourier
        self.y = np.abs(result)[:int(CHUNK/2)] #explained above
        mean = np.mean(self.y)
        var = np.var(self.y)
        meansMean = np.mean(self.lastMeans)
        freqMean = np.mean(self.x * self.y) / mean # used to identify dominant frequency in the sound

        if self.preDetect == -1:
            if 8000 < freqMean < 12000 and 10.0*meansMean < mean and 5000 < mean and 200000000 < var:
                self.preDetect = mean
                self.preDetectTime = time.time()
                print(f"Frequency Mean: {freqMean}, Mean: {mean}, Variance: {var}")
        elif self.preDetectTime + 0.2 < time.time():
            if mean < self.preDetect:
                self.i+=1
                print('Snap detected!', self.i)
                self.on_snap_detected()
            self.preDetect = -1

        if len(self.lastMeans) >= 10:
            self.lastMeans.pop(0)
        self.lastMeans.append(mean)

        return (None, pyaudio.paContinue)

if __name__ == '__main__':
    sd = SnappingDetector()
    for i, device in enumerate(sd.getDevices()):
        print(i, device['name'])
    device = int(input('Input device ID > '))
    sd.start(device)
    input("Press Enter to stop...")
    sd.stream.stop_stream()
    sd.stream.close()
    sd.audio.terminate()
