import os
from unittest.mock import Mock

import boto3
import pytest
from botocore.exceptions import ClientError
from botocore.stub import Stubber

from src.agent.bedrock import ALLOWED_MODEL_IDS, BedrockClient, BedrockSettings


@pytest.fixture(autouse=True)
def clean_configuration(monkeypatch):
    for name in ("AWS_PROFILE", "AWS_REGION", "AWS_DEFAULT_REGION", "BEDROCK_MODEL_ID"):
        monkeypatch.delenv(name, raising=False)


def test_settings_read_dotenv_without_mutating_environment(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "AWS_PROFILE=hackaton\nAWS_REGION=us-east-1\n"
        "BEDROCK_MODEL_ID=us.anthropic.claude-haiku-4-5\n",
        encoding="utf-8",
    )
    settings = BedrockSettings.from_env(env_file)
    assert settings == BedrockSettings(ALLOWED_MODEL_IDS[2], "us-east-1", "hackaton")
    assert "AWS_PROFILE" not in os.environ
    assert "BEDROCK_MODEL_ID" not in os.environ
    monkeypatch.setenv("BEDROCK_MODEL_ID", ALLOWED_MODEL_IDS[1])
    assert BedrockSettings.from_env(env_file).model_id == ALLOWED_MODEL_IDS[1]
    assert BedrockSettings.from_env(tmp_path / "missing.env").profile is None


def test_empty_values_use_defaults(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("AWS_PROFILE=\nAWS_REGION=\nBEDROCK_MODEL_ID=\n", encoding="utf-8")
    assert BedrockSettings.from_env(env_file) == BedrockSettings()


def test_default_region_environment_is_supported(tmp_path, monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-west-2")
    assert BedrockSettings.from_env(tmp_path / "missing.env").region == "us-west-2"


@pytest.mark.parametrize("model_id", ["us.anthropic.claude-sonnet-5-5", "fable", "unknown"])
def test_disallowed_model_fails_before_creating_aws_client(tmp_path, monkeypatch, model_id):
    monkeypatch.setenv("BEDROCK_MODEL_ID", model_id)
    session = Mock()
    monkeypatch.setattr("src.agent.bedrock.boto3.Session", session)
    with pytest.raises(ValueError, match="no está permitido"):
        BedrockClient.from_env(tmp_path / "missing.env")
    session.assert_not_called()


def test_factory_uses_configured_profile_and_region(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("AWS_PROFILE=hackaton\nAWS_REGION=us-east-1\n", encoding="utf-8")
    session = Mock()
    monkeypatch.setattr("src.agent.bedrock.boto3.Session", session)
    client = BedrockClient.from_env(env_file)
    session.assert_called_once_with(profile_name="hackaton", region_name="us-east-1")
    session.return_value.client.assert_called_once_with("bedrock-runtime")
    assert client.runtime is session.return_value.client.return_value


def test_factory_without_profile_uses_default_credential_chain(tmp_path, monkeypatch):
    session = Mock()
    monkeypatch.setattr("src.agent.bedrock.boto3.Session", session)
    BedrockClient.from_env(tmp_path / "missing.env")
    session.assert_called_once_with(profile_name=None, region_name="us-east-1")


@pytest.fixture
def runtime():
    # Explicit dummy credentials avoid local profiles, STS and metadata access.
    return boto3.Session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        region_name="us-east-1",
    ).client("bedrock-runtime")


def test_converse_preserves_tool_use_and_configured_model(runtime):
    settings = BedrockSettings(model_id=ALLOWED_MODEL_IDS[2])
    messages = [{"role": "user", "content": [{"text": "Quiero orientación"}]}]
    tool_config = {
        "tools": [{"toolSpec": {"name": "lookup", "inputSchema": {"json": {"type": "object"}}}}]
    }
    response = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [{"toolUse": {"toolUseId": "test-tool", "name": "lookup", "input": {}}}],
            }
        },
        "stopReason": "tool_use",
        "usage": {"inputTokens": 1, "outputTokens": 1, "totalTokens": 2},
        "metrics": {"latencyMs": 1},
    }
    with Stubber(runtime) as stubber:
        stubber.add_response(
            "converse",
            response,
            {
                "modelId": settings.model_id,
                "messages": messages,
                "toolConfig": tool_config,
                "inferenceConfig": {"maxTokens": 100},
            },
        )
        assert (
            BedrockClient(settings, runtime).converse(
                messages, toolConfig=tool_config, inferenceConfig={"maxTokens": 100}
            )
            == response
        )
        stubber.assert_no_pending_responses()


def test_aws_errors_propagate_to_caller(runtime):
    with Stubber(runtime) as stubber:
        stubber.add_client_error("converse", service_error_code="ExpiredTokenException")
        with pytest.raises(ClientError) as error:
            BedrockClient(BedrockSettings(), runtime).converse(
                [{"role": "user", "content": [{"text": "Hola"}]}]
            )
        assert error.value.response["Error"]["Code"] == "ExpiredTokenException"


def test_request_cannot_override_configured_model():
    runtime = Mock()
    with pytest.raises(ValueError, match="BEDROCK_MODEL_ID"):
        BedrockClient(BedrockSettings(), runtime).converse([], modelId="fable")
    runtime.converse.assert_not_called()
