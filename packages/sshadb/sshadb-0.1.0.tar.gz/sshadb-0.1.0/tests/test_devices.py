def test_devices(client):
    devices = client.devices()
    assert isinstance(devices, list)
    for d in devices:
        assert isinstance(d, dict)
        assert "serial" in d and "state" in d
