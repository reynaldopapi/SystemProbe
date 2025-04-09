import random
from PySide6.QtWidgets import (QVBoxLayout, QLabel, QTextBrowser, QPushButton, QWidget, QTextEdit,
                               QHBoxLayout, QSlider, QMessageBox, QSizePolicy, QGroupBox)
from PySide6.QtCore import Qt, Slot
from .base_screen import BaseScreen
from workers import Worker # Import the worker

class OutputTestingScreen(BaseScreen):
    def __init__(self, main_window, state_manager, settings_manager, llm_handler):
        super().__init__(main_window, state_manager, settings_manager, llm_handler)
        self.worker = None # To hold the QThread worker
        self.current_input_example_used = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Step 3: Test Output and Evaluate")
        title_font = title.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        self.input_used_label = QLabel("Input Used: None")
        self.input_used_label.setWordWrap(True)
        layout.addWidget(self.input_used_label)

        self.output_browser = QTextBrowser()
        self.output_browser.setPlaceholderText("Generating output from Tester LLM (B)...")
        self.output_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.output_browser)

        # --- Evaluation Group ---
        eval_group = QGroupBox("Evaluate Output")
        eval_layout = QVBoxLayout(eval_group)

        score_layout = QHBoxLayout()
        score_label = QLabel("Score (0=Bad, 10=Perfect):")
        self.score_slider = QSlider(Qt.Orientation.Horizontal)
        self.score_slider.setRange(0, 10)
        self.score_slider.setValue(5) # Default score
        self.score_value_label = QLabel(str(self.score_slider.value()))
        self.score_slider.valueChanged.connect(lambda val: self.score_value_label.setText(str(val)))

        score_layout.addWidget(score_label)
        score_layout.addWidget(self.score_slider)
        score_layout.addWidget(self.score_value_label)
        eval_layout.addLayout(score_layout)

        layout.addWidget(eval_group)
        # --- End Evaluation Group ---

        # --- User Guidance Group ---
        guidance_group = QGroupBox("Optional Guidance for Refinement")
        guidance_layout = QVBoxLayout(guidance_group)

        guidance_label = QLabel("Provide specific feedback for the Refiner LLM (e.g., 'be more concise', 'focus on JSON output'). This will be used when you click 'Refine Prompt' to generate suggestions.")
        guidance_label.setWordWrap(True)
        guidance_layout.addWidget(guidance_label)

        self.guidance_edit = QTextEdit()
        self.guidance_edit.setPlaceholderText("Optional: Enter feedback here...")
        self.guidance_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.guidance_edit.setMaximumHeight(150) # Limit height
        guidance_layout.addWidget(self.guidance_edit)

        layout.addWidget(guidance_group)
        # --- End User Guidance Group ---

        layout.setStretchFactor(eval_group, 2) # Give more space to analysis
        layout.setStretchFactor(guidance_group, 1)

        nav_layout = QHBoxLayout()
        self.back_button = QPushButton("Back (Edit Prompt)")
        self.back_button.setToolTip("Go back to edit the prompt that generated this output.")
        self.back_button.clicked.connect(self.go_back)

        self.refine_button = QPushButton("Refine Prompt")
        self.refine_button.setToolTip("Go to refinement screen where you can use your guidance to generate suggestions and reroll results.")
        self.refine_button.clicked.connect(self.refine_prompt)

        self.accept_button = QPushButton("Accept Prompt (Score >= 8 Recommended)")
        self.accept_button.setToolTip("Accept the current system prompt as the final version.")
        self.accept_button.clicked.connect(self.accept_prompt)

        nav_layout.addWidget(self.back_button)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.refine_button)
        nav_layout.addWidget(self.accept_button)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

        # Initially disable buttons until generation is complete
        self.set_buttons_enabled(False)

    def set_buttons_enabled(self, enabled):
        self.back_button.setEnabled(enabled)
        self.refine_button.setEnabled(enabled)
        self.accept_button.setEnabled(enabled)
        self.score_slider.setEnabled(enabled)

    def enter_screen(self):
        super().enter_screen() # Calls load_state
        self.state_manager.set_current_step("output_testing")
        # Trigger LLM B (Tester) call
        self.run_tester_llm()

    def load_state(self):
        # Load the last known score into the slider
        last_score = self.state_manager.get_last_score()
        self.score_slider.setValue(last_score if last_score is not None else 5)
        self.score_value_label.setText(str(self.score_slider.value()))
        # Output browser will be filled by the LLM call result
        self.output_browser.setPlaceholderText("Generating output...")
        self.output_browser.clear() # Clear previous output
        self.input_used_label.setText("Input Used: Preparing...")


    def save_state(self):
        # Save the score when leaving the screen (e.g., when clicking Refine/Accept)
        # We save the output text when the LLM call finishes
        self.state_manager.set_last_score(self.score_slider.value())
        # Save the optional guidance text
        self.state_manager.set_optional_guidance(self.guidance_edit.toPlainText())

    def run_tester_llm(self):
        # Check for API key before proceeding
        if not self.settings_manager.get_groq_api_key():
            self.show_error("API Key Missing", "Groq API key not configured. Please set it in File -> Settings.")
            self.output_browser.setPlaceholderText("API Key Missing. Cannot generate output.")
            self.set_buttons_enabled(True) # Allow navigation back
            self.back_button.setEnabled(True)
            self.refine_button.setEnabled(False) # Can't refine without output
            self.accept_button.setEnabled(False) # Can't accept without output
            return

        self.output_browser.setPlaceholderText("Generating output from Tester LLM (B)...")
        self.update_status("Tester LLM (B): Generating output...")
        self.set_buttons_enabled(False) # Disable buttons during generation

        current_prompt = self.state_manager.get_current_prompt()
        input_examples = self.state_manager.get_state().get("userInputExamples", [])

        # Select an input example (round-robin or random, optional)
        self.current_input_example_used = None
        if input_examples:
             # Simple random selection for demonstration
             self.current_input_example_used = random.choice(input_examples)
             self.input_used_label.setText(f"Input Used:\n```\n{self.current_input_example_used}\n```")
        else:
            self.input_used_label.setText("Input Used: None")


        # --- Setup Worker Thread ---
        self.worker = Worker(self.llm_handler.run_tester_llm, current_prompt, self.current_input_example_used)
        self.worker.signals.result.connect(self.handle_tester_result)
        self.worker.signals.error.connect(self.handle_llm_error)
        self.worker.signals.finished.connect(self.on_worker_finished)
        self.worker.signals.status.connect(self.update_status) # Connect worker status to main status bar
        self.worker.start()
        # --- End Worker Setup ---

    @Slot(object)
    def handle_tester_result(self, output_text):
        self.output_browser.setPlainText(output_text)
        # Save the generated output to state
        self.state_manager.set_last_tester_output(output_text)
        self.update_status("Tester LLM (B): Output received.")

    @Slot(tuple)
    def handle_llm_error(self, error_info):
        exctype, value, tb_str = error_info
        print(f"LLM Error: {value}\n{tb_str}") # Log full traceback
        self.output_browser.setPlaceholderText(f"Error generating output: {value}")
        self.show_error("LLM Error", f"Failed to get response from Tester LLM (B):\n{value}\n\nCheck console log and API key.")
        self.update_status(f"Error: {value}")

    @Slot()
    def on_worker_finished(self):
        self.set_buttons_enabled(True) # Re-enable buttons
        self.worker = None # Clear the worker reference
        self.update_status("Ready for evaluation.") # Update status bar


    def go_back(self):
        # Don't save score if just going back to edit
        # State should still reflect the prompt that *generated* the current output
        self.main_window.navigate_to("initial_prompt") # Or maybe last screen visited? Need state history for that.

    def refine_prompt(self):
        self.leave_screen() # Saves the current score
        self.main_window.navigate_to("refinement")
        # Refinement screen's enter_screen will trigger LLM A

    def accept_prompt(self):
        score = self.score_slider.value()
        if score < 8:
             reply = QMessageBox.question(self, "Accept Prompt?",
                                          f"The current score is {score}/10 (below recommended 8). Are you sure you want to accept this system prompt?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                          QMessageBox.StandardButton.No)
             if reply == QMessageBox.StandardButton.No:
                 return

        final_prompt = self.state_manager.get_current_prompt()
        self.state_manager.set_final_prompt(final_prompt)
        self.leave_screen() # Saves score
        # Add the final accepted step to history before navigating
        history_entry = {
            "prompt": final_prompt,
            "testerOutput": self.state_manager.get_last_tester_output(),
            "score": score,
            "userFeedback": "N/A (Accepted)", # Indicate acceptance
            "refinerAnalysis": "N/A (Accepted)"
        }
        self.state_manager.add_prompt_history_entry(history_entry)

        self.main_window.navigate_to("final_prompt")