#!/usr/bin/env python3
"""
Command line interface for LinkedIn Finder

⚠️ LEGAL DISCLAIMER:
This tool is for educational and legitimate business purposes only.
Users must comply with LinkedIn's Terms of Service and all applicable laws.
"""

import argparse
import sys
from typing import Optional
from .finder import LinkedInFinder, find_linkedin_profile_simple


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Find LinkedIn profiles using search queries"
    )

    parser.add_argument(
        "query", help="Search query (e.g., 'John Smith Microsoft' or 'Jane Doe')"
    )

    parser.add_argument("--company", help="Company name (if not included in query)")

    parser.add_argument("--job-title", help="Job title (optional)")

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0, minimum 1.0 for compliance)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        import logging

        logging.getLogger().setLevel(logging.INFO)

    # Create finder instance
    finder = LinkedInFinder(delay_between_requests=args.delay)

    # Search for profile
    if args.company or args.job_title:
        # Use structured search
        result = finder.search_profile(
            name=args.query, company=args.company or "", job_title=args.job_title or ""
        )
    else:
        # Use simple search
        result = finder.search_simple(args.query)

    # Output result
    if result.success:
        print(result.profile_url)
        sys.exit(0)
    else:
        print(f"Error: {result.error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
