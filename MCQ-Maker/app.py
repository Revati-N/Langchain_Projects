import streamlit as st
import tempfile
import os
from io import BytesIO
from pathlib import Path
import json
import re

# Document processing
import fitz  # PyMuPDF
from docx import Document

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    text = ""
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text()
    pdf_document.close()
    return text

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    doc = Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_txt(txt_file):
    """Extract text from TXT file"""
    return txt_file.read().decode('utf-8')

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text"""
    file_extension = Path(uploaded_file.name).suffix.lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_extension == '.docx':
        return extract_text_from_docx(uploaded_file)
    elif file_extension == '.txt':
        return extract_text_from_txt(uploaded_file)
    else:
        st.error("Unsupported file format. Please upload PDF, DOCX, or TXT files.")
        return None

def create_mcq_prompt():
    """Create prompt template for MCQ generation"""
    prompt_template = """
    Based on the following content, create {num_questions} multiple choice questions with 4 options each. 
    The questions should be relevant to the content and test understanding of key concepts.
    
    Content: {content}
    
    Please format your response as JSON with the following structure:
    {{
        "questions": [
            {{
                "question": "Question text here?",
                "options": [
                    "A) Option 1",
                    "B) Option 2", 
                    "C) Option 3",
                    "D) Option 4"
                ],
                "correct_answer": "A",
                "explanation": "Brief explanation of why this is correct"
            }}
        ]
    }}
    
    Make sure questions are:
    - Clear and unambiguous
    - Based on important concepts from the content
    - Have one clearly correct answer
    - Include plausible distractors for incorrect options
    
    Generate exactly {num_questions} questions.
    """
    
    return PromptTemplate(
        input_variables=["content", "num_questions"],
        template=prompt_template
    )

def initialize_llm():
    """Initialize Ollama LLM with Llama2"""
    try:
        llm = Ollama(
            model="llama2",
            base_url="http://localhost:11434"
        )
        return llm
    except Exception as e:
        st.error(f"Error connecting to Ollama: {e}")
        st.info("Make sure Ollama is running with: ollama serve")
        st.info("And Llama2 is installed with: ollama pull llama2")
        return None

def generate_mcqs(content, num_questions, llm):
    """Generate MCQs using LangChain and Llama2"""
    try:
        # Create prompt template
        prompt = create_mcq_prompt()
        
        # Create chain
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Split content if too long
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=200
        )
        
        # If content is too long, take first chunk
        chunks = text_splitter.split_text(content)
        content_to_use = chunks[0] if chunks else content
        
        # Generate MCQs
        with st.spinner("Generating MCQs..."):
            response = chain.run(
                content=content_to_use,
                num_questions=num_questions
            )
        
        return response
    except Exception as e:
        st.error(f"Error generating MCQs: {e}")
        return None

def parse_mcq_response(response):
    """Parse the LLM response to extract MCQs"""
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            mcq_data = json.loads(json_str)
            return mcq_data
        else:
            # If no JSON found, try manual parsing
            return parse_text_response(response)
    except json.JSONDecodeError:
        return parse_text_response(response)

def parse_text_response(response):
    """Fallback parser for non-JSON responses"""
    questions = []
    lines = response.split('\n')
    
    current_question = None
    current_options = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line contains a question (ends with ?)
        if '?' in line and not line.startswith(('A)', 'B)', 'C)', 'D)')):
            if current_question and current_options:
                questions.append({
                    "question": current_question,
                    "options": current_options,
                    "correct_answer": "A",  # Default
                    "explanation": "Please verify the correct answer."
                })
            current_question = line
            current_options = []
        
        # Check if line is an option
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            current_options.append(line)
    
    # Add last question
    if current_question and current_options:
        questions.append({
            "question": current_question,
            "options": current_options,
            "correct_answer": "A",
            "explanation": "Please verify the correct answer."
        })
    
    return {"questions": questions}

def display_mcqs(mcq_data):
    """Display generated MCQs in Streamlit"""
    if not mcq_data or "questions" not in mcq_data:
        st.error("No questions found in the response.")
        return
    
    st.subheader("Generated MCQs")
    
    for i, q in enumerate(mcq_data["questions"], 1):
        with st.expander(f"Question {i}", expanded=True):
            st.write(f"**{q['question']}**")
            
            for option in q['options']:
                st.write(option)
            
            st.write(f"**Correct Answer:** {q.get('correct_answer', 'Not specified')}")
            
            if 'explanation' in q:
                st.write(f"**Explanation:** {q['explanation']}")
            
            st.divider()

def download_mcqs_as_text(mcq_data):
    """Create downloadable text file of MCQs"""
    if not mcq_data or "questions" not in mcq_data:
        return None
    
    content = "MULTIPLE CHOICE QUESTIONS\n"
    content += "=" * 50 + "\n\n"
    
    for i, q in enumerate(mcq_data["questions"], 1):
        content += f"Question {i}: {q['question']}\n"
        for option in q['options']:
            content += f"  {option}\n"
        content += f"Correct Answer: {q.get('correct_answer', 'Not specified')}\n"
        if 'explanation' in q:
            content += f"Explanation: {q['explanation']}\n"
        content += "\n" + "-" * 30 + "\n\n"
    
    return content

def main():
    st.set_page_config(
        page_title="MCQ Generator",
        page_icon="📝",
        layout="wide"
    )
    
    st.title("📝 MCQ Generator using Llama2 & LangChain")
    st.markdown("Generate multiple choice questions from your documents using AI")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=5)
        
        st.header("Instructions")
        st.markdown("""
        1. Make sure Ollama is running (`ollama serve`)
        2. Install Llama2 model (`ollama pull llama2`)
        3. Upload your document (PDF, DOCX, or TXT)
        4. Click 'Generate MCQs'
        """)
    
    # Initialize LLM
    llm = initialize_llm()
    
    if llm is None:
        st.stop()
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your document",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        # Extract text from file
        with st.spinner("Processing document..."):
            extracted_text = process_uploaded_file(uploaded_file)
        
        if extracted_text:
            # Show document preview
            with st.expander("Document Preview", expanded=False):
                st.text_area("Content", extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text, height=200)
            
            # Generate MCQs button
            if st.button("Generate MCQs", type="primary"):
                mcq_response = generate_mcqs(extracted_text, num_questions, llm)
                
                if mcq_response:
                    # Parse the response
                    mcq_data = parse_mcq_response(mcq_response)
                    
                    # Store in session state
                    st.session_state.mcq_data = mcq_data
                    
                    # Display MCQs
                    display_mcqs(mcq_data)
                    
                    # Download option
                    if mcq_data and "questions" in mcq_data:
                        text_content = download_mcqs_as_text(mcq_data)
                        if text_content:
                            st.download_button(
                                label="Download MCQs as Text File",
                                data=text_content,
                                file_name=f"mcqs_{uploaded_file.name.split('.')[0]}.txt",
                                mime="text/plain"
                            )
    
    # Display previously generated MCQs if they exist
    elif 'mcq_data' in st.session_state:
        display_mcqs(st.session_state.mcq_data)

if __name__ == "__main__":
    main()
