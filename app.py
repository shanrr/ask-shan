"""
Ask-Shan: A self-hosted AI assistant

Author: Rakshith Shanbhag
"""


import streamlit as st
import ollama
from ollama import ChatResponse
import requests
import json
import time

# Page configuration
st.set_page_config(
    page_title="Ask-Shan",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .model-info {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(5px);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    
    .warning-info {
        background: rgba(255, 193, 7, 0.2);
        backdrop-filter: blur(5px);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #FFC107;
    }
    
    .sidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    h1 {
        color: white;
        text-align: center;
        font-size: 3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 2rem;
    }
    
    .stSelectbox label {
        color: white;
        font-weight: bold;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)


# Model information will be fetched dynamically from Ollama registry

def check_ollama_connection():
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_installed_models():
    """Get list of locally installed models from Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            data = response.json()
            return [model["name"].split(":")[0] for model in data.get("models", [])]
        return []
    except:
        return []

def get_all_available_models():
    """Get list of all available models from Ollama library"""
    # Popular models available in Ollama registry
    # This list can be expanded based on Ollama's model library
    popular_models = [
        "llama3.2", "llama3.1", "llama3", "llama2", "llama2:13b", "llama2:70b",
        "codellama", "codellama:13b", "codellama:34b",
        "mistral", "mistral:7b", "mixtral", "mixtral:8x7b",
        "phi3", "phi3:medium", "phi3:mini",
        "gemma", "gemma:2b", "gemma:7b",
        "qwen2", "qwen2:7b", "qwen2:72b",
        "llava", "llava:13b", "llava:34b",
        "vicuna", "vicuna:13b", "vicuna:33b",
        "orca-mini", "orca-mini:13b",
        "wizard-coder", "wizard-math",
        "dolphin-mistral", "dolphin-llama3",
        "openchat", "starling-lm",
        "neural-chat", "solar",
        "tinyllama", "medllama2",
        "yarn-mistral", "deepseek-coder"
    ]
    return sorted(popular_models)

def get_model_info(model_name):
    """Get estimated model information"""
    # Basic size estimation based on model names
    size_mapping = {
        "2b": "1.4GB", "3b": "2.0GB", "7b": "4.0GB", "8b": "4.7GB", "13b": "7.3GB",
        "34b": "20GB", "70b": "40GB", "72b": "41GB", "8x7b": "26GB"
    }
    
    # Extract size from model name
    model_size = "~4GB"  # default
    for size_key, size_val in size_mapping.items():
        if size_key in model_name.lower():
            model_size = size_val
            break
    
    # Model descriptions
    descriptions = {
        "llama3.2": "Latest Llama model with improved performance",
        "llama3.1": "Advanced Llama 3.1 with enhanced capabilities",
        "llama3": "Meta's Llama 3 model, excellent general performance",
        "llama2": "Meta's Llama 2 model, reliable and well-tested",
        "codellama": "Specialized for code generation and programming",
        "mistral": "Efficient model from Mistral AI",
        "mixtral": "Mixture of Experts model, very powerful",
        "phi3": "Microsoft's efficient small language model",
        "gemma": "Google's open source model",
        "qwen2": "Alibaba's multilingual model",
        "llava": "Large Language and Vision Assistant",
        "vicuna": "Open-source chatbot trained by fine-tuning LLaMA",
        "orca-mini": "Compact model with strong reasoning",
        "wizard-coder": "Specialized for code generation",
        "wizard-math": "Specialized for mathematical reasoning",
        "dolphin-mistral": "Uncensored Mistral model",
        "dolphin-llama3": "Uncensored Llama3 model",
        "openchat": "Open-source conversational AI",
        "starling-lm": "Reinforcement Learning trained model",
        "neural-chat": "Intel's neural chat model",
        "solar": "Upstage's solar model",
        "tinyllama": "Very small but capable model",
        "medllama2": "Medical domain specialized model",
        "yarn-mistral": "Extended context Mistral model",
        "deepseek-coder": "DeepSeek's coding specialized model"
    }
    
    # Find description
    description = "General purpose language model"
    for key, desc in descriptions.items():
        if key in model_name.lower():
            description = desc
            break
    
    return {"size": model_size, "description": description}

def pull_model(model_name):
    """Pull a model from Ollama"""
    try:
        # Start the pull process
        response = requests.post(
            "http://localhost:11434/api/pull",
            json={"name": model_name},
            stream=True,
            timeout=300
        )
        
        if response.status_code == 200:
            progress_placeholder = st.empty()
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "status" in data:
                            progress_placeholder.info(f" {data['status']}")
                        if data.get("status") == "success":
                            return True
                    except json.JSONDecodeError:
                        continue
        return False
    except Exception as e:
        st.error(f"Error pulling model: {str(e)}")
        return False

def main():
    # Title
    st.markdown("# Ask-Shan")
    
    # Check Ollama connection
    if not check_ollama_connection():
        st.error(" Ollama server is not running! Please start it with: `ollama serve`")
        st.stop()
    
    # Sidebar for model selection
    with st.sidebar:
        st.markdown("###  Model Configuration")
        
        # Get all available models from Ollama registry
        all_available_models = get_all_available_models()
        
        # Get locally installed models
        installed_models = get_installed_models()
        
        # Model selection
        selected_model = st.selectbox(
            "Choose Model:",
            options=all_available_models,
            index=0,
            help="Select the AI model you want to use",
            format_func=lambda x: f"{' ' if x in installed_models else '📥 '}{x}"
        )
        
        # Display model information
        model_info = get_model_info(selected_model)
        st.markdown(f"""
        <div class="model-info">
            <h4>Model Details</h4>
            <p><strong>Name:</strong> {selected_model}</p>
            <p><strong>Estimated Size:</strong> {model_info['size']}</p>
            <p><strong>Description:</strong> {model_info['description']}</p>
            <p><strong>Status:</strong> {' Installed' if selected_model in installed_models else ' Not Installed'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if model is available locally
        model_installed = selected_model in installed_models
        
        if not model_installed:
            st.markdown(f"""
            <div class="warning-info">
                <h4> Model Not Available</h4>
                <p>The selected model <strong>{selected_model}</strong> is not installed locally.</p>
                <p>Click the button below to download and install it.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f" Download {selected_model}"):
                with st.spinner(f"Downloading {selected_model}... This may take a while."):
                    success = pull_model(selected_model)
                    if success:
                        st.success(f" {selected_model} downloaded successfully!")
                        st.rerun()
                    else:
                        st.error(f" Failed to download {selected_model}")
        else:
            st.success(f" {selected_model} is ready to use!")
        
        # Display installed vs available models
        st.markdown("###  Model Status")
        
        # Show installed models
        if installed_models:
            st.markdown("** Installed Models:**")
            for model in installed_models:
                st.markdown(f" {model}")
        else:
            st.markdown("**No models installed yet**")
        
        # Show total available
        st.markdown(f"**Available Models:** {len(all_available_models)} models in registry")
        
        # System info
        st.markdown("### Tips")
        st.markdown("""
        - Larger models provide better responses but require more RAM
        - Keep Ollama server running in the background
        - First-time model downloads can be large
        """)

    # Initialize session state
    if "ollama_model" not in st.session_state:
        st.session_state["ollama_model"] = selected_model
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Update model if changed
    if st.session_state["ollama_model"] != selected_model:
        st.session_state["ollama_model"] = selected_model
        if selected_model not in installed_models:
            st.warning(f"Please download {selected_model} from the sidebar first!")

    # Main chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What's on your mind? "):
        # Check if selected model is available
        if selected_model not in installed_models:
            st.error(f"Please download the {selected_model} model first using the sidebar!")
            st.stop()
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking... "):
                    response: ChatResponse = ollama.chat(
                        model=st.session_state["ollama_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                    )
                # Handle different response formats
                if hasattr(response, 'message'):
                    # If it's a ChatResponse object
                    response_content = response.message.content
                elif isinstance(response, dict):
                    # If it's a dictionary response
                    response_content = response.get('message', {}).get('content', 'No response generated')
                else:
                    # Fallback
                    response_content = str(response)
                
                st.markdown(response_content)
                
                # Add assistant message to session state
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_content}
                )
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                st.info("Make sure Ollama is running and the model is available!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
if __name__ == "__main__":
    main()