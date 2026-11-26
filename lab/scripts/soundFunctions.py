import numpy as np

R = 8.314
PA = 101325

TEMPS = [20, 22, 24, 26, 28, 30]
PW0 = [2336.8, 2642.4, 2982.4, 3360.0, 3778.5, 4241.7]

M_N2, M_O2, M_AR, M_CO2, M_H2O = 0.02801, 0.03200, 0.03995, 0.04401, 0.01802
I_N2, I_O2, I_AR, I_CO2, I_H2O = 5, 5, 3, 6, 6

X_N2, X_O2, X_AR = 0.7809, 0.2098, 0.0093


def h2oFraction(temperature, rh):
    pw0 = np.interp(temperature, TEMPS, PW0)
    return rh / 100 * pw0 / PA


def speedOfSound(temperature, h2oX, co2Max):
    T = temperature + 273.15
    co2 = np.linspace(0, co2Max / 100, 51)

    k = 1 - h2oX
    xN2 = X_N2 * k
    xO2 = (X_O2 - co2) * k
    xAr = X_AR * k
    xCO2 = co2 * k

    M = M_N2 * xN2 + M_O2 * xO2 + M_AR * xAr + M_CO2 * xCO2 + M_H2O * h2oX
    Cv = (I_N2 * xN2 + I_O2 * xO2 + I_AR * xAr + I_CO2 * xCO2 + I_H2O * h2oX) / 2 * R
    Cp = Cv + R

    soundSpeed = np.sqrt(Cp / Cv * R * T / M)
    return co2 * 100, soundSpeed


def findDelay(mic0, mic1, pre=50, post=250, noiseCount=200, k=5, nMin=700, nMax=1000):
    a = mic0 - np.mean(mic0[:noiseCount])
    b = mic1 - np.mean(mic1[:noiseCount])

    noise = np.std(a[:noiseCount])
    above = np.abs(a) > k * noise
    onset = int(np.argmax(above)) if np.any(above) else noiseCount
    start = max(onset - pre, 0)

    A = a[start:onset + post]
    maxA = np.max(np.abs(A))
    if maxA == 0:
        return 0, 0.002
    A = A / maxA

    bestN, bestErr = 0, np.inf
    upper = min(nMax, len(b) - (onset + post))
    for N in range(nMin, upper):
        B = b[start + N:onset + post + N]
        maxB = np.max(np.abs(B))
        if maxB == 0:
            continue
        B = B / maxB
        err = np.sum((A - B) ** 2)
        if err < bestErr:
            bestN, bestErr = N, err

    tau = bestN * 0.004 + 0.002
    return bestN, tau


def readConditions(path):
    values = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=")
                values[key.strip()] = float(value.split()[0])
    return values["Temperature"], values["Relative humidity"]