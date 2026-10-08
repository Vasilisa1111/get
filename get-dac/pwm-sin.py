import pwm_dac as pwm
import signal_generator as sg
import time




if __name__ == "__main__":
    amplitude = 3.185           
    signal_frequency = 20       
    sampling_frequency = 100   
    try:        
        dac = pwm.PWM_DAC(12, 1000, 3.185, False)

        start_time = time.time()

        while True:
            
            current_time = time.time() - start_time

            
            norm_value = sg.get_sin_wave_amplitude(signal_frequency, current_time)

            voltage = norm_value * amplitude

            dac.set_voltage(voltage)

            sg.wait_for_sampling_period(sampling_frequency)
    except KeyboardInterrupt:
            print("\nГенерация синусоиды остановлена")
    finally:
        dac.deinit()

