try:
    from cvc.policy.anthropic_pilot import AlphaCyborgPolicy, AnthropicCyborgPolicy
except ImportError:
    AlphaCyborgPolicy = None  # type: ignore[assignment,misc]
    AnthropicCyborgPolicy = None  # type: ignore[assignment,misc]

try:
    from cvc.policy.openai_pilot import OpenAICyborgPolicy
except ImportError:
    OpenAICyborgPolicy = None  # type: ignore[assignment,misc]

__all__ = ["AlphaCyborgPolicy", "AnthropicCyborgPolicy", "OpenAICyborgPolicy"]
