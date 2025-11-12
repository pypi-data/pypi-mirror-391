# Claws: Crossref Labs AWS Tools
Claws is a Python module that provides a simple and convenient way to interact with AWS services, such as S3 and CloudWatch. It utilizes the boto3 library and aiohttp for asynchronous operations, making it ideal for applications that require high-performance and efficient resource utilization.

![license](https://img.shields.io/gitlab/license/crossref/labs/claws) ![activity](https://img.shields.io/gitlab/last-commit/crossref/labs/claws)

![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white) ![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

This is a prototype Crossref Labs system. It is not guaranteed to be stable and the metadata schema and behaviour may be subject to change at any time.

## Features
* S3 client and resource management with automatic deferred initialization
* Presigned URL generation for S3 objects
* Asynchronous downloading of multiple S3 objects
* Retrieval of S3 objects as strings
* Custom exception handling for S3 object retrieval errors
* Easy integration with monitoring and instrumentation tools
* Streaming upload to S3 to handle large JSON files

## Requirements
* Python 3.6 or higher
* boto3
* aiohttp
* smart-open

## Installation

To install the Claws module, simply use the following pip command:

    pip install claws

## Usage
Here is a basic example of how to use the Claws module to interact with AWS S3:

    from claws.aws_utils import AWSConnector


    # Initialize the AWSConnector with a specific S3 bucket
    connector = AWSConnector(bucket="my-bucket", unsigned=False)
    
    # Download an S3 object as a string
    result = connector.s3_obj_to_str(bucket="my-bucket", s3_path="path/to/object.txt")
    
    # Download multiple S3 objects asynchronously in parallel
    s3_objects = ["path/to/object1.txt", "path/to/object2.txt", "path/to/object3.txt"]
    results = connector.get_multiple_s3_objs(bucket="my-bucket", s3_objs=s3_objects)
    
    for result in results:
        print(result)

## Contributing
Contributions to the Claws module are welcome. Please feel free to submit pull requests or report issues on the GitHub repository.

## License
Claws is released under the [MIT License](https://opensource.org/licenses/MIT).

# Credits
* [.gitignore](https://github.com/github/gitignore) from Github.
* [AWS Lambda Powertools](https://awslabs.github.io/aws-lambda-powertools-python/2.10.0/) by Amazon.

&copy; Crossref 2023