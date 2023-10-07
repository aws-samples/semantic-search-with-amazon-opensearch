from typing import Tuple
from uuid import uuid4
from langchain.docstore.document import Document
from langchain import ConversationChain,PromptTemplate, LLMChain
from langchain.memory import ConversationBufferMemory, DynamoDBChatMessageHistory,ConversationBufferWindowMemory
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import OpenSearchVectorSearch
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import messages_to_dict
import config   
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import requests
from typing import Dict
from langchain import PromptTemplate, SagemakerEndpoint
import json
import time
import logging
from typing import List
from langchain.embeddings import SagemakerEndpointEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
import os
# from langchain.tools import  Tool, tool

EMBEDDING_ENDPOINT = os.environ['EMBEDDING_ENDPOINT_NAME'] 
DOMAIN_ADMIN_UNAME = os.environ['OPENSEARCH_USERNAME']
DOMAIN_ADMIN_PW = os.environ['OPENSEARCH_PASSWORD']
DOMAIN_ENDPOINT = os.environ['OPENSEARCH_DOMAIN_ENDPOINT']
DOMAIN_INDEX = os.environ['OPENSEARCH_INDEX']

def run(bucket_: str, key_: str) -> Tuple[str, str]:
    
    print('embedding model initialisation')
    
    #Sagemaker embedding model
    class SagemakerEndpointEmbeddingsJumpStart(SagemakerEndpointEmbeddings):
        def embed_documents(
            self, texts: List[str], chunk_size: int = 5
        ) -> List[List[float]]:
            """Compute doc embeddings using a SageMaker Inference Endpoint.

            Args:
                texts: The list of texts to embed.
                chunk_size: The chunk size defines how many input texts will
                    be grouped together as request. If None, will use the
                    chunk size specified by the class.

            Returns:
                List of embeddings, one for each text.
            """
            results = []
            _chunk_size = len(texts) if chunk_size > len(texts) else chunk_size
            st = time.time()
            for i in range(0, len(texts), _chunk_size):
                response = self._embedding_func(texts[i:i + _chunk_size])
                results.extend(response)
            time_taken = time.time() - st
            #logger.info(f"got results for {len(texts)} in {time_taken}s, length of embeddings list is {len(results)}")
            return results
        
    class ContentHandler(EmbeddingsContentHandler):
        content_type = "application/json"
        accepts = "application/json"

        def transform_input(self, prompt: str, model_kwargs={}) -> bytes:

            input_str = json.dumps({"text_inputs": prompt, **model_kwargs})
            return input_str.encode('utf-8') 

        def transform_output(self, output: bytes) -> str:

            response_json = json.loads(output.read().decode("utf-8"))
            embeddings = response_json["embedding"]
            if len(embeddings) == 1:
                return [embeddings[0]]
            return embeddings
        
    embeddings = SagemakerEndpointEmbeddingsJumpStart( 
            endpoint_name=EMBEDDING_ENDPOINT,
            region_name='us-east-1', 
            content_handler=ContentHandler()
        )

    
    import boto3
    import os
    s3 = boto3.client('s3')

    local_path = '/tmp/'


    with open(os.path.join(local_path, key_), 'wb') as file:
        s3.download_file(bucket_, key_, file.name)

    from PyPDF2 import PdfReader
    pdf_reader = PdfReader("/tmp/"+key_)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    

    from langchain.text_splitter import CharacterTextSplitter
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    print(len(chunks))

    
    os_domain_ep = 'https://'+DOMAIN_ENDPOINT

    logger = logging.getLogger()
    docsearch = OpenSearchVectorSearch.from_texts(index_name = DOMAIN_INDEX,
                                                  texts=chunks,
                                       embedding=embeddings,
                                       opensearch_url=os_domain_ep,
                                       http_auth=(DOMAIN_ADMIN_UNAME, DOMAIN_ADMIN_PW)   )
    
    print("docs inserted into opensearch")

    
    response = "docs inserted into opensearch" 
    
    print(response)
    return response

