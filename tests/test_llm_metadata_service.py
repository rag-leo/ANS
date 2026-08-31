import json
from unittest.mock import MagicMock, patch

from openai import RateLimitError

from backend.services.llm_metadata_service import LLMMetadataService


def _fake_completion(content: str):

    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=content))]
    return response


def _build_service() -> LLMMetadataService:

    with patch(
        "backend.services.llm_metadata_service.AzureOpenAI"
    ):
        return LLMMetadataService()


def test_extract_metadata_parses_valid_response():

    service = _build_service()

    service.client.chat.completions.create = MagicMock(
        return_value=_fake_completion(
            json.dumps({"category": "Market Intelligence", "crop": ["Wheat"]})
        )
    )

    result = service.extract_metadata("Wheat prices rise", "excerpt text")

    assert result == {
        "category": "Market Intelligence",
        "crop": ["Wheat"],
        "keywords": ["Wheat"],
    }


def test_extract_metadata_calls_the_classification_deployment_not_chat():

    service = _build_service()
    service.deployment_name = "my-mini-deployment"

    mock_create = MagicMock(
        return_value=_fake_completion(
            json.dumps({"category": "General", "crop": []})
        )
    )
    service.client.chat.completions.create = mock_create

    service.extract_metadata("Title", "Excerpt")

    assert mock_create.call_args.kwargs["model"] == "my-mini-deployment"


def test_extract_metadata_falls_back_to_general_for_unknown_category():

    service = _build_service()

    service.client.chat.completions.create = MagicMock(
        return_value=_fake_completion(
            json.dumps({"category": "Sports", "crop": ["Wheat"]})
        )
    )

    result = service.extract_metadata("Title", "Excerpt")

    assert result["category"] == "General"


def test_extract_metadata_drops_crops_outside_the_taxonomy():

    service = _build_service()

    service.client.chat.completions.create = MagicMock(
        return_value=_fake_completion(
            json.dumps(
                {
                    "category": "Crop Advisory",
                    "crop": ["Wheat", "Dragonfruit", "cotton"],
                }
            )
        )
    )

    result = service.extract_metadata("Title", "Excerpt")

    # "Dragonfruit" isn't in the taxonomy and is dropped; "cotton"
    # (lowercase from the model) is normalized to the canonical form.
    assert result["crop"] == ["Wheat", "Cotton"]


def test_extract_metadata_falls_back_to_general_on_malformed_json():

    service = _build_service()

    service.client.chat.completions.create = MagicMock(
        return_value=_fake_completion("not valid json")
    )

    result = service.extract_metadata("Title", "Excerpt")

    assert result == {"category": "General", "crop": [], "keywords": []}


def test_extract_metadata_falls_back_to_general_when_api_call_fails():

    service = _build_service()

    service.client.chat.completions.create = MagicMock(
        side_effect=RuntimeError("network error")
    )

    result = service.extract_metadata("Title", "Excerpt")

    assert result == {"category": "General", "crop": [], "keywords": []}


def test_complete_retries_on_rate_limit_then_succeeds():

    service = _build_service()

    rate_limit_error = RateLimitError(
        "rate limited",
        response=MagicMock(status_code=429),
        body=None,
    )

    mock_create = MagicMock(
        side_effect=[
            rate_limit_error,
            _fake_completion(json.dumps({"category": "General", "crop": []})),
        ]
    )
    service.client.chat.completions.create = mock_create

    result = service.extract_metadata("Title", "Excerpt")

    assert mock_create.call_count == 2
    assert result["category"] == "General"
