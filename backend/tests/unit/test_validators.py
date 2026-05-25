from app.utils.validators import is_valid_url, sanitize_client_id


def test_valid_https_url():
    assert is_valid_url("https://example.com/page") is True


def test_valid_http_url():
    assert is_valid_url("http://localhost:8080") is True


def test_invalid_url_no_scheme():
    assert is_valid_url("example.com") is False


def test_invalid_url_ftp():
    assert is_valid_url("ftp://files.example.com") is False


def test_sanitize_client_id_removes_special_chars():
    assert sanitize_client_id("client@123!") == "client123"


def test_sanitize_client_id_allows_dash_underscore():
    assert sanitize_client_id("client-id_1") == "client-id_1"


def test_sanitize_client_id_truncates_to_64():
    long_id = "a" * 100
    assert len(sanitize_client_id(long_id)) == 64
