"""
End-to-End Tests for Template Variants API

Tests template variant CRUD operations.
These tests do NOT consume credits.

Run: pytest tests/e2e/test_variants_e2e.py -v
"""
import pytest
from bluma import Bluma
from bluma.errors import ValidationError, NotFoundError


@pytest.mark.e2e
class TestVariantsE2E:
    """End-to-end tests for Template Variants API"""

    def test_create_variant(self, bluma: Bluma, test_template_id: str, cleanup_variants):
        """Test creating a template variant"""
        print(f"\n🎨 Creating variant for template: {test_template_id}")

        variant = bluma.variants.create(
            template_id=test_template_id,
            name="Test Variant E2E",
            settings={
                "systemPrompt": "Use a professional tone",
                "compositionProps": {
                    "voiceId": "female-professional",
                    "primaryColor": "#0066CC"
                }
            }
        )

        cleanup_variants.append((test_template_id, variant.id))

        # Verify response
        assert variant.id is not None
        assert variant.template_id == test_template_id
        assert variant.name == "Test Variant E2E"
        assert variant.is_active is True
        assert variant.created_at is not None

        print(f"   ✅ Variant created: {variant.id}")
        print(f"      • Name: {variant.name}")

    def test_list_variants(self, bluma: Bluma, test_template_id: str, cleanup_variants):
        """Test listing template variants"""
        # Create a test variant first
        variant = bluma.variants.create(
            template_id=test_template_id,
            name="List Test Variant",
            settings={"systemPrompt": "Test"}
        )
        cleanup_variants.append((test_template_id, variant.id))

        # List variants
        variants = bluma.variants.list(test_template_id)

        assert isinstance(variants, list) or hasattr(variants, 'variants')
        print(f"   ✅ Listed variants for {test_template_id}")

    def test_get_variant(self, bluma: Bluma, test_template_id: str, cleanup_variants):
        """Test retrieving a specific variant"""
        created = bluma.variants.create(
            template_id=test_template_id,
            name="Get Test Variant",
            settings={}
        )
        cleanup_variants.append((test_template_id, created.id))

        retrieved = bluma.variants.get(test_template_id, created.id)

        assert retrieved.id == created.id
        assert retrieved.name == created.name
        print(f"   ✅ Variant retrieved: {retrieved.id}")

    def test_update_variant(self, bluma: Bluma, test_template_id: str, cleanup_variants):
        """Test updating a variant"""
        created = bluma.variants.create(
            template_id=test_template_id,
            name="Original Name",
            settings={}
        )
        cleanup_variants.append((test_template_id, created.id))

        updated = bluma.variants.update(
            template_id=test_template_id,
            variant_id=created.id,
            name="Updated Name"
        )

        assert updated.name == "Updated Name"
        print(f"   ✅ Variant updated: {updated.id}")

    def test_delete_variant(self, bluma: Bluma, test_template_id: str):
        """Test deleting a variant"""
        variant = bluma.variants.create(
            template_id=test_template_id,
            name="Delete Test",
            settings={}
        )

        bluma.variants.delete(test_template_id, variant.id)

        with pytest.raises(NotFoundError):
            bluma.variants.get(test_template_id, variant.id)

        print(f"   ✅ Variant deleted: {variant.id}")

    def test_variant_not_found(self, bluma: Bluma, test_template_id: str):
        """Test getting non-existent variant"""
        with pytest.raises(NotFoundError):
            bluma.variants.get(test_template_id, "var_nonexistent123")

        print(f"   ✅ 404 error raised correctly")
