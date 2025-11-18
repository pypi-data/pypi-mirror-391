import json
from unittest.mock import patch

import pytest
import typer

from terraback.cli.main import cmd_import_all


def _write_import_file(tmp_path, data):
    imp_file = tmp_path / "sample_import.json"
    imp_file.write_text(json.dumps(data))
    (tmp_path / ".terraform").mkdir()


def test_parallel_workspaces_success(tmp_path, capsys):
    data = [{"resource_type": "aws_instance", "resource_name": "ex", "remote_id": "i-1"}]
    _write_import_file(tmp_path, data)

    with (
        patch("terraback.cli.main._check_terraform_installation", return_value=True),
        patch("terraback.cli.main.parallel_workspace_import", return_value=[]),
    ):
        cmd_import_all(
            output_dir=tmp_path,
            terraform_dir=tmp_path,
            dry_run=False,
            yes=True,
            parallel=2,
            validate=True,
            workflow="parallel-workspaces",
            batch_size=1,
            progress=False,
        )

    captured = capsys.readouterr()
    assert "All resources imported successfully" in captured.out


def test_parallel_workspaces_reports_errors(tmp_path, capsys):
    data = [{"resource_type": "aws_instance", "resource_name": "ex", "remote_id": "i-1"}]
    _write_import_file(tmp_path, data)

    errors = [{"imp": {"address": "aws_instance.ex"}, "stderr": "boom"}]
    with (
        patch("terraback.cli.main._check_terraform_installation", return_value=True),
        patch("terraback.cli.main.parallel_workspace_import", return_value=errors),
    ):
        with pytest.raises(typer.Exit):
            cmd_import_all(
                output_dir=tmp_path,
                terraform_dir=tmp_path,
                dry_run=False,
                yes=True,
                parallel=2,
                validate=True,
                workflow="parallel-workspaces",
                batch_size=1,
                progress=False,
            )

    captured = capsys.readouterr()
    assert "Some resources failed to import" in captured.out
    assert "aws_instance.ex" in captured.out
    assert "boom" in captured.out
