from PySide6.QtWidgets import QWidget

class BaseScreen(QWidget):
    """Base class for all screens to handle common functionalities like state loading/saving."""
    def __init__(self, main_window, state_manager, settings_manager, llm_handler):
        super().__init__()
        self.main_window = main_window
        self.state_manager = state_manager
        self.settings_manager = settings_manager
        self.llm_handler = llm_handler

    def enter_screen(self):
        """Called when the screen becomes active. Load state here."""
        self.load_state()
        print(f"Entering screen: {self.__class__.__name__}")

    def leave_screen(self):
        """Called when navigating away. Save state here."""
        self.save_state()
        print(f"Leaving screen: {self.__class__.__name__}")

    def load_state(self):
        """Load data from state_manager into UI elements. Implement in subclasses."""
        pass

    def save_state(self):
        """Save data from UI elements into state_manager. Implement in subclasses."""
        pass

    def update_status(self, message):
        """Helper to show message in main window status bar."""
        if self.main_window:
            self.main_window.update_status_bar(message)

    def show_error(self, title, message):
        """Helper to show error message box."""
        if self.main_window:
            self.main_window.show_error_message(title, message)