import pytest


@pytest.fixture
def tmp_repo(tmp_path):
    """A bare directory standing in for a repository under test."""
    return tmp_path
