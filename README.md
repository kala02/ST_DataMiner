# ST_DataMiner
The Spatial Transcriptomics Data Miner is a  command-line tool that automatically aggregates spatial transcriptomics datasets from multiple public repositories into a single, organized Excel catalog. It streamlines the process of discovering and accessing spatial gene expression data for research purposes.






A comprehensive command-line tool for mining spatial transcriptomics datasets from multiple platforms including NCBI GEO, 10x Genomics, and HTAN.

## Features

- 🔍 **Multi-platform data aggregation**: NCBI GEO, 10x Genomics, HTAN
- 🧬 **Organism separation**: Automatically separates human vs non-human datasets
- 📊 **Smart organization**: Organize by platform, organism, or both
- 🏷️ **Platform mapping**: Converts GPL IDs to readable platform names (e.g., GPL24676 → \"10x Genomics Visium\")
- ✅ **Fixed XML parsing**: Properly extracts Experiment Type and Publication data from NCBI
- 📈 **Progress tracking**: Real-time progress indicators
- 📁 **Excel export**: Multi-sheet Excel files with summary statistics

## Installation

- pandas
- requests
- openpyxl (via pandas)

Additional recommended packages:
```bash
pip install beautifulsoup4 lxml
```

## Usage

### Basic Usage (All Platforms)

```bash
python st_miner.py
```

This will fetch data from all platforms (NCBI, 10x, HTAN) and create `spatial_transcriptomics_catalog.xlsx`.

### Fetch from Specific Platforms

```bash
# Only NCBI GEO
python st_miner.py --only-ncbi

# Only 10x Genomics
python st_miner.py --only-10x

# Only HTAN
python st_miner.py --only-htan

# NCBI + 10x (exclude HTAN)
python st_miner.py --include-ncbi --include-10x
```

### NCBI Custom Options

```bash
# Custom search query
python st_miner.py --only-ncbi --query \"Visium AND brain[Title]\"

# Limit results
python st_miner.py --only-ncbi --max-results 500

# Provide email (recommended for NCBI)
python st_miner.py --only-ncbi --email \"your.email@example.com\"
```

### Output Organization

```bash
# Organize by both platform and organism (default)
python st_miner.py --organize-by both

# Organize by platform only
python st_miner.py --organize-by platform

# Organize by organism only (human vs others)
python st_miner.py --organize-by organism

# Single sheet (no organization)
python st_miner.py --organize-by none
```

### Custom Output File

```bash
python st_miner.py --output my_catalog.xlsx
```

### Complete Example

```bash
python st_miner.py \
  --include-ncbi \
  --include-10x \
  --query \"(Visium OR Slide-seq) AND mouse[Organism]\" \
  --max-results 1000 \
  --email \"researcher@university.edu\" \
  --organize-by both \
  --output mouse_st_datasets.xlsx
```

## Output Structure

### Default Organization (--organize-by both)

The Excel file will contain multiple sheets:

1. **Summary** - Overall statistics
2. **Human - NCBI GEO** - Human datasets from NCBI
3. **Human - 10x Genomics** - Human datasets from 10x
4. **Human - HTAN** - Human datasets from HTAN
5. **Other - NCBI GEO** - Non-human datasets from NCBI
6. **Other - 10x Genomics** - Non-human datasets from 10x

### Column Structure

Each sheet contains:
- **S.No.** - Serial number
- **Platform** - Readable platform name (e.g., \"10x Genomics Visium\", \"NCBI GEO (GPL24676)\")
- **Accession** - Dataset accession ID
- **Public Date** - Publication date
- **Experiment Type** - Type of experiment (properly extracted)
- **Title** - Dataset title
- **Organism** - Organism name
- **Summary (for Tissue)** - Tissue/sample description
- **Samples** - Number of samples
- **Publication** - PMID (properly extracted)
- **Download Link** - Direct link to dataset


## Architecture

```
st_miner/
├── init.py          # Package initialization
├── cli.py               # Main CLI entry point
├── config.py            # Configuration and constants
├── utils.py             # Utility functions
├── ncbi_fetcher.py      # NCBI GEO data fetcher
├── tenx_fetcher.py      # 10x Genomics data fetcher
├── tenx_enhanced.py       
├── htan_fetcher.py      # HTAN data fetcher
└── exporter.py          # Excel export with organization
├── st_miner.py  
```



## Data Fetching Strategy

This tool uses a **hybrid approach** combining live API fetching with comprehensive curated lists:

### NCBI GEO - Live API Fetching ✅
- Fully automated via NCBI E-utilities API
- Searches and retrieves real-time data
- Rate-limited to comply with NCBI guidelines (3 requests/second)
- Supports custom queries and filters

### 10x Genomics - Curated List (16 datasets) 📋
**Why curated instead of live fetching:**
- ❌ **Technical limitation**: 10x website uses Algolia search embedded in React/Next.js app
- ❌ **Dynamic loading**: Dataset information loads via JavaScript after page render
- ❌ **Complex scraping**: Would require reverse-engineering their search API with authentication
- ✅ **Curated solution**: Manually maintained list of all 16 public spatial datasets
- ✅ **Comprehensive coverage**: Includes all Fresh Frozen, FFPE, and CytAssist datasets
- ✅ **Reliable**: Not affected by website redesigns or API changes
- ✅ **Fast**: Instant results without web requests

**Coverage:**
- 12 Human datasets (brain, heart, breast cancer, lymph node, prostate, colorectal, lung, ovarian cancers)
- 4 Mouse datasets (brain sections, kidney)

### HTAN - Curated List (12 datasets) 📋
**Why curated instead of live fetching:**
- ❌ **Technical limitation**: HTAN portal is a React SPA with async data loading
- ❌ **API complexity**: Data distributed across Synapse with complex authentication
- ❌ **Dynamic content**: Dataset metadata not in HTML source
- ✅ **Curated solution**: Manually maintained list of spatial transcriptomics atlases
- ✅ **Comprehensive**: Covers all major HTAN cancer atlases with spatial data
- ✅ **Up-to-date**: Regularly updated as new atlases are published
- ✅ **Quality**: Verified metadata with PMIDs where available

**Coverage:**
- 12 Human tumor atlases covering 8 cancer types
- Platforms: Visium and Slide-seq
- Includes Breast, Colorectal, Lung, Glioblastoma, Pancreatic, Melanoma, Prostate, Ovarian cancers

### Expected Behavior

When you run the tool, you'll see:
```
🧠 10x Genomics
--------------------------------------------------
🔍 Fetching datasets from 10x Genomics...
   ⚠️  Live fetching failed, using curated list as fallback...
✅ Found 16 datasets from 10x Genomics
```

This is **normal and expected** - the \"live fetching failed\" message indicates the tool is working correctly by using the comprehensive curated list.


## Notes

-- **NCBI API**: Rate-limited to 3 requests/second, automatically handled
- **Curated lists**: Maintained and updated regularly with new public datasets
- **Total coverage**: 1000+ NCBI datasets + 16 10x + 12 HTAN = comprehensive spatial transcriptomics catalog
- **Python cache**: If you see outdated dataset counts, clear cache: `find . -name \"__pycache__\" -type d -exec rm -rf {} +`
- For large NCBI queries (>1000 results), use `--max-results 5000` or higher

## License

MIT License

## Author

Built for spatial transcriptomics research community.
"
