"""Configuration and constants for ST data miner."""

# NCBI E-utilities base URLs
NCBI_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
NCBI_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# API rate limiting
NCBI_REQUEST_DELAY = 0.4  # seconds between requests (NCBI allows 3 requests/second)
GENERAL_REQUEST_DELAY = 1.0  # for other APIs

# Default search parameters
DEFAULT_NCBI_QUERY = '(("spatial transcriptomics"[All Fields] OR "Visium"[All Fields] OR "Slide-seq"[All Fields]) AND "gse"[Filter])'
DEFAULT_MAX_RESULTS = 1000
DEFAULT_CHUNK_SIZE = 100

# Human organism identifiers
HUMAN_ORGANISMS = [
    "Homo sapiens",
    "Human",
    "homo sapiens",
    "human"
]

# Platform mappings
PLATFORM_MAPPINGS = {
    "GPL24676": "10x Genomics Visium",
    "GPL21263": "10x Genomics 3' v3",
    "GPL20301": "10x Genomics 3' v2",
    "GPL16791": "Illumina HiSeq",
    "GPL18573": "Illumina NextSeq",
    "GPL24247": "Slide-seq",
    "GPL29210": "Slide-seqV2",
}

# Output file settings
DEFAULT_OUTPUT_FILE = "spatial_transcriptomics_catalog.xlsx"

# Column order for output
COLUMN_ORDER = [
    "S.No.",
    "Platform",
    "Accession",
    "Public Date",
    "Experiment Type",
    "Title",
    "Organism",
    "Summary (for Tissue)",
    "Samples",
    "Publication",
    "Download Link"
]
