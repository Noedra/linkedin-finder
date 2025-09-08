"""
LinkedIn Profile Finder

A simple Python package to find LinkedIn profiles using search queries.
"""

from .finder import (
    LinkedInFinder,
    SearchResult,
    find_linkedin_profile,
    find_linkedin_profile_simple,
)

__version__ = "1.0.0"
__author__ = "AI Assistant"
__all__ = [
    "LinkedInFinder",
    "SearchResult",
    "find_linkedin_profile",
    "find_linkedin_profile_simple",
]
