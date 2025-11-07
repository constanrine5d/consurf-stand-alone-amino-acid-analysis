#!/usr/bin/env python3
"""
Analyze amino acid distribution at specific positions in ConSurf MSA
"""

import sys
import argparse
from collections import Counter
from pathlib import Path
import os


def parse_msa_fasta_with_headers(msa_file):
    """Parse FASTA format MSA file, returning both headers and sequences"""
    sequences = []
    headers = []
    with open(msa_file, 'r') as f:
        current_seq = []
        current_header = None
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_seq and current_header:
                    sequences.append(''.join(current_seq))
                    headers.append(current_header)
                    current_seq = []
                current_header = line
            else:
                current_seq.append(line)
        if current_seq and current_header:
            sequences.append(''.join(current_seq))
            headers.append(current_header)
    return headers, sequences


def parse_msa_fasta(msa_file):
    """Parse FASTA format MSA file"""
    _, sequences = parse_msa_fasta_with_headers(msa_file)
    return sequences


def find_alignment_position(query_seq, target_position):
    """
    Find alignment position corresponding to query sequence position.
    target_position is 1-indexed (as in PDB/grades file)
    """
    query_position = 0
    for i, aa in enumerate(query_seq):
        if aa != '-':
            query_position += 1
            if query_position == target_position:
                return i
    return None


def create_fasta_files_by_amino_acid(msa_file, position, alignment_pos, pdb_position, results_dir):
    """
    Create folder structure with FASTA files organized by amino acid at position.
    
    Structure:
    results_dir/amino_acids_analysis_results/position_X_PDB_Y/
        ├── not_covered/
        │   └── sequences.fasta
        └── covered/
            ├── 1_AA_XX.X/
            │   └── sequences.fasta
            ├── 2_AA_XX.X/
            │   └── sequences.fasta
            ...
    """
    # Read MSA with headers
    headers, sequences = parse_msa_fasta_with_headers(msa_file)
    
    # Create base directory structure
    base_dir = Path(results_dir) / "amino_acids_analysis_results"
    base_dir.mkdir(exist_ok=True)
    
    # Clean PDB position for folder name (remove colons)
    pdb_clean = pdb_position.replace(':', '_') if pdb_position else 'NA'
    position_dir = base_dir / f"position_{position}_{pdb_clean}"
    position_dir.mkdir(exist_ok=True)
    
    # Create not_covered and covered directories
    not_covered_dir = position_dir / "not_covered"
    not_covered_dir.mkdir(exist_ok=True)
    
    covered_dir = position_dir / "covered"
    covered_dir.mkdir(exist_ok=True)
    
    # Organize sequences by amino acid
    aa_sequences = {}  # {aa: [(header, sequence), ...]}
    gap_sequences = []  # [(header, sequence), ...]
    
    for header, seq in zip(headers, sequences):
        aa = seq[alignment_pos]
        if aa == '-':
            gap_sequences.append((header, seq))
        else:
            if aa not in aa_sequences:
                aa_sequences[aa] = []
            aa_sequences[aa].append((header, seq))
    
    # Write not_covered sequences
    if gap_sequences:
        not_covered_file = not_covered_dir / "sequences.fasta"
        with open(not_covered_file, 'w') as f:
            for header, seq in gap_sequences:
                f.write(f"{header}\n{seq}\n")
        print(f"  ✓ Not covered: {len(gap_sequences)} sequences → {not_covered_file}")
    
    # Count total non-gap for percentages
    total_non_gap = sum(len(seqs) for seqs in aa_sequences.values())
    
    # Sort amino acids by count (descending)
    sorted_aa = sorted(aa_sequences.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Write covered sequences, one folder per amino acid
    for rank, (aa, seqs) in enumerate(sorted_aa, 1):
        count = len(seqs)
        percentage = (count / total_non_gap) * 100 if total_non_gap > 0 else 0
        
        # Create folder name: rank_AA_percentage
        folder_name = f"{rank}_{aa}_{percentage:.1f}"
        aa_dir = covered_dir / folder_name
        aa_dir.mkdir(exist_ok=True)
        
        # Write sequences to FASTA file
        aa_file = aa_dir / "sequences.fasta"
        with open(aa_file, 'w') as f:
            for header, seq in seqs:
                f.write(f"{header}\n{seq}\n")
        
        print(f"  ✓ {rank}. {aa} ({percentage:.1f}%): {count} sequences → {aa_file}")
    
    print(f"\n✓ Folder structure created: {position_dir}")
    return position_dir


def analyze_position(msa_file, grades_file, position, output_file=None, create_folders=True):
    """Analyze amino acid distribution at a specific position"""
    
    # Read MSA
    sequences = parse_msa_fasta(msa_file)
    query_seq = sequences[0]
    
    # Find alignment position
    alignment_pos = find_alignment_position(query_seq, position)
    
    if alignment_pos is None:
        print(f"ERROR: Position {position} not found in query sequence")
        return None
    
    # Get query amino acid
    query_aa = query_seq[alignment_pos]
    
    # Count amino acids at this position
    aa_at_position = []
    for seq in sequences:
        aa = seq[alignment_pos]
        if aa != '-':
            aa_at_position.append(aa)
    
    aa_counts = Counter(aa_at_position)
    total_non_gap = len(aa_at_position)
    
    # Read grades file to get PDB position
    pdb_position = None
    grades_line = None
    with open(grades_file, 'r') as f:
        for line in f:
            if line.strip().startswith(str(position) + '\t'):
                grades_line = line.strip()
                parts = line.split()
                if len(parts) >= 3:
                    pdb_position = parts[2]
                break
    
    # Prepare output
    result = []
    result.append("=" * 80)
    result.append(f"AMINO ACID DISTRIBUTION ANALYSIS")
    result.append("=" * 80)
    result.append(f"Position in sequence: {position}")
    result.append(f"PDB position: {pdb_position if pdb_position else 'N/A'}")
    result.append(f"Alignment position: {alignment_pos + 1}")
    result.append(f"Query amino acid: {query_aa}")
    result.append(f"Total sequences: {len(sequences)}")
    result.append(f"Sequences with amino acid (non-gap): {total_non_gap}/{len(sequences)}")
    result.append("")
    
    # Sort by count
    sorted_aa = sorted(aa_counts.items(), key=lambda x: x[1], reverse=True)
    
    result.append(f"{'AA':<5} {'Count':<10} {'%':<10} {'Cumulative %':<15} {'Bar'}")
    result.append("-" * 80)
    
    cumulative = 0
    for aa, count in sorted_aa:
        percentage = (count / total_non_gap) * 100
        cumulative += percentage
        bar = '█' * int(percentage / 2)
        marker = ' ← Query' if aa == query_aa else ''
        result.append(f"{aa:<5} {count:<10} {percentage:>6.2f}%   {cumulative:>6.2f}%        {bar}{marker}")
    
    result.append("")
    result.append("=" * 80)
    
    # Chemical properties summary
    hydrophobic = ['A', 'V', 'I', 'L', 'M', 'F', 'Y', 'W']
    polar = ['S', 'T', 'N', 'Q', 'C']
    charged_pos = ['K', 'R', 'H']
    charged_neg = ['D', 'E']
    special = ['G', 'P']
    
    def calc_group_pct(group):
        return sum((aa_counts.get(aa, 0) / total_non_gap) * 100 for aa in group)
    
    result.append("CHEMICAL PROPERTIES DISTRIBUTION:")
    result.append("-" * 80)
    result.append(f"Hydrophobic (A,V,I,L,M,F,Y,W):  {calc_group_pct(hydrophobic):>6.2f}%")
    result.append(f"Polar uncharged (S,T,N,Q,C):    {calc_group_pct(polar):>6.2f}%")
    result.append(f"Positively charged (K,R,H):     {calc_group_pct(charged_pos):>6.2f}%")
    result.append(f"Negatively charged (D,E):       {calc_group_pct(charged_neg):>6.2f}%")
    result.append(f"Special (G,P):                  {calc_group_pct(special):>6.2f}%")
    result.append("=" * 80)
    
    # Print to stdout
    output_text = '\n'.join(result)
    print(output_text)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output_text + '\n')
        print(f"\nResults saved to: {output_file}")
    
    # Create folder structure with FASTA files
    if create_folders:
        print("\nCreating folder structure with FASTA files...")
        results_dir = Path(msa_file).parent
        create_fasta_files_by_amino_acid(msa_file, position, alignment_pos, pdb_position, results_dir)
    
    return {
        'position': position,
        'pdb_position': pdb_position,
        'query_aa': query_aa,
        'total_sequences': len(sequences),
        'non_gap': total_non_gap,
        'distribution': dict(aa_counts)
    }


def analyze_all_positions(msa_file, grades_file, output_file, create_folders=True):
    """Analyze all positions in the sequence and save to file"""
    
    # Read grades file to get all positions
    positions = []
    with open(grades_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('*') and not line.startswith('POS'):
                parts = line.split()
                if len(parts) >= 3 and parts[0].isdigit():
                    positions.append(int(parts[0]))
    
    if not positions:
        print("ERROR: No positions found in grades file")
        return None
    
    print(f"Analyzing all {len(positions)} positions...")
    print(f"Output file: {output_file}")
    print()
    
    # Read MSA once (with headers for folder creation)
    headers, sequences = parse_msa_fasta_with_headers(msa_file)
    query_seq = sequences[0]
    total_seqs = len(sequences)
    
    results = []
    results_dir = Path(msa_file).parent
    
    with open(output_file, 'w') as f:
        # Write header
        f.write("=" * 100 + "\n")
        f.write("AMINO ACID DISTRIBUTION ANALYSIS - ALL POSITIONS\n")
        f.write("=" * 100 + "\n")
        f.write(f"Total positions: {len(positions)}\n")
        f.write(f"Total sequences in MSA: {total_seqs}\n")
        f.write(f"Analysis date: {Path(output_file).stat().st_mtime}\n")
        f.write("=" * 100 + "\n\n")
        
        # Analyze each position
        for i, pos in enumerate(positions, 1):
            if i % 50 == 0:
                print(f"Progress: {i}/{len(positions)} positions analyzed...")
            
            # Find alignment position
            alignment_pos = find_alignment_position(query_seq, pos)
            if alignment_pos is None:
                continue
            
            query_aa = query_seq[alignment_pos]
            
            # Count amino acids
            aa_at_position = []
            for seq in sequences:
                aa = seq[alignment_pos]
                if aa != '-':
                    aa_at_position.append(aa)
            
            aa_counts = Counter(aa_at_position)
            total_non_gap = len(aa_at_position)
            
            # Get PDB position from grades file
            pdb_position = None
            with open(grades_file, 'r') as gf:
                for line in gf:
                    if line.strip().startswith(str(pos) + '\t'):
                        parts = line.split()
                        if len(parts) >= 3:
                            pdb_position = parts[2]
                        break
            
            # Write to file
            f.write("-" * 100 + "\n")
            f.write(f"Position {pos} | PDB: {pdb_position if pdb_position else 'N/A'} | Query: {query_aa} | Coverage: {total_non_gap}/{total_seqs}\n")
            f.write("-" * 100 + "\n")
            
            # Sort by count
            sorted_aa = sorted(aa_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Write distribution
            for aa, count in sorted_aa:
                percentage = (count / total_non_gap) * 100
                marker = '*' if aa == query_aa else ' '
                f.write(f"{marker} {aa}  {count:>4}  {percentage:>6.2f}%  ")
                # Bar chart
                bar = '█' * int(percentage / 2)
                f.write(bar + '\n')
            
            f.write("\n")
            
            # Create folder structure for this position
            if create_folders:
                create_fasta_files_by_amino_acid(msa_file, pos, alignment_pos, pdb_position, results_dir)
            
            # Store for summary
            results.append({
                'position': pos,
                'pdb_position': pdb_position,
                'query_aa': query_aa,
                'total_sequences': total_seqs,
                'non_gap': total_non_gap,
                'distribution': dict(aa_counts),
                'top_aa': sorted_aa[0][0] if sorted_aa else None,
                'top_pct': (sorted_aa[0][1] / total_non_gap * 100) if sorted_aa else 0
            })
        
        # Write summary at the end
        f.write("\n" + "=" * 100 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 100 + "\n\n")
        
        # Query amino acid matches top amino acid
        matches = sum(1 for r in results if r['query_aa'] == r['top_aa'])
        f.write(f"Positions where query AA is most common: {matches}/{len(results)} ({matches/len(results)*100:.1f}%)\n\n")
        
        # Most conserved positions (>80% one amino acid)
        highly_conserved = [r for r in results if r['top_pct'] > 80]
        f.write(f"Highly conserved positions (>80% one AA): {len(highly_conserved)}\n")
        for r in highly_conserved[:20]:  # Show top 20
            f.write(f"  Pos {r['position']} ({r['pdb_position']}): {r['top_aa']} {r['top_pct']:.1f}%\n")
        if len(highly_conserved) > 20:
            f.write(f"  ... and {len(highly_conserved) - 20} more\n")
        f.write("\n")
        
        # Most variable positions (<30% for any amino acid)
        highly_variable = [r for r in results if r['top_pct'] < 30]
        f.write(f"Highly variable positions (<30% for any AA): {len(highly_variable)}\n")
        for r in highly_variable[:20]:  # Show top 20
            f.write(f"  Pos {r['position']} ({r['pdb_position']}): {r['top_aa']} {r['top_pct']:.1f}%\n")
        if len(highly_variable) > 20:
            f.write(f"  ... and {len(highly_variable) - 20} more\n")
        
        f.write("\n" + "=" * 100 + "\n")
    
    print(f"\n✓ Analysis complete!")
    print(f"  Analyzed: {len(results)} positions")
    print(f"  Output: {output_file}")
    if create_folders:
        print(f"  Folder structure: {results_dir}/amino_acids_analysis_results/")
    
    return results


def analyze_multiple_positions(msa_file, grades_file, positions, output_file=None, create_folders=True):
    """Analyze multiple positions"""
    results = []
    
    for pos in positions:
        print(f"\n{'='*80}")
        print(f"Analyzing position {pos}...")
        print('='*80 + '\n')
        result = analyze_position(msa_file, grades_file, pos, create_folders=create_folders)
        if result:
            results.append(result)
        print()
    
    # Summary
    if len(results) > 1 and output_file:
        summary_file = output_file.replace('.txt', '_summary.txt')
        with open(summary_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("SUMMARY OF MULTIPLE POSITIONS\n")
            f.write("=" * 80 + "\n\n")
            
            for r in results:
                f.write(f"Position {r['position']} ({r['pdb_position']}): {r['query_aa']}\n")
                f.write(f"  Sequences: {r['non_gap']}/{r['total_sequences']}\n")
                
                # Top 3 amino acids
                sorted_dist = sorted(r['distribution'].items(), key=lambda x: x[1], reverse=True)[:3]
                f.write(f"  Top 3: ")
                for aa, count in sorted_dist:
                    pct = (count / r['non_gap']) * 100
                    f.write(f"{aa}({pct:.1f}%) ")
                f.write("\n\n")
        
        print(f"\nSummary saved to: {summary_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze amino acid distribution at specific positions in ConSurf MSA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # All positions (saved to file)
  python analyze_position.py -m msa_fasta.aln -g consurf_grades.txt --all
  
  # Single position
  python analyze_position.py -m msa_fasta.aln -g consurf_grades.txt -p 226
  
  # Multiple positions
  python analyze_position.py -m msa_fasta.aln -g consurf_grades.txt -p 226 227 228
  
  # Save to file
  python analyze_position.py -m msa_fasta.aln -g consurf_grades.txt -p 226 -o position_226.txt
        """
    )
    
    parser.add_argument('-m', '--msa', required=True,
                        help='Path to MSA file (FASTA format)')
    parser.add_argument('-g', '--grades', required=True,
                        help='Path to consurf_grades.txt file')
    parser.add_argument('-p', '--positions', nargs='+', type=int,
                        help='Position(s) to analyze (1-indexed, as in grades file)')
    parser.add_argument('--all', action='store_true',
                        help='Analyze all positions (saved to file automatically)')
    parser.add_argument('-o', '--output', 
                        help='Output file (optional for single/multiple positions, auto-generated for --all)')
    
    args = parser.parse_args()
    
    # Check files exist
    for f in [args.msa, args.grades]:
        if not Path(f).exists():
            print(f"ERROR: File not found: {f}")
            sys.exit(1)
    
    # Analyze positions
    if args.all:
        # All positions mode
        if not args.output:
            # Auto-generate output filename
            msa_dir = Path(args.msa).parent
            args.output = str(msa_dir / "amino_acid_distribution_all_positions.txt")
        analyze_all_positions(args.msa, args.grades, args.output)
    elif args.positions:
        # Specific positions
        if len(args.positions) == 1:
            analyze_position(args.msa, args.grades, args.positions[0], args.output)
        else:
            analyze_multiple_positions(args.msa, args.grades, args.positions, args.output)
    else:
        print("ERROR: Must specify either --all or -p/--positions")
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
