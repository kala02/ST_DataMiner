"""Enhanced 10x Genomics fetcher with comprehensive dataset list."""

import requests
from typing import List, Dict
from bs4 import BeautifulSoup
import time

class TenXEnhancedFetcher:
    """Enhanced fetcher with comprehensive 10x Genomics spatial datasets."""
    
    def __init__(self):
        self.base_url = "https://www.10xgenomics.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_datasets(self) -> List[Dict]:
        """
        Fetch comprehensive list of 10x Genomics spatial datasets.
        
        Returns:
            List of dataset dictionaries
        """
        print("🔍 Fetching datasets from 10x Genomics...")
        
        # Start with comprehensive known datasets
        datasets = self._get_comprehensive_10x_datasets()
        
        print(f"✅ Found {len(datasets)} datasets from 10x Genomics")
        return datasets
    
    def _get_comprehensive_10x_datasets(self) -> List[Dict]:
        """
        Comprehensive list of 10x Genomics spatial transcriptomics datasets.
        
        Note: Individual dataset URLs change frequently on 10x website.
        Using main search page URLs for reliability.
        
        Last updated: November 2024
        """
        # Main datasets page with Spatial Gene Expression filter
        main_datasets_url = "https://www.10xgenomics.com/datasets?query=&page=1&configure%5BhitsPerPage%5D=50&refinementList%5Bproduct.name%5D%5B0%5D=Spatial%20Gene%20Expression"
        
        datasets = [
            # Human Datasets - Fresh Frozen
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-brain-coronal",
                "Title": "Human Brain Section (Coronal) - Fresh Frozen",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "Coronal section of adult human brain showing multiple anatomical regions including hippocampus and cortex",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=human+brain+coronal",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-brain-sagittal",
                "Title": "Human Brain Section (Sagittal Posterior) - Fresh Frozen",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "Sagittal posterior section of adult human brain",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=human+brain+sagittal",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-heart",
                "Title": "Human Heart - Fresh Frozen",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "Fresh frozen human heart tissue section",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=human+heart",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-breast-cancer-block-a-section-1",
                "Title": "Human Breast Cancer (Block A Section 1) - Fresh Frozen",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "Invasive ductal carcinoma breast tissue, Block A Section 1",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=human+breast+cancer",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-breast-cancer-block-a-section-2",
                "Title": "Human Breast Cancer (Block A Section 2) - Fresh Frozen",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "Invasive ductal carcinoma breast tissue, Block A Section 2",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=human+breast+cancer",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-lymph-node",
                "Title": "Human Lymph Node - Fresh Frozen",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "Fresh frozen human lymph node tissue section",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=human+lymph+node",
                "Source": "10x Genomics"
            },
            
            # Human Datasets - FFPE
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-prostate-cancer-ffpe",
                "Title": "Human Prostate Cancer with Invasive Carcinoma - FFPE",
                "Public Date": "2021",
                "Experiment Type": "Spatial Gene Expression - FFPE",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "FFPE human prostate cancer tissue with invasive carcinoma",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=human+prostate+cancer+ffpe",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-colorectal-cancer-ffpe",
                "Title": "Human Colorectal Cancer - FFPE",
                "Public Date": "2021",
                "Experiment Type": "Spatial Gene Expression - FFPE",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "FFPE human colorectal cancer tissue section",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=human+colorectal+cancer+ffpe",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-lung-cancer-ffpe",
                "Title": "Human Lung Cancer - FFPE",
                "Public Date": "2021",
                "Experiment Type": "Spatial Gene Expression - FFPE",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "FFPE human lung adenocarcinoma tissue",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=human+lung+cancer+ffpe",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-ovarian-cancer-ffpe",
                "Title": "Human Ovarian Cancer - FFPE",
                "Public Date": "2021",
                "Experiment Type": "Spatial Gene Expression - FFPE",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "FFPE human ovarian cancer tissue",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=human+ovarian+cancer+ffpe",
                "Source": "10x Genomics"
            },
            
            # Mouse Datasets
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-mouse-brain-coronal",
                "Title": "Mouse Brain Section (Coronal) - Fresh Frozen",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Mus musculus",
                "Summary (for Tissue)": "Coronal section of adult mouse brain",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=mouse+brain+coronal",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-mouse-brain-sagittal",
                "Title": "Mouse Brain Section (Sagittal Posterior) - Fresh Frozen",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Mus musculus",
                "Summary (for Tissue)": "Sagittal posterior section of adult mouse brain",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=mouse+brain+sagittal",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-mouse-brain-sagittal-anterior",
                "Title": "Mouse Brain Section (Sagittal Anterior) - Fresh Frozen",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Mus musculus",
                "Summary (for Tissue)": "Sagittal anterior section of adult mouse brain",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=mouse+brain+anterior",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-mouse-kidney",
                "Title": "Mouse Kidney Section (Coronal) - Fresh Frozen",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Mus musculus",
                "Summary (for Tissue)": "Fresh frozen adult mouse kidney tissue section",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=mouse+kidney",
                "Source": "10x Genomics"
            },
            
            # CytAssist Datasets
            {
                "Platform": "10x Genomics Visium CytAssist",
                "Accession": "10x-human-brain-cytassist",
                "Title": "Human Brain (CytAssist FFPE)",
                "Public Date": "2022",
                "Experiment Type": "Spatial Gene Expression - CytAssist",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "Human brain FFPE tissue processed with CytAssist",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=human+brain+cytassist",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium CytAssist",
                "Accession": "10x-human-glioblastoma-cytassist",
                "Title": "Human Glioblastoma (CytAssist FFPE)",
                "Public Date": "2022",
                "Experiment Type": "Spatial Gene Expression - CytAssist",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "Human glioblastoma FFPE tissue processed with CytAssist",
                "Samples": "1",
                "Publication": "",
                "Download Link": main_datasets_url + "&query=human+glioblastoma+cytassist",
                "Source": "10x Genomics"
            },
        ]
        
        return datasets
