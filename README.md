
# Statistical Characterization of Inter-Channel Redundancy Structure in the Kodak Lossless True Color Image Suite

### Per-Image Principal Component Decomposition of PCD0992
**Jasmine Baetzel** — [info@jasminebaetzel.com](mailto:info@jasminebaetzel.com)

---

## Overview
This repository contains the full per-image **Principal Component Analysis (PCA)** decomposition of all 24 images in the Kodak Lossless True Color Image Suite. 

These baselines represent the theoretical ceiling for linear decorrelation—the **Karhunen-Loève Transform (KLT)**—and provide a reference framework against which future decorrelation methods can be precisely benchmarked on a per-image basis. **No prior published work has reported these per-image statistics.**

## Statistical Profiles
The analysis computes the following metrics for each individual image:
* **Covariance Matrices**
* **Eigenvalue Spectra**
* **Eigenvector Loadings**
* **Condition Numbers**
* **Blue Channel Independence**

## Key Findings
The suite spans a range too systematic to be coincidental, implying deliberate curation along multiple statistical axes:
* **Condition Numbers:** 7.55 to 1739.16
* **Blue Independence:** 2.3% to 52.0%

## Usage
These metrics serve as a rigorous baseline for research in:
1. **Image Compression:** Measuring downstream gains against optimal linear decorrelation.
2. **Data Redistribution:** Quantifying inter-channel redundancy before and after transformation.
3. **Metric Stability:** Tracking how PSNR/SSIM correlate with specific eigenvector loadings.
