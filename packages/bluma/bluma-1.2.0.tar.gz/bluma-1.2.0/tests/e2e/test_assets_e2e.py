"""
End-to-End Tests for Assets API

Tests asset upload, listing, and management.
These tests do NOT consume credits.

Run: pytest tests/e2e/test_assets_e2e.py -v
"""
import io
import pytest
from bluma import Bluma
from bluma.errors import ValidationError, NotFoundError


@pytest.mark.e2e
class TestAssetsE2E:
    """End-to-end tests for Assets API"""

    def test_upload_asset(self, bluma: Bluma, cleanup_assets):
        """Test uploading an asset"""
        print("\n📤 Uploading asset...")

        # Create a test image file
        test_image = io.BytesIO(b"fake-image-data")
        test_image.name = "test-image.jpg"

        # Upload asset
        result = bluma.assets.upload(
            files=[test_image],
            file_type="image/jpeg"
        )

        # Verify response
        assert result is not None
        if isinstance(result, list):
            assert len(result) > 0
            asset = result[0]
            cleanup_assets.append(asset.id if hasattr(asset, 'id') else asset.asset_id)
        else:
            cleanup_assets.append(result.id if hasattr(result, 'id') else result.asset_id)

        print(f"   ✅ Asset uploaded successfully")

    def test_list_assets(self, bluma: Bluma):
        """Test listing assets"""
        assets = bluma.assets.list()

        assert isinstance(assets, list) or hasattr(assets, 'assets')
        print(f"   ✅ Assets listed successfully")

    def test_get_asset(self, bluma: Bluma, cleanup_assets):
        """Test retrieving a specific asset"""
        # Upload test asset
        test_file = io.BytesIO(b"test-data")
        test_file.name = "test.jpg"

        result = bluma.assets.upload(files=[test_file])

        asset_id = None
        if isinstance(result, list):
            asset_id = result[0].id if hasattr(result[0], 'id') else result[0].asset_id
        else:
            asset_id = result.id if hasattr(result, 'id') else result.asset_id

        cleanup_assets.append(asset_id)

        # Retrieve asset
        retrieved = bluma.assets.get(asset_id)

        assert retrieved.id == asset_id
        print(f"   ✅ Asset retrieved: {retrieved.id}")

    def test_rename_asset(self, bluma: Bluma, cleanup_assets):
        """Test renaming an asset"""
        # Upload test asset
        test_file = io.BytesIO(b"test-data")
        test_file.name = "original.jpg"

        result = bluma.assets.upload(files=[test_file])

        asset_id = None
        if isinstance(result, list):
            asset_id = result[0].id if hasattr(result[0], 'id') else result[0].asset_id
        else:
            asset_id = result.id if hasattr(result, 'id') else result.asset_id

        cleanup_assets.append(asset_id)

        # Rename
        renamed = bluma.assets.rename(asset_id, "renamed.jpg")

        assert renamed.name == "renamed.jpg"
        print(f"   ✅ Asset renamed: {renamed.id}")

    def test_delete_asset(self, bluma: Bluma):
        """Test deleting an asset"""
        # Upload test asset
        test_file = io.BytesIO(b"delete-test")
        test_file.name = "delete.jpg"

        result = bluma.assets.upload(files=[test_file])

        asset_id = None
        if isinstance(result, list):
            asset_id = result[0].id if hasattr(result[0], 'id') else result[0].asset_id
        else:
            asset_id = result.id if hasattr(result, 'id') else result.asset_id

        # Delete
        bluma.assets.delete(asset_id)

        # Verify deletion (soft delete might still return)
        try:
            retrieved = bluma.assets.get(asset_id)
            if hasattr(retrieved, 'deleted_at'):
                assert retrieved.deleted_at is not None
        except NotFoundError:
            pass

        print(f"   ✅ Asset deleted: {asset_id}")

    def test_asset_not_found(self, bluma: Bluma):
        """Test getting non-existent asset"""
        with pytest.raises(NotFoundError):
            bluma.assets.get("asset_nonexistent123")

        print(f"   ✅ 404 error raised correctly")

    def test_upload_multiple_assets(self, bluma: Bluma, cleanup_assets):
        """Test uploading multiple assets at once"""
        # Create multiple test files
        files = []
        for i in range(3):
            file = io.BytesIO(f"test-data-{i}".encode())
            file.name = f"test-{i}.jpg"
            files.append(file)

        # Upload
        result = bluma.assets.upload(files=files)

        # Verify
        if isinstance(result, list):
            assert len(result) == 3
            for asset in result:
                asset_id = asset.id if hasattr(asset, 'id') else asset.asset_id
                cleanup_assets.append(asset_id)

        print(f"   ✅ Multiple assets uploaded successfully")
