# ===============================
# QMCTB-03 (v6.6 FINAL)
# EMPIRICAL SMD SCALING + ERROR BARS
# ===============================

import numpy as np
import matplotlib.pyplot as plt
import os, time

# -------------------------------
# CONFIG
# -------------------------------
N = 512
N_AVG = 10
N_RUNS = 5            # 🔥 error bars
GLOBAL_SEED = 42

L = 5e-3
dx = L / N

lam = 532e-9
z = 0.05

BIN_SIZES = np.arange(2, 65, 2)
D_VALUES  = np.arange(100e-6, 501e-6, 50e-6)

V_THRESHOLD = 0.75

os.makedirs("artifacts", exist_ok=True)

# -------------------------------
# CORE
# -------------------------------
def fresnel_2D(E):
    fx = np.fft.fftfreq(N, d=dx)
    FX, FY = np.meshgrid(fx, fx)
    factor = np.clip(1 - (lam*FX)**2 - (lam*FY)**2, 0, None)
    H = np.exp(1j * 2*np.pi*z/lam * np.sqrt(factor))
    return np.fft.ifft2(np.fft.fft2(E) * H)

def far_field(E):
    I = np.abs(np.fft.fftshift(np.fft.fft2(E)))**2
    return I / (I.max() + 1e-12)

def add_noise(I, rng):
    shot = rng.poisson(I * 300) / 300
    read = rng.normal(0, 0.01, size=I.shape)
    return np.clip(shot + read, 0, None)

def pixel_bin(I, b):
    s = (I.shape[0] // b) * b
    if s < b:
        return None
    return I[:s,:s].reshape(s//b, b, s//b, b).mean(axis=(1,3))

def compute_visibility(I):
    Nb = I.shape[0]
    if Nb < 10:
        return 0.0
    c = Nb // 2
    w = max(2, Nb // 6)
    line = I[c, c-w:c+w]
    if len(line) < 3:
        return 0.0
    line = np.convolve(line, np.ones(3)/3, mode='same')
    vmax, vmin = line.max(), line.min()
    return (vmax - vmin) / (vmax + vmin + 1e-12)

# -------------------------------
# SYSTEM
# -------------------------------
def build_system(d):
    x = np.linspace(-L/2, L/2, N)
    X, Y = np.meshgrid(x, x)

    E_source = np.exp(-(X**2 + Y**2) / (0.6e-3)**2)

    a = 40e-6
    aperture = (
        (np.abs(X + d/2) < a/2) |
        (np.abs(X - d/2) < a/2)
    ).astype(float)

    return fresnel_2D(E_source * aperture)

# -------------------------------
# VISIBILITY
# -------------------------------
def compute_V0(E_det, b, seed):

    rng = np.random.default_rng(seed)
    I_accum = None

    for _ in range(N_AVG):

        I = far_field(E_det)
        I_b = pixel_bin(I, b)
        if I_b is None:
            return None

        I_b = add_noise(I_b, rng)
        I_accum = I_b if I_accum is None else I_accum + I_b

    I_avg = I_accum / N_AVG
    I_avg /= (I_avg.max() + 1e-12)

    return compute_visibility(I_avg)

# -------------------------------
# MAIN
# -------------------------------
def main():

    print("\n=== QMCTB-03 v6.6 FINAL ===\n")

    d_list = []
    B_mean = []
    B_std  = []

    for d in D_VALUES:

        print(f"d = {int(d*1e6)} µm", end="  ")

        E_det = build_system(d)

        B_runs = []

        for run in range(N_RUNS):

            valid_bins = []

            for b in BIN_SIZES:

                V0 = compute_V0(E_det, b, GLOBAL_SEED + run)
                if V0 is None:
                    continue

                if V0 >= V_THRESHOLD:
                    valid_bins.append(b)

            if len(valid_bins) > 0:
                B_runs.append(max(valid_bins))

        if len(B_runs) > 0:

            B_runs = np.array(B_runs)

            d_list.append(d)
            B_mean.append(B_runs.mean())
            B_std.append(B_runs.std())

            nyq = lam*z/(dx*d)
            print(f"B={B_runs.mean():.1f}±{B_runs.std():.1f} (Nyq≈{nyq:.1f})")

        else:
            print("no valid bin")

    d_arr = np.array(d_list)
    B_mean = np.array(B_mean)
    B_std  = np.array(B_std)

    # -------------------------------
    # FIT
    # -------------------------------
    b_exp, logA = np.polyfit(np.log(d_arr), np.log(B_mean), 1)
    A = np.exp(logA)

    print(f"\n🔥 FINAL exponent b = {b_exp:.3f}")

    # -------------------------------
    # PLOT
    # -------------------------------
    plt.figure(figsize=(6,5))

    plt.errorbar(d_arr*1e6, B_mean, yerr=B_std, fmt='o', capsize=4, label="B_min ± std")

    d_fit = np.linspace(d_arr.min(), d_arr.max(), 200)
    plt.plot(d_fit*1e6, A * d_fit**b_exp, '--', label=f"fit b={b_exp:.2f}")

    plt.plot(d_fit*1e6, lam*z/(dx*d_fit), ':', label="Nyquist")

    plt.xlabel("Slit separation d (µm)")
    plt.ylabel("Minimum bin size B_min")
    plt.title("QMCTB-03 Final Scaling (v6.6)")
    plt.legend()
    plt.grid(alpha=0.3)

    filename = f"artifacts/smd_v66_{int(time.time())}.png"
    plt.savefig(filename, dpi=300)
    plt.show()

    print(f"\nSaved → {filename}")

# -------------------------------
if __name__ == "__main__":
    main()
