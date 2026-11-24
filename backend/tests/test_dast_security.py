import httpx
import pytest

BASE_URL = "http://127.0.0.1:8000"
HEADERS_CLOSE = {"Connection": "close"}


@pytest.fixture(scope="module")
def subscriber_session():
    with httpx.Client(base_url=BASE_URL, headers=HEADERS_CLOSE, timeout=10.0) as client:
        resp = client.post(
            "/api/v1/auth/login",
            data={
                "username": "subscriber@telecom.com",
                "password": "UserPassword123!",
            },
        )
        assert resp.status_code == 200, f"Subscriber login failed ({resp.status_code}): {resp.text}"
        return resp.json(), dict(resp.cookies)


def test_dast_01_sqli_login_bypass():
    """DAST-01: Verify SQL Injection payload cannot bypass authentication."""
    with httpx.Client(base_url=BASE_URL, headers=HEADERS_CLOSE, timeout=10.0) as client:
        resp = client.post(
            "/api/v1/auth/login",
            data={
                "username": "' OR '1'='1' --",
                "password": "invalid_password",
            },
        )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
    assert resp.json()["detail"] == "Incorrect email or password"


def test_dast_02_csrf_missing_header_blocked(subscriber_session):
    """DAST-02: Verify state-changing POST without X-CSRF-Token is rejected."""
    tokens, cookies = subscriber_session
    with httpx.Client(
        base_url=BASE_URL, headers=HEADERS_CLOSE, cookies=cookies, timeout=10.0
    ) as client:
        resp = client.post(
            "/api/v1/swap-requests",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "target_msisdn": "+353871234567",
                "current_iccid": "8935300000000000001",
                "reason": "Automated DAST CSRF Exploit Test",
                "swap_type": "physical_to_esim",
            },
        )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    assert "CSRF" in resp.json()["detail"]


def test_dast_03_rbac_admin_endpoint_blocked(subscriber_session):
    """DAST-03: Verify Subscriber JWT cannot access Admin global queue."""
    tokens, _ = subscriber_session
    with httpx.Client(base_url=BASE_URL, headers=HEADERS_CLOSE, timeout=10.0) as client:
        resp = client.get(
            "/api/v1/admin/swap-requests",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    assert "Admin privileges required." in resp.json()["detail"]


def test_dast_04_bola_idor_unauthorized_object_access(subscriber_session):
    """DAST-04: Verify BOLA/IDOR protection blocks unauthorized object access."""
    tokens, cookies = subscriber_session
    with httpx.Client(
        base_url=BASE_URL, headers=HEADERS_CLOSE, cookies=cookies, timeout=10.0
    ) as client:
        create_resp = client.post(
            "/api/v1/swap-requests",
            headers={
                "Authorization": f"Bearer {tokens['access_token']}",
                "X-CSRF-Token": tokens["csrf_token"],
            },
            json={
                "target_msisdn": "+353871234567",
                "current_iccid": "8935300000000000001",
                "reason": "Legitimate DAST Ownership Test",
                "swap_type": "physical_to_esim",
            },
        )
        assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
        created_id = create_resp.json()["id"]

        unauth_resp = client.get(f"/api/v1/swap-requests/{created_id}")
    assert unauth_resp.status_code == 401


def test_dast_05_security_headers_enforced():
    """DAST-05: Verify defensive HTTP response headers are present."""
    with httpx.Client(base_url=BASE_URL, headers=HEADERS_CLOSE, timeout=10.0) as client:
        resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert resp.headers.get("x-frame-options") == "DENY"
    assert resp.headers.get("x-content-type-options") == "nosniff"
    assert "strict-transport-security" in resp.headers
    assert "content-security-policy" in resp.headers