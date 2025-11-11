import os
import json
import psutil
from ara_cli.directory_navigator import DirectoryNavigator


class AgentStatusManager:
    def get_status_file_path(self):
        ara_root = DirectoryNavigator.find_ara_directory_root()
        if not ara_root:
            return None
        return os.path.join(ara_root, ".araconfig", "agent_status.json")

    def get_agent_pid(self):
        status_file = self.get_status_file_path()
        if not status_file or not os.path.exists(status_file):
            return None

        with open(status_file, "r") as f:
            try:
                status = json.load(f)
                return status.get("pid")
            except json.JSONDecodeError:
                return None

    def update_status_file(self, mode):
        status_file = self.get_status_file_path()
        if not status_file or not os.path.exists(status_file):
            return

        try:
            with open(status_file, "r") as f:
                status = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return

        status["mode"] = mode

        with open(status_file, "w") as f:
            json.dump(status, f)

    def get_agent_status(self):
        status_file = self.get_status_file_path()
        if not status_file or not os.path.exists(status_file):
            return "No agent is currently running."

        with open(status_file, "r") as f:
            try:
                status = json.load(f)
            except json.JSONDecodeError:
                return "No agent is currently running."

        pid = status.get("pid")
        if not pid or not psutil.pid_exists(pid):
            if os.path.exists(status_file):
                os.remove(status_file)
            return "No agent is currently running."

        name = status.get("name")
        mode = status.get("mode")
        return f"Agent: {name} (running - {mode})"

    def write_status(self, pid, name, mode):
        status = {"pid": pid, "name": name, "mode": mode}
        status_file = self.get_status_file_path()
        if status_file:
            with open(status_file, "w") as f:
                json.dump(status, f)

    def clear_status(self):
        status_file = self.get_status_file_path()
        if status_file and os.path.exists(status_file):
            os.remove(status_file)
