# Healthcare MCP Server

A Model Context Protocol (MCP) server providing AI assistants with access to healthcare data and medical information tools.

## Overview

Healthcare MCP Server is a specialized server that implements the Model Context Protocol (MCP) to provide AI assistants with access to healthcare data and medical information tools. It enables AI models to retrieve accurate, up-to-date medical information from authoritative sources.

## Features

- **FDA Drug Information**: Search and retrieve comprehensive drug information from the FDA database
- **PubMed Research**: Search medical literature from PubMed's database of scientific articles
- **Health Topics**: Access evidence-based health information from Health.gov
- **Clinical Trials**: Search for ongoing and completed clinical trials
- **Medical Terminology**: Look up ICD-10 codes and medical terminology definitions
- **Caching**: Efficient caching system with connection pooling to reduce API calls and improve performance
- **Usage Tracking**: Anonymous usage tracking to monitor API usage
- **Error Handling**: Robust error handling and logging
- **Multiple Interfaces**: Support for both stdio (for CLI) and HTTP/SSE interfaces
- **API Documentation**: Interactive API documentation with Swagger UI
- **Comprehensive Testing**: Extensive test suite with pytest and coverage reporting

## Installation

### Quick Install (Cline Marketplace)

The easiest way to install this server is through the Cline Marketplace:

1. Open Cline and click the Extensions button in the toolbar
2. Search for "Healthcare MCP"
3. Click Install

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Cicatriiz/healthcare-mcp-public.git
   cd healthcare-mcp-public
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional):
   ```bash
   # Create .env file from example
   cp .env.example .env
   # Edit .env with your API keys (optional)
   ```

5. Run the server:
   ```bash
   python run.py
   ```

## Usage

### Running in Different Transport Modes

- **stdio mode** (default, for Cline):
  ```bash
  python run.py
  ```

- **HTTP/SSE mode** (for web clients):
  ```bash
  python run.py --http --port 8000
  ```

### Testing the Tools

You can test the MCP tools using the new pytest-based test suite:

```bash
# Run all tests with pytest and coverage
python -m tests.run_tests --pytest

# Run a specific test file
python -m tests.run_tests --test test_fda_tool.py

# Test the HTTP server
python -m tests.run_tests --server --port 8000
```

For backward compatibility, you can still run the old tests:

```bash
# Run all tests (old style)
python -m tests.run_tests

# Test individual tools (old style)
python -m tests.run_tests --fda        # Test FDA drug lookup
python -m tests.run_tests --pubmed     # Test PubMed search
python -m tests.run_tests --health     # Test Health Topics
python -m tests.run_tests --trials     # Test Clinical Trials search
python -m tests.run_tests --icd        # Test ICD-10 code lookup
```

## API Reference

### FDA Drug Lookup

```
fda_drug_lookup(drug_name: str, search_type: str = "general")
```

**Parameters:**
- `drug_name`: Name of the drug to search for
- `search_type`: Type of information to retrieve
  - `general`: Basic drug information (default)
  - `label`: Drug labeling information
  - `adverse_events`: Reported adverse events

### PubMed Search

```
pubmed_search(query: str, max_results: int = 5, date_range: str = "")
```

**Parameters:**
- `query`: Search query for medical literature
- `max_results`: Maximum number of results to return (default: 5)
- `date_range`: Limit to articles published within years (e.g. '5' for last 5 years)

### Health Topics

```
health_topics(topic: str, language: str = "en")
```

**Parameters:**
- `topic`: Health topic to search for information
- `language`: Language for content (en or es, default: en)

### Clinical Trials Search

```
clinical_trials_search(condition: str, status: str = "recruiting", max_results: int = 10)
```

**Parameters:**
- `condition`: Medical condition or disease to search for
- `status`: Trial status (recruiting, completed, active, not_recruiting, or all)
- `max_results`: Maximum number of results to return

### ICD-10 Code Lookup

```
lookup_icd_code(code: str = None, description: str = None, max_results: int = 10)
```

**Parameters:**
- `code`: ICD-10 code to look up (optional if description is provided)
- `description`: Medical condition description to search for (optional if code is provided)
- `max_results`: Maximum number of results to return

## Data Sources

This MCP server utilizes several publicly available healthcare APIs:

- [FDA OpenFDA API](https://open.fda.gov/apis/)
- [PubMed E-utilities API](https://www.ncbi.nlm.nih.gov/books/NBK25500/)
- [Health.gov API](https://health.gov/our-work/national-health-initiatives/health-literacy/consumer-health-content/free-web-content/apis-developers)
- [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/about-api)
- [NLM Clinical Table Search Service for ICD-10-CM](https://clinicaltables.nlm.nih.gov/apidoc/icd10cm/v3/doc.html)

## Premium Version

This is the free version of Healthcare MCP Server with usage limits. For advanced features and higher usage limits, check out our premium version:

- **Unlimited API calls**
- **Advanced healthcare data tools**
- **Custom integrations**
- **Priority support**

Visit [healthcaremcp.com](https://healthcaremcp.com) to learn more and sign up for a premium account.

## License

MIT License
