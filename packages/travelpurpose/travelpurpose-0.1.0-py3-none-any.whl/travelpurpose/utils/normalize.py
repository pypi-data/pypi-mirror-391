"""
Text normalization and city name processing utilities.
"""

import logging
import re
import unicodedata
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


def normalize_city_name(name: str) -> str:
    """
    Normalize city name for matching.

    Args:
        name: Raw city name

    Returns:
        Normalized city name
    """
    if not name:
        return ""

    # Convert to lowercase
    name = name.lower()

    # Remove common suffixes
    suffixes = [" city", " metropolitan", " metro", " province", " region"]
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[: -len(suffix)]

    # Strip and collapse whitespace
    name = " ".join(name.split())

    return name


def to_ascii(text: str) -> str:
    """
    Convert text to ASCII, preserving readability.

    Args:
        text: Input text

    Returns:
        ASCII version of text
    """
    # Normalize to NFKD form and encode to ASCII, ignoring errors
    return (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").strip()
    )


def normalize_tag(tag: str) -> str:
    """
    Normalize a tag for matching.

    Args:
        tag: Raw tag string

    Returns:
        Normalized tag
    """
    if not tag:
        return ""

    # Convert to lowercase
    tag = tag.lower()

    # Remove special characters except spaces, hyphens, underscores
    tag = re.sub(r"[^a-z0-9\s\-_]", "", tag)

    # Replace spaces and hyphens with underscores
    tag = re.sub(r"[\s\-]+", "_", tag)

    # Remove leading/trailing underscores
    tag = tag.strip("_")

    # Collapse multiple underscores
    tag = re.sub(r"_+", "_", tag)

    return tag


def extract_keywords(text: str, min_length: int = 3) -> Set[str]:
    """
    Extract keywords from text.

    Args:
        text: Input text
        min_length: Minimum keyword length

    Returns:
        Set of keywords
    """
    if not text:
        return set()

    # Convert to lowercase
    text = text.lower()

    # Remove special characters
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Split into words
    words = text.split()

    # Filter by length and common stop words
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "can",
    }

    keywords = {w for w in words if len(w) >= min_length and w not in stop_words}

    return keywords


def fuzzy_match_tag(tag: str, keyword_list: List[str], threshold: float = 0.7) -> Optional[str]:
    """
    Fuzzy match a tag against a list of keywords.

    Args:
        tag: Tag to match
        keyword_list: List of keywords to match against
        threshold: Similarity threshold (0-1)

    Returns:
        Best matching keyword or None
    """
    from difflib import SequenceMatcher

    tag_norm = normalize_tag(tag)
    if not tag_norm:
        return None

    best_match = None
    best_score = 0.0

    for keyword in keyword_list:
        keyword_norm = normalize_tag(keyword)
        if not keyword_norm:
            continue

        # Check for substring match
        if tag_norm in keyword_norm or keyword_norm in tag_norm:
            return keyword

        # Compute similarity
        score = SequenceMatcher(None, tag_norm, keyword_norm).ratio()
        if score > best_score:
            best_score = score
            best_match = keyword

    if best_score >= threshold:
        return best_match

    return None


def deduplicate_cities(cities: List[Dict]) -> List[Dict]:
    """
    Deduplicate cities by wikidata_id or normalized name+country.

    Args:
        cities: List of city dictionaries

    Returns:
        Deduplicated list
    """
    seen = set()
    unique = []

    for city in cities:
        # Prefer wikidata_id for deduplication
        if "wikidata_id" in city and city["wikidata_id"]:
            key = f"wikidata:{city['wikidata_id']}"
        else:
            # Fall back to name+country
            name = normalize_city_name(city.get("name", ""))
            country = city.get("country", "").lower()
            key = f"{name}:{country}"

        if key not in seen:
            seen.add(key)
            unique.append(city)

    logger.info(f"Deduplicated {len(cities)} cities to {len(unique)} unique entries")
    return unique


def translate_tag(tag: str, source_lang: str = "auto", target_lang: str = "en") -> str:
    """
    Translate a tag to English (placeholder - can integrate translation API).

    Args:
        tag: Tag to translate
        source_lang: Source language code
        target_lang: Target language code

    Returns:
        Translated tag (currently just returns original with normalization)
    """
    # For now, just normalize. In production, integrate translation API.
    # Examples: Google Translate API, DeepL, Azure Translator
    return normalize_tag(tag)


def parse_json_ld(html_content: str) -> List[Dict]:
    """
    Extract JSON-LD structured data from HTML.

    Args:
        html_content: HTML content

    Returns:
        List of JSON-LD objects
    """
    import json

    from bs4 import BeautifulSoup

    try:
        soup = BeautifulSoup(html_content, "lxml")
        scripts = soup.find_all("script", {"type": "application/ld+json"})

        json_ld_objects = []
        for script in scripts:
            try:
                data = json.loads(script.string)
                json_ld_objects.append(data)
            except json.JSONDecodeError:
                continue

        return json_ld_objects
    except Exception as e:
        logger.error(f"Failed to parse JSON-LD: {e}")
        return []


def extract_meta_tags(html_content: str) -> Dict[str, str]:
    """
    Extract meta tags from HTML.

    Args:
        html_content: HTML content

    Returns:
        Dictionary of meta tag properties
    """
    from bs4 import BeautifulSoup

    try:
        soup = BeautifulSoup(html_content, "lxml")
        meta_tags = {}

        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")
            if name and content:
                meta_tags[name] = content

        return meta_tags
    except Exception as e:
        logger.error(f"Failed to extract meta tags: {e}")
        return {}


def extract_headings(html_content: str) -> List[str]:
    """
    Extract H1 and H2 headings from HTML.

    Args:
        html_content: HTML content

    Returns:
        List of heading texts
    """
    from bs4 import BeautifulSoup

    try:
        soup = BeautifulSoup(html_content, "lxml")
        headings = []

        for tag in ["h1", "h2"]:
            for heading in soup.find_all(tag):
                text = heading.get_text(strip=True)
                if text:
                    headings.append(text)

        return headings
    except Exception as e:
        logger.error(f"Failed to extract headings: {e}")
        return []
