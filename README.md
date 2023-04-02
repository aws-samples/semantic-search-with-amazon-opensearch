## Improve search relevance with machine learning in Amazon OpenSearch Service

This repository guides users through creating a semantic search using Amazon SageMaker and Amazon OpenSearch services


## How does it work?

This code repository is for [Semantic Search Workshop](https://catalog.workshops.aws/semantic-search/en-US). For more information about semantic search, please refer the workshop content.

![diagram](./semantic_search_fullstack.jpg)

### CloudFormation Deployment

1. The workshop can only be deployed in us-east-1 region
2. Use the Cloudformation template `cfn/semantic-search.yaml` to create CF stack
3. Cloudformation stack name must be `semantic-search` as we use this stack name in our lab
4. You can click the following link to deploy CloudFormation Stack
  
|   Region  |   Launch Template |
|  ---------------------------   |   -----------------------  |
|  **US East (N. Virginia)**     | [![Deploy to AWS](deploy-to-aws.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/quickcreate?templateUrl=https://ee-assets-prod-us-east-1.s3.amazonaws.com/modules/1e02deca779a4be58b9d50513a464cdc/v1/semanticsearch/semantic-search-v2.yaml&stackName=semantic-search) |


### Lab Instruction
There are 6 modues in this workshop:
* **Module 1 - Search basics**: You will learn fundamentals of text search and semantic search. This section also introduces differences between a best matching algorithm, popularly known as BM25 similarity and semantic similarity.

* **Module 2 -Text search**: You will learn text search with Amazon OpenSearch Service. In information retrieval this type of searching is traditionally called 'Keyword' search.

* **Module 3 - Semantic search**: You will learn semantic search with Amazon OpenSearch Service and Amazon SageMaker. You will use a machine learning technique called Bidirectional Encoder Representations from transformers, popularly known as BERT. BERT uses a pre-trained natural language processing (NLP) model that represents text in the form numbers or in other words, vectors. You will learn to use vectors with kNN feature in Amazon OpenSearch Service.

* **Module 4 - Fullstack semantic search**: You will bring together all the concepts learnt earlier with an user interface that shows the advantages of using semantic search with text search. You will be using Amazon OpenSearch Service, Amazon SageMaker, AWS Lambda, Amazon API Gateway and Amazon S3 for this purpose.

* **Module 5 - Fine tuning semantic search**: Large language models like BERT show better results when they are trained in-domain, which means fine tuning the general model to fit ones particular business requirements in the domain of its application. You will learn how to fine tune the model for semantic search with the chosen data set.

* **Mudule 6 - Neural Search**: Implement semantic search with [OpenSearch Neural Search Plugin](https://opensearch.org/docs/latest/search-plugins/neural-search/).


Please refer [Semantic Search Workshop](https://catalog.workshops.aws/semantic-search/en-US) for lab instruction.


## License

This library is licensed under the MIT-0 License. See the LICENSE file.

