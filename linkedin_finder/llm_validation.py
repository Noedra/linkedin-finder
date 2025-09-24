"""
LLM-based validation functions for LinkedIn Finder

This module provides AI-powered validation for names, companies, and other data
using the Groq API with small, fast language models.
"""

import json
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from .groq_client import create_groq_client, GroqClient

logger = logging.getLogger(__name__)


@dataclass
class NameValidationResult:
    """Result of LLM name validation"""

    is_match: bool
    confidence: float  # 0.0 to 1.0
    reasoning: str
    same_person: bool
    nickname_detected: bool
    error: Optional[str] = None


class LLMValidator:
    """
    LLM-powered validator for names and other data

    Uses fast, small models for quick and reliable validation tasks.
    """

    def __init__(
        self, api_key: Optional[str] = None, model: str = "llama-3.1-8b-instant"
    ):
        """
        Initialize LLM validator

        Args:
            api_key: Groq API key (optional, will try to load from env)
            model: Model to use for validation
        """
        self.groq_client = create_groq_client(api_key=api_key, model=model)
        self.available = (
            self.groq_client is not None and self.groq_client.is_available()
        )

        if not self.available:
            logger.warning(
                "LLM validation not available - falling back to traditional methods"
            )

    def validate_name_match(
        self, expected_name: str, found_name: str, context: Optional[str] = None
    ) -> NameValidationResult:
        """
        Validate if two names refer to the same person using LLM

        Args:
            expected_name: The name we're looking for
            found_name: The name found in search results
            context: Optional context (e.g., company, job title)

        Returns:
            NameValidationResult with detailed analysis
        """
        if not self.available:
            return self._fallback_validation(expected_name, found_name)

        try:
            # Construct the prompt for name validation
            system_message = """You are a name validation expert. Your job is to determine if two names refer to the same person.

Consider:
- Nicknames (Mike/Michael, Chris/Christopher, Liz/Elizabeth, etc.)
- Cultural name variations
- Name ordering differences
- Titles and credentials (Dr., Jr., etc.)
- Common spelling variations
- Middle names or initials

Respond with a JSON object containing:
{
    "is_match": boolean,
    "confidence": float (0.0 to 1.0),
    "reasoning": "explanation of your decision",
    "same_person": boolean,
    "nickname_detected": boolean
}

Be conservative - only return true if you're confident they're the same person."""

            context_info = f"\nContext: {context}" if context else ""

            prompt = f"""Compare these two names:
Expected: "{expected_name}"
Found: "{found_name}"{context_info}

Are these the same person? Respond with JSON only."""

            response = self.groq_client.simple_prompt(
                prompt=prompt,
                system_message=system_message,
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=200,
            )

            if not response.success:
                logger.error(f"Groq API error: {response.error}")
                return self._fallback_validation(expected_name, found_name)

            # Parse the JSON response
            try:
                result_data = json.loads(response.content.strip())

                return NameValidationResult(
                    is_match=result_data.get("is_match", False),
                    confidence=float(result_data.get("confidence", 0.0)),
                    reasoning=result_data.get("reasoning", ""),
                    same_person=result_data.get("same_person", False),
                    nickname_detected=result_data.get("nickname_detected", False),
                )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response: {response.content}")
                return self._fallback_validation(expected_name, found_name)

        except Exception as e:
            logger.error(f"LLM validation error: {e}")
            return self._fallback_validation(expected_name, found_name)

    def _fallback_validation(
        self, expected_name: str, found_name: str
    ) -> NameValidationResult:
        """
        Fallback validation using simple string similarity
        """
        from difflib import SequenceMatcher

        if not expected_name or not found_name:
            return NameValidationResult(
                is_match=False,
                confidence=0.0,
                reasoning="Empty name provided",
                same_person=False,
                nickname_detected=False,
                error="Fallback validation used",
            )

        # Simple similarity check
        similarity = SequenceMatcher(
            None, expected_name.lower(), found_name.lower()
        ).ratio()
        is_match = similarity >= 0.8  # Conservative threshold for fallback

        return NameValidationResult(
            is_match=is_match,
            confidence=similarity,
            reasoning=f"Fallback string similarity: {similarity:.2f}",
            same_person=is_match,
            nickname_detected=False,
            error="LLM not available - used fallback",
        )

    def validate_company_match(
        self, expected_company: str, found_company: str
    ) -> Dict[str, Any]:
        """
        Validate if two company names refer to the same organization

        Args:
            expected_company: The company we're looking for
            found_company: The company found in search results

        Returns:
            Dict with validation results
        """
        if not self.available:
            # Fallback to existing company validation logic
            from difflib import SequenceMatcher

            similarity = SequenceMatcher(
                None, expected_company.lower(), found_company.lower()
            ).ratio()
            return {
                "is_match": similarity >= 0.6,
                "confidence": similarity,
                "reasoning": f"Fallback similarity: {similarity:.2f}",
                "error": "LLM not available",
            }

        try:
            system_message = """You are a company name validation expert. Determine if two company names refer to the same organization.

Consider:
- Different legal forms (Inc, LLC, Corp, Ltd, etc.)
- Abbreviations and full names (IBM vs International Business Machines)
- Brand names vs legal names (Google vs Alphabet Inc)
- Common variations and subsidiaries
- International variations

Respond with JSON:
{
    "is_match": boolean,
    "confidence": float (0.0 to 1.0),
    "reasoning": "explanation"
}"""

            prompt = f"""Compare these company names:
Expected: "{expected_company}"
Found: "{found_company}"

Are these the same company? Respond with JSON only."""

            response = self.groq_client.simple_prompt(
                prompt=prompt,
                system_message=system_message,
                temperature=0.1,
                max_tokens=150,
            )

            if response.success:
                try:
                    return json.loads(response.content.strip())
                except json.JSONDecodeError:
                    pass

            # Fallback on error
            from difflib import SequenceMatcher

            similarity = SequenceMatcher(
                None, expected_company.lower(), found_company.lower()
            ).ratio()
            return {
                "is_match": similarity >= 0.6,
                "confidence": similarity,
                "reasoning": f"Fallback after LLM error: {similarity:.2f}",
                "error": "LLM validation failed",
            }

        except Exception as e:
            logger.error(f"Company validation error: {e}")
            # Fallback
            from difflib import SequenceMatcher

            similarity = SequenceMatcher(
                None, expected_company.lower(), found_company.lower()
            ).ratio()
            return {
                "is_match": similarity >= 0.6,
                "confidence": similarity,
                "reasoning": f"Exception fallback: {similarity:.2f}",
                "error": str(e),
            }


# Global validator instance (lazy initialization)
_validator_instance: Optional[LLMValidator] = None


def get_llm_validator(api_key: Optional[str] = None) -> LLMValidator:
    """
    Get or create the global LLM validator instance

    Args:
        api_key: Optional API key (only used on first call)

    Returns:
        LLMValidator instance
    """
    global _validator_instance

    if _validator_instance is None:
        _validator_instance = LLMValidator(api_key=api_key)

    return _validator_instance


def validate_name_match(
    expected_name: str,
    found_name: str,
    context: Optional[str] = None,
    api_key: Optional[str] = None,
) -> NameValidationResult:
    """
    Convenience function for name validation

    Args:
        expected_name: The name we're looking for
        found_name: The name found in search results
        context: Optional context information
        api_key: Optional API key

    Returns:
        NameValidationResult
    """
    validator = get_llm_validator(api_key=api_key)
    return validator.validate_name_match(expected_name, found_name, context)


def validate_company_match(
    expected_company: str, found_company: str, api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function for company validation

    Args:
        expected_company: The company we're looking for
        found_company: The company found in search results
        api_key: Optional API key

    Returns:
        Dict with validation results
    """
    validator = get_llm_validator(api_key=api_key)
    return validator.validate_company_match(expected_company, found_company)
