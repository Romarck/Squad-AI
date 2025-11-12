from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, List, Optional
import requests
import json
import base64
import os


class JiraIntegrationRequest(BaseModel):
    """Input schema for Jira Integration Tool."""
    action: str = Field(..., description="Action to perform: 'create_issue', 'read_issue', or 'update_issue'")
    title: str = Field(default="", description="Title of the issue (required for create_issue)")
    description: str = Field(default="", description="Description of the issue (required for create_issue)")
    project_key: str = Field(default="AUTO", description="Jira project key (for create_issue)")
    issue_key: str = Field(default="", description="Jira issue key (required for read_issue and update_issue)")
    status: str = Field(default="", description="New status for the issue (optional for update_issue)")
    comment: str = Field(default="", description="Comment to add to the issue (required for update_issue)")


class JiraIntegrationTool(BaseTool):
    """Tool for comprehensive Jira integration including creating, reading, and updating issues with proxy support."""

    name: str = "jira_integration_tool"
    description: str = (
        "Comprehensive Jira integration tool that can:\n"
        "1. Create new Jira issues/tasks\n"
        "2. Read existing Jira issues (title and description)\n"
        "3. Update Jira issues with comments and optionally change status\n"
        "\n"
        "Actions:\n"
        "- create_issue: Creates a new issue (requires title, description, optional project_key)\n"
        "- read_issue: Reads an issue (requires issue_key)\n"
        "- update_issue: Adds comment to an issue (requires issue_key, comment, optional status)\n"
        "\n"
        "Proxy Support:\n"
        "- Supports corporate proxy via HTTP_PROXY and HTTPS_PROXY environment variables\n"
        "- Automatically configures proxy when environment variables are set\n"
        "\n"
        "Requires environment variables: JIRA_URL, JIRA_EMAIL, JIRA_API_KEY\n"
        "Optional proxy variables: HTTP_PROXY, HTTPS_PROXY"
    )
    args_schema: Type[BaseModel] = JiraIntegrationRequest

    def _get_proxy_config(self) -> Dict[str, str]:
        """Get proxy configuration from environment variables."""
        http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
        https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        
        proxy_config = {}
        
        if http_proxy:
            proxy_config["http"] = http_proxy
            print(f"DEBUG: HTTP proxy configured: {http_proxy}")
        
        if https_proxy:
            proxy_config["https"] = https_proxy
            print(f"DEBUG: HTTPS proxy configured: {https_proxy}")
        
        if not proxy_config:
            print("DEBUG: No proxy configuration found")
        
        return proxy_config

    def _create_session(self) -> requests.Session:
        """Create a requests session with proxy configuration if available."""
        session = requests.Session()
        
        # Configure proxy
        proxy_config = self._get_proxy_config()
        if proxy_config:
            session.proxies.update(proxy_config)
            print(f"DEBUG: Session configured with proxies: {proxy_config}")
        
        return session

    def _get_auth_headers(self) -> Dict[str, str]:
        """Create authentication headers for Jira API."""
        try:
            jira_email = os.environ.get("JIRA_EMAIL")
            jira_api_key = os.environ.get("JIRA_API_KEY")
            
            if not jira_email or not jira_api_key:
                raise ValueError("JIRA_EMAIL and JIRA_API_KEY environment variables are required")
            
            # Create basic auth string
            credentials = f"{jira_email}:{jira_api_key}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            return {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        except Exception as e:
            raise ValueError(f"Failed to create authentication headers: {str(e)}")

    def _get_base_url(self) -> str:
        """Get Jira base URL from environment variables."""
        jira_url = os.environ.get("JIRA_URL")
        if not jira_url:
            raise ValueError("JIRA_URL environment variable is required")
        
        # Ensure URL ends with /rest/api/2
        if not jira_url.endswith('/'):
            jira_url += '/'
        if not jira_url.endswith('rest/api/2/'):
            jira_url += 'rest/api/2/'
        
        return jira_url

    def _parse_error_response(self, response: requests.Response) -> str:
        """Parse error response from Jira API to extract meaningful error messages."""
        try:
            # Try to parse as JSON first
            error_data = response.json()
            
            error_messages = []
            
            # Handle different error response formats
            if 'errorMessages' in error_data and error_data['errorMessages']:
                error_messages.extend(error_data['errorMessages'])
            
            if 'errors' in error_data and error_data['errors']:
                for field, message in error_data['errors'].items():
                    error_messages.append(f"{field}: {message}")
            
            # If we have structured errors, return them
            if error_messages:
                return f"Jira API errors: {'; '.join(error_messages)}"
            
            # If no structured errors but we have JSON, return the whole thing
            return f"Jira API response: {json.dumps(error_data, indent=2)}"
            
        except (json.JSONDecodeError, ValueError):
            # If it's not JSON, return the raw text
            return f"Jira API error (Status {response.status_code}): {response.text}"

    def _validate_create_issue_fields(self, title: str, description: str, project_key: str) -> str:
        """Validate required fields for issue creation."""
        errors = []
        
        if not title or title.strip() == "":
            errors.append("Title is required and cannot be empty")
        
        if not description or description.strip() == "":
            errors.append("Description is required and cannot be empty")
        
        if not project_key or project_key.strip() == "":
            errors.append("Project key is required and cannot be empty")
        
        if len(title) > 255:
            errors.append("Title is too long (maximum 255 characters)")
        
        return "; ".join(errors) if errors else ""

    def _make_request(self, method: str, url: str, headers: Dict[str, str], data: str = None, timeout: int = 30) -> requests.Response:
        """Make HTTP request with proxy support and error handling."""
        session = self._create_session()
        
        try:
            print(f"DEBUG: Making {method} request to: {url}")
            if self._get_proxy_config():
                print(f"DEBUG: Using proxy configuration")
            
            response = session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                timeout=timeout
            )
            
            print(f"DEBUG: Response status: {response.status_code}")
            return response
            
        except requests.exceptions.ProxyError as e:
            print(f"DEBUG: Proxy error: {str(e)}")
            raise requests.exceptions.RequestException(f"Proxy connection failed: {str(e)}")
        except requests.exceptions.SSLError as e:
            print(f"DEBUG: SSL error (possibly proxy related): {str(e)}")
            raise requests.exceptions.RequestException(f"SSL connection failed (check proxy configuration): {str(e)}")
        except requests.exceptions.ConnectionError as e:
            print(f"DEBUG: Connection error: {str(e)}")
            if self._get_proxy_config():
                raise requests.exceptions.RequestException(f"Connection failed (check proxy configuration and network): {str(e)}")
            else:
                raise requests.exceptions.RequestException(f"Connection failed: {str(e)}")
        finally:
            session.close()

    def _create_issue(self, title: str, description: str, project_key: str = "AUTO") -> str:
        """Create a new Jira issue."""
        try:
            # Validate fields before making API call
            validation_error = self._validate_create_issue_fields(title, description, project_key)
            if validation_error:
                return f"Validation failed: {validation_error}"

            base_url = self._get_base_url()
            headers = self._get_auth_headers()
            
            # Create issue payload - using Task instead of Story for better compatibility
            issue_data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": title.strip(),
                    "description": description.strip(),
                    "issuetype": {"name": "Task"}  # Changed from Story to Task for better compatibility
                }
            }
            
            # Log the request for debugging
            print(f"DEBUG: Creating Jira issue with payload: {json.dumps(issue_data, indent=2)}")
            print(f"DEBUG: Request URL: {base_url}issue")
            
            response = self._make_request(
                method="POST",
                url=f"{base_url}issue",
                headers=headers,
                data=json.dumps(issue_data)
            )
            
            print(f"DEBUG: Response headers: {dict(response.headers)}")
            
            if response.status_code == 201:
                result = response.json()
                issue_key = result.get('key', '')
                issue_url = result.get('self', '')
                return f"Successfully created Jira issue: {issue_key}\nURL: {issue_url}"
            else:
                error_details = self._parse_error_response(response)
                return f"Failed to create issue (Status {response.status_code}): {error_details}"
                
        except requests.exceptions.Timeout:
            return "Error: Request timed out while creating issue (30 seconds)"
        except requests.exceptions.RequestException as e:
            return f"Network/Proxy error while creating issue: {str(e)}"
        except ValueError as e:
            return f"Configuration error: {str(e)}"
        except Exception as e:
            return f"Unexpected error creating issue: {str(e)}"

    def _read_issue(self, issue_key: str) -> str:
        """Read a Jira issue and return title and description."""
        try:
            if not issue_key or issue_key.strip() == "":
                return "Error: Issue key is required and cannot be empty"

            base_url = self._get_base_url()
            headers = self._get_auth_headers()
            
            print(f"DEBUG: Reading Jira issue: {issue_key}")
            
            response = self._make_request(
                method="GET",
                url=f"{base_url}issue/{issue_key.strip()}",
                headers=headers
            )
            
            if response.status_code == 200:
                issue = response.json()
                fields = issue.get('fields', {})
                
                title = fields.get('summary', 'No title')
                description = fields.get('description', 'No description')
                status = fields.get('status', {}).get('name', 'Unknown')
                assignee = fields.get('assignee')
                assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
                issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
                
                return (
                    f"Issue: {issue_key}\n"
                    f"Title: {title}\n"
                    f"Type: {issue_type}\n"
                    f"Status: {status}\n"
                    f"Assignee: {assignee_name}\n"
                    f"Description: {description}"
                )
            elif response.status_code == 404:
                return f"Issue {issue_key} not found. Please verify the issue key is correct."
            elif response.status_code == 401:
                return "Authentication failed. Please check your JIRA_EMAIL and JIRA_API_KEY."
            elif response.status_code == 403:
                return f"Access denied to issue {issue_key}. You may not have permission to view this issue."
            else:
                error_details = self._parse_error_response(response)
                return f"Failed to read issue {issue_key}: {error_details}"
                
        except requests.exceptions.Timeout:
            return "Error: Request timed out while reading issue (30 seconds)"
        except requests.exceptions.RequestException as e:
            return f"Network/Proxy error while reading issue: {str(e)}"
        except ValueError as e:
            return f"Configuration error: {str(e)}"
        except Exception as e:
            return f"Unexpected error reading issue: {str(e)}"

    def _update_issue(self, issue_key: str, comment: str, status: str = "") -> str:
        """Add a comment to a Jira issue and optionally update status."""
        try:
            if not issue_key or issue_key.strip() == "":
                return "Error: Issue key is required and cannot be empty"

            base_url = self._get_base_url()
            headers = self._get_auth_headers()
            
            results = []
            
            # Add comment
            if comment and comment.strip():
                comment_data = {
                    "body": comment.strip()
                }
                
                print(f"DEBUG: Adding comment to {issue_key}: {comment_data}")
                
                response = self._make_request(
                    method="POST",
                    url=f"{base_url}issue/{issue_key.strip()}/comment",
                    headers=headers,
                    data=json.dumps(comment_data)
                )
                
                print(f"DEBUG: Comment response status: {response.status_code}")
                
                if response.status_code == 201:
                    results.append(f"Successfully added comment to {issue_key}")
                else:
                    error_details = self._parse_error_response(response)
                    results.append(f"Failed to add comment: {error_details}")
            
            # Update status if provided
            if status and status.strip():
                # Get available transitions
                print(f"DEBUG: Getting transitions for {issue_key}")
                
                transitions_response = self._make_request(
                    method="GET",
                    url=f"{base_url}issue/{issue_key.strip()}/transitions",
                    headers=headers
                )
                
                if transitions_response.status_code == 200:
                    transitions = transitions_response.json().get('transitions', [])
                    target_transition = None
                    
                    print(f"DEBUG: Available transitions: {[t.get('to', {}).get('name', '') for t in transitions]}")
                    
                    # Find transition that leads to desired status
                    for transition in transitions:
                        if transition.get('to', {}).get('name', '').lower() == status.lower():
                            target_transition = transition
                            break
                    
                    if target_transition:
                        transition_data = {
                            "transition": {
                                "id": target_transition['id']
                            }
                        }
                        
                        print(f"DEBUG: Transitioning to {status} with data: {transition_data}")
                        
                        transition_response = self._make_request(
                            method="POST",
                            url=f"{base_url}issue/{issue_key.strip()}/transitions",
                            headers=headers,
                            data=json.dumps(transition_data)
                        )
                        
                        if transition_response.status_code == 204:
                            results.append(f"Successfully updated status of {issue_key} to {status}")
                        else:
                            error_details = self._parse_error_response(transition_response)
                            results.append(f"Failed to update status: {error_details}")
                    else:
                        available_statuses = [t.get('to', {}).get('name', '') for t in transitions]
                        results.append(f"Status '{status}' not available. Available transitions: {available_statuses}")
                else:
                    error_details = self._parse_error_response(transitions_response)
                    results.append(f"Failed to get available transitions: {error_details}")
            
            return "\n".join(results) if results else "No actions performed"
                
        except requests.exceptions.Timeout:
            return "Error: Request timed out while updating issue (30 seconds)"
        except requests.exceptions.RequestException as e:
            return f"Network/Proxy error while updating issue: {str(e)}"
        except ValueError as e:
            return f"Configuration error: {str(e)}"
        except Exception as e:
            return f"Unexpected error updating issue: {str(e)}"

    def _run(self, action: str, title: str = "", description: str = "", project_key: str = "AUTO", 
            issue_key: str = "", status: str = "", comment: str = "") -> str:
        """Execute the specified Jira action."""
        
        try:
            # Log proxy configuration status
            proxy_config = self._get_proxy_config()
            if proxy_config:
                print(f"DEBUG: Tool initialized with proxy configuration: {list(proxy_config.keys())}")
            else:
                print("DEBUG: Tool initialized without proxy configuration")
            
            if action == "create_issue":
                if not title or not description:
                    return "Error: Both title and description are required for creating an issue"
                return self._create_issue(title, description, project_key)
            
            elif action == "read_issue":
                if not issue_key:
                    return "Error: issue_key is required for reading an issue"
                return self._read_issue(issue_key)
            
            elif action == "update_issue":
                if not issue_key:
                    return "Error: issue_key is required for updating an issue"
                if not comment and not status:
                    return "Error: Either comment or status (or both) must be provided for updating an issue"
                return self._update_issue(issue_key, comment, status)
            
            else:
                return f"Error: Invalid action '{action}'. Supported actions: create_issue, read_issue, update_issue"
                
        except Exception as e:
            return f"Unexpected error: {str(e)}"