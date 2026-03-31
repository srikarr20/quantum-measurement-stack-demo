# Quantum Measurement Stack

## QMCTB-02 (v3.1) — Detector Coherence Transfer Function

![QMCTB-02 Result](artifacts/qmctb02_final.png)

---

## Overview

QMCTB-02 implements a simulation framework to study interference visibility under detector-plane phase noise using a double-slit system with Fresnel propagation and detector modeling.

The system reveals a **nonlinear coherence transition**, where visibility does not decay smoothly but instead exhibits a sharp threshold behavior.

---

## Key Result

**Coherence threshold:**
σ_c ≈ 2.37 rad  
R² ≈ 0.999  

- Below σ_c → high visibility (coherence preserved)  
- Above σ_c → rapid visibility collapse  

This behavior deviates from standard exponential decoherence models and suggests a **threshold-like detector response**.

---

## Interpretation

The results support the **Imprint Hypothesis**:

> Wave-like behavior emerges as a contextual imprint of particle–field interactions and collapses at the detector plane when correlation fidelity is lost.

Interference visibility behaves as a **detector-plane transfer function**, indicating that measurement architecture plays a direct role in observed coherence.

---

## Run the Simulation

```bash
python run_qmctb02_v3_1.py


# Quantum Measurement Stack

### Imprint Hypothesis

# Quantum Measurement Stack

## QMCTB-02 (v3) — Detector Coherence Transfer Function

![QMCTB-02 Result](artifacts/qmctb02_v3_final.png)

The detector coherence transfer function demonstrates a sharp transition in interference visibility as detector phase noise increases.

**Critical threshold:**
σ_c ≈ 2.38 rad

- Below this threshold → coherence preserved, strong interference  
- Above this threshold → rapid visibility collapse  

Model fidelity:
R² ≈ 0.9986

This provides quantitative support for the Imprint Hypothesis:

Wave-like behavior emerges as a contextual imprint of particle–field interactions and collapses at the detector plane when coherence is lost.

---

## Imprint Hypothesis

- Summary: `docs/hypothesis/Imprint_Hypothesis_Handout.pdf`
- Full paper: `docs/hypothesis/The Imprint Hypothesis.pdf`

---

## Detector Plane Imaging (DPI) Framework

This work is part of a broader measurement framework:

https://github.com/srikarr20/detector-plane-imaging

DPI models coherence evolution prior to detection and establishes the detector plane as the locus of measurement outcomes.

QMCTB-02 provides quantitative validation of this framework by demonstrating a detector-driven coherence transition.

---

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19153014.svg)](https://doi.org/10.5281/zenodo.19153014)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18075090.svg)]

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19153014.svg)](https://doi.org/10.5281/zenodo.19153014)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18075090.svg)]

**Authoritative QMCTB-01 v1.0 archive:**  
https://doi.org/10.5281/zenodo.18075090

The **Quantum Measurement Stack (QMS)** is an instrumentation-focused framework
that treats quantum measurement as a causally ordered pipeline, rather than a
single abstract event.

The framework operationally localizes irreversible information loss at the **detector plane**,
defined as the complete detector–electronics–software measurement pipeline.


---

## Protocol Status: QMCTB v1.0 (Frozen)

The **QMCTB v1.0 detector-plane causality benchmark** is **frozen**.

This means:
- The measurement boundary definition is fixed
- The causal decomposition is fixed
- Benchmark logic, pass/fail criteria, and interpretation rules are fixed
- No parameter, algorithmic, or structural changes are permitted within v1.0

The frozen protocol specification and custodial scope are defined in:

📄 **`QMCTB-01_v1.0_Freeze_and_Custody.md`**

Future extensions or alternative benchmarks will be released only under new
version identifiers and will not retroactively modify QMCTB v1.0.

---

## Canonical Measurement Stack

![Quantum Measurement Stack](./qmctb/artifacts/QMCTB-01_Measurement_Stack_BlockDiagram.png)


**Measurement boundary (non-negotiable):**  
The detector plane includes detector material, conversion stages, readout
electronics, digitization, firmware, software reconstruction, and output
generation. Human observation occurs only after this boundary and has no causal
influence on coherence preservation.

---

## Repository Structure

This repository contains a modular implementation of the Quantum Measurement
Stack:

- **imprint/** — Pre-measurement imprint field dynamics (observer-free)
- **detector/** — Detector-plane imaging concepts
- **daq/** — Data acquisition integrity
- **diagnostics/** — Visibility, fidelity, and coherence diagnostics
- **qcs/** — Quantum Control System layer
- **qmctb/** — QMCTB-01 detector-plane causality benchmark
- **entanglement_recorder/** — Prototype entanglement recording architecture

Each module documents a single layer’s responsibilities and interfaces.

---

## Benchmark: QMCTB-01

QMCTB-01 is a reproducible detector-plane causality benchmark demonstrating that
interference visibility is determined by detector architecture, not photon
accumulation.

- Intensity-only detection irreversibly suppresses interference
- Correlation-preserving detection yields immediate, stable fringe geometry

See **qmctb/** for code, methods, and reference artifacts.

---

## Formal Definition

The authoritative definition of stack ordering, causality, and irreversibility
is specified in **DEFINITION.md**.

---

## Citation

If you use this framework, please cite:

**Primary (Authoritative Benchmark):**
S. Rallabandi, *Quantum Measurement & Control Test Bench (QMCTB-01): Detector Plane Causality Benchmark*, Zenodo (2025).
https://doi.org/10.5281/zenodo.18075090

**Extended Benchmark Suite (Includes QMCTB-02):**
S. Rallabandi, *Quantum Measurement Stack Benchmarks: QMCTB-01 (Causality) and QMCTB-02 (Coherence Transfer)*, Zenodo (2026).
https://doi.org/10.5281/zenodo.19153014

QMCTB-01 establishes detector-plane causality, while QMCTB-02 characterizes the detector coherence transfer function V(σ), including extraction of σ_c and k.


