import shlex

def test_push_and_pull_roundtrip(client, test_serial, tmp_path):
    content = "hello-sshadb"
    local_file = tmp_path / "hello.txt"
    local_file.write_text(content)

    device_path = "/data/local/tmp/sshadb_test_push.txt"

    client.push(test_serial, str(local_file), device_path)

    read_back = client.shell(test_serial, f"cat {shlex.quote(device_path)}")
    assert content in read_back

    downloaded = tmp_path / "downloaded.txt"
    client.pull(test_serial, device_path, str(downloaded))

    assert downloaded.read_text().strip() == content

    client.shell(test_serial, f"rm -f {shlex.quote(device_path)}")
