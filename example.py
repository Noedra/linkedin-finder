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

    # Example 3: Using the Finder class with detailed results and company validation
    print(
        "3. Detailed search with Finder class (Enhanced with profile info and company validation):"
    )
    finder = LinkedInFinder(company_similarity_threshold=0.6)  # Strict company matching
    result = finder.search_profile("Satya Nadella", "Microsoft", "CEO")

    if result.success:
        print(f"   ✅ Success!")
        print(f"   Profile: {result.profile_url}")
        print(f"   Title: {result.title}")

        # New enhanced fields
        if result.job_title_extracted:
            print(f"   Job Title: {result.job_title_extracted}")
        if result.company_extracted:
            print(f"   Company: {result.company_extracted}")
        if result.location:
            print(f"   Location: {result.location}")
        if result.connections:
            print(f"   Connections: {result.connections}")
        if result.description:
            # Show first 100 chars of description
            desc_preview = (
                result.description[:100] + "..."
                if len(result.description) > 100
                else result.description
            )
            print(f"   Bio: {desc_preview}")

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

    # Example 5: Demonstrating strict company validation
    print(
        "5. Strict company validation (will reject profiles without matching company):"
    )
    result = finder.search_profile(
        "Tim Cook", "Apple"
    )  # Apple CEO likely doesn't have LinkedIn

    if result.success:
        print(f"   ✅ Found: {result.profile_url}")
        print(f"   Company: {result.company_extracted}")
    else:
        print(f"   ❌ Correctly rejected - no matching company found")
        print(f"   Reason: Profile validation ensures accuracy")
    print()

    # Example 6: Search without company constraint
    print("6. Same person without company constraint:")
    result_no_company = finder.search_profile("Tim Cook", "")  # No company validation

    if result_no_company.success:
        print(f"   ✅ Found: {result_no_company.profile_url}")
        print(f"   Company: {result_no_company.company_extracted or 'None extracted'}")
        print(f"   Note: This might be a different Tim Cook!")
    else:
        print(f"   ❌ Not found: {result_no_company.error}")
    print()

    print("=== Examples Complete ===")


if __name__ == "__main__":
    main()
