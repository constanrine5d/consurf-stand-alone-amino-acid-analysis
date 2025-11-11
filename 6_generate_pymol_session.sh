#!/bin/bash
#
# Generate PyMOL Session with ConSurf Conservation Coloring
# Creates a .pse session file from ConSurf analysis results
#

set -e  # Exit on error

# Configuration
CONDA_ENV="python3.10bio"

# Show usage
show_usage() {
    cat << EOF
Usage: $0 <RESULTS_DIR>

Generate PyMOL session with ConSurf conservation coloring.

ARGUMENTS:
    RESULTS_DIR           Results directory (e.g., results/results_example)

EXAMPLES:
    $0 results/results_example
    $0 ./results_final

OUTPUT:
    - <RESULTS_DIR>/consurf_session.pse

To open in PyMOL:
    pymol <RESULTS_DIR>/consurf_session.pse
    
EOF
}

# Parse arguments
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

RESULTS_DIR="$1"

# Activate conda environment
echo "==================================="
echo "PyMOL Session Generator"
echo "==================================="
echo ""

# Check if results directory exists
if [ ! -d "$RESULTS_DIR" ]; then
    echo "❌ ERROR: Results directory not found: $RESULTS_DIR"
    exit 1
fi

echo "📁 Results directory: $RESULTS_DIR"
echo ""

# Find the PDB file with conservation scores
PDB_FILE=$(find "$RESULTS_DIR" -name "*_With_Conservation_Scores.pdb" -type f | head -1)

if [ -z "$PDB_FILE" ]; then
    echo "❌ ERROR: No PDB file with conservation scores found in $RESULTS_DIR"
    echo "   Looking for: *_With_Conservation_Scores.pdb"
    echo ""
    echo "Please run ConSurf analysis first (3_run_consurf_complete.sh)"
    exit 1
fi

PDB_BASENAME=$(basename "$PDB_FILE")
echo "✓ Found PDB file: $PDB_BASENAME"

# Check for consurf_grades.txt
if [ ! -f "$RESULTS_DIR/consurf_grades.txt" ]; then
    echo "❌ ERROR: consurf_grades.txt not found in $RESULTS_DIR"
    exit 1
fi

echo "✓ Found conservation grades file"
echo ""

# Activate conda environment
echo "Activating conda environment: $CONDA_ENV"
eval "$(conda shell.bash hook)"
conda activate "$CONDA_ENV"

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to activate conda environment: $CONDA_ENV"
    exit 1
fi

echo "✓ Conda environment activated"
echo ""

# Create Python script to generate PyMOL session
echo "Generating PyMOL session..."

# Export variables for Python script
export RESULTS_DIR
export PDB_FILE

python3 << 'PYTHON_SCRIPT'
import sys
import os

# Get environment variables
results_dir = os.environ.get('RESULTS_DIR', './results_final')
pdb_file = os.environ.get('PDB_FILE', '')

if not pdb_file or not os.path.exists(pdb_file):
    print(f"ERROR: PDB file not found: {pdb_file}")
    sys.exit(1)

# Import PyMOL
try:
    import pymol
    from pymol import cmd
except ImportError:
    print("ERROR: PyMOL not found in conda environment")
    print("Please install: conda install -c conda-forge pymol-open-source")
    sys.exit(1)

# Initialize PyMOL in quiet mode
pymol.finish_launching(['pymol', '-qc'])

print(f"Loading structure: {os.path.basename(pdb_file)}")

# Load the PDB file
object_name = os.path.splitext(os.path.basename(pdb_file))[0]
cmd.load(pdb_file, object_name)

print("Applying ConSurf conservation coloring...")

# Define ConSurf color scale (traditional)
# Grade 9 (conserved) → Maroon/Purple
# Grade 5 (neutral) → White
# Grade 1 (variable) → Turquoise/Cyan
# Grade * (insufficient data) → Gray (80%)

consurf_colors = {
    1: [0x16/255.0, 0xE4/255.0, 0xE4/255.0],  # Turquoise (variable)
    2: [0x4D/255.0, 0xF0/255.0, 0xF0/255.0],  # Light cyan
    3: [0x80/255.0, 0xFA/255.0, 0xFA/255.0],  # Very light cyan
    4: [0xB3/255.0, 0xFC/255.0, 0xFC/255.0],  # Pale cyan
    5: [0xFF/255.0, 0xFF/255.0, 0xFF/255.0],  # White (neutral)
    6: [0xFC/255.0, 0xC4/255.0, 0xE8/255.0],  # Pale pink
    7: [0xF5/255.0, 0x8C/255.0, 0xD4/255.0],  # Light magenta
    8: [0xE8/255.0, 0x55/255.0, 0xBF/255.0],  # Medium magenta
    9: [0x7D/255.0, 0x26/255.0, 0xCD/255.0],  # Purple (conserved)
    '*': [0.8, 0.8, 0.8]  # Gray for insufficient data
}

# Create PyMOL color definitions
for grade, rgb in consurf_colors.items():
    if grade == '*':
        color_name = 'consurf_insufficient'
    else:
        color_name = f'consurf_{grade}'
    cmd.set_color(color_name, rgb)

print("Coloring residues by conservation grade...")

# Read consurf_grades.txt to get grade assignments
grades_file = os.path.join(results_dir, 'consurf_grades.txt')
residue_grades = {}

try:
    with open(grades_file, 'r') as f:
        # Skip header lines until we find the data section
        for line in f:
            if line.strip().startswith('POS') and 'SEQ' in line:
                break
        
        # Read residue data
        for line in f:
            line = line.strip()
            if not line or line.startswith('-'):
                continue
            
            parts = line.split()
            if len(parts) < 5:
                continue
            
            try:
                pos = int(parts[0])
                # Extract chain and residue number from ATOM column (e.g., "CYS:1:A")
                if ':' in parts[2]:
                    atom_parts = parts[2].split(':')
                    if len(atom_parts) >= 3:
                        resnum = int(atom_parts[1])
                        chain = atom_parts[2]
                        grade = parts[4]  # COLOR column
                        
                        residue_grades[(chain, resnum)] = grade
            except (ValueError, IndexError):
                continue

except FileNotFoundError:
    print(f"ERROR: Could not find grades file: {grades_file}")
    sys.exit(1)

print(f"Found {len(residue_grades)} residues with conservation grades")

# Apply colors to residues
colored_count = 0
insufficient_count = 0

for (chain, resnum), grade in residue_grades.items():
    selection = f"chain {chain} and resi {resnum}"
    
    if grade == '*':
        cmd.color('consurf_insufficient', selection)
        insufficient_count += 1
    else:
        try:
            grade_num = int(grade)
            if 1 <= grade_num <= 9:
                cmd.color(f'consurf_{grade_num}', selection)
                colored_count += 1
        except ValueError:
            pass

print(f"✓ Colored {colored_count} residues by conservation")
print(f"✓ Marked {insufficient_count} residues with insufficient data (gray)")

# Set visualization style
print("Setting visualization style...")

# Show as cartoon (using default settings)
cmd.hide('everything', object_name)
cmd.show('cartoon', object_name)

# Keep PyMOL defaults - don't override cartoon settings
# Background stays black (PyMOL default)

# Zoom to fit
cmd.zoom(object_name)

# Orient for good initial view
cmd.orient(object_name)

# Create a color bar/legend for the conservation scale
print("Creating conservation scale legend...")

# Create pseudoatom objects to display the color scale
legend_objects = []
for grade in range(1, 10):
    obj_name = f'legend_grade_{grade}'
    # Position legend items vertically on the right side
    cmd.pseudoatom(obj_name, pos=[40, 50 - (grade * 6), 0])
    cmd.color(f'consurf_{grade}', obj_name)
    cmd.show('spheres', obj_name)
    cmd.set('sphere_scale', 2.0, obj_name)
    legend_objects.append(obj_name)

# Group legend objects
cmd.group('ConSurf_Legend', ' '.join(legend_objects))

# Add labels for the scale
cmd.pseudoatom('legend_label_conserved', pos=[40, 54, 0])
cmd.label('legend_label_conserved', '"Conserved (9)"')
cmd.pseudoatom('legend_label_variable', pos=[40, -4, 0])
cmd.label('legend_label_variable', '"Variable (1)"')
cmd.hide('everything', 'legend_label_*')
cmd.set('label_size', 20)
cmd.set('label_color', 'white')

# Save PyMOL session
output_file = os.path.join(results_dir, 'consurf_session.pse')
cmd.save(output_file)

print(f"\n✓ PyMOL session saved: {os.path.basename(output_file)}")
print(f"   Full path: {os.path.abspath(output_file)}")

# Quit PyMOL
cmd.quit()

PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✓ PYMOL SESSION GENERATION COMPLETE!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📊 Output file: $RESULTS_DIR/consurf_session.pse"
    echo ""
    echo "🎨 Color Scale:"
    echo "   Grade 9 (Purple)     → Highly Conserved"
    echo "   Grade 5 (White)      → Average/Neutral"
    echo "   Grade 1 (Turquoise)  → Variable"
    echo "   Gray (80%)           → Insufficient Data"
    echo ""
    echo "🔬 To open in PyMOL:"
    echo "   pymol $RESULTS_DIR/consurf_session.pse"
    echo ""
else
    echo ""
    echo "❌ ERROR: PyMOL session generation failed"
    exit 1
fi
