from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory # Or other suitable memory
from groq import Groq
import re
import os
import json
from typing import List, Dict, Any, Optional

class GroqHandler:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.default_models = [
            "llama3-70b-8192",
            "mixtral-8x7b-32768",
            "llama3-8b-8192",
            "gemma-7b-it"
        ]
        self._initialize_clients()

    def _initialize_clients(self):
        api_key = self.settings_manager.get_groq_api_key()
        model_name = self.settings_manager.get_llm_model()

        if not api_key:
            print("Warning: Groq API Key not found. LLM features will be disabled.")
            self.chat_model = None
            return

        try:
            # ZS:LIBRARY:LANGCHAIN specified
            self.chat_model = ChatGroq(
                temperature=0.7, # Default temperature, might need adjustment
                groq_api_key=api_key,
                model_name=model_name,
                # max_tokens= Can be set if needed
            )
            print(f"Groq client initialized with model: {model_name}")
        except Exception as e:
            print(f"Error initializing Groq client: {e}")
            self.chat_model = None

    def update_api_key(self):
        """Re-initialize the client if the API key changes."""
        self._initialize_clients()

    def fetch_available_models(self, status_callback=None, progress_callback=None) -> Optional[List[Dict[str, Any]]]:
        """Fetch available models from the Groq API.

        Args:
            status_callback: Optional callback function to report status
            progress_callback: Optional callback function to report progress (not used)

        Returns:
            A list of model objects or None if the API call fails
        """
        if status_callback:
            status_callback("Fetching available models from Groq API...")

        api_key = self.settings_manager.get_groq_api_key()
        if not api_key:
            if status_callback:
                status_callback("Error: Groq API Key not found. Cannot fetch models.")
            return None

        try:
            # Create a Groq client
            client = Groq(api_key=api_key)
            # Fetch models
            models_response = client.models.list()

            # Convert to a list of dictionaries for consistent handling
            models_list = []
            for model in models_response.data:
                model_id = model.id if hasattr(model, 'id') else str(model)
                # Skip whisper models
                if "whisper" in model_id.lower():
                    continue

                # Create a dictionary with model details
                model_dict = {
                    "id": model_id,
                    "object": getattr(model, 'object', 'model'),
                    "created": getattr(model, 'created', 0),
                    "owned_by": getattr(model, 'owned_by', 'Unknown'),
                    "context_window": getattr(model, 'context_window', 0),
                }
                models_list.append(model_dict)

            if status_callback:
                status_callback(f"Successfully fetched {len(models_list)} models from Groq API.")

            return models_list
        except Exception as e:
            if status_callback:
                status_callback(f"Error fetching models: {e}")
            print(f"Error fetching models from Groq API: {e}")
            return None

    def get_model_details(self, model_id, status_callback=None, progress_callback=None) -> Optional[Dict[str, Any]]:
        """Get details for a specific model from the Groq API.

        Args:
            model_id: The ID of the model to get details for
            status_callback: Optional callback function to report status
            progress_callback: Optional callback function to report progress (not used)

        Returns:
            A model object or None if the API call fails
        """
        if status_callback:
            status_callback(f"Fetching details for model {model_id}...")

        api_key = self.settings_manager.get_groq_api_key()
        if not api_key:
            if status_callback:
                status_callback("Error: Groq API Key not found. Cannot fetch model details.")
            return None

        try:
            # Create a Groq client
            client = Groq(api_key=api_key)
            # Fetch model details
            model = client.models.retrieve(model_id)

            # Convert to a dictionary for consistent handling
            model_dict = {
                "id": model.id if hasattr(model, 'id') else model_id,
                "object": getattr(model, 'object', 'model'),
                "created": getattr(model, 'created', 0),
                "owned_by": getattr(model, 'owned_by', 'Unknown'),
                "context_window": getattr(model, 'context_window', 0),
            }

            if status_callback:
                status_callback(f"Successfully fetched details for model {model_id}.")

            return model_dict
        except Exception as e:
            if status_callback:
                status_callback(f"Error fetching model details: {e}")
            print(f"Error fetching details for model {model_id}: {e}")
            return None

    def _clean_groq_output(self, text):
        """Removes Groq specific XML tags like <|thinking|> as per README."""
        if not text:
            return ""
        # Basic regex to remove tags like <|tagname|> ... </|tagname|> or self-closing <|tagname|/>
        # This might need refinement based on actual Groq output variations.
        cleaned = re.sub(r'<\|[^>]*?\|>', '', text)
        cleaned = re.sub(r'</\|[^>]*?\|>', '', cleaned) # Handle closing tags if separate
        return cleaned.strip()

    def run_tester_llm(self, system_prompt, user_input=None, **kwargs):
        """
        Runs LLM B (Tester) with the current system prompt.
        kwargs are passed potentially from the worker thread (status_callback etc.)
        """
        status_callback = kwargs.get('status_callback', print) # Get callback from worker

        if not self.chat_model:
            status_callback("Error: Groq client not initialized (check API key).")
            raise ConnectionError("Groq client not initialized.")

        status_callback("Tester LLM: Preparing messages...")
        messages = [SystemMessage(content=system_prompt)]
        if user_input:
            messages.append(HumanMessage(content=f"User Input to consider:\n```\n{user_input}\n```\nPlease generate the output based ONLY on the System Prompt's instructions."))
        else:
             messages.append(HumanMessage(content="Please generate the output based ONLY on the System Prompt's instructions."))

        prompt = ChatPromptTemplate.from_messages(messages)
        chain = prompt | self.chat_model

        try:
            status_callback("Tester LLM: Sending request to Groq...")
            response = chain.invoke({}) # Invoke takes context variables if prompt needs them
            status_callback("Tester LLM: Received response.")
            cleaned_output = self._clean_groq_output(response.content)
            status_callback("Tester LLM: Processing complete.")
            return cleaned_output
        except Exception as e:
            status_callback(f"Tester LLM: Error - {e}")
            print(f"Error during Tester LLM call: {e}")
            # Propagate the error to be shown in the UI
            raise ConnectionError(f"Groq API Error (Tester): {e}")


    def run_refiner_llm(self, context_data, **kwargs):
        """
        Runs LLM A (Refiner) to analyze and suggest a better system prompt.
        context_data should be a dictionary containing all necessary info.
        kwargs are passed potentially from the worker thread (status_callback etc.)
        """
        status_callback = kwargs.get('status_callback', print)

        if not self.chat_model:
             status_callback("Error: Groq client not initialized (check API key).")
             raise ConnectionError("Groq client not initialized.")

        status_callback("Refiner LLM: Preparing context...")

        # Extract context
        initial_goal = "Optimize a system prompt for an LLM." # Could be made more specific if needed
        examples_input = context_data.get('userInputExamples', [])
        examples_output = context_data.get('desiredOutputExamples', [])
        last_prompt = context_data.get('last_prompt', '')
        last_output = context_data.get('last_output', '')
        last_score = context_data.get('last_score', 'N/A')
        user_feedback = context_data.get('user_feedback', '')
        prompt_history = context_data.get('prompt_history', []) # List of dicts

        # Construct the prompt for the Refiner LLM (LLM A)
        # This needs careful crafting based on the README's intent
        refiner_system_prompt = """You are an expert System Prompt Refiner. Your goal is to analyze the performance of a given system prompt and suggest an improved version.
You will be given:
1. The overall goal.
2. Example user inputs and their corresponding *ideal* outputs.
3. The system prompt that was tested (`Tested System Prompt`).
4. The output generated by another LLM using that tested prompt (`Generated Output`).
5. A user's score (0-10, 10=perfect) for the generated output (`User Score`).
6. Optional user feedback or guidance (`User Feedback`).
7. A history of previously attempted prompts and their scores (`Prompt History`) to avoid cycles.

Your task is to:
1. Analyze why the `Generated Output` did or did not meet the requirements defined by the `Ideal Outputs` and the `User Score`.
2. Consider the `User Feedback` for specific directions.
3. Review the `Prompt History` to avoid suggesting prompts that failed previously.
4. Generate a *new, improved* system prompt (`Suggested New System Prompt`) that is more likely to produce the `Ideal Outputs` for the given `Example Inputs`.
5. Provide a brief analysis explaining your reasoning (`Analysis`).

Output Format:
Provide your response ONLY in the following format:

Analysis:
<Your analysis here>

Suggested New System Prompt:
<Your suggested system prompt here>
"""

        # Format the history for the prompt
        history_str = "Previous Attempts:\n"
        if prompt_history:
            for i, entry in enumerate(prompt_history):
                history_str += f"{i+1}. Prompt: '{entry.get('prompt', 'N/A')[:100]}...' Score: {entry.get('score', 'N/A')}\n"
        else:
            history_str += "No previous attempts in this session.\n"

        # Format examples
        examples_str = "Example Input/Output Pairs:\n"
        if examples_input and examples_output and len(examples_input) == len(examples_output):
             for i in range(len(examples_input)):
                 examples_str += f"- Input: {examples_input[i]}\n  Ideal Output: {examples_output[i]}\n"
        elif examples_output: # Only output examples are mandatory per README
             for i, output in enumerate(examples_output):
                 examples_str += f"- Ideal Output {i+1}: {output}\n"
        else:
            examples_str += "No examples provided.\n" # Should be validated earlier but handle defensively

        # Construct the Human Message content
        human_message_content = f"""
Context for Refinement:
------------------------
Overall Goal: {initial_goal}

{examples_str}
------------------------
Last Attempt Details:
Tested System Prompt:
```
{last_prompt}
```
Generated Output:
```
{last_output}
```

User Score: {last_score}/10

User Feedback: {user_feedback if user_feedback else 'None provided.'}
------------------------
{history_str}
------------------------

Based on all the above information, please provide your analysis and the suggested new system prompt in the specified format.
"""
        messages = [
            SystemMessage(content=refiner_system_prompt),
            HumanMessage(content=human_message_content)
        ]

        prompt = ChatPromptTemplate.from_messages(messages)
        chain = prompt | self.chat_model

        try:
            status_callback("Refiner LLM: Sending request to Groq...")
            response = chain.invoke({})
            status_callback("Refiner LLM: Received response.")
            raw_output = response.content
            # Parse the structured output (Analysis and Suggested Prompt)
            analysis = "Analysis not found."
            suggested_prompt = "Suggested prompt not found."

            analysis_match = re.search(r"Analysis:\s*(.*?)\s*Suggested New System Prompt:", raw_output, re.DOTALL | re.IGNORECASE)
            prompt_match = re.search(r"Suggested New System Prompt:\s*(.*)", raw_output, re.DOTALL | re.IGNORECASE)

            if analysis_match:
                analysis = analysis_match.group(1).strip()
            if prompt_match:
                suggested_prompt = prompt_match.group(1).strip()

            # Clean the extracted parts
            cleaned_analysis = self._clean_groq_output(analysis)
            cleaned_suggested_prompt = self._clean_groq_output(suggested_prompt)

            status_callback("Refiner LLM: Processing complete.")
            return {
                "analysis": cleaned_analysis,
                "suggested_prompt": cleaned_suggested_prompt
            }
        except Exception as e:
            status_callback(f"Refiner LLM: Error - {e}")
            print(f"Error during Refiner LLM call: {e}")
            raise ConnectionError(f"Groq API Error (Refiner): {e}")