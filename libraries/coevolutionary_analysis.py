#!/usr/bin/env python3
"""
Enhanced Coevolutionary Analysis with Amino Acid Pair Frequencies and Higher-Order Analysis

Features:
- Shows actual amino acid pairs observed (e.g., E-Y, D-F)
- Computes mutual information for triplets and quartets
- Identifies coevolving sectors/networks

Author: Konstantinos Grigorakis
Date: November 2025
"""

import sys
import os
import numpy as np
import pandas as pd
from Bio import AlignIO
from collections import Counter
from itertools import combinations
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Set
import warnings
warnings.filterwarnings('ignore')


AMINO_ACIDS = list('ACDEFGHIKLMNPQRSTVWY')


def get_amino_acid_pairs(alignment_array: np.ndarray, pos_i_idx: int, pos_j_idx: int, 
                         top_n: int = 5) -> List[Tuple[str, str, float, int]]:
    """
    Get most common amino acid pairs observed at two positions.
    
    Returns: [(aa_i, aa_j, frequency, count), ...]
    """
    col_i = alignment_array[:, pos_i_idx]
    col_j = alignment_array[:, pos_j_idx]
    
    # Filter gaps
    mask = (col_i != '-') & (col_j != '-')
    col_i_clean = col_i[mask]
    col_j_clean = col_j[mask]
    
    if len(col_i_clean) == 0:
        return []
    
    # Count pairs
    pairs = list(zip(col_i_clean, col_j_clean))
    pair_counts = Counter(pairs)
    total = len(pairs)
    
    # Sort by frequency
    sorted_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    # Format as (aa_i, aa_j, frequency, count)
    result = [(aa_i, aa_j, count/total, count) for (aa_i, aa_j), count in sorted_pairs]
    
    return result


def compute_mutual_information(col_i: np.ndarray, col_j: np.ndarray) -> float:
    """
    Compute mutual information between two positions.
    MI(X,Y) = Σ p(x,y) log(p(x,y) / (p(x)p(y)))
    """
    # Filter gaps
    mask = (col_i != '-') & (col_j != '-')
    col_i_clean = col_i[mask]
    col_j_clean = col_j[mask]
    
    if len(col_i_clean) == 0:
        return 0.0
    
    # Compute frequencies
    count_i = Counter(col_i_clean)
    count_j = Counter(col_j_clean)
    count_ij = Counter(zip(col_i_clean, col_j_clean))
    
    total = len(col_i_clean)
    
    mi = 0.0
    for (aa_i, aa_j), n_ij in count_ij.items():
        p_ij = n_ij / total
        p_i = count_i[aa_i] / total
        p_j = count_j[aa_j] / total
        
        if p_ij > 0 and p_i > 0 and p_j > 0:
            mi += p_ij * np.log2(p_ij / (p_i * p_j))
    
    return max(0, mi)  # MI is non-negative


def compute_triplet_mi(alignment_array: np.ndarray, pos_i: int, pos_j: int, pos_k: int) -> float:
    """
    Compute 3-way mutual information.
    MI(X,Y,Z) = Σ p(x,y,z) log(p(x,y,z) / (p(x)p(y)p(z)))
    """
    col_i = alignment_array[:, pos_i]
    col_j = alignment_array[:, pos_j]
    col_k = alignment_array[:, pos_k]
    
    # Filter gaps
    mask = (col_i != '-') & (col_j != '-') & (col_k != '-')
    col_i_clean = col_i[mask]
    col_j_clean = col_j[mask]
    col_k_clean = col_k[mask]
    
    if len(col_i_clean) < 10:  # Need enough data
        return 0.0
    
    # Compute frequencies
    count_i = Counter(col_i_clean)
    count_j = Counter(col_j_clean)
    count_k = Counter(col_k_clean)
    count_ijk = Counter(zip(col_i_clean, col_j_clean, col_k_clean))
    
    total = len(col_i_clean)
    
    mi3 = 0.0
    for (aa_i, aa_j, aa_k), n_ijk in count_ijk.items():
        p_ijk = n_ijk / total
        p_i = count_i[aa_i] / total
        p_j = count_j[aa_j] / total
        p_k = count_k[aa_k] / total
        
        if p_ijk > 0 and p_i > 0 and p_j > 0 and p_k > 0:
            mi3 += p_ijk * np.log2(p_ijk / (p_i * p_j * p_k))
    
    return max(0, mi3)


def compute_connected_triplet_mi(alignment_array: np.ndarray, pos_i: int, pos_j: int, pos_k: int) -> float:
    """
    Compute connected mutual information for triplet.
    This removes pairwise correlations to focus on genuine 3-way coupling.
    
    CMI(i,j,k) = MI(i,j,k) - [MI(i,j) + MI(i,k) + MI(j,k)]
    """
    mi_ijk = compute_triplet_mi(alignment_array, pos_i, pos_j, pos_k)
    
    # Pairwise MIs
    mi_ij = compute_mutual_information(alignment_array[:, pos_i], alignment_array[:, pos_j])
    mi_ik = compute_mutual_information(alignment_array[:, pos_i], alignment_array[:, pos_k])
    mi_jk = compute_mutual_information(alignment_array[:, pos_j], alignment_array[:, pos_k])
    
    # Connected MI
    cmi = mi_ijk - (mi_ij + mi_ik + mi_jk)
    
    return cmi


def find_top_triplets(alignment_array: np.ndarray, position_indices: List[int], 
                     position_labels: Dict[int, str], top_n: int = 20, 
                     max_candidates: int = 100) -> List[Tuple[str, str, str, float]]:
    """
    Find top covarying triplets using connected mutual information.
    
    Strategy: Only test triplets where all 3 pairs are in top pairwise signals.
    """
    print(f"\nSearching for covarying triplets...")
    print(f"  Testing combinations from top {max_candidates} pairwise signals")
    
    # First, get top pairwise MI values
    n_pos = len(position_indices)
    pair_scores = []
    
    for i in range(n_pos):
        for j in range(i+1, n_pos):
            mi = compute_mutual_information(alignment_array[:, i], alignment_array[:, j])
            pair_scores.append((i, j, mi))
    
    # Sort and get top candidates
    pair_scores.sort(key=lambda x: x[2], reverse=True)
    top_pairs = pair_scores[:max_candidates]
    
    # Build set of positions that appear in top pairs
    candidate_positions = set()
    for i, j, _ in top_pairs:
        candidate_positions.add(i)
        candidate_positions.add(j)
    
    candidate_list = sorted(list(candidate_positions))
    print(f"  Candidate positions: {len(candidate_list)}")
    
    # Test all triplets from candidate positions
    triplet_scores = []
    n_triplets = len(list(combinations(candidate_list, 3)))
    print(f"  Testing {n_triplets} triplet combinations...")
    
    tested = 0
    for i, j, k in combinations(candidate_list, 3):
        cmi = compute_connected_triplet_mi(alignment_array, i, j, k)
        if cmi > 0:  # Only keep positive signals
            aln_pos_i = position_indices[i]
            aln_pos_j = position_indices[j]
            aln_pos_k = position_indices[k]
            
            label_i = position_labels[aln_pos_i]
            label_j = position_labels[aln_pos_j]
            label_k = position_labels[aln_pos_k]
            
            triplet_scores.append((label_i, label_j, label_k, cmi))
        
        tested += 1
        if tested % 1000 == 0:
            print(f"    Progress: {tested}/{n_triplets} ({100*tested/n_triplets:.1f}%)")
    
    # Sort and return top
    triplet_scores.sort(key=lambda x: x[3], reverse=True)
    print(f"  Found {len(triplet_scores)} triplets with positive signal")
    
    return triplet_scores[:top_n]


def save_enhanced_top_pairs(top_pairs: List[Tuple[str, str, float]], 
                            alignment_array: np.ndarray,
                            filtered_positions: List[int],
                            position_labels: Dict[int, str],
                            output_file: str, 
                            top_n: int):
    """Save top pairs with amino acid pair frequencies."""
    
    # Build reverse mapping: label -> array index
    label_to_idx = {}
    for idx, aln_pos in enumerate(filtered_positions):
        label = position_labels[aln_pos]
        label_to_idx[label] = idx
    
    with open(output_file, 'w') as f:
        f.write("=" * 120 + "\n")
        f.write(f"TOP {top_n} COVARYING POSITION PAIRS (WITH AMINO ACID FREQUENCIES)\n")
        f.write("=" * 120 + "\n\n")
        f.write(f"{'Rank':<6} {'Residue 1':<12} {'Residue 2':<12} {'Covariance':<12} Most Common Pairs (AA1-AA2: freq%)\n")
        f.write("-" * 120 + "\n")
        
        for rank, (res1, res2, cov) in enumerate(top_pairs, 1):
            # Get amino acid pairs
            idx1 = label_to_idx[res1]
            idx2 = label_to_idx[res2]
            aa_pairs = get_amino_acid_pairs(alignment_array, idx1, idx2, top_n=5)
            
            # Format pairs
            if aa_pairs:
                pairs_str = ", ".join([f"{a1}-{a2}:{100*freq:.1f}%" for a1, a2, freq, _ in aa_pairs])
            else:
                pairs_str = "N/A"
            
            f.write(f"{rank:<6} {res1:<12} {res2:<12} {cov:<12.6f} {pairs_str}\n")
    
    print(f"  Saved enhanced pairs list: {output_file}")


def save_triplet_results(triplets: List[Tuple[str, str, str, float]], output_file: str):
    """Save triplet coevolution results."""
    with open(output_file, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write("TOP COVARYING TRIPLETS (3-WAY COUPLING)\n")
        f.write("=" * 100 + "\n\n")
        f.write("Connected MI > 0 indicates genuine 3-way coevolution beyond pairwise correlations\n\n")
        f.write(f"{'Rank':<6} {'Residue 1':<12} {'Residue 2':<12} {'Residue 3':<12} {'Conn. MI':<12}\n")
        f.write("-" * 100 + "\n")
        
        for rank, (res1, res2, res3, cmi) in enumerate(triplets, 1):
            f.write(f"{rank:<6} {res1:<12} {res2:<12} {res3:<12} {cmi:<12.6f}\n")
    
    print(f"  Saved triplet analysis: {output_file}")


# Import all other functions from v2
import importlib.util
import sys

# Load the v2 module dynamically to reuse functions
script_dir = os.path.dirname(os.path.abspath(__file__))
v2_path = os.path.join(script_dir, "coevolutionary_analysis_v2.py")

spec = importlib.util.spec_from_file_location("coev_v2", v2_path)
coev_v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coev_v2)

# Import needed functions
read_consurf_grades = coev_v2.read_consurf_grades
map_alignment_to_sequence = coev_v2.map_alignment_to_sequence
read_alignment = coev_v2.read_alignment
filter_by_gaps = coev_v2.filter_by_gaps
compute_covariance = coev_v2.compute_covariance
compute_covariance_matrix = coev_v2.compute_covariance_matrix
plot_heatmap = coev_v2.plot_heatmap
get_top_pairs = coev_v2.get_top_pairs
plot_top_pairs = coev_v2.plot_top_pairs
analyze_position = coev_v2.analyze_position
save_summary_stats = coev_v2.save_summary_stats


def main():
    """Main execution."""
    if len(sys.argv) < 3:
        print("Usage: python coevolutionary_analysis_v3.py <MSA_FILE> <OUTPUT_DIR> [OPTIONS]")
        print("\nOptions:")
        print("  --grades-file <file>        ConSurf grades file for residue labeling")
        print("  --max-gap-percent <value>   Max gap % (default: 50)")
        print("  --top-pairs <n>             Number of top pairs (default: 50)")
        print("  --analyze-position <label>  Analyze specific residue (e.g., GLU233)")
        print("  --find-triplets             Search for 3-way coevolution (slower)")
        print("  --triplet-candidates <n>    Max positions to test for triplets (default: 100)")
        sys.exit(1)
    
    msa_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Parse options
    grades_file = None
    max_gap_pct = 50.0
    top_n = 50
    analyze_positions = []
    find_triplets = False
    triplet_candidates = 100
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--grades-file':
            grades_file = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == '--max-gap-percent':
            max_gap_pct = float(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '--top-pairs':
            top_n = int(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '--analyze-position':
            analyze_positions.append(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '--find-triplets':
            find_triplets = True
            i += 1
        elif sys.argv[i] == '--triplet-candidates':
            triplet_candidates = int(sys.argv[i+1])
            i += 2
        else:
            i += 1
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("ENHANCED COEVOLUTIONARY ANALYSIS")
    print("=" * 80)
    print(f"\nInput MSA: {msa_file}")
    print(f"Output directory: {output_dir}")
    if grades_file:
        print(f"Grades file: {grades_file}")
    if find_triplets:
        print(f"Triplet analysis: ENABLED (testing top {triplet_candidates} positions)")
    
    # Read alignment
    print("\nReading alignment...")
    alignment_array, aln_positions = read_alignment(msa_file)
    
    # Map to residue labels
    print("Mapping to residue labels...")
    aln_to_label = map_alignment_to_sequence(msa_file, grades_file)
    print(f"  Mapped {len(aln_to_label)} positions")
    
    # Filter gaps
    filtered_array, filtered_positions, filtered_labels = filter_by_gaps(
        alignment_array, aln_positions, aln_to_label, max_gap_pct
    )
    
    # Compute covariance
    cov_df = compute_covariance_matrix(filtered_array, filtered_positions, filtered_labels)
    
    # Save matrix
    csv_file = os.path.join(output_dir, "covariance_matrix.csv")
    cov_df.to_csv(csv_file)
    print(f"\n  Saved matrix: {csv_file}")
    
    # Summary stats
    stats_file = os.path.join(output_dir, "summary_statistics.txt")
    save_summary_stats(cov_df, stats_file)
    
    # Heatmap
    heatmap_file = os.path.join(output_dir, "covariance_heatmap.png")
    plot_heatmap(cov_df, heatmap_file)
    
    # Top pairs
    print("\nIdentifying top covarying pairs...")
    top_pairs = get_top_pairs(cov_df, top_n)
    
    pairs_plot = os.path.join(output_dir, "top_covarying_pairs.png")
    plot_top_pairs(top_pairs, pairs_plot, top_n)
    
    # Enhanced text output with AA pairs
    pairs_txt = os.path.join(output_dir, "top_covarying_pairs_detailed.txt")
    save_enhanced_top_pairs(top_pairs, filtered_array, filtered_positions, 
                           filtered_labels, pairs_txt, top_n)
    
    # Triplet analysis if requested
    if find_triplets:
        triplets = find_top_triplets(filtered_array, 
                                     list(range(len(filtered_positions))),
                                     filtered_labels,
                                     top_n=20,
                                     max_candidates=triplet_candidates)
        
        if triplets:
            triplet_file = os.path.join(output_dir, "covarying_triplets.txt")
            save_triplet_results(triplets, triplet_file)
    
    # Position-specific analysis
    if analyze_positions:
        print("\nAnalyzing specific positions...")
        for pos_label in analyze_positions:
            out_file = os.path.join(output_dir, f"position_{pos_label}_covariance.png")
            analyze_position(cov_df, pos_label, out_file)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"\nResults in: {output_dir}")


if __name__ == "__main__":
    main()
