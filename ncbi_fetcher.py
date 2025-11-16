"""NCBI GEO data fetcher with improved XML parsing."""

import requests
import xml.etree.ElementTree as ET
import time
from typing import List, Dict, Optional
from config import (
    NCBI_ESEARCH_URL,
    NCBI_ESUMMARY_URL,
    NCBI_REQUEST_DELAY,
    DEFAULT_NCBI_QUERY,
    DEFAULT_MAX_RESULTS,
    DEFAULT_CHUNK_SIZE
)
from utils import safe_find_text, extract_pmid, map_platform_name, clean_text


class NCBIFetcher:
    """Fetches spatial transcriptomics data from NCBI GEO."""
    
    def __init__(self, email: Optional[str] = None):
        """
        Initialize NCBI fetcher.
        
        Args:
            email: Email for NCBI API (optional but recommended)
        """
        self.email = email
        self.request_delay = NCBI_REQUEST_DELAY
    
    def search(self, query: str = DEFAULT_NCBI_QUERY, max_results: int = DEFAULT_MAX_RESULTS) -> List[str]:
        """
        Search NCBI GEO for studies matching the query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
        
        Returns:
            List of GEO study IDs
        """
        print(f"🔍 Searching NCBI GEO for: {query[:100]}...")
        
        params = {
            "db": "gds",
            "term": query,
            "retmax": max_results,
            "usehistory": "y",
            "retmode": "xml"
        }
        
        if self.email:
            params["email"] = self.email
        
        try:
            response = requests.get(NCBI_ESEARCH_URL, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ Error during NCBI search: {e}")
            return []
        
        try:
            root = ET.fromstring(response.content)
            id_list = [id_elem.text for id_elem in root.findall(".//Id") if id_elem.text]
            
            if not id_list:
                print("⚠️  No results found in NCBI GEO.")
                return []
            
            print(f"✅ Found {len(id_list)} NCBI GEO study IDs")
            return id_list
            
        except ET.ParseError as e:
            print(f"❌ Error parsing NCBI search results: {e}")
            return []
    
    def fetch_summaries(self, id_list: List[str], chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[Dict]:
        """
        Fetch detailed summaries for GEO IDs.
        
        Args:
            id_list: List of GEO IDs
            chunk_size: Number of IDs to fetch per request
        
        Returns:
            List of study dictionaries
        """
        if not id_list:
            return []
        
        studies = []
        total_chunks = (len(id_list) + chunk_size - 1) // chunk_size
        
        print(f"📥 Fetching summaries for {len(id_list)} studies in {total_chunks} chunks...")
        
        for i in range(0, len(id_list), chunk_size):
            chunk = id_list[i:i + chunk_size]
            chunk_num = i // chunk_size + 1
            
            print(f"   Processing chunk {chunk_num}/{total_chunks}...", end="\r")
            
            params = {
                "db": "gds",
                "id": ",".join(chunk),
                "retmode": "xml"
            }
            
            if self.email:
                params["email"] = self.email
            
            try:
                response = requests.get(NCBI_ESUMMARY_URL, params=params, timeout=30)
                response.raise_for_status()
                
                # Parse this chunk
                chunk_studies = self._parse_summaries(response.content)
                studies.extend(chunk_studies)
                
            except requests.RequestException as e:
                print(f"\n⚠️  Error fetching chunk {chunk_num}: {e}")
                continue
            except Exception as e:
                print(f"\n⚠️  Error processing chunk {chunk_num}: {e}")
                continue
            
            # Rate limiting
            time.sleep(self.request_delay)
        
        print(f"\n✅ Successfully parsed {len(studies)} NCBI GEO summaries")
        return studies
    
    def _parse_summaries(self, xml_content: bytes) -> List[Dict]:
        """
        Parse XML summaries from NCBI.
        
        Args:
            xml_content: XML response content
        
        Returns:
            List of parsed study dictionaries
        """
        studies = []
        
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            print(f"\n⚠️  XML parsing error: {e}")
            return studies
        
        for docsum in root.findall(".//DocSum"):
            try:
                # Extract basic fields
                accession = safe_find_text(docsum, 'Name', 'Accession')
                title = clean_text(safe_find_text(docsum, 'Name', 'title'))
                public_date = safe_find_text(docsum, 'Name', 'PDAT')
                organism = safe_find_text(docsum, 'Name', 'taxon')
                summary = clean_text(safe_find_text(docsum, 'Name', 'summary'))
                platform_gpl = safe_find_text(docsum, 'Name', 'GPL')
                samples = safe_find_text(docsum, 'Name', 'n_samples')
                
                # Extract Experiment Type - use gdsType and ptechType
                exp_type = self._extract_experiment_type(docsum)
                
                 # Extract Publication/PMID - use PubMedIds and Relations
                publication = self._extract_publication(docsum)
                
                # Map platform to readable name
                platform = map_platform_name(platform_gpl)
                
                # Generate download link
                download_link = ""
                if accession:
                    download_link = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}"
                
                studies.append({
                    "Platform": platform,
                    "Accession": accession,
                    "Title": title,
                    "Public Date": public_date,
                    "Experiment Type": exp_type,
                    "Organism": organism,
                    "Summary (for Tissue)": summary,
                    "Samples": samples,
                    "Publication": publication,
                    "Download Link": download_link,
                    "Source": "NCBI GEO"
                })
                
            except Exception as e:
                # Skip problematic entries but continue
                continue
        
        return studies
    
    def _extract_experiment_type(self, docsum) -> str:
        """
        Extract experiment type from DocSum with robust parsing.
        
        Args:
            docsum: XML DocSum element
        
        Returns:
            Experiment type string
        """
        exp_types = []
        
        # Try gdsType (e.g., \"Expression profiling by array\", \"Other\")
        gds_type = safe_find_text(docsum, 'Name', 'gdsType')
        if gds_type and gds_type != "Other":
            exp_types.append(gds_type)
        
        # Try ptechType (platform technology type)
        ptech_type = safe_find_text(docsum, 'Name', 'ptechType')
        if ptech_type:
            exp_types.append(ptech_type)
        
        # Try entryType 
        entry_type = safe_find_text(docsum, 'Name', 'entryType')
        if entry_type and entry_type not in ['GSE', 'GDS']:
            exp_types.append(entry_type)
        
        # Try legacy ExpType field (from older records)
        
        # Try to find ExpType item
        exp_type_item = docsum.find("./Item[@Name='ExpType']")
        
        if exp_type_item is not None:
            # Check if it's a LIST container
            if exp_type_item.get('Type') == 'List':
                # Find inner text items
                inner_items = exp_type_item.findall("./Item[@Name='ExpType']")
                if inner_items:
                    # Take the first one or join multiple
                    types = [item.text.strip() for item in inner_items if item.text]
                    exp_types.extend(types)
            elif exp_type_item.text:
                exp_types.append(exp_type_item.text.strip())
        
        # Remove duplicates and join
        exp_types = list(dict.fromkeys(exp_types))  # preserve order, remove duplicates
        
        if exp_types:
            return ", ".join(exp_types)
        
        return "Spatial Transcriptomics"  # Default for ST datasets
    
    def _extract_publication(self, docsum) -> str:
        """
        Extract publication PMID from DocSum with robust parsing.
        
        Args:
            docsum: XML DocSum element
        
        Returns:
            PMID string
        """
        publication = ""
        
        # First try PubMedIds field (most reliable)
        pubmed_item = docsum.find("./Item[@Name='PubMedIds']")
        if pubmed_item is not None:
            # This is typically a List
            if pubmed_item.get('Type') == 'List':
                # Find all inner Int items
                inner_items = pubmed_item.findall(".Item")
                if inner_items:
                    for item in inner_items:
                        if item.text:
                            # Clean and get first PMID
                            pmid = item.text.strip()
                            if pmid and pmid.isdigit():
                                publication = pmid
                                break
            elif pubmed_item.text:
                pmid = pubmed_item.text.strip()
                if pmid and pmid.isdigit():
                    publication = pmid
        
        # Fallback: try Relations field
        if not publication:
            relations_item = docsum.find("./Item[@Name='Relations']")
            if relations_item is not None and relations_item.get('Type') == 'List':
                all_relations = relations_item.findall(".Item")
                for rel in all_relations:
                    if rel.text and "pubmed" in rel.text.lower():
                        pmid = extract_pmid(rel.text)
                        if pmid:
                            publication = pmid
                            break
        
        # Another fallback: try ExtRelations
        if not publication:
            ext_rel_item = docsum.find("./Item[@Name='ExtRelations']")
            if ext_rel_item is not None and ext_rel_item.get('Type') == 'List':
                all_relations = ext_rel_item.findall(".Item")
                for rel in all_relations:
                    if rel.text:
                        pmid = extract_pmid(rel.text)
                        if pmid:
                            publication = pmid
                            break
            
        
        return publication
    
    def fetch_all(self, query: str = DEFAULT_NCBI_QUERY, max_results: int = DEFAULT_MAX_RESULTS) -> List[Dict]:
        """
        Convenience method to search and fetch in one call.
        
        Args:
            query: Search query
            max_results: Maximum results
        
        Returns:
            List of study dictionaries
        """
        id_list = self.search(query, max_results)
        if not id_list:
            return []
        
        return self.fetch_summaries(id_list)
