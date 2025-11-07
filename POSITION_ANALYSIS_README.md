# ConSurf Position Analysis Tool

Analyze amino acid distribution at specific positions in ConSurf multiple sequence alignments (MSA).

## Files

- `analyze_position.py` - Python script for analyzing positions
- `analyze_position.sh` - Bash wrapper script with conda environment support

## Quick Start

### Single Position
```bash
./analyze_position.sh 226
```

### Multiple Positions
```bash
./analyze_position.sh 226 227 228 229
```

### Save Output to File
```bash
./analyze_position.sh -o position_226_analysis.txt 226
```

### Use Different Results Directory
```bash
./analyze_position.sh -r /path/to/results 226
```

## Configuration Options

The shell script accepts the following options:

| Option | Description | Default |
|--------|-------------|---------|
| `-e, --env ENV` | Conda environment name | `python3.10bio` |
| `-r, --results DIR` | Results directory | `/Users/constanrine5d/programs/ConSurf/results_final` |
| `-m, --msa FILE` | MSA file path | `results_final/msa_fasta.aln` |
| `-g, --grades FILE` | Grades file path | `results_final/consurf_grades.txt` |
| `-o, --output FILE` | Save output to file | (none - prints to stdout) |
| `-h, --help` | Show help message | |

## Output Format

The analysis provides:

1. **Position Information**
   - Position in sequence (1-indexed)
   - PDB position (e.g., GLU:233:G)
   - Alignment position
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

## Example Output

```
Position: 226 (GLU:233:G)
Query amino acid: E
Total sequences: 150

AA    Count      %          Cumulative %    Bar
--------------------------------------------------------------
N     80        53.33%      53.33%        ██████████████████████████
E     9          6.00%      59.33%        ███ ← Query
T     9          6.00%      65.33%        ███
Q     8          5.33%      70.67%        ██
...

CHEMICAL PROPERTIES:
Hydrophobic:           24.00%
Polar uncharged:       69.33%
Positively charged:     0.67%
Negatively charged:     6.00%
```

## Finding Positions of Interest

To find a specific residue position in the grades file:

```bash
grep "GLU:233" results_final/consurf_grades.txt
```

Output:
```
226   E   GLU:233:G   -0.960   7   -1.132, -0.860   ...
```

The first column (226) is the position number to use with this tool.

## Direct Python Usage

You can also run the Python script directly:

```bash
python3 analyze_position.py \
  -m results_final/msa_fasta.aln \
  -g results_final/consurf_grades.txt \
  -p 226 227 228
```

## How ConSurf Selects Sequences

### Current Setup (150 sequences)
- **Found by HMMER**: 163,846 sequences
- **After CD-HIT clustering** (95% identity): 4,000 unique sequences
- **Final MSA**: 150 sequences (default limit)

### Why 150 Sequences?

The default `--MAX_HOMOLOGS 150` parameter limits the final MSA to 150 sequences because:

1. **Computational efficiency**: Rate4site runtime increases with sequence count
2. **Alignment quality**: Too many sequences can introduce gaps and noise
3. **Diminishing returns**: Beyond ~150 sequences, conservation signal plateaus
4. **Historical standard**: Based on ConSurf webserver best practices

### Using More Sequences

You can increase the number of sequences used:

```bash
cd stand_alone_consurf-1.00
python stand_alone_consurf.py \
  --pdb ../TtXyn30A_WT.pdb \
  --chain G \
  --dir ../results_final_300 \
  --algorithm HMMER \
  --MIN_ID 10 \
  --cutoff 0.001 \
  --MAX_HOMOLOGS 300
```

**Or use all available sequences:**

```bash
python stand_alone_consurf.py \
  --pdb ../TtXyn30A_WT.pdb \
  --chain G \
  --dir ../results_final_all \
  --algorithm HMMER \
  --MIN_ID 10 \
  --cutoff 0.001 \
  --MAX_HOMOLOGS all
```

### Trade-offs

| Sequences | Pros | Cons |
|-----------|------|------|
| 150 (default) | Fast (~3 min rate4site), good signal | May miss rare variants |
| 300-500 | Better sampling, more variants | Slower (6-10 min), more gaps |
| All (~4000) | Complete sampling | Very slow (30+ min), alignment issues |

### Recommended Settings

- **Standard analysis**: 150 sequences (default)
- **High confidence needed**: 300 sequences
- **Exploring rare variants**: 500-1000 sequences
- **Publication quality**: Test multiple values (150, 300, 500)

## Interpreting Results

### High Percentage (>50%)
Position is highly conserved for that amino acid across evolution.

### Even Distribution
Position is highly variable - many amino acids tolerated.

### Chemical Property Dominance
- **Polar >60%**: Surface-exposed, H-bonding important
- **Hydrophobic >50%**: Buried, core stability role
- **Charged >40%**: Catalytic site or binding pocket

### Query Amino Acid is Rare (<10%)
Your protein has an unusual residue at this position - could indicate:
- Species-specific adaptation
- Functional specialization
- Potential mutation site for engineering

## Tips

1. **Conserved positions** (grade 9) usually show >70% for one amino acid
2. **Variable positions** (grade 1-3) show diverse distribution
3. **Active sites** often show specific chemical property bias
4. **Interface residues** may show alternating patterns

## Troubleshooting

### "File not found" errors
- Check that ConSurf analysis has completed
- Verify the results directory path
- Ensure `msa_fasta.aln` and `consurf_grades.txt` exist

### "Position not found" errors
- Position numbers are 1-indexed (as in grades file)
- Maximum position = length of your protein
- Check position exists: `grep "^  226" consurf_grades.txt`

### Conda environment issues
- Activate manually first: `conda activate python3.10bio`
- Or specify different environment: `./analyze_position.sh -e myenv 226`

## Related Files

- `amino_acid_variety_analysis.txt` - Overall variety statistics across all positions
- `consurf_grades.txt` - Full conservation grades for all positions
- `msa_fasta.aln` - Multiple sequence alignment
- `r4s.res` - Raw rate4site conservation scores

## Citation

If you use this analysis in publications, please cite:
- ConSurf: Ashkenazy H, et al. (2016) Nucleic Acids Res. 44(W1):W344-50
- This tool: Custom analysis script for position-specific AA distribution
