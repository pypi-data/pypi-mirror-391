import os
import glob
from ara_cli.chat_script_runner.script_finder import ScriptFinder

class ScriptLister:
    def __init__(self):
        self.script_finder = ScriptFinder()

    def get_all_scripts(self):
        custom_scripts = self.get_custom_scripts()
        global_scripts = [f"global/{s}" for s in self.get_global_scripts()]
        return custom_scripts + global_scripts

    def get_custom_scripts(self):
        custom_scripts_dir = self.script_finder.get_custom_scripts_dir()
        if not custom_scripts_dir or not os.path.isdir(custom_scripts_dir):
            return []
        return [os.path.basename(f) for f in glob.glob(os.path.join(custom_scripts_dir, "*.py"))]

    def get_global_scripts(self):
        global_scripts_dir = self.script_finder.get_global_scripts_dir()
        if not global_scripts_dir or not os.path.isdir(global_scripts_dir):
            return []
        return [os.path.basename(f) for f in glob.glob(os.path.join(global_scripts_dir, "*.py"))]
