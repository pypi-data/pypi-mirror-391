import json
from unittest.mock import patch

from terraback.cli.main import import_all_resources


class DummyProgressBar:
    def __init__(self):
        self.updates = []

    def update(self, n):
        self.updates.append(n)


class DummyProgress:
    def __init__(self, bar):
        self.bar = bar

    def __enter__(self):
        return self.bar

    def __exit__(self, exc_type, exc, tb):
        pass


def _fake_result(returncode=0, stdout="", stderr=""):
    class Result:
        def __init__(self):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    return Result()


def test_workspaces_import_with_progress(tmp_path):
    data = [
        {"resource_type": "aws_instance", "resource_name": f"r{i}", "remote_id": f"i-{i}"}
        for i in range(3)
    ]
    imp_file = tmp_path / "sample_import.json"
    imp_file.write_text(json.dumps(data))
    (tmp_path / ".terraform").mkdir()

    bar = DummyProgressBar()
    calls = []

    def fake_progressbar(length, label=""):
        assert length == len(data)
        return DummyProgress(bar)

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return _fake_result()

    with (
        patch("subprocess.run", side_effect=fake_run),
        patch("sys.stdout.isatty", return_value=True),
        patch("typer.progressbar", side_effect=fake_progressbar),
        patch("typer.echo")
    ):
        import_all_resources(
            output_dir=tmp_path,
            terraform_dir=tmp_path,
            dry_run=False,
            yes=True,
            parallel=1,
            validate=True,
            workflow="workspaces",
            batch_size=2,
            progress=True,
        )

    assert ["terraform", "workspace", "new", "tb0"] in calls
    assert ["terraform", "workspace", "select", "tb0"] in calls
    assert ["terraform", "workspace", "new", "tb1"] in calls
    assert ["terraform", "workspace", "select", "tb1"] in calls
    import_calls = [c for c in calls if "import" in c]
    assert len(import_calls) == 0
    assert bar.updates == []


def test_workspaces_no_progress(tmp_path):
    data = [{"resource_type": "aws_instance", "resource_name": "only", "remote_id": "i-0"}]
    imp_file = tmp_path / "sample_import.json"
    imp_file.write_text(json.dumps(data))
    (tmp_path / ".terraform").mkdir()

    progress_called = False

    def fake_progressbar(*args, **kwargs):
        nonlocal progress_called
        progress_called = True
        return DummyProgress(DummyProgressBar())

    with (
        patch("subprocess.run", return_value=_fake_result()),
        patch("sys.stdout.isatty", return_value=True),
        patch("typer.progressbar", side_effect=fake_progressbar),
        patch("typer.echo")
    ):
        import_all_resources(
            output_dir=tmp_path,
            terraform_dir=tmp_path,
            dry_run=False,
            yes=True,
            parallel=1,
            validate=True,
            workflow="workspaces",
            batch_size=1,
            progress=False,
        )

    assert not progress_called
