import time
import numpy as np
import RPi.GPIO as GPIO
import mcp3021_driver #[cite: 3]

# Настройки пинов и напряжений
CHARGE_PIN = 14
MAX_CHARGE_VOLTAGE = 3.26  # Реальное напряжение логической единицы GPIO (обычно около 3.26 - 3.3 В)
dynamic_range = 5.195      #[cite: 3]

# Инициализация GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(CHARGE_PIN, GPIO.OUT)

# Инициализация АЦП MCP3021
adc = mcp3021_driver.MCP3021(dynamic_range) #[cite: 3]

voltage_values = [] #[cite: 3]
time_values = []    #[cite: 3]

try:
    print("Начало эксперимента: Зарядка...")
    start_time = time.time()
    
    # Подаем напряжение на RC-цепь
    GPIO.output(CHARGE_PIN, 1)
    voltage = 0.0
    
    # Заряжаем до 95% от напряжения питания GPIO (~3.1 В)
    while voltage < 0.95 * MAX_CHARGE_VOLTAGE:
        voltage = adc.get_voltage() #[cite: 3]
        voltage_values.append(voltage) #[cite: 3]
        time_values.append(time.time() - start_time) #[cite: 3]
        
    print("Конденсатор заряжен. Начало разрядки...")
    # Отключаем питание, конденсатор начинает разряжаться через резистор
    GPIO.output(CHARGE_PIN, 0)
    
    # Разряжаем до 5% от напряжения (~0.16 В)
    while voltage > 0.05 * MAX_CHARGE_VOLTAGE:
        voltage = adc.get_voltage() #[cite: 3]
        voltage_values.append(voltage) #[cite: 3]
        time_values.append(time.time() - start_time) #[cite: 3]

    print("Эксперимент завершен. Сохранение данных...")
    
    # Объединение и сохранение по инструкции
    data = np.column_stack((time_values, voltage_values))
    np.savetxt('data.csv',
               data,
               delimiter=',',
               fmt='%.4f',
               header='Время[с],Напряжение[В]',
               comments='',
               encoding='utf-8')
    print("Файл data.csv успешно создан!")

finally:
    # Безопасный выход
    GPIO.output(CHARGE_PIN, 0)
    GPIO.cleanup()
    adc.deinit() #[cite: 3]