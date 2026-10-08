import mcp4725_driver as mcp
import signal_generator as sg
import time


def main():
    amplitude = 3.185             
    signal_frequency = 10       
    sampling_frequency = 1000   

    try:
        dac = mcp.MCP4725(4.2, verbose=False)
        print(f"Запущена генерация синусоиды на MCP4725:")
        print(f"-Частота синуса: {signal_frequency} Гц")
        print(f"-Частота дискретизации: {sampling_frequency} Гц")
        print(f"Для остановки нажмите Ctrl+C\n")
        start_time = time.time()

        while True:
            current_time = time.time() - start_time
            norm_value = sg.get_sin_wave_amplitude(signal_frequency, current_time)
            target_voltage = norm_value * amplitude
            
            dac.set_voltage(target_voltage)
            sg.wait_for_sampling_period(sampling_frequency)
    except KeyboardInterrupt:
        print("\nГенерация синусоиды остановлена.")
    finally:
        dac.deinit()
if __name__ == "__main__":
    main()