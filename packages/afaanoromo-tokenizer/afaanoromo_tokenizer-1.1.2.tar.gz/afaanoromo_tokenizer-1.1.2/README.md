# Afaan Oromo Tokenizer



Afaan_oromo_tokenizer is a linguistically informed and computationally efficient tokenizer for **Afaan Oromo**, one of the most widely spoken low-resource languages in Africa.  


-------------------------------------------------


 - While tokenizers exist for major languages (English, Chinese, etc.), Afan Oromo lacks robust open-source tokenization tools.  
 - Afaan_oromo_tokenizer bridges that gap, facilitating NLP research for afaan Oromo.


---

## Features

- Included: **BPE**, **Unigram**, **WordPiece**
- Trained on **14 million tokens**
- Total unique tokens in dataset: **420,000**
- Vocabulary size for each tokenizer type: **55,000**

---

## Installation

```bash
pip install afaanoromo-okenizer

```
## Usage

```python
from afaanoromo_tokenizer import ao_tokenizer

# Example text
text = "Afaanni Oromoo afaan saba guddaati!"

# --- BPE tokenizer ---
bpe_tokenizer = ao_tokenizer("bpe")
bpe_tokens = bpe_tokenizer.encode(text).tokens
print("BPE tokens:", bpe_tokens)
bpe_decoded = bpe_tokenizer.decode(bpe_tokens)
print("BPE decoded:", bpe_decoded)

# --- Unigram tokenizer ---
unigram_tokenizer = ao_tokenizer("unigram")
unigram_tokens = unigram_tokenizer.encode(text).tokens
print("Unigram tokens:", unigram_tokens)
unigram_decoded = unigram_tokenizer.decode(unigram_tokens)
print("Unigram decoded:", unigram_decoded)

# --- WordPiece tokenizer ---
wordpiece_tokenizer = ao_tokenizer("wordpiece")
wordpiece_tokens = wordpiece_tokenizer.encode(text).tokens
print("WordPiece tokens:", wordpiece_tokens)
wordpiece_decoded = wordpiece_tokenizer.decode(wordpiece_tokens)
print("WordPiece decoded:", wordpiece_decoded)


```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
