"""
LangGraph state and agent nodes with enhanced quality review.
"""
from typing import TypedDict, List, Dict, Any
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from src.config import AGENT_LLM_CONFIG
from src.tools import fetch_github_repos, call_cloud_run

# Optional imports for vector storage (graceful fallback if unavailable)
try:
    from langchain_community.embeddings import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    vector_available = True
except ImportError:
    vector_available = False
    print("Warning: Vector storage (FAISS/OpenAI embeddings) not available. Using text-only analysis.")

# ---------- LangGraph State ----------
class AgentState(TypedDict):
    username: str
    repos: str                     # 'all' or comma-separated list
    repos_data: List[Dict[str, Any]]
    analyses: List[str]
    final_report: str
    
    # Quality review states
    data_quality_review: Dict[str, Any]
    analysis_quality_review: Dict[str, Any] 
    final_quality_review: Dict[str, Any]

# ---------- Prompts ----------
DATA_QUALITY_PROMPT = PromptTemplate(
    input_variables=["repos_data"],
    template="""
You are a data quality reviewer. Assess the completeness and quality of the GitHub repository data below.

Evaluate:
1. Repository accessibility and metadata completeness
2. File content quality and readability
3. Data structure and organization
4. Any missing or corrupted information

Provide a structured review with:
- Overall assessment (APPROVED/NEEDS_IMPROVEMENT)
- Specific issues found (if any)
- Recommendations for data quality improvement
- File processing statistics

Repository Data:
{repos_data}
"""
)

ANALYZER_PROMPT = PromptTemplate(
    input_variables=["repo"],
    template="""
You are a senior software architect analyzing GitHub repositories. 

For the repository data below, provide a comprehensive technical analysis covering:

1. **Purpose and Domain**
   - What problem does this repository solve?
   - Target audience and use cases
   - Business/technical domain

2. **Technical Architecture**
   - Key technologies, frameworks, and languages used
   - Architecture patterns and design decisions
   - Dependencies and integrations

3. **Code Quality and Structure**
   - Project organization and structure
   - Code quality indicators
   - Documentation and testing approaches

4. **Notable Patterns and Strengths**
   - Innovative or well-implemented features
   - Best practices demonstrated
   - Scalability and maintainability aspects

5. **Areas for Improvement**
   - Potential technical debt or issues
   - Missing components or features
   - Performance or security considerations

Repository Data:
{repo}
"""
)

ANALYSIS_QUALITY_PROMPT = PromptTemplate(
    input_variables=["analysis"],
    template="""
You are an analysis quality reviewer. Evaluate the technical analysis below for:

1. **Technical Depth**
   - Are all major technical aspects covered?
   - Is the analysis sufficiently detailed?
   - Are the conclusions well-supported?

2. **Accuracy and Completeness**
   - Are the technical assessments accurate?
   - Is any critical information missing?
   - Are the recommendations actionable?

3. **Professional Standards**
   - Is the analysis clearly structured?
   - Is the language professional and precise?
   - Would this be useful for technical decision-making?

Provide a structured review with:
- Overall assessment (APPROVED/NEEDS_IMPROVEMENT)
- Specific strengths of the analysis
- Areas requiring improvement (if any)
- Recommendations for enhancing analysis quality

Analysis to Review:
{analysis}
"""
)

SYNTHESIZER_PROMPT = PromptTemplate(
    input_variables=["analyses"],
    template="""
Combine the following individual repository analyses into a comprehensive multi-repository report.

Create a cohesive report that includes:

1. **Executive Summary**
   - Overview of all repositories analyzed
   - Key findings and insights
   - Overall portfolio assessment

2. **Technical Portfolio Analysis**
   - Technology stack trends and patterns
   - Architecture approaches across repositories
   - Code quality and best practices summary

3. **Comparative Insights**
   - Similarities and differences between repositories
   - Evolution of technologies and approaches
   - Cross-repository learning opportunities

4. **Strategic Recommendations**
   - Portfolio-level improvement opportunities
   - Technology standardization suggestions
   - Development process insights

Individual Analyses:
{analyses}
"""
)

FINAL_QUALITY_PROMPT = PromptTemplate(
    input_variables=["report"],
    template="""
You are a final quality reviewer for technical reports. Evaluate this multi-repository analysis report for:

1. **Content Quality**
   - Is the report comprehensive and well-structured?
   - Are all sections complete and coherent?
   - Is the executive summary accurate and insightful?

2. **Professional Standards**
   - Is the language clear and professional?
   - Are technical terms used correctly?
   - Is the format appropriate for stakeholders?

3. **Actionable Value**
   - Does the report provide actionable insights?
   - Are recommendations practical and specific?
   - Would this report be valuable for decision-making?

Provide a structured final review with:
- Overall assessment (APPROVED/NEEDS_IMPROVEMENT)
- Report strengths and highlights
- Areas requiring revision (if any)
- Final recommendations for report quality

Report to Review:
{report}
"""
)

# ---------- Node Functions ----------
def fetcher_node(state: AgentState) -> AgentState:
    """Fetch repository data from GitHub API."""
    try:
        repos_data = fetch_github_repos.invoke({
            "username": state["username"],
            "repo_names": state["repos"]
        })
        state["repos_data"] = repos_data
    except Exception as e:
        state["repos_data"] = [{
            "error": f"Failed to fetch repository data: {str(e)}",
            "files": {},
            "total_files_processed": 0
        }]
    
    return state

def data_quality_reviewer_node(state: AgentState) -> AgentState:
    """Review the quality of fetched repository data."""
    try:
        chain = LLMChain(llm=AGENT_LLM_CONFIG["data_reviewer"], prompt=DATA_QUALITY_PROMPT)
        review = chain.run(repos_data=str(state["repos_data"]))
        
        # Determine approval based on review content
        approved = "APPROVED" in review.upper()
        
        state["data_quality_review"] = {
            "review": review,
            "approved": approved,
            "reviewer": "Data Quality Reviewer"
        }
    except Exception as e:
        state["data_quality_review"] = {
            "review": f"Error during data quality review: {str(e)}",
            "approved": False,
            "reviewer": "Data Quality Reviewer"
        }
    
    return state

def analyzer_node(state: AgentState) -> AgentState:
    """Analyze repositories using LLM and optional vector embeddings."""
    analyses = []
    
    for repo in state["repos_data"]:
        try:
            # Optional vector analysis if available
            vector_insight = ""
            if vector_available and repo.get("files"):
                try:
                    docs = [
                        Document(page_content=content, metadata={"file": path})
                        for path, content in repo["files"].items()
                        if isinstance(content, str) and len(content) > 0
                    ]
                    
                    if docs:
                        embeddings = OpenAIEmbeddings()
                        vectorstore = FAISS.from_documents(docs, embeddings)
                        # Vector analysis could be enhanced here
                        vector_insight = f"\n\nVector Analysis: Processed {len(docs)} files for semantic analysis."
                except Exception:
                    vector_insight = "\n\nVector Analysis: Not available for this repository."
            
            # LLM analysis
            chain = LLMChain(llm=AGENT_LLM_CONFIG["analyzer"], prompt=ANALYZER_PROMPT)
            analysis = chain.run(repo=str(repo))
            
            # Optional Cloud Run integration
            cloud_insight = ""
            try:
                if os.getenv("CLOUD_RUN_URL") and os.getenv("CLOUD_RUN_TOKEN"):
                    cloud_result = call_cloud_run.invoke({
                        "endpoint": "/analyze",
                        "payload": {"repository": repo["name"], "files": repo.get("files", {})}
                    })
                    if cloud_result.get("success"):
                        cloud_insight = f"\n\nCloud Analysis: {cloud_result['data']}"
            except Exception:
                # Cloud Run is optional, continue without it
                pass
            
            full_analysis = analysis + vector_insight + cloud_insight
            analyses.append(full_analysis)
            
        except Exception as e:
            analyses.append(f"Error analyzing repository {repo.get('name', 'unknown')}: {str(e)}")
    
    state["analyses"] = analyses
    return state

def analysis_quality_reviewer_node(state: AgentState) -> AgentState:
    """Review the quality of repository analyses."""
    try:
        all_analyses = " ".join(state["analyses"])
        chain = LLMChain(llm=AGENT_LLM_CONFIG["analysis_reviewer"], prompt=ANALYSIS_QUALITY_PROMPT)
        review = chain.run(analysis=all_analyses)
        
        # Determine approval based on review content
        approved = "APPROVED" in review.upper()
        
        state["analysis_quality_review"] = {
            "review": review,
            "approved": approved,
            "reviewer": "Analysis Quality Reviewer"
        }
    except Exception as e:
        state["analysis_quality_review"] = {
            "review": f"Error during analysis quality review: {str(e)}",
            "approved": False,
            "reviewer": "Analysis Quality Reviewer"
        }
    
    return state

def synthesizer_node(state: AgentState) -> AgentState:
    """Synthesize individual analyses into a comprehensive report."""
    try:
        chain = LLMChain(llm=AGENT_LLM_CONFIG["synthesizer"], prompt=SYNTHESIZER_PROMPT)
        final_report = chain.run(analyses="\n\n".join(state["analyses"]))
        state["final_report"] = final_report
    except Exception as e:
        state["final_report"] = f"Error during synthesis: {str(e)}"
    
    return state

def final_quality_reviewer_node(state: AgentState) -> AgentState:
    """Final quality review of the complete report."""
    try:
        chain = LLMChain(llm=AGENT_LLM_CONFIG["final_reviewer"], prompt=FINAL_QUALITY_PROMPT)
        review = chain.run(report=state["final_report"])
        
        # Determine approval based on review content
        approved = "APPROVED" in review.upper()
        
        state["final_quality_review"] = {
            "review": review,
            "approved": approved,
            "reviewer": "Final Quality Reviewer"
        }
    except Exception as e:
        state["final_quality_review"] = {
            "review": f"Error during final quality review: {str(e)}",
            "approved": False,
            "reviewer": "Final Quality Reviewer"
        }
    
    return state