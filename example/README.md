# Example: TtXyn30A Analysis

This directory contains a complete example analysis of **TtXyn30A** (Thermoanaerobacterium thermosulfurigenes xylanase 30A).

## 📁 Contents

```
example/
├── README.md                    # This file
├── TtXyn30A_WT.pdb             # Input protein structure
├── TtXyn30A_WT.pdb.MODRES      # Modified residues info
├── r4s.res                      # Rate4Site results
└── results_final/               # Complete analysis results
    ├── msa_fasta.aln           # Multiple sequence alignment (FASTA format)
    ├── msa_clustal.aln         # Multiple sequence alignment (Clustal format)
    ├── consurf_grades.txt      # Conservation grades for each position
    ├── protein_seq.fas         # Query protein sequence
    ├── TheTree.txt             # Phylogenetic tree
    ├── log.txt                 # Analysis log file
    └── amino_acids_analysis_results/  # Position-specific analyses
        └── position_226_GLU_233_G/    # Example: Position 226 analysis
            ├── not_covered/
            └── covered/
                ├── 1_N_60.0/
                ├── 2_T_7.7/
                ├── 3_E_4.7/
                └── ...
```

## 🧬 About TtXyn30A

- **Protein**: Xylanase 30A
- **Organism**: *Thermoanaerobacterium thermosulfurigenes*
- **Function**: Glycoside hydrolase family 30, degrades xylan
- **PDB Structure**: TtXyn30A_WT.pdb
- **Sequence Length**: 239 amino acids (analyzed positions)

## 📊 Analysis Summary

### Conservation Statistics

From `results_final/consurf_grades.txt`:
- **Total positions analyzed**: 239
- **Total sequences in MSA**: 300
- **Highly conserved positions (>80%)**: Multiple catalytic and structural residues
- **Variable positions (<30%)**: Surface loops and non-essential regions

### Interesting Position: GLU:233 (Position 226)

Located in a functionally important region, this position shows:

- **Query Amino Acid**: E (Glutamic acid) - **only 4.67%** of sequences
- **Most Common**: N (Asparagine) - **60.00%** of sequences
- **Total Coverage**: 300/300 sequences (100% coverage, no gaps)

**Full Distribution:**
1. N (Asparagine) - 60.0% - 180 sequences
2. T (Threonine) - 7.7% - 23 sequences
3. **E (Glutamic acid)** - 4.7% - 14 sequences ← Query
4. V (Valine) - 4.7% - 14 sequences
5. Q (Glutamine) - 4.0% - 12 sequences
6. S (Serine) - 4.0% - 12 sequences
7. F (Phenylalanine) - 3.7% - 11 sequences
8. L (Leucine) - 3.0% - 9 sequences
9. I (Isoleucine) - 2.3% - 7 sequences
10. A (Alanine) - 2.3% - 7 sequences
11. M (Methionine) - 1.7% - 5 sequences
12. W (Tryptophan) - 0.7% - 2 sequences
13. G (Glycine) - 0.7% - 2 sequences
14. Y (Tyrosine) - 0.3% - 1 sequence
15. R (Arginine) - 0.3% - 1 sequence

**Chemical Properties:**
- Polar uncharged (S,T,N,Q,C): 75.67%
- Hydrophobic (A,V,I,L,M,F,Y,W): 18.67%
- Negatively charged (D,E): 4.67%
- Positively charged (K,R,H): 0.33%
- Special (G,P): 0.67%

This suggests that while the query has a charged residue, most homologs have polar uncharged residues at this position, indicating potential functional divergence or adaptation.

## 🚀 Re-run Analysis

To reproduce this analysis from scratch:

```bash
# From main repository directory
./run_consurf_complete.sh example/TtXyn30A_WT.pdb

# Or step by step:
cd example

# 1. Run ConSurf
python ../stand_alone_consurf-1.00/stand_alone_consurf.py \
    --algorithm HMMER \
    --Maximum_Likelihood \
    --seq protein_seq.fas \
    --dir results_final

# 2. Analyze specific position
../analyze_position.sh -r results_final 226

# 3. Analyze all positions
../analyze_position.sh -r results_final --all
```

## 📖 Explore the Results

### View Conservation Grades

```bash
# View all positions with conservation scores
less results_final/consurf_grades.txt

# Find specific positions
grep "GLU:233" results_final/consurf_grades.txt
```

### Examine MSA

```bash
# View multiple sequence alignment
less results_final/msa_fasta.aln

# Count sequences
grep -c "^>" results_final/msa_fasta.aln
```

### Check Amino Acid Distribution

```bash
# View summary report
less results_final/amino_acid_distribution_all_positions.txt

# Browse position-specific FASTA files
cd results_final/amino_acids_analysis_results/position_226_GLU_233_G/covered/
ls -la

# View sequences with Asparagine (most common)
less 1_N_60.0/sequences.fasta

# View sequences with Glutamic acid (query)
less 3_E_4.7/sequences.fasta
```

## 🔬 Use Cases for This Example

1. **Learning**: Understand ConSurf output format and interpretation
2. **Testing**: Verify your installation works correctly
3. **Benchmarking**: Compare your results with these reference results
4. **Method Development**: Use as test data for new analysis methods
5. **Teaching**: Demonstrate evolutionary conservation analysis

## 📚 Related Files

- `TtXyn30A_WT.pdb` - PDB structure file (can be visualized with PyMOL, Chimera, etc.)
- `consurf_grades.txt` - Conservation scores (can be mapped onto structure)
- `TheTree.txt` - Phylogenetic tree (can be visualized with FigTree, iTOL, etc.)

## 💡 Tips

- The amino acid distribution folders are organized by rank and percentage
- Sequences in each folder share the same amino acid at the analyzed position
- Original FASTA headers are preserved for traceability
- All alignments are intact (gaps preserved)

## 🔗 References

If you use this example data, please cite:
- ConSurf: Ashkenazy H., et al. (2016) *Nucleic Acids Research* 44(W1), W344-W350
- Original protein structure: Check PDB database for TtXyn30A citations

---

**Note**: This is example data. For publication-quality analysis, verify parameters and consider protein-specific requirements.
