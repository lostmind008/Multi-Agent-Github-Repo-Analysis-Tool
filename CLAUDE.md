# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Project:** Multi-Agent GitHub Repository Analysis Tool  
**Created by:** [LostMind AI](https://www.LostMindAI.com)

## Project Overview

This is a **Multi-Agent GitHub Analysis System** that uses LangGraph to orchestrate AI agents for comprehensive repository analysis. The system fetches GitHub repositories, analyzes them using multiple LLM providers, and generates detailed PDF reports.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys and tokens
```

### Running Analysis
```bash
# Analyze all repositories for a user
python main.py --user USERNAME

# Analyze specific repositories
python main.py --user USERNAME --repos repo1,repo2,repo3

# Custom output path
python main.py --user USERNAME --out custom_report.pdf

# Example with real usage
python main.py --user octocat --repos Hello-World --out octocat_analysis.pdf
```

### Testing and Development
```bash
# Run tests (when implemented)
python -m pytest

# Test with a small repository first
python main.py --user YOUR_USERNAME --repos small-test-repo

# Check report output
open reports/repo_report.pdf      # macOS
start reports/repo_report.pdf     # Windows
```

## System Architecture

### Multi-Agent Workflow
The system uses **LangGraph** to orchestrate a six-stage agent pipeline:

1. **Fetcher Agent** (`fetcher_node`)
   - Retrieves repository metadata and file contents via GitHub API
   - Handles both public and private repositories (with proper tokens)
   - Processes file contents and manages binary file detection

2. **Data Quality Reviewer** (`data_quality_reviewer_node`)
   - Validates repository access and data completeness
   - Checks file readability and metadata quality
   - Ensures data meets analysis requirements

3. **Analyzer Agent** (`analyzer_node`)
   - Analyzes each repository using configurable LLM providers
   - Creates vector embeddings for intelligent code search (when available)
   - Can integrate with Cloud Run services for additional insights
   - Generates detailed per-repository analysis reports

4. **Analysis Quality Reviewer** (`analysis_quality_reviewer_node`)
   - Reviews technical depth and accuracy of analyses
   - Validates completeness of technical assessment
   - Provides feedback on analysis quality

5. **Synthesizer Agent** (`synthesizer_node`)
   - Combines individual repository analyses into cohesive reports
   - Provides executive summaries and comparative insights
   - Generates final formatted output for PDF generation

6. **Final Quality Reviewer** (`final_quality_reviewer_node`)
   - Ensures report meets professional standards
   - Validates coherence and formatting
   - Provides final quality assessment

### LLM Provider Architecture
The system supports multiple LLM providers through a unified configuration:

```python
LLM_CONFIG = {
    "gpt4o": ChatOpenAI(model="gpt-4o"),
    "gemini2.5": ChatGoogleGenerativeAI(model="gemini-1.5-pro-exp-0801"),
    "claude3.5": ChatAnthropic(model="claude-3-5-sonnet-20240620"),
    "grok": get_grok_llm(),  # With fallback handling
}
```

**Default LLM**: Dynamically selected based on available API keys

### Vector Storage and Embeddings
- **Optional FAISS** vector store for efficient code similarity search
- **OpenAI Embeddings** for code semantic analysis (when available)
- Graceful fallback when vector storage dependencies unavailable
- Each repository's files become searchable document vectors

### Tool-Based Extensibility
Two primary tools enable system extensibility:

- `fetch_github_repos`: GitHub API integration with PyGithub
- `call_cloud_run`: Generic Cloud Run service integration

## Key Development Patterns

### Adding New LLM Providers
1. Install the provider's LangChain integration
2. Add configuration to `get_available_llms()` in `src/config.py`
3. Update `requirements.txt` with new dependencies
4. Add corresponding API key to `.env.example`

### Extending Agent Workflow
1. Define new node functions in `src/agents.py`
2. Add nodes to the graph in `src/workflow.py`
3. Update `AgentState` TypedDict if new state fields needed
4. Wire new nodes with appropriate edges

### Adding New Tools
1. Create `@tool` decorated functions in `src/tools.py`
2. Import and use tools in agent node functions
3. Follow LangChain tool patterns for proper integration
4. Add error handling for external API dependencies

### Configuration Management
- **Environment Variables**: All secrets in `.env` file
- **LLM Configuration**: Dynamic selection in `src/config.py`
- **Prompts**: Defined as `PromptTemplate` objects in `src/agents.py`
- **Tool Integration**: Environment-based URL and token configuration

## Project Structure

```
├── main.py                 # CLI entrypoint with validation
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .gitignore            # Git ignore patterns
├── CLAUDE.md             # This guidance file
└── src/
    ├── __init__.py       # Package initialization
    ├── config.py         # Dynamic LLM provider configuration
    ├── tools.py          # LangChain tools (GitHub, Cloud Run)
    ├── agents.py         # Agent nodes and quality reviewers
    ├── workflow.py       # LangGraph workflow with quality gates
    └── report.py         # Professional PDF generation
```

### Key Dependencies
- **LangChain**: LLM orchestration and tool integration
- **LangGraph**: Multi-agent workflow state management
- **PyGithub**: GitHub API client
- **ReportLab**: PDF report generation
- **OpenAI/Google/Anthropic SDKs**: LLM provider integrations
- **Optional**: FAISS (vector storage), tiktoken (tokenization)

## Integration Points

### GitHub API
- Requires `GITHUB_TOKEN` with appropriate repository access
- Handles both public and private repository analysis
- Manages file content extraction with binary file detection

### Cloud Run Services
- Optional integration via `CLOUD_RUN_URL` and `CLOUD_RUN_TOKEN`
- Generic POST endpoint calling for extended analysis
- Configurable per-analysis basis

### Vector Embeddings
- Optional OpenAI embeddings for code semantic analysis
- Optional FAISS vector store for efficient similarity search
- Graceful fallback when dependencies unavailable

## Error Handling Patterns
- **API Rate Limits**: Built into PyGithub client
- **LLM Failures**: Try-catch blocks around LLM calls with fallbacks
- **File Processing**: Binary file detection and graceful fallbacks
- **Cloud Integration**: Optional Cloud Run calls with exception handling
- **Dependency Management**: Graceful handling of optional dependencies

## Development Workflow
1. Set up environment and install dependencies
2. Configure API keys and tokens in `.env`
3. Test with small repositories first using `--validate-only`
4. Extend agents or tools as needed
5. Generate and review PDF reports
6. Iterate on prompts and analysis quality