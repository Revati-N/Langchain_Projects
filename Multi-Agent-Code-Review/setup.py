# setup.py
import subprocess
import sys

def install_requirements():
    requirements = [
        "streamlit",
        "langchain",
        "ollama",
        "python-dotenv"
    ]
    
    for package in requirements:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def setup_ollama():
    print("🚀 Setting up Ollama and Llama2...")
    print("Please run these commands in your terminal:")
    print("1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
    print("2. Pull Llama2: ollama pull llama2")
    print("3. Start Ollama service: ollama serve")

if __name__ == "__main__":
    install_requirements()
    setup_ollama()
