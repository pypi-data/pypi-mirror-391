"""
End-to-End Tests for Collections API

Tests collection CRUD and asset management.
These tests do NOT consume credits.

Run: pytest tests/e2e/test_collections_e2e.py -v
"""
import pytest
from bluma import Bluma
from bluma.errors import ValidationError, NotFoundError


@pytest.mark.e2e
class TestCollectionsE2E:
    """End-to-end tests for Collections API"""

    def test_create_collection(self, bluma: Bluma, cleanup_collections):
        """Test creating a collection"""
        print("\n📁 Creating collection...")

        collection = bluma.collections.create(
            name="E2E Test Collection",
            description="Collection for end-to-end testing",
            asset_type="all"
        )

        cleanup_collections.append(collection.id)

        assert collection.id is not None
        assert collection.name == "E2E Test Collection"
        assert collection.description == "Collection for end-to-end testing"
        assert collection.created_at is not None

        print(f"   ✅ Collection created: {collection.id}")

    def test_list_collections(self, bluma: Bluma, cleanup_collections):
        """Test listing collections"""
        # Create test collection
        collection = bluma.collections.create(
            name="List Test Collection",
            asset_type="images"
        )
        cleanup_collections.append(collection.id)

        # List collections
        collections = bluma.collections.list()

        assert isinstance(collections, list) or hasattr(collections, 'collections')
        print(f"   ✅ Collections listed successfully")

    def test_get_collection(self, bluma: Bluma, cleanup_collections):
        """Test retrieving a specific collection"""
        created = bluma.collections.create(
            name="Get Test Collection",
            asset_type="videos"
        )
        cleanup_collections.append(created.id)

        retrieved = bluma.collections.get(created.id)

        assert retrieved.id == created.id
        assert retrieved.name == created.name
        print(f"   ✅ Collection retrieved: {retrieved.id}")

    def test_update_collection(self, bluma: Bluma, cleanup_collections):
        """Test updating a collection"""
        collection = bluma.collections.create(
            name="Original Name",
            asset_type="all"
        )
        cleanup_collections.append(collection.id)

        updated = bluma.collections.update(
            collection_id=collection.id,
            name="Updated Name",
            description="Updated description"
        )

        assert updated.name == "Updated Name"
        print(f"   ✅ Collection updated: {updated.id}")

    def test_delete_collection(self, bluma: Bluma):
        """Test deleting a collection"""
        collection = bluma.collections.create(
            name="Delete Test",
            asset_type="all"
        )

        bluma.collections.delete(collection.id)

        # Verify deletion (soft delete might still return 200)
        try:
            retrieved = bluma.collections.get(collection.id)
            # If soft delete, check deleted_at field
            if hasattr(retrieved, 'deleted_at'):
                assert retrieved.deleted_at is not None
        except NotFoundError:
            # Hard delete
            pass

        print(f"   ✅ Collection deleted: {collection.id}")

    def test_collection_asset_management(self, bluma: Bluma, cleanup_collections):
        """Test adding and removing assets from collection"""
        collection = bluma.collections.create(
            name="Asset Management Test",
            asset_type="all"
        )
        cleanup_collections.append(collection.id)

        # Note: Adding assets requires existing asset IDs
        # This test is a placeholder for when assets are available
        print(f"   ℹ️  Asset management test requires pre-existing assets")
        pytest.skip("Implement after assets E2E tests")

    def test_collection_not_found(self, bluma: Bluma):
        """Test getting non-existent collection"""
        with pytest.raises(NotFoundError):
            bluma.collections.get("coll_nonexistent123")

        print(f"   ✅ 404 error raised correctly")
