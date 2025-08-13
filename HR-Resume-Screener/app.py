import streamlit as st
import pandas as pd
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import tempfile
import os
import json
import re

class ResumeParser:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def extract_text_from_pdf(self, pdf_file):
        """Extract text from uploaded PDF resume"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            loader = PyPDFLoader(tmp_file_path)
            documents = loader.load()
            text = "\n".join([doc.page_content for doc in documents])
            return text
        except Exception as e:
            st.error(f"Error extracting PDF: {str(e)}")
            return ""
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

class ResumeAnalyzer:
    def __init__(self):
        try:
            # Initialize Ollama with Llama2
            self.llm = Ollama(
                model="llama2",
                base_url="http://localhost:11434"
            )
        except Exception as e:
            st.error(f"Error connecting to Ollama: {str(e)}")
            st.error("Make sure Ollama is running and llama2 model is installed")
            
        # Define analysis prompt template
        self.analysis_prompt = PromptTemplate(
            input_variables=["resume_text", "job_description"],
            template="""
            As an HR expert, analyze the following resume against the job description.
            
            Job Description:
            {job_description}
            
            Resume:
            {resume_text}
            
            Please provide your analysis in this exact format:
            
            MATCH SCORE: [score from 1-10]
            
            KEY STRENGTHS:
            - [strength 1]
            - [strength 2]
            - [strength 3]
            
            MISSING QUALIFICATIONS:
            - [missing item 1]
            - [missing item 2]
            
            EXPERIENCE RELEVANCE:
            [assessment of experience relevance]
            
            EDUCATION ALIGNMENT:
            [assessment of education match]
            
            RECOMMENDATION:
            [HIRE/INTERVIEW/REJECT] - [brief reason]
            
            Be concise and specific in your analysis.
            """
        )
        
        # Define extraction prompt
        self.extraction_prompt = PromptTemplate(
            input_variables=["resume_text"],
            template="""
            Extract key information from this resume and format as JSON:
            
            Resume:
            {resume_text}
            
            Return only valid JSON in this format:
            {{
                "name": "candidate full name",
                "email": "email@example.com",
                "phone": "phone number",
                "skills": ["skill1", "skill2", "skill3"],
                "experience_years": "X years",
                "education": "highest degree and field",
                "current_role": "current or most recent job title",
                "summary": "brief professional summary"
            }}
            
            If information is not found, use "Not specified" as the value.
            """
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)
        self.extraction_chain = LLMChain(llm=self.llm, prompt=self.extraction_prompt)
    
    def analyze_resume(self, resume_text, job_description):
        """Analyze resume against job description using Llama2"""
        try:
            response = self.chain.run(
                resume_text=resume_text[:4000],  # Limit text length
                job_description=job_description[:2000]
            )
            return response
        except Exception as e:
            return f"Analysis error: {str(e)}"
    
    def extract_key_info(self, resume_text):
        """Extract structured information from resume"""
        try:
            response = self.extraction_chain.run(resume_text=resume_text[:3000])
            return response
        except Exception as e:
            return f"Extraction error: {str(e)}"
    
    def parse_score_from_analysis(self, analysis):
        """Extract numerical score from analysis text"""
        try:
            # Look for "MATCH SCORE: X" pattern
            score_match = re.search(r'MATCH SCORE:\s*(\d+)', analysis)
            if score_match:
                return int(score_match.group(1))
            
            # Alternative patterns
            score_patterns = [
                r'score[:\s]+(\d+)',
                r'(\d+)/10',
                r'(\d+)\s*out\s*of\s*10'
            ]
            
            for pattern in score_patterns:
                match = re.search(pattern, analysis, re.IGNORECASE)
                if match:
                    return int(match.group(1))
            
            return 5  # Default score if not found
        except:
            return 5
    
    def parse_recommendation_from_analysis(self, analysis):
        """Extract recommendation from analysis text"""
        try:
            # Look for recommendation section
            rec_match = re.search(r'RECOMMENDATION:\s*([A-Z]+)', analysis)
            if rec_match:
                return rec_match.group(1)
            
            # Alternative patterns
            if re.search(r'hire|recommend', analysis, re.IGNORECASE):
                return "HIRE"
            elif re.search(r'interview', analysis, re.IGNORECASE):
                return "INTERVIEW"
            elif re.search(r'reject', analysis, re.IGNORECASE):
                return "REJECT"
            
            return "REVIEW"
        except:
            return "REVIEW"

class BatchProcessor:
    def __init__(self, parser, analyzer):
        self.parser = parser
        self.analyzer = analyzer
    
    def process_multiple_resumes(self, resume_files, job_description):
        """Process multiple resumes and return sorted results"""
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, resume_file in enumerate(resume_files):
            status_text.text(f'Processing {resume_file.name}...')
            progress_bar.progress((i + 1) / len(resume_files))
            
            # Extract text
            resume_text = self.parser.extract_text_from_pdf(resume_file)
            
            if resume_text:
                # Get analysis
                analysis = self.analyzer.analyze_resume(resume_text, job_description)
                key_info = self.analyzer.extract_key_info(resume_text)
                
                # Parse results
                score = self.analyzer.parse_score_from_analysis(analysis)
                recommendation = self.analyzer.parse_recommendation_from_analysis(analysis)
                
                results.append({
                    'filename': resume_file.name,
                    'score': score,
                    'recommendation': recommendation,
                    'analysis': analysis,
                    'key_info': key_info,
                    'resume_text': resume_text[:500] + "..."  # Preview
                })
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Sort by score (highest first)
        return sorted(results, key=lambda x: x['score'], reverse=True)

def main():
    st.set_page_config(
        page_title="AI Resume Screener",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("🎯 AI-Powered Resume Screener")
    st.markdown("Upload resumes and job descriptions for intelligent screening using Llama2")
    
    # Check Ollama connection
    try:
        llm_test = Ollama(model="llama2", base_url="http://localhost:11434")
        st.success("✅ Connected to Ollama with Llama2")
    except:
        st.error("❌ Cannot connect to Ollama. Make sure it's running with llama2 model.")
        st.info("Run: `ollama pull llama2` and `ollama serve`")
        return
    
    # Initialize components
    parser = ResumeParser()
    analyzer = ResumeAnalyzer()
    batch_processor = BatchProcessor(parser, analyzer)
    
    # Sidebar for configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Job description input
    job_description = st.sidebar.text_area(
        "Job Description",
        height=300,
        placeholder="Enter the job description here...",
        help="Paste the complete job description including requirements, responsibilities, and qualifications."
    )
    
    # Advanced options
    with st.sidebar.expander("🔧 Advanced Options"):
        batch_mode = st.checkbox("Batch Processing Mode", value=True)
        show_detailed_analysis = st.checkbox("Show Detailed Analysis", value=True)
        auto_sort = st.checkbox("Auto-sort by Score", value=True)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Upload Resumes")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more resume PDF files"
        )
        
        if uploaded_files and job_description:
            if st.button("🚀 Start Analysis", type="primary"):
                if batch_mode and len(uploaded_files) > 1:
                    # Batch processing
                    st.header("🔍 Batch Analysis Results")
                    results = batch_processor.process_multiple_resumes(uploaded_files, job_description)
                    
                    # Store results in session state
                    st.session_state.results = results
                    
                else:
                    # Individual processing
                    st.header("🔍 Individual Analysis Results")
                    results = []
                    
                    for uploaded_file in uploaded_files:
                        st.subheader(f"📄 {uploaded_file.name}")
                        
                        with st.spinner("Processing..."):
                            resume_text = parser.extract_text_from_pdf(uploaded_file)
                            
                            if resume_text:
                                analysis = analyzer.analyze_resume(resume_text, job_description)
                                key_info = analyzer.extract_key_info(resume_text)
                                score = analyzer.parse_score_from_analysis(analysis)
                                recommendation = analyzer.parse_recommendation_from_analysis(analysis)
                                
                                results.append({
                                    'filename': uploaded_file.name,
                                    'score': score,
                                    'recommendation': recommendation,
                                    'analysis': analysis,
                                    'key_info': key_info
                                })
                        
                        st.divider()
                    
                    st.session_state.results = results
    
    with col2:
        if hasattr(st.session_state, 'results') and st.session_state.results:
            results = st.session_state.results
            
            st.header("📊 Results Dashboard")
            
            # Summary metrics
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Total Resumes", len(results))
            with col_b:
                avg_score = sum(r['score'] for r in results) / len(results)
                st.metric("Average Score", f"{avg_score:.1f}/10")
            with col_c:
                hire_count = sum(1 for r in results if r['recommendation'] == 'HIRE')
                st.metric("Recommended", hire_count)
            
            # Results table
            st.subheader("📈 Ranking Table")
            
            # Create DataFrame for display
            display_data = []
            for i, result in enumerate(results):
                display_data.append({
                    'Rank': i + 1,
                    'Resume': result['filename'],
                    'Score': f"{result['score']}/10",
                    'Recommendation': result['recommendation'],
                    'Status': "🟢" if result['recommendation'] == 'HIRE' else 
                             "🟡" if result['recommendation'] == 'INTERVIEW' else "🔴"
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Detailed results
            if show_detailed_analysis:
                st.subheader("📋 Detailed Analysis")
                
                selected_resume = st.selectbox(
                    "Select resume for detailed view:",
                    options=[r['filename'] for r in results],
                    index=0
                )
                
                # Find selected result
                selected_result = next(r for r in results if r['filename'] == selected_resume)
                
                # Display detailed analysis
                with st.expander("🔍 Full Analysis", expanded=True):
                    st.write(selected_result['analysis'])
                
                with st.expander("📝 Extracted Information"):
                    st.code(selected_result['key_info'])
                
                # Download results
                st.subheader("📥 Export Results")
                
                # Prepare data for export
                export_data = []
                for result in results:
                    export_data.append({
                        'Filename': result['filename'],
                        'Score': result['score'],
                        'Recommendation': result['recommendation'],
                        'Analysis': result['analysis'],
                        'Key_Info': result['key_info']
                    })
                
                export_df = pd.DataFrame(export_data)
                csv = export_df.to_csv(index=False)
                
                st.download_button(
                    label="Download Results as CSV",
                    data=csv,
                    file_name="resume_screening_results.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
