import glob
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import soundFunctions as s

plt.rcParams["font.size"] = 16

baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plotsPath = os.path.join(baseDir, "plots")
os.makedirs(plotsPath, exist_ok=True)

# Можно запускать:
#   py scripts/soundView.py           -> все файлы из data/
#   py scripts/soundView.py data1     -> все файлы из data1/
#   py scripts/soundView.py air1      -> открыть конкретную запись с лупой
if len(sys.argv) == 1:
    mode = "all"
    dataPath = os.path.join(baseDir, "data")
elif os.path.isdir(sys.argv[1]):
    mode = "all"
    dataPath = sys.argv[1]
else:
    mode = sys.argv[1]
    dataPath = sys.argv[2] if len(sys.argv) > 2 else os.path.join(baseDir, "data")


def load_record(name):
    mic0_raw = np.loadtxt(os.path.join(dataPath, name + "_0.txt"))
    mic1_raw = np.loadtxt(os.path.join(dataPath, name + "_1.txt"))
    N, tau = s.findDelay(mic0_raw, mic1_raw)

    mic0 = mic0_raw - np.mean(mic0_raw[:200])
    mic1 = mic1_raw - np.mean(mic1_raw[:200])

    time0 = np.arange(len(mic0)) * 0.004
    time1 = np.arange(len(mic1)) * 0.004 + 0.002
    return time0, mic0, time1, mic1, N, tau


def save_single(name, show=False):
    time0, mic0, time1, mic1, N, tau = load_record(name)
    print(f"{name:10s} N = {N}, tau = {tau:.3f} мс")

    plt.figure(figsize=(11, 5.5))
    plt.plot(time0, mic0, linewidth=1.6, label="Микрофон 0")
    plt.plot(time1, mic1, linewidth=1.6, label="Микрофон 1")
    plt.xlabel("Время, мс")
    plt.ylabel("Сигнал АЦП (минус фон)")
    plt.title(f"{name}: N = {N}, τ = {tau:.3f} мс")
    plt.grid()
    plt.legend(fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(plotsPath, f"{name}.png"), dpi=150, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()


def save_group(prefix, title_ru):
    files = sorted(glob.glob(os.path.join(dataPath, prefix + "*_0.txt")))
    if not files:
        return

    fig, axes = plt.subplots(len(files), 1, figsize=(12, 3.6 * len(files)), sharex=True)
    axes = np.atleast_1d(axes)

    for ax, file0 in zip(axes, files):
        name = os.path.basename(file0)[:-len("_0.txt")]
        time0, mic0, time1, mic1, N, tau = load_record(name)
        ax.plot(time0, mic0, linewidth=1.4, label="Микрофон 0")
        ax.plot(time1, mic1, linewidth=1.4, label="Микрофон 1")
        ax.set_ylabel("Код АЦП")
        ax.set_title(f"{name}: N = {N}, τ = {tau:.3f} мс")
        ax.grid()
        ax.legend(loc="upper right", fontsize=13)

    axes[-1].set_xlabel("Время, мс")
    fig.suptitle(title_ru, fontsize=18, y=1.01)
    plt.tight_layout()
    plt.savefig(os.path.join(plotsPath, f"mics-{prefix}.png"), dpi=150, bbox_inches="tight")
    plt.close()


if mode == "all":
    files = sorted(glob.glob(os.path.join(dataPath, "*_0.txt")))
    for file0 in files:
        name = os.path.basename(file0)[:-len("_0.txt")]
        save_single(name, show=False)

    save_group("air", "Сигналы двух микрофонов — воздух")
    save_group("breath", "Сигналы двух микрофонов — выдох")
    print(f"Готово! Сохранено одиночных графиков: {len(files)} + сводные mics-air.png и mics-breath.png")
else:
    save_single(mode, show=True)