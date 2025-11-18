import pytest
from terraback.cli.main import _ensure_resource_blocks


def test_acm_certificate_stub_uses_resource_data(tmp_path):
    resources = [
        {
            "type": "aws_acm_certificate",
            "name": "cert",
            "id": "arn:aws:acm:us-east-1:123456789012:certificate/abc",
            "resource_data": {"DomainName": "real.example.com"},
        }
    ]

    _ensure_resource_blocks(tmp_path, resources)

    content = (tmp_path / "terraback_import_stubs.tf").read_text()
    assert 'domain_name = "real.example.com"' in content


def test_instance_stub_uses_resource_data(tmp_path):
    resources = [
        {
            "type": "aws_instance",
            "name": "example",
            "id": "i-123",
            "resource_data": {"ImageId": "ami-real", "InstanceType": "m5.large"},
        }
    ]

    _ensure_resource_blocks(tmp_path, resources)

    content = (tmp_path / "terraback_import_stubs.tf").read_text()
    assert 'ami = "ami-real"' in content
    assert 'instance_type = "m5.large"' in content


def test_route_table_stub_uses_resource_data(tmp_path):
    resources = [
        {
            "type": "aws_route_table",
            "name": "rtb",
            "id": "rtb-123",
            "resource_data": {"VpcId": "vpc-555"},
        }
    ]

    _ensure_resource_blocks(tmp_path, resources)

    content = (tmp_path / "terraback_import_stubs.tf").read_text()
    assert 'vpc_id = "vpc-555"' in content


def test_vpc_stub_uses_resource_data(tmp_path):
    resources = [
        {
            "type": "aws_vpc",
            "name": "main",
            "id": "vpc-111",
            "resource_data": {"CidrBlock": "10.1.0.0/16"},
        }
    ]

    _ensure_resource_blocks(tmp_path, resources)

    content = (tmp_path / "terraback_import_stubs.tf").read_text()
    assert 'cidr_block = "10.1.0.0/16"' in content


def test_subnet_stub_uses_resource_data(tmp_path):
    resources = [
        {
            "type": "aws_subnet",
            "name": "subnet",
            "id": "subnet-123",
            "resource_data": {"VpcId": "vpc-111", "CidrBlock": "10.1.1.0/24"},
        }
    ]

    _ensure_resource_blocks(tmp_path, resources)

    content = (tmp_path / "terraback_import_stubs.tf").read_text()
    assert 'vpc_id = "vpc-111"' in content
    assert 'cidr_block = "10.1.1.0/24"' in content


def test_sns_subscription_stub_uses_resource_data(tmp_path):
    resources = [
        {
            "type": "aws_sns_topic_subscription",
            "name": "sub",
            "id": "arn:aws:sns:us-east-1:123:sub",
            "resource_data": {
                "TopicArn": "arn:aws:sns:us-east-1:123:topic",
                "Protocol": "lambda",
                "Endpoint": "arn:aws:lambda:us-east-1:123:function:handler",
            },
        }
    ]

    _ensure_resource_blocks(tmp_path, resources)

    content = (tmp_path / "terraback_import_stubs.tf").read_text()
    assert 'topic_arn = "arn:aws:sns:us-east-1:123:topic"' in content
    assert 'protocol = "lambda"' in content
    assert 'endpoint = "arn:aws:lambda:us-east-1:123:function:handler"' in content
