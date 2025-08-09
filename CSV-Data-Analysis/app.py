import streamlit as st
import pandas as pd
import numpy as np
# FIXED IMPORTS
from langchain_ollama import OllamaLLM  # Correct import
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64

# Configure Streamlit page (ONLY ONCE!)
st.set_page_config(
    page_title="CSV Data Analyzer",
    page_icon="📊",
    layout="wide"
)

# Initialize Ollama LLM (SINGLE DEFINITION)
@st.cache_resource
def initialize_llm():
    """Initialize Ollama Llama2 model"""
    try:
        llm = OllamaLLM(  # Updated class name
            model="llama2",
            temperature=0.1,
            num_predict=512
        )
        return llm
    except Exception as e:
        st.error(f"Error initializing Ollama: {str(e)}")
        st.info("Make sure Ollama is installed and Llama2 model is available")
        return None

# Function to create pandas agent
def create_agent(df, llm):
    """Create pandas dataframe agent with LangChain"""
    try:
        agent = create_pandas_dataframe_agent(
            llm=llm,
            df=df,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            allow_dangerous_code=True  # Required for pandas operations
        )
        return agent
    except Exception as e:
        st.error(f"Error creating agent: {str(e)}")
        return None

# Function to generate data summary
def generate_summary(df):
    """Generate basic data summary"""
    summary = {
        "Shape": df.shape,
        "Columns": df.columns.tolist(),
        "Data Types": df.dtypes.to_dict(),
        "Missing Values": df.isnull().sum().to_dict(),
        "Numeric Summary": df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else "No numeric columns"
    }
    return summary

# Function to create visualizations
def create_visualization(df, chart_type, x_col=None, y_col=None):
    """Create different types of visualizations"""
    fig = None
    
    if chart_type == "Histogram":
        if x_col and pd.api.types.is_numeric_dtype(df[x_col]):
            fig = px.histogram(df, x=x_col, title=f"Histogram of {x_col}")
    
    elif chart_type == "Scatter Plot":
        if x_col and y_col and pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
            fig = px.scatter(df, x=x_col, y=y_col, title=f"Scatter Plot: {x_col} vs {y_col}")
    
    elif chart_type == "Bar Chart":
        if x_col:
            if pd.api.types.is_numeric_dtype(df[x_col]):
                fig = px.bar(df.head(20), x=df.index[:20], y=x_col, title=f"Bar Chart of {x_col}")
            else:
                value_counts = df[x_col].value_counts().head(20)
                fig = px.bar(x=value_counts.index, y=value_counts.values, 
                           title=f"Value Counts of {x_col}")
    
    elif chart_type == "Line Chart":
        if x_col and y_col and pd.api.types.is_numeric_dtype(df[y_col]):
            fig = px.line(df, x=x_col, y=y_col, title=f"Line Chart: {x_col} vs {y_col}")
    
    elif chart_type == "Correlation Heatmap":
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                          title="Correlation Heatmap")
    
    return fig

# Main Streamlit app
def main():
    st.title("📊 CSV Data Analyzer with LangChain & Ollama")
    st.markdown("Upload a CSV file and analyze it using natural language queries powered by Llama2")
    
    # Initialize LLM
    llm = initialize_llm()
    
    if llm is None:
        st.stop()
    
    # Sidebar for file upload and settings
    with st.sidebar:
        st.header("Upload & Settings")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload a CSV file to analyze"
        )
        
        if uploaded_file is not None:
            # Load data
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"File uploaded successfully! Shape: {df.shape}")
                
                # Display basic info
                st.subheader("Dataset Info")
                st.write(f"**Rows:** {df.shape[0]}")
                st.write(f"**Columns:** {df.shape[1]}")
                st.write(f"**Memory Usage:** {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                st.stop()
    
    # Main content area
    if uploaded_file is not None:
        # Create tabs for different functionalities
        tab1, tab2, tab3, tab4 = st.tabs(["🔍 Data Overview", "💬 Natural Language Query", "📈 Visualizations", "📋 Data Summary"])
        
        with tab1:
            st.header("Data Overview")
            
            # Display first few rows
            st.subheader("First 10 Rows")
            st.dataframe(df.head(10))
            
            # Column information
            st.subheader("Column Information")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Data Type': df.dtypes,
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum(),
                'Unique Values': df.nunique()
            })
            st.dataframe(col_info)
        
        with tab2:
            st.header("Natural Language Query")
            st.markdown("Ask questions about your data in natural language!")
            
            # Create agent
            agent = create_agent(df, llm)
            
            if agent:
                # Example queries
                st.subheader("Example Queries")
                examples = [
                    "What are the column names in this dataset?",
                    "Show me basic statistics for numerical columns",
                    "What is the shape of the dataset?",
                    "Are there any missing values?",
                    "Show me the first 5 rows",
                    "What is the correlation between numerical columns?",
                    "Find outliers in the numerical columns"
                ]
                
                selected_example = st.selectbox("Select an example query:", [""] + examples)
                
                # Query input
                if selected_example:
                    query = st.text_area("Your Query:", value=selected_example, height=100)
                else:
                    query = st.text_area("Your Query:", placeholder="Enter your question about the data...", height=100)
                
                if st.button("Analyze", type="primary"):
                    if query:
                        with st.spinner("Analyzing your query..."):
                            try:
                                response = agent.run(query)
                                st.subheader("Analysis Result:")
                                st.write(response)
                                
                            except Exception as e:
                                st.error(f"Error processing query: {str(e)}")
                                st.info("Try rephrasing your question or use a simpler query.")
                    else:
                        st.warning("Please enter a query.")
            else:
                st.error("Could not create analysis agent. Please check your Ollama setup.")
        
        with tab3:
            st.header("Data Visualizations")
            
            # Visualization controls
            col1, col2 = st.columns(2)
            
            with col1:
                chart_type = st.selectbox(
                    "Select Chart Type:",
                    ["Histogram", "Scatter Plot", "Bar Chart", "Line Chart", "Correlation Heatmap"]
                )
            
            with col2:
                columns = df.columns.tolist()
                numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if chart_type in ["Histogram", "Bar Chart"]:
                    x_col = st.selectbox("Select Column:", columns)
                    y_col = None
                elif chart_type in ["Scatter Plot", "Line Chart"]:
                    x_col = st.selectbox("Select X Column:", columns)
                    y_col = st.selectbox("Select Y Column:", columns)
                else:
                    x_col = None
                    y_col = None
            
            # Generate visualization
            if st.button("Generate Chart", type="primary"):
                fig = create_visualization(df, chart_type, x_col, y_col)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Could not generate chart. Please check your column selections and data types.")
        
        with tab4:
            st.header("Detailed Data Summary")
            
            # Generate comprehensive summary
            summary = generate_summary(df)
            
            # Display summary sections
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Dataset Shape")
                st.write(f"Rows: {summary['Shape'][0]}")
                st.write(f"Columns: {summary['Shape'][1]}")
                
                st.subheader("Column Names")
                for i, col in enumerate(summary['Columns'], 1):
                    st.write(f"{i}. {col}")
            
            with col2:
                st.subheader("Data Types")
                for col, dtype in summary['Data Types'].items():
                    st.write(f"**{col}:** {dtype}")
                
                st.subheader("Missing Values")
                missing_data = [(col, count) for col, count in summary['Missing Values'].items() if count > 0]
                if missing_data:
                    for col, count in missing_data:
                        st.write(f"**{col}:** {count} missing")
                else:
                    st.write("✅ No missing values found")
            
            # Numeric summary
            if summary['Numeric Summary'] != "No numeric columns":
                st.subheader("Numerical Statistics")
                numeric_df = pd.DataFrame(summary['Numeric Summary'])
                st.dataframe(numeric_df)
            
            # Download processed data
            st.subheader("Download Data")
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv"
            )
    
    else:
        # Welcome message
        st.markdown("""
        ## Welcome to CSV Data Analyzer! 🎉
        
        This application allows you to:
        - **Upload CSV files** and explore your data
        - **Ask natural language questions** about your dataset using Llama2
        - **Create visualizations** with interactive charts
        - **Generate comprehensive summaries** of your data
        
        ### Getting Started:
        1. Make sure you have Ollama installed with Llama2 model
        2. Upload a CSV file using the sidebar
        3. Explore your data using the different tabs
        
        ### Prerequisites:
        ```
        # Install Ollama
        curl -fsSL https://ollama.com/install.sh | sh
        
        # Pull Llama2 model
        ollama pull llama2
        ```
        """)

if __name__ == "__main__":
    main()
