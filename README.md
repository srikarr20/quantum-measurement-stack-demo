[![DOI](https://zenodo.org/badge/19353701.svg)](https://doi.org/10.5281/zenodo.19353701)


# Quantum Measurement Stack Demo (QMCTB-03)


👉 **Entry point:** `qmctb03_v66.py`

---

## Overview

This project investigates how **detector resolution and noise influence the observability of interference (coherence)** in a simulated double-slit optical system.

Rather than assuming ideal sampling conditions, we model a full **measurement stack**:

- Wave propagation (Fresnel)
- Detector discretization (pixel binning)
- Noise processes (shot + read)
- Visibility estimation
- Threshold-based observability

---

## Key Result

**Scaling behavior:**

B_min ∝ d^(-0.77)

where:
- **d** is the slit separation  
- **B_min** is the maximum bin size that preserves visibility  

---

## Interpretation

Ideal sampling predicts:

B ∝ d^(-1)

However, under realistic measurement conditions, we observe a **shallower scaling (b ≈ -0.77)** due to:

- detector noise  
- pixel averaging (coarse-graining)  
- threshold-based visibility criteria  

---

## Core Insight

> Interference is not simply present or absent.  
> It becomes **observable only when detector resolution and noise permit stable estimation**.

This leads to a **stochastic observability band**, rather than a sharp resolution boundary.

---

## Methodology

For each slit separation **d**:

1. Generate field via Fresnel propagation  
2. Apply detector binning (pixel aggregation)  
3. Add noise (shot + read)  
4. Compute fringe visibility  
5. Identify largest bin size satisfying:

V ≥ 0.75

6. Repeat across multiple runs → compute mean and uncertainty  

---

## ▶️ How to Run

```bash
python qmctb03_v66.py

📊 Output

The simulation produces:

Scaling curve: B_min vs d
Power-law fit (exponent ≈ -0.77)
Nyquist reference curve
Error bars (multi-run variability)

Outputs are saved in:

artifacts/

qmctb03_v66.py         → final experiment (main entry point)
qmctb03_v6x.py         → development history
qmctb03_heatmap_*.py   → parameter exploration
artifacts/             → generated outputs (ignored in git)

🔁 Reproducibility
Fixed global seed ensures consistency
Multiple runs provide statistical robustness
Results are stable across executions
📚 Scientific Context

This work builds on established principles that:

visibility estimation is sensitive to detector noise
interferometric measurements are signal-to-noise limited
sampling alone does not determine observability

and extends them by quantifying a noise-conditioned resolution threshold.

👤 Author

Srikar R

📄 License

MIT (or specify your license)


---

## 📖 Citation

If you use this work, please cite:

Srikar R.  
*Quantum Measurement Stack Demo (QMCTB-03)*  
Zenodo, 2026.  
DOI: https://doi.org/10.5281/zenodo.19353701
