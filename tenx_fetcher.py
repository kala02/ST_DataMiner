"""10x Genomics datasets fetcher."""

import requests
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import json
import re
from config import GENERAL_REQUEST_DELAY


class TenXFetcher:
    """Fetches spatial transcriptomics datasets from 10x Genomics."""
    
    def __init__(self):
        """Initialize 10x Genomics fetcher."""
        self.base_url = "https://www.10xgenomics.com"
        self.datasets_api = "https://www.10xgenomics.com/support/spatial-gene-expression-ffpe/documentation/datasets"
        self.request_delay = GENERAL_REQUEST_DELAY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_datasets(self) -> List[Dict]:
        """
        Fetch spatial transcriptomics datasets from 10x Genomics.
        
        Returns:
            List of dataset dictionaries
        """
        print("🔍 Fetching datasets from 10x Genomics...")
        
        datasets = []
        
        try:
            # Try to fetch live data from 10x Genomics
            live_datasets = self._fetch_live_datasets()
            
            if live_datasets:
                datasets = live_datasets
            else:
                # Fallback to curated list if scraping fails
                print("   ⚠️  Live fetching failed, using curated list as fallback...")
                datasets = self._get_curated_10x_datasets()
            
            print(f"✅ Found {len(datasets)} datasets from 10x Genomics")
            
        except Exception as e:
            print(f"⚠️  Error fetching 10x Genomics data: {e}")
            print("   Using curated list as fallback...")
            datasets = self._get_curated_10x_datasets()
        
        return datasets
    
    def _fetch_live_datasets(self) -> List[Dict]:
        """
        Fetch live datasets from 10x Genomics website.
        
        Returns:
            List of dataset dictionaries
        """
        datasets = []
        
        # 10x has multiple dataset pages, try different URLs
        dataset_pages = [
            "https://www.10xgenomics.com/datasets?query=&page=1&configure%5BhitsPerPage%5D=500&configure%5BgetRankingInfo%5D=true&refinementList%5Bspecies%5D=&refinementList%5Bproduct.name%5D%5B0%5D=Spatial%20Gene%20Expression",
            "https://cf.10xgenomics.com/supp/spatial-exp/spatial_datasets.json"  # Possible API endpoint
        ]
        
        for url in dataset_pages:
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    
                    # Try to parse as JSON first (API endpoint)
                    if 'json' in url or response.headers.get('content-type', '').startswith('application/json'):
                        try:
                            data = response.json()
                            parsed = self._parse_json_response(data)
                            if parsed:
                                datasets.extend(parsed)
                                continue
                        except:
                            pass
                    
                    # Parse HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    parsed = self._parse_html_datasets(soup)
                    if parsed:
                        datasets.extend(parsed)
                        break
                
                time.sleep(self.request_delay)
                
            except Exception as e:
                print(f"   Failed to fetch from {url[:50]}...: {e}")
                continue
        
        # Remove duplicates based on title
        if datasets:
            seen = set()
            unique_datasets = []
            for d in datasets:
                if d['Title'] not in seen:
                    seen.add(d['Title'])
                    unique_datasets.append(d)
            return unique_datasets
        
        return []
    
    def _parse_json_response(self, data: dict) -> List[Dict]:
        """Parse JSON API response."""
        datasets = []
        
        # Try different possible JSON structures
        items = data.get('datasets', data.get('hits', data.get('results', [])))
        
        for item in items:
            try:
                # Check if it's a spatial dataset
                product = item.get('product', {})
                if 'spatial' not in str(product).lower():
                    continue
                
                dataset = {
                    "Platform": "10x Genomics Visium",
                    "Accession": item.get('id', f"10x-{item.get('name', 'unknown')}"),
                    "Title": item.get('title', item.get('name', '')),
                    "Public Date": item.get('date', item.get('publicationDate', '')),
                    "Experiment Type": "Spatial Gene Expression",
                    "Organism": item.get('species', item.get('organism', '')),
                    "Summary (for Tissue)": item.get('description', item.get('summary', '')),
                    "Samples": "1",
                    "Publication": " ",
                    "Download Link": item.get('url', item.get('link', '')),
                    "Source": "10x Genomics"
                }
                datasets.append(dataset)
            except:
                continue
        
        return datasets
    
    def _parse_html_datasets(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse HTML page for datasets."""
        datasets = []
        
        # Look for dataset cards/entries
        # 10x typically uses divs or cards for datasets
        potential_containers = [
            soup.find_all('div', class_=re.compile(r'dataset|card|item', re.I)),
            soup.find_all('article'),
            soup.find_all('li', class_=re.compile(r'dataset|result', re.I))
        ]
        
        for containers in potential_containers:
            for item in containers:
                try:
                    # Try to extract title
                    title_elem = item.find(['h1', 'h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|name', re.I))
                    if not title_elem:
                        title_elem = item.find('a')
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Check if it's spatial-related
                    item_text = item.get_text().lower()
                    if 'spatial' not in item_text and 'visium' not in item_text:
                        continue
                    
                    # Extract organism
                    organism = "Unknown"
                    if 'human' in item_text:
                        organism = "Homo sapiens"
                    elif 'mouse' in item_text:
                        organism = "Mus musculus"
                    
                    # Extract link
                    link = " "
                    link_elem = item.find('a', href=True)
                    if link_elem:
                        link = link_elem['href']
                        if not link.startswith('http'):
                            link = self.base_url + link
                    
                    # Extract description
                    desc_elem = item.find(['p', 'div'], class_=re.compile(r'description|summary', re.I))
                    description = desc_elem.get_text(strip=True) if desc_elem else " "
                    
                    dataset = {
                        "Platform": "10x Genomics Visium",
                        "Accession": f"10x-{hash(title) % 100000}",
                        "Title": title,
                        "Public Date": " ",
                        "Experiment Type": "Spatial Gene Expression",
                        "Organism": organism,
                        "Summary (for Tissue)": description,
                        "Samples": "1",
                        "Publication": " ",
                        "Download Link": link,
                        "Source": "10x Genomics"
                    }
                    datasets.append(dataset)
                    
                except Exception as e:
                    continue
        return datasets
    
    def _get_curated_10x_datasets(self) -> List[Dict]:
        """Use enhanced comprehensive dataset list."""
        from tenx_enhanced import TenXEnhancedFetcher
        enhanced = TenXEnhancedFetcher()
        return enhanced._get_comprehensive_10x_datasets()
    
    def _get_curated_10x_datasets_old(self) -> List[Dict]:
        """
        Get curated list of 10x Genomics spatial transcriptomics datasets.
        
        Returns:
            List of dataset dictionaries
        """
        # Curated list of well-known 10x Visium datasets
        datasets = [
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-brain-1",
                "Title": "Human Brain Section (Coronal)",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "Coronal section of the human brain, showing multiple anatomical regions",
                "Samples": "1",
                "Publication": "",
                "Download Link": "https://www.10xgenomics.com/resources/datasets/human-brain-section-coronal-1-standard-1-0-0",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-heart-1",
                "Title": "Human Heart",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "Fresh frozen human heart tissue",
                "Samples": "1",
                "Publication": "",
                "Download Link": "https://www.10xgenomics.com/resources/datasets/human-heart-1-standard-1-0-0",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-breast-cancer-1",
                "Title": "Human Breast Cancer (Block A Section 1)",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "Invasive ductal carcinoma breast tissue",
                "Samples": "1",
                "Publication": "",
                "Download Link": "https://www.10xgenomics.com/resources/datasets/human-breast-cancer-block-a-section-1-1-standard-1-1-0",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-mouse-brain-1",
                "Title": "Mouse Brain Section (Coronal)",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Mus musculus",
                "Summary (for Tissue)": "Coronal section of adult mouse brain",
                "Samples": "1",
                "Publication": "",
                "Download Link": "https://www.10xgenomics.com/resources/datasets/mouse-brain-section-coronal-1-standard-1-0-0",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-mouse-kidney-1",
                "Title": "Mouse Kidney Section",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Mus musculus",
                "Summary (for Tissue)": "Fresh frozen adult mouse kidney tissue",
                "Samples": "1",
                "Publication": "",
                "Download Link": "https://www.10xgenomics.com/resources/datasets/mouse-kidney-section-coronal-1-standard-1-1-0",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-prostate-cancer",
                "Title": "Human Prostate Cancer with Invasive Carcinoma",
                "Public Date": "2021",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "FFPE human prostate cancer tissue with invasive carcinoma",
                "Samples": "1",
                "Publication": "",
                "Download Link": "https://www.10xgenomics.com/resources/datasets/human-prostate-cancer-with-invasive-carcinoma-ffpe-1-standard",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-colorectal-cancer",
                "Title": "Human Colorectal Cancer",
                "Public Date": "2021",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "FFPE human colorectal cancer tissue",
                "Samples": "1",
                "Publication": "",
                "Download Link": "https://www.10xgenomics.com/resources/datasets/human-colorectal-cancer-ffpe-1-standard",
                "Source": "10x Genomics"
            },
            {
                "Platform": "10x Genomics Visium",
                "Accession": "10x-human-lymph-node",
                "Title": "Human Lymph Node",
                "Public Date": "2020",
                "Experiment Type": "Spatial Gene Expression",
                "Organism": "Homo sapiens",
                "Summary (for Tissue)": "Fresh frozen human lymph node tissue",
                "Samples": "1",
                "Publication": "",
                "Download Link": "https://www.10xgenomics.com/resources/datasets/human-lymph-node-1-standard-1-1-0",
                "Source": "10x Genomics"
            },
        ]
        
        return datasets
