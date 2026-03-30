"""
QMCTB-02 FINAL STABLE
Detector Coherence Transfer Function Benchmark
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import curve_fit


# =========================================================
# CONFIG
# =========================================================
VISIBILITY_THRESHOLD = 0.8
SIGMA_MAX = 2 * np.pi
SIGMA_POINTS = 25
INITIAL_FRAMES = 10
N_REALISATIONS = 6

ARTIFACT_DIR = Path("qmctb/qmctb-02/artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# FIELD (DPI)
# =========================================================
λ = 532e-9
N = 512
L = 5e-3
dx = L / N

x = np.linspace(-L/2, L/2, N)
X, Y = np.meshgrid(x, x)

w0 = 0.6e-3
E_source = np.exp(-(X**2 + Y**2) / w0**2)
E_source /= np.max(np.abs(E_source))

d = 250e-6
a = 40e-6
aperture = ((np.abs(X + d/2) < a/2) | (np.abs(X - d/2) < a/2)).astype(float)
E_after = E_source * aperture


def fresnel_2D(E, dx, lam, z):
    fx = np.fft.fftfreq(N, d=dx)
    FX, FY = np.meshgrid(fx, fx)
    factor = np.maximum(0, 1 - (lam*FX)**2 - (lam*FY)**2)
    H = np.exp(1j * 2*np.pi*z/lam * np.sqrt(factor))
    return np.fft.ifft2(np.fft.fft2(E) * H)


E_det = fresnel_2D(E_after, dx, λ, z=0.05)


# =========================================================
# DETECTOR MODEL
# =========================================================
def far_field(E):
    return np.abs(np.fft.fftshift(np.fft.fft2(E)))**2


def pixel_bin(I, bin_size=4):
    s = (N // bin_size) * bin_size
    return I[:s, :s].reshape(
        N//bin_size, bin_size,
        N//bin_size, bin_size
    ).mean(axis=(1, 3))


def add_noise(I, rng):
    shot = rng.poisson(I * 500) / 500
    read = rng.normal(0, 0.01, size=I.shape)
    return np.clip(shot + read, 0, None)


def compute_visibility(I):
    Nb = I.shape[0]
    c = Nb // 2
    w = Nb // 7
    line = I[c, c-w:c+w]
    return (line.max() - line.min()) / (line.max() + line.min() + 1e-9)


# =========================================================
# SIMULATION
# =========================================================
def simulate_sigma(frames, sigma):
    runs = []

    for r in range(N_REALISATIONS):
        rng = np.random.default_rng(1000 + r)
        I_accum = np.zeros((N//4, N//4))

        for _ in range(frames):

            if sigma == 0:
                E = E_det
            else:
                phase = np.exp(1j * sigma * rng.normal(size=(N, N)))
                E = E_det * phase

            I = far_field(E)
            I /= I.max()
            I = pixel_bin(I)
            I = add_noise(I, rng)

            I_accum += I

        I_avg = I_accum / frames
        I_avg /= I_avg.max()
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
def sigmoid(sigma, V_high, V_low, sigma_c, k):
    return V_low + (V_high - V_low) / (1 + np.exp(k * (sigma - sigma_c)))


def fit_sigmoid(sigma_vals, V_vals):
    p0 = [0.97, 0.45, 2.3, 5.0]
    bounds = ([0.8, 0.0, 0.5, 0.1], [1.0, 0.8, 5.0, 20.0])

    popt, pcov = curve_fit(sigmoid, sigma_vals, V_vals,
                           p0=p0, bounds=bounds, maxfev=10000)

    perr = np.sqrt(np.diag(pcov))
    return popt, perr


def compute_r2(y, y_fit):
    ss_res = np.sum((y - y_fit)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    return 1 - ss_res / ss_tot


# =========================================================
# MAIN
# =========================================================
def main():

    print("\nRunning QMCTB-02 baseline...\n")

    Vp, _ = simulate_sigma(INITIAL_FRAMES, 0)
    Vd, _ = simulate_sigma(INITIAL_FRAMES, np.pi)

    print(f"Vp = {Vp:.3f}  |  Vd = {Vd:.3f}  |  ΔV = {Vp - Vd:.3f}")

    print("\nRunning sigma sweep...\n")

    sigma_vals, V_mean, V_std = run_sigma_sweep(INITIAL_FRAMES)

    popt, perr = fit_sigmoid(sigma_vals, V_mean)
    V_high, V_low, sigma_c, k = popt
    _, _, sigma_c_err, k_err = perr

    sigma_dense = np.linspace(0, SIGMA_MAX, 300)
    V_fit = sigmoid(sigma_dense, *popt)

    r2 = compute_r2(V_mean, sigmoid(sigma_vals, *popt))

    print(f"\nσ_c = {sigma_c:.3f} ± {sigma_c_err:.3f} rad")
    print(f"k   = {k:.2f} ± {k_err:.2f}")
    print(f"R²  = {r2:.4f}")

    # =====================================================
    # PLOT
    # =====================================================
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.fill_between(sigma_vals, V_mean - V_std, V_mean + V_std, alpha=0.10)
    ax.plot(sigma_vals, V_mean, "o-", label="Measured")
    ax.plot(sigma_dense, V_fit, "--",
            label=f"Fit (σ_c={sigma_c:.2f}, k={k:.2f}, R²={r2:.3f})")

    # Threshold lines
    ax.axvline(sigma_c, linestyle="--")
    ax.axhline(VISIBILITY_THRESHOLD, linestyle=":")
    ax.axhline(V_low, linestyle="--", alpha=0.6)

    # Inline labels
    ax.text(0.1, VISIBILITY_THRESHOLD + 0.02, "V_th", fontsize=9)
    ax.text(0.1, V_low + 0.02, "V_low", fontsize=9)

    # σ_c annotation
    y_sigma_c = sigmoid(sigma_c, *popt)
    ax.annotate(
        r"$\sigma_c$",
        xy=(sigma_c, y_sigma_c),
        xytext=(sigma_c + 0.4, y_sigma_c + 0.1),
        arrowprops=dict(arrowstyle="->", lw=0.8),
        fontsize=9
    )

    # Regime shading
    sigma_coherent_max = sigma_vals[np.where(V_mean >= VISIBILITY_THRESHOLD)[0][-1]]
    sigma_incoherent_min = sigma_vals[np.where(V_mean <= (np.min(V_mean)+0.05))[0][0]]

    ax.axvspan(0, sigma_coherent_max, alpha=0.08)
    ax.axvspan(sigma_coherent_max, sigma_incoherent_min, alpha=0.08, hatch="///")
    ax.axvspan(sigma_incoherent_min, SIGMA_MAX, alpha=0.08, hatch="...")

    ax.text(sigma_coherent_max/2, 0.15, "Coherent", ha="center", fontsize=9)
    ax.text((sigma_coherent_max+sigma_incoherent_min)/2, 0.15, "Transition", ha="center", fontsize=9)
    ax.text((sigma_incoherent_min+SIGMA_MAX)/2, 0.15, "Incoherent", ha="center", fontsize=9)

    ax.set_xlabel("σ (detector phase noise)")
    ax.set_ylabel("Visibility V")
    ax.set_title("QMCTB-02 Detector Coherence Transfer Function")

    ax.text(
        0.02, 0.95,
        f"σ_c = {sigma_c:.2f} ± {sigma_c_err:.2f}\n"
        f"k = {k:.2f} ± {k_err:.2f}\n"
        f"R² = {r2:.3f}",
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment='top'
    )

    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(ARTIFACT_DIR / "qmctb02_final.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
