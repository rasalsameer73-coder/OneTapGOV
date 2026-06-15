import pytest

if __name__ == '__main__':
    ret = pytest.main(["-q", "tests/api/test_documents.py"])
    print('PYTEST_EXIT_CODE:', ret)
