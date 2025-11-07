#!/bin/bash -e
#
# ConSurf Complete Setup and Run Script
# This script handles environment activation and runs ConSurf analysis
#

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONSURF_DIR="/Users/constanrine5d/programs/ConSurf"
CONSURF_SCRIPT="${CONSURF_DIR}/stand_alone_consurf-1.00/stand_alone_consurf.py"
CONDA_ENV="python3.10bio"

# Function to print colored messages
print_step() {
    echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check arguments
if [ $# -lt 2 ]; then
    echo -e "${BLUE}Usage:${NC} $0 <PDB_FILE> <CHAIN_ID> [OUTPUT_DIR]"
    echo ""
    echo -e "${BLUE}Arguments:${NC}"
    echo "  PDB_FILE   - Path to PDB file"
    echo "  CHAIN_ID   - Chain identifier (e.g., A, B, G)"
    echo "  OUTPUT_DIR - Output directory (default: ./consurf_output)"
    echo ""
    echo -e "${BLUE}Example:${NC}"
    echo "  $0 TtXyn30A_WT.pdb G ./results"
    echo ""
    echo -e "${BLUE}Database Location:${NC} /Volumes/const_2tb/consurf_databases/"
    echo -e "${BLUE}Conda Environment:${NC} $CONDA_ENV"
    exit 1
fi

PDB_FILE="$1"
CHAIN_ID="$2"
OUTPUT_DIR="${3:-./consurf_output}"

# Check if PDB file exists
if [ ! -f "$PDB_FILE" ]; then
    print_error "PDB file '$PDB_FILE' not found!"
    exit 1
fi

# Get absolute paths
PDB_FILE=$(cd "$(dirname "$PDB_FILE")" && pwd)/$(basename "$PDB_FILE")
OUTPUT_DIR=$(mkdir -p "$OUTPUT_DIR" && cd "$OUTPUT_DIR" && pwd)

print_step "ConSurf Analysis Setup"
echo ""
print_info "PDB File: $PDB_FILE"
print_info "Chain: $CHAIN_ID"
print_info "Output: $OUTPUT_DIR"
print_info "Conda Env: $CONDA_ENV"
echo ""

# Step 1: Source conda
print_step "Step 1: Setting up conda environment"
# Initialize conda for bash
if [ -f /opt/anaconda3/etc/profile.d/conda.sh ]; then
    source /opt/anaconda3/etc/profile.d/conda.sh
    print_info "Initialized conda from /opt/anaconda3"
elif [ -f ~/.zprofile ]; then
    source ~/.zprofile
    source /opt/anaconda3/etc/profile.d/conda.sh 2>/dev/null || true
    print_info "Sourced ~/.zprofile"
else
    print_error "Could not find conda initialization"
    exit 1
fi

# Step 2: Activate conda environment
print_step "Step 2: Activating conda environment: $CONDA_ENV"
conda activate "$CONDA_ENV" || {
    print_error "Failed to activate conda environment '$CONDA_ENV'"
    print_info "Available environments:"
    conda env list
    exit 1
}
print_info "Environment activated successfully"
print_info "Python version: $(python --version 2>&1)"

# Step 3: Verify required packages
print_step "Step 3: Verifying required Python packages"
python -c "import Bio; import requests" 2>&1 || {
    print_error "Required packages not found!"
    print_info "Installing biopython and requests..."
    pip install biopython requests
}
print_info "✓ biopython and requests are installed"

# Step 4: Check tools availability
print_step "Step 4: Checking required tools"
TOOLS_OK=true

check_tool() {
    if command -v $1 &> /dev/null; then
        print_info "✓ $1 found: $(command -v $1)"
    else
        print_warning "✗ $1 not found"
        TOOLS_OK=false
    fi
}

check_tool "hmmbuild"
check_tool "hmmsearch"
check_tool "cd-hit"
check_tool "muscle"
check_tool "mafft"
check_tool "clustalw"

if [ "$TOOLS_OK" = false ]; then
    print_warning "Some tools are missing but ConSurf may still work"
fi

# Step 5: Check rate4site
print_step "Step 5: Checking rate4site"
RATE4SITE="${CONSURF_DIR}/bin/rate4site"
if [ -f "$RATE4SITE" ]; then
    print_info "✓ rate4site found: $RATE4SITE"
else
    print_error "rate4site not found at $RATE4SITE"
    exit 1
fi

# Step 6: Check database
print_step "Step 6: Checking database availability"
DB_DIR="/Volumes/const_2tb/consurf_databases"
if [ -d "$DB_DIR" ]; then
    print_info "✓ Database directory found: $DB_DIR"
    
    # Check for FASTA files
    if [ -f "$DB_DIR/uniprot_sprot.fasta" ]; then
        SIZE=$(du -sh "$DB_DIR/uniprot_sprot.fasta" | cut -f1)
        print_info "  - uniprot_sprot.fasta: $SIZE"
    fi
    if [ -f "$DB_DIR/uniprot_trembl.fasta" ]; then
        SIZE=$(du -sh "$DB_DIR/uniprot_trembl.fasta" | cut -f1)
        print_info "  - uniprot_trembl.fasta: $SIZE"
    fi
else
    print_warning "Database directory not found: $DB_DIR"
    print_info "You may need to download and format databases first"
fi

# Step 7: Run ConSurf
print_step "Step 7: Running ConSurf analysis"
echo ""

cd "$CONSURF_DIR/stand_alone_consurf-1.00"

# Monitor progress in background
monitor_progress() {
    local output_dir="$1"
    local last_msg=""
    local last_hmmer_size=0
    local hmmer_unchanged_count=0
    local filtering_started=false
    
    while true; do
        sleep 3
        
        # Check for log file
        if [ -f "${output_dir}/log.txt" ]; then
            # Get the last meaningful line
            last_line=$(tail -5 "${output_dir}/log.txt" | grep -E "running:|waiting|analyse|determine|EXIT" | tail -1)
            
            if [ -n "$last_line" ] && [ "$last_line" != "$last_msg" ]; then
                echo -e "${BLUE}[PROGRESS]${NC} $last_line"
                last_msg="$last_line"
            fi
            
            # Check if search output exists and show size only if it changed
            if [ -f "${output_dir}/sequences_found_hmmer.txt" ] && [ "$filtering_started" = false ]; then
                size=$(wc -l < "${output_dir}/sequences_found_hmmer.txt" 2>/dev/null || echo 0)
                if [ "$size" -gt 0 ] && [ "$size" != "$last_hmmer_size" ]; then
                    echo -e "${GREEN}[HMMER]${NC} Found $size sequences (file growing...)"
                    last_hmmer_size=$size
                    hmmer_unchanged_count=0
                elif [ "$size" -eq "$last_hmmer_size" ] && [ "$size" -gt 0 ]; then
                    hmmer_unchanged_count=$((hmmer_unchanged_count + 1))
                    # After 3 checks with no change, stop monitoring HMMER (filtering will show progress)
                    if [ "$hmmer_unchanged_count" -eq 3 ]; then
                        filtering_started=true
                    fi
                fi
            fi
            
            # Check if process finished
            if grep -q "EXIT" "${output_dir}/log.txt" 2>/dev/null; then
                break
            fi
        fi
    done
}

# Start progress monitor in background
print_info "Starting ConSurf with progress monitoring..."
print_warning "This will take several minutes (searching 94GB database)..."
echo ""

# Start monitor in background
monitor_progress "$OUTPUT_DIR" &
MONITOR_PID=$!

# Run ConSurf with recommended parameters
# --algorithm HMMER: Use HMMER for sequence search
# Bayes algorithm (default, more accurate than Maximum Likelihood)
# --MIN_ID 10: Very low identity threshold to find distant homologs
# --cutoff 0.001: More permissive E-value to find more sequences
# --MAX_HOMOLOGS 500: Use 500 sequences for MSA
python stand_alone_consurf.py \
    --pdb "$PDB_FILE" \
    --chain "$CHAIN_ID" \
    --dir "$OUTPUT_DIR" \
    --algorithm HMMER \
    --MAX_HOMOLOGS 300 \
    --MIN_ID 10 \
    --cutoff 0.001 2>&1 | tee "${OUTPUT_DIR}/consurf_run.log"

EXIT_CODE=$?

# Kill the monitor
kill $MONITOR_PID 2>/dev/null
wait $MONITOR_PID 2>/dev/null

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    print_step "ConSurf analysis completed successfully!"
    print_info "Results saved to: $OUTPUT_DIR"
    print_info "Log file: ${OUTPUT_DIR}/consurf_run.log"
    echo ""
    print_info "Output files:"
    ls -lh "$OUTPUT_DIR" | tail -n +2 | awk '{print "  " $9 " (" $5 ")"}'
else
    print_error "ConSurf analysis failed with exit code $EXIT_CODE"
    print_info "Check the log file: ${OUTPUT_DIR}/consurf_run.log"
    exit $EXIT_CODE
fi
