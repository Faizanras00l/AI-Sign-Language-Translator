"""
ASL Chatbot Backend
Provides AI-powered chat assistant for the ASL Learning & Accessibility Platform.
"""

import os
import json
import requests
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

# Use the same paid API key as text-to-sign
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY environment variable not set. Chatbot may not function.")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct:free"  # Free Mistral model

# Paths
SCRIPT_DIR = Path(__file__).parent
VOCAB_FILE = SCRIPT_DIR / "processed_index.json"


# ============================================================
# VOCABULARY LOADING
# ============================================================

def load_vocabulary():
    """Load the vocabulary list from the JSON file."""
    try:
        with open(VOCAB_FILE, 'r') as f:
            data = json.load(f)
            return list(data.keys())
    except FileNotFoundError:
        print(f"Warning: {VOCAB_FILE} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Warning: Failed to decode {VOCAB_FILE}.")
        return []


# ============================================================
# SYSTEM PROMPT
# ============================================================

def get_system_prompt():
    """Generate the system prompt with vocabulary context."""
    vocab_list = load_vocabulary()
    vocab_string = ", ".join(vocab_list) if vocab_list else "No vocabulary loaded"
    
    return f"""You are the official, intelligent AI Assistant for the **ASL Learning & Accessibility Platform**. 
Your goal is to provide a premium, professional, and supportive experience for users who are learning American Sign Language or using the accessibility features of this app.

**Your Persona:**
- **Professional & Warm**: Speak with authority but maintain a friendly, encouraging tone suitable for learners and the Deaf community.
- **Context-Aware**: You are *embedded* in the app. Do not talk like a generic AI. Refer to "our app," "this platform," and "the modules here."
- **Concise yet Comprehensive**: Give direct answers. Avoid fluff, but ensure the user feels fully supported.

**Core Knowledge Base (Your Capabilities):**

1.  **🎓 Education Module (The Learning Center)**
    - You guide users through structured courses (Beginner to Advanced).
    - Mention our prestigious partners like **Gallaudet University** and **RIT/NTID** to build trust.
    - Explain that we track progress, offer quizzes, and award certificates.

2.  **🚨 SOS / Emergency Module**
    - **CRITICAL**: If a user mentions safety or emergency, prioritize this.
    - Explain features like **Sign SOS recognition**, live location sharing, and one-tap dialing for police/ambulance.
    - *Tone Check*: Be serious and reassuring when discussing this module.

3.  **✍️ Text-to-Sign Module**
    - You convert text into sign language videos.
    - **Vocabulary Check**: You have access to a specific list of ~2000 supported words. 
    - *Action*: If a user asks "Can you sign [word]?", **CHECK THE LIST**.
        - If YES: "Yes! We have a video for that word."
        - If NO: "I don't have that word in my library yet, but try a synonym!"

4.  **👐 Sign-to-Text Module**
    - Explain that we use a **3D CNN model** trained on the WLASL dataset to interpret signs via the camera.

**How to Respond:**
- **When asked "What can you do?":** Say something like:
  "I am here to help you master ASL and stay safe. I can guide you through our learning modules tailored by top universities, help you communicate in emergencies with our SOS features, and instantly translate text to sign language (and vice versa!) using our advanced AI tools."
- **When asked generic questions:** pivot back to the app's features.
- Keep responses concise but helpful.

**Supported Vocabulary ({len(vocab_list)} words):**
{vocab_string}

**Rules:**
- Do not make up features we don't have.
- Do not claim to be a human interpreter.
- Keep responses focused on this specific ASL application.
- Be helpful, warm, and encouraging!
"""


# ============================================================
# CHAT RESPONSE FUNCTION (Used by Flask API)
# ============================================================

def chat_response(user_message: str, conversation_history: list = None) -> dict:
    """
    Get chatbot response for a single message.
    
    Args:
        user_message: The user's message
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        
    Returns:
        dict with:
        - success: bool
        - response: str (the bot's reply)
        - history: list (updated conversation history)
        - error: str (if success is False)
    """
    if conversation_history is None:
        conversation_history = []
    
    # Build messages array with system prompt
    messages = [{"role": "system", "content": get_system_prompt()}]
    
    # Add conversation history
    messages.extend(conversation_history)
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    # API headers
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "ASL Chatbot"
    }
    
    # API payload
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        
        # Log response for debugging
        print(f"[Chatbot] API Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Robust parsing with error handling
            if not result:
                return {
                    "success": False,
                    "error": "Empty response from API",
                    "response": "Sorry, I didn't get a response. Please try again.",
                    "history": conversation_history
                }
            
            choices = result.get('choices')
            if not choices or len(choices) == 0:
                print(f"[Chatbot] No choices in response: {result}")
                return {
                    "success": False,
                    "error": "No response choices from API",
                    "response": "Sorry, the AI couldn't generate a response. Please try again.",
                    "history": conversation_history
                }
            
            message = choices[0].get('message')
            if not message:
                print(f"[Chatbot] No message in choice: {choices[0]}")
                return {
                    "success": False,
                    "error": "No message in response",
                    "response": "Sorry, I had trouble processing the response. Please try again.",
                    "history": conversation_history
                }
            
            assistant_content = message.get('content', '')
            if not assistant_content:
                assistant_content = "I'm sorry, I couldn't generate a response. Please try again."
            
            # Update history (without system prompt)
            new_history = conversation_history.copy()
            new_history.append({"role": "user", "content": user_message})
            new_history.append({"role": "assistant", "content": assistant_content})
            
            return {
                "success": True,
                "response": assistant_content,
                "history": new_history
            }
        else:
            error_text = response.text[:200] if response.text else "Unknown error"
            print(f"[Chatbot] API Error: {response.status_code} - {error_text}")
            return {
                "success": False,
                "error": f"API error: {response.status_code}",
                "response": "Sorry, I'm having trouble connecting to the AI service. Please try again.",
                "history": conversation_history
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "response": "Sorry, the request timed out. Please try again.",
            "history": conversation_history
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": "Sorry, something went wrong. Please try again.",
            "history": conversation_history
        }


# ============================================================
# CLI MODE (for testing)
# ============================================================

def main():
    """Command-line interface for testing the chatbot."""
    print("Initializing ASL Chatbot...")
    
    vocab_list = load_vocabulary()
    print(f"Loaded {len(vocab_list)} words from vocabulary.")
    
    print("\nChatbot Ready! (Type 'exit' or 'quit' to stop)")
    print("-" * 50)
    
    history = []
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue
            
            print("Thinking...", end="", flush=True)
            result = chat_response(user_input, history)
            
            print(f"\rBot: {result['response']}")
            history = result['history']
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
