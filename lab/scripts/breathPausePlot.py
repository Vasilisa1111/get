import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import soundFunctions as s

plt.rcParams["font.size"] = 16

baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataPath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(baseDir, "data")
plotsPath = os.path.join(baseDir, "plots")

L = 1.158
t, rh = s.readConditions(os.path.join(dataPath, "conditions.txt"))
co2_fit, speedWet_fit = s.speedOfSound(t, s.h2oFraction(t, 100), 5)
fitWet = np.polyfit(speedWet_fit, co2_fit, 1)

# Опыты 1–4, соответствующие файлам breath1–breath4
names = ["breath1", "breath2", "breath3", "breath4"]
exhale_end = np.array([67, 66, 66, 66])   # с
clap_time  = np.array([71, 73, 73, 71])   # с
pauses = clap_time - exhale_end           # [4, 7, 7, 5] с

taus, speeds, co2s = [], [], []
for name in names:
    mic0 = np.loadtxt(os.path.join(dataPath, name + "_0.txt"))
    mic1 = np.loadtxt(os.path.join(dataPath, name + "_1.txt"))
    _, tau = s.findDelay(mic0, mic1)
    c = L / (tau / 1000)
    co2 = np.polyval(fitWet, c)
    taus.append(tau)
    speeds.append(c)
    co2s.append(co2)

taus = np.array(taus)
speeds = np.array(speeds)
co2s = np.array(co2s)

corr = np.corrcoef(pauses, co2s)[0, 1]
trend = np.polyfit(pauses, co2s, 1)
x_line = np.linspace(3.5, 7.5, 50)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.5, 6.5))

# --- Левый график: точки с подписями (имя, пауза, CO2) ---
ax1.scatter(pauses, co2s, s=120, zorder=4, label="Опыты breath1–breath4")
ax1.plot(x_line, np.polyval(trend, x_line), "--", linewidth=2, color="tab:orange",
         zorder=3, label=f"Тренд ({trend[0]:.2f} %/с, r = {corr:.2f})")

# Смещения и выравнивание, чтобы подписи не пересекали линию тренда и легенду
label_pos = {
    "breath1": ((0, -16),  "center", "top"),
    "breath2": ((12, 0),   "left",   "center"),
    "breath3": ((12, 0),   "left",   "center"),
    "breath4": ((12, 6),   "left",   "bottom"),
}
for name, p, y in zip(names, pauses, co2s):
    offset, ha, va = label_pos[name]
    ax1.annotate(
        f"{name}\n({p} с; {y:.1f} %)",
        (p, y),
        textcoords="offset points",
        xytext=offset,
        ha=ha,
        va=va,
        fontsize=13,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85),
        zorder=5,
    )

ax1.set_xlim(3.2, 8.7)
ax1.set_ylim(2.0, 8.8)
ax1.set_xlabel("Пауза от конца выдоха до хлопка, с")
ax1.set_ylabel("Доля CO₂ в выдохе, %")
ax1.set_title("Зависимость доли CO₂ от паузы до хлопка")
ax1.grid()
ax1.legend(loc="lower left", fontsize=13)

# --- Правый график: столбцы с подписями скорости и CO2 ---
bars = ax2.bar(names, speeds, color="tab:blue", alpha=0.8)
for bar, c, co2 in zip(bars, speeds, co2s):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        c + 0.12,
        f"{c:.1f} м/с\n({co2:.1f} %)",
        ha="center",
        va="bottom",
        fontsize=13,
        fontweight="bold",
    )

ax2.axhline(np.mean(speeds), color="tab:red", linestyle="--", linewidth=2,
            label=f"Среднее: {np.mean(speeds):.2f} м/с")
ax2.set_ylim(min(speeds) - 1.2, max(speeds) + 1.8)
ax2.set_ylabel("Скорость звука, м/с")
ax2.set_title("Скорость звука в отдельных выдохах")
ax2.grid(axis="y")
ax2.legend(loc="upper right", fontsize=14)

plt.tight_layout()
os.makedirs(plotsPath, exist_ok=True)
plt.savefig(os.path.join(plotsPath, "breath-pause.png"), dpi=150, bbox_inches="tight")
plt.show()