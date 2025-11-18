"""
ChronoFidelius: A library for plaintext encryption using homophonic substitution and historical character frequencies.

This package provides tools for encrypting plaintext with configurable error injection,
frequency-based key generation, and homophonic substitution ciphers.

Classes:
- ChronoFidelius: Main class for managing plaintext encryption.

Usage:
    from chronofidelius import ChronoFidelius

    # Example
    cf = ChronoFidelius(plaintext="Hello, World!",
                        include_errors=True,
                        error_type="all",
                        set_seed=42)
    cf.encrypt_homophonic()

    print(cf.pt_ct_dict)
    > defaultdict(<class 'dict'>, {
            '0': {
                'plaintext': 'HELLOWORLD',
                'plaintext_errors_included': 'HEELLOWORLD',
                'ciphertext_even_len_2_1opt': ['23', '41', '64', '64', '90', '94', '90', '74', '64', '45'],
                'key_even_len_2_1opt': {'D': ['45'], 'E': ['41'], 'H': ['23'], 'L': ['64'], 'O': ['90'], 'R': ['74'], 'W': ['94']},
                'ciphertext_even_len_2_2opt':
                    ....
                }
        }
"""

from .main import ChronoFidelius
from .unigram_frequencies import all_unigrams_frequencies

