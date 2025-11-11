import os
from ara_cli.ara_config import ConfigManager
from ara_cli.template_manager import TemplatePathManager

class ScriptFinder:
    def __init__(self):
        self.config = ConfigManager.get_config()

    def get_custom_scripts_dir(self):
        return os.path.join(self.config.local_prompt_templates_dir, "custom-scripts")

    def get_global_scripts_dir(self):
        return os.path.join(self.config.local_prompt_templates_dir, "global-scripts")

    def find_script(self, script_name: str) -> str | None:
        if script_name.startswith("global/"):
            script_path = os.path.join(self.get_global_scripts_dir(), script_name.replace("global/", ""))
            if os.path.exists(script_path):
                return script_path
        else:
            script_path = os.path.join(self.get_custom_scripts_dir(), script_name)
            if os.path.exists(script_path):
                return script_path
        return None
