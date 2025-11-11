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
- Enzyme characterization check using UniProt API
- Numbered workflow scripts (1-5) for easy execution order

## Complete Workflow Guide

### Prerequisites

Before starting, ensure you have:

1. **Conda environment** with bioinformatics tools:
   - hmmer, clustalw, cd-hit, mafft, muscle
   - Python 3.10+ with biopython and requests

2. **Database setup**: 
   - Edit `DB_DIR` variable in `1_setup_databases.sh` if databases are not at `/Volumes/const_2tb/consurf_databases`
   - Or skip script 1 if databases are already set up

3. **PDB file**: Your protein structure file (e.g., `protein.pdb`)

### Step-by-Step Execution

#### Step 1: Setup Databases (Optional)

If databases are not already configured:

```bash
# Edit the DB_DIR path in the script first
nano 1_setup_databases.sh  # Change line 10: DB_DIR="/your/path/consurf_databases"

# Then run
./1_setup_databases.sh
```

This script:
- Downloads Swiss-Prot database (~90MB compressed, ~300MB uncompressed)
- Extracts TrEMBL database if present (optional, ~94GB)
- Formats databases for BLAST searching
- Takes 15-30 minutes depending on drive speed

**Note**: You can skip this if databases are already set up elsewhere. Just ensure paths in `2_verify_setup.sh` match your setup.

#### Step 2: Verify Installation

```bash
./2_verify_setup.sh
```

Checks for:
- Python packages (biopython, requests, tqdm)
- Alignment tools (CLUSTALW, MUSCLE, MAFFT)
- HMMER tools (jackhmmer, hmmbuild, hmmsearch)
- CD-HIT clustering tool
- Rate4Site binary
- Database files and sizes

Expected output: All ✅ checks should pass. If any fail, install the missing tools.

#### Step 3: Run ConSurf Analysis

```bash
./3_run_consurf_complete.sh <PDB_FILE> <CHAIN_ID> [OUTPUT_DIR]
```

Example:
```bash
./3_run_consurf_complete.sh example.pdb A
# Or with custom output directory:
./3_run_consurf_complete.sh example.pdb A results/results_example
```

This script:
- Activates conda environment automatically
- Runs BLAST/HMMER search against protein databases
- Performs CD-HIT clustering at 95% identity
- Selects top 150 sequences (default, configurable)
- Builds multiple sequence alignment (MSA)
- Calculates conservation scores with Rate4Site
- Generates ConSurf grades (1-9, where 9 = highly conserved)
- Takes ~40-60 minutes for a typical protein

**Output files**:
```
results/results_example/
├── consurf_grades.txt          # Conservation scores (1-9)
├── msa_fasta.aln              # Multiple sequence alignment
├── r4s.res                    # Rate4Site results
├── TheTree.txt                # Phylogenetic tree
├── query_final_homolougs.fasta # Selected sequences
└── example_With_Conservation_Scores.pdb  # Annotated PDB
```

#### Step 4: Analyze Amino Acid Distribution

Analyze amino acid variability at each position:

```bash
# Analyze all positions (recommended)
./4_analyze_position.sh results/results_example

# Or analyze specific positions
./4_analyze_position.sh results/results_example 226        # Single position
./4_analyze_position.sh results/results_example 226 227 228  # Multiple positions
```

This script:
- Reads MSA and conservation grades
- Calculates amino acid distribution at each position
- Groups sequences by amino acid into separate FASTA files
- Creates organized folder structure
- Takes ~5-10 minutes for all positions

**Output structure**:
```
results/results_example/amino_acids_analysis_results/
├── position_1_MET_1_A/
│   ├── not_covered/
│   │   └── sequences.fasta           # Sequences with gaps (-)
│   └── covered/
│       ├── 1_M_85.2/                # 85.2% have Methionine
│       │   └── sequences.fasta       # 186 sequences
│       ├── 2_L_7.4/                 # 7.4% have Leucine
│       │   └── sequences.fasta       # 16 sequences
│       └── ...
├── position_2_SER_2_A/
└── ...
```

**Folder naming convention**:
- Position folder: `position_{SEQ_POS}_{PDB_AA}_{PDB_NUM}_{CHAIN}`
- Amino acid folder: `{RANK}_{AA}_{PERCENTAGE}`

#### Step 5: Check Enzyme Characterization

Query UniProt to determine if sequences are from characterized enzymes:

```bash
# Analyze all sequences.fasta files recursively
./5_check_characterized_enzymes.sh results/results_example

# Or analyze a specific file
./5_check_characterized_enzymes.sh results/results_example --file path/to/sequences.fasta
```

This script:
- Extracts UniProt IDs from FASTA headers
- Queries UniProt API in batches (optimized)
- Analyzes unique proteins from all sequence files
- Retrieves protein names and publication counts
- Categorizes sequences by characterization level
- Takes ~2-5 minutes for complete analysis

**Output**: Creates `enzyme_characterization_report.txt` next to each `sequences.fasta`:

```
=================================================================
ENZYME CHARACTERIZATION REPORT
=================================================================
Analysis Date: 2025-11-11 10:45:23
Total Sequences: 50

SUMMARY
-----------------------------------------------------------------
Reviewed (Swiss-Prot):     0 sequences  (0.0%)
Well-studied (5+ pubs):    0 sequences  (0.0%)
Characterized:            45 sequences (90.0%)
Uncharacterized:           5 sequences (10.0%)

DETAILED RESULTS
-----------------------------------------------------------------

CHARACTERIZED PROTEINS (45):
tr|A0A1D8PFG7|A0A1D8PFG7_CANAL    Glucan 1,3-beta-glucosidase (Pubs: 0)
tr|A0A286XZ89|A0A286XZ89_9PEZI    Glucan endo-1,3-beta-glucosidase (Pubs: 2)
...

UNCHARACTERIZED PROTEINS (5):
tr|A0A0D2YZ45|A0A0D2YZ45_9ASCO    Uncharacterized protein (Pubs: 0)
...
```

**Categories**:
- **Reviewed (Swiss-Prot)**: Manually curated, high confidence
- **Well-studied (5+ publications)**: Extensively researched
- **Characterized**: Has protein name, may have 0-4 publications
- **Uncharacterized**: No functional annotation

#### Step 6: Generate PyMOL Visualization

Create a PyMOL session with ConSurf conservation coloring:

```bash
./6_generate_pymol_session.sh results/results_example
```

This script:
- Loads PDB structure with conservation scores
- Applies ConSurf color scale (turquoise → white → purple)
- Creates cartoon representation
- Adds visual color scale legend
- Takes ~30 seconds

**Output**: Creates `consurf_session.pse` in results directory

**To view**:
```bash
pymol results/results_example/consurf_session.pse
```

**Color Scale**:
- Grade 9 (Purple) → Highly Conserved
- Grade 5 (White) → Average/Neutral
- Grade 1 (Turquoise) → Variable
- Gray (80%) → Insufficient Data

### Complete Run Summary

For a typical protein (549 amino acids):

| Step | Time | Key Outputs |
|------|------|-------------|
| 1. Setup Databases | 15-30 min | Database files formatted for BLAST |
| 2. Verify Setup | 1 min | Confirmation all tools installed |
| 3. ConSurf Analysis | 40-60 min | Conservation scores, MSA, tree |
| 4. Position Analysis | 5-10 min | Position folders with FASTA files |
| 5. Enzyme Check | 2-5 min | Characterization reports |
| 6. PyMOL Session | 30 sec | Visual conservation mapping |
| **Total** | **~1-2 hours** | **Complete evolutionary analysis** |

### Understanding the Results

**Conservation Grades (1-9)**:
- **9**: Highly conserved (≤10% variability) - likely functionally critical
- **7-8**: Moderately conserved - potentially important for structure/function  
- **4-6**: Variable - may be surface-exposed or adaptable
- **1-3**: Highly variable - likely not functionally constrained

**Amino Acid Distribution**:
- High percentage (>70%) for one AA = highly conserved position
- Even distribution = highly variable position
- Chemical property bias (e.g., all charged) = functional constraint

**Characterization Reports**:
- Use to identify sequences from well-studied vs. uncharacterized organisms
- Filter by publication count for comparative studies
- Cross-reference with known mutants or variants

## Quick Start Example

```bash
# 1. Verify everything is installed
./2_verify_setup.sh

# 2. Run complete analysis on your protein
./3_run_consurf_complete.sh example.pdb A

# 3. Analyze all positions
./4_analyze_position.sh results/results_example

# 4. Check enzyme characterization
./5_check_characterized_enzymes.sh results/results_example

# 5. Generate PyMOL visualization
./6_generate_pymol_session.sh results/results_example

# 6. View in PyMOL
pymol results/results_example/consurf_session.pse
```

## Usage

See **[Complete Workflow Guide](#complete-workflow-guide)** above for detailed step-by-step instructions.

### Quick Reference

**Basic workflow**:
```bash
./2_verify_setup.sh                                # Verify installation
./3_run_consurf_complete.sh protein.pdb A          # Run ConSurf (auto: results/results_protein)
./4_analyze_position.sh results/results_protein    # Analyze all positions
./5_check_characterized_enzymes.sh results/results_protein  # Check characterization
./6_generate_pymol_session.sh results/results_protein      # Create visualization
```

**Individual script options**:
```bash
# Position analysis
./4_analyze_position.sh results/results_example 226          # Single position
./4_analyze_position.sh results/results_example 226 227 228  # Multiple positions

# Enzyme characterization
./5_check_characterized_enzymes.sh results/results_example                        # All files
./5_check_characterized_enzymes.sh results/results_example --file path/to/sequences.fasta  # Specific file
```

### Output Structure

```
results/results_example/amino_acids_analysis_results/
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
├── check_characterized_enzymes.py # UniProt enzyme checker
├── 1_setup_databases.sh          # Database setup
├── 2_verify_setup.sh             # Verify installation
├── 3_run_consurf_complete.sh     # Run ConSurf
├── 4_analyze_position.sh         # Analyze positions
├── 5_check_characterized_enzymes.sh # Check enzyme status
├── bin/                          # Pre-compiled binaries
├── stand_alone_consurf-1.00/     # ConSurf scripts
├── environment.yml               # Conda environment export
└── example/                      # Example data (TtXyn30A)
```

## Requirements

- Python 3.10+
- Conda environment with: hmmer, clustalw, cd-hit, mafft, muscle, biopython
- Python packages: requests (for UniProt API queries)
```
name: python3.10bio
channels:
  - conda-forge
  - defaults
  - bioconda
  - https://repo.anaconda.com/pkgs/main
  - https://repo.anaconda.com/pkgs/r
dependencies:
  - appnope=0.1.4=pyhd8ed1ab_1
  - asttokens=3.0.0=pyhd8ed1ab_1
  - attrs=24.3.0=py310hca03da5_0
  - biopython=1.78=py310h1a28f6b_0
  - blas=1.0=openblas
  - blosc=1.21.6=h7dd00d9_1
  - bzip2=1.0.8=h80987f9_6
  - c-ares=1.34.5=h5505292_0
  - ca-certificates=2025.11.4=hca03da5_0
  - cairo=1.18.0=hc6c324b_2
  - cd-hit=4.8.1=haf7d672_13
  - clustalw=2.1=h4675bf2_12
  - comm=0.2.2=pyhd8ed1ab_1
  - cyrus-sasl=2.1.28=ha1cbb27_0
  - debugpy=1.8.11=py310h313beb8_0
  - decorator=5.1.1=pyhd8ed1ab_1
  - exceptiongroup=1.2.2=pyhd8ed1ab_1
  - executing=2.1.0=pyhd8ed1ab_1
  - expat=2.7.1=h313beb8_0
  - font-ttf-dejavu-sans-mono=2.37=hab24e00_0
  - font-ttf-inconsolata=3.000=h77eed37_0
  - font-ttf-source-code-pro=2.038=h77eed37_0
  - font-ttf-ubuntu=0.83=h77eed37_3
  - fontconfig=2.15.0=h1383a14_1
  - fonts-conda-ecosystem=1=0
  - fonts-conda-forge=1=hc364b38_1
  - freetype=2.14.1=hce30654_0
  - gawk=5.3.1=h8a92848_0
  - gettext=0.25.1=h3dcc1bd_0
  - gettext-tools=0.25.1=h493aca8_0
  - glew=2.2.0=hba38e01_0
  - glm=1.0.1=h6597b73_0
  - gmp=6.3.0=h7bae524_2
  - graphite2=1.3.14=hec049ff_2
  - harfbuzz=10.2.0=he637ebf_1
  - hdf4=4.2.13=h5e329fb_3
  - hdf5=1.14.5=hd77251f_2
  - hmmer=3.4=haef7865_3
  - icu=73.2=hc8870d7_0
  - importlib-metadata=8.6.1=pyha770c72_0
  - ipykernel=6.29.5=py310hca03da5_1
  - ipython=8.32.0=pyh907856f_0
  - ipywidgets=8.1.5=py310hca03da5_0
  - jedi=0.19.2=pyhd8ed1ab_1
  - jpeg=9e=h1a8c8d9_3
  - jsonschema=4.23.0=py310hca03da5_0
  - jsonschema-specifications=2023.7.1=py310hca03da5_0
  - jupyter_client=8.6.3=pyhd8ed1ab_1
  - jupyter_core=5.7.2=pyh31011fe_1
  - jupyterlab_widgets=3.0.13=py310hca03da5_0
  - krb5=1.21.3=h237132a_0
  - libaec=1.1.4=h51d1e36_0
  - libasprintf=0.25.1=h493aca8_0
  - libasprintf-devel=0.25.1=h493aca8_0
  - libcurl=8.17.0=hdece5d2_0
  - libcxx=19.1.7=ha82da77_0
  - libedit=3.1.20230828=h80987f9_0
  - libev=4.33=h93a5062_2
  - libexpat=2.7.1=hec049ff_0
  - libffi=3.4.4=hca03da5_1
  - libfreetype=2.14.1=hce30654_0
  - libfreetype6=2.14.1=h6da58f4_0
  - libgettextpo=0.25.1=h493aca8_0
  - libgettextpo-devel=0.25.1=h493aca8_0
  - libgfortran=5.0.0=11_3_0_hca03da5_28
  - libgfortran5=11.3.0=h009349e_28
  - libglib=2.84.2=hdc2269c_0
  - libiconv=1.18=h23cfdf5_2
  - libintl=0.25.1=h493aca8_0
  - libintl-devel=0.25.1=h493aca8_0
  - libkrb5=1.21.3=h73ed823_4
  - libnetcdf=4.9.3=h56724e0_0
  - libnghttp2=1.67.0=hc438710_0
  - libntlm=1.8=h5505292_0
  - libopenblas=0.3.29=hea593b9_0
  - libpng=1.6.50=h280e0eb_1
  - libpq=17.6=h479fd88_0
  - libsodium=1.0.20=h99b78c6_0
  - libsqlite=3.51.0=h9a5124b_0
  - libssh2=1.11.1=h1590b86_0
  - libxcb=1.17.0=hdb1d25a_0
  - libxml2=2.13.9=h528a072_0
  - libzip=1.11.2=h1336266_0
  - libzlib=1.3.1=h5f15de7_0
  - llvm-openmp=20.1.8=he822017_0
  - lmdb=0.9.31=h93a5062_1
  - lz4-c=1.10.0=h286801f_1
  - mafft=7.526=h99b78c6_0
  - matplotlib-inline=0.1.7=pyhd8ed1ab_1
  - mpfr=4.2.1=hb693164_3
  - muscle=5.3=h28ef24b_3
  - mysql-common=9.3.0=hd7719f6_0
  - mysql-libs=9.3.0=ha8be5b7_0
  - narwhals=1.31.0=py310hca03da5_1
  - nbformat=5.10.4=py310hca03da5_0
  - ncurses=6.4=h313beb8_0
  - nest-asyncio=1.6.0=pyhd8ed1ab_1
  - openldap=2.6.10=hbe55e7a_0
  - openssl=3.6.0=h5503f6c_0
  - packaging=24.2=pyhd8ed1ab_2
  - parso=0.8.4=pyhd8ed1ab_1
  - pcre2=10.42=h26f9a81_0
  - pexpect=4.9.0=pyhd8ed1ab_1
  - pickleshare=0.7.5=pyhd8ed1ab_1004
  - pip=25.1=pyhc872135_2
  - pixman=0.46.4=h81086ad_1
  - platformdirs=4.3.7=py310hca03da5_0
  - plotly=6.0.1=py310hd096484_0
  - ply=3.11=pyhd8ed1ab_3
  - pmw=2.1.1=py310hbe9552e_0
  - prompt-toolkit=3.0.50=pyha770c72_0
  - psutil=5.9.0=py310h80987f9_1
  - pthread-stubs=0.4=hd74edd7_1002
  - ptyprocess=0.7.0=pyhd3eb1b0_2
  - pure_eval=0.2.3=pyhd8ed1ab_1
  - pygments=2.19.1=pyhd8ed1ab_0
  - pymol-open-source=3.1.0=py310hacbed85_2
  - pyqt=6.9.1=py310h9be6068_0
  - pyqt6-sip=13.10.2=py310h45c6bc8_0
  - python=3.10.13=h2469fbe_1_cpython
  - python-dateutil=2.9.0post0=py310hca03da5_2
  - python-fastjsonschema=2.20.0=py310hca03da5_0
  - python_abi=3.10=8_cp310
  - pyzmq=26.2.0=py310h313beb8_0
  - qtbase=6.9.2=h44406b1_3
  - qtdeclarative=6.9.2=hfc17e28_1
  - qtsvg=6.9.2=h310a915_1
  - qttools=6.9.2=hd987465_1
  - qtwebchannel=6.9.2=hfc17e28_1
  - qtwebsockets=6.9.2=hfc17e28_1
  - readline=8.2=h1a28f6b_0
  - referencing=0.30.2=py310hca03da5_0
  - rpds-py=0.22.3=py310h2aea54e_0
  - setuptools=78.1.1=py310hca03da5_0
  - sip=6.12.0=py310h1af2607_1
  - six=1.17.0=pyhd8ed1ab_0
  - snappy=1.2.2=hd121638_0
  - sqlite=3.50.2=h79febb2_1
  - stack_data=0.6.3=pyhd8ed1ab_1
  - tk=8.6.15=hcd8a7d5_0
  - tornado=6.4.2=py310h80987f9_0
  - traitlets=5.14.3=pyhd8ed1ab_1
  - typing_extensions=4.12.2=pyha770c72_1
  - wcwidth=0.2.13=pyhd8ed1ab_1
  - wheel=0.45.1=py310hca03da5_0
  - widgetsnbextension=4.0.13=py310hca03da5_0
  - xorg-libx11=1.8.12=h6a5fb8c_0
  - xorg-libxau=1.0.12=h5505292_0
  - xorg-libxdmcp=1.1.5=hd74edd7_0
  - xorg-libxfixes=6.0.2=hc919400_0
  - xz=5.6.4=h80987f9_1
  - zeromq=4.3.5=hc1bb282_7
  - zipp=3.21.0=pyhd8ed1ab_1
  - zlib=1.3.1=h5f15de7_0
  - zstd=1.5.7=h6491c7d_2
  - pip:
      - acpype==2023.10.27
      - certifi==2025.4.26
      - charset-normalizer==3.4.2
      - contourpy==1.3.1
      - cycler==0.12.1
      - defusedxml==0.7.1
      - delphi4py==1.3.0
      - et-xmlfile==2.0.0
      - fonttools==4.57.0
      - idna==3.10
      - iniconfig==2.0.0
      - kiwisolver==1.4.8
      - matplotlib==3.10.1
      - networkx==3.4.2
      - numpy==1.26.4
      - odfpy==1.4.1
      - openbabel-wheel==3.1.1.21
      - openpyxl==3.1.5
      - pandas==2.2.3
      - pdbmender==0.6.1
      - pillow==11.1.0
      - pluggy==1.5.0
      - pyparsing==3.2.3
      - pypka==2.10.0
      - pytest==8.3.4
      - pytz==2025.2
      - requests==2.32.3
      - scipy==1.15.2
      - tomli==2.2.1
      - tqdm==4.67.1
      - tzdata==2025.2
      - urllib3==2.4.0
```
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

---

## Amino Acid Distribution Analysis Feature

### Overview

The position analysis script automatically creates organized folder structures with FASTA files grouped by amino acid at each analyzed position.

### Feature Description

When analyzing any position, the script creates:

```
<RESULTS_DIR>/amino_acids_analysis_results/
└── position_X_PDB_Y/
    ├── not_covered/
    │   └── sequences.fasta          # Sequences with gaps (-) at this position
    └── covered/
        ├── 1_AA_XX.X/
        │   └── sequences.fasta      # Top amino acid with percentage
        ├── 2_AA_XX.X/
        │   └── sequences.fasta      # Second most common
        └── ...                       # One folder per amino acid found
```
### Folder Naming Convention

- **Base folder**: `position_{SEQ_POS}_{PDB_POSITION}`
  - Example: `position_226_GLU_233_G`
- **Amino acid folders**: `{RANK}_{AA}_{PERCENTAGE}`
  - Example: `1_N_60.0` for the most common amino acid (N at 60%)

### Use Cases

1. **Mutation Analysis**: Extract sequences with specific amino acids for comparison
2. **Variant Study**: Analyze sequences that differ from query at specific positions
3. **Conservation Patterns**: Identify sequence groups with similar substitutions
4. **Phylogenetic Analysis**: Group sequences by amino acid variants
5. **Structural Biology**: Study sequences with similar/different residues at key positions

---

## Position Analysis Tool Details

### Configuration Options

The shell script accepts the following options:

| Option | Description | Required/Default |
|--------|-------------|------------------|
| `RESULTS_DIR` | Results directory (positional) | **Required** |
| `-e, --env ENV` | Conda environment name | `python3.10bio` |
| `-m, --msa FILE` | MSA file path | `<RESULTS_DIR>/msa_fasta.aln` |
| `-g, --grades FILE` | Grades file path | `<RESULTS_DIR>/consurf_grades.txt` |
| `-o, --output FILE` | Save output to file | (none) |

### Output Format

The analysis provides:

1. **Position Information**
   - Position in sequence (1-indexed)
   - PDB position (e.g., GLU:233:G)
   - Query amino acid

2. **Amino Acid Distribution**
   - Count and percentage of each amino acid
   - Cumulative percentage
   - Visual bar chart
   - Query amino acid marked with ←

3. **Chemical Properties Summary**
   - Hydrophobic (A,V,I,L,M,F,Y,W)
   - Polar uncharged (S,T,N,Q,C)
   - Positively charged (K,R,H)
   - Negatively charged (D,E)
   - Special (G,P)

### Interpreting Results

- **High Percentage (>50%)**: Position is highly conserved
- **Even Distribution**: Position is highly variable
- **Chemical Property Dominance**: 
  - Polar >60%: Surface-exposed, H-bonding important
  - Hydrophobic >50%: Buried, core stability role
  - Charged >40%: Catalytic site or binding pocket
- **Query Amino Acid is Rare (<10%)**: Unusual residue, potential mutation site

### ConSurf Sequence Selection

**Current Setup (150 sequences)**:
- Found by HMMER: ~160,000 sequences
- After CD-HIT clustering (95% identity): ~4,000 unique sequences
- Final MSA: 150 sequences (default limit)

**Why 150 Sequences?**
1. Computational efficiency
2. Alignment quality
3. Diminishing returns beyond ~150
4. ConSurf webserver best practices

**Using More Sequences:**
```bash
python stand_alone_consurf.py --MAX_HOMOLOGS 300
# or
python stand_alone_consurf.py --MAX_HOMOLOGS all
```

**Trade-offs:**
- 150 (default): Fast (~3 min), good signal
- 300-500: Better sampling, slower (6-10 min)
- All (~4000): Complete sampling, very slow (30+ min)

### Tips

1. Conserved positions (grade 9) usually show >70% for one amino acid
2. Variable positions (grade 1-3) show diverse distribution
3. Active sites often show specific chemical property bias
4. Interface residues may show alternating patterns

