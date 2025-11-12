def test_get_state(client, test_serial):
    state = client.get_state(test_serial)
    assert state in {"device", "offline", "unknown"}
