import pytest
from terraback.cli.main import _ensure_resource_blocks


def test_sns_subscription_stub_from_id(tmp_path):
    subscription_arn = "arn:aws:sns:us-east-1:123456789012:mytopic:abcd1234"
    resources = [
        {
            "type": "aws_sns_topic_subscription",
            "name": "from_id",
            "id": subscription_arn,
        }
    ]

    _ensure_resource_blocks(tmp_path, resources)

    stub_file = tmp_path / "terraback_import_stubs.tf"
    content = stub_file.read_text()
    assert 'topic_arn = "arn:aws:sns:us-east-1:123456789012:mytopic"' in content
