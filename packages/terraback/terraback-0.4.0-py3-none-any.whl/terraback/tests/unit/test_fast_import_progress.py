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


def test_fast_import_auto_progress(tmp_path):
    data = [
        {"resource_type": "aws_instance", "resource_name": "one", "remote_id": "i-1"},
        {"resource_type": "aws_instance", "resource_name": "two", "remote_id": "i-2"},
    ]
    imp_file = tmp_path / "sample_import.json"
    imp_file.write_text(json.dumps(data))
    (tmp_path / ".terraform").mkdir()

    bar = DummyProgressBar()

    def fake_progressbar(length, label=""):
        assert length == len(data)
        return DummyProgress(bar)

    with (
        patch("terraback.utils.terraform_checker.TerraformChecker.get_terraform_version", return_value="v1.5.0"),
        patch("terraback.utils.import_workflows.import_with_blocks_enhanced"),
        patch("sys.stdout.isatty", return_value=True),
        patch("typer.progressbar", side_effect=fake_progressbar),
        patch("typer.echo"),
    ):
        import_all_resources(
            output_dir=tmp_path,
            terraform_dir=tmp_path,
            dry_run=False,
            yes=True,
            parallel=2,
            validate=True,
            workflow="auto",
            batch_size=2,
            progress=True,
        )

    assert bar.updates == [2]


def test_fast_import_auto_no_progress(tmp_path):
    data = [{"resource_type": "aws_instance", "resource_name": "one", "remote_id": "i-1"}]
    imp_file = tmp_path / "sample_import.json"
    imp_file.write_text(json.dumps(data))
    (tmp_path / ".terraform").mkdir()

    progress_called = False

    def fake_progressbar(*args, **kwargs):
        nonlocal progress_called
        progress_called = True
        return DummyProgress(DummyProgressBar())

    with (
        patch("terraback.utils.terraform_checker.TerraformChecker.get_terraform_version", return_value="v1.5.0"),
        patch("terraback.utils.import_workflows.import_with_blocks_enhanced"),
        patch("sys.stdout.isatty", return_value=True),
        patch("typer.progressbar", side_effect=fake_progressbar),
        patch("typer.echo"),
    ):
        import_all_resources(
            output_dir=tmp_path,
            terraform_dir=tmp_path,
            dry_run=False,
            yes=True,
            parallel=1,
            validate=True,
            workflow="auto",
            batch_size=1,
            progress=False,
        )

    assert not progress_called
