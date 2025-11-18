# Afaan Oromo Tokenizer

A Python library providing **tokenizers for the Afaan Oromo language** using three popular subword algorithms: **BPE**, **Unigram**, and **WordPiece**. Ideal for NLP tasks.

---

## Features
- Included: **BPE**, **Unigram**, **WordPiece**  
- Trained on **13 million tokens**  
- Supports **425 unique tokens**  
- Vocabulary size for each tokenizer type: **55,000**  


---

## Installation

```bash
pip install afaanoromo-tokenizer
```
## Usage
```python
from afaanoromo-tokenizer import ao_tokenizer

# Example text
text = "Afaanni oromoo afaan saba guddaati!"

# --- BPE tokenizer ---
bpe_tokenizer = ao_tokenizer("bpe")
bpe_tokens = bpe_tokenizer.encode(text)
print("BPE tokens:", bpe_tokens)
bpe_decoded = bpe_tokenizer.decode(bpe_tokens)
print("BPE decoded:", bpe_decoded)

# --- Unigram tokenizer ---
unigram_tokenizer = ao_tokenizer("unigram")
unigram_tokens = unigram_tokenizer.encode(text)
print("Unigram tokens:", unigram_tokens)
unigram_decoded = unigram_tokenizer.decode(unigram_tokens)
print("Unigram decoded:", unigram_decoded)

# --- WordPiece tokenizer ---
wordpiece_tokenizer = ao_tokenizer("wordpiece")
wordpiece_tokens = wordpiece_tokenizer.encode(text)
print("WordPiece tokens:", wordpiece_tokens)
wordpiece_decoded = wordpiece_tokenizer.decode(wordpiece_tokens)
print("WordPiece decoded:", wordpiece_decoded)

```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
