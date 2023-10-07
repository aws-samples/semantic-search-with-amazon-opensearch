## Code organization

### main.py
Lambda handler that processes the incoming request and calls the LLM chain to generate a reply. 

### chain.py
The LLM chain code that calls the LLM with the input from the user.

## Packaging the Lambda functions

Clone the repository
```bash
git clone https://github.com/aws-samples/semantic-search-with-amazon-opensearch.git
```

Move to the package directory
```bash
cd generative-ai/Module_1_Chat_With_PDF
```

Install the dependencies; this creates a Conda env named `conversational-search-with-opensearch-service` and activates it.
```bash
conda deactivate
conda env create -f environment.yml # only needed once
conda activate conversational-search-with-opensearch-service
```

Bundle the code for Lambda deployment.
```bash
./bundle.sh
```
This will create two lambda .zip packages and webapp .zip package inside generative-ai/Module_1_Chat_With_PDF directory as lambda.zip, lambda_s3.zip and webapp.zip respectively.