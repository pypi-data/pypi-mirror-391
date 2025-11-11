from ara_cli.chat_agent.agent_workspace_manager import AgentWorkspaceManager
from ara_cli.error_handler import AraError, ErrorLevel
from ara_cli.chat_agent.agent_status_manager import AgentStatusManager
from ara_cli.chat_agent.agent_communicator import AgentCommunicator
import os
import subprocess
import threading
import psutil
import queue


class AgentProcessManager:
    _instance = None

    def __new__(cls, chat_instance=None):
        if cls._instance is None:
            cls._instance = super(AgentProcessManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, chat_instance=None):
        if hasattr(self, "_initialized") and self._initialized:
            if chat_instance:
                self.chat_instance = chat_instance
            return
        if chat_instance is None:
            raise ValueError(
                "chat_instance must be provided for the first instantiation"
            )

        self.chat_instance = chat_instance
        self.agent_process = None
        self.agent_reader_thread = None
        self.agent_output_queue = queue.Queue()
        self.agent_mode = False
        self.agent_name = None
        self.status_manager = AgentStatusManager()
        self._initialized = True

    def cleanup_agent_process(self):
        pid = self.status_manager.get_agent_pid()
        if pid and psutil.pid_exists(pid):
            try:
                p = psutil.Process(pid)
                p.terminate()
                p.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass

        self.status_manager.clear_status()

        if self.agent_process:
            try:
                self.agent_process.terminate()
            except:
                pass
            self.agent_process = None

        if self.agent_reader_thread and self.agent_reader_thread.is_alive():
            self.agent_reader_thread = None

        self.agent_mode = False
        self.agent_name = None
        if hasattr(self, "chat_instance"):
            self.chat_instance.prompt = "ara> "

    def start_agent(
        self, agent_name, initial_prompt, artefact_classifier=None, artefact_name=None
    ):
        if self.get_agent_status() != "No agent is currently running.":
            raise AraError(
                "An agent is already running. Use AGENT_STOP to stop it first."
            )

        if agent_name not in self.chat_instance.AVAILABLE_AGENTS:
            raise AraError(f"Unknown agent: {agent_name}")

        base_work_dir = AgentWorkspaceManager.determine_base_work_dir(
            self.chat_instance
        )
        agent_workspace_dir = AgentWorkspaceManager.determine_agent_workspace(
            self.chat_instance, artefact_classifier, artefact_name
        )

        cmd = [
            "ara-agents",
            agent_name,
            "-u",
            initial_prompt,
            "-g",
            "roundrobin",
            "-b",
            ".",
            "-s",
        ]

        if artefact_classifier and artefact_name:
            try:
                artefact_path = self._find_artefact_path(
                    artefact_classifier, artefact_name
                )
                cmd.extend(["-r", artefact_path])
                print(f"Starting {agent_name} with artefact: {artefact_path}")
                print(f"Base work directory: {base_work_dir}")
                print(f"Agent logs directory: {agent_workspace_dir}")
            except AraError as e:
                raise AraError(f"Error: {e}")
        else:
            print(f"Starting {agent_name}...")
            print(f"Base work directory: {base_work_dir}")
            print(f"Agent logs directory: {agent_workspace_dir}")

        env = os.environ.copy()
        env["CENTRAL_LOG_PATH"] = os.path.join(
            agent_workspace_dir, "io_context.log")

        try:
            self.agent_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=base_work_dir,
                env=env,
            )
            self.agent_name = agent_name
            self.status_manager.write_status(
                self.agent_process.pid, self.agent_name, "processing"
            )

            communicator = AgentCommunicator(self)
            self.agent_reader_thread = threading.Thread(
                target=communicator.read_agent_output, daemon=True
            )
            self.agent_reader_thread.start()

            print(f"Agent {agent_name} started. Waiting for response...\n")
            communicator.process_agent_output()

        except FileNotFoundError:
            raise AraError(
                "Agent could not started."
                "\nReason: 'ara-agents' command not found. Make sure ara-agents is locally installed.",
                level=ErrorLevel.CRITICAL,
            )
        except Exception as e:
            self.cleanup_agent_process()
            raise AraError(f"Error starting agent: {e}")

    def _find_artefact_path(self, artefact_classifier, artefact_name):
        from ara_cli.classifier import Classifier

        classifier_dir = Classifier.get_sub_directory(artefact_classifier)
        if not classifier_dir:
            raise AraError(f"Unknown classifier: {artefact_classifier}")

        chat_dir = os.path.dirname(self.chat_instance.chat_name)
        ara_dir = os.path.join(chat_dir, "ara", classifier_dir)

        for ext in [artefact_classifier, "md"]:
            artefact_path = os.path.join(ara_dir, f"{artefact_name}.{ext}")
            if os.path.exists(artefact_path):
                return artefact_path

        raise AraError(
            f"Artefact not found: {artefact_name}.{artefact_classifier}")

    def send_to_agent(self, text):
        if not self.agent_process or self.agent_process.poll() is not None:
            print("Error: Agent process is not running")
            self.cleanup_agent_process()
            return

        try:
            self.agent_process.stdin.write(text + "\n")
            self.agent_process.stdin.flush()

            self.agent_mode = False
            self.chat_instance.prompt = "ara> "
            self.status_manager.update_status_file(mode="processing")

            communicator = AgentCommunicator(self)
            communicator.process_agent_output()

        except Exception as e:
            print(f"Error sending to agent: {e}")
            self.cleanup_agent_process()

    def continue_agent(self):
        status = self.get_agent_status()
        if "No agent" in status:
            print("No agent is currently running.")
            return

        if not self.agent_process or self.agent_process.poll() is not None:
            print(
                "AGENT_CONTINUE can only be used from the chat interface that started the agent."
            )
            return

        if not self.agent_mode:
            print("Agent is not waiting for input. Wait for 'ara-agent>' prompt.")
            return

        print("Continuing agent with empty input...")
        self.send_to_agent("")

    def get_agent_status(self):
        return self.status_manager.get_agent_status()
