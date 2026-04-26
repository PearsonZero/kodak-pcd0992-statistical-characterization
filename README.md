# Kodak PCD0992 Statistical Profile Series

**Per-Image PCA and Inter-Channel Redundancy Analysis of the Kodak Lossless True Color Image Suite**

Baetzel, J. (2026)
> **Follow-up (2026b):** For per-image measurement of how BT.601 performs against these KLT ceilings, see [BT.601 Decorrelation Gap Analysis](https://github.com/PearsonZero/kodak-pcd0992-bt601-decorrelation-gap).

-----

## Overview

This repository contains the first published per-image statistical characterization of all 24 images in the Kodak Lossless True Color Image Suite (PCD0992). Each image is documented as a two-page reference data sheet reporting the complete inter-channel redundancy structure: covariance matrix, eigendecomposition, Pearson correlations, spatial autocorrelation, and derived classification metrics.

All statistics were computed directly from the 8-bit RGB pixel arrays of the standard 768x512 base-resolution PNG distribution. No subjective descriptions appear in any profile. All redundancy classifications are generated programmatically from the computed metrics using fixed thresholds documented in the methodology.

-----

## Related Research

**Parent Paper:** Baetzel, J. (2026). *Statistical Characterization of Inter-Channel Redundancy Structure in the Kodak Lossless True Color Image Suite.* Per-Image Principal Component Decomposition of PCD0992.

- Focus: Theoretical framework establishing the first complete per-image PCA decomposition of the Kodak suite. Documents the dimensionality spectrum, blue channel independence range, eigenvector loading patterns, and evidence for deliberate curation across the 24-image collection.
- Availability: Included in this repository (`baetzel_2026_kodak_pca_characterization.pdf`).

**This Series:** Baetzel, J. (2026). *Kodak PCD0992 Statistical Profile Series.* Per-Image PCA and Inter-Channel Redundancy Analysis.

- Focus: Individual reference data sheets and machine-readable metric exports for each of the 24 images. Provides the per-image evidence underlying the suite-wide analysis in the parent paper — covariance matrices, eigendecompositions, correlation heatmaps, spatial autocorrelation, and logic-generated redundancy classifications.
- Availability: `/baseline/` directory (24 PDFs + 25 JSON files).

The parent paper establishes *why* the Kodak suite spans the full spectrum of inter-channel redundancy. The profile series documents *what* each individual image contributes to that spectrum.

-----

## Dataset Specifications

|Property   |Value                                                               |
|-----------|--------------------------------------------------------------------|
|Suite      |Kodak Lossless True Color Image Suite (PCD0992)                     |
|Image Count|24                                                                  |
|Resolution |768x512 or 512x768                                                  |
|Bit Depth  |24-bit (8 bits per channel)                                         |
|Color Space|sRGB                                                                |
|Color Mode |RGB                                                                 |
|Format     |PNG (lossless)                                                      |
|Provenance |Kodak PCD Film Scanner 2000, 35mm film, PhotoYCC decode to 8-bit RGB|

-----

## Computed Metrics Per Image

Each two-page profile reports the following:

**Page 1**

- RGB channel distribution (smoothed density curves from pixel data)
- Per-channel statistics: mean, standard deviation, variance, kurtosis, skewness, min, max
- Inter-channel correlation heatmap (3x3)
- Pairwise Pearson correlation coefficients (R-G, R-B, G-B) and suite average
- Full 3x3 covariance matrix

**Page 2**

- Eigendecomposition: eigenvalues, variance explained (%), eigenvector loadings
- Derived metrics: condition number, eigenvalue ratios, blue channel independence, PC1 dominant channel
- Dimensionality tier classification
- Spatial autocorrelation (lag-1, horizontal and vertical)
- Average local variance (3x3 neighborhood)
- Redundancy profile (logic-generated from computed metrics)

-----

## Suite Overview

The 24 images span nearly the full range of inter-channel redundancy configurations achievable through film-based photographic capture. Condition numbers range from 7.55 to 1,739.16 — more than two orders of magnitude — covering color distributions from near-spherical to extremely elongated.

### Dimensionality Tiers

|Tier                                 |PC1 Range   |Count|Images                                                                |
|-------------------------------------|------------|-----|----------------------------------------------------------------------|
|Three-Dimensional (PC1 < 75%)        |69.27-73.37%|3    |kodim02, kodim03, kodim23                                             |
|Two-Dimensional (PC1 75-85%)         |81.60%      |1    |kodim14                                                               |
|Weakly One-Dimensional (PC1 85-93%)  |86.87-91.91%|8    |kodim04, kodim05, kodim07, kodim09, kodim11, kodim18, kodim21, kodim22|
|Strongly One-Dimensional (PC1 93-97%)|93.36-96.96%|7    |kodim01, kodim08, kodim10, kodim12, kodim15, kodim16, kodim19         |
|Near-Degenerate (PC1 > 97%)          |97.36-98.42%|5    |kodim06, kodim13, kodim17, kodim20, kodim24                           |

### Eigenvector Loading Patterns

|Pattern           |Count|Images                                                       |
|------------------|-----|-------------------------------------------------------------|
|Green dominant    |7    |kodim03, kodim05, kodim08, kodim09, kodim10, kodim16, kodim17|
|Green-Blue coupled|6    |kodim01, kodim04, kodim11, kodim12, kodim15, kodim21         |
|Red dominant      |6    |kodim02, kodim06, kodim14, kodim18, kodim19, kodim23         |
|Balanced          |4    |kodim07, kodim13, kodim20, kodim24                           |
|Blue dominant     |1    |kodim22                                                      |

### Suite Extremes

|Metric               |Low            |High               |
|---------------------|---------------|-------------------|
| Avg \|r\| | kodim23: 0.5595 | kodim20: 0.9903 |
|Condition Number     |kodim23: 7.55  |kodim20: 1,739.16  |
|PC1 Variance         |kodim03: 69.27%|kodim20: 98.42%    |
|Blue Independence    |kodim15: 2.3%  |kodim03: 52.0%     |
|Highest Single Pair r|               |kodim20 R-G: 0.9955|
|Lowest Single Pair r |               |kodim03 R-B: 0.2890|

-----

## How to Read a Profile Sheet

**Condition Number** (lambda1/lambda3): Ratio of the largest to smallest eigenvalue. High values indicate a needle-like color distribution concentrated along one axis. Low values indicate a more spherical distribution where each channel carries independent information.

**Blue Channel Independence**: The percentage of blue channel variance not captured by the first principal component. Computed as (1 - (blue_loading_PC1^2 x lambda1 / Var(B))) x 100. Low values indicate the blue channel is almost entirely predictable from the primary variance axis. High values indicate the blue channel carries substantial unique information.

**Dimensionality Tier**: Classification based on PC1 variance explained. Thresholds at 75%, 85%, 93%, and 97% produce five tiers from Three-Dimensional to Near-Degenerate, corresponding to distinct regimes of inter-channel redundancy.

**Eigenvector Pattern**: The loading structure of the first principal component. Identifies which channel or channel pair drives the dominant variance axis: balanced (all channels near-equal), coupled (two channels co-load), or dominant (one channel leads).

**Spatial Autocorrelation** (lag-1): Pearson correlation between each pixel and its immediate neighbor, computed separately for horizontal and vertical directions. Values near 1.0 indicate smooth, spatially coherent image data.

-----

## File Structure

```
/
    README.md
    baetzel_2026_kodak_pca_characterization.pdf
/baseline/
    KODIM01_STATISTICAL_PROFILE.pdf
    kodim01_stats.json
    KODIM02_STATISTICAL_PROFILE.pdf
    kodim02_stats.json
    ...
    KODIM24_STATISTICAL_PROFILE.pdf
    kodim24_stats.json
    kodak_suite_master_stats.json
/docs/
    methodology.md
```

**Root**: The parent PCA characterization paper and repository README.
**`/baseline/`**: 24 two-page PDF reference data sheets and 25 JSON files (24 individual + 1 master).
**`/docs/`**: Computation pipeline documentation for full reproducibility.

-----

## References

[1] Eastman Kodak Company. Kodak Publication No. PCD-042, 1992.

[2] Baetzel, J. (2026). “Statistical Characterization of Inter-Channel Redundancy Structure in the Kodak Lossless True Color Image Suite.”

[3] Watanabe, S. “Karhunen-Loeve Expansion and Factor Analysis,” pp. 635-660, 1965.

[4] Giorgianni, E.J. and Madden, T.E. *Digital Color Management*. Addison-Wesley, 1998.

-----

## Citation

```
Baetzel, J. (2026). Kodak PCD0992 Statistical Profile Series:
Per-Image PCA and Inter-Channel Redundancy Analysis of the
Kodak Lossless True Color Image Suite.
```

-----

## License

Statistical analysis and profile sheets by Jasmine Baetzel (2026). Benchmark images from the Kodak Lossless True Color Image Suite (PCD0992), released by Eastman Kodak Company for unrestricted usage.
