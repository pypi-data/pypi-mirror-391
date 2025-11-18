"""Tests for error handling and transformation"""
import pytest
from bluma.errors import ValidationError, AuthenticationError, InsufficientCreditsError

# TODO: Add comprehensive error tests
def test_validation_error():
    """Test ValidationError creation"""
    error = ValidationError(400, {"message": "Invalid input"})
    assert error.status == 400
