"""GitHub organization tools for Point-Topic."""

from typing import Optional
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from point_topic_mcp.core.utils import check_env_vars
from dotenv import load_dotenv
import os
import json

load_dotenv()

ORG_NAME = "Point-Topic"

if check_env_vars('github_tools', ['GITHUB_TOKEN']):
    
    def _gh():
        """Get GitHub client."""
        from github import Github
        return Github(os.getenv("GITHUB_TOKEN"))
    
    def _fmt_issue(issue) -> dict:
        """Format issue data."""
        return {
            "number": issue.number,
            "title": issue.title,
            "state": issue.state,
            "url": issue.html_url,
            "repository": issue.repository.full_name,
            "author": issue.user.login,
            "created": issue.created_at.isoformat(),
            "labels": [l.name for l in issue.labels],
            "assignees": [a.login for a in issue.assignees],
        }

    def general_info() -> None:
        """
        These tools are used to interact with the Point-Topic GitHub organization.
        They can be used only by Admins.
        They are used to provide information on the Point Topic systems, as all our codebases are hosted here.
        They are used to search for issues and pull requests, create issues and pull requests,
        add comments to issues and pull requests, update issues and pull requests,
        and read file contents from repositories.

        Some of the most relevant repositories are:
        - UPC_Core (the dbt pipeline for the core UPC datasets)
        - UPC_Client (the dbt pipeline for delivering outputs to everywhere)
        - upc_query_agent (the MCP Client application)
        - point-topic-mcp (this repository)
 
        This function is only for displaying some general information to the agent via the docstring

        Returns: None
        """
        return None
    
    def search_issues(
        query: str = "",
        repo: str = "",
        state: str = "open",
        labels: str = "",
        assignee: str = "",
        max_results: int = 30,
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """Search issues/PRs across Point-Topic organization or in specific repo.
        
        Args:
            query: Search text
            repo: Limit to specific repo (optional)
            state: "open", "closed", or "all"
            labels: Comma-separated labels
            assignee: Username
            max_results: Max results (default 30)
        """
        try:
            g = _gh()
            parts = [f"org:{ORG_NAME}"]
            if query: parts.append(query)
            if repo: 
                parts.append(f"repo:{ORG_NAME}/{repo}" if "/" not in repo else f"repo:{repo}")
            if state != "all": parts.append(f"state:{state}")
            if labels:
                for l in labels.split(","): parts.append(f"label:{l.strip()}")
            if assignee: parts.append(f"assignee:{assignee}")
            
            results = [_fmt_issue(i) for i, _ in zip(g.search_issues(" ".join(parts)), range(max_results))]
            return json.dumps({"count": len(results), "issues": results}, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    def get_issue(
        repo: str,
        number: int,
        with_comments: bool = True,
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """Get issue/PR details including body and comments.
        
        Args:
            repo: Repo name
            number: Issue/PR number
            with_comments: Include comments (default True)
        """
        try:
            g = _gh()
            repo_name = f"{ORG_NAME}/{repo}" if "/" not in repo else repo
            issue = g.get_repo(repo_name).get_issue(number)
            
            result = _fmt_issue(issue)
            result["body"] = issue.body
            
            if with_comments and issue.comments > 0:
                result["comments"] = [{
                    "author": c.user.login,
                    "body": c.body,
                    "created": c.created_at.isoformat()
                } for c in issue.get_comments()]
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    def list_repos(
        language: str = "",
        max_results: int = 50,
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """List Point-Topic organization repositories.
        
        Args:
            language: Filter by language (e.g. "Python")
            max_results: Max results (default 50)
        """
        try:
            g = _gh()
            org = g.get_organization(ORG_NAME)
            results = []
            
            for i, repo in enumerate(org.get_repos()):
                if i >= max_results: break
                if language and repo.language != language: continue
                
                results.append({
                    "name": repo.name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "language": repo.language,
                    "private": repo.private,
                    "default_branch": repo.default_branch,
                    "open_issues": repo.open_issues_count,
                    "updated": repo.updated_at.isoformat(),
                })
            
            return json.dumps({"count": len(results), "repos": results}, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    def get_repo(
        repo: str,
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """Get repository details including branches.
        
        Args:
            repo: Repo name
        """
        try:
            g = _gh()
            repo_name = f"{ORG_NAME}/{repo}" if "/" not in repo else repo
            r = g.get_repo(repo_name)
            
            return json.dumps({
                "name": r.name,
                "description": r.description,
                "url": r.html_url,
                "language": r.language,
                "default_branch": r.default_branch,
                "branches": [{"name": b.name, "protected": b.protected} for b in r.get_branches()],
                "topics": r.get_topics(),
                "stats": {
                    "stars": r.stargazers_count,
                    "forks": r.forks_count,
                    "open_issues": r.open_issues_count,
                }
            }, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    def read_file(
        repo: str,
        path: str,
        branch: str = "",
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """Read file contents from repository.
        
        Args:
            repo: Repo name
            path: File path (e.g. "src/main.py") or directory path
            branch: Branch name (default: repo default branch)
        
        Returns: File contents or JSON list of directory contents
        """
        try:
            g = _gh()
            repo_name = f"{ORG_NAME}/{repo}" if "/" not in repo else repo
            r = g.get_repo(repo_name)
            ref = branch or r.default_branch
            
            contents = r.get_contents(path, ref=ref)
            
            # If it's a file
            if hasattr(contents, 'decoded_content'):
                return contents.decoded_content.decode('utf-8')
            
            # If it's a directory
            if isinstance(contents, list):
                items = [{
                    "name": item.name,
                    "path": item.path,
                    "type": item.type,
                    "size": item.size if item.type == "file" else None
                } for item in contents]
                return json.dumps({"path": path, "items": items}, indent=2)
            
            return "Error: Unexpected content type"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def search_code(
        query: str,
        repo: str = "",
        language: str = "",
        max_results: int = 30,
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """Search code across Point-Topic repos.
        
        Args:
            query: Code search query
            repo: Limit to specific repo (optional)
            language: Filter by language (e.g. "Python")
            max_results: Max results (default 30)
        """
        try:
            g = _gh()
            parts = [query, f"org:{ORG_NAME}"]
            if language: parts.append(f"language:{language}")
            if repo:
                repo_name = f"{ORG_NAME}/{repo}" if "/" not in repo else repo
                parts.append(f"repo:{repo_name}")
            
            results = [{
                "repo": code.repository.full_name,
                "path": code.path,
                "url": code.html_url
            } for code, _ in zip(g.search_code(" ".join(parts)), range(max_results))]
            
            return json.dumps({"count": len(results), "results": results}, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    def get_commits(
        repo: str,
        branch: str = "",
        author: str = "",
        max_results: int = 20,
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """Get commit history for repository.
        
        Args:
            repo: Repo name
            branch: Branch name (optional)
            author: Filter by author (optional)
            max_results: Max results (default 20)
        """
        try:
            g = _gh()
            repo_name = f"{ORG_NAME}/{repo}" if "/" not in repo else repo
            r = g.get_repo(repo_name)
            
            kwargs = {}
            if branch: kwargs["sha"] = branch
            if author: kwargs["author"] = author
            
            commits = [{
                "sha": c.sha[:8],
                "message": c.commit.message.split("\n")[0],
                "author": c.commit.author.name,
                "date": c.commit.author.date.isoformat(),
                "url": c.html_url
            } for c, _ in zip(r.get_commits(**kwargs), range(max_results))]
            
            return json.dumps({"count": len(commits), "commits": commits}, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    # SAFE WRITE OPERATIONS
    
    def create_issue(
        repo: str,
        title: str,
        body: str = "",
        labels: str = "",
        assignees: str = "",
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """Create new issue. SAFE: cannot modify/delete existing data.
        
        Args:
            repo: Repo name
            title: Issue title
            body: Issue body (markdown)
            labels: Comma-separated labels
            assignees: Comma-separated usernames
        """
        try:
            g = _gh()
            repo_name = f"{ORG_NAME}/{repo}" if "/" not in repo else repo
            r = g.get_repo(repo_name)
            
            kwargs = {"title": title, "body": body}
            if labels: kwargs["labels"] = [l.strip() for l in labels.split(",")]
            if assignees: kwargs["assignees"] = [a.strip() for a in assignees.split(",")]
            
            issue = r.create_issue(**kwargs)
            
            return json.dumps({
                "success": True,
                "number": issue.number,
                "url": issue.html_url
            }, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    def create_pr(
        repo: str,
        title: str,
        head: str,
        base: str = "",
        body: str = "",
        draft: bool = False,
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """Create PR from existing branch. SAFE: cannot modify files.
        
        Args:
            repo: Repo name
            title: PR title
            head: Source branch (must exist)
            base: Target branch (default: repo default)
            body: PR body (markdown)
            draft: Create as draft (default False)
        """
        try:
            g = _gh()
            repo_name = f"{ORG_NAME}/{repo}" if "/" not in repo else repo
            r = g.get_repo(repo_name)
            
            pr = r.create_pull(
                title=title,
                body=body,
                head=head,
                base=base or r.default_branch,
                draft=draft
            )
            
            return json.dumps({
                "success": True,
                "number": pr.number,
                "url": pr.html_url
            }, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    def add_comment(
        repo: str,
        number: int,
        comment: str,
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """Add comment to issue/PR. SAFE: cannot modify/delete.
        
        Args:
            repo: Repo name
            number: Issue/PR number
            comment: Comment text (markdown)
        """
        try:
            g = _gh()
            repo_name = f"{ORG_NAME}/{repo}" if "/" not in repo else repo
            issue = g.get_repo(repo_name).get_issue(number)
            c = issue.create_comment(comment)
            
            return json.dumps({
                "success": True,
                "url": c.html_url
            }, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    def update_issue(
        repo: str,
        number: int,
        title: str = "",
        body: str = "",
        state: str = "",
        labels: str = "",
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """Update issue/PR. SAFE: cannot delete.
        
        Args:
            repo: Repo name
            number: Issue/PR number
            title: New title (optional)
            body: New body (optional)
            state: "open" or "closed" (optional)
            labels: Comma-separated labels to ADD (optional)
        """
        try:
            g = _gh()
            repo_name = f"{ORG_NAME}/{repo}" if "/" not in repo else repo
            issue = g.get_repo(repo_name).get_issue(number)
            
            kwargs = {}
            if title: kwargs["title"] = title
            if body: kwargs["body"] = body
            if state in ["open", "closed"]: kwargs["state"] = state
            
            if kwargs:
                issue.edit(**kwargs)
            
            if labels:
                issue.add_to_labels(*[l.strip() for l in labels.split(",")])
            
            return json.dumps({
                "success": True,
                "url": issue.html_url
            }, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, indent=2)

