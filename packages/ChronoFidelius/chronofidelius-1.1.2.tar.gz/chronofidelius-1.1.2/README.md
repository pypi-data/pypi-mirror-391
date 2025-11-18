# ChronoFidelius

ChronoFidelius is a Python library for plaintext encryption using homophonic substitution and historical character frequencies. It provides configurable error injection, frequency-based key generation, and advanced encryption techniques inspired by historical cryptography.

---

## Features
- **Homophonic Substitution Cipher**: Encrypts plaintext with multiple cipher options for each character
- **Frequency-Based Key Generation**: Supports even and uneven key generation using historical unigram frequencies
- **Error Injection**: Introduces errors (additions, deletions, or doubles) into plaintext for obfuscation
- **Custom Configurations**: Control error frequency, character spacing, and more

---

## Installation

Install `ChronoFidelius` using `pip`:

```bash
pip install ChronoFidelius
```

Or, install directly from the source:

```bash
git clone https://github.com/mbruton0426/ChronoFidelius.git
cd ChronoFidelius
pip install .
```

---

## Usage

When initializing ChronoFidelius, the only required variable is some text to encrypt, either as a str or list of str.

### Initalization:
```python
from chronofidelius import ChronoFidelius

# Initialize the ChronoFidelius object
cf = ChronoFidelius("Hello, World!")
```

Optional Parameters: initialization
- **set_seed (int, optional)**: A seed value for reproducibility of random operations. Default is None
- **include_errors (bool, optional)**: If True, introduces errors (e.g., additions, deletions, doubles) into the plaintext. Default is False
- **error_type (str, optional)**: Specifies the type of error to introduce. Must be set if `include_errors` is True. Default is None. Valid options are:
        - **"additions"**: Adds random characters
        - **"deletions"**: Removes characters
        - **"doubles"**: Doubles characters
        - **"all"**: Randomly selects between "additions", "deletions", or "doubles"
- **error_frequency (float, optional)**: Frequency of errors in the plaintext (0–1). For example, 0.05 introduces errors to 5% of the text. Default is 0.05
- **include_spacing (bool, optional)**: If True, retains spaces and line breaks during formatting. Default is False
- **max_length (int, optional)**: Maximum length of the formatted plaintext or chunks. Default is 200
- **set_punctuation (str, optional)**: Specifies the set of punctuation characters to remove. Default is string.punctuation
- **set_case (str, optional): Specifies case for plaintext strings. Default is upper. Valid options are:
        - **"upper"**: Uppercase all characters
        - **"lower"**: Lowercase all characters
        - **"no_change"**: Make no changes to case


### Encrypting Plaintexts
Plaintexts can be encrypted with: 
```python
cf.encrypt_homophonic()
```
This automatically encrypts plaintext(s) according to every possible option based on the default values. Plaintext(s), ciphertexts, and keys are then all available as a dictionary in:

```python
cf.pt_ct_dict
```
Optional Parameters: encrypt_homophonic()
- **key_type (str)**: The type of encryption key ("even", "uneven", or "both"). Default is "even"
- **lang_code (str)**: Language code for character frequencies and automatic alphabet retrieval. Valid options: "Czech (cz)", "Dutch (nl)", "English (en)", "French (fr)", "German (de)", "Greek (el)", "Hungarian (hu)", "Icelandic (is)", "Italian (it)", "Latin (la)", "Polish (pl)", "Russian (ru)", "Slovene (sl)", "Spanish (es)", "Swedish (sv)"
- **freq_year (str)**: Time period for character frequencies. Varies by language. Set to "a" for a print out of available year ranges.
- **set_frequencies (dict)**: Custom frequency mappings for uneven key generation
- **set_alphabet (str)**: Manually set alphabet to use for key generation
- **ct_as_int (bool)**: Whether to represent ciphertext characters as a single string connected by "_" (False), or as a list of string type integers (True). Default is True 
- **mix_code (bool)**: Whether to encrypt consonants and vowels with different length integers. Valid only when ct_as_int is True. Default is False.


### Utilizing Custom Character Frequencies
All uneven-type encryptions require character frequencies. If frequencies are not available for the language you're working with, or you would otherwise like to set your own, you may do so.
```python
# Custom frequency dictionary
custom_frequencies = {"A": 0.1, "B": 0.2, "C": 0.3, "D": 0.4}

cf.encrypt_homophonic(set_frequencies=custom_frequencies)
```
---

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

---

## Citation

If you use this tool in your research, please cite:

```latex
@inproceedings{bruton2025statistics,
  title     = {From Statistics to Neural Networks: Enhancing Ciphertext-Plaintext Alignment in Historical Substitution Ciphers For Automatic Key Extraction},
  author    = {Bruton, Micaella and Megyesi, Be{\'a}ta},
  booktitle = {Proceedings of the International Conference on Historical Cryptology (HistoCrypt)},
  year      = {2025},
}
```
