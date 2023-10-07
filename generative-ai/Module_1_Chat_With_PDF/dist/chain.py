from typing import Tuple
from uuid import uuid4
from langchain.docstore.document import Document
import os


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
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.chains.question_answering import load_qa_chain
from typing import Any, Dict, Iterable, List, Optional, Tuple, Callable
import json
# from langchain.tools import  Tool, tool

EMBEDDING_ENDPOINT = os.environ['EMBEDDING_ENDPOINT_NAME'] 
LLM_ENDPOINT = os.environ['TEXT2TEXT_ENDPOINT_NAME'] 
DOMAIN_ADMIN_UNAME = os.environ['OPENSEARCH_USERNAME']
DOMAIN_ADMIN_PW = os.environ['OPENSEARCH_PASSWORD']
DOMAIN_ENDPOINT = os.environ['OPENSEARCH_DOMAIN_ENDPOINT']
DOMAIN_INDEX = os.environ['OPENSEARCH_INDEX']
DYNAMO_DB_TABLE = os.environ['DYNAMODB_TABLE']

def run(api_key: str, session_id: str, prompt: str) -> Tuple[str, str]:
    """This is the main function that executes the prediction chain.
    Updating this code will change the predictions of the service.
    Current implementation creates a new session id for each run, client
    should pass the returned session id in the next execution run, so the
    conversation chain can load message context from previous execution.

    Args:
        api_key: api key for the LLM service, OpenAI used here
        session_id: session id from the previous execution run, pass blank for first execution
        prompt: prompt question entered by the user

    Returns:
        The prediction from LLM
    """
    
    if not session_id.strip():
        print('no session id')
        session_id = str(uuid4())
    
    chat_memory = DynamoDBChatMessageHistory(
        table_name=DYNAMO_DB_TABLE,
        session_id=session_id
    )
    messages = chat_memory.messages

    # Maintains immutable sessions
    # If previous session was present, create
    # a new session and copy messages, and 
    # generate a new session_id 

    if messages:
        session_id = str(uuid4())
        chat_memory = DynamoDBChatMessageHistory(
            table_name=DYNAMO_DB_TABLE,
            session_id=session_id
        )

        # This is a workaround at the moment. Ideally, this should
        # be added to the DynamoDBChatMessageHistory class
        
        try:
            messages = messages_to_dict(messages)
            chat_memory.table.put_item(
                Item={"SessionId": session_id, "History": messages}
            )
        except Exception as e:
            print(e)
    
    memory = ConversationBufferMemory(chat_memory=chat_memory, return_messages=True)

    # session memory WO DynamoDB
    # memory_ = ConversationBufferWindowMemory(
    # memory_key='chat_history',
    # k=5,
    # return_messages=True
    # )

    #Using prompt template instead of STUFF and conversational chain
    
    # prompt_template = ChatPromptTemplate.from_messages([
    #     SystemMessagePromptTemplate.from_template("The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know."),
    #     MessagesPlaceholder(variable_name="history"),
    #     HumanMessagePromptTemplate.from_template("{input}")
    # ])
    # conversation = ConversationChain(
    #     llm=llm, 
    #     prompt=prompt_template,
    #     verbose=True, 
    #     memory=memory
    # )

   
    #Sagemaker embedding model
    import time
    import json
    import logging
    from typing import List
    from langchain.embeddings import SagemakerEndpointEmbeddings
    from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
    from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler

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

    class SimiliarOpenSearchVectorSearch(OpenSearchVectorSearch):
        def relevance_score(self, distance: float) -> float:
            return distance
        def _select_relevance_score_fn(self) -> Callable[[float], float]:
            return self.relevance_score
   
    os_domain_ep = 'https://'+DOMAIN_ENDPOINT

    openSearch_ = SimiliarOpenSearchVectorSearch(index_name=DOMAIN_INDEX,
                                       embedding_function=embeddings,
                                       opensearch_url=os_domain_ep,
                                       http_auth=(DOMAIN_ADMIN_UNAME, DOMAIN_ADMIN_PW)   ) 
    
    openSearch_retriever = openSearch_.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        'k': 2,
        'score_threshold': 0.7
    }
)

    #Only using OpenSearch 
    docs_ = openSearch_.similarity_search(prompt)
    print("opensearch results:"+docs_[0].page_content)

    #openAI LLM
    #llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

    prompt_template = """Use the following pieces of context to answer the question at the end.

    {context}

    Question: {question}
    Answer:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    #Sagemaker Falcon XL LLM
    class ContentHandler(LLMContentHandler):
        content_type = "application/json"
        accepts = "application/json"

        def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
            input_str = json.dumps({"inputs": prompt, "parameters":model_kwargs})
            return input_str.encode("utf-8")

        def transform_output(self, output: bytes) -> str:
            #response_json = json.loads(output.read().decode("utf-8"))
            decode_str_output = output.read().decode("utf-8")
            print(type(decode_str_output))
            print(len(decode_str_output))
            print(decode_str_output)
            #return output.read().decode("utf-8")
            response_json = json.loads(decode_str_output)
            print("LLM generated text:\n" + response_json[0]["generated_text"])
            return response_json[0]["generated_text"]


    content_handler = ContentHandler()

    params = {
        "max_new_tokens": 128,
        "num_return_sequences": 1,
        "top_k": 200,
        "top_p": 0.9,
        "do_sample": False,
        "return_full_text": False,
        "temperature": 0.0001
        }
    
    llm=SagemakerEndpoint(
        endpoint_name=LLM_ENDPOINT,
        #credentials_profile_name="credentials-profile-name",
        region_name="us-east-1",
        model_kwargs=params,
        content_handler=content_handler,
    )

    # using STUFF instead of prompt templates

    qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=openSearch_retriever,
    memory = memory
    )

    # using prompt templates instead of STUFF

    # chain = load_qa_chain(
    # llm=llm,
    # prompt=PROMPT,
    # )
    
   
    print("Only OpenSearch as retriever=true")
    response = qa.run( prompt) # docs_[0].page_content # chain({"input_documents": docs_, "question": prompt}, return_only_outputs=True)
    print("response from agent")
    print("response:"+response)
    print("response:"+session_id)
    return response, session_id

