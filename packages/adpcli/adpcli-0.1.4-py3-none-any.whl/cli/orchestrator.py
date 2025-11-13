"""
Main orchestrator that reads the YAML configuration file
and coordinates calls to platform-specific clients.
"""

import yaml
import logging
from typing import Dict, Any
from .github_client import GitHubClient 

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrator that coordinates artifact provisioning."""

    def __init__(self, gitHubClient, config_path: str):
        """
        Initialize the orchestrator with the path to the configuration file.

        Args:
            config_path: Path to the proyecto.yml file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.client = gitHubClient

    def _load_config(self) -> Dict[str, Any]:
        """Load and parse the YAML configuration file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            raise

    def provision(self):
        """
        Execute provisioning for all configured services.
        """
        logger.info("Starting provisioning process...")

        # Process GitHub if configured
        if "github" in self.config:
            logger.info("Processing GitHub configuration...")
            self._provision_github(self.config["github"])
        else:
            logger.info("No GitHub configuration found")

        # Other services can be added here in the future
        # if 'sonar' in self.config:
        #     self._provision_sonar(self.config['sonar'])

        logger.info("Provisioning process completed")

    def _provision_github(self, github_config: Dict[str, Any]):
        """
        Process GitHub configuration and call the corresponding client.

        Args:
            github_config: Dictionary with GitHub configuration from YAML
        """
        try:
            repo_name = github_config.get("repo_name")
            
            # Create repository
            
            self.client.create_repository(
                repo_name=repo_name,
                description=github_config.get("description"),
                is_private=github_config.get("is_private", False),
                template=github_config.get("template"),
            )
            
            # Assign permissions
            if "permissions" in github_config:
                permissions = github_config["permissions"]

                # Assign permissions to teams
                if "teams" in permissions:
                    for team in permissions["teams"]:
                        self.client.add_team_permission(
                            repo_name=repo_name,
                            team_slug=team.get("slug"),
                            permission=team.get("permission"),
                        )

                # Assign permissions to collaborators
                if "collaborators" in permissions:
                    for collaborator in permissions["collaborators"]:
                        self.client.add_collaborator_permission(
                            repo_name=repo_name,
                            username=collaborator.get("username"),
                            permission=collaborator.get("permission"),
                        )
            
            # Check workflow type to handle branch creation and protection
            workflow_type = self.config.get("workflow", {}).get("type", "")
            is_git_flow = workflow_type == "Git Flow"
            is_github_flow = workflow_type == "Github Flow"
            
            # Create branches
            if "branches" in github_config:
                for branch_config in github_config["branches"]:
                    branch_name = branch_config.get("name")
                    source_branch = branch_config.get("source", "main")
                    self.client.create_branch(
                        repo_name=repo_name,
                        branch_name=branch_name,
                        source_branch=source_branch,
                    )
            
            # If workflow is "Git Flow", create develop branch BEFORE applying protection
            main_protection_config = None
            if is_git_flow:
                try:
                    logger.info("Workflow is Git Flow - creating develop branch...")
                    self.client.create_branch(
                        repo_name=repo_name,
                        branch_name="develop",
                        source_branch="main",
                    )
                    logger.info("Develop branch created successfully")
                except Exception as e:
                    logger.warning(f"Could not create develop branch for Git Flow: {e}")
                    # Continue execution even if this fails
            
            # Apply branch protection
            if "branch_protection" in github_config:
                for protection in github_config["branch_protection"]:
                    branch = protection.get("branch")
                    # Extract branch name and remove it from config before passing to protect_branch
                    protection_config = {k: v for k, v in protection.items() if k != "branch"}
                    
                    # Store main branch protection config for Git Flow
                    if branch == "main":
                        main_protection_config = protection_config
                    
                    # Skip develop branch protection if Git Flow (we'll apply main's config later)
                    if is_git_flow and branch == "develop":
                        logger.info("Skipping develop branch protection from YAML (will use main's config for Git Flow)")
                        continue
                    
                    # Skip develop branch protection if Github Flow (develop branch is not created in Github Flow)
                    if is_github_flow and branch == "develop":
                        logger.info("Skipping develop branch protection for Github Flow (develop branch is not created in this workflow)")
                        continue
                    
                    self.client.protect_branch(
                        repo_name=repo_name,
                        branch=branch,
                        config=protection_config,
                    )
            
            # If workflow is "Git Flow", apply main's protection config to develop
            if is_git_flow and main_protection_config:
                try:
                    logger.info("Applying main branch protection to develop branch (Git Flow)...")
                    self.client.protect_branch(
                        repo_name=repo_name,
                        branch="develop",
                        config=main_protection_config,
                    )
                    logger.info("Develop branch protected with same restrictions as main")
                except Exception as e:
                    logger.warning(f"Could not apply protection to develop branch for Git Flow: {e}")
                    # Continue execution even if this fails

            # Remove admin permission from the authenticated user (local user)
            # This ensures the user who created the repo doesn't retain admin access
            # This must be done last, after all other operations
            try:
                print("repo_name: ", repo_name)
                
                self.client.remove_collaborator_admin_permission(
                    repo_name=repo_name
                )
            except Exception as e:
                logger.warning(f"Could not remove admin permission from authenticated user: {e}")
                # Continue execution even if this fails

            logger.info("GitHub configuration completed successfully")
        except Exception as e:
            logger.error(f"Error processing GitHub configuration: {e}")
            raise

