def test_shell_echo(client, test_serial):
    out = client.shell(test_serial, "echo hello")
    assert out.strip() == "hello"
