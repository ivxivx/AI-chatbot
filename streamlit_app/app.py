from streamlit_datalist import stDatalist
import streamlit as st
from dotenv import load_dotenv
import model.transform as tf 
from htmlTemplates import css, bot_template, user_template

st.set_page_config(page_title="Chat",
                       page_icon=":page_facing_up:")
st.write(css, unsafe_allow_html=True)

    
def handle_userinput(user_question):
    if st.session_state.conversation == None: 
        return
    
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)

    
def main():
    load_dotenv()
    
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.title(':orange[Chat]')
    user_question = stDatalist("Ask a question", [
            "What is your name", 
            "What are your hobbies", 
            "Do you have email address",
            "Are you now in Malaysia",
            "When did you work at Amber Group",
            "What is your tech stack at Triple A",
            "Have you completed bachelor degree"
        ])
    
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader(":orange[Your documents]")
        uploaded_files = st.file_uploader(
                ":blue[Upload files here and click on 'Process Document']. Accepts :red[text files only.]",
                accept_multiple_files=True)
        
        if st.button("Process Document"):
            if uploaded_files:
                with st.spinner("Processing document(s)"):
                    # get file content as text
                    raw_text = tf.extract_docs(uploaded_files)

                    # get the text chunks
                    text_chunks = tf.chunk_texts(raw_text)

                    # create vector store
                    vectorstore = tf.get_vectorstore(text_chunks)

                    # create conversation chain
                    st.session_state.conversation = tf.get_chain(vectorstore)
            
                
if __name__ == '__main__':
    main()