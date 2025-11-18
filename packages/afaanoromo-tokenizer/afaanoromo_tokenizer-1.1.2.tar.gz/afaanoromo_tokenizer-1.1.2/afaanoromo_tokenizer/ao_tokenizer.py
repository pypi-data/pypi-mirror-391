import json
from tokenizers import Tokenizer
import importlib.resources as pkg_resources
from . import af_tokenizer_files  # just the package folder, can be the same

def ao_tokenizer(model_type: str = "bpe") -> Tokenizer:
    """
    Load a pretrained Afaan Oromo tokenizer.

    Parameters
    ----------
    model_type : str, optional
        The tokenizer type. Must be one of: "bpe", "unigram", "wordpiece".
        Default is "bpe".

    Raises
    ------
    ValueError
        If `model_type` is not supported.
    FileNotFoundError
        If the tokenizer file does not exist in the package.
    """
    model_type = model_type.lower()
    tokenizer_files = {
        "bpe": "bpe_tokenizer.json",
        "unigram": "unigram_tokenizer.json",
        "wordpiece": "wordpiece_tokenizer.json",
    }

    if model_type not in tokenizer_files:
        valid = ", ".join(tokenizer_files.keys())
        raise ValueError(f"Invalid model_type '{model_type}'. Expected one of: {valid}")

    file_name = tokenizer_files[model_type]

    try:
        # Open JSON tokenizer file from package resources
        with pkg_resources.path("afaanoromo_tokenizer", file_name) as path:
            tokenizer = Tokenizer.from_file(str(path))
    except FileNotFoundError:
        raise FileNotFoundError(f"Tokenizer file '{file_name}' not found in package.")

    return tokenizer
