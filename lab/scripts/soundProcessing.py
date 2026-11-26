import sys
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import soundFunctions as s

plt.rcParams["font.size"] = 16

baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataPath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(baseDir, "data")
plotsPath = os.path.join(baseDir, "plots")
os.makedirs(plotsPath, exist_ok=True)

L = 1.158

t, rh = s.readConditions(os.path.join(dataPath, "conditions.txt"))
print("t = %.1f C, rh = %.1f %%" % (t, rh))

# Коэффициенты прямых на участке 0..5 % CO2 (п4.5)
co2_fit, speedRoom_fit = s.speedOfSound(t, s.h2oFraction(t, rh), 5)
co2_fit, speedWet_fit = s.speedOfSound(t, s.h2oFraction(t, 100), 5)

fitRoom = np.polyfit(speedRoom_fit, co2_fit, 1)
fitWet = np.polyfit(speedWet_fit, co2_fit, 1)
print("Прямая, влажность аудитории:", fitRoom)
print("Прямая, влажность 100 %:", fitWet)

# --- График 1: только расчётные кривые для влажного воздуха (0..5 % CO2) ---
plt.figure(figsize=(10, 6.5))
plt.plot(co2_fit, speedRoom_fit, linewidth=2.5, label="влажность %.1f %%" % rh)
plt.plot(co2_fit, speedWet_fit, linewidth=2.5, label="влажность 100 %")
plt.title("Скорость звука во влажном воздухе (t = %.1f °C)" % t)
plt.xlabel("Доля CO₂ в сухом воздухе, %")
plt.ylabel("Скорость звука, м/с")
plt.grid()
plt.legend(fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(plotsPath, "speed-of-sound-theory.png"), dpi=150, bbox_inches="tight")


def delays(prefix):
    taus = []
    for file0 in sorted(glob.glob(os.path.join(dataPath, prefix + "*_0.txt"))):
        name = os.path.basename(file0)[:-len("_0.txt")]
        mic0 = np.loadtxt(os.path.join(dataPath, name + "_0.txt"))
        mic1 = np.loadtxt(os.path.join(dataPath, name + "_1.txt"))
        N, tau = s.findDelay(mic0, mic1)
        print("%-8s N = %d, tau = %.3f мс" % (name, N, tau))
        taus.append(tau)
    return np.array(taus)


tauAir = delays("air")
tauBreath = delays("breath")

cAir = L / (np.mean(tauAir) / 1000)
cBreath = L / (np.mean(tauBreath) / 1000)

co2Air = np.polyval(fitRoom, cAir)
co2Breath = np.polyval(fitWet, cBreath)

print("Воздух: c = %.1f м/с, CO2 = %.1f %%" % (cAir, co2Air))
print("Выдох:  c = %.1f м/с, CO2 = %.1f %%" % (cBreath, co2Breath))

for label, taus, fit in [("Воздух", tauAir, fitRoom), ("Выдох", tauBreath, fitWet)]:
    if len(taus) > 1:
        dTau = np.std(taus, ddof=1) / np.sqrt(len(taus))
        c = L / (np.mean(taus) / 1000)
        dC = c * dTau / np.mean(taus)
        print("%s: dtau = %.4f мс, dc = %.2f м/с, dCO2 = %.1f %%" % (label, dTau, dC, abs(fit[0]) * dC))

eta = (co2Breath / 100 - 0.0003) / 0.2095
print("Доля усвоенного кислорода: %.2f" % eta)

# --- График 2: итоговый график с измеренными точками ---
co2Max = max(5.0, np.ceil(max(co2Air, co2Breath) + 0.5))
co2, speedRoom = s.speedOfSound(t, s.h2oFraction(t, rh), co2Max)
co2, speedWet = s.speedOfSound(t, s.h2oFraction(t, 100), co2Max)

plt.figure(figsize=(10, 6.5))
lineRoom, = plt.plot(co2, speedRoom, linewidth=2.5, label="влажность %.1f %%" % rh)
plt.plot(co2, speedWet, linewidth=2.5, label="влажность 100 %")

if co2Air < 0:
    co2Ext = np.linspace(co2Air - 0.3, 0, 20)
    speedExt = (co2Ext - fitRoom[1]) / fitRoom[0]
    plt.plot(co2Ext, speedExt, "--", linewidth=2, color=lineRoom.get_color(), alpha=0.7)
    plt.axvline(0, color="gray", linestyle=":", linewidth=1.2)

plt.plot(co2Air, cAir, "*", markersize=18, label="Воздух: %.1f м/с, %.1f %%" % (cAir, co2Air))
plt.plot(co2Breath, cBreath, "*", markersize=18, label="Выдох: %.1f м/с, %.1f %%" % (cBreath, co2Breath))
plt.title("Скорость звука и доля CO₂ (t = %.1f °C)" % t)
plt.xlabel("Доля CO₂ в сухом воздухе, %")
plt.ylabel("Скорость звука, м/с")
plt.grid()
plt.legend(fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(plotsPath, "speed-of-sound.png"), dpi=150, bbox_inches="tight")

plt.show()