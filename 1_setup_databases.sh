#!/bin/bash
#
# ConSurf Database Setup Script
# Extracts and formats protein databases on external drive
#

set -e  # Exit on error

# Configuration - Change this path if needed
DB_DIR="/Volumes/const_2tb/consurf_databases"
SOURCE_DIR="$(pwd)"

echo "==================================="
echo "ConSurf Database Setup"
echo "==================================="
echo ""

# Check if database directory location exists
if [ ! -d "$(dirname "$DB_DIR")" ]; then
    echo "⚠️  ERROR: Database directory parent path not found: $(dirname "$DB_DIR")"
    echo ""
    echo "Please update the DB_DIR variable in this script to point to your desired location."
    echo "Edit line 10 of $0"
    echo ""
    echo "Current setting: DB_DIR=\"$DB_DIR\""
    echo ""
    exit 1
fi

# Check for pv
if ! command -v pv &> /dev/null; then
    echo "⚠️  Warning: 'pv' not found. Progress bars will not be available."
    echo "   To install: brew install pv"
    echo ""
    USE_PV=false
else
    USE_PV=true
fi

# Create database directory
echo "Creating database directory: $DB_DIR"
mkdir -p "$DB_DIR"
echo "✓ Directory ready"
echo ""

# Check source file
echo "Checking source file..."
if [ ! -f "${SOURCE_DIR}/uniprot_trembl.fasta.gz" ]; then
    echo "ERROR: Source file not found: ${SOURCE_DIR}/uniprot_trembl.fasta.gz"
    exit 1
fi
SOURCE_SIZE=$(du -h "${SOURCE_DIR}/uniprot_trembl.fasta.gz" | cut -f1)
echo "✓ Found: uniprot_trembl.fasta.gz (${SOURCE_SIZE})"

# Extract TrEMBL database
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1/3: Extracting UniProt TrEMBL Database"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "This will take 15-30 minutes depending on your drive speed"
echo ""
if [ -f "${DB_DIR}/uniprot_trembl.fasta" ]; then
    EXISTING_SIZE=$(du -h "${DB_DIR}/uniprot_trembl.fasta" | cut -f1)
    echo "✓ File already exists (${EXISTING_SIZE}), skipping extraction"
else
    echo "Starting extraction..."
    echo ""
    if [ "$USE_PV" = true ]; then
        pv -pterb "${SOURCE_DIR}/uniprot_trembl.fasta.gz" | gunzip > "${DB_DIR}/uniprot_trembl.fasta"
    else
        gunzip -c "${SOURCE_DIR}/uniprot_trembl.fasta.gz" > "${DB_DIR}/uniprot_trembl.fasta"
    fi
    echo ""
    FINAL_SIZE=$(du -h "${DB_DIR}/uniprot_trembl.fasta" | cut -f1)
    echo "✓ Extraction complete! Final size: ${FINAL_SIZE}"
fi

# Download Swiss-Prot if needed
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2/3: Swiss-Prot Database"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
if [ -f "${DB_DIR}/uniprot_sprot.fasta.gz" ]; then
    echo "Found compressed file, extracting..."
    echo ""
    if [ "$USE_PV" = true ]; then
        pv -pterb "${DB_DIR}/uniprot_sprot.fasta.gz" | gunzip > "${DB_DIR}/uniprot_sprot.fasta"
    else
        gunzip -c "${DB_DIR}/uniprot_sprot.fasta.gz" > "${DB_DIR}/uniprot_sprot.fasta"
    fi
    echo ""
    SPROT_SIZE=$(du -h "${DB_DIR}/uniprot_sprot.fasta" | cut -f1)
    echo "✓ Extraction complete! Size: ${SPROT_SIZE}"
elif [ -f "${DB_DIR}/uniprot_sprot.fasta" ]; then
    SPROT_SIZE=$(du -h "${DB_DIR}/uniprot_sprot.fasta" | cut -f1)
    echo "✓ Already extracted (${SPROT_SIZE})"
else
    echo "Downloading Swiss-Prot database (~90MB compressed, ~300MB uncompressed)..."
    echo ""
    curl --progress-bar -o "${DB_DIR}/uniprot_sprot.fasta.gz" \
        "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz"
    echo ""
    echo "Extracting..."
    echo ""
    if [ "$USE_PV" = true ]; then
        pv -pterb "${DB_DIR}/uniprot_sprot.fasta.gz" | gunzip > "${DB_DIR}/uniprot_sprot.fasta"
    else
        gunzip -c "${DB_DIR}/uniprot_sprot.fasta.gz" > "${DB_DIR}/uniprot_sprot.fasta"
    fi
    echo ""
    SPROT_SIZE=$(du -h "${DB_DIR}/uniprot_sprot.fasta" | cut -f1)
    echo "✓ Download and extraction complete! Size: ${SPROT_SIZE}"
fi

# Format databases for BLAST
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3/3: Formatting Databases for BLAST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "This creates index files for fast searching"
echo ""

echo "Formatting TrEMBL (may take 5-10 minutes)..."
if [ -f "${DB_DIR}/uniprot_trembl.fasta.psq" ]; then
    echo "✓ Already formatted, skipping"
else
    # Run makeblastdb with progress dots
    (
        makeblastdb -in "${DB_DIR}/uniprot_trembl.fasta" -dbtype prot -parse_seqids > /dev/null 2>&1
    ) &
    BLAST_PID=$!
    
    while kill -0 $BLAST_PID 2>/dev/null; do
        printf "█"
        sleep 1
    done
    wait $BLAST_PID
    echo ""
    echo "✓ TrEMBL formatting complete"
fi
echo ""

echo "Formatting Swiss-Prot (should be quick, ~1 minute)..."
if [ -f "${DB_DIR}/uniprot_sprot.fasta.psq" ]; then
    echo "✓ Already formatted, skipping"
else
    (
        makeblastdb -in "${DB_DIR}/uniprot_sprot.fasta" -dbtype prot -parse_seqids > /dev/null 2>&1
    ) &
    BLAST_PID=$!
    
    while kill -0 $BLAST_PID 2>/dev/null; do
        printf "█"
        sleep 0.5
    done
    wait $BLAST_PID
    echo ""
    echo "✓ Swiss-Prot formatting complete"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ DATABASE SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Database location: $DB_DIR"
echo ""
echo "📊 Files created:"
TREMBL_SIZE=$(du -h "${DB_DIR}/uniprot_trembl.fasta" 2>/dev/null | cut -f1)
SPROT_SIZE=$(du -h "${DB_DIR}/uniprot_sprot.fasta" 2>/dev/null | cut -f1)
TREMBL_FILES=$(ls -1 "${DB_DIR}"/uniprot_trembl.fasta.* 2>/dev/null | wc -l | xargs)
SPROT_FILES=$(ls -1 "${DB_DIR}"/uniprot_sprot.fasta.* 2>/dev/null | wc -l | xargs)

echo "   • uniprot_trembl.fasta (${TREMBL_SIZE}) + ${TREMBL_FILES} index files"
echo "   • uniprot_sprot.fasta (${SPROT_SIZE}) + ${SPROT_FILES} index files"
echo ""
echo "🚀 Ready to run ConSurf analysis!"
echo ""
echo "   Usage: ./run_consurf.sh <pdb_file> <chain_id> [output_dir]"
echo ""
echo "   Example: ./run_consurf.sh protein.pdb A my_analysis"
echo ""
