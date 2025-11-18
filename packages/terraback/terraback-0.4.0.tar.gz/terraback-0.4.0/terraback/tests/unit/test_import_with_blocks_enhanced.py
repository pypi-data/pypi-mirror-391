from pathlib import Path
from unittest.mock import patch
import json

from terraback.import_workflows import import_with_blocks_enhanced


class Result:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_blocks_enhanced_batches_and_cleanup(tmp_path):
    resources = [
        {"type": "aws_instance", "name": f"ex{i}", "id": f"i-{i}"}
        for i in range(5)
    ]
    (tmp_path / ".terraform").mkdir()
    (tmp_path / "terraform_import_debug.log").write_text("")

    calls = []

    def fake_run(cmd, cwd=None, **kwargs):
        calls.append(cmd)
        if "plan" in cmd:
            Path(cwd, "generated.tf").write_text("")
        if "apply" in cmd:
            Path(cwd, "terraform.tfstate").write_text(json.dumps({}))
        return Result()

    with patch("subprocess.run", side_effect=fake_run):
        import_with_blocks_enhanced(tmp_path, resources, batch_size=2, parallelism=3)

    plan_cmds = [c for c in calls if "plan" in c]
    apply_cmds = [c for c in calls if "apply" in c]
    assert len(plan_cmds) == 3
    assert len(apply_cmds) == 0
    assert all("-parallelism=3" in c for c in plan_cmds)

    assert not (tmp_path / "terraback_import_blocks.tf").exists()
    assert not (tmp_path / "generated.tf").exists()
    assert not (tmp_path / "import.plan").exists()
    assert not (tmp_path / "terraform.tfstate").exists()
    assert not (tmp_path / "terraform_import_debug.log").exists()


def test_blocks_enhanced_skips_missing(tmp_path):
    resources = [
        {"type": "aws_instance", "name": "missing", "id": "i-0"},
        {"type": "aws_instance", "name": "ok", "id": "i-1"},
    ]
    (tmp_path / ".terraform").mkdir()
    (tmp_path / "terraform_import_debug.log").write_text("")

    calls = []

    def fake_run(cmd, cwd=None, **kwargs):
        calls.append(cmd)
        if "plan" in cmd and not hasattr(fake_run, "failed"):
            fake_run.failed = True
            return Result(
                returncode=1,
                stderr=(
                    "Error: Cannot import non-existent remote object\n\n"
                    "While attempting to import an existing object to \"aws_instance.missing\""
                    ", the provider detected that no object exists with the given id."
                ),
            )
        if "plan" in cmd:
            Path(cwd, "generated.tf").write_text("")
        return Result()

    with patch("subprocess.run", side_effect=fake_run):
        import_with_blocks_enhanced(tmp_path, resources, batch_size=2, parallelism=3)

    plan_cmds = [c for c in calls if "plan" in c]
    assert len(plan_cmds) == 2
    assert resources == [{"type": "aws_instance", "name": "ok", "id": "i-1"}]
    assert not (tmp_path / "terraform_import_debug.log").exists()

