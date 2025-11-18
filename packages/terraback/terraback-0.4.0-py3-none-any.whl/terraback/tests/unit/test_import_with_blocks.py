from unittest.mock import patch

import pytest
import typer
from terraback.import_workflows import import_with_blocks
from terraback.utils.cleanup import clean_import_artifacts


def _fake_result(returncode=0, stdout="", stderr=""):
    class Result:
        def __init__(self):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    return Result()


def test_runs_init_when_missing(tmp_path):
    resources = [{"type": "aws_instance", "name": "example", "id": "i-1"}]
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return _fake_result()

    with patch("subprocess.run", side_effect=fake_run):
        import_with_blocks(tmp_path, resources)

    assert ["terraform", "init"] in calls
    assert ["terraform", "plan", "-generate-config-out=generated.tf"] in calls
    assert not any(cmd[0] == "terraform" and "apply" in cmd for cmd in calls)


def test_skips_init_when_present(tmp_path):
    resources = [{"type": "aws_instance", "name": "example", "id": "i-1"}]
    (tmp_path / ".terraform").mkdir()
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return _fake_result()

    with patch("subprocess.run", side_effect=fake_run):
        import_with_blocks(tmp_path, resources)

    assert ["terraform", "init"] not in calls
    assert ["terraform", "plan", "-generate-config-out=generated.tf"] in calls
    assert not any(cmd[0] == "terraform" and "apply" in cmd for cmd in calls)


def test_plan_failure_exits(tmp_path):
    resources = [{"type": "aws_instance", "name": "example", "id": "i-1"}]
    (tmp_path / ".terraform").mkdir()
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if "plan" in cmd:
            return _fake_result(returncode=1, stderr="failed plan")
        return _fake_result()

    with patch("subprocess.run", side_effect=fake_run):
        with pytest.raises(typer.Exit):
            import_with_blocks(tmp_path, resources)

    assert ["terraform", "init"] not in calls
    assert ["terraform", "plan", "-generate-config-out=generated.tf"] in calls


def test_cleanup_files(tmp_path):
    resources = [{"type": "aws_instance", "name": "example", "id": "i-1"}]
    (tmp_path / ".terraform").mkdir()

    # Pre-create files that should be removed
    (tmp_path / "import.plan").write_text("")
    (tmp_path / "terraform.tfstate").write_text("")
    (tmp_path / "import_extra.tf").write_text("")
    (tmp_path / "terraform_import_debug.log").write_text("")

    def fake_run(cmd, **kwargs):
        if "plan" in cmd:
            (tmp_path / "generated.tf").write_text("")
        if "apply" in cmd:
            (tmp_path / "terraform.tfstate").write_text("")
        return _fake_result()

    with patch("subprocess.run", side_effect=fake_run):
        import_with_blocks(tmp_path, resources)

    assert not (tmp_path / "terraback_import_blocks.tf").exists()
    assert not (tmp_path / "generated.tf").exists()
    assert not (tmp_path / "import.plan").exists()
    assert not (tmp_path / "terraform.tfstate").exists()
    assert not list(tmp_path.glob("import_*.tf"))
    assert not (tmp_path / "terraform_import_debug.log").exists()