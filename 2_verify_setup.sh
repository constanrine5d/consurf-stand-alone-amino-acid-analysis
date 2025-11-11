#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==> Verifying ConSurf Installation${NC}\n"

# Activate conda environment
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate python3.10bio

# Read GENERAL_CONSTANTS.py and verify each tool
CONSTANTS_FILE="./stand_alone_consurf-1.00/GENERAL_CONSTANTS.py"

echo -e "${YELLOW}Checking Python packages:${NC}"
python -c "import Bio; print('✅ biopython:', Bio.__version__)" 2>&1 || echo -e "${RED}✗ biopython not found${NC}"
python -c "import requests; print('✅ requests:', requests.__version__)" 2>&1 || echo -e "${RED}✗ requests not found${NC}"
python -c "import tqdm; print('✅ tqdm:', tqdm.__version__)" 2>&1 || echo -e "${RED}✗ tqdm not found${NC}"
echo ""

echo -e "${YELLOW}Checking alignment tools:${NC}"

# CLUSTALW
CLUSTALW=$(grep "^CLUSTALW = " "$CONSTANTS_FILE" | head -1 | cut -d'"' -f2)
if [ -f "$CLUSTALW" ]; then
    echo -e "${GREEN}✅ CLUSTALW:${NC} $CLUSTALW"
    $CLUSTALW -help 2>&1 | head -1
else
    echo -e "${RED}✗ CLUSTALW NOT FOUND:${NC} $CLUSTALW"
fi

# MUSCLE
MUSCLE=$(grep "^MUSCLE = " "$CONSTANTS_FILE" | cut -d'"' -f2)
if [ -f "$MUSCLE" ]; then
    echo -e "${GREEN}✅ MUSCLE:${NC} $MUSCLE"
    $MUSCLE -version 2>&1 | head -1
else
    echo -e "${RED}✗ MUSCLE NOT FOUND:${NC} $MUSCLE"
fi

# MAFFT
MAFFT=$(grep "^MAFFT_LINSI_GUIDANCE = " "$CONSTANTS_FILE" | cut -d'"' -f2)
if [ -f "$MAFFT" ]; then
    echo -e "${GREEN}✅ MAFFT:${NC} $MAFFT"
    $MAFFT --version 2>&1 | head -1
else
    echo -e "${RED}✗ MAFFT NOT FOUND:${NC} $MAFFT"
fi

echo ""
echo -e "${YELLOW}Checking HMMER tools:${NC}"

# HMMER tools
for tool in jackhmmer hmmbuild hmmsearch; do
    if command -v $tool &> /dev/null; then
        path=$(which $tool)
        echo -e "${GREEN}✅ $tool:${NC} $path"
        $tool -h 2>&1 | grep "^#" | head -1
    else
        echo -e "${RED}✗ $tool NOT FOUND${NC}"
    fi
done

echo ""
echo -e "${YELLOW}Checking CD-HIT:${NC}"

# CD-HIT
CD_HIT_DIR=$(grep "^CD_HIT_DIR = " "$CONSTANTS_FILE" | cut -d'"' -f2)
if [ -f "${CD_HIT_DIR}cd-hit" ]; then
    echo -e "${GREEN}✅ CD-HIT:${NC} ${CD_HIT_DIR}cd-hit"
    ${CD_HIT_DIR}cd-hit -h 2>&1 | head -3 | tail -1
else
    echo -e "${RED}✗ CD-HIT NOT FOUND:${NC} ${CD_HIT_DIR}cd-hit"
fi

echo ""
echo -e "${YELLOW}Checking Rate4Site:${NC}"

# # Rate4Site
# RATE4SITE=$(grep "^RATE4SITE  = " "$CONSTANTS_FILE" | cut -d'"' -f2)
# if [ -f "$RATE4SITE" ]; then
#     echo -e "${GREEN}✅ RATE4SITE:${NC} $RATE4SITE"
#     $RATE4SITE -h 2>&1 | grep "rate4site" | head -1
# else
#     echo -e "${RED}✗ RATE4SITE NOT FOUND:${NC} $RATE4SITE"
# fi

# RATE4SITE_SLOW=$(grep "^RATE4SITE_SLOW = " "$CONSTANTS_FILE" | cut -d'"' -f2)
# if [ -f "$RATE4SITE_SLOW" ]; then
#     echo -e "${GREEN}✅ RATE4SITE_SLOW:${NC} $RATE4SITE_SLOW"
# else
#     echo -e "${RED}✗ RATE4SITE_SLOW NOT FOUND:${NC} $RATE4SITE_SLOW"
# fi

# echo ""
# echo -e "${YELLOW}Checking BLAST tools:${NC}"

# BLASTPGP
BLASTPGP=$(grep "^BLASTPGP = " "$CONSTANTS_FILE" | cut -d'"' -f2)
if [ -f "$BLASTPGP" ]; then
    echo -e "${GREEN}✅ BLASTPGP (psiblast):${NC} $BLASTPGP"
    $BLASTPGP -version 2>&1 | head -1
else
    echo -e "${RED}✗ BLASTPGP NOT FOUND:${NC} $BLASTPGP"
fi

echo ""
echo -e "${YELLOW}Checking databases:${NC}"

# Databases
UNIREF90_DB=$(grep "^UNIREF90_DB = " "$CONSTANTS_FILE" | head -1 | cut -d'"' -f2)
if [ -f "$UNIREF90_DB" ]; then
    size=$(ls -lh "$UNIREF90_DB" | awk '{print $5}')
    echo -e "${GREEN}✅ UNIREF90_DB:${NC} $UNIREF90_DB ($size)"
else
    echo -e "${RED}✗ UNIREF90_DB NOT FOUND:${NC} $UNIREF90_DB"
fi

SWISSPROT_DB=$(grep "^SWISSPROT_DB = " "$CONSTANTS_FILE" | cut -d'"' -f2)
if [ -f "$SWISSPROT_DB" ]; then
    size=$(ls -lh "$SWISSPROT_DB" | awk '{print $5}')
    echo -e "${GREEN}✅ SWISSPROT_DB:${NC} $SWISSPROT_DB ($size)"
else
    echo -e "${RED}✗ SWISSPROT_DB NOT FOUND:${NC} $SWISSPROT_DB"
fi

echo ""
echo -e "${YELLOW}Checking PDB file:${NC}"
PDB_FILE="./example.pdb"
if [ -f "$PDB_FILE" ]; then
    echo -e "${GREEN}✅ PDB file:${NC} $PDB_FILE"
else
    echo -e "${RED}✗ PDB file NOT FOUND:${NC} $PDB_FILE"
fi

echo ""
echo -e "${BLUE}==> Verification Complete${NC}"
