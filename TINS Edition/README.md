<!-- Zero Source Specification v1.0 -->
<!-- ZS:PLATFORM:DESKTOP -->
<!-- ZS:LANGUAGE:PYTHON -->
<!-- ZS:GUI:PYSIDE6 -->
<!-- ZS:LLM_API:GROQ -->
<!-- ZS:LLM_MODEL:QWEN-72B-CHAT --> <!-- Using known available model on Groq -->
<!-- ZS:LIBRARY:LANGCHAIN -->
<!-- ZS:COMPLEXITY:HIGH -->

# SystemProbe: AI-Powered System Prompt Optimization

## Description

SystemProbe is a desktop application designed to help users discover the optimal system prompt for interacting with Large Language Models (LLMs) without requiring complex fine-tuning or LoRA training. It guides users through an iterative process of refining a system prompt to achieve desired outputs for dynamic inputs.

The core problem SystemProbe addresses is the difficulty in crafting a single system prompt that consistently guides an LLM to produce outputs matching specific, often nuanced, expectations across various user inputs. SystemProbe employs a unique dual-LLM workflow: one LLM (the "Tester") attempts to fulfill the task using the current system prompt, while another LLM (the "Refiner") analyzes the results and suggests improvements to the system prompt itself. By incorporating user-provided examples, scoring, and explicit feedback, SystemProbe transforms prompt engineering from trial-and-error into a structured, efficient, and insightful optimization process.

The target users are prompt engineers, AI developers, researchers, and anyone needing to elicit specific, consistent behavior from LLMs via system prompts.

## Functionality

### Core Features

1.  **Guided Workflow:** Takes the user step-by-step through the process of defining inputs, providing examples, setting an initial prompt, testing, scoring, refining, and finalizing.
2.  **Input & Example Collection:** Allows users to provide sample dynamic user inputs and corresponding ideal outputs to define the target behavior.
3.  **Initial Prompt Setting:** Users can provide a starting system prompt or use a suggested default.
4.  **Dual LLM Testing & Refinement:**
    *   Uses an LLM (Tester - LLM B) to generate outputs based on the current system prompt and user input.
    *   Uses a second LLM instance (Refiner - LLM A) to analyze the Tester's output against the desired examples/scoring and suggest an improved system prompt.
5.  **Iterative Loop:** Cycles through testing, scoring/feedback, and refinement until the user accepts the output quality or the generated system prompt.
6.  **User Scoring & Feedback:** Allows subjective scoring (e.g., 0-10 scale) of the Tester LLM's output and provides a mechanism for users to give textual feedback or guidance to the Refiner LLM.
7.  **Context Management:** Intelligently manages the context passed to both LLMs, including initial instructions, examples, previous attempts, scores, and feedback using Langchain.
8.  **Final Prompt Generation:** Presents the optimized system prompt achieved through the iterative process.
9.  **Session Management:** Allows saving the current workflow state (inputs, examples, prompt history, current prompt) and loading previous sessions.
10. **Export Functionality:** Enables exporting the final optimized system prompt (e.g., to a text file or JSON).
11. **API Integration:** Connects to the Groq API for LLM generation. Requires user-provided API key.

### User Interface

The application utilizes a multi-screen layout managed by a stacked widget within the main window. Navigation is primarily linear through the workflow steps, with back buttons allowing review of previous stages.

**1. Home Screen**

*   **Layout:** Simple vertical layout.
*   **Content:**
    *   Application Title: "SystemProbe"
    *   Subtitle: "Optimize system prompts without training your LLMs."
    *   Action Buttons:
        *   "Start New Workflow": Clears any existing state and navigates to the Input Configuration Screen.
        *   "Load Existing Session": Opens a file dialog to load a previously saved `.systemprobe` session file.
    *   Information Area: Displays app version and a brief welcome message.

**2. Input Configuration Screen**

*   **Layout:** Vertical layout, potentially with collapsible sections.
*   **Content:**
    *   Title: "Step 1: Define Inputs and Examples"
    *   Input Field (`QTextEdit`): "Example User Input(s)" - For providing one or more representative dynamic inputs the system prompt should handle. Explain that these *might* be used by the Tester LLM. Label should clarify this is optional context but recommended.
    *   Input Field (`QTextEdit`): "Desired Example Output(s)" - For providing corresponding ideal outputs for the inputs above. These are crucial for the Refiner LLM's analysis. Minimum one example required. Allow easy addition/separation of multiple examples.
    *   Guidance Text: Explain the purpose of these inputs/outputs (defining the target behavior).
    *   Navigation Buttons:
        *   "Next": Validates that at least one example output is provided, saves state, and proceeds to Initial System Prompt Screen.
        *   "Back": Returns to Home Screen.

**3. Initial System Prompt Screen**

*   **Layout:** Vertical layout.
*   **Content:**
    *   Title: "Step 2: Set Initial System Prompt"
    *   Input Field (`QTextEdit`): "Initial System Prompt" - A large text area pre-filled with a generic starter prompt (e.g., "You are a helpful assistant."). User must edit or confirm this prompt.
    *   Guidance Text: Explain that this is the starting point for refinement.
    *   Navigation Buttons:
        *   "Start Testing": Saves state and proceeds to the Output Testing Screen, triggering the first call to the Tester LLM (B).
        *   "Back": Returns to Input Configuration Screen.

**4. Output Testing Screen**

*   **Layout:** Split view or vertical layout.
*   **Content:**
    *   Title: "Step 3: Test Output and Evaluate"
    *   Display Area (`QTextBrowser` or similar): "Tester LLM Output" - Shows the output generated by LLM B using the current system prompt and potentially one of the user inputs provided earlier. Indicate which input (if any) was used.
    *   Evaluation Section:
        *   Label: "Score the output (0=Bad, 10=Perfect):"
        *   Slider (`QSlider`): Range 0-10, default value 5.
        *   Label displaying the current slider value.
    *   Status Indicator: Show "Generating output..." or similar while waiting for LLM B.
    *   Navigation/Action Buttons:
        *   "Accept Prompt (Score >= 8 Recommended)": If the user is satisfied, proceeds to the Final System Prompt Screen. Enabled state might depend on score.
        *   "Refine Prompt": Saves the score, triggers the Refiner LLM (A) analysis, and proceeds to the Refinement Screen.
        *   "Back": Returns to Initial System Prompt Screen (allowing prompt modification before re-testing).

**5. Refinement Screen**

*   **Layout:** Split view or vertical layout.
*   **Content:**
    *   Title: "Step 4: Analyze and Refine"
    *   Display Area (`QTextBrowser`): "Refiner LLM Analysis & Suggested Prompt" - Shows the analysis from LLM A regarding the previous output's shortcomings (based on examples and score) and the *newly suggested* system prompt. Clearly label the suggested prompt.
    *   Input Field (`QTextEdit`): "Optional Guidance for Next Refinement" - Allows the user to provide specific textual feedback to LLM A for the *next* refinement round (e.g., "be more concise", "focus on tone").
    *   Status Indicator: Show "Refining prompt..." while waiting for LLM A.
    *   Navigation/Action Buttons:
        *   "Test Refined Prompt": Submits the optional guidance, saves state, updates the current system prompt to the one suggested by LLM A, and navigates *back* to the Output Testing Screen to test the *new* prompt with LLM B.
        *   "Accept Current Suggested Prompt": Skips further testing and accepts the prompt suggested by LLM A, proceeding to the Final System Prompt Screen.
        *   "Back": Returns to the Output Testing Screen (showing the *previous* LLM B output again).

**6. Final System Prompt Screen**

*   **Layout:** Vertical layout.
*   **Content:**
    *   Title: "Step 5: Final Optimized System Prompt"
    *   Display Area (`QTextBrowser`): "Optimized System Prompt" - Shows the final system prompt accepted by the user.
    *   Action Buttons:
        *   "Save Prompt": Opens a file dialog to save the displayed prompt to a `.txt` file.
        *   "Export Session": Opens a file dialog to save the entire session state (inputs, examples, history, final prompt) to a `.systemprobe` (e.g., JSON) file.
        *   "Copy to Clipboard": Copies the final prompt text.
        *   "Start New Workflow": Returns to the Home Screen, clearing the current state.

**Global UI Elements:**

*   **Main Window Title:** `SystemProbe`
*   **Menu Bar (`QMenuBar`):**
    *   File: New Workflow, Load Session, Save Session, Export Prompt, Exit.
    *   Settings: API Key Configuration (input field for Groq API key), Theme (Toggle Dark/Light).
    *   Help: About, View Documentation (opens this README or a link).
*   **Status Bar (`QStatusBar`):** Displays informational messages (e.g., "Session saved," "API call in progress...", "Error: API key invalid").

### Behavior Specifications

1.  **Workflow Logic:** The core loop involves LLM B generating output based on the *current* system prompt, the user scoring it, LLM A analyzing the score/examples/feedback and generating a *new* system prompt, which then becomes the *current* system prompt for the next LLM B generation.
2.  **API Calls:** All LLM calls should be asynchronous (e.g., using `QThread`) to prevent UI freezing. The status bar should indicate when calls are in progress.
3.  **Error Handling:**
    *   Display clear error messages via modal dialogs (`QMessageBox`) for API errors (invalid key, rate limits, network issues), file I/O errors, or validation failures (e.g., missing example outputs).
    *   Provide guidance on how to resolve the error where possible (e.g., "Check your Groq API key in Settings").
4.  **Session Management:**
    *   Autosave progress to a temporary file after each significant step (e.g., completing a screen).
    *   Explicit Save/Load functionality uses a dedicated format (e.g., JSON) storing all relevant state variables.
    *   Loading a session should restore the application to the state and screen where it was saved.
5.  **Groq XML Tag Handling:** The application must handle the `<|think|>` or similar XML tags sometimes present in Groq API responses. These tags should be stripped or handled appropriately before displaying the final output to the user in the Output Testing screen and before passing outputs to the Refiner LLM. They might optionally be logged internally for debugging.

## Technical Implementation

### Architecture

1.  **GUI Framework:** `PySide6` for the desktop application interface.
2.  **Core Logic:** Python application logic separating UI from the workflow and LLM interaction.
3.  **Dual LLM Pattern:**
    *   **LLM B (Tester):** Takes the current system prompt and an optional user input example. Generates the output for evaluation.
    *   **LLM A (Refiner):** Takes the original examples, the system prompt used by LLM B, the output generated by LLM B, the user's score, and any user textual feedback. Analyzes the performance and generates an improved system prompt.
4.  **Modularity:** Structure the code logically (e.g., separate modules for UI, LLM interaction, state management, workflow logic).

### LLM Integration

1.  **API Provider:** `Groq` (https://groq.com/)
2.  **API Key:** User must provide their own Groq API key via the Settings menu. This key should be stored securely (e.g., using system keychain if possible, or at least not plaintext in config files) or configured via environment variables. The application must handle cases where the key is missing or invalid.
3.  **Model:** Default model for both Refiner (A) and Tester (B) roles: `Qwen-qwq-32B` (or the closest available high-capability Qwen model on Groq at implementation time). Model selection should ideally be configurable in settings for advanced users later.
4.  **Interaction Library:** `Langchain` library will be used to manage interactions with the Groq API, format prompts, and manage conversational context/memory between iterations.

### Context Management (Using Langchain)

1.  **Memory:** Langchain's memory modules will manage the state passed to the LLMs.
2.  **Refiner Context (LLM A):** Needs access to:
    *   Initial user-provided goal/instructions.
    *   User-provided example inputs/outputs.
    *   The specific system prompt used by LLM B in the last turn.
    *   The specific output generated by LLM B in the last turn.
    *   The user's numerical score for that output.
    *   The user's textual feedback/guidance (if provided).
    *   A summary history of previously attempted prompts and their scores/failures to avoid loops and encourage progress.
3.  **Tester Context (LLM B):** Primarily needs:
    *   The current system prompt (generated by LLM A or the initial one).
    *   One of the user-provided example inputs (optional, can be selected round-robin or randomly).
    *   Minimal conversational history, mostly just the current task based on the system prompt.
4.  **Failure Tracking:** Maintain a list or summary of prompts that resulted in low scores to guide the Refiner away from repeating mistakes. This context should be appended to/managed by Langchain memory.

### Data Structures

1.  **Session State:** A Python dictionary (serializable to JSON) containing:
    *   `userInputExamples`: List of strings.
    *   `desiredOutputExamples`: List of strings.
    *   `promptHistory`: List of dictionaries, each containing:
        *   `prompt`: The system prompt text.
        *   `testerOutput`: The output from LLM B.
        *   `score`: Integer (0-10).
        *   `userFeedback`: String (optional).
        *   `refinerAnalysis`: String (LLM A's thoughts, optional).
    *   `currentSystemPrompt`: String.
    *   `finalSystemPrompt`: String (set when accepted).
    *   `currentWorkflowStep`: Identifier for the active screen/step.
2.  **API Payloads:** Standard JSON structures required by the Groq API via Langchain.

### Algorithms

1.  **Core Refinement Loop:**
    *   `Start:` User provides inputs, examples, initial prompt.
    *   `Test:` Call LLM B with `currentSystemPrompt` and optional input. Display output.
    *   `Evaluate:` User provides score and optional feedback.
    *   `Check Acceptance:` If user accepts, go to `Finalize`.
    *   `Refine:` Call LLM A with relevant context (prompt, output, score, feedback, examples, history). LLM A returns analysis and `newSystemPrompt`.
    *   `Update:` Set `currentSystemPrompt = newSystemPrompt`. Add the previous attempt to `promptHistory`. Go to `Test`.
    *   `Finalize:` Display `currentSystemPrompt` as the final result. Enable save/export.

## Style Guide

1.  **Default Theme:** Dark Mode. Use a visually appealing dark theme with good contrast (e.g., dark gray/charcoal backgrounds, light gray/white text, blue or cyan accents for interactive elements).
2.  **Optional Theme:** Light Mode. Provide a toggle in Settings to switch to a clean, standard light theme. Theme changes should apply instantly.
3.  **Fonts:** Use standard sans-serif system fonts (e.g., Segoe UI on Windows, San Francisco on macOS, Cantarell/Noto Sans on Linux). Font size should be reasonably adjustable via Settings for accessibility.
4.  **Layout:** Use consistent padding and spacing. Ensure layouts adapt reasonably to window resizing.
5.  **Responsiveness:** While primarily desktop-focused, ensure UI elements don't become unusable at moderately smaller window sizes.

## Testing Scenarios

1.  **Happy Path:** Complete a workflow from start to finish, accepting a prompt after 3 refinement loops. Save the prompt and session. Load the session.
2.  **API Key Error:** Start the workflow with an invalid/missing API key. Verify error message and guidance to Settings.
3.  **API Call Failure:** Simulate a network error during an LLM call. Verify UI feedback (status bar, error message) and graceful recovery (e.g., allow retry).
4.  **No Examples Provided:** Attempt to proceed from Input Configuration without providing example outputs. Verify validation error.
5.  **Large Text Handling:** Test with very long example inputs/outputs and system prompts. Ensure UI remains responsive.
6.  **Session Load:** Save a session midway through refinement (e.g., on Refinement Screen). Close and reload. Verify it restores correctly.
7.  **Theme Toggle:** Switch between Dark and Light themes. Verify all UI elements update correctly.
8.  **XML Tag Handling:** Verify `<|thinking|>` tags from Groq are not displayed in the user-facing output.

## Accessibility Requirements

1.  **Keyboard Navigation:** All interactive elements (buttons, input fields, sliders, menus) must be navigable and operable using the keyboard (Tab, Shift+Tab, Enter, Space, Arrow keys).
2.  **Contrast:** Ensure sufficient text/background contrast in both Dark and Light themes (WCAG AA minimum).
3.  **Focus Indication:** Clearly visible focus indicators for the currently active element.
4.  **Font Scaling:** Basic font size adjustment via Settings.

## Performance Goals

1.  **UI Responsiveness:** The UI must remain responsive during LLM API calls (handled via threading). No freezes.
2.  **Startup Time:** Application should launch within a few seconds.
3.  **Text Handling:** Smooth scrolling and editing even with large amounts of text in input/output fields.

## Extended Features (Optional - For Future Consideration)

1.  **Model Selection:** Allow users to choose different models available via Groq (or other APIs).
2.  **Batch Testing:** Allow testing a system prompt against multiple user inputs simultaneously.
3.  **Advanced Analysis:** Provide more detailed metrics or visualizations of prompt performance over iterations.
4.  **Prompt Templating:** Allow users to define templates for system prompts with variable insertion.
5.  **Prompt Version History:** Within a session, allow viewing and reverting to previous versions of the system prompt.
6.  **Integration with other APIs:** Add support for OpenAI, Anthropic etc.

---