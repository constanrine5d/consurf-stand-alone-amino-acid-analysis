#!/bin/bash

################################################################################
# Check Characterized Enzymes Script
# 
# This script analyzes sequences from amino acid distribution analysis to
# identify characterized enzymes using UniProt database.
################################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Show usage
show_usage() {
    cat << EOF
Usage: $0 <RESULTS_DIR> [OPTIONS]

Analyze sequences to identify characterized enzymes using UniProt database.

ARGUMENTS:
    RESULTS_DIR           Results directory (e.g., results/results_example)

OPTIONS:
    --file FILE           Analyze specific FASTA file only
    --no-detail           Hide detailed enzyme list
    -h, --help            Show this help message

EXAMPLES:
    # Analyze all FASTA files in results directory
    $0 results/results_example
    
    # Analyze specific FASTA file
    $0 results/results_example --file results/results_example/amino_acids_analysis_results/position_226/covered/1_GLU_45.0/sequences.fasta

OUTPUT:
    - enzyme_characterization_report.txt (next to each sequences.fasta)
    
EOF
}

# Parse arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Results directory is required${NC}"
    show_usage
    exit 1
fi

RESULTS_DIR="$1"
shift

MODE="all"
SHOW_DETAILED="true"

while [[ $# -gt 0 ]]; do
    case $1 in
        --file)
            MODE="$2"
            shift 2
            ;;
        --no-detail)
            SHOW_DETAILED="false"
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

echo "=================================="
echo "Characterized Enzyme Analysis"
echo "=================================="
echo ""

# Check if results directory exists
if [ ! -d "$RESULTS_DIR" ]; then
    echo -e "${RED}Error: Results directory not found: $RESULTS_DIR${NC}"
    exit 1
fi

# Check if MODE is set to a specific file
if [ "$MODE" != "all" ] && [ ! -f "$MODE" ]; then
    echo -e "${RED}Error: FASTA file not found: $MODE${NC}"
    exit 1
fi

# Check if Python environment is set up
if [ ! -f ".venv/bin/python" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not found${NC}"
    echo "Setting up Python environment..."
    python3 -m venv .venv
    .venv/bin/pip install requests > /dev/null 2>&1
fi

# Check if requests library is installed
if ! .venv/bin/python -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}Installing required Python package (requests)...${NC}"
    .venv/bin/pip install requests
fi

# Build command
CMD=".venv/bin/python libraries/check_characterized_enzymes.py"

if [ "$MODE" = "all" ]; then
    CMD="$CMD all --base-dir \"$RESULTS_DIR\""
else
    CMD="$CMD \"$MODE\""
fi

if [ "$SHOW_DETAILED" = "true" ]; then
    CMD="$CMD --detailed"
fi

# Run analysis
if [ "$MODE" = "all" ]; then
    echo -e "${GREEN}Analyzing all FASTA files in: $RESULTS_DIR/amino_acids_analysis_results${NC}"
else
    echo -e "${GREEN}Analyzing: $MODE${NC}"
fi
echo ""

eval $CMD

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Analysis complete!${NC}"
    if [ "$MODE" = "all" ]; then
        echo -e "Reports saved next to each sequences.fasta file"
    fi
else
    echo ""
    echo -e "${RED}✗ Analysis failed${NC}"
    exit 1
fi
