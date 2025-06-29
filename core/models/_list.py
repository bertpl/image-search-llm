import ollama


def get_model_names() -> list[str]:
    """
    :return: list of model names that match the required capabilities
    """
    return sorted([model.model for model in ollama.list().models])


def ensure_model_exists(model_name: str) -> None:
    """
    Ensure that a model with the given name exists in the Ollama environment.
    :param model_name: Name of the model to check.
    :raises ValueError: If the model does not exist.
    """
    if model_name not in get_model_names():
        raise ValueError(
            f"Model '{model_name}' not installed.  Install or specify another model using the --model option."
        )
