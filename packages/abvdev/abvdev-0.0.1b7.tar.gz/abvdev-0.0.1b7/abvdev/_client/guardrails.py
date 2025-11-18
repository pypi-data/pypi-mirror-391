"""ABV Guardrails client for content validation with automatic tracing.

This module provides guardrail validation capabilities with automatic
tracing integration. All guardrail validations are automatically traced
as guardrail observations in ABV.

IMPORTANT: Types in this file must exactly match:
- abv-js-sdk/packages/client/src/guardrails/types.ts
- abv/web/src/features/guardrails/shared-types.ts
If you change types here, update those files as well, and vice versa.
"""

import time
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, TypedDict, Union

import httpx

from abvdev.logger import abv_logger

if TYPE_CHECKING:
    from abvdev._client.client import ABV
    from abvdev._client.span import ABVGuardrail


# ============================================================================
# Core Enums
# ============================================================================


class GuardrailType(str, Enum):
    """Types of guardrail validators available."""

    TOXIC_LANGUAGE = "toxic-language"
    CONTAINS_STRING = "contains-string"
    VALID_JSON = "valid-json"
    BIASED_LANGUAGE = "biased-language"


# Type aliases for validation results
ValidationStatus = Literal["pass", "fail", "unsure"]
SensitivityLevel = Literal["low", "medium", "high"]
ContainsStringMatchMode = Literal["any", "all", "none"]
BiasedLanguageCategory = Literal[
    "gender",
    "race",
    "religion",
    "age",
    "nationality",
    "political",
    "disability",
    "socioeconomic",
]


# ============================================================================
# Configuration Types
# ============================================================================


class BaseLLMGuardrailConfig(TypedDict, total=False):
    """Base configuration for LLM-based guardrail validators.

    Note: Uses camelCase keys to match the backend API contract.
    """

    sensitivity: Optional[SensitivityLevel]
    model: Optional[str]
    temperature: Optional[float]
    maxTokens: Optional[int]


class ValidJsonConfig(TypedDict, total=False):
    """Configuration for JSON validation guardrail.

    Note: Uses camelCase keys to match the backend API contract.
    """

    allowEmpty: Optional[bool]
    strictMode: Optional[bool]
    schema: Optional[Dict[str, Any]]


class ContainsStringConfig(TypedDict, total=False):
    """Configuration for string matching guardrail.

    Note: Uses camelCase keys to match the backend API contract.
    """

    strings: List[str]
    mode: ContainsStringMatchMode
    caseSensitive: Optional[bool]


class ToxicLanguageConfig(BaseLLMGuardrailConfig, total=False):
    """Configuration for toxic language detection guardrail."""

    pass


class BiasedLanguageConfig(BaseLLMGuardrailConfig, total=False):
    """Configuration for biased language detection guardrail."""

    categories: Optional[List[BiasedLanguageCategory]]


# Union type for all configs
GuardrailConfig = Union[
    ValidJsonConfig, ContainsStringConfig, ToxicLanguageConfig, BiasedLanguageConfig
]


# ============================================================================
# Request/Response Types
# ============================================================================


class GuardrailValidationRequest(TypedDict, total=False):
    """Internal request structure sent to ABV API."""

    text: str
    validatorType: str
    config: Optional[GuardrailConfig]


class LLMDetails(TypedDict, total=False):
    """LLM usage details from validation response."""

    model: str
    provider: str
    promptTokens: Optional[int]
    completionTokens: Optional[int]
    totalTokens: Optional[int]
    finishReason: Optional[str]


class GuardrailValidationResponse(TypedDict, total=False):
    """Internal response structure received from ABV API."""

    status: ValidationStatus
    reason: str
    confidence: float
    sensitivity: Optional[SensitivityLevel]
    llmDetails: Optional[LLMDetails]


class ValidationResult(TypedDict, total=False):
    """Public validation result returned to users."""

    status: ValidationStatus
    reason: str
    confidence: float
    sensitivity: Optional[SensitivityLevel]


# ============================================================================
# Guardrails Client
# ============================================================================


class GuardrailsClient:
    """Client for ABV Guardrails with automatic tracing.

    This client provides validation capabilities with automatic tracing
    integration. All requests are automatically traced as guardrail
    observations in ABV.

    Example:
        ```python
        from abvdev import ABV

        # Guardrails is automatically available when you provide an API key
        abv = ABV(
            api_key="sk-abv-...",
            region="us"  # Optional, defaults to "us"
        )

        # Synchronous usage
        result = abv.guardrails.validators.toxic_language.validate(
            "user input text",
            {"sensitivity": "medium"}
        )

        # Async usage
        result = await abv.guardrails.validators.toxic_language.validate_async(
            "user input text",
            {"sensitivity": "high"}
        )

        # Handle result
        if result["status"] == "pass":
            # Safe to proceed
            pass
        else:
            # Block or moderate
            print(f"Blocked: {result['reason']}")
        ```
    """

    def __init__(
        self,
        api_key: str,
        region: str = "us",
        base_url: Optional[str] = None,
        abv_client: Optional["ABV"] = None,
    ):
        """Initialize the guardrails client.

        Args:
            api_key: ABV API key for authentication
            region: API region ("us" or "eu")
            base_url: Optional base URL override for the API
            abv_client: Reference to parent ABV client for tracing
        """
        # Determine base URL: explicit base_url overrides region
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = (
                "https://eu.app.abv.dev" if region == "eu" else "https://app.abv.dev"
            )

        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "abv-python-sdk",
        }
        self._abv_client = abv_client
        self.validators = Validators(self)

        abv_logger.debug(
            f"Initialized GuardrailsClient with region={region}, "
            f"base_url={self.base_url}"
        )

    def _validate(
        self,
        text: str,
        validator_type: GuardrailType,
        config: Optional[GuardrailConfig] = None,
    ) -> ValidationResult:
        """Validate text using a guardrail validator (synchronous).

        Args:
            text: The text to validate
            validator_type: The type of validator to use
            config: Optional validator-specific configuration

        Returns:
            Validation result with status, reason, and confidence
        """
        # Create guardrail observation for tracing
        guardrail = None
        if self._abv_client:
            guardrail = self._abv_client.start_observation(
                name=f"guardrail-{validator_type.value}",
                as_type="guardrail",
                input={"text": text},
            )

        start_time = time.time()

        try:
            # Build request (config already uses camelCase keys)
            request: GuardrailValidationRequest = {
                "text": text,
                "validatorType": validator_type.value,
            }
            if config is not None:
                request["config"] = config

            # Call API
            response = self._call_api(request)

            duration = int((time.time() - start_time) * 1000)  # Convert to ms

            # Update observation with full details
            if guardrail:
                update_payload: Dict[str, Any] = {
                    "validator_config": {
                        "validatorType": validator_type.value,
                        "config": config,
                    },
                    "validation_result": {
                        "status": response["status"],
                        "reason": response["reason"],
                        "confidence": response["confidence"],
                        "duration": duration,
                    },
                    "output": {
                        "status": response["status"],
                        "reason": response["reason"],
                        "confidence": response["confidence"],
                        "validatorType": validator_type.value,
                        **(config if config else {}),
                    },
                }

                # Add sensitivity if present
                if response.get("sensitivity"):
                    update_payload["output"]["sensitivity"] = response["sensitivity"]

                # Add LLM details if present
                if response.get("llmDetails"):
                    llm_details = response["llmDetails"]
                    update_payload["model"] = llm_details["model"]
                    update_payload["usage_details"] = {
                        "prompt_tokens": llm_details.get("promptTokens", 0),
                        "completion_tokens": llm_details.get("completionTokens", 0),
                        "total_tokens": llm_details.get("totalTokens", 0),
                    }

                guardrail.update(**update_payload)

            abv_logger.debug(
                f"Completed guardrail validation: type={validator_type.value}, "
                f"status={response['status']}, duration={duration}ms"
            )

            # Return simplified result
            result: ValidationResult = {
                "status": response["status"],
                "reason": response["reason"],
                "confidence": response["confidence"],
            }
            if response.get("sensitivity"):
                result["sensitivity"] = response["sensitivity"]

            return result

        except Exception as e:
            # Update observation with error
            if guardrail:
                guardrail.update(level="ERROR", status_message=str(e))

            abv_logger.error(f"Guardrail validation failed: {e}")
            raise

        finally:
            # Always end observation
            if guardrail:
                guardrail.end()

    async def _validate_async(
        self,
        text: str,
        validator_type: GuardrailType,
        config: Optional[GuardrailConfig] = None,
    ) -> ValidationResult:
        """Validate text using a guardrail validator (asynchronous).

        Args:
            text: The text to validate
            validator_type: The type of validator to use
            config: Optional validator-specific configuration

        Returns:
            Validation result with status, reason, and confidence
        """
        # Create guardrail observation for tracing
        guardrail = None
        if self._abv_client:
            guardrail = self._abv_client.start_observation(
                name=f"guardrail-{validator_type.value}",
                as_type="guardrail",
                input={"text": text},
            )

        start_time = time.time()

        try:
            # Build request (config already uses camelCase keys)
            request: GuardrailValidationRequest = {
                "text": text,
                "validatorType": validator_type.value,
            }
            if config is not None:
                request["config"] = config

            # Call API
            response = await self._call_api_async(request)

            duration = int((time.time() - start_time) * 1000)  # Convert to ms

            # Update observation with full details
            if guardrail:
                update_payload: Dict[str, Any] = {
                    "validator_config": {
                        "validatorType": validator_type.value,
                        "config": config,
                    },
                    "validation_result": {
                        "status": response["status"],
                        "reason": response["reason"],
                        "confidence": response["confidence"],
                        "duration": duration,
                    },
                    "output": {
                        "status": response["status"],
                        "reason": response["reason"],
                        "confidence": response["confidence"],
                        "validatorType": validator_type.value,
                        **(config if config else {}),
                    },
                }

                # Add sensitivity if present
                if response.get("sensitivity"):
                    update_payload["output"]["sensitivity"] = response["sensitivity"]

                # Add LLM details if present
                if response.get("llmDetails"):
                    llm_details = response["llmDetails"]
                    update_payload["model"] = llm_details["model"]
                    update_payload["usage_details"] = {
                        "prompt_tokens": llm_details.get("promptTokens", 0),
                        "completion_tokens": llm_details.get("completionTokens", 0),
                        "total_tokens": llm_details.get("totalTokens", 0),
                    }

                guardrail.update(**update_payload)

            abv_logger.debug(
                f"Completed async guardrail validation: "
                f"type={validator_type.value}, status={response['status']}, "
                f"duration={duration}ms"
            )

            # Return simplified result
            result: ValidationResult = {
                "status": response["status"],
                "reason": response["reason"],
                "confidence": response["confidence"],
            }
            if response.get("sensitivity"):
                result["sensitivity"] = response["sensitivity"]

            return result

        except Exception as e:
            # Update observation with error
            if guardrail:
                guardrail.update(level="ERROR", status_message=str(e))

            abv_logger.error(f"Async guardrail validation failed: {e}")
            raise

        finally:
            # Always end observation
            if guardrail:
                guardrail.end()

    def _call_api(
        self, request: GuardrailValidationRequest
    ) -> GuardrailValidationResponse:
        """Call the ABV guardrails validation API (synchronous).

        Args:
            request: The validation request

        Returns:
            Validation response from API

        Raises:
            Exception: If API call fails or returns error
        """
        url = f"{self.base_url}/api/public/guardrails/validate"

        with httpx.Client() as client:
            response = client.post(
                url, headers=self.headers, json=request, timeout=60.0
            )

            if not response.is_success:
                error_msg = f"Guardrails API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = (
                        error_data.get("message")
                        or error_data.get("error")
                        or error_msg
                    )
                except:
                    error_msg = (
                        f"Guardrails API error: {response.status_code} "
                        f"{response.text}"
                    )
                raise Exception(error_msg)

            data = response.json()

            # Validate response structure
            if not isinstance(data, dict):
                raise Exception("Invalid response format from ABV Guardrails API")

            if (
                "status" not in data
                or "reason" not in data
                or "confidence" not in data
            ):
                raise Exception(
                    "Missing required fields in ABV Guardrails API response"
                )

            return GuardrailValidationResponse(
                status=data["status"],
                reason=data["reason"],
                confidence=data["confidence"],
                sensitivity=data.get("sensitivity"),
                llmDetails=data.get("llmDetails"),
            )

    async def _call_api_async(
        self, request: GuardrailValidationRequest
    ) -> GuardrailValidationResponse:
        """Call the ABV guardrails validation API (asynchronous).

        Args:
            request: The validation request

        Returns:
            Validation response from API

        Raises:
            Exception: If API call fails or returns error
        """
        url = f"{self.base_url}/api/public/guardrails/validate"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, headers=self.headers, json=request, timeout=60.0
            )

            if not response.is_success:
                error_msg = f"Guardrails API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = (
                        error_data.get("message")
                        or error_data.get("error")
                        or error_msg
                    )
                except:
                    error_msg = (
                        f"Guardrails API error: {response.status_code} "
                        f"{response.text}"
                    )
                raise Exception(error_msg)

            data = response.json()

            # Validate response structure
            if not isinstance(data, dict):
                raise Exception("Invalid response format from ABV Guardrails API")

            if (
                "status" not in data
                or "reason" not in data
                or "confidence" not in data
            ):
                raise Exception(
                    "Missing required fields in ABV Guardrails API response"
                )

            return GuardrailValidationResponse(
                status=data["status"],
                reason=data["reason"],
                confidence=data["confidence"],
                sensitivity=data.get("sensitivity"),
                llmDetails=data.get("llmDetails"),
            )


# ============================================================================
# Validator Interfaces
# ============================================================================


class Validators:
    """Container for type-safe validator interfaces."""

    def __init__(self, client: GuardrailsClient):
        """Initialize validators with reference to client.

        Args:
            client: Parent guardrails client
        """
        self.toxic_language = ToxicLanguageValidator(client)
        self.biased_language = BiasedLanguageValidator(client)
        self.contains_string = ContainsStringValidator(client)
        self.valid_json = ValidJsonValidator(client)


class ToxicLanguageValidator:
    """Validator for toxic language detection using LLM."""

    def __init__(self, client: GuardrailsClient):
        """Initialize validator.

        Args:
            client: Parent guardrails client
        """
        self._client = client

    def validate(
        self, text: str, config: Optional[ToxicLanguageConfig] = None
    ) -> ValidationResult:
        """Validate text for toxic language (synchronous).

        Args:
            text: The text to validate
            config: Optional configuration for sensitivity, model, etc.

        Returns:
            Validation result with status, reason, and confidence

        Example:
            ```python
            result = abv.guardrails.validators.toxic_language.validate(
                "This service is terrible!",
                {"sensitivity": "medium"}
            )
            if result["status"] == "fail":
                print(f"Toxic content detected: {result['reason']}")
            ```
        """
        return self._client._validate(text, GuardrailType.TOXIC_LANGUAGE, config)

    async def validate_async(
        self, text: str, config: Optional[ToxicLanguageConfig] = None
    ) -> ValidationResult:
        """Validate text for toxic language (asynchronous).

        Args:
            text: The text to validate
            config: Optional configuration for sensitivity, model, etc.

        Returns:
            Validation result with status, reason, and confidence
        """
        return await self._client._validate_async(
            text, GuardrailType.TOXIC_LANGUAGE, config
        )


class BiasedLanguageValidator:
    """Validator for biased language detection using LLM."""

    def __init__(self, client: GuardrailsClient):
        """Initialize validator.

        Args:
            client: Parent guardrails client
        """
        self._client = client

    def validate(
        self, text: str, config: Optional[BiasedLanguageConfig] = None
    ) -> ValidationResult:
        """Validate text for biased language (synchronous).

        Args:
            text: The text to validate
            config: Optional configuration for categories, sensitivity, etc.

        Returns:
            Validation result with status, reason, and confidence

        Example:
            ```python
            result = abv.guardrails.validators.biased_language.validate(
                "Seeking young developers",
                {"sensitivity": "high", "categories": ["age"]}
            )
            ```
        """
        return self._client._validate(text, GuardrailType.BIASED_LANGUAGE, config)

    async def validate_async(
        self, text: str, config: Optional[BiasedLanguageConfig] = None
    ) -> ValidationResult:
        """Validate text for biased language (asynchronous).

        Args:
            text: The text to validate
            config: Optional configuration for categories, sensitivity, etc.

        Returns:
            Validation result with status, reason, and confidence
        """
        return await self._client._validate_async(
            text, GuardrailType.BIASED_LANGUAGE, config
        )


class ContainsStringValidator:
    """Validator for string matching (deterministic)."""

    def __init__(self, client: GuardrailsClient):
        """Initialize validator.

        Args:
            client: Parent guardrails client
        """
        self._client = client

    def validate(self, text: str, config: ContainsStringConfig) -> ValidationResult:
        """Validate that text contains/doesn't contain specific strings (synchronous).

        Args:
            text: The text to validate
            config: Configuration with strings, mode, and case_sensitive

        Returns:
            Validation result with status, reason, and confidence

        Example:
            ```python
            # Block if prohibited words found
            result = abv.guardrails.validators.contains_string.validate(
                "This will cure all problems!",
                {
                    "strings": ["cure", "guarantee", "miracle"],
                    "mode": "none",
                    "case_sensitive": False
                }
            )
            ```
        """
        return self._client._validate(text, GuardrailType.CONTAINS_STRING, config)

    async def validate_async(
        self, text: str, config: ContainsStringConfig
    ) -> ValidationResult:
        """Validate that text contains/doesn't contain specific strings (asynchronous).

        Args:
            text: The text to validate
            config: Configuration with strings, mode, and case_sensitive

        Returns:
            Validation result with status, reason, and confidence
        """
        return await self._client._validate_async(
            text, GuardrailType.CONTAINS_STRING, config
        )


class ValidJsonValidator:
    """Validator for JSON structure validation (deterministic)."""

    def __init__(self, client: GuardrailsClient):
        """Initialize validator.

        Args:
            client: Parent guardrails client
        """
        self._client = client

    def validate(
        self, text: str, config: Optional[ValidJsonConfig] = None
    ) -> ValidationResult:
        """Validate that text is valid JSON (synchronous).

        Args:
            text: The text to validate
            config: Optional configuration for schema, strict_mode, etc.

        Returns:
            Validation result with status, reason, and confidence

        Example:
            ```python
            result = abv.guardrails.validators.valid_json.validate(
                '{"name": "John", "age": 30}',
                {"strict_mode": True}
            )
            ```
        """
        return self._client._validate(text, GuardrailType.VALID_JSON, config)

    async def validate_async(
        self, text: str, config: Optional[ValidJsonConfig] = None
    ) -> ValidationResult:
        """Validate that text is valid JSON (asynchronous).

        Args:
            text: The text to validate
            config: Optional configuration for schema, strict_mode, etc.

        Returns:
            Validation result with status, reason, and confidence
        """
        return await self._client._validate_async(
            text, GuardrailType.VALID_JSON, config
        )
