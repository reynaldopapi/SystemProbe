import json
import os
from datetime import datetime
from PySide6.QtCore import QObject, Signal

class StateManager(QObject):
    state_loaded = Signal()
    state_cleared = Signal()
    prompt_history_updated = Signal()

    def __init__(self):
        super().__init__()
        self.clear_state()

    def clear_state(self):
        self._session_state = {
            "userInputExamples": [],
            "desiredOutputExamples": [],
            "promptHistory": [],
            "currentSystemPrompt": "You are a helpful assistant.", # Default initial prompt
            "finalSystemPrompt": None,
            "currentWorkflowStep": "home", # Identifier for the active screen/step
            "optionalGuidance": "", # User guidance for refiner
            "lastTesterOutput": "", # Store last output for refiner context
            "lastScore": None, # Store last score for refiner context
            "session_filepath": None # Track the path if saved/loaded
        }
        self.state_cleared.emit()
        print("State cleared.")

    def get_state(self):
        return self._session_state

    def set_state(self, new_state):
        # Basic validation could be added here
        self._session_state = new_state
        self.state_loaded.emit()
        print("State loaded.")

    def update_state(self, key, value):
        if key in self._session_state:
            self._session_state[key] = value
            # Emit specific signals if needed, e.g., for history updates
            if key == 'promptHistory':
                self.prompt_history_updated.emit()
        else:
            print(f"Warning: Attempted to update non-existent state key '{key}'")

    def add_prompt_history_entry(self, entry):
        """Adds a structured entry to the prompt history."""
        required_keys = {'prompt', 'testerOutput', 'score', 'userFeedback', 'refinerAnalysis'}
        if not all(key in entry for key in required_keys):
             print(f"Warning: History entry missing required keys: {entry}")
             # Pad missing keys maybe? Or raise error? For now, just warn.
             for key in required_keys:
                 entry.setdefault(key, None) # Ensure keys exist

        self._session_state['promptHistory'].append(entry)
        self.prompt_history_updated.emit()

    def get_current_prompt(self):
        return self._session_state.get('currentSystemPrompt', '')

    def get_final_prompt(self):
        return self._session_state.get('finalSystemPrompt')

    def get_current_step(self):
        return self._session_state.get('currentWorkflowStep', 'home')

    def set_current_step(self, step_id):
         self.update_state('currentWorkflowStep', step_id)

    def save_session(self, filepath):
        if not filepath:
            return False
        if not filepath.endswith(".systemprobe"):
            filepath += ".systemprobe"

        try:
            self._session_state['session_filepath'] = filepath
            # Make a copy to avoid modifying the live state dict during serialization
            state_to_save = self._session_state.copy()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state_to_save, f, indent=4)
            print(f"Session saved to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving session to {filepath}: {e}")
            self._session_state['session_filepath'] = None # Reset on failure
            return False

    def load_session(self, filepath):
        if not filepath or not os.path.exists(filepath):
            print(f"Error: Session file not found at {filepath}")
            return False
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_state = json.load(f)

            # Basic validation of loaded state keys could go here
            required_top_keys = self._session_state.keys()
            if not all(key in loaded_state for key in required_top_keys):
                print("Error: Loaded session file has missing keys. Load aborted.")
                return False

            self.set_state(loaded_state) # Overwrite current state
            self._session_state['session_filepath'] = filepath # Ensure path is stored
            print(f"Session loaded from {filepath}")
            self.state_loaded.emit() # Notify UI to update
            return True
        except Exception as e:
            print(f"Error loading session from {filepath}: {e}")
            return False

    # --- Getters for specific state elements needed by UI ---
    def get_user_input_examples(self): return "\n---\n".join(self._session_state.get("userInputExamples", []))
    def get_desired_output_examples(self): return "\n---\n".join(self._session_state.get("desiredOutputExamples", []))
    def get_optional_guidance(self): return self._session_state.get("optionalGuidance", "")
    def get_last_tester_output(self): return self._session_state.get("lastTesterOutput", "")
    def get_last_score(self): return self._session_state.get("lastScore", 5) # Default score display

    # --- Setters that parse UI input ---
    def set_user_input_examples(self, text): self.update_state("userInputExamples", [ex.strip() for ex in text.split("\n---\n") if ex.strip()])
    def set_desired_output_examples(self, text): self.update_state("desiredOutputExamples", [ex.strip() for ex in text.split("\n---\n") if ex.strip()])
    def set_initial_prompt(self, text): self.update_state("currentSystemPrompt", text.strip())
    def set_current_prompt(self, text): self.update_state("currentSystemPrompt", text.strip())
    def set_final_prompt(self, text): self.update_state("finalSystemPrompt", text.strip())
    def set_optional_guidance(self, text): self.update_state("optionalGuidance", text.strip())
    def set_last_tester_output(self, text): self.update_state("lastTesterOutput", text)
    def set_last_score(self, score): self.update_state("lastScore", score)