import asyncio
import base64
from functools import wraps
from typing import Callable

from aiohttp import client
from yarl import URL

import json
import logging
from smart_open import open


def deferred_init(func) -> Callable:
    """
    A decorator to indicate that a property should trigger deferred init.
    :param func: the function to wrap.
    :return: a Callable
    """

    @wraps(func)
    def _decorator(self, *args, **kwargs):
        if not self._done_init:
            self._deferred_init()

        return func(self, *args, **kwargs)

    return _decorator


class AWSConnector:
    """
    A class to connect to AWS.
    """

    def _deferred_init(self) -> None:
        """
        This is a deferred init function that will be called when the first
        property is accessed. We defer the init because boto3 has slow startup
        times and this accelerates the test suite.
        :return: None
        """
        import boto3
        from botocore import UNSIGNED
        from botocore.config import Config

        self.config = Config(
            signature_version=UNSIGNED,
            region_name=self._region_name,
        )

        self.signed_config = Config(region_name=self._region_name)
        self._session = boto3.Session(
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
            aws_session_token=self._aws_session_token,
        )

        self._s3_client = (
            self._session.client(
                "s3",
                config=(self.config if self._unsigned else self.signed_config),
            )
            if not self._endpoint_url
            else boto3.client(
                "s3",
                endpoint_url=self._endpoint_url,
                config=(self.config if self._unsigned else self.signed_config),
            )
        )

        self._cloudwatch_client = (
            self._session.client(
                "cloudwatch",
                config=self.signed_config,
            )
            if not self._endpoint_url
            else boto3.client(
                "cloudwatch",
                endpoint_url=self._endpoint_url,
                config=self.signed_config,
            )
        )

        self._log_client = (
            self._session.client(
                "logs",
                config=self.signed_config,
            )
            if not self._endpoint_url
            else boto3.client(
                "logs",
                endpoint_url=self._endpoint_url,
                config=self.signed_config,
            )
        )

        self._resource = (
            self._session.resource(
                "s3",
                config=(self.config if self._unsigned else self.signed_config),
            )
            if not self._endpoint_url
            else self._session.resource(
                "s3",
                endpoint_url=self._endpoint_url,
                config=(self.config if self._unsigned else self.signed_config),
            )
        )

        if self._bucket_name != "":
            self._bucket = self._resource.Bucket(
                self._bucket_name,
            )

        self._secret_manager_client = self._session.client(
            service_name="secretsmanager",
            config=(self.config if self._unsigned else self.signed_config),
        )

        self._done_init = True

    def __init__(
        self,
        endpoint_url: str = None,
        bucket: str = "",
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_session_token=None,
        unsigned: bool = True,
        region_name: str = "us-east-1",
    ):
        self._done_init = False
        self._endpoint_url = endpoint_url
        self.config = None
        self._s3_client = None
        self._cloudwatch_client = None
        self._log_client = None
        self._session = None
        self._resource = None
        self._bucket = None
        self._bucket_name = bucket
        self._instrumentation = None
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._aws_session_token = aws_session_token
        self._unsigned = unsigned
        self._secret_manager_client = None
        self._region_name = region_name

    @property
    @deferred_init
    def secret_manager_client(self):
        """
        Get the secret manager client
        :return: secret manager client
        """
        return self._secret_manager_client

    @secret_manager_client.setter
    @deferred_init
    def secret_manager_client(self, value):
        """
        Set the secret manager client
        :param value: the secret manager client
        :return: None
        """
        self._secret_manager_client = value

    @property
    def instrumentation(self):
        """
        Return the instrumentation/logging class
        :return: an Instrumentation class
        """
        return self._instrumentation

    @instrumentation.setter
    def instrumentation(self, value):
        """
        Set the instrumentation/logging class
        :param value: an Instrumentation class
        :return: None
        """
        self._instrumentation = value

    @property
    @deferred_init
    def s3_client(self):
        """
        Get the s3 client
        :return: S3 client
        """
        return self._s3_client

    @s3_client.setter
    @deferred_init
    def s3_client(self, value):
        """
        Set the s3 client
        :param value: the s3 client
        :return: None
        """
        self._s3_client = value

    @property
    @deferred_init
    def log_client(self):
        """
        Get the log client
        :return: log client
        """
        return self._log_client

    @log_client.setter
    @deferred_init
    def log_client(self, value):
        """
        Set the log client
        :param value: the log client
        :return: None
        """
        self._log_client = value

    @property
    @deferred_init
    def cloudwatch_client(self):
        """
        Get the CloudWatch client
        :return: the CloudWatch client
        """
        return self._cloudwatch_client

    @cloudwatch_client.setter
    @deferred_init
    def cloudwatch_client(self, value):
        """
        Set the CloudWatch client
        :param value: the CloudWatch client
        :return: None
        """
        self._cloudwatch_client = value

    @property
    @deferred_init
    def s3_resource(self):
        """
        Get the s3 resource
        :return: the s3 resource object
        """
        return self._resource

    @s3_resource.setter
    @deferred_init
    def s3_resource(self, value):
        """
        Set the s3 resource
        :param value: the s3 resource object
        :return: None
        """
        self._resource = value

    @property
    @deferred_init
    def s3_session(self):
        """
        Get the s3 session
        :return: the s3 session object
        """
        return self._session

    @s3_session.setter
    @deferred_init
    def s3_session(self, value):
        """
        Set the s3 session
        :param value: the s3 session object
        :return: None
        """
        self._session = value

    @property
    @deferred_init
    def bucket(self):
        """
        Get the s3 bucket
        :return: the s3 bucket object
        """

        return self._bucket

    async def download_s3_obj(
        self,
        bucket: str,
        key: str,
        aiohttp_session: client.ClientSession,
    ) -> dict:
        """
        Download the s3 object asynchronously
        :param bucket: the bucket to get the object from
        :param key: the key to get
        :param aiohttp_session: an aiohttp session to reuse
        :return: a dictionary of the key and the downloaded object
        """
        if self.instrumentation:
            self.instrumentation.logger.info(f"Async getting s3 object: {key}")

        request_url = self.s3_client.generate_presigned_url(
            "get_object", {"Bucket": bucket, "Key": key}
        )

        async with aiohttp_session.get(
            URL(request_url, encoded=True)
        ) as response:
            result = await response.read()

            result = result.decode("utf-8")

            if not result.startswith("{") and not result.startswith("["):
                if self.instrumentation:
                    self.instrumentation.logger.info(
                        f"JSON response from s3 for {key} "
                        "does not start with [ or {. "
                        "Returning blank."
                    )

                # if we hit here, it's an "annotation not found" error
                result = "{}"

            return {key: result}

    async def _get_tasks(
        self, bucket: str, s3_objs: list
    ) -> tuple[list, client.ClientSession]:
        """
        Get the tasks for the async download
        :param bucket: the bucket to get the objects from
        :param s3_objs: the list of s3 objects to get
        :return: a set of tasks and the aiohttp session
        """
        session = client.ClientSession()

        return [
            self.download_s3_obj(
                bucket=bucket,
                key=f,
                aiohttp_session=session,
            )
            for f in s3_objs
        ], session

    @staticmethod
    def get_or_create_eventloop():
        try:
            return asyncio.get_event_loop()
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return asyncio.get_event_loop()

    def get_multiple_s3_objs(self, bucket, s3_objs):
        """
        Get multiple s3 objects in parallel
        :param bucket: the bucket to get the objects from
        :param s3_objs: the list of s3 objects to get
        :return: a tuple of the results
        """
        loop = self.get_or_create_eventloop()

        try:
            tasks, session = loop.run_until_complete(
                self._get_tasks(bucket=bucket, s3_objs=s3_objs)
            )

            tasks = loop.run_until_complete(asyncio.gather(*tasks))
            loop.run_until_complete(session.close())
        except Exception as e:
            if self.instrumentation:
                self.instrumentation.logger.info("Error with async s3 get")
                self.instrumentation.logger.info(e)
            raise e

        return tasks

    def s3_obj_to_str(
        self,
        bucket: str,
        s3_path: str,
        raise_on_fail=False,
    ) -> str:
        """
        Get the s3 object as a string
        :param bucket: the bucket to get the object from
        :param s3_path: the path to the object
        :param raise_on_fail: whether to raise an exception if the object is
        not found
        :return: a string result
        """
        if self.instrumentation:
            self.instrumentation.logger.info(f"Getting s3 object: {s3_path}")

        try:
            return (
                self.s3_client.get_object(
                    Bucket=bucket,
                    Key=s3_path,
                )["Body"]
                .read()
                .decode("utf-8")
            )
        except Exception as e:
            if self.instrumentation:
                self.instrumentation.logger.info(
                    f"Error getting s3 object: {s3_path} {e}"
                )
            if raise_on_fail:
                raise S3ObjException(e) from e
            else:
                return "{}"

    @staticmethod
    def s3_to_json_key(key) -> str:
        """
        Get a json key from the s3 key
        :param key: the key
        :return: a string
        """
        return key.split("/")[-1].split(".")[0]

    def push_json_to_s3(
        self,
        json_obj,
        bucket,
        path,
        verbose=False,
    ) -> None:
        """
        Writes the JSON data to S3
        :param bucket: the name of the bucket
        :param path: the path of the object to store
        :param json_obj: the JSON to write
        :param verbose: whether to print status messages
        :return:
        """

        if verbose:
            logging.info(f"Writing JSON to S3 bucket {bucket} at path {path}")

        url = f"s3://{bucket}/{path}"
        with open(
            url,
            "w",
            transport_params={"client": self.s3_client},
        ) as output:
            json.dump(json_obj, output, indent=4)
            output.flush()

    def get_secret(self, secret_name):
        """
        return AWS secrets in usable form
        """

        get_secret_value_response = self.secret_manager_client.get_secret_value(
            SecretId=secret_name
        )
        if "SecretString" in get_secret_value_response:
            return get_secret_value_response["SecretString"]
        else:
            return base64.b64decode(get_secret_value_response["SecretBinary"])

    def list_prefix(self, prefix, file_extension=None):
        """
        Returns files in a prefix
        :param prefix: the prefix to list
        :param file_extension: the file extension to filter by
        :return:
        """
        if file_extension:
            return {
                obj.key.split("/")[-1]
                for obj in self.bucket.objects.filter(Prefix=prefix)
                if obj.key.endswith(file_extension)
            }
        else:
            return {
                obj.key.split("/")[-1]
                for obj in self.bucket.objects.filter(Prefix=prefix)
            }

    def delete_under_prefix(self, prefix) -> list[str]:
        """
        Deletes all files under a prefix
        :param prefix: the prefix to delete
        :return:
        """
        deleted = []

        for obj in self.bucket.objects.filter(Prefix=prefix):
            if self.instrumentation:
                self.instrumentation.logger.info(
                    f"Deleting s3 object: {obj.key}"
                )
            deleted.append(obj.key)
            obj.delete()

        return deleted


class S3ObjException(Exception):
    """
    Exception for S3 object errors
    """

    pass
