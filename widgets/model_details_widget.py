from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QComboBox, QPushButton
from PySide6.QtCore import Signal, Qt, QThread
from workers import Worker

class ModelDetailsWidget(QWidget):
    model_updated = Signal(str)  # Signal emitted when model is changed

    def __init__(self, settings_manager, llm_handler, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.llm_handler = llm_handler
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Model selection form
        form_layout = QFormLayout()

        # Model selector
        self.model_combo = QComboBox()
        self.populate_model_combo()
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        form_layout.addRow("LLM Model:", self.model_combo)

        # Update models button
        self.update_models_button = QPushButton("Update Model List from API")
        self.update_models_button.clicked.connect(self.update_model_list)
        form_layout.addRow("", self.update_models_button)

        # Model details
        self.context_window_label = QLabel("Context Window: Unknown")
        form_layout.addRow("", self.context_window_label)

        self.owner_label = QLabel("Owner: Unknown")
        form_layout.addRow("", self.owner_label)

        self.temperature_label = QLabel("Temperature: 0.7")  # Default value
        form_layout.addRow("", self.temperature_label)

        layout.addLayout(form_layout)
        self.setLayout(layout)

        # Update model details for current model
        self.update_model_details(self.settings_manager.get_llm_model())

    def populate_model_combo(self):
        """Populate the model combo box with available models"""
        self.model_combo.clear()

        # Check if we should use API models or default models
        if self.settings_manager.get_use_api_models():
            # Use stored API models
            models = self.settings_manager.get_model_list()
            if models:
                for model in models:
                    self.model_combo.addItem(model.get("id", ""))
            else:
                # Fall back to default models if no API models are stored
                for model in self.llm_handler.default_models:
                    self.model_combo.addItem(model)
        else:
            # Use default models
            for model in self.llm_handler.default_models:
                self.model_combo.addItem(model)

        # Set current model
        current_model = self.settings_manager.get_llm_model()
        index = self.model_combo.findText(current_model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)

    def update_model_list(self):
        """Fetch models from the API and update the combo box"""
        self.update_models_button.setEnabled(False)
        self.update_models_button.setText("Updating models...")

        # Create a worker to fetch models in the background
        self.worker = Worker(self.llm_handler.fetch_available_models)
        self.worker.signals.result.connect(self.on_models_fetched)
        self.worker.signals.error.connect(self.on_models_fetch_error)
        self.worker.signals.finished.connect(self.on_worker_finished)
        self.worker.start()

    def on_models_fetched(self, models):
        """Handle fetched models from the API"""
        if models:
            # Store models in settings
            self.settings_manager.set_model_list(models)
            self.settings_manager.set_use_api_models(True)

            # Update the combo box
            self.model_combo.clear()
            for model in models:
                self.model_combo.addItem(model.get("id", ""))

            # Set current model
            current_model = self.settings_manager.get_llm_model()
            index = self.model_combo.findText(current_model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)

            # Update button text
            self.update_models_button.setText(f"Update Model List ({len(models)} models)")
        else:
            self.update_models_button.setText("Update Failed - Try Again")

    def on_models_fetch_error(self, error_info):
        """Handle error when fetching models"""
        self.update_models_button.setText("Update Failed - Try Again")
        print(f"Error fetching models: {error_info}")

    def on_worker_finished(self):
        """Handle worker thread completion"""
        self.update_models_button.setEnabled(True)
        # Ensure the worker is properly cleaned up
        if hasattr(self, 'worker') and self.worker is not None:
            self.worker.setParent(None)  # Detach from parent
            self.worker = None

    def on_model_changed(self, model_name):
        """Handle model selection change"""
        if model_name:
            self.settings_manager.set_llm_model(model_name)
            self.update_model_details(model_name)
            self.model_updated.emit(model_name)

    def update_model_details(self, model_name):
        """Update the displayed model details"""
        # First check if we have cached details
        details = self.settings_manager.get_model_details(model_name)

        if details:
            # Use cached details
            self.display_model_details(details)
        else:
            # Try to fetch details from API
            if self.settings_manager.get_use_api_models():
                self.details_worker = Worker(self.llm_handler.get_model_details, model_name)
                self.details_worker.signals.result.connect(self.on_model_details_fetched)
                self.details_worker.signals.error.connect(self.on_details_fetch_error)
                self.details_worker.signals.finished.connect(self.on_details_worker_finished)
                self.details_worker.start()
            else:
                # Just show basic info for default models
                self.context_window_label.setText("Context Window: Unknown")
                self.owner_label.setText("Owner: Unknown")
                self.temperature_label.setText("Temperature: 0.7")  # Default value

    def on_model_details_fetched(self, details):
        """Handle fetched model details"""
        if details:
            # Cache the details
            model_id = details.get("id", "")
            if model_id:
                self.settings_manager.set_model_details(model_id, details)

            # Display the details
            self.display_model_details(details)

    def on_details_fetch_error(self, error_info):
        """Handle error when fetching model details"""
        print(f"Error fetching model details: {error_info}")

    def on_details_worker_finished(self):
        """Handle details worker thread completion"""
        # Ensure the worker is properly cleaned up
        if hasattr(self, 'details_worker') and self.details_worker is not None:
            self.details_worker.setParent(None)  # Detach from parent
            self.details_worker = None

    def display_model_details(self, details):
        """Display model details in the UI"""
        context_window = details.get("context_window", "Unknown")
        owner = details.get("owned_by", "Unknown")

        self.context_window_label.setText(f"Context Window: {context_window}")
        self.owner_label.setText(f"Owner: {owner}")
        self.temperature_label.setText("Temperature: 0.7")  # Default value, could be configurable
