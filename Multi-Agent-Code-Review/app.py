import streamlit as st
import time
from agents import MultiAgentCodeReviewer
import json

# Page configuration
st.set_page_config(
    page_title="🤖 Multi-Agent Code Reviewer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .agent-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #ff6b6b;
    }
    .security-card { border-left-color: #e74c3c; }
    .performance-card { border-left-color: #f39c12; }
    .style-card { border-left-color: #3498db; }
    .beginner-card { border-left-color: #2ecc71; }
    .architecture-card { border-left-color: #9b59b6; }
    
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'reviewer' not in st.session_state:
    with st.spinner("🚀 Initializing AI agents..."):
        st.session_state.reviewer = MultiAgentCodeReviewer()

# Header
st.title("🤖 Multi-Agent Code Review System")
st.markdown("**Five AI experts reviewing your code from different perspectives**")

# Sidebar
with st.sidebar:
    st.header("🎯 Meet Your AI Team")
    
    agents_info = {
        "🛡️ SecureBot": "Security vulnerabilities hunter",
        "⚡ SpeedDemon": "Performance optimization expert", 
        "🎨 StyleGuru": "Code aesthetics and best practices",
        "👨‍🏫 TeachBot": "Beginner-friendly explanations",
        "🏗️ ArchitectMind": "System design and architecture"
    }
    
    for agent, description in agents_info.items():
        st.markdown(f"**{agent}**")
        st.caption(description)
        st.markdown("---")
    
    st.header("📊 Statistics")
    if 'review_count' not in st.session_state:
        st.session_state.review_count = 0
    st.metric("Reviews Completed", st.session_state.review_count)

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Submit Your Code")
    
    # Language selection
    language = st.selectbox(
        "Programming Language",
        ["python", "javascript", "java", "cpp", "c", "go", "rust", "typescript", "sql"],
        index=0
    )
    
    # Code input
    code_input = st.text_area(
        "Paste your code here:",
        height=400,
        placeholder=f"// Paste your {language} code here...\n\nfunction example() {{\n    // Your code\n}}",
        help="Paste the code you want reviewed by our AI agent team"
    )
    
    # Review button
    review_button = st.button("🔍 Start Review", type="primary", use_container_width=True)

with col2:
    st.header("📋 Review Results")
    
    if review_button and code_input.strip():
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Start review
        with st.spinner("🤖 AI agents are analyzing your code..."):
            status_text.text("Initializing review process...")
            progress_bar.progress(10)
            
            # Get reviews from all agents
            reviews = st.session_state.reviewer.review_code(code_input, language)
            
            # Update progress
            progress_bar.progress(80)
            status_text.text("Generating summary...")
            
            # Get summary
            summary = st.session_state.reviewer.get_summary_review(reviews)
            
            progress_bar.progress(100)
            status_text.text("Review complete! ✅")
            
            # Update statistics
            st.session_state.review_count += 1
            
        # Display results
        st.success("Review completed successfully!")
        
        # Summary section
        st.subheader("📊 Executive Summary")
        st.markdown(summary)
        
        # Individual agent reviews
        st.subheader("🤖 Individual Agent Reviews")
        
        agent_colors = {
            "SecureBot": "security-card",
            "SpeedDemon": "performance-card", 
            "StyleGuru": "style-card",
            "TeachBot": "beginner-card",
            "ArchitectMind": "architecture-card"
        }
        
        agent_icons = {
            "SecureBot": "🛡️",
            "SpeedDemon": "⚡",
            "StyleGuru": "🎨", 
            "TeachBot": "👨‍🏫",
            "ArchitectMind": "🏗️"
        }
        
        for agent_name, review_data in reviews.items():
            with st.expander(f"{agent_icons[agent_name]} {agent_name} Review", expanded=True):
                if review_data['status'] == 'success':
                    st.markdown(f'<div class="agent-card {agent_colors[agent_name]}">{review_data["review"]}</div>', 
                              unsafe_allow_html=True)
                else:
                    st.error(f"Error from {agent_name}: {review_data['review']}")
        
        # Download option
        st.subheader("💾 Export Review")
        review_report = {
            "code": code_input,
            "language": language,
            "summary": summary,
            "reviews": reviews,
            "timestamp": time.time()
        }
        
        st.download_button(
            label="📄 Download Full Review Report",
            data=json.dumps(review_report, indent=2),
            file_name=f"code_review_{language}_{int(time.time())}.json",
            mime="application/json"
        )
    
    elif review_button and not code_input.strip():
        st.error("Please paste some code to review!")
    
    else:
        st.info("👆 Paste your code and click 'Start Review' to get feedback from all 5 AI agents!")