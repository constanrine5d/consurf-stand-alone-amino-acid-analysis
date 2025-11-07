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
  - bzip2=1.0.8=h80987f9_6
  - ca-certificates=2025.11.4=hca03da5_0
  - cd-hit=4.8.1=haf7d672_13
  - clustalw=2.1=h4675bf2_12
  - comm=0.2.2=pyhd8ed1ab_1
  - debugpy=1.8.11=py310h313beb8_0
  - decorator=5.1.1=pyhd8ed1ab_1
  - exceptiongroup=1.2.2=pyhd8ed1ab_1
  - executing=2.1.0=pyhd8ed1ab_1
  - expat=2.7.1=h313beb8_0
  - gawk=5.3.1=h8a92848_0
  - gmp=6.3.0=h7bae524_2
  - hmmer=3.4=haef7865_3
  - importlib-metadata=8.6.1=pyha770c72_0
  - ipykernel=6.29.5=py310hca03da5_1
  - ipython=8.32.0=pyh907856f_0
  - ipywidgets=8.1.5=py310hca03da5_0
  - jedi=0.19.2=pyhd8ed1ab_1
  - jsonschema=4.23.0=py310hca03da5_0
  - jsonschema-specifications=2023.7.1=py310hca03da5_0
  - jupyter_client=8.6.3=pyhd8ed1ab_1
  - jupyter_core=5.7.2=pyh31011fe_1
  - jupyterlab_widgets=3.0.13=py310hca03da5_0
  - krb5=1.21.3=h237132a_0
  - libasprintf=0.25.1=h493aca8_0
  - libcxx=19.1.7=ha82da77_0
  - libedit=3.1.20230828=h80987f9_0
  - libffi=3.4.4=hca03da5_1
  - libgettextpo=0.25.1=h493aca8_0
  - libgfortran=5.0.0=11_3_0_hca03da5_28
  - libgfortran5=11.3.0=h009349e_28
  - libiconv=1.18=h23cfdf5_2
  - libintl=0.25.1=h493aca8_0
  - libopenblas=0.3.29=hea593b9_0
  - libsodium=1.0.20=h99b78c6_0
  - libzlib=1.3.1=h5f15de7_0
  - llvm-openmp=20.1.8=he822017_0
  - mafft=7.526=h99b78c6_0
  - matplotlib-inline=0.1.7=pyhd8ed1ab_1
  - mpfr=4.2.1=hb693164_3
  - muscle=5.3=h28ef24b_3
  - narwhals=1.31.0=py310hca03da5_1
  - nbformat=5.10.4=py310hca03da5_0
  - ncurses=6.4=h313beb8_0
  - nest-asyncio=1.6.0=pyhd8ed1ab_1
  - openssl=3.5.4=h5503f6c_0
  - packaging=24.2=pyhd8ed1ab_2
  - parso=0.8.4=pyhd8ed1ab_1
  - pexpect=4.9.0=pyhd8ed1ab_1
  - pickleshare=0.7.5=pyhd8ed1ab_1004
  - pip=25.1=pyhc872135_2
  - platformdirs=4.3.7=py310hca03da5_0
  - plotly=6.0.1=py310hd096484_0
  - prompt-toolkit=3.0.50=pyha770c72_0
  - psutil=5.9.0=py310h80987f9_1
  - ptyprocess=0.7.0=pyhd3eb1b0_2
  - pure_eval=0.2.3=pyhd8ed1ab_1
  - pygments=2.19.1=pyhd8ed1ab_0
  - python=3.10.18=h19e8193_0
  - python-dateutil=2.9.0post0=py310hca03da5_2
  - python-fastjsonschema=2.20.0=py310hca03da5_0
  - pyzmq=26.2.0=py310h313beb8_0
  - readline=8.2=h1a28f6b_0
  - referencing=0.30.2=py310hca03da5_0
  - rpds-py=0.22.3=py310h2aea54e_0
  - setuptools=78.1.1=py310hca03da5_0
  - six=1.17.0=pyhd8ed1ab_0
  - sqlite=3.50.2=h79febb2_1
  - stack_data=0.6.3=pyhd8ed1ab_1
  - tk=8.6.15=hcd8a7d5_0
  - tornado=6.4.2=py310h80987f9_0
  - traitlets=5.14.3=pyhd8ed1ab_1
  - typing_extensions=4.12.2=pyha770c72_1
  - wcwidth=0.2.13=pyhd8ed1ab_1
  - wheel=0.45.1=py310hca03da5_0
  - widgetsnbextension=4.0.13=py310hca03da5_0
  - xz=5.6.4=h80987f9_1
  - zeromq=4.3.5=hc1bb282_7
  - zipp=3.21.0=pyhd8ed1ab_1
  - zlib=1.3.1=h5f15de7_0
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
prefix: /opt/anaconda3/envs/python3.10bio
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
results_final/amino_acids_analysis_results/
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

| Option | Description | Default |
|--------|-------------|---------|
| `-e, --env ENV` | Conda environment name | `python3.10bio` |
| `-r, --results DIR` | Results directory | `./results_final` |
| `-m, --msa FILE` | MSA file path | `results_final/msa_fasta.aln` |
| `-g, --grades FILE` | Grades file path | `results_final/consurf_grades.txt` |
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

