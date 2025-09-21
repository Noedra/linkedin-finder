#!/usr/bin/env python3
"""
Example usage of LinkedIn Finder package
"""

from linkedin_finder import (
    LinkedInFinder,
    find_linkedin_profile,
    find_linkedin_profile_simple,
)


def main():
    """Example usage"""
    print("=== LinkedIn Finder Examples ===\n")

    # Example 1: Simple function usage
    print("1. Simple function usage:")
    profile_url = find_linkedin_profile("John Smith", "Microsoft")
    if profile_url:
        print(f"   Found: {profile_url}")
    else:
        print("   Not found")
    print()

    # Example 2: Simple query search
    print("2. Simple query search:")
    profile_url = find_linkedin_profile_simple("Jane Doe Google")
    if profile_url:
        print(f"   Found: {profile_url}")
    else:
        print("   Not found")
    print()

    # Example 3: Using the Finder class with detailed results
    print("3. Detailed search with Finder class:")
    finder = LinkedInFinder()
    result = finder.search_profile("Satya Nadella", "Microsoft", "CEO")

    if result.success:
        print(f"   ✅ Success!")
        print(f"   Profile: {result.profile_url}")
        print(f"   Title: {result.title}")
        print(f"   Strategy: {result.strategy}")
        print(f"   Query used: {result.query_used}")
    else:
        print(f"   ❌ Failed: {result.error}")
    print()

    # Example 4: Multiple searches
    print("4. Multiple searches:")
    searches = [
        {"name": "John Smith", "company": "Microsoft"},
        {"name": "Jane Doe", "company": "Google"},
        {"name": "Bob Johnson", "company": "Apple"},
    ]

    results = finder.search_multiple(searches, max_workers=2)

    for i, result in enumerate(results):
        name = searches[i]["name"]
        company = searches[i]["company"]
        if result.success:
            print(f"   ✅ {name} at {company}: {result.profile_url}")
        else:
            print(f"   ❌ {name} at {company}: Not found")
    print()

    print("=== Examples Complete ===")


if __name__ == "__main__":
    main()


