#!/bin/bash
################################################################################
# Script: 7_run_coevolution_analysis.sh
# Description: Run coevolutionary analysis on ConSurf MSA results
# 
# This script computes pairwise covariance matrices between aligned positions
# to detect potential coevolutionary signals in protein sequences.
#
# Usage: ./7_run_coevolution_analysis.sh <RESULTS_DIR> [OPTIONS]
#
# Author: Konstantinos Grigorakis
# Date: November 2025
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

################################################################################
# Functions
################################################################################

print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

usage() {
    cat << EOF
Usage: $0 <RESULTS_DIR> [OPTIONS]

Run coevolutionary analysis on ConSurf results.

Required Arguments:
  RESULTS_DIR          Path to ConSurf results directory (e.g., results/results_ProteinName)

Optional Arguments:
  --max-gap-percent N  Maximum gap percentage to include position (default: 50)
  --include-gaps       Include gaps as valid state in calculations (default: no)
  --top-pairs N        Number of top covarying pairs to visualize (default: 50)
  --analyze-position P Analyze specific residue (e.g., GLU233, can use multiple times)
  --msa-file FILE      Use custom MSA file instead of default msa_fasta.aln
  --find-triplets      Search for 3-way coevolution (SLOW but finds higher-order signals)
  --triplet-candidates N  Max positions to test for triplets (default: 100)
  -h, --help          Show this help message

Examples:
  # Basic analysis
  $0 results/results_TtXyn30A_WT

  # With stricter gap filtering
  $0 results/results_TtXyn30A_WT --max-gap-percent 30

  # Analyze specific positions
  $0 results/results_TtXyn30A_WT --analyze-position GLU233 --analyze-position TYR97

  # Find triplets (3-way coevolution)
  $0 results/results_TtXyn30A_WT --find-triplets

  # Custom MSA file
  $0 results/results_TtXyn30A_WT --msa-file my_custom_alignment.fasta

Output:
  Results will be saved to: <RESULTS_DIR>/coevolutionary_analysis/

  Generated files:
    - covariance_matrix.csv                : Full covariance matrix
    - covariance_heatmap.png                : Visual heatmap of covariance
    - top_covarying_pairs.png               : Bar chart of top pairs
    - top_covarying_pairs_detailed.txt      : Top pairs WITH amino acid frequencies
    - summary_statistics.txt                : Statistical summary
    - position_RESIDUE_covariance.png       : Per-position analysis (if requested)
    - covarying_triplets.txt                : 3-way coevolution (if --find-triplets used)

EOF
    exit 0
}

################################################################################
# Main Script
################################################################################

print_header "COEVOLUTIONARY ANALYSIS"

# Check for help flag
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]] || [[ $# -lt 1 ]]; then
    usage
fi

# Parse required arguments
RESULTS_DIR="$1"
shift

# Check if results directory exists
if [[ ! -d "$RESULTS_DIR" ]]; then
    print_error "Results directory not found: $RESULTS_DIR"
    exit 1
fi

# Default MSA file
MSA_FILE="${RESULTS_DIR}/msa_fasta.aln"

# Parse optional arguments
EXTRA_ARGS=""
ANALYZE_POSITIONS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --max-gap-percent)
            EXTRA_ARGS="$EXTRA_ARGS --max-gap-percent $2"
            shift 2
            ;;
        --include-gaps)
            EXTRA_ARGS="$EXTRA_ARGS --include-gaps"
            shift
            ;;
        --top-pairs)
            EXTRA_ARGS="$EXTRA_ARGS --top-pairs $2"
            shift 2
            ;;
        --analyze-position)
            ANALYZE_POSITIONS+=("$2")
            shift 2
            ;;
        --msa-file)
            MSA_FILE="$2"
            shift 2
            ;;
        *)
            print_warning "Unknown option: $1"
            shift
            ;;
    esac
done

# Add analyze positions to extra args
for pos in "${ANALYZE_POSITIONS[@]}"; do
    EXTRA_ARGS="$EXTRA_ARGS --analyze-position $pos"
done

# Check if MSA file exists
if [[ ! -f "$MSA_FILE" ]]; then
    print_error "MSA file not found: $MSA_FILE"
    print_info "Expected file: ${RESULTS_DIR}/msa_fasta.aln"
    print_info "Or specify custom file with: --msa-file <path>"
    exit 1
fi

# Output directory
OUTPUT_DIR="${RESULTS_DIR}/coevolutionary_analysis"

print_info "Configuration:"
echo "  Results directory: $RESULTS_DIR"
echo "  MSA file: $MSA_FILE"
echo "  Output directory: $OUTPUT_DIR"
if [[ ${#ANALYZE_POSITIONS[@]} -gt 0 ]]; then
    echo "  Analyzing positions: ${ANALYZE_POSITIONS[*]}"
fi
echo ""

# Check Python script
PYTHON_SCRIPT="${SCRIPT_DIR}/libraries/coevolutionary_analysis.py"
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    print_error "Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Check if conda environment is activated
if [[ -z "$CONDA_DEFAULT_ENV" ]]; then
    print_warning "No conda environment detected"
    print_info "Attempting to activate python3.10bio environment..."
    
    # Try to activate conda environment
    if command -v conda &> /dev/null; then
        eval "$(conda shell.bash hook)"
        conda activate python3.10bio || {
            print_error "Failed to activate python3.10bio environment"
            print_info "Please activate your Python environment manually:"
            print_info "  conda activate python3.10bio"
            exit 1
        }
        print_success "Activated python3.10bio environment"
    else
        print_error "Conda not found in PATH"
        exit 1
    fi
else
    print_success "Using conda environment: $CONDA_DEFAULT_ENV"
fi

# Verify required Python packages
print_info "Checking Python dependencies..."
python -c "import numpy, pandas, Bio, matplotlib, seaborn" 2>/dev/null || {
    print_error "Missing required Python packages"
    print_info "Please install required packages:"
    print_info "  conda install numpy pandas biopython matplotlib seaborn"
    exit 1
}
print_success "All dependencies found"

# Run analysis
print_header "RUNNING COEVOLUTIONARY ANALYSIS"

# Check for consurf_grades.txt for residue labeling
GRADES_FILE="${RESULTS_DIR}/consurf_grades.txt"
if [[ -f "$GRADES_FILE" ]]; then
    python "$PYTHON_SCRIPT" "$MSA_FILE" "$OUTPUT_DIR" --grades-file "$GRADES_FILE" $EXTRA_ARGS
else
    print_warning "consurf_grades.txt not found - using alignment positions instead of PDB numbering"
    python "$PYTHON_SCRIPT" "$MSA_FILE" "$OUTPUT_DIR" $EXTRA_ARGS
fi

# Check if analysis completed successfully
if [[ $? -eq 0 ]]; then
    echo ""
    print_header "ANALYSIS COMPLETE"
    print_success "Coevolutionary analysis completed successfully!"
    echo ""
    print_info "Results saved to: $OUTPUT_DIR"
    echo ""
    print_info "Generated files:"
    
    # List generated files
    if [[ -d "$OUTPUT_DIR" ]]; then
        for file in "$OUTPUT_DIR"/*; do
            if [[ -f "$file" ]]; then
                filename=$(basename "$file")
                filesize=$(du -h "$file" | cut -f1)
                echo "  • $filename ($filesize)"
            fi
        done
    fi
    
    echo ""
    print_info "Next steps:"
    echo "  1. Review summary_statistics.txt for overview"
    echo "  2. Check covariance_heatmap.png for visual patterns"
    echo "  3. Examine top_covarying_pairs.txt for strongest signals"
    echo "  4. Open CSV in Excel/Python for detailed analysis"
    echo ""
    
else
    echo ""
    print_error "Analysis failed! Check error messages above."
    exit 1
fi
