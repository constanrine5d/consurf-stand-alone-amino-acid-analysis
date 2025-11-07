# Fork and Push to Public GitHub Repository

## Option 1: Fork on GitHub (Recommended)

### 1. Fork the Original Repository

1. Go to https://github.com/leezx/ConSurf-StandAlone
2. Click the **"Fork"** button (top right)
3. Choose your account as the destination
4. Wait for GitHub to create the fork

### 2. Update Your Local Repository

```bash
# Check current remote
git remote -v

# Update origin to point to YOUR forked repository
git remote set-url origin git@github.com:YOUR_USERNAME/ConSurf-StandAlone.git

# Verify it's correct
git remote -v

# Add original repo as 'upstream' (to track original)
git remote add upstream https://github.com/leezx/ConSurf-StandAlone.git

# Verify both remotes exist
git remote -v
# Should show:
# origin    git@github.com:YOUR_USERNAME/ConSurf-StandAlone.git (fetch)
# origin    git@github.com:YOUR_USERNAME/ConSurf-StandAlone.git (push)
# upstream  https://github.com/leezx/ConSurf-StandAlone.git (fetch)
# upstream  https://github.com/leezx/ConSurf-StandAlone.git (push)
```

### 3. Push Your Enhanced Version

```bash
# Push your commit to your fork
git push origin main

# If it asks for force (because of different history):
git push origin main --force-with-lease
```

### 4. Update Repository Description

After pushing, go to your forked repository:
1. Click **"About"** ⚙️ (settings gear, top right of repo)
2. Add description:
   ```
   ConSurf Stand-Alone with enhanced amino acid distribution analysis - Fork of leezx/ConSurf-StandAlone
   ```
3. Add topics:
   - `bioinformatics`
   - `protein-analysis`
   - `conservation-analysis`
   - `consurf`
   - `evolutionary-conservation`
   - `amino-acid-analysis`
   - `sequence-analysis`

---

## Option 2: Create New Repo with Attribution (Alternative)

If forking doesn't work or you want a fresh start:

### 1. Create New Public Repository

1. Go to https://github.com/new
2. **Repository name**: `ConSurf-StandAlone` or `ConSurf-AminoAcid-Analysis`
3. **Description**: "ConSurf Stand-Alone with enhanced amino acid distribution analysis"
4. **Visibility**: ✅ **Public**
5. **DO NOT** initialize with README
6. Click "Create repository"

### 2. Update Local Remote

```bash
# Remove old origin
git remote remove origin

# Add your new repo
git remote add origin git@github.com:YOUR_USERNAME/ConSurf-StandAlone.git

# Push
git push -u origin main
```

---

## Add Proper Attribution to README

The README.md already has a section for authors, but let's make attribution clearer:

### Add to the top of README.md:

```markdown
# ConSurf Stand-Alone with Amino Acid Analysis

> **Forked from**: [leezx/ConSurf-StandAlone](https://github.com/leezx/ConSurf-StandAlone)  
> **Original source**: [Rostlab/ConSurf](https://github.com/Rostlab/ConSurf)

A comprehensive toolkit for running ConSurf evolutionary conservation analysis locally, with **enhanced amino acid distribution analysis** and sequence grouping capabilities.
```

### Update Authors Section:

```markdown
## 👤 Authors & Attribution

- **Original ConSurf**: Haim Ashkenazy, Penn O., Doron-Faigenboim A., Cohen O., Cannarozzi G., Zomer O., Pupko T.
  - Web server: https://consurf.tau.ac.il/
  - Original repo: https://github.com/Rostlab/ConSurf (2015)

- **ConSurf Stand-Alone Setup**: [leezx](https://github.com/leezx)
  - Detailed installation guide and database setup
  - Source: https://github.com/leezx/ConSurf-StandAlone

- **Amino Acid Analysis Enhancement**: Constantine Grigorakis
  - Position-specific amino acid distribution analysis
  - Automated sequence grouping by amino acid
  - FASTA file organization and batch processing
```

---

## License Considerations

The original ConSurf and Rate4Site have their own licenses. Add a LICENSE file:

```markdown
# License

This repository contains multiple components with different origins:

## ConSurf Stand-Alone Scripts
- Original work from Tel Aviv University
- Available from: https://consurf.tau.ac.il/
- Stand-alone version setup by leezx

## Rate4Site Binaries
- Copyright: Tel Aviv University
- Website: https://www.tau.ac.il/~itaymay/cp/rate4site.html
- Pre-compiled binaries included for convenience

## Enhanced Analysis Tools (analyze_position.py and related scripts)
- Created by: Constantine Grigorakis
- License: MIT

```

---

## Quick Command Summary

```bash
# Check where you are
git remote -v
git log --oneline -5

# Fork on GitHub first, then:
git remote set-url origin git@github.com:YOUR_USERNAME/ConSurf-StandAlone.git
git remote add upstream https://github.com/leezx/ConSurf-StandAlone.git

# Push your changes
git push origin main

# If needed (different history):
git push origin main --force-with-lease

# Keep your fork updated with upstream later:
git fetch upstream
git merge upstream/main
```

---

## What Makes Your Fork Special

Document these improvements in your fork:

### ✨ New Features (vs. leezx/ConSurf-StandAlone):

1. **Amino Acid Distribution Analysis**
   - Analyze single, multiple, or all positions
   - Automatic amino acid counting and percentages
   - Chemical properties distribution

2. **Automated Sequence Organization**
   - Creates folder structure: `position_X_Y/covered/1_AA_XX.X/`
   - FASTA files grouped by amino acid at each position
   - Separate folders for gaps (not_covered)

3. **Enhanced Documentation**
   - Comprehensive README with emojis and clear sections
   - Step-by-step workflow guides
   - Example data with TtXyn30A protein

4. **Production-Ready Structure**
   - Numbered workflow scripts (1-4) for clear execution order
   - Complete .gitignore
   - Pre-compiled binaries included

5. **Example Data Included**
   - TtXyn30A protein analysis
   - Complete results in example/ folder
   - Demonstrates all features

---

## After Pushing

### Create a Nice GitHub README Display

Your repo will automatically show:
- ✅ README.md with nice formatting
- ✅ Fork badge (shows "forked from leezx/ConSurf-StandAlone")
- ✅ Topics/tags for discoverability

### Optional: Create a Release

After pushing:
```bash
# Tag your enhanced version
git tag -a v1.0.0 -m "First release: ConSurf with amino acid analysis"
git push origin v1.0.0
```

Then create a Release on GitHub with release notes.

---

## Keeping Your Fork Updated

If leezx updates their repo, you can merge changes:

```bash
# Fetch updates from original
git fetch upstream

# Merge into your main
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

---

**Ready to push!** 🚀

1. Fork https://github.com/leezx/ConSurf-StandAlone on GitHub
2. Update remote: `git remote set-url origin git@github.com:YOUR_USERNAME/ConSurf-StandAlone.git`
3. Push: `git push origin main`
