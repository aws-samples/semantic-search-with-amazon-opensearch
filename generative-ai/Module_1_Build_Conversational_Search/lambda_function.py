import boto3
lambda_ = boto3.client('lambda')

def createLambdaFunction(encoders, roleARN, env_variables):
    
    iam_ = boto3.client('iam')
    waiter = iam_.get_waiter('role_exists')
    
    waiter.wait(
    RoleName=roleARN.split("/")[1],
    WaiterConfig={
        'Delay': 2,
        'MaxAttempts': 5
    }
    )
    
    for encoder in encoders:
        response = lambda_.create_function(
        FunctionName=encoder,
        Runtime='python3.9',
        Role=roleARN,
        Handler='main_'+encoder+'.handler',
        Code={

            'S3Bucket': 'ws-assets-prod-iad-r-pdx-f3b3f9f1a7d6a3d0',
            'S3Key': '2108cfcf-6cd6-4613-83c0-db4e55998757/'+encoder+'.zip',

        },
        Timeout=900,
        MemorySize=512,
        Environment={
            'Variables': env_variables
        }
        )
        print("\n"+encoder +" Lambda Function created, ARN: "+response['FunctionArn'])
        