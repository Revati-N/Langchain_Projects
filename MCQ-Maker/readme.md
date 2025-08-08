# MCQ Generator - AI-Powered Quiz Maker

Generate multiple choice questions from your documents using Llama2 and LangChain with a beautiful Streamlit interface.

## 🌟 Features

- **Document Support**: Upload PDF, DOCX, and TXT files
- **AI-Powered Generation**: Uses Llama2 model via Ollama for intelligent question creation
- **LangChain Integration**: Leverages LangChain for robust prompt management
- **Interactive UI**: Clean Streamlit web interface
- **Local Processing**: All data stays on your machine - complete privacy
- **Download Results**: Export generated MCQs as text files
- **Customizable**: Adjust number of questions (1-10)

## 📋 Prerequisites

- Python 3.8+
- Ollama installed and running
- Llama2 model pulled in Ollama

## 🚀 Installation

### 1. Install Ollama and Llama2

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# For Windows, download from https://ollama.ai/download

# Start Ollama service
ollama serve

# Pull Llama2 model (this may take a few minutes)
ollama pull llama2
```

### 2. Install Python Dependencies

```bash
pip install streamlit langchain langchain-community ollama pymupdf python-docx
```

### 3. Download the Application

Save the provided code as `mcq_generator.py`

## 🎯 Usage

### 1. Start the Application

```bash
streamlit run mcq_generator.py
```

### 2. Using the Interface

1. **Configure Settings** (sidebar):
   - Set number of questions (1-10)
   - Review setup instructions

2. **Upload Document**:
   - Click "Browse files" or drag & drop
   - Supported formats: PDF, DOCX, TXT
   - View document preview if needed

3. **Generate MCQs**:
   - Click "Generate MCQs" button
   - Wait for AI processing (may take 30-60 seconds)
   - Review generated questions with answers and explanations

4. **Download Results**:
   - Click "Download MCQs as Text File"
   - Save for later use or sharing

## 📂 Supported File Formats

- **PDF** (.pdf) - Extracts text from all pages
- **Word Document** (.docx) - Processes paragraphs and text
- **Text File** (.txt) - Direct text processing

## 🛠️ Technical Architecture

```
User Document → Text Extraction → Text Splitting → LangChain Prompt → Llama2 Model → MCQ Generation → Streamlit Display
```

### Key Components

- **Document Processing**: PyMuPDF, python-docx
- **AI Framework**: LangChain for prompt management
- **Language Model**: Llama2 via Ollama (local inference)
- **Web Interface**: Streamlit
- **Text Processing**: RecursiveCharacterTextSplitter

## ⚙️ Configuration Options

### Model Settings
- **Model**: Llama2 (default)
- **Base URL**: http://localhost:11434 (Ollama default)
- **Chunk Size**: 3000 characters
- **Chunk Overlap**: 200 characters

### Question Settings
- **Number of Questions**: 1-10 (adjustable via slider)
- **Question Format**: Multiple choice with 4 options
- **Output Format**: JSON with fallback text parsing

## 🔧 Troubleshooting

### Common Issues

1. **"Error connecting to Ollama"**
   ```bash
   # Make sure Ollama is running
   ollama serve
   ```

2. **"Model not found"**
   ```bash
   # Pull the Llama2 model
   ollama pull llama2
   ```

3. **Large documents taking too long**
   - The app automatically uses the first 3000 characters
   - Consider splitting very large documents

4. **Questions not in proper format**
   - The app has fallback parsing for non-JSON responses
   - Manual verification may be needed for edge cases

### System Requirements

- **RAM**: 4GB minimum (8GB+ recommended for Llama2)
- **Storage**: 5GB+ for Llama2 model
- **CPU**: Modern multi-core processor recommended

## 🤝 Contributing

Feel free to contribute improvements:
- Better document parsing
- Additional model support
- Enhanced UI/UX
- Performance optimizations

## 📄 License

This project is open source and available under the MIT License.

## 🔗 Dependencies

- `streamlit`: Web interface framework
- `langchain`: LLM application framework
- `langchain-community`: Community LangChain integrations
- `ollama`: Local LLM inference
- `pymupdf`: PDF text extraction
- `python-docx`: Word document processing

## 🆘 Support

If you encounter issues:
1. Check that Ollama is running: `ollama serve`
2. Verify Llama2 is installed: `ollama list`
3. Ensure all Python dependencies are installed
4. Check the Streamlit logs for detailed error messages

***

**Happy Quiz Making! 📝✨**