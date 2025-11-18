"""Tests for CollectionsResource"""
import pytest
from pytest_httpx import HTTPXMock
from bluma.types import Collection, Asset
from bluma.errors import NotFoundError


class TestCollectionsCreate:
    """Test collections.create()"""

    def test_create_collection_success(self, client, httpx_mock: HTTPXMock, mock_collection_data):
        """Test successful collection creation"""
        httpx_mock.add_response(json=mock_collection_data, status_code=201)

        collection = client.collections.create(
            name="Product Photos", description="High-quality product photography"
        )

        assert isinstance(collection, Collection)
        assert collection.id == "coll_abc123"
        assert collection.name == "Product Photos"
        assert collection.description == "High-quality product photography"
        assert collection.asset_count == 5

    def test_create_collection_without_description(self, client, httpx_mock: HTTPXMock, mock_collection_data):
        """Test collection creation without description"""
        httpx_mock.add_response(json=mock_collection_data, status_code=201)

        collection = client.collections.create(name="My Collection")

        assert isinstance(collection, Collection)
        request = httpx_mock.get_request()
        body = request.read().decode()
        assert "name" in body


class TestCollectionsList:
    """Test collections.list()"""

    def test_list_collections_success(self, client, httpx_mock: HTTPXMock, mock_collection_data):
        """Test listing collections"""
        httpx_mock.add_response(
            json={"collections": [mock_collection_data, {**mock_collection_data, "id": "coll_def456"}]}
        )

        collections = client.collections.list()

        assert len(collections) == 2
        assert all(isinstance(c, Collection) for c in collections)
        assert collections[0].id == "coll_abc123"
        assert collections[1].id == "coll_def456"


class TestCollectionsGet:
    """Test collections.get()"""

    def test_get_collection_success(self, client, httpx_mock: HTTPXMock, mock_collection_data):
        """Test getting collection details"""
        httpx_mock.add_response(json=mock_collection_data)

        collection = client.collections.get(collection_id="coll_abc123")

        assert isinstance(collection, Collection)
        assert collection.id == "coll_abc123"
        assert collection.name == "Product Photos"

    def test_get_collection_not_found(self, client, httpx_mock: HTTPXMock):
        """Test getting non-existent collection"""
        error_response = {"error": {"type": "not_found", "status": 404, "detail": "Collection not found"}}
        httpx_mock.add_response(json=error_response, status_code=404)

        with pytest.raises(NotFoundError):
            client.collections.get(collection_id="invalid_id")


class TestCollectionsRename:
    """Test collections.rename()"""

    def test_rename_collection_success(self, client, httpx_mock: HTTPXMock, mock_collection_data):
        """Test renaming collection"""
        updated_data = {**mock_collection_data, "name": "Updated Name"}
        httpx_mock.add_response(json=updated_data)

        collection = client.collections.rename(collection_id="coll_abc123", name="Updated Name")

        assert collection.name == "Updated Name"
        request = httpx_mock.get_request()
        assert request.method == "PUT"
        assert "/asset-pool/collections/coll_abc123" in str(request.url)


class TestCollectionsDelete:
    """Test collections.delete()"""

    def test_delete_collection_success(self, client, httpx_mock: HTTPXMock):
        """Test deleting a collection"""
        httpx_mock.add_response(json={}, status_code=200)

        # Should not raise any exception
        client.collections.delete(collection_id="coll_abc123")

        request = httpx_mock.get_request()
        assert request.method == "DELETE"
        assert "/asset-pool/collections/coll_abc123" in str(request.url)


class TestCollectionsAssets:
    """Test collection asset management"""

    def test_add_assets_to_collection(self, client, httpx_mock: HTTPXMock):
        """Test adding assets to collection"""
        httpx_mock.add_response(json={}, status_code=200)

        client.collections.add_assets(collection_id="coll_abc123", asset_ids=["asset_1", "asset_2", "asset_3"])

        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert "/asset-pool/collections/coll_abc123/assets" in str(request.url)
        body = request.read().decode()
        assert "assetIds" in body

    def test_remove_asset_from_collection(self, client, httpx_mock: HTTPXMock):
        """Test removing asset from collection"""
        httpx_mock.add_response(json={}, status_code=200)

        client.collections.remove_asset(collection_id="coll_abc123", asset_id="asset_1")

        request = httpx_mock.get_request()
        assert request.method == "DELETE"
        assert "/asset-pool/collections/coll_abc123/assets/asset_1" in str(request.url)

    def test_list_collection_assets(self, client, httpx_mock: HTTPXMock, mock_asset_data):
        """Test listing assets in collection"""
        httpx_mock.add_response(json={"assets": [mock_asset_data, {**mock_asset_data, "id": "asset_def456"}]})

        assets = client.collections.list_assets(collection_id="coll_abc123")

        assert len(assets) == 2
        assert all(isinstance(a, Asset) for a in assets)
        assert assets[0].id == "asset_abc123"
        assert assets[1].id == "asset_def456"
