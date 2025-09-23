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
from tqdm import tqdm
from difflib import SequenceMatcher

# Set up logging
logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result of a LinkedIn profile search"""

    success: bool
    profile_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    job_title_extracted: Optional[str] = None
    location: Optional[str] = None
    connections: Optional[str] = None
    company_extracted: Optional[str] = None
    name_extracted: Optional[str] = None
    query_used: Optional[str] = None
    strategy: Optional[int] = None
    error: Optional[str] = None


class LinkedInFinder:
    """Find LinkedIn profiles using optimized DDGS search with name and company validation"""

    def __init__(
        self,
        delay_between_requests: float = 1.0,
        company_similarity_threshold: float = 0.6,
        name_similarity_threshold: float = 0.7,
    ):
        """
        Initialize the LinkedIn finder

        Args:
            delay_between_requests: Delay between search requests in seconds
                                   (minimum 1.0 recommended for compliance)
            company_similarity_threshold: Minimum similarity score (0.0-1.0) for company matching
                                        Set to 0.0 to disable company validation (default: 0.6)
            name_similarity_threshold: Minimum similarity score (0.0-1.0) for name matching
                                     Validates that found profiles match the searched person's name
                                     to reduce false positives. Set to 0.0 to disable name validation
                                     (default: 0.7 - optimized for best precision/recall balance)
        """
        # Ensure minimum delay for compliance
        self.delay_between_requests = max(delay_between_requests, 1.0)
        self.company_similarity_threshold = company_similarity_threshold
        self.name_similarity_threshold = name_similarity_threshold
        self.ddgs = DDGS()

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

    def parse_profile_info(self, title: str, body: str) -> Dict[str, Optional[str]]:
        """
        Parse additional profile information from search result title and body

        Args:
            title: The title from search results
            body: The body/description from search results

        Returns:
            Dictionary with extracted information
        """
        info = {
            "job_title_extracted": None,
            "location": None,
            "connections": None,
            "company_extracted": None,
            "name_extracted": None,
            "description": body,
        }

        # Extract name from title first
        info["name_extracted"] = self.extract_name_from_title(title)

        if not body:
            return info

        # Extract job title from title (e.g., "John Smith - CEO at Microsoft | LinkedIn")
        title_match = re.search(r" - ([^|]+) \| LinkedIn", title, re.IGNORECASE)
        if title_match:
            job_company = title_match.group(1).strip()
            # Try to split job title and company (e.g., "CEO at Microsoft")
            at_match = re.search(r"^(.+?)\s+at\s+(.+)$", job_company, re.IGNORECASE)
            if at_match:
                info["job_title_extracted"] = at_match.group(1).strip()
                info["company_extracted"] = at_match.group(2).strip()
            else:
                # Check if the whole thing might be a company name
                # (e.g., "Microsoft" or "Apple Inc.")
                if len(job_company.split()) <= 3 and not any(
                    title_word in job_company.lower()
                    for title_word in [
                        "ceo",
                        "cto",
                        "cfo",
                        "president",
                        "director",
                        "manager",
                        "engineer",
                        "developer",
                        "analyst",
                    ]
                ):
                    info["company_extracted"] = job_company
                else:
                    info["job_title_extracted"] = job_company

        # Extract location (e.g., "Location: Redmond", "Location: Mountain View")
        location_match = re.search(r"Location:\s*([^·•\n]+)", body, re.IGNORECASE)
        if location_match:
            info["location"] = location_match.group(1).strip()

        # Extract connections (e.g., "500+ connections", "1 connection")
        connections_match = re.search(r"(\d+\+?\s+connections?)", body, re.IGNORECASE)
        if connections_match:
            info["connections"] = connections_match.group(1).strip()

        # If we didn't get company from title, try to extract from body
        if not info["company_extracted"]:
            # Look for "Experience: CompanyName" or "at CompanyName"
            exp_match = re.search(r"Experience:\s*([^·•\n]+)", body, re.IGNORECASE)
            if exp_match:
                info["company_extracted"] = exp_match.group(1).strip()
            else:
                # Look for "at [Company]" pattern in the body
                at_match = re.search(r"\bat\s+([A-Z][^·•\n,]+)", body)
                if at_match:
                    info["company_extracted"] = at_match.group(1).strip()

        return info

    def calculate_company_similarity(self, company1: str, company2: str) -> float:
        """
        Calculate similarity between two company names

        Args:
            company1: First company name
            company2: Second company name

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not company1 or not company2:
            return 0.0

        # Normalize company names for comparison
        def normalize_company(company: str) -> str:
            # Convert to lowercase and remove common suffixes
            company = company.lower().strip()
            company = re.sub(
                r"\b(inc\.?|llc|corp\.?|corporation|company|ltd\.?|limited|co\.?)\b",
                "",
                company,
            ).strip()
            # Remove extra whitespace
            company = re.sub(r"\s+", " ", company)
            return company

        norm1 = normalize_company(company1)
        norm2 = normalize_company(company2)

        # Use SequenceMatcher for similarity
        similarity = SequenceMatcher(None, norm1, norm2).ratio()

        # Boost score if one company name is contained in the other
        if norm1 in norm2 or norm2 in norm1:
            similarity = max(similarity, 0.8)

        return similarity

    def is_company_match(self, expected_company: str, found_company: str) -> bool:
        """
        Check if the found company matches the expected company

        Args:
            expected_company: The company we're searching for
            found_company: The company found in the search result

        Returns:
            True if companies match above threshold, False otherwise
        """
        if not expected_company or self.company_similarity_threshold <= 0.0:
            return True  # Skip validation if no expected company or threshold is 0

        if not found_company:
            return False

        similarity = self.calculate_company_similarity(expected_company, found_company)
        logger.debug(
            f"Company similarity: '{expected_company}' vs '{found_company}' = {similarity:.2f}"
        )

        return similarity >= self.company_similarity_threshold

    def normalize_name_for_matching(self, name: str) -> str:
        """
        Normalize a name for fuzzy matching comparison

        This function handles various name formats and variations to enable better matching.
        """
        if not name:
            return ""

        # Start with basic cleaning
        normalized = self.clean_name(name).lower()

        # Remove common punctuation that might appear in names
        normalized = re.sub(r"[.,;:()\"']", " ", normalized)

        # Handle common name variations and contractions
        name_replacements = {
            r"\bmike\b": "michael",
            r"\bmatt\b": "matthew",
            r"\btom\b": "thomas",
            r"\bbob\b": "robert",
            r"\bbill\b": "william",
            r"\bdick\b": "richard",
            r"\bjim\b": "james",
            r"\bdan\b": "daniel",
            r"\bdave\b": "david",
            r"\bchris\b": "christopher",
            r"\bsteve\b": "steven",
            r"\bken\b": "kenneth",
            r"\brich\b": "richard",
            r"\bron\b": "ronald",
            r"\btony\b": "anthony",
            r"\bjoe\b": "joseph",
            r"\bpat\b": "patrick",
            r"\bamy\b": "amelia",
            r"\bliz\b": "elizabeth",
            r"\bkate\b": "katherine",
            r"\bsue\b": "susan",
            r"\bnan\b": "nancy",
            r"\bbeth\b": "elizabeth",
        }

        for pattern, replacement in name_replacements.items():
            normalized = re.sub(pattern, replacement, normalized)

        # Normalize multiple spaces to single spaces
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    def extract_name_from_title(self, title: str) -> str:
        """
        Extract the person's name from a LinkedIn search result title

        LinkedIn titles typically follow formats like:
        - "John Smith - CEO at Microsoft | LinkedIn"
        - "John Smith | LinkedIn"
        - "John Smith, PhD - Research Scientist | LinkedIn"
        """
        if not title:
            return ""

        # Remove " | LinkedIn" suffix if present
        title = re.sub(r"\s*\|\s*linkedin\s*$", "", title, flags=re.IGNORECASE).strip()

        # Extract name before first " - " (job title separator)
        name_match = re.match(r"^([^-]+?)(?:\s*-\s*.+)?$", title)
        if name_match:
            name = name_match.group(1).strip()

            # Remove common suffixes that might be part of the name
            name = re.sub(
                r",?\s*(PhD|MD|MBA|MS|BS|BA|Jr\.?|Sr\.?)$",
                "",
                name,
                flags=re.IGNORECASE,
            )

            return name.strip()

        return title.strip()

    def calculate_name_similarity(self, expected_name: str, found_name: str) -> float:
        """
        Calculate similarity between expected name and found name using multiple approaches
        """
        if not expected_name or not found_name:
            return 0.0

        # Normalize both names
        norm_expected = self.normalize_name_for_matching(expected_name)
        norm_found = self.normalize_name_for_matching(found_name)

        if not norm_expected or not norm_found:
            return 0.0

        # Exact match after normalization
        if norm_expected == norm_found:
            return 1.0

        # Split into parts for more flexible matching
        expected_parts = norm_expected.split()
        found_parts = norm_found.split()

        # Check for exact subset matches (handles middle names, initials, etc.)
        if len(expected_parts) >= 2 and len(found_parts) >= 2:
            # Both first and last names must match (order flexible)
            expected_set = set(expected_parts)
            found_set = set(found_parts)

            # Check if all expected parts are found (allows for additional middle names)
            if expected_set.issubset(found_set):
                return 0.95

            # Check if all found parts are in expected (handles when found name is shorter)
            if found_set.issubset(expected_set):
                return 0.95

            # Check if first and last names match (most important parts)
            if (
                expected_parts[0] == found_parts[0]
                and expected_parts[-1] == found_parts[-1]
            ):
                return 0.9

            # Check if last names match and first names are similar (handles nicknames)
            if expected_parts[-1] == found_parts[-1]:
                first_similarity = SequenceMatcher(
                    None, expected_parts[0], found_parts[0]
                ).ratio()
                if first_similarity >= 0.8:
                    return 0.85

        # Overall string similarity as fallback
        overall_similarity = SequenceMatcher(None, norm_expected, norm_found).ratio()

        # Boost if names are very similar (likely same person)
        if overall_similarity >= 0.85:
            return overall_similarity

        # Check for initials matching (e.g., "J. Smith" vs "John Smith")
        if len(expected_parts) >= 2 and len(found_parts) >= 2:
            # Check if one name uses initials
            expected_initials = "".join([part[0] for part in expected_parts if part])
            found_initials = "".join([part[0] for part in found_parts if part])

            # If initials match and at least last name matches
            if (
                expected_initials == found_initials
                and expected_parts[-1] == found_parts[-1]
            ):
                return 0.8

        return overall_similarity

    def is_name_match(self, expected_name: str, found_name: str) -> bool:
        """
        Check if the found name matches the expected name

        Args:
            expected_name: The name we're searching for
            found_name: The name found in the search result

        Returns:
            True if names match above threshold, False otherwise
        """
        if not expected_name or self.name_similarity_threshold <= 0.0:
            return True  # Skip validation if no expected name or threshold is 0

        if not found_name:
            return False

        similarity = self.calculate_name_similarity(expected_name, found_name)
        logger.debug(
            f"Name similarity: '{expected_name}' vs '{found_name}' = {similarity:.2f}"
        )

        return similarity >= self.name_similarity_threshold

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
        logger.debug(f"Searching for: {name}" + (f" at {company}" if company else ""))

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

                # Look for LinkedIn profiles and validate company match
                valid_profiles = []

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
                        # Extract additional information from search results
                        title = result.get("title", "")
                        body = result.get("body", "")
                        parsed_info = self.parse_profile_info(title, body)

                        # Validate name match first (always check if name validation is enabled)
                        name_valid = True
                        if self.name_similarity_threshold > 0.0:
                            if parsed_info["name_extracted"]:
                                name_valid = self.is_name_match(
                                    name, parsed_info["name_extracted"]
                                )
                                if not name_valid:
                                    logger.debug(
                                        f"❌ Name mismatch for {url}: expected '{name}', found '{parsed_info['name_extracted']}'"
                                    )
                                    continue
                            else:
                                # No name found in result - reject this profile when name validation is enabled
                                logger.debug(
                                    f"❌ Profile rejected - no name extracted: {url} (expected name: '{name}')"
                                )
                                continue

                        # Validate company match if we have an expected company
                        company_valid = True
                        if company:  # We have an expected company to validate against
                            if parsed_info["company_extracted"]:
                                # We found a company in the result, check if it matches
                                company_valid = self.is_company_match(
                                    company, parsed_info["company_extracted"]
                                )
                                if not company_valid:
                                    logger.debug(
                                        f"❌ Company mismatch for {url}: expected '{company}', found '{parsed_info['company_extracted']}'"
                                    )
                                    continue
                            else:
                                # No company found in result - reject this profile when we expect a company
                                # This ensures we don't return wrong profiles when company validation is important
                                logger.debug(
                                    f"❌ Profile rejected - no company extracted: {url} (expected company: '{company}')"
                                )
                                continue

                        # If we get here, both name and company validations passed
                        validation_info = []
                        if (
                            self.name_similarity_threshold > 0.0
                            and parsed_info["name_extracted"]
                        ):
                            validation_info.append(
                                f"Name: {parsed_info['name_extracted']}"
                            )
                        if company and parsed_info["company_extracted"]:
                            validation_info.append(
                                f"Company: {parsed_info['company_extracted']}"
                            )

                        validation_str = (
                            f" ({', '.join(validation_info)})"
                            if validation_info
                            else ""
                        )
                        logger.debug(
                            f"✅ Found matching profile: {url}{validation_str}"
                        )
                        valid_profiles.append((result, parsed_info))

                # Return the first valid profile
                if valid_profiles:
                    result, parsed_info = valid_profiles[0]
                    url = result.get("href", "")
                    title = result.get("title", "")

                    return SearchResult(
                        success=True,
                        profile_url=url,
                        title=title,
                        description=parsed_info["description"],
                        job_title_extracted=parsed_info["job_title_extracted"],
                        location=parsed_info["location"],
                        connections=parsed_info["connections"],
                        company_extracted=parsed_info["company_extracted"],
                        name_extracted=parsed_info["name_extracted"],
                        query_used=query,
                        strategy=i,
                    )

            except Exception as e:
                logger.debug(f"Strategy {i} failed for {name}: {e}")
                continue

        # Provide more specific error message
        validation_info = []
        if self.name_similarity_threshold > 0.0:
            validation_info.append(
                f"name validation (threshold: {self.name_similarity_threshold})"
            )
        if self.company_similarity_threshold > 0.0:
            validation_info.append(
                f"company validation (threshold: {self.company_similarity_threshold})"
            )

        validation_str = (
            f" with {' and '.join(validation_info)}" if validation_info else ""
        )

        if company:
            error_msg = f"No LinkedIn profiles found for {name} at {company}{validation_str}. This could mean: 1) The person doesn't have a LinkedIn profile, 2) The profile isn't indexed by search engines, 3) The name/company in their profile doesn't match the search criteria (profiles are validated for accuracy), or 4) Try adjusting the similarity thresholds or search terms"
        else:
            error_msg = f"No LinkedIn profiles found for {name}{validation_str}"

        logger.debug(f"❌ {error_msg}")
        return SearchResult(
            success=False,
            error=error_msg,
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
        completed_count = 0

        def process_search(idx: int, search_data: Dict[str, str], pbar: tqdm) -> None:
            nonlocal completed_count
            try:
                ddgs_instance = DDGS()  # Create new instance for thread
                finder = LinkedInFinder(
                    self.delay_between_requests,
                    self.company_similarity_threshold,
                    self.name_similarity_threshold,
                )
                finder.ddgs = ddgs_instance

                result = finder.search_profile(
                    search_data.get("name", ""),
                    search_data.get("company", ""),
                    search_data.get("job_title", ""),
                )

                with lock:
                    results[idx] = result
                    completed_count += 1
                    pbar.update(1)
                    # Update description with current search info
                    name = search_data.get("name", "Unknown")
                    company = search_data.get("company", "")
                    desc = f"Searching LinkedIn profiles - Current: {name}"
                    if company:
                        desc += f" at {company}"
                    pbar.set_description(desc)

            except Exception as e:
                with lock:
                    results[idx] = SearchResult(
                        success=False, error=f"Error processing search: {e}"
                    )
                    completed_count += 1
                    pbar.update(1)

        # Create progress bar
        with tqdm(
            total=len(searches), desc="Searching LinkedIn profiles", unit="profile"
        ) as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(process_search, i, search_data, pbar)
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
