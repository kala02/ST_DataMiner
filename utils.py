"""Utility functions for ST data miner."""

import xml.etree.ElementTree as ET
from typing import Optional, List
import re
from config import HUMAN_ORGANISMS, PLATFORM_MAPPINGS


def safe_find_text(element, name_attr: str, name_val: str) -> str:
    """
    Safely finds an XML item and returns its text.
    Returns "" if the item or text is not found.
    
    Args:
        element: XML element to search in
        name_attr: Attribute name (e.g., 'Name')
        name_val: Attribute value to match
    
    Returns:
        Text content or empty string
    """
    try:
        item = element.find(f".//Item[@{name_attr}='{name_val}']")
        if item is not None and item.text:
            return item.text.strip()
        return ""
    except AttributeError:
        return ""


def extract_pmid(text: str) -> str:
    """
    Extract PMID from text.
    
    Args:
        text: Text containing PMID
    
    Returns:
        PMID string or empty string
    """
    if not text:
        return ""
    
    # Try to find PMID: pattern
    if "PMID:" in text:
        try:
            pmid = text.split("PMID:")[1].split()[0].strip()
            # Remove any non-numeric characters
            pmid = re.sub(r'[^0-9]', '', pmid)
            return pmid if pmid else ""
        except (IndexError, AttributeError):
            pass
    
    # Try to find just numbers that look like PMIDs (typically 8 digits)
    pmid_match = re.search(r'\b(\d{7,9})\b', text)
    if pmid_match:
        return pmid_match.group(1)
    
    return ""


def is_human_organism(organism: str) -> bool:
    """
    Check if organism is human.
    
    Args:
        organism: Organism name
    
    Returns:
        True if human, False otherwise
    """
    if not organism:
        return False
    
    organism_lower = organism.lower().strip()
    return any(human.lower() in organism_lower for human in HUMAN_ORGANISMS)


def map_platform_name(platform_id: str) -> str:
    """
    Map platform GPL ID to readable name.
    
    Args:
        platform_id: GPL platform ID (with or without 'GPL' prefix)
    
    Returns:
        Readable platform name
    """
    if not platform_id:
        return "NCBI GEO"
    

    # Normalize platform_id - add GPL prefix if it's just numbers
    if platform_id.isdigit():
        platform_id = f"GPL{platform_id}"
    
    # Handle multiple platforms (semicolon-separated)
    if ";" in platform_id:
        platforms = [p.strip() for p in platform_id.split(";")]
        mapped_platforms = []
        for p in platforms:
            if p.isdigit():
                p = f"GPL{p}"
            # Check mappings
            mapped = None
            for gpl_id, name in PLATFORM_MAPPINGS.items():
                if gpl_id == p or gpl_id in p:
                    mapped = name
                    break
            if mapped:
                mapped_platforms.append(mapped)
            else:
                mapped_platforms.append(f"NCBI GEO ({p})")
        
        # Return unique platforms
        return "; ".join(list(dict.fromkeys(mapped_platforms)))

    # Check if it's in our mappings
    for gpl_id, name in PLATFORM_MAPPINGS.items():
        if gpl_id == platform_id or gpl_id in platform_id:
            return name
    
    # If it's a GPL ID, return as is with NCBI prefix
    if platform_id.startswith("GPL"):
        return f"NCBI GEO ({platform_id})"
    
    # Default
    return f"NCBI GEO (GPL{platform_id})"


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters.
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def validate_accession(accession: str) -> bool:
    """
    Validate GEO accession format.
    
    Args:
        accession: Accession string
    
    Returns:
        True if valid, False otherwise
    """
    if not accession:
        return False
    
    # GEO accessions typically start with GSE, GSM, GPL, etc.
    pattern = r'^G(SE|SM|PL|DS)\d+$'
    return bool(re.match(pattern, accession))
