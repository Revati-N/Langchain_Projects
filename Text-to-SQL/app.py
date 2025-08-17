import streamlit as st
import sqlite3
import pandas as pd
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama

# Page configuration
st.set_page_config(
    page_title="Text-to-SQL with Llama 2",
    page_icon="🗃️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sql-query {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
    }
    .result-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False

def create_sample_database():
    """Create a sample SQLite database with sample data"""
    conn = sqlite3.connect('database/sample.db')
    cursor = conn.cursor()
    
    # Create employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            salary INTEGER,
            hire_date TEXT
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER
        )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute('SELECT COUNT(*) FROM employees')
    if cursor.fetchone()[0] == 0:
        sample_employees = [
            (1, 'John Doe', 'Engineering', 75000, '2022-01-15'),
            (2, 'Jane Smith', 'Marketing', 65000, '2021-03-20'),
            (3, 'Mike Johnson', 'Sales', 55000, '2023-02-10'),
            (4, 'Sarah Wilson', 'Engineering', 80000, '2020-11-05'),
            (5, 'Bob Brown', 'HR', 60000, '2022-07-18')
        ]
        cursor.executemany('INSERT INTO employees VALUES (?, ?, ?, ?, ?)', sample_employees)
    
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            (1, 'Laptop', 'Electronics', 1200.00, 50),
            (2, 'Mouse', 'Electronics', 25.00, 200),
            (3, 'Desk Chair', 'Furniture', 300.00, 30),
            (4, 'Monitor', 'Electronics', 400.00, 75),
            (5, 'Coffee Mug', 'Office Supplies', 15.00, 100)
        ]
        cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?, ?)', sample_products)
    
    conn.commit()
    conn.close()

@st.cache_resource
def initialize_llm_and_db():
    """Initialize LLM and database connection"""
    try:
        # Initialize Ollama with Llama 2
        llm = Ollama(
            model="llama2",
            temperature=0,
            callback_manager=None
        )
        
        # Create sample database if it doesn't exist
        import os
        os.makedirs('database', exist_ok=True)
        create_sample_database()
        
        # Connect to database
        db = SQLDatabase.from_uri("sqlite:///database/sample.db")
        
        return llm, db
    except Exception as e:
        st.error(f"Error initializing LLM or database: {str(e)}")
        return None, None

def create_sql_chain(llm, db):
    """Create SQL query chain"""
    # Custom prompt template for better SQL generation
    sql_prompt = PromptTemplate.from_template("""
    Given an input question, create a syntactically correct SQLite query to run.
    Use the following format:
    
    Question: {question}
    
    Only return the SQL query, nothing else. Do not include any explanations or additional text.
    
    Here is the relevant table info: {table_info}
    
    Question: {question}
    """)
    
    return create_sql_query_chain(llm, db, prompt=sql_prompt)

def execute_query_and_get_answer(question, llm, db):
    """Execute natural language question and return SQL + results"""
    try:
        # Create SQL query chain
        write_query = create_sql_query_chain(llm, db)
        
        # Create execution tool
        execute_query = QuerySQLDataBaseTool(db=db)
        
        # Chain them together
        chain = write_query | execute_query
        
        # Get the SQL query first
        sql_query = write_query.invoke({"question": question})
        
        # Execute and get results
        result = chain.invoke({"question": question})
        
        return sql_query, result
    
    except Exception as e:
        return None, f"Error: {str(e)}"

def main():
    st.markdown('<h1 class="main-header">🗃️ Text-to-SQL with Llama 2</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Database info
        st.subheader("📊 Database Info")
        if st.button("🔄 Refresh Database Connection"):
            st.cache_resource.clear()
            st.rerun()
        
        # Model settings
        st.subheader("🤖 Model Settings")
        st.info("Using Ollama with Llama 2")
        
        # Clear chat history
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Initialize LLM and database
    llm, db = initialize_llm_and_db()
    
    if llm is None or db is None:
        st.error("Failed to initialize LLM or database. Please check your Ollama installation.")
        st.stop()
    
    # Display database schema
    with st.expander("📋 View Database Schema", expanded=False):
        try:
            table_info = db.get_table_info()
            st.code(table_info, language="sql")
        except Exception as e:
            st.error(f"Error getting table info: {str(e)}")
    
    # Main chat interface
    st.subheader("💬 Ask a question about your data")
    
    # Example questions
    st.markdown("**Example questions:**")
    example_questions = [
        "How many employees are in each department?",
        "What is the average salary by department?",
        "Show me all products with price greater than $100",
        "Which employee has the highest salary?",
        "How many products are in the Electronics category?"
    ]
    
    cols = st.columns(len(example_questions))
    for i, question in enumerate(example_questions):
        if cols[i % len(cols)].button(f"💡 {question[:30]}...", key=f"example_{i}"):
            st.session_state.current_question = question
    
    # Question input
    question = st.text_input(
        "Enter your question:",
        value=st.session_state.get('current_question', ''),
        placeholder="e.g., How many employees work in Engineering?",
        key="question_input"
    )
    
    # Submit button
    if st.button("🚀 Submit Query", type="primary") and question:
        with st.spinner("Processing your question..."):
            sql_query, result = execute_query_and_get_answer(question, llm, db)
            
            if sql_query:
                # Display generated SQL
                st.markdown("### 📝 Generated SQL Query")
                st.markdown(f'<div class="sql-query"><code>{sql_query}</code></div>', unsafe_allow_html=True)
                
                # Display results
                st.markdown("### 📊 Query Results")
                if result and result != "[]":
                    try:
                        # Try to parse as a list and create DataFrame
                        import ast
                        if result.startswith('[') and result.endswith(']'):
                            data = ast.literal_eval(result)
                            if data:
                                df = pd.DataFrame(data)
                                st.dataframe(df, use_container_width=True)
                            else:
                                st.info("No results found.")
                        else:
                            st.code(result)
                    except:
                        st.code(result)
                else:
                    st.info("No results found.")
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "question": question,
                    "sql": sql_query,
                    "result": result
                })
            
            else:
                st.error(f"Failed to generate SQL query: {result}")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 📝 Query History")
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5
            with st.expander(f"Q{len(st.session_state.chat_history)-i}: {chat['question'][:50]}..."):
                st.markdown("**Question:**")
                st.write(chat['question'])
                st.markdown("**Generated SQL:**")
                st.code(chat['sql'], language="sql")
                st.markdown("**Result:**")
                st.code(chat['result'])

if __name__ == "__main__":
    main()
