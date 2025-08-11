import streamlit as st
import requests
import json
import time

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
HEADERS = {"Content-Type": "application/json"}

def call_ollama_api(prompt, model="llama2"):
    """Make API call to Ollama"""
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, headers=HEADERS, json=data)
        if response.status_code == 200:
            return response.json().get("response", "Error: No response received")
        else:
            return f"Error: API returned status code {response.status_code}"
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"

def generate_youtube_script(topic, duration, target_audience, tone):
    """Generate YouTube script using Llama 2"""
    
    prompt = f"""
    Create a compelling YouTube video script with the following specifications:
    
    Topic: {topic}
    Duration: {duration} minutes
    Target Audience: {target_audience}
    Tone: {tone}
    
    Please structure the script with:
    1. Hook (first 15 seconds) - grab attention immediately
    2. Introduction - introduce yourself and the topic
    3. Main Content - break into 3-4 key points with examples
    4. Call to Action - encourage engagement
    5. Outro - thank viewers and promote next video
    
    Include engagement cues like "pause and think about this" or "comment below your thoughts".
    Make it conversational and natural for speaking.
    
    Format the script clearly with timestamps and section headers.
    """
    
    return call_ollama_api(prompt)

def generate_video_titles(topic, count=5):
    """Generate multiple title options"""
    
    prompt = f"""
    Generate {count} catchy, click-worthy YouTube video titles for the topic: {topic}
    
    Make them:
    - Attention-grabbing and curiosity-inducing
    - Between 40-60 characters
    - Include numbers, questions, or power words when appropriate
    - Suitable for YouTube's algorithm
    
    List them as:
    1. Title one
    2. Title two
    etc.
    """
    
    return call_ollama_api(prompt)

def generate_video_description(topic, script_preview):
    """Generate video description"""
    
    prompt = f"""
    Create a YouTube video description for a video about: {topic}
    
    Script preview: {script_preview[:200]}...
    
    Include:
    - Compelling opening line
    - Brief summary of what viewers will learn
    - Timestamps for main sections
    - Call to action for likes/subscribes
    - Relevant hashtags (5-10)
    
    Keep it under 200 words but informative and engaging.
    """
    
    return call_ollama_api(prompt)

def main():
    # Page configuration
    st.set_page_config(
        page_title="AI YouTube Script Writer",
        page_icon="📹",
        layout="wide"
    )
    
    # Header
    st.title("📹 AI YouTube Script Writer")
    st.markdown("*Powered by Ollama Llama 2*")
    st.markdown("---")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Script Settings")
        
        # Topic input
        topic = st.text_input(
            "Video Topic*", 
            placeholder="e.g., How to start a YouTube channel",
            help="What is your video about?"
        )
        
        # Duration slider
        duration = st.slider(
            "Video Duration (minutes)", 
            min_value=1, 
            max_value=30, 
            value=10,
            help="How long should your video be?"
        )
        
        # Target audience
        target_audience = st.selectbox(
            "Target Audience",
            ["General Audience", "Beginners", "Intermediate", "Advanced", "Kids", "Teens", "Adults"]
        )
        
        # Tone selection
        tone = st.selectbox(
            "Tone/Style",
            ["Conversational", "Educational", "Entertaining", "Professional", "Casual", "Inspirational"]
        )
        
        # Generate button
        generate_script = st.button("🚀 Generate Script", type="primary")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if generate_script and topic:
            with st.spinner("Generating your YouTube script..."):
                # Generate script
                script = generate_youtube_script(topic, duration, target_audience, tone)
                
                st.subheader("📝 Your YouTube Script")
                st.text_area("Script Content", script, height=600, key="script_output")
                
                # Download button
                st.download_button(
                    label="💾 Download Script",
                    data=script,
                    file_name=f"youtube_script_{topic.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
        
        elif generate_script and not topic:
            st.error("Please enter a video topic!")
        
        else:
            st.info("👈 Enter your video details in the sidebar and click 'Generate Script' to get started!")
    
    with col2:
        if generate_script and topic:
            st.subheader("💡 Additional Tools")
            
            # Generate titles
            if st.button("Generate Title Ideas"):
                with st.spinner("Creating title options..."):
                    titles = generate_video_titles(topic)
                    st.text_area("Title Suggestions", titles, height=200)
            
            # Generate description
            if st.button("Generate Description"):
                with st.spinner("Writing description..."):
                    # Use first part of script if available
                    script_preview = script[:200] if 'script' in locals() else topic
                    description = generate_video_description(topic, script_preview)
                    st.text_area("Video Description", description, height=250)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        **Tips for better scripts:**
        - Be specific with your topic
        - Consider your audience's knowledge level
        - Test different tones for your niche
        - Always review and personalize the generated content
        """
    )

if __name__ == "__main__":
    main()
