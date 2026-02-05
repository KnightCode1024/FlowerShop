import pytest
from types import SimpleNamespace

from src.flowershop_api.repositories.s3 import S3Repository
from src.flowershop_api.entrypoint.config import config


class DummyClient:
    def __init__(self, raise_on_delete=False):
        self._last_put = None
        self._last_delete = None
        self.raise_on_delete = raise_on_delete

    async def put_object(self, **kwargs):
        self._last_put = kwargs
        return None

    async def delete_object(self, **kwargs):
        if self.raise_on_delete:
            raise Exception("delete failed")
        self._last_delete = kwargs
        return None


class DummyClientCtx:
    def __init__(self, client):
        self.client = client

    async def __aenter__(self):
        return self.client

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummyUploadFile:
    def __init__(self, filename: str, content: bytes, content_type: str = "image/png"):
        self.filename = filename
        self._content = content
        self.content_type = content_type

    async def read(self):
        return self._content


@pytest.mark.asyncio
async def test_upload_image_should_call_put_and_return_url():
    # Arrange
    repo = S3Repository()
    # override s3_client with dummy
    dummy_client = DummyClient()
    repo.s3_client = SimpleNamespace(bucket_name="test-bucket", get_client=lambda: DummyClientCtx(dummy_client))

    # set predictable config
    config.s3.PUBLIC_ENDPOINT = "http://public.example"
    config.s3.BUCKET_NAME = "test-bucket"

    img = DummyUploadFile("flower.png", b"PNGDATA", "image/png")

    # Act
    url = await repo.upload_image(img, product_id=42)

    # Assert - url contains expected parts
    assert "/products/42/" in url
    assert url.endswith(".png")

    # Assert put_object was called with expected args
    assert dummy_client._last_put is not None
    assert dummy_client._last_put["Bucket"] == "test-bucket"
    assert dummy_client._last_put["ContentType"] == "image/png"
    assert dummy_client._last_put["Body"] == b"PNGDATA"
    assert "Key" in dummy_client._last_put and dummy_client._last_put["Key"].startswith("products/42/")


@pytest.mark.asyncio
async def test_upload_images_multiple_files_return_list_of_urls():
    repo = S3Repository()
    dummy_client = DummyClient()
    repo.s3_client = SimpleNamespace(bucket_name="bucket", get_client=lambda: DummyClientCtx(dummy_client))

    config.s3.PUBLIC_ENDPOINT = "http://public"
    config.s3.BUCKET_NAME = "bucket"

    images = [
        DummyUploadFile("a.png", b"a", "image/png"),
        DummyUploadFile("b.jpg", b"b", "image/jpeg"),
    ]

    urls = await repo.upload_images(images, product_id=7)
    assert isinstance(urls, list)
    assert len(urls) == 2
    assert "/products/7/" in urls[0]
    assert "/products/7/" in urls[1]
    assert urls[0].endswith(".png")
    assert urls[1].endswith(".jpg")


@pytest.mark.asyncio
async def test_delete_image_success_and_failure():
    repo = S3Repository()
    # success case
    success_client = DummyClient()
    repo.s3_client = SimpleNamespace(bucket_name="bucket-1", get_client=lambda: DummyClientCtx(success_client))
    img_url = f"http://public/bucket-1/products/9/somekey.png"
    res = await repo.delete_image(img_url)
    assert res is True
    assert success_client._last_delete["Bucket"] == "bucket-1"
    assert success_client._last_delete["Key"] == "products/9/somekey.png"

    # failure case - client raises
    fail_client = DummyClient(raise_on_delete=True)
    repo.s3_client = SimpleNamespace(bucket_name="bucket-1", get_client=lambda: DummyClientCtx(fail_client))
    res2 = await repo.delete_image(img_url)
    assert res2 is False


@pytest.mark.asyncio
async def test_delete_images_counts_deleted_items():
    repo = S3Repository()
    # one will succeed, one will fail (invalid url)
    client = DummyClient()
    repo.s3_client = SimpleNamespace(bucket_name="bucket-x", get_client=lambda: DummyClientCtx(client))
    urls = [
        f"http://public/bucket-x/products/1/k1.png",
        f"http://public/bucket-x/products/2/k2.png",
    ]
    # monkeypatch delete_image to simulate one failure
    orig_delete = repo.delete_image

    async def fake_delete(u):
        if "products/1" in u:
            return True
        return False

    repo.delete_image = fake_delete
    deleted_count = await repo.delete_images(urls)
    assert deleted_count == 1
