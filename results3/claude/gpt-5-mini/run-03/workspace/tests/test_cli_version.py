from src.cli import main


def test_version_output(capfd):
    main(["--version"])
    captured = capfd.readouterr()
    assert "0.1.0" in captured.out
