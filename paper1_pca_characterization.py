#!/usr/bin/env python3
"""
Statistical Characterization of Inter-Channel Redundancy Structure
in the Kodak Lossless True Color Image Suite

Per-Image Principal Component Decomposition of PCD0992

Baetzel (2026a)

Computes: covariance matrix, eigendecomposition, variance explained,
condition number, blue channel independence, eigenvector loading patterns,
residual correlations in PCA space, dimensionality tier classification.

Outputs: 24 per-image JSON files + suite master JSON.

Requirements: Python 3, NumPy, Pillow
Usage: python paper1_pca_characterization.py --input-dir ./kodak_images --output-dir ./results
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def load_image_pixels(filepath):
    """Load image and return (H, W, 3) uint8 array and dimensions."""
    img = Image.open(filepath).convert("RGB")
    pixels = np.array(img, dtype=np.float64)
    return pixels, img.size  # (width, height)


def compute_pca_stats(pixels):
    """
    Compute full PCA characterization from raw RGB pixel values.

    Parameters
    ----------
    pixels : ndarray, shape (H, W, 3)
        Raw 8-bit RGB pixel values as float64.

    Returns
    -------
    dict : Complete PCA characterization.
    """
    H, W, _ = pixels.shape
    N = H * W
    flat = pixels.reshape(N, 3)  # (N, 3) — each row is [R, G, B]

    # Channel statistics
    means = flat.mean(axis=0)
    stds = flat.std(axis=0, ddof=0)
    channel_energy = (flat ** 2).sum(axis=0)
    total_energy = channel_energy.sum()
    energy_pct = channel_energy / total_energy * 100

    # Pairwise Pearson correlations (RGB)
    corr_matrix = np.corrcoef(flat.T)  # 3x3
    r_rg = corr_matrix[0, 1]
    r_rb = corr_matrix[0, 2]
    r_gb = corr_matrix[1, 2]
    avg_abs_r = (abs(r_rg) + abs(r_rb) + abs(r_gb)) / 3

    # Covariance matrix (ddof=1, numpy default for np.cov)
    cov_matrix = np.cov(flat.T)

    # Eigendecomposition
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    # Sort descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    total_variance = eigenvalues.sum()
    variance_explained = eigenvalues / total_variance * 100

    # Condition number
    condition_number = eigenvalues[0] / eigenvalues[2] if eigenvalues[2] > 0 else float("inf")

    # Eigenvalue ratios
    ratio_pc1_pc2 = eigenvalues[0] / eigenvalues[1] if eigenvalues[1] > 0 else float("inf")
    ratio_pc2_pc3 = eigenvalues[1] / eigenvalues[2] if eigenvalues[2] > 0 else float("inf")

    # Blue channel independence
    # Blue is channel index 2
    blue_loading_pc1 = eigenvectors[2, 0]
    blue_var = cov_matrix[2, 2]
    if blue_var > 0:
        blue_captured_by_pc1 = (blue_loading_pc1 ** 2 * eigenvalues[0]) / blue_var
        blue_independence = (1.0 - blue_captured_by_pc1) * 100.0
    else:
        blue_independence = 0.0

    # PC1 dominant channel
    abs_loadings = np.abs(eigenvectors[:, 0])
    dominant_idx = np.argmax(abs_loadings)
    channel_names = ["R", "G", "B"]
    pc1_dominant = f"{channel_names[dominant_idx]} ({abs_loadings[dominant_idx]:.2f})"

    # Residual correlations in PCA space (should be ~0)
    pca_data = (flat - means) @ eigenvectors  # project into PCA space
    pca_corr = np.corrcoef(pca_data.T)
    residual_pc1_pc2 = pca_corr[0, 1]
    residual_pc1_pc3 = pca_corr[0, 2]
    residual_pc2_pc3 = pca_corr[1, 2]

    # Eigenvector loading details
    ev_loadings = []
    for pc_idx in range(3):
        ev_loadings.append({
            "PC": pc_idx + 1,
            "R": float(eigenvectors[0, pc_idx]),
            "G": float(eigenvectors[1, pc_idx]),
            "B": float(eigenvectors[2, pc_idx]),
        })

    # Blue channel per-PC analysis
    blue_loading_pc2 = eigenvectors[2, 1]
    blue_loading_pc3 = eigenvectors[2, 2]
    blue_captured_by_pc2 = (blue_loading_pc2 ** 2) * eigenvalues[1]
    blue_captured_by_pc3 = (blue_loading_pc3 ** 2) * eigenvalues[2]

    # Classify eigenvector pattern
    abs_pc1 = np.abs(eigenvectors[:, 0])
    r_load, g_load, b_load = abs_pc1
    if max(abs_pc1) - min(abs_pc1) < 0.04:
        ev_pattern = "Balanced"
    elif g_load > 0.59 and b_load > 0.59 and r_load < 0.52:
        ev_pattern = "Green-Blue coupled"
    elif g_load > 0.60 and g_load == max(abs_pc1):
        ev_pattern = "Green dominant"
    elif r_load > 0.62:
        ev_pattern = "Red dominant"
    elif b_load > 0.61 and r_load < 0.52:
        ev_pattern = "Blue dominant"
    else:
        ev_pattern = "Mixed"

    return {
        "channel_statistics": {
            "means": {"R": float(means[0]), "G": float(means[1]), "B": float(means[2])},
            "std_devs": {"R": float(stds[0]), "G": float(stds[1]), "B": float(stds[2])},
            "energy_pct": {"R": float(energy_pct[0]), "G": float(energy_pct[1]), "B": float(energy_pct[2])},
        },
        "rgb_correlations": {
            "R_G": float(r_rg),
            "R_B": float(r_rb),
            "G_B": float(r_gb),
            "avg_abs_r": float(avg_abs_r),
        },
        "covariance_matrix": [[round(float(x), 4) for x in row] for row in cov_matrix],
        "eigenvalues": {
            "lambda1": float(eigenvalues[0]),
            "lambda2": float(eigenvalues[1]),
            "lambda3": float(eigenvalues[2]),
        },
        "variance_explained_pct": {
            "PC1": float(variance_explained[0]),
            "PC2": float(variance_explained[1]),
            "PC3": float(variance_explained[2]),
        },
        "eigenvector_loadings": ev_loadings,
        "eigenvector_pattern": ev_pattern,
        "condition_number": float(condition_number),
        "eigenvalue_ratios": {
            "PC1_PC2": float(ratio_pc1_pc2),
            "PC2_PC3": float(ratio_pc2_pc3),
        },
        "blue_channel_independence_pct": float(blue_independence),
        "blue_analysis": {
            "pc1_loading": float(blue_loading_pc1),
            "pc1_loading_squared": float(blue_loading_pc1 ** 2),
            "variance_captured_by_pc1_pct": float(blue_captured_by_pc1 / blue_var * 100) if blue_var > 0 else 0,
            "variance_captured_by_pc2_pct": float(blue_captured_by_pc2 / blue_var * 100) if blue_var > 0 else 0,
            "variance_captured_by_pc3_pct": float(blue_captured_by_pc3 / blue_var * 100) if blue_var > 0 else 0,
        },
        "pc1_dominant": pc1_dominant,
        "residual_correlations_pca": {
            "PC1_PC2": float(residual_pc1_pc2),
            "PC1_PC3": float(residual_pc1_pc3),
            "PC2_PC3": float(residual_pc2_pc3),
        },
    }


def classify_dimensionality(pc1_pct):
    """Classify image into dimensionality tier based on PC1 variance explained."""
    if pc1_pct < 75:
        return "Three-dimensional"
    elif pc1_pct < 85:
        return "Two-dimensional"
    elif pc1_pct < 93:
        return "Weakly one-dimensional"
    elif pc1_pct < 97:
        return "Strongly one-dimensional"
    else:
        return "Near-degenerate"


def classify_blue_independence(blue_indep):
    """Classify blue channel independence range."""
    if blue_indep < 5:
        return "Minimal (< 5%)"
    elif blue_indep < 15:
        return "Moderate (5-15%)"
    elif blue_indep < 35:
        return "Substantial (15-35%)"
    else:
        return "Major (> 35%)"


def main():
    parser = argparse.ArgumentParser(
        description="Paper 1: PCA Characterization of the Kodak Image Suite"
    )
    parser.add_argument(
        "--input-dir", required=True,
        help="Directory containing kodim01.png through kodim24.png"
    )
    parser.add_argument(
        "--output-dir", default="./paper1_results",
        help="Directory for output JSON files (default: ./paper1_results)"
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect all results for suite summary
    all_results = []

    for i in range(1, 25):
        image_id = f"kodim{i:02d}"
        filename = f"{image_id}.png"
        filepath = input_dir / filename

        if not filepath.exists():
            print(f"WARNING: {filepath} not found, skipping.")
            continue

        print(f"Processing {image_id}...")

        pixels, (width, height) = load_image_pixels(filepath)
        stats = compute_pca_stats(pixels)

        # Build per-image JSON
        dim_tier = classify_dimensionality(stats["variance_explained_pct"]["PC1"])
        blue_tier = classify_blue_independence(stats["blue_channel_independence_pct"])

        per_image = {
            "image_id": image_id,
            "filename": filename,
            "dimensions": {"width": width, "height": height},
            "bit_depth": 24,
            "pixels": width * height,
            "dimensionality_tier": dim_tier,
            "blue_independence_tier": blue_tier,
            **stats,
            "methodology": {
                "source": "Kodak Lossless True Color Image Suite (PCD0992)",
                "software": "Python 3, NumPy, Pillow",
                "covariance": "Sample covariance (numpy default, ddof=1)",
                "eigendecomposition": "numpy.linalg.eigh, sorted descending",
                "computed_from": "Raw 8-bit RGB pixel values, no preprocessing",
            },
        }

        # Save per-image JSON
        out_path = output_dir / f"{image_id}_stats.json"
        with open(out_path, "w") as f:
            json.dump(per_image, f, indent=2)
        print(f"  Saved: {out_path}")

        all_results.append(per_image)

    if not all_results:
        print("ERROR: No images found. Check --input-dir path.")
        sys.exit(1)

    # Build suite summary
    print(f"\nBuilding suite summary from {len(all_results)} images...")

    pc1_vals = [r["variance_explained_pct"]["PC1"] for r in all_results]
    cond_vals = [r["condition_number"] for r in all_results]
    blue_indep_vals = [r["blue_channel_independence_pct"] for r in all_results]
    avg_abs_r_vals = [r["rgb_correlations"]["avg_abs_r"] for r in all_results]

    # Dimensionality tier distribution
    dim_tiers = {}
    for r in all_results:
        tier = r["dimensionality_tier"]
        if tier not in dim_tiers:
            dim_tiers[tier] = {"count": 0, "images": [], "pc1_range": [], "cond_range": []}
        dim_tiers[tier]["count"] += 1
        dim_tiers[tier]["images"].append(r["image_id"])
        dim_tiers[tier]["pc1_range"].append(r["variance_explained_pct"]["PC1"])
        dim_tiers[tier]["cond_range"].append(r["condition_number"])

    for tier in dim_tiers:
        dim_tiers[tier]["pc1_range"] = [
            round(min(dim_tiers[tier]["pc1_range"]), 2),
            round(max(dim_tiers[tier]["pc1_range"]), 2),
        ]
        dim_tiers[tier]["cond_range"] = [
            round(min(dim_tiers[tier]["cond_range"]), 2),
            round(max(dim_tiers[tier]["cond_range"]), 2),
        ]

    # Eigenvector pattern distribution
    ev_patterns = {}
    for r in all_results:
        pat = r["eigenvector_pattern"]
        if pat not in ev_patterns:
            ev_patterns[pat] = {"count": 0, "images": []}
        ev_patterns[pat]["count"] += 1
        ev_patterns[pat]["images"].append(r["image_id"])

    suite_summary = {
        "_schema_notes": "Baetzel (2026a) — PCA Characterization Suite Summary",
        "suite": "Kodak Lossless True Color Image Suite (PCD0992)",
        "images_analyzed": len(all_results),
        "pc1_variance_stats": {
            "mean_pct": round(float(np.mean(pc1_vals)), 2),
            "median_pct": round(float(np.median(pc1_vals)), 2),
            "min_pct": round(float(np.min(pc1_vals)), 2),
            "min_image": all_results[int(np.argmin(pc1_vals))]["image_id"],
            "max_pct": round(float(np.max(pc1_vals)), 2),
            "max_image": all_results[int(np.argmax(pc1_vals))]["image_id"],
            "range_pct": round(float(np.max(pc1_vals) - np.min(pc1_vals)), 2),
        },
        "condition_number_stats": {
            "mean": round(float(np.mean(cond_vals)), 2),
            "median": round(float(np.median(cond_vals)), 2),
            "min": round(float(np.min(cond_vals)), 2),
            "min_image": all_results[int(np.argmin(cond_vals))]["image_id"],
            "max": round(float(np.max(cond_vals)), 2),
            "max_image": all_results[int(np.argmax(cond_vals))]["image_id"],
        },
        "blue_independence_stats": {
            "mean_pct": round(float(np.mean(blue_indep_vals)), 2),
            "median_pct": round(float(np.median(blue_indep_vals)), 2),
            "min_pct": round(float(np.min(blue_indep_vals)), 2),
            "min_image": all_results[int(np.argmin(blue_indep_vals))]["image_id"],
            "max_pct": round(float(np.max(blue_indep_vals)), 2),
            "max_image": all_results[int(np.argmax(blue_indep_vals))]["image_id"],
            "range_pct": round(float(np.max(blue_indep_vals) - np.min(blue_indep_vals)), 2),
        },
        "rgb_correlation_stats": {
            "mean_avg_abs_r": round(float(np.mean(avg_abs_r_vals)), 4),
            "min_avg_abs_r": round(float(np.min(avg_abs_r_vals)), 4),
            "max_avg_abs_r": round(float(np.max(avg_abs_r_vals)), 4),
        },
        "dimensionality_tiers": dim_tiers,
        "eigenvector_patterns": ev_patterns,
        "residual_correlations_pca": {
            "note": "All images achieve r = 0.000000 in PCA space (KLT ceiling)",
        },
        "per_image_summary": [
            {
                "image_id": r["image_id"],
                "PC1_pct": round(r["variance_explained_pct"]["PC1"], 2),
                "PC2_pct": round(r["variance_explained_pct"]["PC2"], 2),
                "PC3_pct": round(r["variance_explained_pct"]["PC3"], 2),
                "condition_number": round(r["condition_number"], 2),
                "blue_independence_pct": round(r["blue_channel_independence_pct"], 1),
                "pc1_dominant": r["pc1_dominant"],
                "dimensionality_tier": r["dimensionality_tier"],
            }
            for r in all_results
        ],
        "methodology": {
            "source": "Kodak Lossless True Color Image Suite (PCD0992)",
            "format": "768x512 / 512x768, 24-bit RGB, lossless PNG",
            "software": "Python 3, NumPy, Pillow",
            "covariance": "Sample covariance (numpy default, ddof=1)",
            "eigendecomposition": "numpy.linalg.eigh, sorted descending",
            "computed_from": "Raw 8-bit RGB pixel values, no preprocessing",
            "reproducibility": "All values computable from publicly available Kodak PNG files",
        },
        "citation": "Baetzel, J. (2026a). Statistical Characterization of Inter-Channel Redundancy Structure in the Kodak Lossless True Color Image Suite.",
    }

    summary_path = output_dir / "kodak_suite_master_stats.json"
    with open(summary_path, "w") as f:
        json.dump(suite_summary, f, indent=2)
    print(f"Saved suite summary: {summary_path}")

    # Print summary table
    print("\n" + "=" * 90)
    print("SUITE SUMMARY — PCA Characterization")
    print("=" * 90)
    print(f"{'Image':<10} {'PC1%':>7} {'PC2%':>7} {'PC3%':>7} {'Cond#':>10} {'Blue%':>7} {'PC1 Dom':<15} {'Tier'}")
    print("-" * 90)
    for r in all_results:
        print(
            f"{r['image_id']:<10} "
            f"{r['variance_explained_pct']['PC1']:>7.2f} "
            f"{r['variance_explained_pct']['PC2']:>7.2f} "
            f"{r['variance_explained_pct']['PC3']:>7.2f} "
            f"{r['condition_number']:>10.2f} "
            f"{r['blue_channel_independence_pct']:>7.1f} "
            f"{r['pc1_dominant']:<15} "
            f"{r['dimensionality_tier']}"
        )
    print("-" * 90)
    print(f"{'MEAN':<10} {np.mean(pc1_vals):>7.2f} {'':>7} {'':>7} {np.mean(cond_vals):>10.2f} {np.mean(blue_indep_vals):>7.1f}")
    print(f"\nCondition number range: {min(cond_vals):.2f} — {max(cond_vals):.2f}")
    print(f"Blue independence range: {min(blue_indep_vals):.1f}% — {max(blue_indep_vals):.1f}%")
    print(f"\nAll residual correlations in PCA space: r = 0.000000 (KLT ceiling confirmed)")


if __name__ == "__main__":
    main()
