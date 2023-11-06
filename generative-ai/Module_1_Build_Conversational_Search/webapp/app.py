import streamlit as st
import uuid
import os
import boto3
import requests
import api
from boto3 import Session
import botocore.session
import json
import random
import string
#from langchain.callbacks.base import BaseCallbackHandler


USER_ICON = "/home/ec2-user/images/user.png"
AI_ICON = "/home/ec2-user/images/opensearch-twitter-card.png"
REGENERATE_ICON = "/home/ec2-user/images/regenerate.png"
s3_bucket_ = "pdf-repo-uploads"
            #"pdf-repo-uploads"

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

if "input_text" not in st.session_state:
    st.session_state.input_text=""

if "input_searchType" not in st.session_state:
    st.session_state.input_searchType = "Conversational Search (RAG)"

# if "input_temperature" not in st.session_state:
#     st.session_state.input_temperature = "0.001"

# if "input_topK" not in st.session_state:
#     st.session_state.input_topK = 200

# if "input_topP" not in st.session_state:
#     st.session_state.input_topP = 0.95

# if "input_maxTokens" not in st.session_state:
#     st.session_state.input_maxTokens = 1024


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
    st.session_state.input_text=""
    # st.session_state.input_searchType="Conversational Search (RAG)"
    # st.session_state.input_temperature = "0.001"
    # st.session_state.input_topK = 200
    # st.session_state.input_topP = 0.95
    # st.session_state.input_maxTokens = 1024

st.markdown('---')

def handle_input():
    inputs = {}
    for key in st.session_state:
        if key.startswith('input_'):
            inputs[key.removeprefix('input_')] = st.session_state[key]
    st.session_state.inputs_ = inputs
    
    #st.write(inputs) 
    question_with_id = {
        'question': inputs["text"],
        'id': len(st.session_state.questions)
    }
    st.session_state.questions.append(question_with_id)
    st.session_state.answers.append({
        'answer': api.call(json.dumps(inputs), st.session_state['session_id']),
        'search_type':inputs['searchType'],
        'id': len(st.session_state.questions)
    })
    st.session_state.input_text=""
    #st.session_state.input_searchType=st.session_state.input_searchType


    
search_type = st.selectbox('Select the Search type',
    ('Conversational Search (RAG)',
    'OpenSearch vector search', 
    'LLM Text Generation'
    ),
   
    key = 'input_searchType',
    help = "Select the type of retriever\n1. Conversational Search (Recommended) - This will include both the OpenSearch and LLM in the retrieval pipeline \n (note: This will put opensearch response as context to LLM to answer) \n2. OpenSearch vector search - This will put only OpenSearch's vector search in the pipeline, \n(Warning: this will lead to unformatted results )\n3. LLM Text Generation - This will include only LLM in the pipeline, \n(Warning: This will give hallucinated and out of context answers)"
    )

col1, col2, col3, col4 = st.columns(4)
    
with col1:
    st.text_input('Temperature', value = "0.001", placeholder='LLM Temperature', key = 'input_temperature',help = "Set the temperature of the Large Language model. \n Note: 1. Set this to values lower to 1 in the order of 0.001, 0.0001, such low values reduces hallucination and creativity in the LLM response; 2. This applies only when LLM is a part of the retriever pipeline")
with col2:
    st.number_input('Top K', value = 200, placeholder='Top K', key = 'input_topK', step = 50, help = "This limits the LLM's predictions to the top k most probable tokens at each step of generation, this applies only when LLM is a prt of the retriever pipeline")
with col3:
    st.number_input('Top P', value = 0.95, placeholder='Top P', key = 'input_topP', step = 0.05, help = "This sets a threshold probability and selects the top tokens whose cumulative probability exceeds the threshold while the tokens are generated by the LLM")
with col4:
    st.number_input('Max Output Tokens', value = 500, placeholder='Max Output Tokens', key = 'input_maxTokens', step = 100, help = "This decides the total number of tokens generated as the final response. Note: Values greater than 1000 takes longer response time")

st.markdown('---')


def write_user_message(md):
    col1, col2 = st.columns([0.60,12])
    
    with col1:
        st.image(USER_ICON, use_column_width='always')
    with col2:
        #st.warning(md['question'])

        st.markdown("<div style='padding:3px 7px 3px 7px;borderWidth: 0px;background:#fffee0;borderColor: red;borderStyle: solid;width: fit-content;height: fit-content;border-radius: 10px;'>"+md['question']+"</div>", unsafe_allow_html = True)
       
def render_answer(answer,search_type,index):
    col1, col2, col3, col4 = st.columns([2,20,6,1])
    with col1:
        st.image(AI_ICON, use_column_width='always')
    with col2:
        # chat_box=st.empty() 
        # self.text+=token+"/" 
        # self.container.markdown(self.text) 
        #st.markdown(answer,unsafe_allow_html = True)
        st.markdown("<div style='padding:3px 7px 3px 7px;borderWidth: 0px;background:#D4F1F4;borderColor: red;borderStyle: solid;width: fit-content;height: fit-content;border-radius: 10px;'><b>"+answer+"</b></div>", unsafe_allow_html = True)
       
    with col3:
        if(search_type== 'Conversational Search (RAG)'):
            st.markdown("<p style='padding:0px 5px 0px 5px;borderWidth: 0px;background:#D4F1F4;borderColor: red;borderStyle: solid;width: fit-content;height: fit-content;border-radius: 5px;'><b>RAG</b></p>", unsafe_allow_html = True, help = "Retriever type of the response")
        if(search_type== 'OpenSearch vector search'):
            st.markdown("<p style='padding:0px 5px 0px 5px;borderWidth: 0px;background:#D4F1F4;borderColor: red;borderStyle: solid;width: fit-content;height: fit-content;border-radius: 5px;'><b>OpenSearch</b></p>", unsafe_allow_html = True, help = "Retriever type of the response")
        if(search_type== 'LLM Text Generation'):
            st.markdown("<p style='padding:0px 5px 0px 5px;borderWidth: 0px;background:#D4F1F4;borderColor: red;borderStyle: solid;width: fit-content;height: fit-content;border-radius: 5px;'><b>LLM</b></p>", unsafe_allow_html = True, help = "Retriever type of the response")
        
        print("------------------------")
        print(type(st.session_state))
        print("------------------------")
        print(st.session_state)
        print("------------------------")
        
    with col4:
        if(index == len(st.session_state.questions)):

            rdn_key = ''.join([random.choice(string.ascii_letters)
                              for _ in range(10)])
            currentValue = st.session_state.input_searchType+st.session_state.input_temperature+str(st.session_state.input_topK)+str(st.session_state.input_topP)+str(st.session_state.input_maxTokens)
            oldValue = st.session_state.inputs_["searchType"]+st.session_state.inputs_["temperature"]+str(st.session_state.inputs_["topK"])+str(st.session_state.inputs_["topP"])+str(st.session_state.inputs_["maxTokens"])

            def on_button_click():
                if(currentValue!=oldValue):
                    st.session_state.input_text = st.session_state.questions[-1]["question"]
                    st.session_state.answers.pop()
                    st.session_state.questions.pop()
                    
                    handle_input()
                    with placeholder.container():
                        render_all()

            if("currentValue"  in st.session_state):
                del st.session_state["currentValue"]

            try:
                del regenerate
            except:
                pass  

            print("------------------------")
            print(st.session_state)

            placeholder__ = st.empty()
            
            placeholder__.button("🔄",key=rdn_key,on_click=on_button_click, help = "This will regenerate the last response with new settings that you entered, Note: This applies to only the last response and to see difference in responses, you should change any of the settings above")#,type="primary",use_container_width=True)
     
#Each answer will have context of the question asked in order to associate the provided feedback with the respective question
def write_chat_message(md, q,index):
    if('body' in md['answer']):
        res = json.loads(md['answer']['body'])
    else:
        res = md['answer']
    st.session_state['session_id'] = res['session_id']
    chat = st.container()
    with chat:
        render_answer(res["response"],md['search_type'],index)
    
def render_all():  
    index = 0
    for (q, a) in zip(st.session_state.questions, st.session_state.answers):
        index = index +1
        print("answers----")
        print(a)
        write_user_message(q)
        write_chat_message(a, q,index)

placeholder = st.empty()
with placeholder.container():
  render_all()

st.markdown("")
col_1, col_2, col_3 = st.columns([6,50,5])
with col_1:
    st.markdown("<p style='padding:0px 0px 0px 0px; color:#FF9900;font-size:120%'><b>Ask:</b></p>",unsafe_allow_html=True, help = 'Enter the questions and click on "GO"')
    
with col_2:
    #st.markdown("")
    input = st.text_input( "Ask here",label_visibility = "collapsed",key="input_text")
with col_3:
    #hidden = st.button("RUN",disabled=True,key = "hidden")
    play = st.button("GO",on_click=handle_input,key = "play")
with st.sidebar:
    st.subheader("Sample PDF(s)")
    # Initialize boto3 to use the S3 client.
    s3_client = boto3.resource('s3')
    bucket=s3_client.Bucket(s3_bucket_)

    objects = bucket.objects.filter(Prefix="sample_pdfs/")
    urls = []

    client = boto3.client('s3')

    for obj in objects:
        if obj.key.endswith('.pdf'): 

            # Generate the S3 presigned URL
            s3_presigned_url = client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': s3_bucket_,
                    'Key': obj.key
                },
                ExpiresIn=3600
            )

            # Print the created S3 presigned URL
            print(s3_presigned_url)
            urls.append(s3_presigned_url)
            #st.write("["+obj.key.split('/')[1]+"]("+s3_presigned_url+")")
            st.link_button(obj.key.split('/')[1], s3_presigned_url)
    
    st.subheader("Your documents")
    pdf_docs = st.file_uploader(
        "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
    if st.button("Process"):
        with st.spinner("Processing"):
            for pdf_doc in pdf_docs:
                print(type(pdf_doc))
                pdf_doc_name = (pdf_doc.name).replace(" ","_")
                print("aws s3 cp pdfs"+pdf_doc_name+" s3://"+s3_bucket_)
                with open(os.path.join("/home/ec2-user/pdfs",pdf_doc_name),"wb") as f: 
                    f.write(pdf_doc.getbuffer())  
                    os.system("aws s3 cp /home/ec2-user/pdfs/"+pdf_doc_name+" s3://"+s3_bucket_)
                request_ = '{ "bucket": "'+s3_bucket_+'","key": "'+pdf_doc_name+'" }'
                os.system("aws lambda invoke --function-name documentEncoder --cli-binary-format raw-in-base64-out --payload '"+request_+"' response.json")
                print('lambda done')
        st.success('you can start searching on your PDF')
