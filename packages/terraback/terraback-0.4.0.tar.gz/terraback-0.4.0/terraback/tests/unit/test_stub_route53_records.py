import pytest
from terraback.cli.main import _ensure_resource_blocks


def test_route53_record_stub_has_records_and_ttl(tmp_path):
    resources = [
        {
            "type": "aws_route53_record",
            "name": "test",
            "id": "Z1234_test",
        }
    ]

    _ensure_resource_blocks(tmp_path, resources)

    stub_file = tmp_path / "terraback_import_stubs.tf"
    assert stub_file.exists()
    content = stub_file.read_text()
    assert 'records = ["127.0.0.1"]' in content
    assert 'ttl = 300' in content


def test_route53_record_stub_parses_name_and_type(tmp_path):
    resources = [
        {
            "type": "aws_route53_record",
            "name": "test",
            "id": "Z1234_example.com._CNAME",
        }
    ]

    _ensure_resource_blocks(tmp_path, resources)

    stub_file = tmp_path / "terraback_import_stubs.tf"
    assert stub_file.exists()
    content = stub_file.read_text()
    assert 'name = "example.com"' in content
    assert 'type = "CNAME"' in content


def test_route53_record_stub_uses_resource_data(tmp_path):
    resources = [
        {
            "type": "aws_route53_record",
            "name": "test",
            "id": "Z111_real.example.com._A",
            "resource_data": {
                "ZoneId": "Z111",
                "Name": "real.example.com.",
                "Type": "A",
                "TTL": 60,
                "ResourceRecords": [{"Value": "10.0.0.1"}],
            },
        }
    ]

    _ensure_resource_blocks(tmp_path, resources)

    stub_file = tmp_path / "terraback_import_stubs.tf"
    assert stub_file.exists()
    content = stub_file.read_text()
    assert 'zone_id = "Z111"' in content
    assert 'name = "real.example.com"' in content
    assert 'type = "A"' in content
    assert 'ttl = 60' in content
    assert 'records = ["10.0.0.1"]' in content


def test_route53_record_stub_from_id(tmp_path):
    resources = [
        {
            "type": "aws_route53_record",
            "name": "no_scan",
            "id": "Z1234_sub.example.com._AAAA",
        }
    ]

    _ensure_resource_blocks(tmp_path, resources)

    stub_file = tmp_path / "terraback_import_stubs.tf"
    content = stub_file.read_text()
    assert 'name = "sub.example.com"' in content
    assert 'type = "AAAA"' in content
