import asyncio
import json
import sys
from unittest.mock import MagicMock, patch, AsyncMock

import aiohttp
import pytest
from aiohttp import client
from moto import mock_s3

sys.path.append("../../")
sys.path.append("../src")
sys.path.append("../src/plugins")

BUCKET = "outputs.research.crossref.org"
SAMPLES_BUCKET = "samples.research.crossref.org"
ANNOTATION_PATH = "annotations"
VALID_ANNOTATIONS = "annotations/valid_annotations"


class TestAWSUtils:
    @pytest.fixture()
    def aiohttp_session(self):
        session = client.ClientSession()
        yield session
        session.close()

    @pytest.mark.asyncio
    async def test_download_s3_obj(self, mocker, aiohttp_session):
        """
        Test that we can successfully download an object from S3
        :param mocker: the mocker to use
        :param aiohttp_session: the pytest fixture to use
        :return: None
        """
        from claws import aws_utils

        aws_connector = aws_utils.AWSConnector(bucket=BUCKET)

        # Set up the S3 bucket and object
        aws_connector.s3_client = MockAsyncS3Client()
        s3_bucket = BUCKET
        s3_key = f"{ANNOTATION_PATH}/member/78/anno1.json"
        s3_content = '{"key1": "value1"}'

        # Call the function to test
        resp = MockResponse(s3_content, 200)

        mocker.patch("aiohttp.ClientSession.get", return_value=resp)

        result = await aws_connector.download_s3_obj(
            s3_bucket, s3_key, aiohttp_session
        )

        # Check if the function returns the correct value
        assert result == {s3_key: s3_content}

    @pytest.mark.asyncio
    async def test_download_s3_obj_starting_with_square_bracket(
        self, mocker, aiohttp_session
    ):
        """
        Test that we can successfully download an object from S3 and that a square bracket is a legitimate starting character (RD-134)
        :param mocker: the mocker to use
        :param aiohttp_session: the pytest fixture to use
        :return: None
        """
        from claws import aws_utils

        aws_connector = aws_utils.AWSConnector(bucket=BUCKET)

        # Set up the S3 bucket and object
        aws_connector.s3_client = MockAsyncS3Client()
        s3_bucket = BUCKET
        s3_key = f"{ANNOTATION_PATH}/member/78/anno1.json"
        s3_content = '[{"key1": "value1"}]'

        # Call the function to test
        resp = MockResponse(s3_content, 200)

        mocker.patch("aiohttp.ClientSession.get", return_value=resp)

        result = await aws_connector.download_s3_obj(
            s3_bucket, s3_key, aiohttp_session
        )

        # Check if the function returns the correct value
        assert result == {s3_key: s3_content}

    @pytest.mark.asyncio
    async def test_download_s3_obj_not_found(self, mocker, aiohttp_session):
        """
        Test that we return a blank entry when the object is not found
        :param mocker: the mocker to use
        :param aiohttp_session: the pytest fixture
        :return: None
        """
        from claws import aws_utils

        aws_connector = aws_utils.AWSConnector(bucket=BUCKET)

        # Set up the S3 bucket and object
        aws_connector.s3_client = MockAsyncS3Client()
        s3_bucket = BUCKET
        s3_key = f"{ANNOTATION_PATH}/member/78/anno1.json"
        s3_content = "<xml NOT FOUND blah>"

        # Call the function to test
        resp = MockResponse(s3_content, 200)

        mocker.patch("aiohttp.ClientSession.get", return_value=resp)

        result = await aws_connector.download_s3_obj(
            s3_bucket, s3_key, aiohttp_session
        )

        # Check if the function returns the correct value: in this case,
        # an empty dict
        assert result == {s3_key: "{}"}

    @mock_s3
    def test_delete_under_prefix(self):
        from claws import aws_utils

        bucket = "mybucket"

        aws_connect = aws_utils.AWSConnector(bucket=bucket, unsigned=False)

        s3_client = aws_connect.s3_client

        aws_connect.s3_resource.create_bucket(Bucket=bucket)

        aws_connect.s3_client.put_bucket_policy(
            Bucket=bucket,
            Policy='{"Version":"2012-10-17", "Statement":[{"Sid":"AddPerm", '
            '"Effect":"Allow", "Principal": "*", "Action":['
            '"s3:GetObject"], "Resource":["arn:aws:s3:::' + bucket + '/*"]}]}',
        )

        s3_client.put_object(Bucket=bucket, Key="myprefix/file", Body="test")
        s3_client.put_object(
            Bucket=bucket, Key="anotherprefix/file", Body="test"
        )

        remaining_files = aws_connect.list_prefix(prefix="myprefix")
        assert len(remaining_files) == 1

        remaining_files = aws_connect.list_prefix(prefix="anotherprefix")
        assert len(remaining_files) == 1

        aws_connect.delete_under_prefix("myprefix")

        remaining_files = aws_connect.list_prefix(prefix="myprefix")

        assert len(remaining_files) == 0

        # check other files are preserved/not deleted
        remaining_files = aws_connect.list_prefix(prefix="anotherprefix")
        assert len(remaining_files) == 1

    @pytest.mark.asyncio
    async def test_get_tasks(
        self,
    ):
        """
        Test that we get the tasks successfully in the event loop
        :return: None
        """
        from claws import aws_utils

        with patch(
            "claws.aws_utils.client.ClientSession"
        ) as mock_client_session_constructor:
            mock_bucket = "test-bucket"
            aws_connector = aws_utils.AWSConnector(bucket=mock_bucket)

            mock_s3_objs = ["file1.txt", "file2.txt", "file3.txt"]
            mock_session = MagicMock(spec=aiohttp.ClientSession)
            mock_client_session_constructor.return_value = mock_session

            tasks, session = await aws_connector._get_tasks(
                mock_bucket, mock_s3_objs
            )

            mock_client_session_constructor.assert_called_once()
            assert len(tasks) == len(mock_s3_objs)
            assert session == mock_session

    @patch("claws.aws_utils.AWSConnector._get_tasks", new_callable=AsyncMock)
    @patch("claws.aws_utils.asyncio.gather", new_callable=AsyncMock)
    @patch("asyncio.get_event_loop")
    def test_get_multiple_s3_objs(
        self, mock_get_tasks, mock_asyncio_gather, mock_get_event_loop
    ):
        """
        Test that we can run an event loop to get multiple s3 objects async
        :param mock_get_tasks: the mocked get_tasks function
        :param mock_asyncio_gather: the mocked asyncio.gather function
        :param mock_get_event_loop: the mocked asyncio.get_event_loop function
        :return: None
        """
        from claws import aws_utils

        mock_bucket = "test-bucket"
        aws_connector = aws_utils.AWSConnector(bucket=mock_bucket)

        mock_s3_objs = ["file1.txt", "file2.txt", "file3.txt"]
        mock_tasks = [MagicMock(), MagicMock(), MagicMock()]

        mock_get_tasks.return_value = MockEventLoop()
        mock_asyncio_gather.return_value = mock_tasks
        mock_loop = MagicMock(spec=asyncio.AbstractEventLoop)
        mock_get_event_loop.return_value = mock_loop

        aws_connector.get_multiple_s3_objs(mock_bucket, mock_s3_objs)

        mock_get_event_loop.assert_called_once()

    def test_s3_to_json_key(self):
        """
        Test we correctly translate S3 to a JSON key
        :return: None
        """
        from claws import aws_utils

        test_cases = [
            ("path/to/file.json", "file"),
            ("anotherpath/to/somefile.txt", "somefile"),
            ("filename.ext", "filename"),
            ("file_without_ext", "file_without_ext"),
        ]

        for key, expected in test_cases:
            assert aws_utils.AWSConnector.s3_to_json_key(key) == expected

    @pytest.mark.parametrize(
        "bucket, s3_path, content",
        [
            ("test-bucket", "path/to/file.txt", "Hello, World!"),
            ("another-bucket", "anotherpath/to/somefile.txt", "Test content"),
        ],
    )
    @mock_s3
    def test_s3_obj_to_str_success(self, bucket, s3_path, content):
        from claws import aws_utils

        aws_connect = aws_utils.AWSConnector(bucket=bucket)

        s3_client = aws_connect.s3_client

        aws_connect.s3_resource.create_bucket(Bucket=bucket)

        aws_connect.s3_client.put_bucket_policy(
            Bucket=bucket,
            Policy='{"Version":"2012-10-17", "Statement":[{"Sid":"AddPerm", '
            '"Effect":"Allow", "Principal": "*", "Action":['
            '"s3:GetObject"], "Resource":["arn:aws:s3:::' + bucket + '/*"]}]}',
        )

        s3_client.put_object(Bucket=bucket, Key=s3_path, Body=content)

        result = aws_connect.s3_obj_to_str(bucket, s3_path)

        assert result == content

    @mock_s3
    def test_push_json_to_s3(self):
        # Test data
        bucket = "mybucket"
        path = "mypath.json"
        data = {"key1": "value1", "key2": "value2"}

        from claws import aws_utils

        aws_connect = aws_utils.AWSConnector(bucket=bucket)

        aws_connect.s3_resource.create_bucket(Bucket=bucket)

        aws_connect.s3_client.put_bucket_policy(
            Bucket=bucket,
            Policy='{"Version":"2012-10-17", "Statement":[{"Sid":"AddPerm", '
            '"Effect":"Allow", "Principal": "*", "Action":['
            '"s3:GetObject"], "Resource":["arn:aws:s3:::' + bucket + '/*"]}]}',
        )

        # Call the method
        aws_connect.push_json_to_s3(data, bucket, path, verbose=False)

        result = aws_connect.s3_obj_to_str(bucket, path)

        assert result == json.dumps(data, indent=4)

    @mock_s3
    def test_list_prefix(self):
        from claws import aws_utils

        prefix = "prefix/"
        aws_connector = aws_utils.AWSConnector(bucket="test-bucket")

        s3 = aws_connector.s3_resource
        bucket = s3.create_bucket(Bucket="test-bucket")
        bucket.Object("prefix/test1.txt").put()
        bucket.Object("prefix/test2.csv").put()
        bucket.Object("other_prefix/test3.txt").put()

        # Test filtering by file extension
        expected_files = {"test1.txt"}
        assert aws_connector.list_prefix(prefix, ".txt") == expected_files

        # Test without filtering by file extension
        expected_files = {"test1.txt", "test2.csv"}
        assert aws_connector.list_prefix(prefix) == expected_files

        # Test with non-existing prefix
        expected_files = set()
        assert (
            aws_connector.list_prefix("non_existing_prefix") == expected_files
        )

    @pytest.mark.parametrize(
        "bucket, s3_path, raise_on_fail, expected",
        [
            ("test-bucket", "path/to/missing.txt", False, "{}"),
            (
                "another-bucket",
                "anotherpath/to/somefile.txt",
                True,
                Exception,
            ),
        ],
    )
    def test_s3_obj_to_str_error(
        self, bucket, s3_path, raise_on_fail, expected
    ):
        from claws import aws_utils

        with mock_s3():
            aws_connect = aws_utils.AWSConnector(bucket=bucket)

            s3_client = aws_connect.s3_client

            s3_client.create_bucket(Bucket=bucket)

            aws_connect.s3_client.put_bucket_policy(
                Bucket=bucket,
                Policy='{"Version":"2012-10-17", "Statement":'
                '[{"Sid":"AddPerm", '
                '"Effect":"Allow", "Principal": "*", "Action":['
                '"s3:GetObject"], "Resource":["arn:aws:s3:::'
                + bucket
                + '/*"]}]}',
            )

            if raise_on_fail:
                with pytest.raises(expected):
                    aws_connect.s3_obj_to_str(
                        bucket,
                        s3_path,
                        raise_on_fail=raise_on_fail,
                    )
            else:
                result = aws_connect.s3_obj_to_str(
                    bucket,
                    s3_path,
                    raise_on_fail=raise_on_fail,
                )
                assert result == expected


class MockEventLoop:
    def run_until_complete(self, coro):
        mock_tasks = [MagicMock(), MagicMock(), MagicMock()]
        mock_session = MagicMock()
        return mock_tasks, mock_session


class MockResponse:
    def __init__(self, text, status):
        self._text = text
        self.status = status

    async def text(self):
        return self._text

    async def read(self):
        ret = await self.text()

        if ret == "{}":
            return {}

        return ret.encode("utf-8")

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


class MockAsyncS3Client:
    def generate_presigned_url(self, operation, data):
        return "https://a-dummy-url.com"
