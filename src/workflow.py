"""
LangGraph workflow with enhanced quality gates.
"""
from langgraph.graph import StateGraph, END
from src.agents import (
    AgentState, 
    fetcher_node, 
    data_quality_reviewer_node,
    analyzer_node,
    analysis_quality_reviewer_node, 
    synthesizer_node,
    final_quality_reviewer_node
)

# Create the workflow graph
graph = StateGraph(AgentState)

# Add all nodes
graph.add_node("fetcher", fetcher_node)
graph.add_node("data_quality_reviewer", data_quality_reviewer_node)
graph.add_node("analyzer", analyzer_node)
graph.add_node("analysis_quality_reviewer", analysis_quality_reviewer_node)
graph.add_node("synthesizer", synthesizer_node)
graph.add_node("final_quality_reviewer", final_quality_reviewer_node)

# Set entry point
graph.set_entry_point("fetcher")

# Add edges for the workflow
graph.add_edge("fetcher", "data_quality_reviewer")
graph.add_edge("data_quality_reviewer", "analyzer")
graph.add_edge("analyzer", "analysis_quality_reviewer")
graph.add_edge("analysis_quality_reviewer", "synthesizer")
graph.add_edge("synthesizer", "final_quality_reviewer")
graph.add_edge("final_quality_reviewer", END)

# Compile the workflow
workflow = graph.compile()

def run_analysis(username: str, repos: str = "all") -> dict:
    """Run the complete multi-agent analysis workflow."""
    
    initial_state = {
        "username": username,
        "repos": repos,
        "repos_data": [],
        "analyses": [],
        "final_report": "",
        "data_quality_review": {},
        "analysis_quality_review": {},
        "final_quality_review": {}
    }
    
    # Execute the workflow
    result = workflow.invoke(initial_state)
    return result

def get_quality_summary(result: dict) -> dict:
    """Extract quality summary from workflow result."""
    
    # Extract quality reviews
    data_quality = result.get("data_quality_review", {})
    analysis_quality = result.get("analysis_quality_review", {})
    final_quality = result.get("final_quality_review", {})
    
    # Calculate overall statistics
    repos_data = result.get("repos_data", [])
    repositories_analyzed = len([r for r in repos_data if not r.get("error")])
    total_files_processed = sum(r.get("total_files_processed", 0) for r in repos_data)
    
    # Determine overall approval
    all_approved = (
        data_quality.get("approved", False) and
        analysis_quality.get("approved", False) and 
        final_quality.get("approved", False)
    )
    
    return {
        "overall_approved": all_approved,
        "repositories_analyzed": repositories_analyzed,
        "total_files_processed": total_files_processed,
        "data_quality": data_quality,
        "analysis_quality": analysis_quality,
        "final_quality": final_quality
    }