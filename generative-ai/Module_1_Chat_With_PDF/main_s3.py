import json
import os
from typing import Dict
import requests
import chain_s3
import config
import json
import urllib.parse
import boto3

def handler(event, context): 
    
    # body = json.loads(event["body"])
    
    # validate_response = validate_inputs(body)
    # if validate_response:
    #     return validate_response

    bucket = event['bucket']#event['Records'][0]['s3']['bucket']['name']
    key = event['key']#urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    

    # bucket = 'lambda-artifact-opensearch'
    # key = 'sample.pdf'

    print(bucket)
    print(key)
    
    response = chain_s3.run(
       
        bucket_ = bucket, 
        key_=key
    )

    print(response)
    

