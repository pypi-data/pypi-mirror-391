"""Tests for AssetsResource"""
import pytest
from pytest_httpx import HTTPXMock
from bluma.types import Asset, AssetUploadResponse
from bluma.errors import NotFoundError


class TestAssetsUpload:
    """Test assets.upload()"""

    def test_upload_asset_success(self, client, httpx_mock: HTTPXMock, mock_asset_upload_response_data):
        """Test successful asset upload initiation"""
        httpx_mock.add_response(json=mock_asset_upload_response_data, status_code=200)

        upload_response = client.assets.upload(file_name="photo.jpg", file_type="image/jpeg")

        assert isinstance(upload_response, AssetUploadResponse)
        assert upload_response.asset_id == "asset_abc123"
        assert upload_response.upload_url.startswith("https://s3.amazonaws.com")
        assert upload_response.cdn_url.startswith("https://cdn.getbluma.com")

    def test_upload_asset_with_collections(self, client, httpx_mock: HTTPXMock, mock_asset_upload_response_data):
        """Test asset upload with collection IDs"""
        httpx_mock.add_response(json=mock_asset_upload_response_data, status_code=200)

        client.assets.upload(
            file_name="photo.jpg", file_type="image/jpeg", collection_ids=["coll_1", "coll_2"]
        )

        request = httpx_mock.get_request()
        body = request.read().decode()
        assert "collectionIds" in body


class TestAssetsGet:
    """Test assets.get()"""

    def test_get_asset_success(self, client, httpx_mock: HTTPXMock, mock_asset_data):
        """Test getting asset details"""
        httpx_mock.add_response(json=mock_asset_data)

        asset = client.assets.get(asset_id="asset_abc123")

        assert isinstance(asset, Asset)
        assert asset.id == "asset_abc123"
        assert asset.name == "product-photo.jpg"
        assert asset.file_type == "image/jpeg"
        assert asset.deleted_at is None

    def test_get_asset_not_found(self, client, httpx_mock: HTTPXMock):
        """Test getting non-existent asset"""
        error_response = {"error": {"type": "not_found", "status": 404, "detail": "Asset not found"}}
        httpx_mock.add_response(json=error_response, status_code=404)

        with pytest.raises(NotFoundError):
            client.assets.get(asset_id="invalid_id")


class TestAssetsList:
    """Test assets.list()"""

    def test_list_assets_all(self, client, httpx_mock: HTTPXMock, mock_asset_data):
        """Test listing all assets"""
        httpx_mock.add_response(json={"assets": [mock_asset_data, {**mock_asset_data, "id": "asset_def456"}]})

        assets = client.assets.list()

        assert len(assets) == 2
        assert all(isinstance(a, Asset) for a in assets)
        assert assets[0].id == "asset_abc123"
        assert assets[1].id == "asset_def456"

    def test_list_assets_with_file_type_filter(self, client, httpx_mock: HTTPXMock, mock_asset_data):
        """Test listing assets filtered by file type"""
        httpx_mock.add_response(json={"assets": [mock_asset_data]})

        assets = client.assets.list(file_type="image/jpeg")

        request = httpx_mock.get_request()
        assert "fileType=image%2Fjpeg" in str(request.url) or "fileType=image/jpeg" in str(request.url)
        assert len(assets) == 1

    def test_list_assets_with_collection_filter(self, client, httpx_mock: HTTPXMock, mock_asset_data):
        """Test listing assets filtered by collection"""
        httpx_mock.add_response(json={"assets": [mock_asset_data]})

        assets = client.assets.list(collection_id="coll_abc123")

        request = httpx_mock.get_request()
        assert "collectionId=coll_abc123" in str(request.url)

    def test_list_assets_include_deleted(self, client, httpx_mock: HTTPXMock, mock_asset_data):
        """Test listing assets including deleted ones"""
        deleted_asset = {**mock_asset_data, "id": "asset_deleted", "deleted_at": "2024-01-15T10:00:00Z"}
        httpx_mock.add_response(json={"assets": [mock_asset_data, deleted_asset]})

        assets = client.assets.list(include_deleted=True)

        request = httpx_mock.get_request()
        assert "includeDeleted=true" in str(request.url)
        assert len(assets) == 2


class TestAssetsRename:
    """Test assets.rename()"""

    def test_rename_asset_success(self, client, httpx_mock: HTTPXMock, mock_asset_data):
        """Test renaming asset"""
        updated_data = {**mock_asset_data, "name": "updated-photo.jpg"}
        httpx_mock.add_response(json=updated_data)

        asset = client.assets.rename(asset_id="asset_abc123", name="updated-photo.jpg")

        assert asset.name == "updated-photo.jpg"
        request = httpx_mock.get_request()
        assert request.method == "PUT"
        assert "/asset-pool/assets/asset_abc123" in str(request.url)


class TestAssetsDelete:
    """Test assets.delete()"""

    def test_delete_asset_success(self, client, httpx_mock: HTTPXMock):
        """Test soft deleting an asset"""
        httpx_mock.add_response(json={}, status_code=200)

        # Should not raise any exception
        client.assets.delete(asset_id="asset_abc123")

        request = httpx_mock.get_request()
        assert request.method == "DELETE"
        assert "/asset-pool/assets/asset_abc123" in str(request.url)


class TestAssetsRecover:
    """Test assets.recover()"""

    def test_recover_asset_success(self, client, httpx_mock: HTTPXMock, mock_asset_data):
        """Test recovering a soft-deleted asset"""
        recovered_data = {**mock_asset_data, "deleted_at": None}
        httpx_mock.add_response(json=recovered_data)

        asset = client.assets.recover(asset_id="asset_abc123")

        assert isinstance(asset, Asset)
        assert asset.deleted_at is None
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert "/asset-pool/assets/asset_abc123/recover" in str(request.url)


class TestAssetsGetRandom:
    """Test assets.get_random()"""

    def test_get_random_asset_success(self, client, httpx_mock: HTTPXMock, mock_asset_data):
        """Test getting a random asset"""
        httpx_mock.add_response(json=mock_asset_data)

        asset = client.assets.get_random(file_type="image/jpeg")

        assert isinstance(asset, Asset)
        assert asset.id == "asset_abc123"
        request = httpx_mock.get_request()
        assert "fileType=image%2Fjpeg" in str(request.url) or "fileType=image/jpeg" in str(request.url)

    def test_get_random_asset_with_collection(self, client, httpx_mock: HTTPXMock, mock_asset_data):
        """Test getting random asset from specific collection"""
        httpx_mock.add_response(json=mock_asset_data)

        client.assets.get_random(file_type="image/jpeg", collection_id="coll_abc123")

        request = httpx_mock.get_request()
        assert "collectionId=coll_abc123" in str(request.url)

    def test_get_random_asset_exclude_used(self, client, httpx_mock: HTTPXMock, mock_asset_data):
        """Test getting random asset excluding already used ones"""
        httpx_mock.add_response(json=mock_asset_data)

        client.assets.get_random(file_type="image/jpeg", used_asset_ids=["asset_1", "asset_2"])

        request = httpx_mock.get_request()
        assert "excludeIds" in str(request.url)
