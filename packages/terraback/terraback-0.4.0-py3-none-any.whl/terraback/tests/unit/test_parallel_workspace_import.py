import json
from pathlib import Path
from unittest.mock import patch

from terraback.import_workflows import parallel_workspace_import


class Result:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_parallel_workspace_import_merges_and_cleans(tmp_path):
    resources = [
        {"address": "aws_instance.one", "id": "i-1"},
        {"address": "aws_instance.two", "id": "i-2"},
    ]
    (tmp_path / ".terraform").mkdir()

    states = [
        {"resources": [{"name": "one"}]},
        {"resources": [{"name": "two"}]},
    ]

    def fake_run(cmd, cwd=None, **kwargs):
        if "import" in cmd:
            idx = 0 if "one" in cmd[-2] else 1
            state_dir = Path(cwd, "terraform.tfstate.d", Path(cwd).name)
            state_dir.mkdir(parents=True, exist_ok=True)
            (state_dir / "terraform.tfstate").write_text(json.dumps(states[idx]))
        return Result()

    captured_state = {}
    from terraback.utils.cleanup import clean_import_artifacts as real_clean

    def fake_cleanup(directory):
        state = directory / "terraform.tfstate"
        if state.exists():
            captured_state["data"] = json.loads(state.read_text())
        real_clean(directory)

    created = []

    class DummyFuture:
        def __init__(self, result):
            self._result = result

        def result(self):
            return self._result

    class DummyExecutor:
        def __init__(self, max_workers):
            created.append(max_workers)
            self.tasks = []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def submit(self, func, *args, **kwargs):
            res = func(*args, **kwargs)
            fut = DummyFuture(res)
            self.tasks.append(fut)
            return fut

    def dummy_as_completed(fs):
        for f in fs:
            yield f

    with patch("subprocess.run", side_effect=fake_run), \
         patch("concurrent.futures.ThreadPoolExecutor", DummyExecutor), \
         patch("concurrent.futures.as_completed", dummy_as_completed), \
         patch("terraback.utils.import_workflows.clean_import_artifacts", side_effect=fake_cleanup):
        errors = parallel_workspace_import(tmp_path, resources, parallel=2)

    assert created[-1] == 2
    assert errors == []
    assert captured_state["data"]["resources"] == [{"name": "one"}, {"name": "two"}]
    assert not (tmp_path / "workspace_0").exists()
    assert not (tmp_path / "workspace_1").exists()


def test_parallel_workspace_import_init_failure(tmp_path):
    resources = [{"address": "aws_instance.one", "id": "i-1"}]
    (tmp_path / ".terraform").mkdir()

    def fake_run(cmd, cwd=None, **kwargs):
        if "init" in cmd:
            return Result(returncode=1, stderr="bad init")
        return Result()

    class DummyFuture:
        def __init__(self, result):
            self._result = result

        def result(self):
            return self._result

    class DummyExecutor:
        def __init__(self, max_workers):
            self.tasks = []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def submit(self, func, *args, **kwargs):
            res = func(*args, **kwargs)
            fut = DummyFuture(res)
            self.tasks.append(fut)
            return fut

    def dummy_as_completed(fs):
        for f in fs:
            yield f

    with patch("subprocess.run", side_effect=fake_run), \
         patch("concurrent.futures.ThreadPoolExecutor", DummyExecutor), \
         patch("concurrent.futures.as_completed", dummy_as_completed):
        errors = parallel_workspace_import(tmp_path, resources)

    assert errors == [
        {
            "imp": resources[0],
            "step": "init",
            "stdout": "",
            "stderr": "bad init",
            "returncode": 1,
        }
    ]


def test_parallel_workspace_import_import_failure(tmp_path):
    resources = [{"address": "aws_instance.one", "id": "i-1"}]
    (tmp_path / ".terraform").mkdir()

    def fake_run(cmd, cwd=None, **kwargs):
        if "init" in cmd:
            return Result()
        if "import" in cmd:
            return Result(returncode=1, stderr="bad import")
        return Result()

    class DummyFuture:
        def __init__(self, result):
            self._result = result

        def result(self):
            return self._result

    class DummyExecutor:
        def __init__(self, max_workers):
            self.tasks = []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def submit(self, func, *args, **kwargs):
            res = func(*args, **kwargs)
            fut = DummyFuture(res)
            self.tasks.append(fut)
            return fut

    def dummy_as_completed(fs):
        for f in fs:
            yield f

    with patch("subprocess.run", side_effect=fake_run), \
         patch("concurrent.futures.ThreadPoolExecutor", DummyExecutor), \
         patch("concurrent.futures.as_completed", dummy_as_completed):
        errors = parallel_workspace_import(tmp_path, resources)

    assert errors == [
        {
            "imp": resources[0],
            "step": "import",
            "stdout": "",
            "stderr": "bad import",
            "returncode": 1,
        }
    ]

