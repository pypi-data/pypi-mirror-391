"""Tests for VariantsResource"""
import pytest
from pytest_httpx import HTTPXMock
from bluma.types import TemplateVariant
from bluma.errors import NotFoundError


class TestVariantsCreate:
    """Test variants.create()"""

    def test_create_variant_success(self, client, httpx_mock: HTTPXMock, mock_variant_data):
        """Test successful variant creation"""
        httpx_mock.add_response(json=mock_variant_data, status_code=201)

        variant = client.variants.create(
            template_id="meme-dialogue",
            name="Funny Tone Preset",
            settings={
                "systemPrompt": "Use a funny tone",
                "compositionProps": {
                    "voiceId": "female-casual",
                    "primaryColor": "#FF69B4",
                },
            },
        )

        assert isinstance(variant, TemplateVariant)
        assert variant.id == "var_abc123"
        assert variant.name == "Funny Tone Preset"
        assert variant.template_id == "meme-dialogue"
        assert variant.is_active is True

    def test_create_variant_without_settings(self, client, httpx_mock: HTTPXMock, mock_variant_data):
        """Test variant creation without settings"""
        httpx_mock.add_response(json=mock_variant_data, status_code=201)

        variant = client.variants.create(
            template_id="meme-dialogue",
            name="Basic Preset",
        )

        assert isinstance(variant, TemplateVariant)
        request = httpx_mock.get_request()
        assert "payload" not in request.read().decode() or request.read().decode().count("settings") == 0


class TestVariantsList:
    """Test variants.list()"""

    def test_list_variants_success(self, client, httpx_mock: HTTPXMock, mock_variant_data):
        """Test listing variants for a template"""
        httpx_mock.add_response(json={"variants": [mock_variant_data, {**mock_variant_data, "id": "var_def456"}]})

        variants = client.variants.list(template_id="meme-dialogue")

        assert len(variants) == 2
        assert all(isinstance(v, TemplateVariant) for v in variants)
        assert variants[0].id == "var_abc123"
        assert variants[1].id == "var_def456"


class TestVariantsGet:
    """Test variants.get()"""

    def test_get_variant_success(self, client, httpx_mock: HTTPXMock, mock_variant_data):
        """Test getting variant details"""
        httpx_mock.add_response(json=mock_variant_data)

        variant = client.variants.get(template_id="meme-dialogue", variant_id="var_abc123")

        assert isinstance(variant, TemplateVariant)
        assert variant.id == "var_abc123"
        assert variant.name == "Funny Tone Preset"

    def test_get_variant_not_found(self, client, httpx_mock: HTTPXMock, mock_error_response):
        """Test getting non-existent variant"""
        error_response = {
            "error": {
                "type": "not_found",
                "status": 404,
                "detail": "Variant not found",
            }
        }
        httpx_mock.add_response(json=error_response, status_code=404)

        with pytest.raises(NotFoundError):
            client.variants.get(template_id="meme-dialogue", variant_id="invalid_id")


class TestVariantsUpdate:
    """Test variants.update()"""

    def test_update_variant_name(self, client, httpx_mock: HTTPXMock, mock_variant_data):
        """Test updating variant name"""
        updated_data = {**mock_variant_data, "name": "Updated Preset"}
        httpx_mock.add_response(json=updated_data)

        variant = client.variants.update(
            template_id="meme-dialogue", variant_id="var_abc123", name="Updated Preset"
        )

        assert variant.name == "Updated Preset"

    def test_update_variant_settings(self, client, httpx_mock: HTTPXMock, mock_variant_data):
        """Test updating variant settings"""
        httpx_mock.add_response(json=mock_variant_data)

        variant = client.variants.update(
            template_id="meme-dialogue",
            variant_id="var_abc123",
            settings={"systemPrompt": "New prompt"},
        )

        assert isinstance(variant, TemplateVariant)
        request = httpx_mock.get_request()
        body = request.read().decode()
        assert "payload" in body
        assert "settings" in body


class TestVariantsDelete:
    """Test variants.delete()"""

    def test_delete_variant_success(self, client, httpx_mock: HTTPXMock):
        """Test deleting a variant"""
        httpx_mock.add_response(json={}, status_code=200)

        # Should not raise any exception
        client.variants.delete(template_id="meme-dialogue", variant_id="var_abc123")

        request = httpx_mock.get_request()
        assert request.method == "DELETE"
        assert "/dashboard/templates/meme-dialogue/variants/var_abc123" in str(request.url)
