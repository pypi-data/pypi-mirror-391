import os
from tokenizers import Tokenizer

# Resolve the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ao_tokenizer(model_type: str = "bpe") -> Tokenizer:
    """
    Load a pretrained Afaan Oromo tokenizer.

    Parameters
    ----------
    model_type : str, optional
        The tokenizer type. Must be one of:
        - "bpe"
        - "unigram"
        - "wordpiece"
        Default is "bpe".

   
    Raises
    ------
    ValueError
        If `model_type` is not one of the supported types.
    FileNotFoundError
        If the tokenizer file does not exist in the base directory.
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

    tokenizer_path = os.path.join(BASE_DIR, tokenizer_files[model_type])

    if not os.path.isfile(tokenizer_path):
        raise FileNotFoundError(f"Tokenizer file not found: {tokenizer_path}")

    return Tokenizer.from_file(tokenizer_path)
