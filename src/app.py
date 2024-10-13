import os
import json
import pandas as pd
from openai import OpenAI
import pdfplumber
import streamlit as st
from pypdf import PdfReader



#set page title
st.title("Alpaca 3")

#config api key
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))
client = OpenAI(
    api_key = config_data["OPENAI_API_KEY"]
)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

print(st.session_state["openai_model"])  # Debugging

#initialize chat session if no previous session exists
if "messages" not in st.session_state:
    st.session_state.messages = []

#display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#take user input
if user_input := st.chat_input("Enter message:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)


    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        result = ""
        full_response = ""
        
        #create a response for user input
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            
            #get the response from gpt model
            result = response.choices[0].delta.content
            if(isinstance(result, str)):
                full_response += result
            
            message_placeholder.markdown(full_response + "▌")

    #add message to history
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})
    #remove the ▌ thingy
    message_placeholder.markdown(full_response)

def read_pdf(file):
    allText = ""
    pdfReader = PdfReader(file)
    for i in range(len(pdfReader.pages)):
        page = pdfReader.pages[i]
        allText += page.extract_text()

    return allText    

#file upload
df = st.file_uploader("Upload your file",
    type = ["pdf"])
if st.button("Analyze"):
    if df is not None:
        raw_text = read_pdf(df)
        st.session_state.messages.append({"role": "user", "content": raw_text})
        st.chat_message("user").markdown(raw_text)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            result = ""
            full_response = ""
        
        #create a response for user input
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            
            #get the response from gpt model
            result = response.choices[0].delta.content
            if(isinstance(result, str)):
                full_response += result
            
            message_placeholder.markdown(full_response + "▌")

        #add message to history
        st.session_state.messages.append(
        {"role": "assistant", "content": full_response})
        #remove the ▌ thingy
        message_placeholder.markdown(full_response)

        #user_input = raw_text
        #if(df.type == "application/pdf"):
        #    try:
        #        with pdfplumber.open(df) as pdf:
        #            pages = pdf.pages[0]
        #            st.write(pages.extract_text())
        #    except:
        #        st.write("None")

#df_list = tabula.read_pdf(df, pages="all")
#if(df_list):
#    df = df_list[0]
#    print(df.head())


