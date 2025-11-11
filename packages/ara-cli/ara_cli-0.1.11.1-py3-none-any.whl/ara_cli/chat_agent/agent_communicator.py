import re
import queue


class AgentCommunicator:
    def __init__(self, agent_process_manager):
        self.agent_process_manager = agent_process_manager
        self.agent_process = agent_process_manager.agent_process
        self.agent_output_queue = agent_process_manager.agent_output_queue
        self.chat_instance = agent_process_manager.chat_instance
        self.status_manager = agent_process_manager.status_manager

    def read_agent_output(self):
        try:
            for line in iter(self.agent_process.stdout.readline, ""):
                if not line:
                    break
                self.agent_output_queue.put(line)
        except Exception as e:
            self.agent_output_queue.put(f"Error reading agent output: {e}\n")

    def _handle_agent_answer(self, lines, answer_index):
        for j in range(answer_index + 1, len(lines) - 1):
            print(lines[j], flush=True)
        print(flush=True)

        self.agent_process_manager.agent_mode = True
        self.chat_instance.prompt = "ara-agent> "
        self.status_manager.update_status_file(mode="waiting for input")

    def _process_lines(self, lines):
        for i, line_text in enumerate(lines[:-1]):
            print(line_text, flush=True)
            if re.match(r'^\s*Answer:', line_text):
                self._handle_agent_answer(lines, i)
                return True, lines[-1]
        return False, lines[-1]

    def process_agent_output(self):
        buffer = ""
        while True:
            try:
                line = self.agent_output_queue.get(timeout=0.1)
                buffer += line

                if "\n" in buffer:
                    lines = buffer.split("\n")
                    found_answer, buffer = self._process_lines(lines)
                    if found_answer:
                        return

            except queue.Empty:
                if self.agent_process and self.agent_process.poll() is not None:
                    if buffer:
                        print(buffer, flush=True)
                    self.agent_process_manager.cleanup_agent_process()
                    return
                continue
            except Exception as e:
                print(f"Error processing agent output: {e}", flush=True)
                self.agent_process_manager.cleanup_agent_process()
                return
