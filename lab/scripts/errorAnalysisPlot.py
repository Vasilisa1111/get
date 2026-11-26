import glob
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import soundFunctions as s

plt.rcParams["font.size"] = 16

baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataPath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(baseDir, "data")
plotsPath = os.path.join(baseDir, "plots")
os.makedirs(plotsPath, exist_ok=True)

L = 1.158
dTau_adc = 0.004 # шаг дискретизации АЦП, мс (4 мкс)
dT = 0.5         # погрешность температуры газа в трубе, °C
dRH = 5.0        # погрешность относительной влажности, %

t, rh = s.readConditions(os.path.join(dataPath, "conditions.txt"))
co2_fit, speedRoom_fit = s.speedOfSound(t, s.h2oFraction(t, rh), 5)
co2_fit, speedWet_fit = s.speedOfSound(t, s.h2oFraction(t, 100), 5)
fitRoom = np.polyfit(speedRoom_fit, co2_fit, 1)
fitWet = np.polyfit(speedWet_fit, co2_fit, 1)


def read_series(prefix, fit):
    taus = []
    for file0 in sorted(glob.glob(os.path.join(dataPath, prefix + "*_0.txt"))):
        name = os.path.basename(file0)[:-len("_0.txt")]
        mic0 = np.loadtxt(os.path.join(dataPath, name + "_0.txt"))
        mic1 = np.loadtxt(os.path.join(dataPath, name + "_1.txt"))
        _, tau = s.findDelay(mic0, mic1)
        taus.append(tau)
    taus = np.array(taus)
    tau_mean = np.mean(taus)
    c_mean = L / (tau_mean / 1000)
    co2_mean = np.polyval(fit, c_mean)

    dTau_rand = np.std(taus, ddof=1) / np.sqrt(len(taus))
    dC_rand = c_mean * dTau_rand / tau_mean
    dCO2_rand = abs(fit[0]) * dC_rand
    return tau_mean, c_mean, co2_mean, dCO2_rand


tauAir_m, cAir, co2Air, dCO2_air_rand = read_series("air", fitRoom)
tauBr_m, cBr, co2Br, dCO2_br_rand = read_series("breath", fitWet)

# Приборные вклады в погрешность CO2 (%) без учёта ΔL
slope = abs(fitRoom[0])
dCO2_adc = slope * (cAir * dTau_adc / tauAir_m)

c0 = s.speedOfSound(t, s.h2oFraction(t, rh), 5)[1][0]
dCO2_T = slope * abs(s.speedOfSound(t + dT, s.h2oFraction(t + dT, rh), 5)[1][0] - c0)
dCO2_RH = slope * abs(s.speedOfSound(t, s.h2oFraction(t, rh + dRH), 5)[1][0] - c0)

# Полная погрешность (корень из суммы квадратов)
dCO2_sys = np.sqrt(dCO2_adc**2 + dCO2_T**2 + dCO2_RH**2)
dCO2_air_tot = np.sqrt(dCO2_air_rand**2 + dCO2_sys**2)
dCO2_br_tot = np.sqrt(dCO2_br_rand**2 + dCO2_sys**2)

print(f"Воздух: CO2 = {co2Air:.2f} ± {dCO2_air_rand:.2f} % (случ.), ± {dCO2_air_tot:.2f} % (полн.)")
print(f"Выдох:  CO2 = {co2Br:.2f} ± {dCO2_br_rand:.2f} % (случ.), ± {dCO2_br_tot:.2f} % (полн.)")
print(f"Вклады: АЦП={dCO2_adc:.2f}%, T={dCO2_T:.2f}%, RH={dCO2_RH:.2f}%")

# --- График: вклад каждого источника погрешности ---
sources = [
    f"Влажность (ΔRH = {dRH:.0f} %)",
    f"Температура (Δt = {dT:.1f} °C)",
    "Разброс опытов (воздух)",
    f"Шаг АЦП (Δτ = {dTau_adc*1000:.0f} мкс)",
    "Разброс опытов (выдох)",
]
values = [dCO2_RH, dCO2_T, dCO2_air_rand, dCO2_adc, dCO2_br_rand]
colors = ["#94a3b8", "#60a5fa", "tab:green", "#f59e0b", "tab:red"]

fig, ax = plt.subplots(figsize=(11, 5.5))
bars = ax.barh(sources, values, color=colors, alpha=0.88)
for bar, val in zip(bars, values):
    ax.text(val + 0.03, bar.get_y() + bar.get_height() / 2, f"{val:.2f} %",
            va="center", fontsize=15, fontweight="bold")

ax.set_xlim(0, max(values) * 1.25)
ax.set_xlabel("Вклад в погрешность ΔCO₂, %")
ax.set_title("Источники погрешности метода")
ax.grid(axis="x")

plt.tight_layout()
plt.savefig(os.path.join(plotsPath, "error-analysis.png"), dpi=150, bbox_inches="tight")
plt.show()