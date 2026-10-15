import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-3, 7, 2000)
y = np.exp(-x) * np.sin(x)
env_upper = np.exp(-x)
env_lower = -np.exp(-x)

plt.figure(figsize=(10, 6))

# График функции и огибающие
plt.plot(x, y, "b-", label=r"$y = e^{-x} \sin x$", linewidth=1.5)
plt.plot(
    x, env_upper, "r--", alpha=0.5, label=r"Огибающие $y = \pm e^{-x}$"
)
plt.plot(x, env_lower, "r--", alpha=0.5)

# Оформление
plt.axhline(0, color="black", linewidth=0.8)
plt.axvline(0, color="black", linewidth=0.8)
plt.ylim(-5, 5)
plt.xlim(-3, 7)
plt.grid(True, alpha=0.3)
plt.title(r"График функции $y = e^{-x} \sin x$")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()

plt.show()