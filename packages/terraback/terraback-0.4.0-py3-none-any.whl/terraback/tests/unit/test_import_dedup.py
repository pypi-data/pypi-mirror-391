import json
from terraback.cli.main import cmd_import_all


def test_duplicate_imports_deduplicated(tmp_path, capsys):
    data = [
        {"resource_type": "aws_instance", "resource_name": "demo", "remote_id": "i-1"},
        {"resource_type": "aws_instance", "resource_name": "demo", "remote_id": "i-1"},
    ]
    imp_file = tmp_path / "sample_import.json"
    imp_file.write_text(json.dumps(data))
    (tmp_path / ".terraform").mkdir()

    cmd_import_all(
        output_dir=tmp_path,
        terraform_dir=tmp_path,
        dry_run=True,
        yes=True,
        parallel=1,
        validate=True,
        create_stubs=False,
        progress=False,
        async_mode=False,
        verify=False,
        workflow="import",
        batch_size=1,
    )

    output = capsys.readouterr().out
    assert output.count("terraform import") == 1

