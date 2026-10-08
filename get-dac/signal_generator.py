import time
import numpy as np


def get_sin_wave_amplitude(freq, time):
    return (np.sin(2 * np.pi * freq * time) + 1.0) / 2.0


def wait_for_sampling_period(sampling_frequency):
    if sampling_frequency > 0:
        time.sleep(1.0 / sampling_frequency)