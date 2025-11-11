from ara_cli.error_handler import AraError

import os


class AgentWorkspaceManager:
    """Manages workspace directories for agent execution."""

    @staticmethod
    def determine_agent_workspace(chat_instance, artefact_classifier=None, artefact_name=None):
        """
        Determines the appropriate workspace directory for agent logs and data.

        Args:
            chat_instance: The Chat instance
            artefact_classifier: Optional artefact classifier (e.g., 'feature')
            artefact_name: Optional artefact name

        Returns:
            str: Absolute path to the agent workspace directory (for logs)
        """
        base_directory = os.path.dirname(chat_instance.chat_name)

        if artefact_classifier and artefact_name:
            # Use artefact-specific workspace for logs
            from ara_cli.classifier import Classifier
            classifier_dir = Classifier.get_sub_directory(artefact_classifier)
            if not classifier_dir:
                raise AraError(f"Unknown classifier: {artefact_classifier}")

            workspace_dir = os.path.join(
                base_directory,
                "ara",
                classifier_dir,
                f"{artefact_name}.data"
            )
        else:
            # Use chat-specific workspace for logs
            chat_name_without_ext = os.path.splitext(
                os.path.basename(chat_instance.chat_name))[0]
            workspace_dir = os.path.join(
                base_directory,
                "ara",
                f"{chat_name_without_ext}"
            )

        # Ensure workspace directory exists
        os.makedirs(workspace_dir, exist_ok=True)
        return os.path.abspath(workspace_dir)

    @staticmethod
    def determine_base_work_dir(chat_instance):
        """
        Determines the base working directory (project root).

        Args:
            chat_instance: The Chat instance

        Returns:
            str: Absolute path to the project root directory
        """

        return os.path.dirname("./")
        # The bwd should be the project root, not inside ara/
        chat_dir = os.path.dirname(chat_instance.chat_name)

        # Find project root by looking for 'ara' directory
        current_dir = chat_dir
        while True:
            if os.path.isdir(os.path.join(current_dir, "ara")):
                return os.path.abspath(current_dir)
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Reached filesystem root
                # Fallback to chat directory if no 'ara' folder found
                return os.path.abspath(chat_dir)
            current_dir = parent_dir
