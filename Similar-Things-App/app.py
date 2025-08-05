import streamlit as st
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

from langchain_community.document_loaders.csv_loader import CSVLoader

# Setup page
st.set_page_config(page_title="Educate Kids", page_icon=":robot:")
st.header("Hey, Ask me something & I will give out similar things")

# Load environment variables if any (optional with Ollama)
load_dotenv()

# Ollama Embeddings (choose model as per your setup)
embeddings = OllamaEmbeddings(model="nomic-embed-text")  # or mxbai-embed-large, all-minilm, etc.

# Load data
loader = CSVLoader(file_path='data.csv', csv_args={
    'delimiter': ',',
    'quotechar': '"',
    'fieldnames': ['Words']
})
data = loader.load()

# Build FAISS vectorstore
db = FAISS.from_documents(data, embeddings)

def get_text():
    input_text = st.text_input("You: ", key='input_text')
    return input_text

user_input = get_text()
submit = st.button('Find similar Things')

if submit and user_input:
    docs = db.similarity_search(user_input, k=2)
    st.subheader("Top Matches:")
    if len(docs) > 0:
        st.text(docs[0].page_content)
    if len(docs) > 1:
        st.text(docs[1].page_content)
