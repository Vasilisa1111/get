import time
import signal_generator
from r2r_dac import R2R_DAC


def main():
    # Параметры R2R ЦАП
    gpio_pins = [16, 20, 21, 25, 26, 17, 27, 22]  # MSB -> LSB
    dynamic_range = 3.185                         # Максимальное напряжение R2R ЦАП (В)

    # Параметры генерируемого сигнала
    signal_frequency = 20.0      # Частота синуса (Гц)
    sampling_frequency = 1000.0  # Частота дискретизации (Гц)
    amplitude = 3.185           # Желаемая амплитуда сигнала (В)

    # Инициализация ЦАП
    dac = R2R_DAC(gpio_bits=gpio_pins, dynamic_range=dynamic_range, verbose=False)

    print(f"Запущена генерация синусоиды на R2R ЦАП:")
    print(f"-Частота синуса: {signal_frequency} Гц")
    print(f"-Частота дискретизации: {sampling_frequency} Гц")
    print(f"Для остановки нажмите Ctrl+C\n")

    start_time = time.time()

    try:
        while True:
            # Текущее время с начала старта
            current_time = time.time() - start_time

            # 1. Вычисляем нормированную амплитуду (0.0 .. 1.0)
            norm_amp = signal_generator.get_sin_wave_amplitude(signal_frequency, current_time)

            # 2. Переводим в напряжение (0.0 .. amplitude В)
            voltage = norm_amp * amplitude

            digital_code=int((voltage/dynamic_range)*255)

            digital_code = max(0,min(255,digital_code))

            # 3. Выдаем напряжение на ЦАП
            dac.set_voltage(voltage)

            # 4. Выдерживаем шаг дискретизации
            signal_generator.wait_for_sampling_period(sampling_frequency)

    except KeyboardInterrupt:
        print("\nГенерация синусоиды остановлена.")
    finally:
        dac.deinit()


if __name__ == "__main__":
    main()