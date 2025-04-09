from PySide6.QtWidgets import (QVBoxLayout, QLabel, QTextBrowser, QPushButton, QWidget,
                               QHBoxLayout, QFileDialog, QMessageBox, QApplication, QSizePolicy)
from PySide6.QtCore import Qt
from .base_screen import BaseScreen
import os

class FinalPromptScreen(BaseScreen):
    def __init__(self, main_window, state_manager, settings_manager, llm_handler):
        super().__init__(main_window, state_manager, settings_manager, llm_handler)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Step 5: Final Optimized System Prompt")
        title_font = title.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        guidance = QLabel("The system prompt below has been finalized through the refinement process.")
        guidance.setWordWrap(True)
        layout.addWidget(guidance)

        self.prompt_browser = QTextBrowser()
        self.prompt_browser.setAcceptRichText(False) # Display as plain text
        self.prompt_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.prompt_browser)

        button_layout = QHBoxLayout()
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.save_prompt_button = QPushButton("Save Prompt (.txt)")
        self.save_prompt_button.clicked.connect(self.save_prompt)
        self.export_session_button = QPushButton("Export Session (.systemprobe)")
        self.export_session_button.clicked.connect(self.export_session)

        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.save_prompt_button)
        button_layout.addWidget(self.export_session_button)
        layout.addLayout(button_layout)

        self.new_workflow_button = QPushButton("Start New Workflow")
        self.new_workflow_button.clicked.connect(self.start_new_workflow)
        layout.addWidget(self.new_workflow_button, alignment=Qt.AlignmentFlag.AlignCenter)


        self.setLayout(layout)

    def load_state(self):
        final_prompt = self.state_manager.get_final_prompt()
        if final_prompt:
            self.prompt_browser.setPlainText(final_prompt)
            self.update_status("Optimized system prompt ready.")
        else:
            self.prompt_browser.setPlaceholderText("No final prompt accepted yet.")
            self.update_status("Workflow not completed or prompt not accepted.")
            # Disable buttons if no prompt
            self.copy_button.setEnabled(False)
            self.save_prompt_button.setEnabled(False)


    def save_state(self):
        # No state to save from this screen itself
        pass

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.prompt_browser.toPlainText())
        self.update_status("Prompt copied to clipboard.")

    def save_prompt(self):
        prompt_text = self.prompt_browser.toPlainText()
        if not prompt_text:
            self.show_error("Nothing to Save", "There is no final prompt to save.")
            return

        # Suggest a filename based on the session or a default
        suggested_name = "optimized_prompt.txt"
        session_path = self.state_manager.get_state().get("session_filepath")
        if session_path:
            base = os.path.splitext(os.path.basename(session_path))[0]
            suggested_name = f"{base}_final_prompt.txt"

        filepath, _ = QFileDialog.getSaveFileName(self, "Save Final Prompt", suggested_name, "Text Files (*.txt)")

        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(prompt_text)
                self.update_status(f"Prompt saved to {filepath}")
            except Exception as e:
                self.show_error("Save Error", f"Failed to save prompt: {e}")
                self.update_status(f"Error saving prompt: {e}")

    def export_session(self):
        # Use the main window's save action
        self.main_window.save_session_action()

    def start_new_workflow(self):
        # Ask for confirmation if state exists?
        self.state_manager.clear_state()
        self.main_window.navigate_to("home")

    def enter_screen(self):
        super().enter_screen()
        self.state_manager.set_current_step("final_prompt")
        # Re-enable buttons based on loaded state
        has_prompt = bool(self.state_manager.get_final_prompt())
        self.copy_button.setEnabled(has_prompt)
        self.save_prompt_button.setEnabled(has_prompt)
        # Export session button should always be enabled if state exists? Or link to main window logic? Let's enable.
        self.export_session_button.setEnabled(True)