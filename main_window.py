from PySide6.QtWidgets import (QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QApplication,
                               QMenuBar, QStatusBar, QFileDialog, QMessageBox, QDialog)
from PySide6.QtGui import QAction, QPalette, QColor, QIcon # Assuming you might add icons later
from PySide6.QtCore import Slot, Qt

# Import screen classes and managers
from screens import (HomeScreen, InputConfigScreen, InitialPromptScreen,
                     OutputTestingScreen, RefinementScreen, FinalPromptScreen,
                     SettingsDialog)
from state_manager import StateManager
# SettingsManager passed in constructor
from llm_integration.groq_handler import GroqHandler
import os

class MainWindow(QMainWindow):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.state_manager = StateManager()
        self.llm_handler = GroqHandler(self.settings_manager) # Pass settings manager

        self.setWindowTitle("SystemProbe")
        self.setMinimumSize(800, 600) # Reasonable default size

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0,0,0,0) # Use full window space

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.screens = {} # Dictionary to hold screen instances

        self._create_screens()
        self._create_menu_bar()
        self._create_status_bar()

        # Connect state manager signals
        self.state_manager.state_loaded.connect(self._on_state_loaded)
        self.state_manager.state_cleared.connect(lambda: self.navigate_to("home")) # Go home on clear

        # Initial navigation
        self.navigate_to("home")

    def _create_screens(self):
        # Instantiate each screen and add it to the stacked widget and screens dict
        screen_classes = {
            "home": HomeScreen,
            "input_config": InputConfigScreen,
            "initial_prompt": InitialPromptScreen,
            "output_testing": OutputTestingScreen,
            "refinement": RefinementScreen,
            "final_prompt": FinalPromptScreen
        }

        for name, ScreenClass in screen_classes.items():
            screen_instance = ScreenClass(self, self.state_manager, self.settings_manager, self.llm_handler)
            self.stacked_widget.addWidget(screen_instance)
            self.screens[name] = screen_instance

    def _create_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # --- File Menu ---
        file_menu = self.menu_bar.addMenu("&File")

        new_action = QAction("&New Workflow", self)
        new_action.triggered.connect(self.new_workflow_action)
        file_menu.addAction(new_action)

        load_action = QAction("&Load Session...", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_session_action)
        file_menu.addAction(load_action)

        save_action = QAction("&Save Session", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_session_action)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Session &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_session_as_action)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_prompt_action = QAction("&Export Final Prompt (.txt)...", self)
        export_prompt_action.triggered.connect(self.export_final_prompt_action)
        file_menu.addAction(export_prompt_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close) # Default QMainWindow close
        file_menu.addAction(exit_action)

        # --- Settings Menu ---
        settings_menu = self.menu_bar.addMenu("&Settings")

        configure_api_action = QAction("&API Key / Settings...", self)
        configure_api_action.triggered.connect(self.open_settings_dialog)
        settings_menu.addAction(configure_api_action)

        # Theme toggle might be better handled directly in settings dialog now
        # theme_menu = settings_menu.addMenu("&Theme")
        # self.dark_theme_action = QAction("Dark", self, checkable=True)
        # self.dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        # self.light_theme_action = QAction("Light", self, checkable=True)
        # self.light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        # theme_group = QActionGroup(self)
        # theme_group.addAction(self.dark_theme_action)
        # theme_group.addAction(self.light_theme_action)
        # theme_menu.addAction(self.dark_theme_action)
        # theme_menu.addAction(self.light_theme_action)
        # self.update_theme_actions() # Set initial check state

        # --- Help Menu ---
        help_menu = self.menu_bar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        # Add View Documentation action if needed (link to README or web docs)
        # doc_action = QAction("View &Documentation", self)
        # doc_action.triggered.connect(self.show_documentation)
        # help_menu.addAction(doc_action)


    def _create_status_bar(self):
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready.")

    @Slot(str)
    def update_status_bar(self, message):
        self.status_bar.showMessage(message, 5000) # Show for 5 seconds unless updated

    def navigate_to(self, screen_name):
        if screen_name in self.screens:
            current_widget = self.stacked_widget.currentWidget()
            if hasattr(current_widget, 'leave_screen'):
                 current_widget.leave_screen() # Call leave method on old screen

            new_widget = self.screens[screen_name]
            self.stacked_widget.setCurrentWidget(new_widget)

            if hasattr(new_widget, 'enter_screen'):
                 new_widget.enter_screen() # Call enter method on new screen

        else:
            print(f"Error: Screen '{screen_name}' not found.")

    def apply_theme(self, theme_name):
        app = QApplication.instance()
        if theme_name == "dark":
            # Basic Dark Theme using QPalette
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
            dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
            dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

            # Set disabled colors explicitly
            dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
            dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
            dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))

            app.setPalette(dark_palette)
            # Apply stylesheet for finer control over styling
            app.setStyleSheet("""
                QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }

                /* Button styling for dark mode */
                QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px 15px;
                }

                QPushButton:hover {
                    background-color: #4a4a4a;
                    border: 1px solid #666666;
                }

                QPushButton:pressed {
                    background-color: #2a82da;
                }

                QPushButton:disabled {
                    background-color: #2d2d2d;
                    color: #777777;
                    border: 1px solid #444444;
                }

                /* Menu styling for dark mode */
                QMenuBar {
                    background-color: #353535;
                    color: white;
                }

                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 10px;
                }

                QMenuBar::item:selected {
                    background-color: #4a4a4a;
                }

                QMenuBar::item:pressed {
                    background-color: #2a82da;
                }

                QMenu {
                    background-color: #353535;
                    color: white;
                    border: 1px solid #555555;
                }

                QMenu::item {
                    padding: 5px 30px 5px 20px;
                }

                QMenu::item:selected {
                    background-color: #4a4a4a;
                }

                QMenu::separator {
                    height: 1px;
                    background-color: #555555;
                    margin: 5px 0px;
                }

                /* Additional UI elements styling */
                QStatusBar {
                    background-color: #353535;
                    color: white;
                    border-top: 1px solid #555555;
                }

                QComboBox {
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 3px 5px;
                }

                QComboBox:hover {
                    background-color: #4a4a4a;
                }

                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 15px;
                    border-left: 1px solid #555555;
                }

                QComboBox QAbstractItemView {
                    background-color: #353535;
                    color: white;
                    selection-background-color: #4a4a4a;
                    selection-color: white;
                    border: 1px solid #555555;
                }

                QLineEdit, QTextEdit, QTextBrowser {
                    background-color: #2a2a2a;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 3px;
                }

                QSlider::groove:horizontal {
                    border: 1px solid #555555;
                    height: 8px;
                    background: #2a2a2a;
                    margin: 2px 0;
                    border-radius: 4px;
                }

                QSlider::handle:horizontal {
                    background: #2a82da;
                    border: 1px solid #2a82da;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 9px;
                }

                QSlider::handle:horizontal:hover {
                    background: #3a92ea;
                    border: 1px solid #3a92ea;
                }

                /* Group Box styling */
                QGroupBox {
                    border: 1px solid #555555;
                    border-radius: 5px;
                    margin-top: 1.5ex;
                    color: white;
                    font-weight: bold;
                }

                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                    color: white;
                }

                QLabel {
                    color: white;
                }

                /* Dialog styling */
                QDialog, QMessageBox {
                    background-color: #353535;
                    color: white;
                }

                QDialog QLabel, QMessageBox QLabel {
                    color: white;
                }

                QDialog QPushButton, QMessageBox QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px 15px;
                }

                QDialog QPushButton:hover, QMessageBox QPushButton:hover {
                    background-color: #4a4a4a;
                    border: 1px solid #666666;
                }

                QDialog QPushButton:pressed, QMessageBox QPushButton:pressed {
                    background-color: #2a82da;
                }

                QDialog QTextBrowser, QMessageBox QTextBrowser {
                    background-color: #2a2a2a;
                    color: white;
                    border: 1px solid #555555;
                }
            """)
        else: # Light theme
            app.setPalette(app.style().standardPalette()) # Revert to default light style
            # Apply minimal stylesheet for consistent styling in light mode
            app.setStyleSheet("""
                QPushButton {
                    border-radius: 4px;
                    padding: 5px 15px;
                }

                QPushButton:hover {
                    background-color: #e6e6e6;
                }

                QPushButton:pressed {
                    background-color: #2a82da;
                    color: white;
                }

                /* Menu styling for light mode */
                QMenuBar {
                    background-color: #f0f0f0;
                }

                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                }

                QMenuBar::item:pressed {
                    background-color: #2a82da;
                    color: white;
                }

                QMenu::item:selected {
                    background-color: #e0e0e0;
                }

                /* Additional UI elements styling for light mode */
                QComboBox {
                    border: 1px solid #c0c0c0;
                    border-radius: 3px;
                    padding: 3px 5px;
                }

                QComboBox:hover {
                    background-color: #e6e6e6;
                }

                QLineEdit, QTextEdit, QTextBrowser {
                    border: 1px solid #c0c0c0;
                    border-radius: 3px;
                    padding: 3px;
                    background-color: white;
                }

                QSlider::groove:horizontal {
                    border: 1px solid #c0c0c0;
                    height: 8px;
                    background: #f0f0f0;
                    margin: 2px 0;
                    border-radius: 4px;
                }

                QSlider::handle:horizontal {
                    background: #2a82da;
                    border: 1px solid #2a82da;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 9px;
                }

                QSlider::handle:horizontal:hover {
                    background: #3a92ea;
                    border: 1px solid #3a92ea;
                }

                /* Group Box styling for light mode */
                QGroupBox {
                    border: 1px solid #c0c0c0;
                    border-radius: 5px;
                    margin-top: 1.5ex;
                    font-weight: bold;
                }

                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                }
            """)

        self.settings_manager.set_theme(theme_name)
        # self.update_theme_actions()


    # def update_theme_actions(self):
    #     current_theme = self.settings_manager.get_theme()
    #     if current_theme == "dark":
    #         self.dark_theme_action.setChecked(True)
    #     else:
    #         self.light_theme_action.setChecked(True)

    # --- Action Methods ---
    def new_workflow_action(self):
         # Confirm if unsaved changes exist
        current_step = self.state_manager.get_current_step()
        if current_step != "home": # Check if we are in the middle of something
            # Create a custom confirmation dialog to ensure it follows the theme
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setWindowTitle("Start New Workflow?")
            msg_box.setText("Are you sure you want to start a new workflow? Any unsaved progress will be lost.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)

            # Apply current theme
            self._apply_theme_to_dialog(msg_box)

            reply = msg_box.exec()
            if reply == QMessageBox.StandardButton.No:
                return
        self.state_manager.clear_state() # Clears state and signal navigates home

    def load_session_action(self):
        # Confirm if unsaved changes exist first
        # ... (add similar confirmation as new_workflow_action if needed) ...

        # Create a file dialog and apply theme
        file_dialog = QFileDialog(self, "Load Session")
        file_dialog.setNameFilter("SystemProbe Session (*.systemprobe)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        self._apply_theme_to_dialog(file_dialog)

        if file_dialog.exec():
            filepath = file_dialog.selectedFiles()[0]
            if self.state_manager.load_session(filepath):
                self.update_status_bar(f"Session loaded: {filepath}")
                # _on_state_loaded handles navigation
            else:
                self.show_error_message("Load Error", f"Failed to load session file: {filepath}")

    def save_session_action(self):
        current_filepath = self.state_manager.get_state().get("session_filepath")
        if current_filepath:
            if self.state_manager.save_session(current_filepath):
                self.update_status_bar(f"Session saved: {current_filepath}")
            else:
                 self.show_error_message("Save Error", f"Failed to save session to {current_filepath}")
        else:
            self.save_session_as_action() # Prompt for path if not saved before

    def save_session_as_action(self):
        # Create a file dialog and apply theme
        file_dialog = QFileDialog(self, "Save Session As")
        file_dialog.setNameFilter("SystemProbe Session (*.systemprobe)")
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        self._apply_theme_to_dialog(file_dialog)

        if file_dialog.exec():
            filepath = file_dialog.selectedFiles()[0]
            if self.state_manager.save_session(filepath):
                 self.update_status_bar(f"Session saved: {filepath}")
            else:
                 self.show_error_message("Save Error", f"Failed to save session to {filepath}")


    def export_final_prompt_action(self):
        # This might be better handled by the final screen, but can be triggered here too
        if self.state_manager.get_current_step() == "final_prompt":
             final_screen = self.screens.get("final_prompt")
             if final_screen:
                 final_screen.save_prompt()
             else:
                  self.show_error_message("Error", "Final Prompt screen not accessible.")
        else:
            # Or allow exporting even if not on the final screen?
            final_prompt = self.state_manager.get_final_prompt()
            if not final_prompt:
                self.show_error_message("Nothing to Export", "No final prompt has been accepted in the current session.")
                return

            # Create a file dialog and apply theme
            file_dialog = QFileDialog(self, "Export Final Prompt")
            file_dialog.setNameFilter("Text Files (*.txt)")
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            file_dialog.selectFile("final_system_prompt.txt")
            self._apply_theme_to_dialog(file_dialog)

            if file_dialog.exec():
                filepath = file_dialog.selectedFiles()[0]
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(final_prompt)
                    self.update_status_bar(f"Final prompt exported to {filepath}")
                except Exception as e:
                    self.show_error_message("Export Error", f"Failed to export prompt: {e}")


    def open_settings_dialog(self):
        dialog = SettingsDialog(self.settings_manager, self)
        # Apply current theme to the dialog
        self._apply_theme_to_dialog(dialog)
        dialog.exec() # exec_() is deprecated

    @Slot()
    def settings_updated(self):
        """Called when settings dialog is accepted."""
        print("Settings updated.")
        # Re-apply theme immediately
        self.apply_theme(self.settings_manager.get_theme())
        # Re-initialize LLM handler if API key or model changed
        self.llm_handler.update_api_key() # GroqHandler needs this method
        self.update_status_bar("Settings updated. Theme applied. LLM client re-initialized.")

    def show_about_dialog(self):
        about_text = """
        <b>SystemProbe</b> - Version 0.1.0 (Generated)
        <p>AI-Powered System Prompt Optimization Tool</p>
        <p>This application helps refine LLM system prompts through an iterative dual-LLM process, based on user examples and feedback.</p>
        <p>Developed according to the Zero Source methodology.</p>
        <p>(c) 2024 Your Name/Org (as per LICENSE)</p>
        """

        # Create a custom about dialog to ensure it follows the theme
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About SystemProbe")
        msg_box.setText(about_text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Apply current theme
        self._apply_theme_to_dialog(msg_box)

        msg_box.exec()


    @Slot()
    def _on_state_loaded(self):
        """Called after state is successfully loaded from file or cleared."""
        # Navigate to the step saved in the state
        step_to_load = self.state_manager.get_current_step()
        if step_to_load in self.screens:
            print(f"Restoring to step: {step_to_load}")
            self.navigate_to(step_to_load)
        else:
            print(f"Warning: Invalid step '{step_to_load}' found in state. Navigating home.")
            self.navigate_to("home")
        # Update window title if session file is loaded
        session_path = self.state_manager.get_state().get("session_filepath")
        if session_path:
             self.setWindowTitle(f"SystemProbe - {os.path.basename(session_path)}")
        else:
             self.setWindowTitle("SystemProbe")


    def _apply_theme_to_dialog(self, dialog):
        """Helper method to apply the current theme to a dialog."""
        if self.settings_manager.get_theme() == "dark":
            dialog.setStyleSheet("""
                QDialog, QMessageBox, QFileDialog {
                    background-color: #353535;
                    color: white;
                }
                QLabel {
                    color: white;
                }
                QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QLineEdit {
                    background-color: #2a2a2a;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 3px;
                }
            """)
        return dialog

    @Slot(str, str)
    def show_error_message(self, title, message):
        # Create a custom message box to ensure it follows the theme
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Apply current theme
        self._apply_theme_to_dialog(msg_box)

        msg_box.exec()

    def closeEvent(self, event):
        # Add confirmation for unsaved changes before closing
        # ... (Logic to check if state is dirty compared to last save) ...
        # For now, just accept close
        # reply = QMessageBox.question(self, 'Quit', 'Are you sure you want to quit?',
        #                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        #                              QMessageBox.StandardButton.No)
        # if reply == QMessageBox.StandardButton.Yes:
        #     event.accept()
        # else:
        #     event.ignore()
        print("Closing application.")
        event.accept()