import streamlit as st
from streamlit_chat import message
from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import (ConversationBufferMemory, 
                                                  ConversationSummaryMemory, 
                                                  ConversationBufferWindowMemory)

if 'conversation' not in st.session_state:
    st.session_state['conversation'] = None
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'ollama_model' not in st.session_state:
    st.session_state['ollama_model'] = 'llama2'

# Setting page title and header
st.set_page_config(page_title="Ollama Chat Clone", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>How can I assist you? </h1>", unsafe_allow_html=True)

st.sidebar.title("🦙 Ollama")
# Model selection dropdown
available_models = ['llama2', 'codellama', 'mistral', 'neural-chat', 'starling-lm', 'llama2-uncensored', 'orca-mini']
st.session_state['ollama_model'] = st.sidebar.selectbox("Choose Ollama Model:", available_models)

# Base URL configuration (optional)
ollama_base_url = st.sidebar.text_input("Ollama Base URL (optional):", value="http://localhost:11434", help="Leave default if running Ollama locally")

summarise_button = st.sidebar.button("Summarise the conversation", key="summarise")
if summarise_button:
    if st.session_state['conversation'] and hasattr(st.session_state['conversation'].memory, 'buffer'):
        summarise_placeholder = st.sidebar.write("Nice chatting with you my friend ❤️:\n\n" + st.session_state['conversation'].memory.buffer)
    else:
        st.sidebar.write("No conversation to summarise yet!")

def getresponse(userInput, model_name, base_url):
    if st.session_state['conversation'] is None:
        try:
            # Initialize Ollama LLM
            llm = Ollama(
                model=model_name,
                base_url=base_url,
                temperature=0.7,
                # num_predict=256,  # Limit response length if needed
            )
            
            # Create conversation chain with summary memory
            st.session_state['conversation'] = ConversationChain(
                llm=llm,
                verbose=True,
                memory=ConversationBufferMemory()  # Using BufferMemory instead of SummaryMemory for better compatibility
            )
        except Exception as e:
            st.error(f"Error connecting to Ollama: {e}")
            return "Sorry, I'm having trouble connecting to the Ollama service. Please make sure Ollama is running."
    
    try:
        response = st.session_state['conversation'].predict(input=userInput)
        print(st.session_state['conversation'].memory.buffer)
        return response
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "Sorry, I encountered an error while generating a response."

response_container = st.container()
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("Your question goes here:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            st.session_state['messages'].append(user_input)
            model_response = getresponse(user_input, st.session_state['ollama_model'], ollama_base_url)
            st.session_state['messages'].append(model_response)

            with response_container:
                for i in range(len(st.session_state['messages'])):
                    if (i % 2) == 0:
                        message(st.session_state['messages'][i], is_user=True, key=str(i) + '_user')
                    else:
                        message(st.session_state['messages'][i], key=str(i) + '_AI')

# Add connection status indicator
with st.sidebar:
    st.markdown("---")
    if st.button("Test Ollama Connection"):
        try:
            test_llm = Ollama(model=st.session_state['ollama_model'], base_url=ollama_base_url)
            test_response = test_llm.invoke("Hello")
            st.success("✅ Ollama connection successful!")
        except Exception as e:
            st.error(f"❌ Connection failed: {e}")
