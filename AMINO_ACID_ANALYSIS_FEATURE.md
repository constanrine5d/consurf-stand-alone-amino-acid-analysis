# Amino Acid Distribution Analysis - Enhanced Feature

## Overview

The position analysis script now automatically creates organized folder structures with FASTA files grouped by amino acid at each analyzed position.

## Feature Description

When analyzing any position, the script creates:

```
results_final/amino_acids_analysis_results/
└── position_X_PDB_Y/
    ├── not_covered/
    │   └── sequences.fasta          # Sequences with gaps (-) at this position
    └── covered/
        ├── 1_AA_XX.X/
        │   └── sequences.fasta      # Top amino acid with percentage
        ├── 2_AA_XX.X/
        │   └── sequences.fasta      # Second most common
        ├── 3_AA_XX.X/
        │   └── sequences.fasta      # Third most common
        └── ...                       # One folder per amino acid found
```

## Folder Naming Convention

- **Base folder**: `position_{SEQ_POS}_{PDB_POSITION}`
  - Example: `position_226_GLU_233_G`
  - PDB position has colons replaced with underscores

- **Amino acid folders**: `{RANK}_{AA}_{PERCENTAGE}`
  - Example: `1_N_60.0` for the most common amino acid (N at 60%)
  - Example: `3_E_4.7` for query amino acid E at position 3 (4.7%)
  - Percentage is rounded to 1 decimal place

## Usage Examples

### Analyze Single Position

```bash
./analyze_position.sh 226
```

**Output:**
- Text report printed to console
- Folder: `results_final/amino_acids_analysis_results/position_226_GLU_233_G/`
- 15 amino acid folders created (N, T, E, V, Q, S, F, L, I, A, M, W, G, Y, R)
- Each contains `sequences.fasta` with all sequences having that amino acid

### Analyze Multiple Positions

```bash
./analyze_position.sh 226 227 228
```

Creates separate folder structures for each position.

### Analyze All Positions

```bash
./analyze_position.sh --all
```

**Warning:** This creates folders for ALL positions (hundreds). Use only when needed.

## File Contents

Each `sequences.fasta` file contains:
- Original FASTA headers from MSA
- Complete aligned sequences (including gaps elsewhere)
- Only sequences that have the specific amino acid at the analyzed position

### Example: Position 226, Amino Acid N (60%)

```
>tr|A0ABZ0W6E1|A0ABZ0W6E1_9BACT_start_73_end_462_Evalue_1.1e-09
---AIQVDSSQAFQGIDGFGYTLTGGSATLIN---------Q---LS-APVKA---ALLQELFG-NDE...
>tr|A0A1I2CZL8|A0A1I2CZL8_9FLAO_start_71_end_454_Evalue_1.1e-11
----IEVDDTKTFQTIDGFGYTLTGGSAQVIN---------Q---LN-AQKRQ---ELLKELFG-NND...
```

## Use Cases

1. **Mutation Analysis**: Extract sequences with specific amino acids for comparison
2. **Variant Study**: Analyze sequences that differ from query at specific positions
3. **Conservation Patterns**: Identify sequence groups with similar substitutions
4. **Phylogenetic Analysis**: Group sequences by amino acid variants
5. **Structural Biology**: Study sequences with similar/different residues at key positions

## Position 226 (GLU:233:G) Example

This position shows:
- **Query AA**: E (Glutamic acid) - only 4.67% (14 sequences)
- **Most common**: N (Asparagine) - 60.00% (180 sequences)
- **Total coverage**: 300/300 sequences (no gaps)

**Distribution:**
1. N - 60.0% (180 sequences)
2. T - 7.7% (23 sequences)
3. **E - 4.7% (14 sequences)** ← Query amino acid
4. V - 4.7% (14 sequences)
5. Q - 4.0% (12 sequences)
... and 10 more amino acids

## Technical Details

- **FASTA preservation**: Original headers and sequences maintained
- **Alignment intact**: All gaps and alignments preserved
- **Sorting**: Folders ranked by frequency (most common = rank 1)
- **Coverage**: Only non-gap positions counted for percentages
- **Automatic**: No manual intervention needed

## Notes

- The `not_covered/` folder is only created if sequences have gaps at that position
- All amino acids found are included, even those with single occurrences
- Folder creation happens automatically for all analysis modes (single, multiple, all)
- Original MSA file is never modified

## Location

All analysis results are stored in:
```
results_final/amino_acids_analysis_results/
```

This keeps the analysis organized and separate from other ConSurf outputs.
