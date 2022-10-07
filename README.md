## Improve search relevance with machine learning in Amazon OpenSearch Service

This repository guides users through creating a semantic search using Amazon SageMaker and Amazon Elasticsearch service


## How does it work?

we have used pre-trained BERT model from sentence-transformers to generate fixed 768 length sentence embedding on Amazon Product Question and Answer(https://registry.opendata.aws/amazon-pqa/). Then those feature vectors is imported in Amazon ES KNN Index as a reference.

When we present a new query text/sentence, it's computing the related embedding from Amazon SageMaker hosted BERT model and query Amazon ES KNN index to find similar text/sentence and corresponds to the actual product image which is stored in Amazon S3

![diagram](./semantic_search_ranking.png)

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
