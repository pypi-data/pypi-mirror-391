"""
Client for interacting with the GitHub REST API.
Handles repository creation, permission assignment, and branch protection.
"""

import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, org_name: Optional[str] = None):
        """
        Initialize the GitHub client.

        Args:
            token: GitHub authentication token
            org_name: Organization name (optional, can be passed per method)
        """
        self.token = token
        self.org_name = org_name
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an HTTP request to the GitHub API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests (json, data, etc.)

        Returns:
            requests Response object
        """
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)

        # Response logging
        if response.status_code >= 400:
            logger.error(f"Error in {method} {url}: {response.status_code} - {response.text}")
        else:
            logger.info(f"Success in {method} {url}: {response.status_code}")

        response.raise_for_status()
        return response

    def create_repository(
        self,
        repo_name: str,
        description: str = "",
        is_private: bool = False,
        template: Optional[Dict[str, str]] = None,
        org_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new repository on GitHub.

        Args:
            repo_name: Repository name
            description: Repository description
            is_private: Whether the repository should be private
            template: Dictionary with 'owner' and 'repo' of the template (optional)
            org_name: Organization name (optional, uses self.org_name if not provided)

        Returns:
            API response with information about the created repository
        """
        org = org_name or self.org_name

        if not org:
            raise ValueError("Organization name must be specified")
        
        if template:
            # Create repository from template
            logger.info(f"Creating repository '{repo_name}' from template '{template['repo']}'...")
            logger.info(f"Template: {template}")
            logger.info(f"Owner: {template['owner']}")
            endpoint = f"/repos/{template['owner']}/{template['repo']}/generate"

            data = {
                "name": repo_name,
                "owner": org,
                "description": description,
                "private": is_private,
            }

            response = self._make_request("POST", endpoint, json=data)
        else:
            # Create empty repository
            logger.info(f"Creating empty repository '{repo_name}'...")
            endpoint = f"/orgs/{org}/repos"

            data = {
                "name": repo_name,
                "description": description,
                "private": is_private,
                "auto_init": False,
            }

            response = self._make_request("POST", endpoint, json=data)
        
        repo_info = response.json()
        logger.info(f"Repository '{repo_name}' created successfully")
        return repo_info

    def add_team_permission(
        self, repo_name: str, team_slug: str, permission: str, org_name: Optional[str] = None
    ):
        """
        Assign permissions to a team on a repository.

        Args:
            repo_name: Repository name
            team_slug: Team slug
            permission: Permission level (pull, push, admin, maintain, triage)
            org_name: Organization name (optional)
        """
        org = org_name or self.org_name

        if not org:
            raise ValueError("Organization name must be specified")

        logger.info(
            f"Assigning permission '{permission}' to team '{team_slug}' on '{repo_name}'..."
        )

        endpoint = f"/orgs/{org}/teams/{team_slug}/repos/{org}/{repo_name}"

        data = {"permission": permission}

        self._make_request("PUT", endpoint, json=data)
        logger.info(f"Permission assigned successfully to team '{team_slug}'")

    def add_collaborator_permission(
        self, repo_name: str, username: str, permission: str, org_name: Optional[str] = None
    ):
        """
        Assign permissions to an individual collaborator on a repository.

        Args:
            repo_name: Repository name
            username: GitHub username of the collaborator
            permission: Permission level (pull, push, admin, maintain, triage)
            org_name: Organization name (optional)
        """
        org = org_name or self.org_name

        if not org:
            raise ValueError("Organization name must be specified")

        logger.info(
            f"Assigning permission '{permission}' to collaborator '{username}' on '{repo_name}'..."
        )

        endpoint = f"/repos/{org}/{repo_name}/collaborators/{username}"

        data = {"permission": permission}

        self._make_request("PUT", endpoint, json=data)
        logger.info(f"Permission assigned successfully to collaborator '{username}'")

    def get_authenticated_user(self) -> Dict[str, Any]:
        """
        Get the authenticated user information.

        Returns:
            Dictionary with user information (login, id, etc.)
        """
        logger.info("Getting authenticated user information...")
        endpoint = "/user"
        response = self._make_request("GET", endpoint)
        user_info = response.json()
        logger.info(f"Authenticated user: {user_info.get('login')}")
        return user_info

    def remove_collaborator(
        self, repo_name: str, username: str, org_name: Optional[str] = None
    ):
        """
        Remove a collaborator from a repository (removes all permissions).

        Args:
            repo_name: Repository name
            username: GitHub username of the collaborator to remove
            org_name: Organization name (optional)
        """
        org = org_name or self.org_name

        if not org:
            raise ValueError("Organization name must be specified")

        logger.info(
            f"Removing collaborator '{username}' from repository '{repo_name}'..."
        )

        endpoint = f"/repos/{org}/{repo_name}/collaborators/{username}"

        self._make_request("DELETE", endpoint)
        logger.info(f"Collaborator '{username}' removed successfully from repository '{repo_name}'")

    
    def create_branch(
        self,
        repo_name: str,
        branch_name: str,
        source_branch: str = "main",
        org_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new branch in a repository.

        Args:
            repo_name: Repository name
            branch_name: Name of the new branch to create
            source_branch: Source branch to create from (default: "main")
            org_name: Organization name (optional)

        Returns:
            API response with information about the created branch
        """
        org = org_name or self.org_name

        if not org:
            raise ValueError("Organization name must be specified")

        logger.info(f"Creating branch '{branch_name}' from '{source_branch}' in '{repo_name}'...")

        # First, get the SHA of the source branch
        source_endpoint = f"/repos/{org}/{repo_name}/git/ref/heads/{source_branch}"
        source_response = self._make_request("GET", source_endpoint)
        source_data = source_response.json()
        sha = source_data["object"]["sha"]

        # Create the new branch using the source branch SHA
        endpoint = f"/repos/{org}/{repo_name}/git/refs"
        data = {"ref": f"refs/heads/{branch_name}", "sha": sha}

        response = self._make_request("POST", endpoint, json=data)
        branch_info = response.json()
        logger.info(f"Branch '{branch_name}' created successfully")
        return branch_info

    def protect_branch(
        self, repo_name: str, branch: str, config: Dict[str, Any], org_name: Optional[str] = None
    ):
        """
        Apply protection rules to a branch.

        Args:
            repo_name: Repository name
            branch: Name of the branch to protect
            config: Dictionary with protection configuration from YAML (supports full repo-protection.json format)
            org_name: Organization name (optional)
        """
        org = org_name or self.org_name

        if not org:
            raise ValueError("Organization name must be specified")

        logger.info(f"Applying protection to branch '{branch}' on '{repo_name}'...")

        endpoint = f"/repos/{org}/{repo_name}/branches/{branch}/protection"

        # Build payload for branch protection - support full repo-protection.json format
        protection_data = {}

        # Required Status Checks
        if "required_status_checks" in config:
            status_checks_config = config["required_status_checks"]
            if status_checks_config is not None:
                # Ensure checks array is properly formatted with context and app_id
                checks = status_checks_config.get("checks", [])
                # Normalize checks to ensure they have the correct format
                normalized_checks = []
                for check in checks:
                    if isinstance(check, dict):
                        # Already in correct format with context and optionally app_id
                        normalized_checks.append(check)
                    elif isinstance(check, str):
                        # Legacy format: just context string
                        normalized_checks.append({"context": check})
                
                protection_data["required_status_checks"] = {
                    "strict": status_checks_config.get("strict", False),
                    "checks": normalized_checks,
                }
            else:
                protection_data["required_status_checks"] = None
        else:
            # Legacy support: status_checks section
            if config.get("status_checks", {}).get("require_up_to_date", False):
                status_config = config["status_checks"]
                protection_data["required_status_checks"] = {
                    "strict": status_config.get("require_up_to_date", False),
                    "checks": [
                        {"context": ctx} if isinstance(ctx, str) else ctx
                        for ctx in status_config.get("contexts", [])
                    ],
                }
            else:
                protection_data["required_status_checks"] = None

        # Enforce Admins
        if "enforce_admins" in config:
            protection_data["enforce_admins"] = config["enforce_admins"]
        else:
            protection_data["enforce_admins"] = None

        # Required Pull Request Reviews
        if "required_pull_request_reviews" in config:
            pr_reviews_config = config["required_pull_request_reviews"]
            if pr_reviews_config is not None:
                protection_data["required_pull_request_reviews"] = {
                    "dismissal_restrictions": pr_reviews_config.get("dismissal_restrictions", {}),
                    "dismiss_stale_reviews": pr_reviews_config.get("dismiss_stale_reviews", True),
                    "require_code_owner_reviews": pr_reviews_config.get("require_code_owner_reviews", False),
                    "required_approving_review_count": pr_reviews_config.get("required_approving_review_count", 1),
                    "require_last_push_approval": pr_reviews_config.get("require_last_push_approval", False),
                    "bypass_pull_request_allowances": pr_reviews_config.get("bypass_pull_request_allowances", {}),
                }
            else:
                protection_data["required_pull_request_reviews"] = None
        else:
            # Legacy support: pull_request section
            if config.get("pull_request", {}).get("required", False):
                pr_config = config["pull_request"]
                protection_data["required_pull_request_reviews"] = {
                    "dismissal_restrictions": {},
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": pr_config.get("require_code_owners", False),
                    "required_approving_review_count": pr_config.get("required_approvals", 1),
                    "require_last_push_approval": False,
                    "bypass_pull_request_allowances": {},
                }
            else:
                protection_data["required_pull_request_reviews"] = None

        # Restrictions
        if "restrictions" in config:
            protection_data["restrictions"] = config["restrictions"]
        else:
            protection_data["restrictions"] = None

        # Required Linear History
        if "required_linear_history" in config:
            protection_data["required_linear_history"] = config["required_linear_history"]
        else:
            protection_data["required_linear_history"] = False

        # Allow Force Pushes
        if "allow_force_pushes" in config:
            protection_data["allow_force_pushes"] = config["allow_force_pushes"]
        else:
            # Legacy support: disallow_force_push
            protection_data["allow_force_pushes"] = not config.get("disallow_force_push", False)

        # Allow Deletions
        if "allow_deletions" in config:
            protection_data["allow_deletions"] = config["allow_deletions"]
        else:
            # Legacy support: disallow_deletion
            protection_data["allow_deletions"] = not config.get("disallow_deletion", False)

        # Block Creations
        if "block_creations" in config:
            protection_data["block_creations"] = config["block_creations"]
        else:
            protection_data["block_creations"] = False

        # Required Conversation Resolution
        if "required_conversation_resolution" in config:
            protection_data["required_conversation_resolution"] = config["required_conversation_resolution"]
        else:
            protection_data["required_conversation_resolution"] = False

        # Lock Branch
        if "lock_branch" in config:
            protection_data["lock_branch"] = config["lock_branch"]
        else:
            protection_data["lock_branch"] = False

        # Allow Fork Syncing
        if "allow_fork_syncing" in config:
            protection_data["allow_fork_syncing"] = config["allow_fork_syncing"]
        else:
            protection_data["allow_fork_syncing"] = True

        # Required Signatures (legacy support)
        if "required_signatures" in config:
            protection_data["required_signatures"] = config["required_signatures"]
        elif "require_signatures" in config:
            protection_data["required_signatures"] = config["require_signatures"]
        else:
            protection_data["required_signatures"] = False

        self._make_request("PUT", endpoint, json=protection_data)
        logger.info(f"Protection applied successfully to branch '{branch}'")

    def remove_collaborator_admin_permission(
        self, repo_name: str, username: str = None, org_name: Optional[str] = None
    ):
        """
        Remove admin permission from a collaborator. If username is not provided,
        removes admin permission from the authenticated user (local user).

        Args:
            repo_name: Repository name
            username: GitHub username (optional, defaults to authenticated user)
            org_name: Organization name (optional)
        """
        logger.info("Algo")
        
        org = org_name or self.org_name

        if not org:
            raise ValueError("Organization name must be specified")

        # If username not provided, get the authenticated user
        if not username:
            user_info = self.get_authenticated_user()
            username = user_info.get("login")
            logger.info(f"No username provided, using authenticated user: {username}")

        logger.info(
            f"Removing collaborator '{username}' from repository '{repo_name}'..."
        )

        # Remove collaborator completely from repository (DELETE)
        endpoint = f"/repos/{org}/{repo_name}/collaborators/{username}"

        try:
            response = self._make_request("DELETE", endpoint)
            # Verify the operation was successful
            if response.status_code == 204:
                logger.info(f"Collaborator '{username}' removed successfully from repository '{repo_name}'")
            else:
                logger.warning(f"Unexpected status code {response.status_code} when removing collaborator '{username}'")
        except requests.exceptions.HTTPError as e:
            # Handle case where collaborator doesn't exist (404)
            if e.response.status_code == 404:
                logger.warning(f"Collaborator '{username}' not found in repository '{repo_name}' (may have already been removed)")
            else:
                logger.error(f"Failed to remove collaborator '{username}': {e}")
                raise
