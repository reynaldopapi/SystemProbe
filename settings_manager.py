from PySide6.QtCore import QSettings, QStandardPaths
import os
import json

class SettingsManager:
    def __init__(self):
        # Using QSettings for platform-independent settings storage
        self.settings = QSettings()

    def get_groq_api_key(self):
        # Try environment variable first, then QSettings
        key = os.environ.get('GROQ_API_KEY')
        if key:
            return key
        return self.settings.value("groqApiKey", "")

    def set_groq_api_key(self, key):
        # Note: Storing API keys directly in QSettings might not be sufficiently secure
        # for all use cases. Consider environment variables or system keychain integrations
        # for higher security needs, as mentioned in the README.
        # For simplicity per the likely scope of initial generation, QSettings is used here.
        self.settings.setValue("groqApiKey", key)
        print("API Key updated in settings. Consider restarting if needed by Langchain.")


    def get_theme(self):
        # Default to dark as per README
        return self.settings.value("theme", "dark")

    def set_theme(self, theme):
        if theme in ["dark", "light"]:
            self.settings.setValue("theme", theme)
        else:
            print(f"Warning: Invalid theme '{theme}'. Using default.")
            self.settings.setValue("theme", "dark")

    def get_llm_model(self):
        # Default to model specified in README metadata
        # ZS:LLM_MODEL:QWEN-72B-CHAT (or similar available on Groq)
        # Let's use a known high-capability model available on Groq
        return self.settings.value("llmModel", "llama3-70b-8192") # Updated to a common Groq model

    def set_llm_model(self, model_name):
        self.settings.setValue("llmModel", model_name)

    def get_use_api_models(self):
        # Default to False to avoid unnecessary API calls on startup
        return self.settings.value("useApiModels", False, type=bool)

    def set_use_api_models(self, use_api):
        self.settings.setValue("useApiModels", use_api)

    def get_model_list(self):
        # Get the stored model list or return an empty list
        model_list_json = self.settings.value("modelList", "[]")
        try:
            return json.loads(model_list_json)
        except json.JSONDecodeError:
            print("Error decoding model list JSON, returning empty list")
            return []

    def set_model_list(self, model_list):
        # Store the model list as JSON
        try:
            model_list_json = json.dumps(model_list)
            self.settings.setValue("modelList", model_list_json)
            return True
        except Exception as e:
            print(f"Error storing model list: {e}")
            return False

    def get_model_details(self, model_id):
        # Get stored details for a specific model
        details_json = self.settings.value(f"modelDetails_{model_id}", "{}")
        try:
            return json.loads(details_json)
        except json.JSONDecodeError:
            print(f"Error decoding model details JSON for {model_id}, returning empty dict")
            return {}

    def set_model_details(self, model_id, details):
        # Store details for a specific model
        try:
            details_json = json.dumps(details)
            self.settings.setValue(f"modelDetails_{model_id}", details_json)
            return True
        except Exception as e:
            print(f"Error storing model details for {model_id}: {e}")
            return False

    def get_last_model_update(self):
        # Get the timestamp of the last model list update
        return self.settings.value("lastModelUpdate", 0, type=int)

    def set_last_model_update(self, timestamp):
        # Store the timestamp of the last model list update
        self.settings.setValue("lastModelUpdate", timestamp)

    # Add methods for font size if implementing that accessibility feature
    def get_font_size(self):
        return int(self.settings.value("fontSize", 10)) # Example default size

    def set_font_size(self, size):
        self.settings.setValue("fontSize", size)