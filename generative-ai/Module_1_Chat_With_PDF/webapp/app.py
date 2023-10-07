import streamlit as st
import uuid
import os
import boto3
import requests
import api
from boto3 import Session
import botocore.session
import json
#from langchain.callbacks.base import BaseCallbackHandler


USER_ICON = "images/user-icon.png"
AI_ICON = "images/opensearch-twitter-card.png"

# Check if the user ID is already stored in the session state
if 'user_id' in st.session_state:
    user_id = st.session_state['user_id']
    print(f"User ID: {user_id}")

# If the user ID is not yet stored in the session state, generate a random UUID
else:
    user_id = str(uuid.uuid4())
    st.session_state['user_id'] = user_id


if 'session_id' not in st.session_state:
    st.session_state['session_id'] = ""
    
if "chats" not in st.session_state:
    st.session_state.chats = [
        {
            'id': 0,
            'question': '',
            'answer': ''
        }
    ]

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = []

if "input" not in st.session_state:
    st.session_state.input = ""



def write_logo():
    col1, col2, col3 = st.columns([5, 1, 5])
    with col2:
        st.image(AI_ICON, use_column_width='always') 

def write_top_bar():
    col1, col2, col3 = st.columns([1,10,2])
    with col1:
        st.image(AI_ICON, use_column_width='always')
    with col2:
        st.subheader("Chat with your PDF using OpenSearch")
    with col3:
        clear = st.button("Clear Chat")
    return clear

clear = write_top_bar()

if clear:
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.input = ""
    

def handle_input():
    input = st.session_state.input
    print("Handling input: ", input)
    question_with_id = {
        'question': input,
        'id': len(st.session_state.questions)
    }
    st.session_state.questions.append(question_with_id)
    st.session_state.answers.append({
        'answer': api.call(input, st.session_state['session_id']),
        'id': len(st.session_state.questions)
    })
    st.session_state.input = ""



def write_user_message(md):
    col1, col2 = st.columns([1,12])
    
    with col1:
        st.image(USER_ICON, use_column_width='always')
    with col2:
        st.warning(md['question'])

# class StreamHandler(BaseCallbackHandler):
#     def __init__(self, container, initial_text=""):
#         self.container = container
#         self.text=initial_text
#     def on_llm_new_token(self, token: str, **kwargs) -> None:
#         # "/" is a marker to show difference 
#         # you don't need it 
#         self.text+=token+"/" 
#         self.container.markdown(self.text) 

def render_answer(answer):
    col1, col2 = st.columns([1,12])
    with col1:
        st.image(AI_ICON, use_column_width='always')
    with col2:
        # chat_box=st.empty() 
        # self.text+=token+"/" 
        # self.container.markdown(self.text) 
        st.markdown(answer,unsafe_allow_html=True)
    
#Each answer will have context of the question asked in order to associate the provided feedback with the respective question
def write_chat_message(md, q):
    if('body' in md['answer']):
        res = json.loads(md['answer']['body'])
    else:
        res = md['answer']
    st.session_state['session_id'] = res['session_id']
    chat = st.container()
    with chat:
        render_answer(res["response"])
    
        
with st.container():
  for (q, a) in zip(st.session_state.questions, st.session_state.answers):
    print("answers----")
    print(a)
    write_user_message(q)
    write_chat_message(a, q)

st.markdown('---')
input = st.text_input("You are talking to the uploaded PDF, ask any question.", key="input", on_change=handle_input)
with st.sidebar:
    st.subheader("Sample PDF(s)")

    

    # Initialize boto3 to use the S3 client.
    s3_client = boto3.resource('s3')
    bucket=s3_client.Bucket('pdf-repo-uploads')

    objects = bucket.objects.filter(Prefix="sample_pdfs/")
    urls = []

    client = boto3.client('s3')

    for obj in objects:
        if obj.key.endswith('.pdf'): 

            # Generate the S3 presigned URL
            s3_presigned_url = client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': 'pdf-repo-uploads',
                    'Key': obj.key
                },
                ExpiresIn=3600
            )

            # Print the created S3 presigned URL
            print(s3_presigned_url)
            urls.append(s3_presigned_url)
            st.write("["+obj.key.split('/')[1]+"]("+s3_presigned_url+")")
    
    st.subheader("Your documents")
    pdf_docs = st.file_uploader(
        "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
    if st.button("Process"):
        with st.spinner("Processing"):
            for pdf_doc in pdf_docs:
                print(type(pdf_doc))
                pdf_doc_name = (pdf_doc.name).replace(" ","_")
                print("aws s3 cp pdfs"+pdf_doc_name+" s3://pdf-repo-uploads/")
                with open(os.path.join("pdfs",pdf_doc_name),"wb") as f: 
                    f.write(pdf_doc.getbuffer())  
                    os.system("aws s3 cp pdfs/"+pdf_doc_name+" s3://pdf-repo-uploads/")
                request_ = '{ "bucket": "pdf-repo-uploads","key": "'+pdf_doc_name+'" }'
                os.system("aws lambda invoke --function-name LambdaOpenSearchIngestion --cli-binary-format raw-in-base64-out --payload '"+request_+"' response.json")
        st.success('you can start searching on your PDF')
