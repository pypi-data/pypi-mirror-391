"""Competition tools for Kaggle API."""

import os
import json
import tempfile
from typing import Optional, Dict, Any

from kaggle_mcp.tools.auth import api, ensure_authenticated

def init_competition_tools(mcp_instance):
    """Initialize competition tools with the given MCP instance."""

    @mcp_instance.tool()
    def competitions_list(search: str = "", category: str = "all", group: str = "general",
                        sort_by: str = "latestDeadline", page: int = 1) -> str:
        """List available Kaggle competitions.
        
        Args:
            search: Term(s) to search for
            category: Filter by category (all, featured, research, recruitment, gettingStarted, masters, playground)
            group: Filter by group (general, entered, inClass)
            sort_by: Sort by (grouped, prize, earliestDeadline, latestDeadline, numberOfTeams, recentlyCreated)
            page: Page number for results paging
        
        Returns:
            JSON string with competition details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            competitions = api.competitions_list(search=search, category=category, 
                                            group=group, sort_by=sort_by, page=page)
            result = []
            
            for comp in competitions:
                result.append({
                    "ref": comp.ref,
                    "title": comp.title,
                    "url": comp.url,
                    "category": comp.category,
                    "deadline": str(comp.deadline) if comp.deadline else None,
                    "reward": comp.reward,
                    "teamCount": comp.teamCount,
                    "userHasEntered": comp.userHasEntered,
                    "description": comp.description
                })
                
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing competitions: {str(e)}"


    @mcp_instance.tool()
    def competition_details(competition: str) -> str:
        """Get details about a specific competition.
        
        Args:
            competition: Competition URL suffix (e.g., 'titanic')
        
        Returns:
            JSON string with competition details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            comp = api.competition_get(competition)
            result = {
                "ref": comp.ref,
                "title": comp.title,
                "url": comp.url,
                "category": comp.category,
                "deadline": str(comp.deadline) if comp.deadline else None,
                "reward": comp.reward,
                "teamCount": comp.teamCount,
                "userHasEntered": comp.userHasEntered,
                "description": comp.description,
                "evaluationMetric": comp.evaluationMetric,
                "isKernelsSubmissionsOnly": comp.isKernelsSubmissionsOnly,
                "tags": comp.tags
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error getting competition details: {str(e)}"


    @mcp_instance.tool()
    def competition_download_files(competition: str, path: str = "", 
                                file_name: str = "", force: bool = False) -> str:
        """Download competition files.
        
        Args:
            competition: Competition URL suffix (e.g., 'titanic')
            path: Folder where file(s) will be downloaded (defaults to a temp directory)
            file_name: File name, all files downloaded if not provided
            force: Force download even if files exist
        
        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg
        
        # Create a temporary directory if no path is specified
        use_temp = False
        if not path:
            path = tempfile.mkdtemp()
            use_temp = True
        
        try:
            if file_name:
                api.competition_download_file(competition, file_name, path=path, force=force)
                result = f"Downloaded file '{file_name}' to {path}"
            else:
                api.competition_download_files(competition, path=path, force=force)
                result = f"Downloaded all competition files to {path}"
            
            return result
        except Exception as e:
            if use_temp:
                try:
                    os.rmdir(path)
                except:
                    pass
            return f"Error downloading competition files: {str(e)}"


    @mcp_instance.tool()
    def competition_list_files(competition: str) -> str:
        """List files in a competition.
        
        Args:
            competition: Competition URL suffix (e.g., 'titanic')
        
        Returns:
            JSON string with file details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg

        try:
            files = api.competition_list_files(competition)
            result = []
            
            for file in files:
                result.append({
                    "name": file.name,
                    "size": file.size,
                    "creationDate": str(file.creationDate) if hasattr(file, 'creationDate') else None
                })
                
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing competition files: {str(e)}"


    @mcp_instance.tool()
    def competition_submissions(competition: str) -> str:
        """List your submissions for a competition.
        
        Args:
            competition: Competition URL suffix (e.g., 'titanic')
        
        Returns:
            JSON string with submission details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg
        
        try:
            submissions = api.competition_submissions(competition)
            result = []
            
            for sub in submissions:
                result.append({
                    "ref": sub.ref if hasattr(sub, 'ref') else None,
                    "fileName": sub.fileName if hasattr(sub, 'fileName') else None,
                    "date": str(sub.date) if hasattr(sub, 'date') else None,
                    "description": sub.description if hasattr(sub, 'description') else None,
                    "status": sub.status if hasattr(sub, 'status') else None,
                    "publicScore": sub.publicScore if hasattr(sub, 'publicScore') else None,
                    "privateScore": sub.privateScore if hasattr(sub, 'privateScore') else None
                })
                
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing submissions: {str(e)}"


    @mcp_instance.tool()
    def competition_leaderboard(competition: str) -> str:
        """Get the competition leaderboard.
        
        Args:
            competition: Competition URL suffix (e.g., 'titanic')
        
        Returns:
            JSON string with leaderboard details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg
        
        try:
            leaderboard = api.competition_leaderboard_view(competition)
            result = []
            
            for entry in leaderboard:
                result.append({
                    "teamId": entry.teamId if hasattr(entry, 'teamId') else None,
                    "teamName": entry.teamName if hasattr(entry, 'teamName') else None,
                    "submissionDate": str(entry.submissionDate) if hasattr(entry, 'submissionDate') else None,
                    "score": entry.score if hasattr(entry, 'score') else None,
                    "rank": entry.rank if hasattr(entry, 'rank') else None
                })
                
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error retrieving leaderboard: {str(e)}"


    @mcp_instance.tool()
    def competition_submit(competition: str, file_path: str, message: str) -> str:
        """Submit to a competition.
        
        Args:
            competition: Competition URL suffix (e.g., 'titanic')
            file_path: Path to the submission file
            message: Submission description
        
        Returns:
            Success message or error details
        """
        authenticated, msg = ensure_authenticated()
        if not authenticated:
            return msg
        
        try:
            # Check if file exists
            if not os.path.isfile(file_path):
                return f"Error: File not found at {file_path}"
            
            # Get file size and last modified date
            file_size = os.path.getsize(file_path)
            last_modified = int(os.path.getmtime(file_path))
            
            # Generate submission URL
            submission_url = api.competition_submit_url(competition, file_size, last_modified)
            
            # Upload the file
            result = api.competition_submit_file(file_path, submission_url['createUrl'])
            
            # Submit with the file token
            response = api.competition_submit(competition, result['token'], message)
            
            return f"Submission successful! Status: {response.status}"
        except Exception as e:
            return f"Error submitting to competition: {str(e)}"
