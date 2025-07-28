# Multi-Agent GitHub Repository Analysis Tool

**Built by [LostMind AI](https://www.LostMindAI.com)**

A practical multi-agent system that analyses GitHub repositories using multiple LLM providers and generates detailed PDF reports. This tool combines LangGraph workflow orchestration with vector embeddings to provide structured insights into code repositories.

## What This Tool Does

This tool was built to address a specific need: systematically analysing GitHub repositories to understand their architecture, technologies, and patterns. Rather than manually reviewing each repository, this system automates the process using AI agents that work together to provide comprehensive analysis.

**The approach:** Instead of a single AI trying to handle everything, we use specialised agents for different tasks - one fetches the data, another analyses it, and a third synthesises the findings. Quality review gates ensure the output meets standards.

## How It Works

### Multi-Agent Workflow
The system uses six specialised agents working in sequence:

1. **Fetcher Agent** - Connects to GitHub API and retrieves repository data
2. **Data Quality Reviewer** - Checks if the data is complete and usable
3. **Analyzer Agent** - Analyses code structure, technologies, and patterns
4. **Analysis Quality Reviewer** - Validates the technical analysis
5. **Synthesizer Agent** - Combines individual analyses into a cohesive report
6. **Final Quality Reviewer** - Ensures the final report meets standards

### LLM Provider Support
The tool supports multiple AI providers and automatically selects the best one available:
- OpenAI GPT-4o
- Google Gemini 2.5
- Anthropic Claude 3.5
- Grok (when available)

Each agent can use different providers depending on what works best for that specific task.

### Report Generation
Generates professional PDF reports with:
- Repository overview and technical assessment
- Architecture analysis and technology stack
- Identified patterns and potential improvements
- Quality metrics and review feedback

---

## Getting Started

### 1. Installation

```bash
# Clone this repository
git clone https://github.com/lostmind008/Multi-Agent-Github-Repo-Analysis-Tool.git
cd Multi-Agent-Github-Repo-Analysis-Tool

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys and tokens
# Required: GITHUB_TOKEN
# At least one LLM provider: OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY, or GROK_API_KEY
# Optional: CLOUD_RUN_URL, CLOUD_RUN_TOKEN
```

### 3. Basic Usage

```bash
# Analyze all repositories for a user
python main.py --user YOUR_GITHUB_USERNAME

# Analyze specific repositories
python main.py --user USERNAME --repos repo1,repo2,repo3

# Generate enhanced report with quality metrics
python main.py --user USERNAME --enhanced

# Custom output path
python main.py --user USERNAME --out custom_report.pdf

# Validate environment setup
python main.py --validate-only
```

### 4. Example Commands

```bash
# Analyze a popular open source project
python main.py --user microsoft --repos vscode --enhanced

# Quick analysis of your own repositories
python main.py --user YOUR_USERNAME --repos your-main-project

# Comprehensive analysis with quality assurance
python main.py --user fastapi --repos fastapi --enhanced --out fastapi_analysis.pdf
```

---

## System Architecture

### Multi-Agent Workflow

```
GitHub API → Fetcher Agent → Data Quality Reviewer
                                    ↓
Final Quality Reviewer ← Synthesizer Agent ← Analysis Quality Reviewer
         ↓                                            ↓
    PDF Report                              Analyzer Agent
                                                ↓
                                    Vector Embeddings + LLM Analysis
```

### Quality Assurance Pipeline

1. **Data Quality Gate**: Validates repository access, file readability, metadata completeness
2. **Analysis Quality Gate**: Reviews technical depth, accuracy, and completeness of analyses  
3. **Final Quality Gate**: Ensures report coherence, formatting, and professional standards

### LLM Provider Strategy

Each agent uses the optimal LLM for its specific function:
- **Data/Quality Reviewers**: Claude 3.5 (excellent at assessment and critique)
- **Analyzer**: GPT-4o (strong technical analysis capabilities)
- **Synthesizer**: Gemini 2.5 (superior at combining and synthesizing content)

---

## Report Features

### Standard Report
- Executive summary and portfolio overview
- Technical assessment by repository
- Comparative analysis and insights
- Actionable recommendations

### Enhanced Report (--enhanced flag)
- Professional formatting with quality metrics table
- Detailed quality review appendix
- Generation metadata and timestamps
- Visual quality indicators throughout

### Quality Metrics Tracked
- Data completeness and accessibility
- Analysis depth and technical accuracy
- Report coherence and professional presentation
- File processing statistics and coverage

---

## Configuration

### Environment Variables

```bash
# GitHub API (Required)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# LLM Providers (At least one required)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
GROK_API_KEY=xai-...

# Cloud Run Integration (Optional)
CLOUD_RUN_URL=https://your-service.run.app
CLOUD_RUN_TOKEN=your-bearer-token
```

### Performance Tuning

The system includes built-in performance optimizations:
- **Repository limit**: Maximum 10 repos for 'all' selection
- **File size limit**: 100KB per file to prevent memory issues
- **File count limit**: Maximum 50 files per repository
- **Timeout handling**: 30-second timeouts for external API calls

---

## System Requirements

- Python 3.9+ (tested on 3.10, 3.11, 3.12)
- Internet connection for GitHub API and LLM providers
- 500MB+ available memory for large repository analysis

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

**Created by:** [LostMind AI](https://www.LostMindAI.com)

## Why This Tool Exists

This tool reflects my approach to building practical AI applications - using multiple specialised agents instead of trying to make one agent do everything. The quality review gates are there because AI output can be inconsistent, and having systematic checks helps ensure reliable results.

The system is designed to be extended and modified. The multi-agent architecture makes it straightforward to add new analysis types or improve existing ones without rewriting the entire system.

---

## Contributing

If you find this tool useful and want to improve it, contributions are welcome. The architecture is designed to make extensions straightforward:

- **New analysis types** can be added as additional agent nodes
- **Different report formats** can be implemented in the report generator
- **Additional LLM providers** can be integrated through the config system
- **Performance improvements** are always appreciated

For issues or questions, please check the troubleshooting section in the documentation first.