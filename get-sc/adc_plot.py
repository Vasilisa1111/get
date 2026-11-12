import numpy as np
import matplotlib.pyplot as plt

def plot_voltage_vs_time(time_data, voltage_data):
    # 1. Создание окна для отображения графика
    plt.figure(figsize=(10, 6))
    
    # 2. Размещение графика зависимости
    plt.plot(time_data, voltage_data, label='U(t)', color='blue', linewidth=2)
    
    # 3. Названия графика и осей
    plt.title('Процесс заряда и разряда RC-цепи\n(R = 1 МОм, C = 10 мкФ)')
    plt.xlabel('Время [с]')
    plt.ylabel('Напряжение [В]')
    
    # 4. Границы по осям X и Y (с небольшим отступом сверху)
    plt.xlim(min(time_data), max(time_data))
    plt.ylim(0, max(voltage_data) * 1.05)
    
    # 5. Включение сетки (основной и вспомогательной)
    plt.grid(which='major', linestyle='-', linewidth=0.7)
    plt.grid(which='minor', linestyle='--', linewidth=0.3)
    plt.minorticks_on()
    plt.legend()
    
    # 6. Сохранение графика в файл (вместо plt.show())
    plt.savefig('rc-plot.png', dpi=300)
    print("График успешно сохранен как rc-plot.png")

# Основная логика работы с файлом
if __name__ == '__main__':
    # Загружаем данные. skiprows=1 пропускает текстовый заголовок
    data = np.loadtxt('data.csv', delimiter=',', skiprows=1)
    
    # Разделяем столбцы
    time_col = data[:, 0]
    voltage_col = data[:, 1]
    
    # Вызываем функцию отрисовки
    plot_voltage_vs_time(time_col, voltage_col)