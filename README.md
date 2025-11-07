# ConSurf Stand-Alone with Amino Acid Analysis

> **Forked from**: [leezx/ConSurf-StandAlone](https://github.com/leezx/ConSurf-StandAlone)  
> **Original source**: [Rostlab/ConSurf](https://github.com/Rostlab/ConSurf)

ConSurf evolutionary conservation analysis with added amino acid distribution analysis and sequence grouping.

**Note**: This repository was created with AI assistance ("vibe-coded") and may contain errors or incomplete configurations. It is intended for personal/research use only. Please verify all settings and paths for your specific environment before use.

## What's New

- Amino acid distribution analysis at specific positions
- Automated sequence grouping by amino acid into FASTA files
- Organized folder structure: `position_X/covered/1_AA_60.0/sequences.fasta`
- Batch processing for single, multiple, or all positions
- Numbered workflow scripts (1-4) for easy execution order

## Usage

### Workflow Scripts

Execute in order:

1. `1_setup_databases.sh` - Setup databases
2. `2_verify_setup.sh` - Verify installation of all modules
3. `3_run_consurf_complete.sh` - Run ConSurf analysis
4. `4_analyze_position.sh` - Analyze amino acid distribution

### Amino Acid Analysis

```bash
# Analyze single position
./4_analyze_position.sh 226

# Analyze multiple positions
./4_analyze_position.sh 226 227 228

# Analyze all positions
./4_analyze_position.sh --all
```

### Output Structure

```
results_final/amino_acids_analysis_results/
└── position_226_GLU_233_G/
    ├── not_covered/              # Sequences with gaps
    │   └── sequences.fasta
    └── covered/
        ├── 1_N_60.0/            # Most common (60%)
        │   └── sequences.fasta
        ├── 2_T_7.7/             # Second (7.7%)
        │   └── sequences.fasta
        └── ...
```

## Repository Structure

```
.
├── analyze_position.py           # Core analysis tool
├── 1_setup_databases.sh          # Database setup
├── 2_verify_setup.sh             # Verify installation
├── 3_run_consurf_complete.sh     # Run ConSurf
├── 4_analyze_position.sh         # Analyze positions
├── bin/                          # Pre-compiled binaries
├── stand_alone_consurf-1.00/     # ConSurf scripts
└── example/                      # Example data (TtXyn30A)
```

## Requirements

- Python 3.10
- Conda environment with: hmmer, clustalw, cd-hit, mafft, muscle
- Rate4Site (binaries included for macOS ARM64)
- UniRef90 database (~150GB)

See original repos for detailed installation instructions.

## Example Data

The `example/` folder contains a complete TtXyn30A analysis with results.

## Authors & Attribution

### Original ConSurf
- Original Repo: https://github.com/Rostlab/ConSurf

### Amino Acid Analysis Enhancement
- Author: Konstantinos Grigorakis
- Contributions: Position analysis, sequence grouping, automated FASTA organization

## Citation

If using ConSurf, cite as per the original repo.

## Links

- [ConSurf Web Server](https://consurf.tau.ac.il/)
- [Rate4Site](https://www.tau.ac.il/~itaymay/cp/rate4site.html)
- [UniProt UniRef](https://www.uniprot.org/help/uniref)
