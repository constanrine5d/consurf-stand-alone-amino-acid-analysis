#!/usr/bin/env python3
"""
Check if sequences in a FASTA file are from characterized enzymes.
Queries UniProt API to check for reviewed (Swiss-Prot) entries and protein names.
"""

import re
import time
import requests
from pathlib import Path
from collections import defaultdict

def extract_uniprot_ids(fasta_file):
    """Extract UniProt IDs from FASTA headers."""
    ids = set()
    with open(fasta_file) as f:
        for line in f:
            if line.startswith('>'):
                # Format: >tr|A0ABZ0W6E1|A0ABZ0W6E1_9BACT_start_73_end_462_Evalue_1.1e-09
                match = re.search(r'\|([A-Z0-9]+)\|', line)
                if match:
                    ids.add(match.group(1))
    return sorted(ids)

def query_uniprot_batch(ids, batch_size=100):
    """
    Query UniProt REST API for protein information.
    Returns dict with ID -> protein info.
    """
    results = {}
    base_url = "https://rest.uniprot.org/uniprotkb/search"
    
    # Process in batches
    for i in range(0, len(ids), batch_size):
        batch = ids[i:i+batch_size]
        query = " OR ".join([f"accession:{id}" for id in batch])
        
        params = {
            'query': query,
            'format': 'tsv',
            'fields': 'accession,reviewed,protein_name,organism_name,ec,gene_names,length,lit_pubmed_id',
            'size': batch_size
        }
        
        print(f"  Querying batch {i//batch_size + 1}/{(len(ids)-1)//batch_size + 1}...")
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse TSV response
            lines = response.text.strip().split('\n')
            if len(lines) > 1:  # Skip header
                for line in lines[1:]:
                    parts = line.split('\t')
                    if len(parts) >= 8:
                        accession = parts[0]
                        # Parse PubMed IDs (semicolon separated)
                        pubmed_ids = []
                        if parts[7]:
                            pubmed_ids = [pid.strip() for pid in parts[7].split(';') if pid.strip()]
                        
                        results[accession] = {
                            'reviewed': parts[1] == 'reviewed',
                            'protein_name': parts[2],
                            'organism': parts[3],
                            'ec': parts[4] if parts[4] else None,
                            'gene': parts[5] if parts[5] else None,
                            'length': parts[6],
                            'pubmed_ids': pubmed_ids,
                            'pub_count': len(pubmed_ids)
                        }
            
            # Rate limiting - be nice to UniProt
            time.sleep(0.5)
            
        except requests.RequestException as e:
            print(f"  Warning: Batch query failed: {e}")
            continue
    
    return results

def generate_report(ids, results, detailed=False):
    """Generate a text report from analysis results."""
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("ENZYME CHARACTERIZATION ANALYSIS")
    output_lines.append("=" * 80)
    output_lines.append(f"Total sequences: {len(ids)}")
    output_lines.append(f"Sequences with UniProt data: {len(results)}")
    output_lines.append("")
    
    # Count statistics
    reviewed_count = sum(1 for info in results.values() if info['reviewed'])
    with_ec = sum(1 for info in results.values() if info['ec'])
    with_pubs = sum(1 for info in results.values() if info['pub_count'] > 0)
    
    output_lines.append("SUMMARY STATISTICS")
    output_lines.append("-" * 80)
    output_lines.append(f"Reviewed (Swiss-Prot): {reviewed_count}")
    output_lines.append(f"With EC number: {with_ec}")
    output_lines.append(f"With publications: {with_pubs}")
    output_lines.append("")
    
    # List all sequences with their information
    output_lines.append("SEQUENCE INFORMATION")
    output_lines.append("-" * 80)
    
    for acc in sorted(results.keys()):
        info = results[acc]
        output_lines.append(f"{acc}")
        output_lines.append(f"  Name: {info['protein_name']}")
        output_lines.append(f"  Organism: {info['organism']}")
        output_lines.append(f"  Reviewed: {'Yes' if info['reviewed'] else 'No'}")
        if info['ec']:
            output_lines.append(f"  EC: {info['ec']}")
        if info['gene']:
            output_lines.append(f"  Gene: {info['gene']}")
        output_lines.append(f"  Length: {info['length']} aa")
        output_lines.append(f"  Publications: {info['pub_count']}")
        if detailed and info['pubmed_ids']:
            pubmed_display = info['pubmed_ids'][:10]
            output_lines.append(f"    PubMed IDs: {', '.join(pubmed_display)}")
            if info['pub_count'] > 10:
                output_lines.append(f"    ... and {info['pub_count'] - 10} more")
        output_lines.append("")
    
    return '\n'.join(output_lines)

def analyze_single_fasta(fasta_file, output_file=None, detailed=False):
    """Analyze a single FASTA file."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {fasta_file}")
    print('='*80)
    
    ids = extract_uniprot_ids(fasta_file)
    print(f"Found {len(ids)} unique UniProt IDs")
    
    results = query_uniprot_batch(ids)
    print(f"Retrieved information for {len(results)}/{len(ids)} sequences")
    
    report = generate_report(ids, results, detailed)
    
    # Determine output file location
    if output_file is None:
        # Place report in same directory as FASTA file
        fasta_path = Path(fasta_file)
        output_file = fasta_path.parent / "enzyme_characterization_report.txt"
    
    Path(output_file).write_text(report)
    print(f"\n✓ Report saved to: {output_file}")
    
    return results

def analyze_all_fastas(base_dir, detailed=False):
    """Find and analyze all sequences.fasta files in amino_acids_analysis_results.
    Optimized: queries UniProt once for all unique IDs across all files."""
    base_path = Path(base_dir)
    analysis_dir = base_path / "amino_acids_analysis_results"
    
    if not analysis_dir.exists():
        print(f"Error: Directory not found: {analysis_dir}")
        return 1
    
    # Find all sequences.fasta files
    fasta_files = list(analysis_dir.glob("**/sequences.fasta"))
    
    if not fasta_files:
        print(f"No sequences.fasta files found in {analysis_dir}")
        return 1
    
    print(f"Found {len(fasta_files)} FASTA files to analyze")
    print(f"\n{'='*80}")
    print("PHASE 1: Collecting all UniProt IDs from all FASTA files")
    print('='*80)
    
    # Collect all unique IDs and map each file to its IDs
    all_ids = set()
    file_id_map = {}
    
    for i, fasta_file in enumerate(sorted(fasta_files), 1):
        print(f"[{i}/{len(fasta_files)}] Scanning {fasta_file.relative_to(base_path)}")
        try:
            ids = extract_uniprot_ids(fasta_file)
            file_id_map[fasta_file] = ids
            all_ids.update(ids)
        except Exception as e:
            print(f"  ✗ Error reading file: {e}")
            file_id_map[fasta_file] = []
    
    print(f"\n✓ Collected {len(all_ids)} unique UniProt IDs across all files")
    
    # Query UniProt once for all IDs
    print(f"\n{'='*80}")
    print("PHASE 2: Querying UniProt for all unique IDs (this may take a few minutes)")
    print('='*80)
    
    all_ids_sorted = sorted(all_ids)
    all_results = query_uniprot_batch(all_ids_sorted)
    
    print(f"\n✓ Retrieved information for {len(all_results)}/{len(all_ids)} sequences")
    
    # Generate reports for each file using cached data
    print(f"\n{'='*80}")
    print("PHASE 3: Generating reports for each FASTA file")
    print('='*80)
    
    for i, fasta_file in enumerate(sorted(fasta_files), 1):
        print(f"\n[{i}/{len(fasta_files)}] Processing {fasta_file.relative_to(base_path)}")
        
        try:
            ids = file_id_map[fasta_file]
            
            # Filter results for this specific file
            file_results = {id: all_results[id] for id in ids if id in all_results}
            
            # Generate report
            report = generate_report(ids, file_results, detailed)
            
            # Save report next to FASTA file
            output_file = fasta_file.parent / "enzyme_characterization_report.txt"
            Path(output_file).write_text(report)
            
            # Count statistics for display
            reviewed = sum(1 for info in file_results.values() if info['reviewed'])
            with_ec = sum(1 for info in file_results.values() if info['ec'])
            with_pubs = sum(1 for info in file_results.values() if info['pub_count'] > 0)
            
            print(f"  ✓ Report saved: {output_file.relative_to(base_path)}")
            print(f"    Total: {len(file_results)}, Reviewed: {reviewed}, With EC: {with_ec}, With pubs: {with_pubs}")
            
        except Exception as e:
            print(f"  ✗ Error generating report: {e}")
            continue
    
    print(f"\n{'='*80}")
    print(f"✓ Completed analysis of {len(fasta_files)} files")
    print(f"  Total unique proteins analyzed: {len(all_results)}")
    print('='*80)
    return 0

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Check if FASTA sequences are characterized enzymes')
    parser.add_argument('input', nargs='?', default='all', 
                       help='Input FASTA file or directory (default: "all" - analyze all FASTA files)')
    parser.add_argument('-o', '--output', help='Output report file (only for single file mode)')
    parser.add_argument('--detailed', action='store_true', help='Show all sequences')
    parser.add_argument('--base-dir', default='./example/results_final',
                       help='Base directory for "all" mode (default: ./example/results_final)')
    
    args = parser.parse_args()
    
    if args.input == 'all':
        # Analyze all FASTA files
        return analyze_all_fastas(args.base_dir, args.detailed)
    else:
        # Analyze single file
        fasta_file = Path(args.input)
        if not fasta_file.exists():
            print(f"Error: File not found: {fasta_file}")
            return 1
        
        results = analyze_single_fasta(fasta_file, args.output, args.detailed)
        
        # Count statistics
        reviewed = sum(1 for info in results.values() if info['reviewed'])
        with_pubs = sum(1 for info in results.values() if info['pub_count'] > 0)
        
        # Return status
        if reviewed > 0:
            print(f"\n✓ Found {reviewed} reviewed (Swiss-Prot) entry/entries")
            return 0
        elif with_pubs > 0:
            print(f"\n✓ Found {with_pubs} entry/entries with publications")
            return 0
        else:
            print("\n✓ Analysis complete")
            return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
