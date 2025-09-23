# LinkedIn Finder

A powerful Python package to find LinkedIn profiles and extract rich profile information using search queries. Perfect for lead generation, recruitment, and professional networking when you know someone's name and company. Features smart company validation to ensure profile accuracy and comprehensive data extraction including job titles, locations, and bio information.

## Features

- 🔍 **Simple API**: Just provide a name and company to find LinkedIn profiles
- 🚀 **Multiple Search Strategies**: Uses various search approaches for better results
- 📊 **Rich Profile Information**: Extracts job titles, company names, locations, connections, and bio descriptions
- 🎯 **Smart Validation**: Dual validation system - both name and company matching to ensure high accuracy
- 🔒 **Name Validation**: Fuzzy matching validates that found profiles actually belong to the searched person
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

### Using the Finder Class (Enhanced with Rich Profile Data)

```python
from linkedin_finder import LinkedInFinder

# Initialize with company validation (default threshold: 0.6)
finder = LinkedInFinder(company_similarity_threshold=0.6)

# Search with name and company
result = finder.search_profile("Satya Nadella", "Microsoft")
if result.success:
    print(f"Found: {result.profile_url}")
    print(f"Job Title: {result.job_title_extracted}")
    print(f"Company: {result.company_extracted}")
    print(f"Location: {result.location}")
    print(f"Connections: {result.connections}")
    print(f"Bio: {result.description[:100]}...")
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
LinkedInFinder(
    delay_between_requests: float = 1.0,
    company_similarity_threshold: float = 0.6,
    name_similarity_threshold: float = 0.7
)
```

- `delay_between_requests`: Delay between search requests in seconds (default: 1.0)
- `company_similarity_threshold`: Minimum similarity score (0.0-1.0) for company matching (default: 0.6). Set to 0.0 to disable company validation
- `name_similarity_threshold`: Minimum similarity score (0.0-1.0) for name matching (default: 0.7). Validates that found profiles match the searched person's name to reduce false positives. Set to 0.0 to disable name validation

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

Result object containing search results and extracted profile information.

#### Attributes

- `success: bool` - Whether the search was successful
- `profile_url: Optional[str]` - LinkedIn profile URL if found
- `title: Optional[str]` - Profile title from search results
- `description: Optional[str]` - Full profile description/bio from search results
- `job_title_extracted: Optional[str]` - Extracted job title (e.g., "CEO", "Software Engineer")
- `location: Optional[str]` - Geographic location (e.g., "San Francisco", "New York")
- `connections: Optional[str]` - Connection count (e.g., "500+ connections")
- `company_extracted: Optional[str]` - Extracted company name
- `name_extracted: Optional[str]` - Extracted person name from profile (used for validation)
- `query_used: Optional[str]` - The search query that worked
- `strategy: Optional[int]` - Which search strategy succeeded
- `error: Optional[str]` - Error message if search failed

### Convenience Functions

#### `find_linkedin_profile(name: str, company: str = "", job_title: str = "") -> Optional[str]`

Simple function that returns just the profile URL or None.

#### `find_linkedin_profile_simple(query: str) -> Optional[str]`

Simple function for query-based search that returns just the profile URL or None.

## Examples

### Basic Usage with Rich Profile Data

```python
from linkedin_finder import LinkedInFinder

# Initialize with company validation
finder = LinkedInFinder(company_similarity_threshold=0.6)

# Search for someone
result = finder.search_profile("Satya Nadella", "Microsoft")
if result.success:
    print(f"Found: {result.profile_url}")
    print(f"Job Title: {result.job_title_extracted}")
    print(f"Company: {result.company_extracted}")
    print(f"Location: {result.location}")
    print(f"Connections: {result.connections}")
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

### Company Validation

The package includes smart company validation to ensure profile accuracy:

```python
# Strict company matching (default: 0.6)
finder = LinkedInFinder(company_similarity_threshold=0.8)

# Moderate company matching
finder = LinkedInFinder(company_similarity_threshold=0.4)

# Disable company validation
finder = LinkedInFinder(company_similarity_threshold=0.0)
```

**How Company Validation Works:**
- When you specify a company, the system validates that found profiles actually work at that company
- Profiles without clear company information are rejected when company validation is enabled
- This prevents returning wrong people with the same name but different employers
- Company names are normalized (removes "Inc.", "LLC", etc.) for better matching

**Example:**
```python
# This will reject profiles that don't clearly show "Apple" as the company
result = finder.search_profile("Tim Cook", "Apple")
if not result.success:
    print("No Apple employee named Tim Cook found")
    # This is better than returning a random Tim Cook!
```

### Rate Limiting

The package includes built-in rate limiting to be respectful to search engines. You can adjust the delay:

```python
finder = LinkedInFinder(delay_between_requests=2.0)  # 2 second delay
```

### Logging

Enable verbose logging to see search progress and company validation:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Use DEBUG to see company matching

finder = LinkedInFinder()
result = finder.search_profile("John Smith", "Microsoft")
```

## Rich Profile Information

The package extracts comprehensive profile information from search results:

### Available Profile Data

- **Job Title**: Current position (e.g., "CEO", "Software Engineer", "Marketing Director")
- **Company**: Current employer with smart normalization
- **Location**: Geographic location (city/region)
- **Connections**: Network size (e.g., "500+ connections")
- **Bio/Description**: Profile summary and mission statements
- **Profile URL**: Direct link to LinkedIn profile

### Example Output

```python
result = finder.search_profile("Satya Nadella", "Microsoft")
if result.success:
    print(f"URL: {result.profile_url}")
    print(f"Job Title: {result.job_title_extracted}")        # "Chairman and CEO"
    print(f"Company: {result.company_extracted}")            # "Microsoft"
    print(f"Location: {result.location}")                    # "Redmond"
    print(f"Connections: {result.connections}")              # "500+ connections"
    print(f"Bio: {result.description[:100]}...")             # "As chairman and CEO of Microsoft..."
```

### Information Extraction Process

1. **Search Results Analysis**: Parses title and description from search engines
2. **Pattern Recognition**: Uses regex patterns to identify job titles, companies, locations
3. **Data Normalization**: Cleans and standardizes extracted information
4. **Validation**: Ensures extracted data meets quality standards

## Dependencies

- `ddgs>=3.0.0` - DuckDuckGo search library for web searches
- `tqdm` - Progress bars for batch operations
- `difflib` - Built-in Python library for company name similarity matching

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
