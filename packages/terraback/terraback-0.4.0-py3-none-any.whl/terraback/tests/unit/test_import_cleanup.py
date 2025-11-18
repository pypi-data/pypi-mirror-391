from unittest.mock import patch

from terraback.import_workflows import (
    import_with_blocks_enhanced,
    parallel_workspace_import,
)
from terraback.utils.cleanup import clean_import_artifacts


class Result:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _fake_run(cmd, **kwargs):
    return Result()


def test_blocks_enhanced_removes_files(tmp_path):
    resources = [{"type": "aws_instance", "name": "example", "id": "i-1"}]
    (tmp_path / ".terraform").mkdir()
    (tmp_path / "import.plan").write_text("")
    (tmp_path / "import_tmp.tf").write_text("")
    (tmp_path / "terraform.tfstate").write_text("")
    (tmp_path / "terraform_import_debug.log").write_text("")

    with patch("subprocess.run", side_effect=_fake_run):
        import_with_blocks_enhanced(tmp_path, resources)

    assert not (tmp_path / "import.plan").exists()
    assert not list(tmp_path.glob("import_*.tf"))
    assert not (tmp_path / "terraform.tfstate").exists()
    assert not (tmp_path / "terraback_import_blocks.tf").exists()
    assert not (tmp_path / "terraform_import_debug.log").exists()


def test_parallel_workspace_import_cleanup(tmp_path):
    resources = [{"address": "aws_instance.example", "id": "i-1"}]
    (tmp_path / ".terraform").mkdir()
    (tmp_path / "terraform.tfstate").write_text("")
    (tmp_path / "terraform_import_debug.log").write_text("")

    with patch("subprocess.run", side_effect=_fake_run):
        parallel_workspace_import(tmp_path, resources)

    assert not (tmp_path / "terraform.tfstate").exists()
    assert not (tmp_path / "terraform_import_debug.log").exists()


def test_clean_import_artifacts_removes_debug_log(tmp_path):
    log = tmp_path / "terraform_import_debug.log"
    log.write_text("")
    clean_import_artifacts(tmp_path)
    assert not log.exists()

