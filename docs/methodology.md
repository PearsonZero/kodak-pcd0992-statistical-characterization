# Methodology

**Computation Pipeline for the Kodak PCD0992 Statistical Profile Series**

Baetzel, J. (2026)

---

## 1. Source Data

All 24 images were obtained from the Kodak Lossless True Color Image Suite (PCD0992) in their standard base-resolution PNG format as distributed by Rich Franzen. These images originate from Kodak Photo CD disc PCD0992, scanned from 35mm photographic film (including Ektachrome and Kodachrome stocks) on the Kodak PCD Film Scanner 2000.

The scanner operated as a linear trilinear CCD device at 2048x3072 native resolution with 12-bit-per-channel analog-to-digital conversion [1]. Scanned data was transformed into Kodak's proprietary PhotoYCC color space — a luminance-chrominance decomposition designed to concentrate approximately 90% of image energy into the luminance channel while preserving an extended color gamut [4]. The base-resolution (768x512) layer was subsequently decoded to 8-bit-per-channel RGB for distribution as lossless PNG files.

The inter-channel correlation structure present in these images reflects the full imaging chain: film spectral sensitivity, scanner CCD response, PhotoYCC encoding coefficients, and the subsequent decode to 8-bit sRGB. This provenance is documented because any analysis of channel redundancy is implicitly operating on data shaped by these transformations.

---

## 2. Computation Environment

All metrics were computed using Python 3 with the following libraries:

| Library | Version | Purpose |
|---|---|---|
| NumPy | 1.x | Array operations, covariance, correlation, eigendecomposition |
| SciPy | 1.x | Kurtosis, skewness (scipy.stats), local variance (scipy.ndimage) |
| Pillow (PIL) | 10.x | Image loading and pixel array extraction |

Images were loaded as 8-bit unsigned integer arrays and cast to 64-bit floating point prior to all computations. No preprocessing, normalization, or color space conversion was applied. All metrics were computed on the raw pixel values as distributed.

---

## 3. Per-Channel Statistics

For each of the three RGB channels, the following statistics were computed from the flattened pixel array (N = width x height values):

**Mean**: Arithmetic mean of all pixel values in the channel.

**Standard Deviation**: Population standard deviation (N denominator, not N-1).

**Variance**: Population variance (square of standard deviation).

**Kurtosis**: Fisher's kurtosis (excess kurtosis), computed via scipy.stats.kurtosis with fisher=True. A value of 0 corresponds to a normal distribution. Positive values indicate heavier tails; negative values indicate lighter tails.

**Skewness**: Sample skewness computed via scipy.stats.skew. Positive values indicate a right-skewed distribution; negative values indicate left-skewed.

**Min / Max**: The minimum and maximum pixel values present in the channel (integer, 0-255 range).

All values are reported to four decimal places for mean, standard deviation, variance, kurtosis, and skewness. Min and max are reported as integers.

---

## 4. Covariance Matrix

The 3x3 covariance matrix was computed using numpy.cov on the stacked channel arrays [R, G, B] with shape (3, N). NumPy computes the sample covariance matrix with N-1 denominator (Bessel's correction) by default.

The diagonal elements represent the variance of each channel. The off-diagonal elements represent the pairwise covariance between channels. The matrix is symmetric.

All covariance values are reported to four decimal places.

---

## 5. Pairwise Pearson Correlations

The Pearson correlation coefficient r for each channel pair was computed using numpy.corrcoef on the stacked channel arrays. This produces the normalized covariance:

r(X,Y) = Cov(X,Y) / (Std(X) x Std(Y))

Three pairwise correlations are reported: R-G, R-B, and G-B. The average absolute correlation is computed as the arithmetic mean of the absolute values of all three pairs:

Avg |r| = (|r(R,G)| + |r(R,B)| + |r(G,B)|) / 3

All correlation values are reported to six decimal places.

---

## 6. Eigendecomposition

The eigendecomposition of the 3x3 covariance matrix was computed using numpy.linalg.eigh, which returns eigenvalues and eigenvectors for symmetric matrices. Eigenvalues were sorted in descending order and eigenvectors were reordered to match.

**Eigenvalues**: The variance along each principal axis. Reported to four decimal places.

**Variance Explained**: Each eigenvalue as a percentage of the total variance (sum of all three eigenvalues). Reported to two decimal places.

**Eigenvector Loadings**: The three components (R, G, B) of each eigenvector, indicating the contribution of each channel to that principal axis. Reported to four decimal places.

**Residual Correlations in PCA Space**: After projecting the centered channel data into the eigenvector basis, pairwise correlations between the projected components are computed. These are exactly 0.000000 for all images by construction, confirming correct decomposition. This represents the theoretical ceiling for linear decorrelation achievable by the Karhunen-Loeve Transform [3].

---

## 7. Derived Metrics

### 7.1 Condition Number

The condition number is defined as the ratio of the largest to smallest eigenvalue. This measures the elongation of the color distribution ellipsoid in three-dimensional RGB space. High values indicate a near-degenerate distribution where most variance is concentrated along a single axis. Low values indicate a more spherical distribution where each channel carries independent information. Reported to two decimal places.

### 7.2 Eigenvalue Ratios

Two successive eigenvalue ratios are reported: PC1/PC2 and PC2/PC3. These distinguish between smooth exponential decay of variance across components and sharp cliff transitions where the color structure drops abruptly from meaningful to negligible at a specific dimensionality threshold. Reported to two decimal places.

### 7.3 Blue Channel Independence

The fraction of blue channel variance not captured by the first principal component:

Blue Independence = (1 - (blue_loading_PC1^2 x lambda1 / Var(B))) x 100

This metric quantifies how much unique information the blue channel carries independent of the dominant variance axis. Reported to one decimal place.

### 7.4 Dimensionality Tier Classification

Each image is classified into one of five tiers based on the percentage of total variance captured by the first principal component:

| Tier | Threshold | Interpretation |
|---|---|---|
| Three-Dimensional | PC1 < 75% | Each channel carries substantial unique information |
| Two-Dimensional | PC1 75-85% | Two independent dimensions of color variation |
| Weakly One-Dimensional | PC1 85-93% | Dominated by one axis but secondary components carry measurable variance |
| Strongly One-Dimensional | PC1 93-97% | Primary axis captures nearly all variance |
| Near-Degenerate | PC1 > 97% | Three channels function as near-copies of a single signal |

These thresholds were established in Baetzel (2026) [2] based on the observed clustering of the 24 Kodak images along the PC1 variance axis and produce the five non-overlapping tiers documented in that paper.

### 7.5 Eigenvector Pattern Classification

The PC1 eigenvector loading pattern is classified programmatically based on the absolute values of the R, G, and B components:

| Pattern | Criteria |
|---|---|
| Balanced | Spread between max and min loading < 0.03 |
| Green-Blue coupled | G > 0.58 and B > 0.56 and R < 0.53 |
| Green dominant | G is the highest loading and G > 0.59 |
| Red dominant | R is the highest loading and R > 0.59 |
| Blue dominant | B is the highest loading and B > 0.59 |

If no specific pattern matches, classification falls back to the channel with the highest absolute loading.

### 7.6 PC1 Dominant Channel

The channel with the highest absolute loading on the PC1 eigenvector. Reported alongside the loading value to four decimal places.

---

## 8. Spatial Autocorrelation

Spatial autocorrelation measures the Pearson correlation between each pixel and its immediate neighbor, computed separately for horizontal (lag-1 right) and vertical (lag-1 down) directions.

Computed independently for each of the three RGB channels. Values near 1.0 indicate smooth, spatially coherent data. Values significantly below 1.0 indicate high-frequency spatial content or noise.

All spatial autocorrelation values are reported to six decimal places.

---

## 9. Average Local Variance

The average local variance measures the mean pixel-level variance within a 3x3 neighborhood, computed using scipy.ndimage.uniform_filter.

Computed independently for each RGB channel. High values indicate fine texture or high-frequency detail. Low values indicate smooth or uniform regions. This metric complements spatial autocorrelation by distinguishing between "high autocorrelation because the image is flat" and "high autocorrelation because the image is smoothly varying."

Reported to four decimal places.

---

## 10. Redundancy Profile Generation

The redundancy profile on each data sheet is generated entirely by programmatic logic — no manual text was written for any of the 24 images. Each field is computed from the metrics using the following rules:

**Classification**: Dimensionality tier (Section 7.4), condition number (Section 7.1), and PC1 variance explained (Section 6).

**Correlation Structure**: The channel pair with the highest absolute Pearson correlation is identified. If the value exceeds 0.95, the pair is described as "dominates." If the spread across all three pairs is less than 0.05, the structure is described as "Uniform correlation across all pairs." Otherwise, the highest pair is described as "leads."

**Blue Channel**: Four tiers based on blue channel independence (Section 7.3). Below 5%: Reports percentage captured by PC1. 5-15%: "Moderate decoupling from PC1." 15-35%: "Substantial independence from PC1." Above 35%: "3D color; major blue variance."

**Spatial Structure**: Reports the mean spatial autocorrelation and mean local variance across all three channels.

**Eigenvector Pattern**: Reports the classification from Section 7.5 with the specific loading values for each channel.

---

## 11. Output Formats

### PDF Data Sheets

Each two-page PDF was generated using matplotlib (300 DPI) for figure rendering and ReportLab for PDF assembly. PDF metadata includes Title, Author, Subject, and Creator fields mapped from each image ID.

### JSON Sidecar Files

Each per-image JSON file contains all computed metrics in a structured hierarchy. The top-level keys are: metadata, channel_statistics, covariance_matrix, correlations, eigendecomposition, derived_metrics, spatial_autocorrelation, average_local_variance_3x3, residual_correlations_pca_space, and redundancy_profile.

### Master JSON

The file kodak_suite_master_stats.json contains all 24 per-image records in a single file, keyed by image ID (kodim01 through kodim24), plus a _metadata record documenting the generation context.

---

## 12. Reproducibility

All computations are deterministic. Given the same 24 PNG source files from the Kodak PCD0992 distribution, the same Python environment, and the same computation pipeline described above, all reported values will reproduce exactly.

The classification thresholds (Section 7.4, 7.5) and redundancy profile logic (Section 10) are fixed parameters, not fitted to data. Changing these thresholds will change the tier assignments and profile text but will not affect any of the underlying computed metrics.

---

## References

[1] Eastman Kodak Company. Kodak Publication No. PCD-042, 1992.

[2] Baetzel, J. (2026). "Statistical Characterization of Inter-Channel Redundancy Structure in the Kodak Lossless True Color Image Suite."

[3] Watanabe, S. "Karhunen-Loeve Expansion and Factor Analysis," pp. 635-660, 1965.

[4] Giorgianni, E.J. and Madden, T.E. Digital Color Management. Addison-Wesley, 1998.
