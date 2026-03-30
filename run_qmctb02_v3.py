
"""
QMCTB-02 FINAL (v3 — production release)
Detector Coherence Transfer Function
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import curve_fit


# =========================================================
# CONFIG
# =========================================================
VISIBILITY_THRESHOLD = 0.8

SIGMA_MAX = np.pi
SIGMA_POINTS = 20
N_AVG = 80
N_REALISATIONS = 6

GLOBAL_SEED = 42

ARTIFACT_DIR = Path("artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# FIELD (DPI)
# =========================================================
λ = 532e-9
N = 512
L = 5e-3
dx = L / N

x = np.linspace(-L / 2, L / 2, N)
X, Y = np.meshgrid(x, x)

w0 = 0.6e-3
E_source = np.exp(-(X**2 + Y**2) / w0**2)
E_source /= np.max(np.abs(E_source))

d = 250e-6
a = 40e-6

aperture = (
    (np.abs(X + d / 2) < a / 2) |
    (np.abs(X - d / 2) < a / 2)
).astype(float)

E_after = E_source * aperture


def fresnel_2D(E, dx, lam, z):
    N_local = E.shape[0]

    fx = np.fft.fftfreq(N_local, d=dx)
    FX, FY = np.meshgrid(fx, fx)

    factor = 1 - (lam * FX)**2 - (lam * FY)**2
    factor = np.clip(factor, 0, None)

    H = np.exp(1j * 2 * np.pi * z / lam * np.sqrt(factor))

    return np.fft.ifft2(np.fft.fft2(E) * H)


E_det = fresnel_2D(E_after, dx, λ, z=0.05)


# =========================================================
# DETECTOR OPERATORS
# =========================================================
def far_field(E):
    I = np.abs(np.fft.fftshift(np.fft.fft2(E)))**2
    return I / (I.max() + 1e-12)


def pixel_bin(I, bin_size=4):
    N_local = I.shape[0]
    s = (N_local // bin_size) * bin_size

    I = I[:s, :s]

    return I.reshape(
        s // bin_size, bin_size,
        s // bin_size, bin_size
    ).mean(axis=(1, 3))


def add_noise(I, rng):
    shot = rng.poisson(I * 500) / 500
    read = rng.normal(0, 0.01, size=I.shape)

    return np.clip(shot + read, 0, None)


def compute_visibility(I):
    Nb = I.shape[0]
    c = Nb // 2
    w = Nb // 7

    left = max(0, c - w)
    right = min(Nb, c + w)

    line = I[c, left:right]

    # smoothing
    line = np.convolve(line, np.ones(3) / 3, mode='same')

    vmax = line.max()
    vmin = line.min()

    return (vmax - vmin) / (vmax + vmin + 1e-12)


# =========================================================
# SIMULATION
# =========================================================
def simulate_sigma(frames, sigma):
    runs = []

    for r in range(N_REALISATIONS):
        seed = GLOBAL_SEED + r + int(sigma * 1000)
        rng = np.random.default_rng(seed)

        I_accum = np.zeros((N // 4, N // 4))

        for _ in range(frames):
            if sigma == 0:
                E = E_det
            else:
                phase = np.exp(1j * sigma * rng.normal(size=(N, N)))
                E = E_det * phase

            I = far_field(E)
            I = pixel_bin(I)
            I = add_noise(I, rng)

            I_accum += I

        I_avg = I_accum / frames
        I_avg /= (I_avg.max() + 1e-12)

        runs.append(compute_visibility(I_avg))

    return np.mean(runs), np.std(runs)


# =========================================================
# SWEEP
# =========================================================
def run_sigma_sweep(frames):
    sigma_vals = np.linspace(0, SIGMA_MAX, SIGMA_POINTS)

    V_mean, V_std = [], []

    for σ in sigma_vals:
        V, s = simulate_sigma(frames, σ)
        V_mean.append(V)
        V_std.append(s)

    return sigma_vals, np.array(V_mean), np.array(V_std)


# =========================================================
# MODEL
# =========================================================
def sigmoid(sigma, V_low, V_high, k, sigma_c):
    x = k * (sigma - sigma_c)
    x = np.clip(x, -50, 50)

    return V_low + (V_high - V_low) / (1 + np.exp(x))


def fit_sigmoid(sigma_vals, V_mean):
    p0 = [V_mean[-1], V_mean[0], 5.0, 2.0]

    popt, pcov = curve_fit(
        sigmoid,
        sigma_vals,
        V_mean,
        p0=p0,
        maxfev=10000
    )

    perr = np.sqrt(np.diag(pcov))
    return popt, perr


def compute_r2(y, y_fit):
    ss_res = np.sum((y - y_fit)**2)
    ss_tot = np.sum((y - np.mean(y))**2)

    return 1 - ss_res / (ss_tot + 1e-12)


# =========================================================
# MAIN
# =========================================================
def main():

    print("\nQMCTB-02 FINAL (v3 — production release)\n")

    Vp, Vp_std = simulate_sigma(N_AVG, 0)
    Vd, Vd_std = simulate_sigma(N_AVG, np.pi)

    print(f"V(σ=0) = {Vp:.6f} ± {Vp_std:.6f}")
    print(f"V(σ=π) = {Vd:.6f} ± {Vd_std:.6f}")
    print(f"ΔV     = {Vp - Vd:.6f}")

    sigma_vals, V_mean, V_std = run_sigma_sweep(N_AVG)

    popt, perr = fit_sigmoid(sigma_vals, V_mean)
    V_low, V_high, k, sigma_c = popt
    dV_low, dV_high, dk, dsigma_c = perr

    sigma_dense = np.linspace(0, SIGMA_MAX, 300)
    V_fit = sigmoid(sigma_dense, *popt)

    r2 = compute_r2(V_mean, sigmoid(sigma_vals, *popt))

    print(f"\nσ_c    = {sigma_c:.6f} ± {dsigma_c:.6f} rad")
    print(f"k      = {k:.4f}  ± {dk:.4f}")
    print(f"V_high = {V_high:.6f} ± {dV_high:.6f}")
    print(f"V_low  = {V_low:.6f} ± {dV_low:.6f}")
    print(f"R²     = {r2:.6f}")

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.fill_between(
        sigma_vals,
        V_mean - V_std,
        V_mean + V_std,
        alpha=0.15
    )

    ax.plot(sigma_vals, V_mean, "o-", lw=1.8, label="Measured")
    ax.plot(sigma_dense, V_fit, "--", lw=2.0, label=f"Fit (R²={r2:.4f})")

    ax.axvline(sigma_c, linestyle="--", label="σ_c")
    ax.axhline(VISIBILITY_THRESHOLD, linestyle=":", label="Threshold")

    ax.set_xlabel("σ (detector phase noise, rad)")
    ax.set_ylabel("Visibility V")
    ax.set_title("QMCTB-02 — Detector Coherence Transfer Function")

    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()

    out = ARTIFACT_DIR / "qmctb02_final.png"
    plt.savefig(out, dpi=300)

    print(f"\nSaved → {out}")

    plt.show()


if __name__ == "__main__":
    main()
