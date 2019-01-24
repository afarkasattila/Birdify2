from matplotlib import pyplot
from numpy import zeros, shape, absolute, amax, uint8, arange, flipud, mean, sqrt, iinfo, int16, float32, linspace
from PIL import Image
from scipy.io import wavfile
from scipy.signal import spectrogram, get_window
import numpy as np

PATH = "soundsamples"

def pow2(n):
    '''checks if n is the power of 2'''
    if(n == 2):
        return True
    elif(n % 2 == 0):
        return pow2(n//2)
    else:
        return False


class WavPreprocessor():
    '''Performs preprocessing on a wav file

    Performs STFT on a wav file, will not work with any other extension,
    cuts the sound into len_seconds length parts,
    then performs stft on each of those, and makes them into images'''

    def __init__(self, window=448, noverlap=224, len_seconds=3, sample_rate=44100, gamma=0.5):
        self.win_size = window
        self.noverlap = noverlap
        self.len_seconds = len_seconds
        self.sample_rate = sample_rate
        self.gamma = gamma


    def _adjust_wav_size(self, array):
        if(array.shape[0] < self.len_seconds * self.sample_rate):
            #if it's too short
            return None
        else:
            array = array[:self.len_seconds * self.sample_rate]
        return array


    def set_wav(self, name_with_path):
        _, self.wav = wavfile.read(name_with_path)
        if len(self.wav.shape) > 1:
            # we know it has more than 1 channels
            self.wav = mean(self.wav, axis=1, dtype=self.wav.dtype)


    def get_spectrogram(self, array, window_type="hamming"):
        _, _, spec_array = spectrogram(array, self.sample_rate, get_window(window_type, self.win_size),
                                      nperseg=self.win_size, noverlap=self.noverlap, axis=0, mode="magnitude")
        return spec_array[:-1,:]


    def _normalize_data(self, array):
        #normalizing data
        _max = amax(array)
        if(_max == 0):
            return None
        array = array / _max
        return array


    def check_square_mean(self, array, threshold):
        rms = sqrt(mean(array ** 2))
        return rms >= threshold


    def decimate_data(self, array, width):
        indices = linspace(0, array.shape[1]-1, width).astype(int16)
        return array[:, indices]


    def resize_save_spectrogram(self, height, width, spectrogram, name_with_path):
        spectrogram = self._normalize_data(spectrogram)
        spectrogram = self.decimate_data(spectrogram, width)
        #and the channels contain the same information
        #gets colormap
        spectrogram = spectrogram ** self.gamma
        if(spectrogram is not None):
            cm = pyplot.get_cmap("jet")
            im = Image.fromarray(uint8(cm(flipud(spectrogram))*255))
            im.save(name_with_path)


    def scale_data(self):
        self.wav = (self.wav / iinfo(self.wav.dtype).max).astype(float32)


    def perform_save_multiple_spectrograms(self, height, width, name_with_path, save_name_with_path,
                                           end_save_name, threshold):
        self.set_wav(name_with_path)
        self.scale_data()
        length = self.wav.shape[0]
        nr = 0

        for i in arange(0, length, self.len_seconds * self.sample_rate):
            #adjusts the size of the sound, then gets the spectrogram
            #and saves it on disk
            array = self._adjust_wav_size(self.wav[i:])
            if array is not None:
                if self.check_square_mean(array, threshold):
                    spectrogram = self.get_spectrogram(array)
                    self.resize_save_spectrogram(height, width, spectrogram, "%s_%d%s"%(save_name_with_path, nr, end_save_name))
                else:
                    print("Sound discarded", name_with_path, nr)
                nr += 1

