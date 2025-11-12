from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
import requests
import json
import os
from requests.auth import HTTPBasicAuth


class JiraConnectivityTesterRequest(BaseModel):
    """Input schema for Jira Connectivity Tester Tool."""
    action: str = Field(
        ..., 
        description="Action to perform: 'test_connection' to test basic auth and connectivity, or 'list_projects' to list available projects"
    )
    project_key: Optional[str] = Field(
        None, 
        description="Optional project key to test specific project permissions (for issue creation testing)"
    )


class JiraConnectivityTesterTool(BaseTool):
    """Tool for testing Jira connectivity and permissions."""

    name: str = "jira_connectivity_tester"
    description: str = (
        "Tests Jira connectivity and permissions. Can test basic authentication, "
        "list available projects, and verify issue creation permissions for specific projects. "
        "Provides detailed diagnostic information about what's working and what's not."
    )
    args_schema: Type[BaseModel] = JiraConnectivityTesterRequest

    def _get_auth_headers(self):
        """Get authentication headers for Jira API requests."""
        jira_url = os.getenv("JIRA_URL")
        jira_email = os.getenv("JIRA_EMAIL")
        jira_api_key = os.getenv("JIRA_API_KEY")
        
        if not all([jira_url, jira_email, jira_api_key]):
            missing = []
            if not jira_url: missing.append("JIRA_URL")
            if not jira_email: missing.append("JIRA_EMAIL") 
            if not jira_api_key: missing.append("JIRA_API_KEY")
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return {
            "url": jira_url.rstrip('/'),
            "auth": HTTPBasicAuth(jira_email, jira_api_key),
            "headers": {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        }

    def _test_basic_connection(self):
        """Test basic connectivity and authentication."""
        try:
            config = self._get_auth_headers()
            
            # Test basic connectivity with myself endpoint
            response = requests.get(
                f"{config['url']}/rest/api/3/myself",
                auth=config['auth'],
                headers=config['headers'],
                timeout=30
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "message": f"✅ Authentication successful! Connected as: {user_data.get('displayName', 'Unknown')} ({user_data.get('emailAddress', 'No email')})",
                    "user_info": {
                        "display_name": user_data.get('displayName'),
                        "email": user_data.get('emailAddress'),
                        "account_id": user_data.get('accountId'),
                        "active": user_data.get('active', False)
                    }
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "message": "❌ Authentication failed! Please check your JIRA_EMAIL and JIRA_API_KEY.",
                    "error": "Invalid credentials"
                }
            elif response.status_code == 403:
                return {
                    "success": False,
                    "message": "❌ Access forbidden! Your credentials are valid but you don't have permission to access this Jira instance.",
                    "error": "Insufficient permissions"
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ Connection failed with status {response.status_code}: {response.text}",
                    "error": f"HTTP {response.status_code}"
                }
        
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "❌ Connection error! Please check your JIRA_URL and network connectivity.",
                "error": "Network connection failed"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "❌ Request timeout! The Jira server is not responding.",
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Unexpected error: {str(e)}",
                "error": str(e)
            }

    def _list_projects(self):
        """List all accessible projects."""
        try:
            config = self._get_auth_headers()
            
            response = requests.get(
                f"{config['url']}/rest/api/3/project",
                auth=config['auth'],
                headers=config['headers'],
                timeout=30
            )
            
            if response.status_code == 200:
                projects = response.json()
                if projects:
                    project_list = []
                    for project in projects:
                        project_list.append({
                            "key": project.get('key'),
                            "name": project.get('name'),
                            "type": project.get('projectTypeKey'),
                            "lead": project.get('lead', {}).get('displayName', 'Unknown'),
                            "url": project.get('self')
                        })
                    
                    result = f"✅ Found {len(projects)} accessible projects:\n"
                    for p in project_list:
                        result += f"  • {p['key']}: {p['name']} (Type: {p['type']}, Lead: {p['lead']})\n"
                    
                    return {
                        "success": True,
                        "message": result.strip(),
                        "projects": project_list
                    }
                else:
                    return {
                        "success": True,
                        "message": "⚠️  No projects found. You might not have access to any projects.",
                        "projects": []
                    }
            else:
                return {
                    "success": False,
                    "message": f"❌ Failed to fetch projects. Status {response.status_code}: {response.text}",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error fetching projects: {str(e)}",
                "error": str(e)
            }

    def _test_project_permissions(self, project_key):
        """Test permissions for a specific project."""
        try:
            config = self._get_auth_headers()
            
            # First, check if project exists and is accessible
            response = requests.get(
                f"{config['url']}/rest/api/3/project/{project_key}",
                auth=config['auth'],
                headers=config['headers'],
                timeout=30
            )
            
            if response.status_code == 404:
                return {
                    "success": False,
                    "message": f"❌ Project '{project_key}' not found or not accessible.",
                    "error": "Project not found"
                }
            elif response.status_code != 200:
                return {
                    "success": False,
                    "message": f"❌ Error accessing project '{project_key}'. Status {response.status_code}: {response.text}",
                    "error": f"HTTP {response.status_code}"
                }
            
            project_info = response.json()
            
            # Test issue type permissions
            issue_types_response = requests.get(
                f"{config['url']}/rest/api/3/project/{project_key}/issuetype",
                auth=config['auth'],
                headers=config['headers'],
                timeout=30
            )
            
            permissions_result = f"✅ Project '{project_key}' ({project_info.get('name')}) is accessible!\n"
            permissions_result += f"  Project Type: {project_info.get('projectTypeKey', 'Unknown')}\n"
            permissions_result += f"  Lead: {project_info.get('lead', {}).get('displayName', 'Unknown')}\n"
            
            if issue_types_response.status_code == 200:
                issue_types = issue_types_response.json()
                permissions_result += f"  Available Issue Types: {len(issue_types)}\n"
                for issue_type in issue_types[:5]:  # Show first 5 issue types
                    permissions_result += f"    • {issue_type.get('name', 'Unknown')}\n"
                if len(issue_types) > 5:
                    permissions_result += f"    ... and {len(issue_types) - 5} more\n"
            else:
                permissions_result += "  ⚠️  Could not fetch issue types (might indicate limited permissions)\n"
            
            # Test create issue permission by checking project metadata
            create_meta_response = requests.get(
                f"{config['url']}/rest/api/3/issue/createmeta?projectKeys={project_key}",
                auth=config['auth'],
                headers=config['headers'],
                timeout=30
            )
            
            if create_meta_response.status_code == 200:
                create_meta = create_meta_response.json()
                projects_meta = create_meta.get('projects', [])
                if projects_meta:
                    permissions_result += "  ✅ Create issue permission: Available\n"
                    issue_types_meta = projects_meta[0].get('issueTypes', [])
                    permissions_result += f"  Creatable Issue Types: {len(issue_types_meta)}\n"
                else:
                    permissions_result += "  ❌ Create issue permission: Not available\n"
            else:
                permissions_result += "  ❌ Create issue permission: Could not verify\n"
            
            return {
                "success": True,
                "message": permissions_result.strip(),
                "project_info": {
                    "key": project_info.get('key'),
                    "name": project_info.get('name'),
                    "type": project_info.get('projectTypeKey'),
                    "lead": project_info.get('lead', {}).get('displayName'),
                    "can_create_issues": len(create_meta.get('projects', [])) > 0 if create_meta_response.status_code == 200 else False
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error testing project permissions: {str(e)}",
                "error": str(e)
            }

    def _run(self, action: str, project_key: Optional[str] = None) -> str:
        """Execute the connectivity test based on the specified action."""
        
        if action not in ["test_connection", "list_projects"]:
            return f"❌ Invalid action '{action}'. Use 'test_connection' or 'list_projects'."
        
        try:
            if action == "test_connection":
                # Test basic connectivity first
                connection_result = self._test_basic_connection()
                result = connection_result['message'] + "\n"
                
                if connection_result['success']:
                    # If connection successful and project_key provided, test project permissions
                    if project_key:
                        project_result = self._test_project_permissions(project_key)
                        result += "\n" + project_result['message']
                    else:
                        result += "\n💡 Tip: Provide a project_key parameter to test project-specific permissions."
                
                return result
            
            elif action == "list_projects":
                # Test connection first
                connection_result = self._test_basic_connection()
                if not connection_result['success']:
                    return connection_result['message']
                
                # If connection successful, list projects
                projects_result = self._list_projects()
                result = connection_result['message'] + "\n\n" + projects_result['message']
                
                # If project_key provided, also test that specific project
                if project_key and projects_result['success']:
                    project_result = self._test_project_permissions(project_key)
                    result += "\n\n" + project_result['message']
                
                return result
            
        except Exception as e:
            return f"❌ Unexpected error during connectivity test: {str(e)}"