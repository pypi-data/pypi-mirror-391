"""Variant class for model name wrapping."""


class Variant:
    """Wrapper class for model names.

    Used to pass model identifiers to client methods, matching Goodfire's API pattern.

    Example:
        variant = Variant("meta-llama/Meta-Llama-3.3-70B-Instruct")
        client.features.search("query", model=variant)
    """

    def __init__(self, model_name: str):
        """Initialize a Variant with a model name.

        Args:
            model_name: The model identifier string (e.g., "meta-llama/Meta-Llama-3.3-70B-Instruct")
        """
        self.model_name = model_name

    def __str__(self) -> str:
        """Return the model name as a string."""
        return self.model_name

    def __repr__(self) -> str:
        """Return a string representation of the Variant."""
        return f"Variant({self.model_name!r})"

    def __eq__(self, other) -> bool:
        """Check equality with another Variant or string."""
        if isinstance(other, Variant):
            return self.model_name == other.model_name
        if isinstance(other, str):
            return self.model_name == other
        return False
