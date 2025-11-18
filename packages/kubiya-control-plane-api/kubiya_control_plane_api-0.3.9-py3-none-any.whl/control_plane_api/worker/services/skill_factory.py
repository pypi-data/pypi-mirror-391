"""Skill factory - instantiates skill toolkits from Control Plane configuration"""

from typing import Optional, Any, List
from pathlib import Path
import structlog
import os

from agno.tools.shell import ShellTools
from agno.tools.python import PythonTools
from agno.tools.file import FileTools
from control_plane_api.worker.services.workflow_executor_tools import WorkflowExecutorTools

logger = structlog.get_logger()


class SkillFactory:
    """
    Factory for creating skill toolkit instances from Control Plane skill configurations.

    Centralizes skill instantiation logic that was previously duplicated
    in agent_activities.py and team_activities.py.
    """

    @staticmethod
    def create_skill(skill_data: dict) -> Optional[Any]:
        """
        Create a skill toolkit from Control Plane configuration.

        Args:
            skill_data: Skill config from Control Plane API:
                - type: Skill type (file_system, shell, python, etc.)
                - name: Skill name
                - configuration: Dict with skill-specific config
                - enabled: Whether skill is enabled

        Returns:
            Instantiated skill toolkit or None if disabled/unsupported
        """
        if not skill_data.get("enabled", True):
            logger.info(
                "skill_skipped_disabled",
                skill_name=skill_data.get("name")
            )
            return None

        skill_type = skill_data.get("type", "").lower()
        config = skill_data.get("configuration", {})
        name = skill_data.get("name", "Unknown")

        try:
            # File system tools
            if skill_type in ["file_system", "file", "file_generation"]:
                base_dir = config.get("base_directory", "/workspace")
                return FileTools(base_dir=Path(base_dir))

            # Shell/terminal tools
            elif skill_type in ["shell", "terminal", "bash"]:
                return ShellTools()

            # Python tools
            elif skill_type in ["python", "python_code"]:
                return PythonTools()

            # Workflow executor tools
            elif skill_type in ["workflow_executor", "workflow"]:
                logger.info(
                    "🔍 Creating workflow_executor skill",
                    skill_name=name,
                    skill_type=skill_type,
                )

                # New multi-workflow format
                workflows = config.get("workflows")

                # Legacy single-workflow format
                workflow_type = config.get("workflow_type", "json")
                workflow_definition = config.get("workflow_definition")
                python_dsl_code = config.get("python_dsl_code")

                # Common configuration
                validation_enabled = config.get("validation_enabled", True)
                default_runner = config.get("default_runner")
                timeout = config.get("timeout", 3600)
                default_parameters = config.get("default_parameters")

                # Get Kubiya API credentials from environment
                # These are needed for remote workflow execution
                kubiya_api_key = os.environ.get("KUBIYA_API_KEY")
                kubiya_api_base = os.environ.get("KUBIYA_API_BASE", "https://api.kubiya.ai")

                logger.info(
                    "workflow_executor_config",
                    skill_name=name,
                    has_workflows=bool(workflows),
                    workflows_count=len(workflows) if workflows else 0,
                    has_api_key=bool(kubiya_api_key),
                    api_base=kubiya_api_base,
                )

                if not kubiya_api_key:
                    logger.warning(
                        "workflow_executor_no_api_key",
                        skill_name=name,
                        message="KUBIYA_API_KEY not found - workflow execution will fail"
                    )

                # Get execution_id from skill_data (top level), not config (configuration sub-dict)
                execution_id = skill_data.get('execution_id')
                print(f"\n🔍 SKILL FACTORY DEBUG:")
                print(f"   skill_data keys: {list(skill_data.keys())}")
                print(f"   config (configuration) keys: {list(config.keys())}")
                print(f"   execution_id from skill_data: {execution_id}")
                print(f"   Passing to WorkflowExecutorTools...\n")

                workflow_tool = WorkflowExecutorTools(
                    name=name,  # Pass the skill name from configuration
                    workflows=workflows,
                    workflow_type=workflow_type,
                    workflow_definition=workflow_definition,
                    python_dsl_code=python_dsl_code,
                    validation_enabled=validation_enabled,
                    default_runner=default_runner,
                    timeout=timeout,
                    default_parameters=default_parameters,
                    kubiya_api_key=kubiya_api_key,  # Explicitly pass API key
                    kubiya_api_base=kubiya_api_base,  # Explicitly pass API base URL
                    execution_id=execution_id,  # Pass execution_id for control plane streaming
                )

                logger.info(
                    "✅ Workflow executor skill created successfully",
                    skill_name=name,
                    tool_class=type(workflow_tool).__name__,
                    has_functions=hasattr(workflow_tool, 'functions'),
                    function_count=len(workflow_tool.functions) if hasattr(workflow_tool, 'functions') else 0,
                )

                return workflow_tool

            else:
                logger.warning(
                    "skill_type_not_supported",
                    skill_type=skill_type,
                    skill_name=name
                )
                return None

        except Exception as e:
            logger.error(
                "skill_instantiation_failed",
                skill_type=skill_type,
                skill_name=name,
                error=str(e)
            )
            return None

    @classmethod
    def create_skills_from_list(
        cls,
        skill_configs: List[dict],
        execution_id: Optional[str] = None
    ) -> List[Any]:
        """
        Create multiple skills from a list of configurations.

        Args:
            skill_configs: List of skill config dicts
            execution_id: Optional execution ID to pass to skills

        Returns:
            List of instantiated skills (non-None)
        """
        print(f"\n🔍 SKILL FACTORY - create_skills_from_list CALLED:")
        print(f"   execution_id param: {execution_id}")
        print(f"   type: {type(execution_id)}")
        print(f"   bool(execution_id): {bool(execution_id)}")
        print(f"   skill_configs count: {len(skill_configs)}\n")

        skills = []

        for idx, config in enumerate(skill_configs):
            print(f"\n🔍 Processing skill #{idx + 1}: {config.get('name', 'unknown')}")
            print(f"   Config keys BEFORE injection: {list(config.keys())}")
            print(f"   Config type: {type(config)}")

            # Pass execution_id to skill config if provided
            if execution_id:
                print(f"   ✅ Injecting execution_id: {execution_id}")
                config['execution_id'] = execution_id
                print(f"   Config keys AFTER injection: {list(config.keys())}")
                print(f"   Verify injection: config['execution_id'] = {config.get('execution_id')}")
            else:
                print(f"⚠️  Skipping execution_id injection (execution_id is: {repr(execution_id)})")

            skill = cls.create_skill(config)
            if skill:
                skills.append(skill)

        logger.info(
            "skills_created",
            requested_count=len(skill_configs),
            created_count=len(skills),
            execution_id=execution_id
        )

        return skills
