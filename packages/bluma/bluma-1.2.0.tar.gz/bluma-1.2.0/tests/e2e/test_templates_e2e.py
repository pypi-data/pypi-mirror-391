"""
End-to-End Tests for Templates API

Tests template listing and retrieval endpoints.
These tests do NOT consume credits.

Run: pytest tests/e2e/test_templates_e2e.py -v
"""
import pytest
from bluma import Bluma
from bluma.types import Template
from bluma.errors import NotFoundError


@pytest.mark.e2e
class TestTemplatesE2E:
    """End-to-end tests for Templates API"""

    def test_list_templates(self, bluma: Bluma):
        """Test listing all available templates"""
        print("\n📋 Listing templates...")

        templates = bluma.templates.list()

        # Verify response
        assert isinstance(templates, list)
        assert len(templates) > 0, "Expected at least one template"

        # Check first template structure
        first = templates[0]
        assert first.id is not None
        assert first.name is not None
        assert first.description is not None
        assert first.base_cost is not None
        assert first.base_cost > 0
        assert first.category is not None
        assert first.duration is not None
        assert first.aspect_ratio is not None
        assert first.context_schema is not None

        print(f"   ✅ Found {len(templates)} templates")
        print(f"   Sample templates:")
        for template in templates[:5]:
            print(f"      • {template.id}: {template.name} ({template.base_cost} credits)")

    def test_list_templates_has_common_templates(self, bluma: Bluma):
        """Test that common templates exist in the list"""
        templates = bluma.templates.list()

        template_ids = [t.id for t in templates]

        # Check for at least one known template
        # (adjust based on actual templates in your backend)
        common_templates = ["meme-dialogue", "news-anchor", "skincare-review", "feelset-slideshow"]

        found = [tid for tid in common_templates if tid in template_ids]

        assert len(found) > 0, f"Expected at least one common template, found: {template_ids}"

        print(f"   ✅ Found common templates: {found}")

    def test_get_template_by_id(self, bluma: Bluma, test_template_id: str):
        """Test retrieving a specific template by ID"""
        print(f"\n📄 Getting template: {test_template_id}")

        template = bluma.templates.get(test_template_id)

        # Verify response
        assert template.id == test_template_id
        assert template.name is not None
        assert template.description is not None
        assert template.base_cost > 0
        assert template.category is not None
        assert template.duration > 0
        assert template.aspect_ratio is not None
        assert template.context_schema is not None

        # Verify context schema structure
        assert isinstance(template.context_schema, dict)
        assert "type" in template.context_schema or "properties" in template.context_schema

        print(f"   ✅ Template retrieved successfully:")
        print(f"      • Name: {template.name}")
        print(f"      • Category: {template.category}")
        print(f"      • Base cost: {template.base_cost} credits")
        print(f"      • Duration: {template.duration}s")
        print(f"      • Aspect ratio: {template.aspect_ratio}")
        if template.example_url:
            print(f"      • Example: {template.example_url}")

    def test_get_template_not_found(self, bluma: Bluma):
        """Test that 404 is raised for non-existent template"""
        with pytest.raises(NotFoundError) as exc_info:
            bluma.templates.get("nonexistent-template-xyz")

        error = exc_info.value
        assert error.status_code == 404

        print(f"   ✅ 404 error raised correctly: {error}")

    def test_template_categories_exist(self, bluma: Bluma):
        """Test that templates have valid categories"""
        templates = bluma.templates.list()

        categories = set(t.category for t in templates if t.category)

        assert len(categories) > 0, "Expected templates to have categories"

        print(f"   ✅ Found {len(categories)} categories:")
        for category in sorted(categories):
            count = sum(1 for t in templates if t.category == category)
            print(f"      • {category}: {count} templates")

    def test_template_aspect_ratios(self, bluma: Bluma):
        """Test that templates have valid aspect ratios"""
        templates = bluma.templates.list()

        aspect_ratios = set(t.aspect_ratio for t in templates if t.aspect_ratio)

        # Common aspect ratios
        valid_ratios = ["9:16", "16:9", "1:1", "4:5"]

        print(f"   ✅ Found aspect ratios: {sorted(aspect_ratios)}")

        for ratio in aspect_ratios:
            assert ratio in valid_ratios or ":" in ratio, f"Unexpected aspect ratio: {ratio}"

    def test_template_cost_ranges(self, bluma: Bluma):
        """Test that template costs are reasonable"""
        templates = bluma.templates.list()

        costs = [t.base_cost for t in templates]

        min_cost = min(costs)
        max_cost = max(costs)
        avg_cost = sum(costs) / len(costs)

        assert min_cost > 0, "All templates should have cost > 0"
        assert max_cost < 100, "Template costs should be reasonable (< 100 credits)"

        print(f"   ✅ Cost analysis:")
        print(f"      • Min: {min_cost} credits")
        print(f"      • Max: {max_cost} credits")
        print(f"      • Average: {avg_cost:.1f} credits")

    def test_template_context_schema_validity(self, bluma: Bluma, test_template_id: str):
        """Test that template context schema is valid JSON Schema"""
        template = bluma.templates.get(test_template_id)

        schema = template.context_schema

        # Basic JSON Schema validation
        assert isinstance(schema, dict), "Schema should be a dict"

        # Common JSON Schema properties
        if "type" in schema:
            assert schema["type"] in ["object", "string", "array"], "Invalid schema type"

        if "properties" in schema:
            assert isinstance(schema["properties"], dict), "Properties should be a dict"

            # Check if 'prompt' property exists (common in templates)
            if "prompt" in schema["properties"]:
                prompt_schema = schema["properties"]["prompt"]
                assert "type" in prompt_schema, "Prompt should have a type"

        print(f"   ✅ Context schema is valid:")
        print(f"      • Type: {schema.get('type', 'not specified')}")
        if "properties" in schema:
            print(f"      • Properties: {list(schema['properties'].keys())}")

    def test_all_templates_accessible(self, bluma: Bluma):
        """Test that all listed templates can be retrieved individually"""
        templates = bluma.templates.list()

        print(f"\n🔍 Verifying all {len(templates)} templates are accessible...")

        failed = []

        for template in templates:
            try:
                retrieved = bluma.templates.get(template.id)
                assert retrieved.id == template.id
            except Exception as e:
                failed.append((template.id, str(e)))

        if failed:
            print(f"   ❌ Failed to retrieve {len(failed)} templates:")
            for template_id, error in failed:
                print(f"      • {template_id}: {error}")
            pytest.fail(f"Failed to retrieve {len(failed)} templates")

        print(f"   ✅ All {len(templates)} templates accessible")
