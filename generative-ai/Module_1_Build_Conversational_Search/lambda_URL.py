import boto3
lambda_ = boto3.client('lambda')

def createLambdaURL(function_name, account_id):
    response_ = lambda_.add_permission(
    FunctionName=function_name,
    StatementId=function_name+'_permissions',
    Action="lambda:InvokeFunctionUrl",
    Principal=account_id,
    FunctionUrlAuthType='AWS_IAM'
 )

    response = lambda_.create_function_url_config(
    FunctionName=function_name,
    AuthType='AWS_IAM',
    Cors={
        'AllowCredentials': True,

        'AllowMethods':["*"],
        'AllowOrigins': ["*"]

    },
    InvokeMode='RESPONSE_STREAM'
 )

    query_invoke_URL = response['FunctionUrl']
    return query_invoke_URL