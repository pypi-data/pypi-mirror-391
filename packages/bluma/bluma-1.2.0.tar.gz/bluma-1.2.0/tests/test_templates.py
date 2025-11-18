"""Tests for TemplatesResource"""
import pytest
from pytest_httpx import HTTPXMock
from bluma.types import Template
from bluma.errors import NotFoundError


class TestTemplatesList:
    """Test templates.list()"""

    def test_list_templates_success(self, client, httpx_mock: HTTPXMock, mock_template_data):
        """Test listing templates"""
        httpx_mock.add_response(
            json={"templates": [mock_template_data, {**mock_template_data, "id": "feelset-slideshow"}]}
        )

        templates = client.templates.list()

        assert len(templates) == 2
        assert all(isinstance(t, Template) for t in templates)
        assert templates[0].id == "meme-dialogue"
        assert templates[1].id == "feelset-slideshow"

    def test_list_templates_empty(self, client, httpx_mock: HTTPXMock):
        """Test listing templates when none exist"""
        httpx_mock.add_response(json={"templates": []})

        templates = client.templates.list()

        assert len(templates) == 0
        assert isinstance(templates, list)


class TestTemplatesGet:
    """Test templates.get()"""

    def test_get_template_success(self, client, httpx_mock: HTTPXMock, mock_template_data):
        """Test getting template details"""
        httpx_mock.add_response(json=mock_template_data)

        template = client.templates.get(template_id="meme-dialogue")

        assert isinstance(template, Template)
        assert template.id == "meme-dialogue"
        assert template.name == "Meme Dialogue"
        assert template.description == "Create funny dialogue videos"
        assert template.base_cost == 5
        assert template.category == "entertainment"
        assert template.duration == 60
        assert template.aspect_ratio == "9:16"
        assert template.context_schema == {"type": "object", "properties": {"prompt": {"type": "string"}}}
        assert template.example_url == "https://cdn.getbluma.com/examples/meme.mp4"

    def test_get_template_not_found(self, client, httpx_mock: HTTPXMock):
        """Test getting non-existent template"""
        error_response = {
            "error": {"type": "not_found", "status": 404, "detail": "Template not found"}
        }
        httpx_mock.add_response(json=error_response, status_code=404)

        with pytest.raises(NotFoundError):
            client.templates.get(template_id="invalid-template")

    def test_get_template_verifies_schema(self, client, httpx_mock: HTTPXMock, mock_template_data):
        """Test that template schema is properly structured"""
        httpx_mock.add_response(json=mock_template_data)

        template = client.templates.get(template_id="meme-dialogue")

        # Verify context_schema structure
        assert "type" in template.context_schema
        assert "properties" in template.context_schema
        assert "prompt" in template.context_schema["properties"]
