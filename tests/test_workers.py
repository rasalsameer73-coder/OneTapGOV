def test_send_notification_impl():
    from app.workers.notification_task import send_notification_impl

    res = send_notification_impl("test_provider", "user1", {"body": "hello"})
    assert res["status"] == "sent"
    assert res["recipient"] == "user1"
    assert res["provider"] == "test_provider"


def test_refresh_recommendations_impl():
    from app.workers.maintenance_task import refresh_recommendations_impl

    res = refresh_recommendations_impl()
    assert res["status"] in {"ok", "error"}
