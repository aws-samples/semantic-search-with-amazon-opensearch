import json
from os import environ

import boto3
from urllib.parse import urlparse

from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Global variables that are reused
sm_runtime_client = boto3.client('sagemaker-runtime')
s3_client = boto3.client('s3')


def get_features(sm_runtime_client, sagemaker_endpoint, payload):
    response = sm_runtime_client.invoke_endpoint(
        EndpointName=sagemaker_endpoint,
        ContentType='text/plain',
        Body=payload)
    response_body = json.loads((response['Body'].read()))
    features = response_body

    return features


def get_neighbors(features, es, k_neighbors=50):
    idx_name = 'nlp_pqa'
    res = es.search(
        request_timeout=30, index=idx_name,
        body={
            'size': k_neighbors,
            'query': {'knn': {'question_vector': {'vector': features, 'k': k_neighbors}}}},
        stored_fields=["question","answer"]
        )
    results = [{'question':res['hits']['hits'][x]['fields']['question'][0],
            'answer':res['hits']['hits'][x]['fields']['answer'][0]} for x in range(k_neighbors)]
    return results


def es_match_query(payload, es, k=50):
    idx_name = 'nlp_pqa'
    search_body = {
        "size": 50,
        "_source": {
            "excludes": ["question_vector"]
        },
        "highlight": {
            "fields": {
                "question": {}
            }
        },
        "query": {
            "match": {
                "question": {
                    "query": payload
                }
            }
        }
    }

    search_response = es.search(request_timeout=30, index=idx_name,
                                body=search_body)['hits']['hits'][:k]
    response = [{'question': x['highlight']['question'], 'answer': x['_source']['answer']} for x in search_response]
    return response



def lambda_handler(event, context):

    # elasticsearch variables
    service = 'es'
    region = environ['AWS_REGION']
    elasticsearch_endpoint = environ['ES_ENDPOINT']

    session = boto3.session.Session()
    credentials = session.get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        service,
        session_token=credentials.token
        )

    es = Elasticsearch(
        hosts=[{'host': elasticsearch_endpoint, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    # sagemaker variables
    sagemaker_endpoint = environ['SM_ENDPOINT']

    api_payload = json.loads(event['body'])
    k = 50
    payload = api_payload['searchString']

    if event['path'] == '/postText':
        features = get_features(sm_runtime_client, sagemaker_endpoint, payload)
        similiar_questions = get_neighbors(features, es, k_neighbors=k)
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin":  "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "*"
            },
            "body": json.dumps({
                "semantics": similiar_questions,
            }),
        }
    else:
        search = es_match_query(payload, es, k)

        for i in range(len(search)):
            search[i]['question'][0] = search[i]['question'][0].replace("<em>",'<em style="background-color:#f18973;">')
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin":  "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "*"
            },
            "body": json.dumps(search),
        }
