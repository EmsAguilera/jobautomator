import google.generativeai as genai
import re

def clean_ai_response(text):
    """
    Cleans the raw text response from the AI.
    - Removes markdown code fences (```...```)
    - Removes leading/trailing quotes, spaces, and special brackets.
    """
    # Remove markdown code fences (e.g., ```latex ... ```)
    text = re.sub(r'^```[a-zA-Z]*\n?', '', text)
    text = re.sub(r'\n?```$', '', text)
    
    # Remove any leading/trailing junk characters like quotes, spaces, or brackets
    # This specifically targets the `[\{ ... \}]` issue
    text = re.sub(r'^[\[\{\s"\']+', '', text)
    text = re.sub(r'[\]\}\s"\']+$', '', text)
    
    return text.strip()

def configure_ai():
    """Prompts for and configures the AI model."""
    try:
        api_key = "AIzaSyC9l7mn97u0LbNIW2jd2FZupwZ8qoTRUNs" #input("Please enter your Google AI API key: ").strip()
        if not api_key:
            print("API key cannot be empty.")
            return None
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Successfully configured Google AI.")
        return model
    except Exception as e:
        print(f"Error configuring Google AI: {e}")
        return None

def generate_content(model, system_instruction, template, context):
    """Generates and cleans content from the AI using a structured prompt."""
    try:
        prompt = f"{system_instruction}\n\n{template.format(**context)}"
        response = model.generate_content(prompt)
        
        # --- THIS IS THE KEY ---
        # We immediately clean the raw response text.
        cleaned_text = clean_ai_response(response.text)
        
        return cleaned_text
    except Exception as e:
        print(f"An error occurred while generating AI content: {e}")
        return None
