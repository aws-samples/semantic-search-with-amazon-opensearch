import boto3

def createLambdaRole(roleName, policies):
    
    iam_ = boto3.client('iam')

    lambda_iam_role = iam_.create_role(
        RoleName=roleName,
        AssumeRolePolicyDocument='{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}',
        Description='LLMApp Lambda Permissions',

    )
    waiter = iam_.get_waiter('role_exists')
    
    waiter.wait(
    RoleName=roleName,
    WaiterConfig={
        'Delay': 2,
        'MaxAttempts': 5
    }
    )
    
    for policy in policies:
        iam_.attach_role_policy(
            RoleName=roleName,
            PolicyArn='arn:aws:iam::aws:policy/'+policy
        )

    lambda_iam_role_arn = lambda_iam_role['Role']['Arn']
    return lambda_iam_role_arn