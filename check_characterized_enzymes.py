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

def categorize_sequences(results):
    """Categorize sequences by characterization level."""
    categories = {
        'reviewed': [],  # Swiss-Prot reviewed entries
        'well_studied': [],  # Has publications (5+)
        'characterized': [],  # Has EC number or specific function name
        'uncharacterized': []  # Generic names or no info
    }
    
    generic_terms = ['uncharacterized', 'hypothetical', 'predicted', 'putative', 
                     'domain-containing', 'family protein']
    
    for acc, info in results.items():
        if info['reviewed']:
            categories['reviewed'].append((acc, info))
        elif info['pub_count'] >= 5:
            categories['well_studied'].append((acc, info))
        elif info['ec'] or not any(term.lower() in info['protein_name'].lower() 
                                   for term in generic_terms):
            categories['characterized'].append((acc, info))
        else:
            categories['uncharacterized'].append((acc, info))
    
    return categories

def generate_report(ids, results, categories, detailed=False):
    """Generate a text report from analysis results."""
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("CHARACTERIZED ENZYME ANALYSIS")
    output_lines.append("=" * 80)
    output_lines.append(f"Total sequences: {len(ids)}")
    output_lines.append(f"Sequences with UniProt data: {len(results)}")
    output_lines.append("")
    
    # Reviewed (Swiss-Prot) entries
    output_lines.append(f"REVIEWED ENTRIES (Swiss-Prot): {len(categories['reviewed'])}")
    output_lines.append("-" * 80)
    if categories['reviewed']:
        for acc, info in sorted(categories['reviewed'], key=lambda x: x[1]['protein_name']):
            output_lines.append(f"{acc}")
            output_lines.append(f"  Name: {info['protein_name']}")
            output_lines.append(f"  Organism: {info['organism']}")
            if info['ec']:
                output_lines.append(f"  EC: {info['ec']}")
            if info['gene']:
                output_lines.append(f"  Gene: {info['gene']}")
            if info['pub_count'] > 0:
                output_lines.append(f"  Publications: {info['pub_count']}")
                if detailed and info['pubmed_ids'][:5]:
                    output_lines.append(f"    PubMed IDs: {', '.join(info['pubmed_ids'][:5])}")
                    if info['pub_count'] > 5:
                        output_lines.append(f"    ... and {info['pub_count'] - 5} more")
            output_lines.append("")
    else:
        output_lines.append("  None found")
        output_lines.append("")
    
    # Well-studied (has significant publications)
    output_lines.append(f"WELL-STUDIED (5+ publications): {len(categories['well_studied'])}")
    output_lines.append("-" * 80)
    if categories['well_studied']:
        # Sort by publication count (most studied first)
        for acc, info in sorted(categories['well_studied'], key=lambda x: x[1]['pub_count'], reverse=True):
            output_lines.append(f"{acc}: {info['protein_name']}")
            if info['ec']:
                output_lines.append(f"  EC: {info['ec']}")
            output_lines.append(f"  Publications: {info['pub_count']}")
            if detailed and info['pubmed_ids'][:5]:
                output_lines.append(f"  PubMed IDs: {', '.join(info['pubmed_ids'][:5])}")
                if info['pub_count'] > 5:
                    output_lines.append(f"  ... and {info['pub_count'] - 5} more")
            output_lines.append(f"  Organism: {info['organism']}")
            output_lines.append("")
    else:
        output_lines.append("  None found")
        output_lines.append("")
    
    # Characterized (has EC or specific name)
    output_lines.append(f"LIKELY CHARACTERIZED: {len(categories['characterized'])}")
    output_lines.append("-" * 80)
    if detailed and categories['characterized']:
        for acc, info in sorted(categories['characterized'], key=lambda x: x[1]['protein_name']):
            output_lines.append(f"{acc}: {info['protein_name']}")
            if info['ec']:
                output_lines.append(f"  EC: {info['ec']}")
            if info['pub_count'] > 0:
                output_lines.append(f"  Publications: {info['pub_count']}")
    else:
        output_lines.append(f"  {len(categories['characterized'])} sequences found")
        output_lines.append("  (use --detailed to see full list)")
    output_lines.append("")
    
    # Uncharacterized
    output_lines.append(f"UNCHARACTERIZED/PREDICTED: {len(categories['uncharacterized'])}")
    output_lines.append("-" * 80)
    if detailed and categories['uncharacterized']:
        for acc, info in categories['uncharacterized']:
            output_lines.append(f"{acc}: {info['protein_name']}")
    else:
        output_lines.append(f"  {len(categories['uncharacterized'])} sequences")
    output_lines.append("")
    
    # Summary statistics
    output_lines.append("=" * 80)
    output_lines.append("SUMMARY")
    output_lines.append("=" * 80)
    total_with_data = len(results)
    if total_with_data > 0:
        reviewed_pct = len(categories['reviewed']) / total_with_data * 100
        well_studied_pct = len(categories['well_studied']) / total_with_data * 100
        char_pct = len(categories['characterized']) / total_with_data * 100
        unchar_pct = len(categories['uncharacterized']) / total_with_data * 100
        
        output_lines.append(f"Reviewed (Swiss-Prot):     {len(categories['reviewed']):4d} ({reviewed_pct:5.1f}%)")
        output_lines.append(f"Well-studied (5+ pubs):    {len(categories['well_studied']):4d} ({well_studied_pct:5.1f}%)")
        output_lines.append(f"Likely characterized:      {len(categories['characterized']):4d} ({char_pct:5.1f}%)")
        output_lines.append(f"Uncharacterized/predicted: {len(categories['uncharacterized']):4d} ({unchar_pct:5.1f}%)")
    
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
    
    categories = categorize_sequences(results)
    report = generate_report(ids, results, categories, detailed)
    
    # Determine output file location
    if output_file is None:
        # Place report in same directory as FASTA file
        fasta_path = Path(fasta_file)
        output_file = fasta_path.parent / "enzyme_characterization_report.txt"
    
    Path(output_file).write_text(report)
    print(f"\n✓ Report saved to: {output_file}")
    
    return categories

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
            
            # Categorize and generate report
            categories = categorize_sequences(file_results)
            report = generate_report(ids, file_results, categories, detailed)
            
            # Save report next to FASTA file
            output_file = fasta_file.parent / "enzyme_characterization_report.txt"
            Path(output_file).write_text(report)
            
            print(f"  ✓ Report saved: {output_file.relative_to(base_path)}")
            print(f"    Reviewed: {len(categories['reviewed'])}, Well-studied: {len(categories['well_studied'])}, "
                  f"Characterized: {len(categories['characterized'])}, Uncharacterized: {len(categories['uncharacterized'])}")
            
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
        
        categories = analyze_single_fasta(fasta_file, args.output, args.detailed)
        
        # Return status
        if categories['reviewed']:
            print(f"\n✓ Found {len(categories['reviewed'])} reviewed enzyme(s)")
            return 0
        elif categories['well_studied']:
            print(f"\n✓ Found {len(categories['well_studied'])} well-studied enzyme(s)")
            return 0
        elif categories['characterized']:
            print(f"\n✓ Found {len(categories['characterized'])} likely characterized enzyme(s)")
            return 0
        else:
            print("\n✗ No clearly characterized enzymes found")
            return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
