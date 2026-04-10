from proj_info import cli


def test_version(capsys):
    rc = cli.main(['--version'])
    captured = capsys.readouterr()
    assert rc == 0
    assert '0.1.0' in captured.out

