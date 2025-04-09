from PySide6.QtWidgets import (QVBoxLayout, QLabel, QTextEdit, QPushButton,
                               QWidget, QMessageBox, QSizePolicy, QHBoxLayout)
from PySide6.QtCore import Qt
from .base_screen import BaseScreen

class InputConfigScreen(BaseScreen):
    def __init__(self, main_window, state_manager, settings_manager, llm_handler):
        super().__init__(main_window, state_manager, settings_manager, llm_handler)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Step 1: Define Inputs and Examples")
        title_font = title.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        guidance1 = QLabel("Provide representative dynamic inputs the final prompt should handle (Optional, but recommended context for testing). Separate multiple inputs with '---'.")
        guidance1.setWordWrap(True)
        layout.addWidget(guidance1)

        self.user_input_edit = QTextEdit()
        self.user_input_edit.setPlaceholderText("Example Input 1\n---\nExample Input 2")
        self.user_input_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.user_input_edit)

        guidance2 = QLabel("Provide the corresponding *IDEAL* outputs for the inputs above. These are crucial for the Refiner LLM. At least one example output is required. Separate multiple outputs with '---'.")
        guidance2.setWordWrap(True)
        layout.addWidget(guidance2)

        self.desired_output_edit = QTextEdit()
        self.desired_output_edit.setPlaceholderText("Ideal Output for Example 1\n---\nIdeal Output for Example 2")
        self.desired_output_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.desired_output_edit)

        # Use Expanding size policy for text edits
        layout.setStretchFactor(self.user_input_edit, 1)
        layout.setStretchFactor(self.desired_output_edit, 1)


        nav_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(lambda: self.main_window.navigate_to("home"))
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.proceed)

        nav_layout.addWidget(self.back_button)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.next_button)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def load_state(self):
        self.user_input_edit.setPlainText(self.state_manager.get_user_input_examples())
        self.desired_output_edit.setPlainText(self.state_manager.get_desired_output_examples())
        self.update_status("Define example inputs and desired outputs.")

    def save_state(self):
        self.state_manager.set_user_input_examples(self.user_input_edit.toPlainText())
        self.state_manager.set_desired_output_examples(self.desired_output_edit.toPlainText())

    def validate_input(self):
        desired_outputs = self.desired_output_edit.toPlainText().strip()
        if not desired_outputs or not [o for o in desired_outputs.split('\n---\n') if o.strip()]:
            self.show_error("Input Required", "Please provide at least one desired example output.")
            return False
        # Could add check for matching number of inputs/outputs if both are provided
        return True

    def proceed(self):
        if self.validate_input():
            self.leave_screen() # Saves state
            self.main_window.navigate_to("initial_prompt")

    def enter_screen(self):
        super().enter_screen()
        self.state_manager.set_current_step("input_config")