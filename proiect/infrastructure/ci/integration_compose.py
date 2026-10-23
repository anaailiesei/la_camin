import json
import sys
import time
from urllib import request, error

BASE = "http://docker:8000"


def http_request(method: str, url: str, data=None, headers=None):
    headers = headers or {}
    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, data=body, headers=headers, method=method)

    try:
        with request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            try:
                parsed = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = raw
            return resp.status, parsed
    except error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = raw
        return e.code, parsed
    except Exception as e:
        raise RuntimeError(f"Request failed for {method} {url}: {e}") from e


def wait_for_service(url: str, timeout: int = 120):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            status, _ = http_request("GET", url)
            if 200 <= status < 500:
                return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError(f"Service did not become ready in time: {url}")


def assert_status(actual: int, expected: int, context: str):
    if actual != expected:
        raise RuntimeError(f"{context}: expected {expected}, got {actual}")

def get_id(body, context):
    if not isinstance(body, dict) or "id" not in body:
        raise RuntimeError(f"{context}: response missing id: {body}")
    return body["id"]


def register(username, email, password):
    status, body = http_request("POST", f"{BASE}/auth/register", {
        "username": username,
        "email": email,
        "password": password
    })

    if status not in (200, 201, 409):
        raise RuntimeError(f"register failed for {email}: status={status}, body={body}")

    print(f"Register {email}: {status}")


def login(email, password):
    status, body = http_request("POST", f"{BASE}/auth/login", {
        "identifier": email,
        "password": password
    })

    assert_status(status, 200, f"login {email}")

    if not isinstance(body, dict) or "token" not in body:
        raise RuntimeError(f"login response missing token: {body}")

    return body["token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def main():
    print("Waiting for auth service...")
    wait_for_service(f"{BASE}/auth/ping")

    print("Waiting for listing service...")
    wait_for_service(f"{BASE}/listings/ping")

    print("Waiting for message service...")
    wait_for_service(f"{BASE}/messages/ping")

    print("Checking auth ping...")
    status, body = http_request("GET", f"{BASE}/auth/ping")
    assert_status(status, 200, "auth ping")
    print(body)

    print("Checking listing ping...")
    status, body = http_request("GET", f"{BASE}/listings/ping")
    assert_status(status, 200, "listing ping")
    print(body)

    print("Checking message ping...")
    status, body = http_request("GET", f"{BASE}/messages/ping")
    assert_status(status, 200, "message ping")
    print(body)

    print("Registering users...")
    register("Ana Popescu", "ana@student.ro", "parola123")
    register("Ion Ionescu", "ion@student.ro", "parola123")

    print("Logging in users...")
    ana_token = login("ana@student.ro", "parola123")
    ion_token = login("ion@student.ro", "parola123")
    print("Tokens obtained.")

    print("Creating listing...")
    listing_payload = {
        "title": "Bicicleta urbana",
        "description": "Bicicleta in stare buna",
        "price": 250.00,
        "category": "Sport"
    }
    status, body = http_request(
        "POST",
        f"{BASE}/listings/create",
        listing_payload,
        headers={"Authorization": f"Bearer {ana_token}"}
    )
    assert_status(status, 201, "create listing")
    listing_id = get_id(body, "create listing")
    print(body)

    print("Getting listing by id...")
    status, body = http_request("GET", f"{BASE}/listings/{listing_id}")
    assert_status(status, 200, "get listing by id")
    print(body)

    print("Listing all listings...")
    status, body = http_request("GET", f"{BASE}/listings")
    assert_status(status, 200, "list listings")
    print("Listings returned.")

    print("Searching listings by category/title...")
    status, body = http_request(
        "GET",
        f"{BASE}/listings?category=Sport&title=Bicicleta&sortBy=price&direction=asc"
    )
    assert_status(status, 200, "search listings")
    print("Search returned.")

    print("Updating listing...")
    update_payload = {
        "title": "Bicicleta urbana actualizata",
        "description": "Bicicleta in stare foarte buna",
        "price": 300.00,
        "category": "Sport"
    }

    status, body = http_request(
        "PUT",
        f"{BASE}/listings/{listing_id}",
        update_payload,
        headers=auth_headers(ana_token)
    )
    assert_status(status, 200, "update listing")
    print(body)

    print("Checking unauthorized listing update...")
    status, body = http_request(
        "PUT",
        f"{BASE}/listings/{listing_id}",
        update_payload,
        headers=auth_headers(ion_token)
    )
    assert_status(status, 403, "unauthorized listing update")
    print("Unauthorized update correctly rejected.")

    print("Sending message...")
    message_payload = {
        "receiverId": 1,
        "listingId": listing_id,
        "content": "Salut, mai este disponibila bicicleta?"
    }

    status, body = http_request(
        "POST",
        f"{BASE}/messages/send",
        message_payload,
        headers=auth_headers(ion_token)
    )
    assert_status(status, 201, "send message")
    message_id = get_id(body, "send message")
    print(body)

    print("Checking inbox...")
    status, body = http_request(
        "GET",
        f"{BASE}/messages/inbox",
        headers=auth_headers(ana_token)
    )
    assert_status(status, 200, "message inbox")
    print("Inbox returned.")

    print("Checking conversation...")
    status, body = http_request(
        "GET",
        f"{BASE}/messages/conversation/2",
        headers=auth_headers(ana_token)
    )
    assert_status(status, 200, "message conversation")
    print("Conversation returned.")

    print("Marking message as read...")
    status, body = http_request(
        "PUT",
        f"{BASE}/messages/{message_id}/read",
        headers=auth_headers(ana_token)
    )
    assert_status(status, 200, "mark message read")
    print(body)

    print("Sending message...")
    message_payload = {
        "receiverId": 1,
        "listingId": listing_id,
        "content": "Salut, mai este disponibila bicicleta?"
    }

    status, body = http_request(
        "POST",
        f"{BASE}/messages/send",
        message_payload,
        headers=auth_headers(ion_token)
    )
    assert_status(status, 201, "send message")
    message_id = get_id(body, "send message")
    print(body)

    print("Checking inbox...")
    status, body = http_request(
        "GET",
        f"{BASE}/messages/inbox",
        headers=auth_headers(ana_token)
    )
    assert_status(status, 200, "message inbox")
    print("Inbox returned.")

    print("Checking conversation...")
    status, body = http_request(
        "GET",
        f"{BASE}/messages/conversation/2",
        headers=auth_headers(ana_token)
    )
    assert_status(status, 200, "message conversation")
    print("Conversation returned.")

    print("Marking message as read...")
    status, body = http_request(
        "PUT",
        f"{BASE}/messages/{message_id}/read",
        headers=auth_headers(ana_token)
    )
    assert_status(status, 200, "mark message read")
    print(body)

    print("Deleting listing...")
    status, body = http_request(
        "DELETE",
        f"{BASE}/listings/{listing_id}",
        headers=auth_headers(ana_token)
    )
    assert_status(status, 204, "delete listing")
    print("Listing deleted.")


    print("Integration test passed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)