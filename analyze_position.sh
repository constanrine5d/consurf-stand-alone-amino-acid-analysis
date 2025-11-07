#!/bin/bash

#############################################################################
# Analyze Amino Acid Distribution at Specific Positions
# Wrapper script for analyze_position.py
#############################################################################

# Configuration
CONDA_ENV="python3.10bio"
RESULTS_DIR="/Users/constanrine5d/programs/ConSurf/results_final"
MSA_FILE="${RESULTS_DIR}/msa_fasta.aln"
GRADES_FILE="${RESULTS_DIR}/consurf_grades.txt"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/analyze_position.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

#############################################################################
# Functions
#############################################################################

print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] [POSITIONS...]

Analyze amino acid distribution at specific positions in ConSurf MSA.

If no positions are specified, analyzes ALL positions (default behavior).

OPTIONS:
    -e, --env ENV          Conda environment name (default: python3.10bio)
    -r, --results DIR      Results directory (default: results_final)
    -m, --msa FILE         MSA file path (default: results_final/msa_fasta.aln)
    -g, --grades FILE      Grades file path (default: results_final/consurf_grades.txt)
    -o, --output FILE      Save output to file (auto-generated for all positions)
    --all                  Explicitly analyze all positions (same as no positions)
    -h, --help             Show this help message

POSITIONS:
    One or more position numbers (1-indexed, as shown in consurf_grades.txt)
    If omitted, ALL positions are analyzed (default).
    
EXAMPLES:
    # Analyze ALL positions (default) - saves to amino_acid_distribution_all_positions.txt
    $0
    
    # Analyze single position
    $0 226
    
    # Analyze multiple positions
    $0 226 227 228
    
    # Save specific position to custom file
    $0 -o pos_226_analysis.txt 226
    
    # Use different results directory
    $0 -r /path/to/results
    
    # Use custom conda environment
    $0 -e myenv

COMMON POSITIONS OF INTEREST:
    - Active site residues
    - Binding pocket residues
    - Interface residues
    - Mutation sites

To find positions in consurf_grades.txt:
    grep "GLU:233" results_final/consurf_grades.txt
    
OUTPUT FILES:
    - amino_acid_distribution_all_positions.txt (default for all positions)
    - Custom filename with -o option
    
FOLDER STRUCTURE (automatically created):
    results_final/amino_acids_analysis_results/
    └── position_226_GLU_233_G/
        ├── not_covered/
        │   └── sequences.fasta          # Sequences with gaps at this position
        └── covered/
            ├── 1_N_60.0/
            │   └── sequences.fasta      # 180 sequences with N (60.00%)
            ├── 2_T_7.67/
            │   └── sequences.fasta      # 23 sequences with T (7.67%)
            ├── 3_E_4.67/                # Query amino acid
            │   └── sequences.fasta      # 14 sequences with E (4.67%)
            └── ...                       # More folders for each amino acid
    
    Each folder contains FASTA files with sequences grouped by amino acid at that position.
    Folder names include: ranking_AminoAcid_Percentage
    
EOF
}

#############################################################################
# Parse arguments
#############################################################################

OUTPUT_FILE=""
POSITIONS=()
ANALYZE_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            CONDA_ENV="$2"
            shift 2
            ;;
        -r|--results)
            RESULTS_DIR="$2"
            MSA_FILE="${RESULTS_DIR}/msa_fasta.aln"
            GRADES_FILE="${RESULTS_DIR}/consurf_grades.txt"
            shift 2
            ;;
        -m|--msa)
            MSA_FILE="$2"
            shift 2
            ;;
        -g|--grades)
            GRADES_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --all)
            ANALYZE_ALL=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            # Check if argument is "all" (case-insensitive)
            arg_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')
            if [[ "$arg_lower" == "all" ]]; then
                ANALYZE_ALL=true
            else
                POSITIONS+=("$1")
            fi
            shift
            ;;
    esac
done

# If no positions specified and --all not explicitly set, default to --all
if [[ ${#POSITIONS[@]} -eq 0 && "$ANALYZE_ALL" == "false" ]]; then
    ANALYZE_ALL=true
fi

#############################################################################
# Validation
#############################################################################

# Remove old validation - positions are now optional
# If no positions and no --all, we already set ANALYZE_ALL=true above

# Check if files exist
if [ ! -f "$MSA_FILE" ]; then
    print_error "MSA file not found: $MSA_FILE"
    exit 1
fi

if [ ! -f "$GRADES_FILE" ]; then
    print_error "Grades file not found: $GRADES_FILE"
    exit 1
fi

if [ ! -f "$PYTHON_SCRIPT" ]; then
    print_error "Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

#############################################################################
# Main execution
#############################################################################

print_header "Amino Acid Distribution Analysis"

echo "Configuration:"
echo "  Conda environment: $CONDA_ENV"
echo "  MSA file:          $MSA_FILE"
echo "  Grades file:       $GRADES_FILE"
if [ "$ANALYZE_ALL" == "true" ]; then
    echo "  Mode:              Analyze ALL positions"
else
    echo "  Positions:         ${POSITIONS[*]}"
fi
if [ -n "$OUTPUT_FILE" ]; then
    echo "  Output file:       $OUTPUT_FILE"
fi
echo ""

# Activate conda environment
print_info "Activating conda environment: $CONDA_ENV"
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate "$CONDA_ENV"

if [ $? -ne 0 ]; then
    print_error "Failed to activate conda environment: $CONDA_ENV"
    exit 1
fi

print_success "Environment activated"
echo ""

# Build command
if [ "$ANALYZE_ALL" == "true" ]; then
    # All positions mode
    CMD="python3 \"$PYTHON_SCRIPT\" -m \"$MSA_FILE\" -g \"$GRADES_FILE\" --all"
    
    if [ -n "$OUTPUT_FILE" ]; then
        CMD="$CMD -o \"$OUTPUT_FILE\""
    else
        # Default output file for all positions
        DEFAULT_OUTPUT="${RESULTS_DIR}/amino_acid_distribution_all_positions.txt"
        CMD="$CMD -o \"$DEFAULT_OUTPUT\""
        echo "  Output will be saved to: $DEFAULT_OUTPUT"
    fi
else
    # Specific positions mode
    CMD="python3 \"$PYTHON_SCRIPT\" -m \"$MSA_FILE\" -g \"$GRADES_FILE\" -p ${POSITIONS[*]}"
    
    if [ -n "$OUTPUT_FILE" ]; then
        CMD="$CMD -o \"$OUTPUT_FILE\""
    fi
fi

# Execute
print_info "Running analysis..."
echo ""

eval $CMD

if [ $? -eq 0 ]; then
    echo ""
    print_success "Analysis completed successfully"
else
    echo ""
    print_error "Analysis failed"
    exit 1
fi
