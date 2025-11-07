# ConSurf Stand-Alone with Amino Acid Analysis

A comprehensive toolkit for running ConSurf evolutionary conservation analysis locally, with enhanced amino acid distribution analysis and sequence grouping capabilities.

## 🌟 Features

- **Complete ConSurf Stand-Alone Setup**: Run ConSurf analysis locally without web server dependencies
- **Enhanced Position Analysis**: Analyze amino acid distribution at specific positions
- **Automated Sequence Grouping**: Automatically organize sequences by amino acid at each position
- **FASTA File Generation**: Create organized FASTA files for each amino acid variant
- **Batch Processing**: Analyze single, multiple, or all positions at once
- **Production Ready**: Clean, documented, and easy to deploy

## 📋 Table of Contents

- [Installation](#installation)
- [Database Setup](#database-setup)
- [Quick Start](#quick-start)
- [Amino Acid Analysis](#amino-acid-analysis)
- [Advanced Usage](#advanced-usage)
- [Example Data](#example-data)
- [Troubleshooting](#troubleshooting)
- [Citation](#citation)

## 🔧 Installation

### Prerequisites

- Python 3.8+
- Conda (recommended) or pip
- ~70GB disk space for UniRef90 database

### 1. Install Rate4Site

**Note**: Pre-compiled Rate4Site binaries (v3.0.0) are included in `bin/` for macOS ARM64. If you need a different version or platform:

```bash
# Download from: https://www.tau.ac.il/~itaymay/cp/rate4site.html
# Or use direct link:
wget ftp://rostlab.org/rate4site/rate4site-3.0.0.tar.gz
tar zxvf rate4site-3.0.0.tar.gz
cd rate4site-3.0.0
./configure --prefix=/path/to/install
make
make install
```

If using the included binaries, add to your PATH:
```bash
export PATH="/path/to/consurf-analysis/bin:$PATH"
```

### 2. Create Conda Environment

```bash
conda create --name consurf python=3.8
conda activate consurf

# Install bioinformatics tools
conda install -c bioconda \
    hmmer=3.1 \
    clustalw=2.1 \
    cd-hit \
    mafft=7 \
    prank \
    muscle=3

# Install Python packages
pip install biopython requests
```

### 3. Clone This Repository

```bash
git clone https://github.com/YOUR_USERNAME/consurf-analysis.git
cd consurf-analysis
```

### 4. Configure Paths

Edit `stand_alone_consurf-1.00/GENERAL_CONSTANTS.py`:

```python
# Update these paths to match your installation
CD_HIT_DIR = "/path/to/conda/envs/consurf/bin/cd-hit"
UNIREF90_DB_FASTA = "/path/to/databases/uniref90.fasta"
HMMER_DIR = "/path/to/conda/envs/consurf/bin"
```

## 💾 Database Setup

### Download UniRef90 Database

```bash
# Create database directory
mkdir -p databases
cd databases

# Download UniRef90 (~67GB compressed, ~150GB uncompressed)
wget https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref90/uniref90.fasta.gz

# Decompress
gunzip uniref90.fasta.gz
```

**Note**: This is a one-time setup. The database is not included in this repository due to size.

## 🚀 Quick Start

### Basic ConSurf Analysis

```bash
# Activate environment
conda activate consurf

# Run ConSurf analysis
python stand_alone_consurf-1.00/stand_alone_consurf.py \
    --algorithm HMMER \
    --Maximum_Likelihood \
    --seq your_protein.fasta \
    --dir output_directory
```

### Complete Workflow (Automated)

Use the provided wrapper script:

```bash
./run_consurf_complete.sh your_protein.pdb
```

This will:
1. Extract sequence from PDB
2. Run ConSurf analysis
3. Generate conservation grades
4. Create visualization files

## 🧬 Amino Acid Analysis

### Overview

The amino acid analysis tool creates organized folder structures with FASTA files grouped by amino acid at each position.

### Analyze Single Position

```bash
./analyze_position.sh 226
```

**Output:**
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
        ├── 3_E_4.7/             # Query AA (4.7%)
        │   └── sequences.fasta
        └── ...
```

### Analyze Multiple Positions

```bash
./analyze_position.sh 226 227 228
```

### Analyze All Positions

```bash
./analyze_position.sh --all
# or
./analyze_position.sh
```

**Warning**: This creates folders for ALL positions (typically hundreds).

### Analysis Options

```bash
./analyze_position.sh --help
```

Options:
- `-e, --env ENV`: Conda environment name (default: python3.10bio)
- `-r, --results DIR`: Results directory (default: results_final)
- `-m, --msa FILE`: MSA file path
- `-g, --grades FILE`: Grades file path
- `-o, --output FILE`: Save output to file
- `--all`: Analyze all positions

## 📊 Advanced Usage

### Python API

```python
from analyze_position import analyze_position, analyze_all_positions

# Analyze single position
result = analyze_position(
    msa_file="results_final/msa_fasta.aln",
    grades_file="results_final/consurf_grades.txt",
    position=226,
    output_file="position_226_report.txt",
    create_folders=True
)

# Analyze all positions
results = analyze_all_positions(
    msa_file="results_final/msa_fasta.aln",
    grades_file="results_final/consurf_grades.txt",
    output_file="all_positions_report.txt",
    create_folders=True
)
```

### Custom Analysis

```python
import analyze_position as ap

# Parse MSA with headers
headers, sequences = ap.parse_msa_fasta_with_headers("msa.aln")

# Find alignment position
query_seq = sequences[0]
alignment_pos = ap.find_alignment_position(query_seq, target_position=226)

# Create custom folder structure
ap.create_fasta_files_by_amino_acid(
    msa_file="msa.aln",
    position=226,
    alignment_pos=alignment_pos,
    pdb_position="GLU:233:G",
    results_dir="custom_output"
)
```

## 📁 Repository Structure

```
.
├── README.md                           # This file
├── .gitignore                         # Git ignore rules
├── analyze_position.py                # Amino acid analysis tool
├── analyze_position.sh                # Shell wrapper for analysis
├── run_consurf_complete.sh            # Complete ConSurf workflow
├── setup_databases.sh                 # Database setup helper
├── verify_setup.sh                    # Installation verification
├── AMINO_ACID_ANALYSIS_FEATURE.md    # Detailed feature documentation
├── POSITION_ANALYSIS_README.md       # Position analysis guide
├── bin/                               # Pre-compiled Rate4Site binaries
│   ├── rate4site                      # Rate4Site executable
│   ├── rate4site_doublerep           # Rate4Site double rep version
│   └── consurf                        # ConSurf binary
├── lib/                               # Rate4Site library
│   └── libphylo.a                     # Phylogenetic library
├── include/                           # Header files
│   └── libphylo/                      # Library headers
├── share/                             # Documentation and data
├── stand_alone_consurf-1.00/         # Original ConSurf scripts
│   ├── stand_alone_consurf.py        # Main ConSurf script
│   ├── GENERAL_CONSTANTS.py          # Configuration file
│   └── ...                            # Supporting modules
└── example/                           # Example data (TtXyn30A)
    ├── TtXyn30A_WT.pdb               # Example protein structure
    ├── r4s.res                        # Example Rate4Site results
    └── results_final/                 # Complete example analysis
        ├── msa_fasta.aln             # Multiple sequence alignment
        ├── consurf_grades.txt        # Conservation grades
        └── amino_acids_analysis_results/  # Position analyses
```

## 📖 Example Data

An example analysis of TtXyn30A (Thermoanaerobacterium thermosulfurigenes xylanase) is included in the `example/` directory.

### Run Example

```bash
cd example
# View pre-computed results
ls -la results_final/

# Or re-run analysis
../run_consurf_complete.sh TtXyn30A_WT.pdb

# Analyze specific position
../analyze_position.sh -r results_final 226
```

### Example Position: GLU:233

Position 226 (PDB: GLU:233:G) shows interesting variation:
- Query AA: E (Glutamic acid) - only 4.67%
- Most common: N (Asparagine) - 60.00%
- Total: 15 different amino acids observed

See `example/results_final/amino_acids_analysis_results/position_226_GLU_233_G/` for details.

## 🔍 Troubleshooting

### Rate4Site Issues

**Problem**: `rate4site: errorMsg.cpp:41: Assertion failed`

**Solution**: Use Maximum Likelihood mode (`--Maximum_Likelihood` flag)

**Problem**: Negative likelihood values with `-im` mode

**Solution**: Use `-ib` mode (Bayesian) instead. This is enforced by the `--Maximum_Likelihood` flag.

### Database Issues

**Problem**: HMMER search fails

**Solution**: Verify UniRef90 database path in `GENERAL_CONSTANTS.py` and ensure file is decompressed.

### Python Dependencies

**Problem**: Import errors

**Solution**: 
```bash
conda activate consurf
pip install biopython requests
```

### Permission Issues

**Problem**: Scripts not executable

**Solution**:
```bash
chmod +x *.sh
chmod +x analyze_position.py
```

## 📚 Documentation

- [Amino Acid Analysis Feature](AMINO_ACID_ANALYSIS_FEATURE.md) - Detailed documentation
- [Position Analysis Guide](POSITION_ANALYSIS_README.md) - Analysis workflow guide
- [ConSurf Official](https://consurf.tau.ac.il/) - Original web server
- [Rate4Site Manual](https://www.tau.ac.il/~itaymay/cp/rate4site.html) - Rate4Site documentation

## 🧪 Use Cases

1. **Mutation Analysis**: Identify which sequences share specific amino acids at positions of interest
2. **Variant Study**: Compare sequences with different residues at key positions
3. **Conservation Patterns**: Understand evolutionary constraints at specific sites
4. **Structural Biology**: Group sequences by residue types for structural comparisons
5. **Protein Engineering**: Identify tolerated substitutions for mutagenesis studies

## 📝 Citation

### ConSurf
```
Ashkenazy H., et al. (2016)
ConSurf 2016: an improved methodology to estimate and visualize 
evolutionary conservation in macromolecules
Nucleic Acids Research, 44(W1), W344-W350
```

### Rate4Site
```
Mayrose I., et al. (2004)
Comparison of site-specific rate-inference methods for protein sequences: 
empirical Bayesian methods are superior
Molecular Biology and Evolution, 21(9), 1781-1791
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This tool builds upon ConSurf stand-alone (available from tau.ac.il) and Rate4Site. Please respect their respective licenses.

The amino acid analysis enhancements are provided as-is for research purposes.

## 👤 Authors

- Original ConSurf: Haim Ashkenazy, Penn O., Doron-Faigenboim A., Cohen O., Cannarozzi G., Zomer O., Pupko T.
- Amino Acid Analysis Enhancement: [Your Name]

## 🔗 Links

- [ConSurf Web Server](https://consurf.tau.ac.il/)
- [ConSurf Database](https://consurfdb.tau.ac.il/)
- [Rate4Site](https://www.tau.ac.il/~itaymay/cp/rate4site.html)
- [UniProt UniRef](https://www.uniprot.org/help/uniref)

---

**Last Updated**: November 7, 2025
