# SystemProbe

**SystemProbe** is an AI-powered desktop application designed to help users discover and optimize **system prompts** for Large Language Models (LLMs) without requiring complex fine-tuning or LoRA training. It guides users through an iterative process of refining system prompts to achieve desired outputs for dynamic inputs.

## Features

- **Dual LLM Workflow**: Uses two LLMs - one for testing prompts and another for refining them
- **Iterative Refinement**: Step-by-step process to refine system prompts based on user feedback
- **Visual Scoring**: Rate prompt effectiveness with an intuitive slider
- **Custom Guidance**: Provide specific guidance to the refiner LLM
- **Session Management**: Save and load your prompt optimization sessions
- **Dark/Light Theme Support**: Choose your preferred visual theme
- **Groq API Integration**: Leverages Groq's powerful LLM models

## Usage

1. **Start the application**:
   ```
   python main.py
   ```
   ![Step 0](https://github.com/fernicar/SystemProbe/blob/main/images/app_capture0.png)

2. **Step 1: Define Inputs and Examples**
   - Enter representative user inputs that your system prompt should handle
   - Provide the ideal outputs for each input example
   - Separate multiple examples with `---`
   ![Step 1](https://github.com/fernicar/SystemProbe/blob/main/images/app_capture1.png)

3. **Step 2: Set Initial System Prompt**
   - Enter your starting system prompt
   - This will be the baseline for refinement
   ![Step 2](https://github.com/fernicar/SystemProbe/blob/main/images/app_capture2.png)

4. **Step 3: Test Output and Score Results**
   - The Tester LLM will generate output based on your system prompt
   - Score the output from 1-10
   - Provide specific feedback on what to improve
   - Choose to refine or accept the prompt
   ![Step 3](https://github.com/fernicar/SystemProbe/blob/main/images/app_capture3.png)

5. **Step 4: Analyze and Refine**
   - Review the Refiner LLM's analysis
   - Add optional guidance for further refinement
   - Click "Refine Prompt" to generate new suggestions
   - Test the refined prompt or accept it as final
   ![Step 4](https://github.com/fernicar/SystemProbe/blob/main/images/app_capture4.png)

6. **Step 5: Final Optimized Prompt**
   - Copy your optimized system prompt
   - Save it to a file
   - Start a new workflow if needed
   ![Step 5](https://github.com/fernicar/SystemProbe/blob/main/images/app_capture5.png)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/fernicar/SystemProbe.git
   cd SystemProbe
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your Groq free API key:
   - Create a `.env` file in the project root with:
     ```
     GROQ_API_KEY='your_groq_api_key_here'
     ```
   - Or enter it in the application settings

## Configuration

- **API Key**: Set your Groq API key in Settings
- **Theme**: Choose between Dark and Light themes
- **LLM Model**: Select from available Groq models
- **Model Updates**: Toggle automatic model list updates

## Technologies Used

- **Python**: Core programming language
- **PySide6**: Qt-based GUI framework
- **Langchain**: Framework for LLM application development
- **Groq API**: High-performance LLM provider
- **QThread Workers**: For non-blocking LLM operations

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/fernicar/SystemProbe/blob/main/LICENSE) file for details.

## Acknowledgments

*   Special thanks to ScuffedEpoch for the [TINS](https://github.com/ScuffedEpoch/TINS) methodology and the initial example.
*   Thanks to the free tier AI assistant for its initial contribution to the project.
*   Gratitude to the Groq team for their API and support.
*   Thanks to the Langchain and PySide6 communities for their respective libraries and documentation.
*   Augment extension for VS Code
*   Tested LLM Gemini2.5pro (free tier beta testing) from Google AI Studio
