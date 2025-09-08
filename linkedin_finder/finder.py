#!/usr/bin/env python3
"""
LinkedIn Profile Finder

A simple, standalone package to find LinkedIn profiles using search queries.

⚠️ LEGAL DISCLAIMER:
This tool is for educational and legitimate business purposes only.
Users must comply with LinkedIn's Terms of Service and all applicable laws.
The tool uses public search engines and does not scrape LinkedIn directly.
"""

import re
import time
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from ddgs import DDGS

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result of a LinkedIn profile search"""

    success: bool
    profile_url: Optional[str] = None
    title: Optional[str] = None
    query_used: Optional[str] = None
    strategy: Optional[int] = None
    error: Optional[str] = None


class LinkedInFinder:
    """Find LinkedIn profiles using optimized DDGS search"""

    def __init__(self, delay_between_requests: float = 1.0):
        """
        Initialize the LinkedIn finder

        Args:
            delay_between_requests: Delay between search requests in seconds
                                   (minimum 1.0 recommended for compliance)
        """
        # Ensure minimum delay for compliance
        self.delay_between_requests = max(delay_between_requests, 1.0)
        self.ddgs = DDGS()
        
        # Log compliance notice
        logger.info("⚠️  LinkedIn Finder: Use responsibly and comply with LinkedIn's ToS")

    def clean_name(self, name: str) -> str:
        """Clean and normalize name for search"""
        if not name:
            return ""

        # Remove common titles and suffixes
        name = re.sub(
            r"\b(Dr\.?|Mr\.?|Ms\.?|Mrs\.?|Prof\.?|PhD|MD|MBA|MS|BS|BA)\b",
            "",
            name,
            flags=re.IGNORECASE,
        )
        # Remove extra whitespace and commas
        name = re.sub(r"\s+", " ", name.strip().replace(",", ""))
        return name

    def clean_company(self, company: str) -> str:
        """Clean and normalize company name for search"""
        if not company:
            return ""

        # Remove common company suffixes for better matching
        company = re.sub(
            r"\b(Inc\.?|LLC|Corp\.?|Corporation|Company|Ltd\.?|Limited)\b",
            "",
            company,
            flags=re.IGNORECASE,
        )
        return company.strip()

    def generate_search_queries(
        self, name: str, company: str = "", job_title: str = ""
    ) -> List[str]:
        """Generate multiple search query variations"""
        clean_name = self.clean_name(name)
        clean_company = self.clean_company(company)

        queries = []

        # Strategy 1: Direct LinkedIn search with quotes
        if clean_company:
            queries.append(f'linkedin "{clean_name}" "{clean_company}"')
        else:
            queries.append(f'linkedin "{clean_name}"')

        # Strategy 2: Without quotes (broader search)
        if clean_company:
            queries.append(f"linkedin {clean_name} {clean_company}")
        else:
            queries.append(f"linkedin {clean_name}")

        # Strategy 3: Name + company + linkedin
        if clean_company:
            queries.append(f'"{clean_name}" "{clean_company}" linkedin')

        # Strategy 4: Just name + linkedin (if company search fails)
        queries.append(f'linkedin "{clean_name}"')

        # Strategy 5: Name + company + job title
        if job_title and clean_company:
            clean_job = self.clean_name(job_title)
            queries.append(f'linkedin "{clean_name}" "{clean_company}" "{clean_job}"')

        # Strategy 6: Site-specific search
        if clean_company:
            queries.append(f'site:linkedin.com/in/ "{clean_name}" "{clean_company}"')

        # Strategy 7: Alternative company name variations
        if clean_company:
            # Try without common words
            company_words = clean_company.split()
            if len(company_words) > 1:
                main_company = company_words[0]  # First word
                queries.append(f'linkedin "{clean_name}" "{main_company}"')

        return queries

    def search_profile(
        self, name: str, company: str = "", job_title: str = ""
    ) -> SearchResult:
        """
        Search for a LinkedIn profile

        Args:
            name: Person's name (required)
            company: Company name (optional)
            job_title: Job title (optional)

        Returns:
            SearchResult object with success status and profile URL if found
        """
        logger.info(f"Searching for: {name}" + (f" at {company}" if company else ""))

        queries = self.generate_search_queries(name, company, job_title)

        for i, query in enumerate(queries, 1):
            try:
                # Apply rate limiting
                time.sleep(self.delay_between_requests)

                # Search using DDGS
                results = list(
                    self.ddgs.text(
                        query=query,
                        max_results=10,
                        region="us-en",
                        safesearch="moderate",
                        backend="auto",
                    )
                )

                # Look for LinkedIn profiles
                for result in results:
                    url = result.get("href", "")
                    if "linkedin.com/in/" in url.lower() and not any(
                        exclude in url.lower()
                        for exclude in [
                            "/search",
                            "/company",
                            "/groups",
                            "/jobs",
                            "/feed",
                        ]
                    ):
                        logger.info(f"✅ Found profile: {url}")
                        return SearchResult(
                            success=True,
                            profile_url=url,
                            title=result.get("title", ""),
                            query_used=query,
                            strategy=i,
                        )

            except Exception as e:
                logger.warning(f"Strategy {i} failed for {name}: {e}")
                continue

        logger.warning(f"❌ No LinkedIn profile found for {name}")
        return SearchResult(
            success=False,
            error="No LinkedIn profiles found with any strategy",
        )

    def search_simple(self, query: str) -> SearchResult:
        """
        Simple search using a single query string

        Args:
            query: Search query (e.g., "John Smith Microsoft")

        Returns:
            SearchResult object with success status and profile URL if found
        """
        # Parse the query to extract name and company
        parts = query.strip().split()
        if len(parts) < 2:
            return SearchResult(
                success=False, error="Query must contain at least a name and company"
            )

        # Assume first part(s) are name, last part(s) are company
        # This is a simple heuristic - could be improved
        if len(parts) == 2:
            name, company = parts
        else:
            # Try to split intelligently
            name = " ".join(parts[:-1])  # Everything except last word
            company = parts[-1]  # Last word as company

        return self.search_profile(name, company)

    def search_multiple(
        self, searches: List[Dict[str, str]], max_workers: int = 3
    ) -> List[SearchResult]:
        """
        Search for multiple LinkedIn profiles in parallel

        Args:
            searches: List of dicts with 'name', 'company', 'job_title' keys
            max_workers: Number of parallel workers

        Returns:
            List of SearchResult objects
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading

        results = [None] * len(searches)
        lock = threading.Lock()

        def process_search(idx: int, search_data: Dict[str, str]) -> None:
            try:
                ddgs_instance = DDGS()  # Create new instance for thread
                finder = LinkedInFinder(self.delay_between_requests)
                finder.ddgs = ddgs_instance

                result = finder.search_profile(
                    search_data.get("name", ""),
                    search_data.get("company", ""),
                    search_data.get("job_title", ""),
                )

                with lock:
                    results[idx] = result

            except Exception as e:
                with lock:
                    results[idx] = SearchResult(
                        success=False, error=f"Error processing search: {e}"
                    )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_search, i, search_data)
                for i, search_data in enumerate(searches)
            ]

            for future in as_completed(futures):
                future.result()  # Wait for completion

        return results


# Convenience functions for common use cases
def find_linkedin_profile(
    name: str, company: str = "", job_title: str = ""
) -> Optional[str]:
    """
    Simple function to find a LinkedIn profile URL

    Args:
        name: Person's name
        company: Company name (optional)
        job_title: Job title (optional)

    Returns:
        LinkedIn profile URL if found, None otherwise
    """
    finder = LinkedInFinder()
    result = finder.search_profile(name, company, job_title)
    return result.profile_url if result.success else None


def find_linkedin_profile_simple(query: str) -> Optional[str]:
    """
    Simple function to find a LinkedIn profile using a query string

    Args:
        query: Search query (e.g., "John Smith Microsoft")

    Returns:
        LinkedIn profile URL if found, None otherwise
    """
    finder = LinkedInFinder()
    result = finder.search_simple(query)
    return result.profile_url if result.success else None
