"""
LangChain-compatible tools for GitHub fetching and Cloud Run invocation.
"""
import os
import requests
from github import Github
from langchain_core.tools import tool
from typing import List, Dict, Any

@tool
def fetch_github_repos(username: str, repo_names: str = "all") -> List[Dict[str, Any]]:
    """
    Fetch metadata and file contents for the given GitHub user/repos.
    repo_names = 'all' or comma-separated list.
    Returns list of repository data with metadata and file contents.
    """
    try:
        g = Github(os.getenv("GITHUB_TOKEN"))
        user = g.get_user(username)
        
        if repo_names == "all":
            repos = list(user.get_repos())[:10]  # Limit to 10 repos for performance
        else:
            repo_list = [name.strip() for name in repo_names.split(",")]
            repos = [user.get_repo(name) for name in repo_list]
        
        data = []
        for repo in repos:
            try:
                # Get repository contents recursively
                contents = repo.get_contents("")
                files = {}
                processed_files = 0
                max_files = 50  # Limit files per repo for performance
                
                while contents and processed_files < max_files:
                    file = contents.pop(0)
                    if file.type == "dir":
                        try:
                            contents.extend(repo.get_contents(file.path))
                        except Exception:
                            # Skip directories that can't be accessed
                            continue
                    else:
                        try:
                            # Limit file size to avoid memory issues
                            if file.size > 100000:  # 100KB limit
                                files[file.path] = f"[Large file - {file.size} bytes - content truncated]"
                            else:
                                content = file.decoded_content.decode('utf-8', errors='ignore')
                                files[file.path] = content
                            processed_files += 1
                        except Exception as e:
                            files[file.path] = f"[Error reading file: {str(e)}]"
                            processed_files += 1
                
                repo_data = {
                    "name": repo.name,
                    "description": repo.description or "",
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "url": repo.html_url,
                    "created_at": str(repo.created_at),
                    "updated_at": str(repo.updated_at),
                    "files": files,
                    "total_files_processed": processed_files
                }
                data.append(repo_data)
                
            except Exception as e:
                # Add repository with error info
                data.append({
                    "name": repo.name,
                    "description": repo.description or "",
                    "error": f"Could not access repository: {str(e)}",
                    "files": {},
                    "total_files_processed": 0
                })
        
        return data
        
    except Exception as e:
        return [{
            "error": f"Failed to fetch repositories for user {username}: {str(e)}",
            "files": {},
            "total_files_processed": 0
        }]


@tool
def call_cloud_run(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generic POST to your Cloud Run service.
    endpoint must start with '/'.
    Returns the JSON response from the service.
    """
    try:
        base_url = os.getenv("CLOUD_RUN_URL")
        token = os.getenv("CLOUD_RUN_TOKEN")
        
        if not base_url or not token:
            return {
                "error": "Cloud Run not configured. Set CLOUD_RUN_URL and CLOUD_RUN_TOKEN in .env",
                "success": False
            }
        
        url = base_url.rstrip("/") + endpoint
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return {
            "data": response.json(),
            "success": True,
            "status_code": response.status_code
        }
        
    except requests.exceptions.Timeout:
        return {
            "error": "Cloud Run request timed out after 30 seconds",
            "success": False
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Cloud Run request failed: {str(e)}",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"Unexpected error calling Cloud Run: {str(e)}",
            "success": False
        }