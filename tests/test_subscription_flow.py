def test_full_subscription_flow(client):
    # register user
    r = client.post("/api/register", json={"email": "user@test.com", "password": "password"})
    assert r.status_code == 201
    registered_user_id = r.get_json()["data"]["user_id"]

    # login user
    r = client.post("/api/login", json={"email": "user@test.com", "password": "password"})
    assert r.status_code == 200
    token = r.get_json()["data"]["token"]
    user_id = r.get_json()["data"]["user_id"]
    assert user_id == registered_user_id

    # login admin
    r = client.post("/api/login", json={"email": "admin@test.com", "password": "password"})
    assert r.status_code == 200
    admin_token = r.get_json()["data"]["token"]

    # subscribe to basic
    r = client.post(
        "/api/subscriptions/subscribe",
        json={"plan_id": 1, "duration_days": 30},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["status"] == "active"

    # get active
    r = client.get("/api/subscriptions/active", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    subscription = r.get_json()["data"]
    assert subscription.get("status") == "active"
    assert subscription.get("plan_id") == 1

    # upgrade to pro
    r = client.post(
        "/api/subscriptions/change-plan",
        json={"plan_id": 2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    subscription = r.get_json()["data"]
    assert subscription.get("plan", {}).get("id") == 2

    # get all active subscriptions
    r = client.get("/api/subscriptions/active/all", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    subscriptions = r.get_json()["data"]
    assert len(subscriptions) == 1
    assert subscriptions[0].get("plan_id") == 2

    # cancel
    r = client.post("/api/subscriptions/cancel", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    # ensure no active now
    r = client.get("/api/subscriptions/active", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.get_json()["data"] is None

    # subscribe to pro
    r = client.post(
        "/api/subscriptions/subscribe",
        json={"plan_id": 2, "duration_days": 30},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["status"] == "active"

    # history
    r = client.get("/api/subscriptions/history", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    history = r.get_json()["data"]
    assert len(history) == 2
    assert history[0].get("plan_id") == 2
    assert history[1].get("plan_id") == 2
