# LinkedIn Finder

A simple Python package to find LinkedIn profiles using search queries. Perfect for quickly finding someone's LinkedIn profile when you know their name and company.

## Features

- 🔍 **Simple API**: Just provide a name and company to find LinkedIn profiles
- 🚀 **Multiple Search Strategies**: Uses various search approaches for better results
- ⚡ **Fast**: Optimized search queries and result parsing
- 🛡️ **Respectful**: Built-in rate limiting to be respectful to search engines
- 📦 **Lightweight**: Minimal dependencies, easy to install and use

## Installation

```bash
pip install linkedin-finder
```

Or install from source:

```bash
git clone <repository-url>
cd linkedin-finder
pip install -e .
```

## Quick Start

### Simple Usage

```python
from linkedin_finder import find_linkedin_profile

# Find a LinkedIn profile
profile_url = find_linkedin_profile("John Smith", "Microsoft")
print(profile_url)  # https://www.linkedin.com/in/johnsmith123
```

### Using the Finder Class

```python
from linkedin_finder import LinkedInFinder

finder = LinkedInFinder()

# Search with name and company
result = finder.search_profile("Jane Doe", "Google")
if result.success:
    print(f"Found: {result.profile_url}")
    print(f"Title: {result.title}")
else:
    print(f"Not found: {result.error}")
```

### Simple Query Search

```python
from linkedin_finder import find_linkedin_profile_simple

# Search using a simple query string
profile_url = find_linkedin_profile_simple("John Smith Microsoft")
print(profile_url)
```

### Command Line Usage

```bash
# Simple search
linkedin-finder "John Smith Microsoft"

# With separate company
linkedin-finder "John Smith" --company "Microsoft"

# With job title
linkedin-finder "John Smith" --company "Microsoft" --job-title "Software Engineer"

# Verbose output
linkedin-finder "John Smith Microsoft" --verbose
```

## API Reference

### `LinkedInFinder`

Main class for finding LinkedIn profiles.

#### Constructor

```python
LinkedInFinder(delay_between_requests: float = 1.0)
```

- `delay_between_requests`: Delay between search requests in seconds (default: 1.0)

#### Methods

##### `search_profile(name: str, company: str = "", job_title: str = "") -> SearchResult`

Search for a LinkedIn profile using structured data.

- `name`: Person's name (required)
- `company`: Company name (optional)
- `job_title`: Job title (optional)

Returns a `SearchResult` object.

##### `search_simple(query: str) -> SearchResult`

Search using a simple query string (e.g., "John Smith Microsoft").

- `query`: Search query string

Returns a `SearchResult` object.

##### `search_multiple(searches: List[Dict], max_workers: int = 3) -> List[SearchResult]`

Search for multiple profiles in parallel.

- `searches`: List of dictionaries with 'name', 'company', 'job_title' keys
- `max_workers`: Number of parallel workers

Returns a list of `SearchResult` objects.

### `SearchResult`

Result object containing search results.

#### Attributes

- `success: bool` - Whether the search was successful
- `profile_url: Optional[str]` - LinkedIn profile URL if found
- `title: Optional[str]` - Profile title from search results
- `query_used: Optional[str]` - The search query that worked
- `strategy: Optional[int]` - Which search strategy succeeded
- `error: Optional[str]` - Error message if search failed

### Convenience Functions

#### `find_linkedin_profile(name: str, company: str = "", job_title: str = "") -> Optional[str]`

Simple function that returns just the profile URL or None.

#### `find_linkedin_profile_simple(query: str) -> Optional[str]`

Simple function for query-based search that returns just the profile URL or None.

## Examples

### Basic Usage

```python
from linkedin_finder import LinkedInFinder

finder = LinkedInFinder()

# Search for someone
result = finder.search_profile("Satya Nadella", "Microsoft")
if result.success:
    print(f"Found: {result.profile_url}")
else:
    print("Profile not found")
```

### Batch Processing

```python
from linkedin_finder import LinkedInFinder

finder = LinkedInFinder()

# Search for multiple people
searches = [
    {"name": "John Smith", "company": "Microsoft"},
    {"name": "Jane Doe", "company": "Google"},
    {"name": "Bob Johnson", "company": "Apple"},
]

results = finder.search_multiple(searches, max_workers=3)

for i, result in enumerate(results):
    if result.success:
        print(f"Found {searches[i]['name']}: {result.profile_url}")
    else:
        print(f"Not found: {searches[i]['name']}")
```

### Command Line Examples

```bash
# Find a specific person
linkedin-finder "Elon Musk Tesla"

# Find with separate parameters
linkedin-finder "Tim Cook" --company "Apple"

# Find with job title
linkedin-finder "Sundar Pichai" --company "Google" --job-title "CEO"

# Use in scripts
PROFILE=$(linkedin-finder "John Smith Microsoft")
echo "Found profile: $PROFILE"
```

## Configuration

### Rate Limiting

The package includes built-in rate limiting to be respectful to search engines. You can adjust the delay:

```python
finder = LinkedInFinder(delay_between_requests=2.0)  # 2 second delay
```

### Logging

Enable verbose logging to see search progress:

```python
import logging
logging.basicConfig(level=logging.INFO)

finder = LinkedInFinder()
result = finder.search_profile("John Smith", "Microsoft")
```

## Dependencies

- `ddgs>=3.0.0` - DuckDuckGo search library

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Legal Disclaimer & LinkedIn Compliance

**IMPORTANT: This tool is for educational and legitimate business purposes only.**

### LinkedIn Terms of Service Compliance

This package is designed to be compliant with LinkedIn's Terms of Service by:

- ✅ **Using public search engines** (Google, Bing, etc.) instead of scraping LinkedIn directly
- ✅ **Respecting rate limits** with built-in delays between requests
- ✅ **Only accessing publicly available information** through search results
- ✅ **No automated data collection** from LinkedIn's website
- ✅ **No circumvention of LinkedIn's technical measures**

### User Responsibilities

Users of this tool are responsible for:

- 🔒 **Complying with LinkedIn's Terms of Service** and all applicable laws
- 🚫 **Not using this tool for spam, harassment, or unauthorized data collection**
- ⏱️ **Respecting rate limits** and not overloading search engines
- 📋 **Obtaining proper permissions** before collecting personal information
- 🎯 **Using the tool ethically** for legitimate business purposes only

### What This Tool Does NOT Do

- ❌ Does not scrape LinkedIn's website directly
- ❌ Does not bypass LinkedIn's technical protections
- ❌ Does not collect data in violation of LinkedIn's ToS
- ❌ Does not perform automated actions on LinkedIn

### What This Tool Does

- ✅ Uses public search engines to find LinkedIn profile URLs
- ✅ Provides publicly available profile links
- ✅ Helps with legitimate networking and business development
- ✅ Respects search engine rate limits

### Legal Notice

**The authors and contributors of this software are not responsible for any misuse of this tool.** Users must ensure their use complies with all applicable laws, regulations, and terms of service. This tool is provided "as is" without warranty of any kind.

**If you use this tool, you agree to use it responsibly and in compliance with all applicable terms of service and laws.**
