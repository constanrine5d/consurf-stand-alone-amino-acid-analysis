#!/bin/bash

################################################################################
# Check Characterized Enzymes Script
# 
# This script analyzes sequences from amino acid distribution analysis to
# identify characterized enzymes using UniProt database.
################################################################################

# ============================
# USER CONFIGURATION VARIABLES
# ============================

# Base results directory (relative to this script)
# Point this to where your amino_acids_analysis_results folder is located
RESULTS_DIR="./results_final"

# Mode: "all" to analyze all FASTA files, or path to single FASTA file
MODE="all"

# Show detailed list of all enzymes (true/false)
SHOW_DETAILED="true"

# ============================
# END CONFIGURATION
# ============================

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================="
echo "Characterized Enzyme Analysis"
echo "=================================="
echo ""

# Check if MODE is set to a specific file
if [ "$MODE" != "all" ] && [ ! -f "$MODE" ]; then
    echo -e "${RED}Error: FASTA file not found: $MODE${NC}"
    echo ""
    echo "Please update the MODE variable at the top of this script."
    echo "Set MODE=\"all\" to analyze all FASTA files, or provide a specific file path."
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
CMD=".venv/bin/python check_characterized_enzymes.py"

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
