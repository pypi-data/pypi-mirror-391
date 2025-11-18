from collections import defaultdict
import random
import string
import pickle
from importlib import resources

class ChronoFidelius:
    """
    A class designed to facilitate the encryption and manipulation of plaintext
    with optional error injection and formatting using historical frequencies and methods.
    """
    def __init__(self, plaintext, set_seed: int = None,
                 include_errors: bool = False, error_type: str = None,
                 error_frequency: float = 0.05, include_spacing: bool = False,
                 max_length: int = 200,
                 set_punctuation: str = string.punctuation,
                 set_case: str = "upper"):
        """
            Initializes the ChronoFidelius class with plaintext and optional configurations.

            Parameters:
            - plaintext (str or list of str): The input plaintext to be processed.
            - set_seed (int, optional): A seed value for reproducibility of random operations. Default is None.
            - include_errors (bool, optional): If True, introduces errors (e.g., additions, deletions, doubles) into
            the plaintext. Default is False.
            - error_type (str, optional): Specifies the type of error to introduce. Valid options are:
                - "additions": Adds random characters.
                - "deletions": Removes characters.
                - "doubles": Doubles characters.
                - "all": Randomly selects between "additions", "deletions", or "doubles".
                Must be set if `include_errors` is True. Default is None.
            - error_frequency (float, optional): Frequency of errors in the plaintext (0–1). For example, 0.05
            introduces errors to 5% of the text. Default is 0.05.
            - include_spacing (bool, optional): If True, retains spaces and line breaks during formatting. Default is
            False.
            - max_length (int, optional): Maximum length of the formatted plaintext or chunks. Default is 200.
            - set_punctuation (str, optional): Specifies the set of punctuation characters to remove. Default is
            string.punctuation.
            - set_case (str, optional): Specifies case for plaintext strings. Default is upper. Valid options are:
                - "upper": Uppercase all characters
                - "lower": Lowercase all characters
                - "no_change": Make no changes to case

            Raises:
            - TypeError: If `plaintext` is not a string or a list of strings.
            - ValueError: If `include_errors` is True but `error_type` is not specified or invalid.
            - ValueError: If `error_frequency` exceeds 1.
        """

        if isinstance(plaintext, str):
            if set_case == "upper":
                self.plaintext = plaintext.upper()
            elif set_case == "lower":
                self.plaintext = plaintext.lower()
            elif set_case == "no_change":
                self.plaintext = plaintext
            else:
                raise ValueError(f"Invalid case option. Valid options: upper, lower, no_change")
        elif isinstance(plaintext, list):
            if set_case == "upper":
                self.plaintext = [text.upper() for text in plaintext]
            elif set_case == "lower":
                self.plaintext = [text.lower() for text in plaintext]
            elif set_case == "no_change":
                self.plaintext = plaintext
            else:
                raise ValueError(f"Invalid case option. Valid options: upper, lower, no_change")
        else:
            raise TypeError(f"Invalid plaintext type. Valid types: str, list")

        self.valid_lang_codes = ["cz", "nl", "en", "fr", "de", "el", "hu", "is",
                                 "it", "la", "pl", "ru", "sl", "es", "sv"]
        self.valid_languages = ["Czech (cz)", "Dutch (nl)", "English (en)", "French (fr)", "German (de)", "Greek (el)",
                                "Hungarian (hu)", "Icelandic (is)", "Italian (it)", "Latin (la)", "Polish (pl)",
                                "Russian (ru)", "Slovene (sl)", "Spanish (es)", "Swedish (sv)"]

        self.seed = set_seed
        self.punctuation = set_punctuation
        self.max_length = max_length
        self.set_case = set_case
        self.pt_ct_dict = defaultdict(dict)  # holds all plaintext and ciphertext

        self.error_types = ["additions", "deletions", "doubles"]  # or all
        self.errors = include_errors
        check_error_types = self.error_types + ["all"]

        if include_errors and error_type is None:
            raise ValueError(f"If include_errors must set error_type.")

        elif include_errors and error_type not in check_error_types:
            raise ValueError(f"Invalid error_type. Valid options: {check_error_types}")

        elif include_errors and error_frequency > 1:
            raise ValueError(f"Invalid error_frequency. {error_frequency} must \
        be less than 1.")

        elif include_errors:
            self._format_plaintext(plaintext=self.plaintext,
                                   include_spacing=include_spacing,
                                   error_type=error_type,
                                   error_frequency=error_frequency)

        else:
            self._format_plaintext(plaintext=self.plaintext,
                                   include_spacing=include_spacing)

    def encrypt_homophonic(self, key_type: str = "even", encryption_dict: dict = None,
                           nonalpha_subs: bool = None, lang_code: str = None,
                           set_frequencies: dict = None, set_alphabet: str = None, # string.ascii_uppercase,
                           freq_year: str = None, ct_as_int: bool = True, mix_code: bool = False):
        """
            Encrypts plaintext using a homophonic cipher.

            Parameters:
            - key_type (str): The type of encryption key ("even", "uneven", or "both"). Default is "even".
            - encryption_dict (dict): Optional pre-defined encryption dictionary. NOT VALID CURRENTLY - TO BE ADDED
            - nonalpha_subs (bool): Specifies whether to include substitutions for non-alphabetic characters. NOT VALID CURRENTLY - TO BE ADDED
            - lang_code (str): Language code for frequency analysis.
            - set_frequencies (dict): Custom frequency mappings for uneven key generation.
            - set_alphabet (str): Alphabet to use for even key generation.
            - freq_year (str): Year to use for historical frequency data.
            - ct_as_int (bool): Whether to represent ciphertext as string integers. Default is True.
            - mix_code (bool): Valid only when ct_as_int is True. Defines whether to encrypt consonants and vowels
            with different length integers. Default is False.

            Raises:
            - ValueError: If `encryption_dict` is provided without `nonalpha_subs`.
            - ValueError: If `key_type` is invalid.

        """

        self.ct_as_int = ct_as_int

        if not ct_as_int:
            self.mix_code = False
        else:
            self.mix_code = mix_code
            self.vowels = ('AEIOUYÀÁÂÃÄÅÆÈÉÊËÌÍÎÏÒÓÔÕÖØÙÚÛÜÝĀĂĄĒĔĘĚĪĬŌŎŐŒŮŪŬŰŸΑΕΙΟΥІАЕЫЭЮЯѠѢѦꙊꙖꟵἈἉἊἋἌἍἎἏ'
                           'ἘἙἚἛἜἝἨἩἪἫἬἭἮἯἸἹἺἻἼἽἾἿὈὉὊὋὌὍὙὛὝὟὨὩὪὫὬὭὮὯᾹᾺῙῩ')

        key_types = ["even", "uneven", "both"]

        if encryption_dict is not None and nonalpha_subs is None:  # NEED TO HANDLE THIS, for nomenclature
            raise ValueError(f"Declared encryption_dict without declaring \
        nonalpha_subs.")

        if not set_alphabet and not lang_code:
            set_alphabet = string.ascii_uppercase
        elif set_alphabet:
            set_alphabet = set_alphabet
        else: # not set_alphabet and lang_code
            if lang_code not in self.valid_lang_codes:
                raise ValueError(
                    f"Invalid lang_code: '{lang_code}' is not supported. Valid options are: {self.valid_languages}")

            char_freq_filepath = f"{lang_code}_char_freqs_dict.pkl"

            data_path = resources.files('chronofidelius.char_freqs').joinpath(char_freq_filepath)
            with data_path.open('rb') as f:
                char_freqs = pickle.load(f)

            if not freq_year:
                if self.set_case == "upper":
                    set_alphabet = "".join(char_freqs['all'].keys()).upper()
                elif self.set_case == "lower":
                    set_alphabet = "".join(char_freqs['all'].keys()).lower()
                elif self.set_case == "no_change":
                    set_alphabet = "".join(char_freqs['all'].keys()).upper() + "".join(
                        char_freqs['all'].keys()).lower()
            else:
                try:
                    if self.set_case == "upper":
                        set_alphabet = "".join(char_freqs[freq_year].keys()).upper()
                    elif self.set_case == "lower":
                        set_alphabet = "".join(char_freqs[freq_year].keys()).lower()
                    elif self.set_case == "no_change":
                        set_alphabet = "".join(char_freqs[freq_year].keys()).upper() + "".join(
                            char_freqs[freq_year].keys()).lower()
                except:
                    raise ValueError(
                        f"Invalid year_range: {freq_year} not supported. Valid options for language {lang_code} are: {char_freqs.keys()}"
                    )

        random.seed(self.seed)

        if key_type == "uneven":
            self._uneven_key_type(set_frequencies, freq_year, lang_code)

        elif key_type == "even":
            self._even_key_type(set_alphabet)

        elif key_type == "both":
            self._uneven_key_type(set_frequencies, freq_year, lang_code)
            self._even_key_type(set_alphabet)

        else:
            raise ValueError(f"Invalid key_type. Valid options: {key_types}")

    def _format_plaintext(self, plaintext, include_spacing: bool,
                          error_type: str = None, error_frequency: float = None):
        """
            Formats the plaintext by cleaning, splitting, and optionally introducing errors.

            Parameters:
            - plaintext (str or list of str): The input plaintext to be formatted.
            - include_spacing (bool): If True, retains spaces and line breaks during formatting.
            - error_type (str, optional): Specifies the type of error to introduce. Valid options are:
                - "additions": Adds random characters.
                - "deletions": Removes characters.
                - "doubles": Doubles characters.
                - "all": Randomly selects between "additions", "deletions", or "doubles".
                Default is None.
            - error_frequency (float, optional): Frequency of errors in the plaintext (0–1). For example, 0.05
            introduces errors to 5% of the text. Default is None.
            - set_case (str, optional): Specifies case for plaintext strings (e.g., upper, lower, no_change). Default
            is upper.

            Sets:
            - self.formatted_plaintext: The cleaned and processed plaintext.
            - self.pt_ct_dict: A dictionary where:
                - Each key represents a chunk index.
                - Each value contains:
                    - "plaintext": The corresponding chunk of plaintext.
                    - "plaintext_errors_included": The chunk including errors as characters (if applicable).
                    - "plaintext_errors_hashed": The chunk including errors as '#' for insertions and '&' for
                    deletions (if applicable).

            Raises:
            - TypeError: If `plaintext` is not a string or list of strings.
        """

        random.seed(self.seed)
        unwanted_chars = self.punctuation + ("\n\t" if include_spacing else " \n\t")

        if isinstance(plaintext, str):
            clean_plaintext = "".join([char for char in plaintext if char not in unwanted_chars])
            split_formatted_plaintext = self._chunk_plaintext(
                text_string=clean_plaintext, max_length=self.max_length)

        elif isinstance(plaintext, list):
            clean_plaintext = [
                "".join([char for char in text if char not in unwanted_chars])
                for text in plaintext
            ]

            split_formatted_plaintext = [
                chunk
                for text in clean_plaintext
                for chunk in self._chunk_plaintext(text_string=text, max_length=self.max_length)
            ]

        self.formatted_plaintext = clean_plaintext

        for i, text_chunk in enumerate(split_formatted_plaintext):
            self.pt_ct_dict[str(i)]["plaintext"] = text_chunk

            if not error_frequency:
                self.pt_ct_dict[str(i)]["plaintext_errors_hashed"] = None
                self.pt_ct_dict[str(i)]["plaintext_errors_included"] = None

            else:
                pt_len = len(text_chunk)
                total_errors = max(1, int(pt_len * error_frequency))
                sorted_indexes = sorted(random.sample(range(pt_len), total_errors))

                gold_pt_errors = ""
                gold_pt_errors_hashed = ""
                for j, char in enumerate(text_chunk):
                    if j in sorted_indexes:
                        error_choice = random.choice(self.error_types) if error_type == "all" else error_type
                        gold_pt_errors += self._make_error_choice(char, error_choice)

                        if error_choice == "additions" or error_choice == "doubles":
                            gold_pt_errors_hashed += char + "#"
                        else:
                            gold_pt_errors_hashed += "&"
                    else:
                        gold_pt_errors += char
                        gold_pt_errors_hashed += char

                self.pt_ct_dict[str(i)]["plaintext_errors_hashed"] = gold_pt_errors_hashed
                self.pt_ct_dict[str(i)]["plaintext_errors_included"] = gold_pt_errors

    def _make_error_choice(self, plaintext_char: str, error_type: str):
        """
        Modifies a plaintext character based on the specified type of error.

        Parameters:
        - plaintext_char (str): The character from the plaintext to be modified.
        - error_type (str): The type of error to introduce. Valid options are
                            "all", "additions", "deletions", and "doubles".
                            "additions" are determined through a random choice of
                            character included in the plaintext.

        Returns:
        - str: The modified plaintext character after introducing the specified error.
        """
        random.seed(self.seed)

        if error_type == "additions" and isinstance(self.formatted_plaintext, str):
            rand_char = random.choice(self.formatted_plaintext)
            return plaintext_char + rand_char
        elif error_type == "additions" and isinstance(self.formatted_plaintext, list):
            rand_char = random.choice(self.formatted_plaintext[0])
            return plaintext_char + rand_char
        elif error_type == "deletions":
            return ""
        elif error_type == "doubles":
            return plaintext_char + plaintext_char
        else:
            raise ValueError(f"{error_type} not valid.")

    def _chunk_plaintext(self, text_string: str, max_length: int):
        """
        Divides a text string into chunks of a specified maximum length.

        Parameters:
        - text_string (str): The string to be chunked.
        - max_length (int): The maximum length of each chunk. It must be a
                            positive integer.

        Returns:
        - list of str: A list containing the chunked substrings. If the original
          string is empty or the max_length is greater than the string length,
          the list will contain the original string as the only element. If
          max_length is less than or equal to zero, the list will be empty.
        """

        return [text_string[i:i + max_length] for i in
                range(0, len(text_string), max_length)]

    def _uneven_key_type(self, set_frequencies: dict = None, freq_year: str = None, lang_code: str = None):
        """
        Configures uneven key types for homophonic encryption.

        Parameters:
        - set_frequencies (dict, optional): A custom frequency dictionary mapping characters to their frequencies.
        - freq_year (str, optional): The year for which unigram frequencies are used.
        - lang_code (str, optional): The language code to select predefined unigram frequencies.

        Sets:
        - self.alphabet (str): The alphabet used for encryption, derived from the frequency dictionary.
        - self.frequency_dict (dict): The dictionary containing character frequencies.

        Raises:
        - ValueError: If both `set_frequencies` and `freq_year` are provided.
        - ValueError: If neither `set_frequencies` nor `freq_year` is provided.
        - ValueError: If `lang_code` is invalid or not supported.
        """

        if set_frequencies and freq_year:
            raise ValueError("Cannot declare both set_frequencies and freq_year.")

        if set_frequencies:
            if self.set_case == "upper":
                self.alphabet = "".join(set_frequencies.keys()).upper()
            elif self.set_case == "lower":
                self.alphabet = "".join(set_frequencies.keys()).lower()
            elif self.set_case == "no_change":
                self.alphabet = "".join(set_frequencies.keys()).lower() + "".join(set_frequencies.keys()).upper()
            self.frequency_dict = set_frequencies

        elif freq_year:
            if lang_code not in self.valid_lang_codes:
                raise ValueError(
                    f"Invalid lang_code: '{lang_code}' is not supported. Valid options are: {self.valid_languages}")

            try:
                char_freq_filepath = f"{lang_code}_char_freqs_dict.pkl"
                data_path = resources.files('chronofidelius.char_freqs').joinpath(char_freq_filepath)
                with data_path.open('rb') as f:
                    char_freqs = pickle.load(f)

                self.frequency_dict = char_freqs[freq_year]
            except:
                raise ValueError(
                    f"Invalid year_range: {freq_year} not supported. Valid options for language {lang_code} are: {char_freqs.keys()}"
                )
            if self.set_case == "upper":
                self.alphabet = "".join(self.frequency_dict.keys()).upper()
            elif self.set_case == "lower":
                self.alphabet = "".join(self.frequency_dict.keys()).lower()
            elif self.set_case == "no_change":
                self.alphabet = "".join(self.frequency_dict.keys()).lower() + "".join(self.frequency_dict.keys()).upper()
        else:
            raise ValueError("Must provide either set_frequencies or freq_year for uneven key_type.")

        self._uneven_splits_homophonic()

    def _even_key_type(self, set_alphabet):
        """
            Configures even key types for homophonic encryption.

            Parameters:
            - set_alphabet (str): The alphabet to use for even key generation.

            Sets:
            - self.alphabet (str): The alphabet used for encryption.

        """
        self.alphabet = set_alphabet
        self._even_splits_homophonic()

    def _even_splits_homophonic(self):
        """
            Generates encryption dictionaries for even key types and links them to plaintexts.

            This method creates encryption dictionaries for keys of varying lengths (2, 3, and 4),
            with multiple options for each length. The encryption dictionaries are then linked
            to the plaintext chunks and ciphertexts based on the characters present in each document.

            Sets:
            - Updates `self.pt_ct_dict` to include:
                - Ciphertexts for each plaintext chunk.
                - Encryption dictionaries specific to each document.

            Raises:
            - ValueError: If `self.alphabet` is not set or is empty.
        """

        if not self.alphabet:
            raise ValueError("Alphabet is not set or is empty. Cannot generate encryption dictionaries.")

        random.seed(self.seed)

        key_lengths = {
            2: {"bottom_n": 10, "top_n": 100, "factor": 3, "extra": 5, "options": 3},
            3: {"bottom_n": 100, "top_n": 1000, "factor": 5, "extra": 10, "options": 5},
            4: {"bottom_n": 1000, "top_n": 10000, "factor": 5, "extra": 15, "options": 5},
        }

        for key_len, params in key_lengths.items():
            total_numbers_needed = len(self.alphabet) * params["factor"] + params["extra"]
            dict_category = f"key_even_len_{key_len}"

            for option in range(1, params["options"] + 1):
                category_name = f"{dict_category}_{option}opt"
                try:
                    self._set_encryption_dict_even(
                        params["bottom_n"], params["top_n"], total_numbers_needed, options=option,
                        category_name=category_name
                    )
                except:
                    continue

        all_key_dicts = [key for key in self.pt_ct_dict.keys() if key.startswith("key_even")]
        all_plaintexts = [
            key for key in self.pt_ct_dict.keys() if not key.startswith("key") and not key.startswith("ciphertext")
        ]

        for each_doc in all_plaintexts:
            doc = self.pt_ct_dict[each_doc]["plaintext"] if self.errors == False else self.pt_ct_dict[each_doc]["plaintext_errors_included"]
            chars_in_doc = sorted(set(doc))

            for key_dict in all_key_dicts:
                current_dict = self.pt_ct_dict[key_dict]
                ct_title = f"ciphertext{key_dict[3:]}"

                doc_specific_key_dict = {char: current_dict[char] for char in chars_in_doc if char in current_dict}
                ct = self._encryption_homophonic(doc, current_dict)
                doc_specific_key_dict = {
                    char: [value for value in values if str(value) in ct]
                    for char, values in doc_specific_key_dict.items()
                }

                self.pt_ct_dict[each_doc][ct_title] = ct
                self.pt_ct_dict[each_doc][key_dict] = doc_specific_key_dict

    def _uneven_splits_homophonic(self):
        """
            Generates encryption dictionaries for uneven key types and links them to plaintexts.

            This method dynamically calculates frequency distributions for uneven key types,
            generates encryption dictionaries for keys of varying lengths (2, 3, and 4), and
            links the dictionaries and corresponding ciphertexts to the plaintexts.

            Sets:
            - Updates `self.pt_ct_dict` to include:
                - Ciphertexts for each plaintext chunk.
                - Encryption dictionaries specific to each document.

            Raises:
            - ValueError: If `self.frequency_dict` is not set or is empty.

        """
        if not self.frequency_dict:
            raise ValueError("Frequency dictionary is not set or is empty. \
            Cannot generate uneven encryption dictionaries.")

        random.seed(self.seed)

        avg = sum(self.frequency_dict.values()) / len(self.frequency_dict.values())
        sort_freq = sorted(set(self.frequency_dict.values()))
        less_idx, more_idx = self._set_index(sort_freq, avg)
        options_dict_freq = self._frequency_to_options_dict(less_idx, more_idx, sort_freq)
        total_numbers_needed = sum(options_dict_freq.values()) + 5

        key_lengths = {
            2: {"bottom_n": 10, "top_n": 100},
            3: {"bottom_n": 100, "top_n": 1000},
            4: {"bottom_n": 1000, "top_n": 10000},
        }

        for key_len, params in key_lengths.items():
            dict_category = f"key_uneven_len_{key_len}_uneven"
            try:
                self._set_encryption_dict_uneven(
                    params["bottom_n"], params["top_n"], total_numbers_needed, options_dict_freq, dict_category
                )
            except:
                continue

        all_key_dicts = [key for key in self.pt_ct_dict.keys() if key.startswith("key_uneven")]
        all_plaintexts = [
            key for key in self.pt_ct_dict.keys() if not key.startswith("key") and not key.startswith("ciphertext")
        ]

        for each_doc in all_plaintexts:
            doc = self.pt_ct_dict[each_doc]["plaintext"] if self.errors == False else self.pt_ct_dict[each_doc]["plaintext_errors_included"]
            chars_in_doc = sorted(set(doc))

            for key_dict in all_key_dicts:
                current_dict = self.pt_ct_dict[key_dict]
                ct_title = f"ciphertext{key_dict[3:]}"

                doc_specific_key_dict = {char: current_dict[char] for char in chars_in_doc if char in current_dict}
                ct = self._encryption_homophonic(doc, current_dict)

                self.pt_ct_dict[each_doc][ct_title] = ct
                self.pt_ct_dict[each_doc][key_dict] = doc_specific_key_dict


    def _set_encryption_dict_even(self, start: int, stop: int, total: int,
                              options: int, category_name: str):
        """
        Creates an encryption dictionary for even key types.

        This method assigns random unique numbers to each character in `self.alphabet` for encryption.
        Each character is assigned a specified number of random numbers (`options`).

        Parameters:
        - start (int): The starting range of random numbers.
        - stop (int): The ending range of random numbers (exclusive).
        - total (int): The total number of random numbers required.
        - options (int): The number of random numbers assigned to each character.
        - category_name (str): The name under which the dictionary is stored in `self.pt_ct_dict`.

        Sets:
        - self.pt_ct_dict[category_name]: A dictionary mapping each character in `self.alphabet`
          to a list of random unique numbers.
        """

        random.seed(self.seed)

        if self.mix_code == True:
            total_vowels = len([char for char in self.alphabet if char in self.vowels]) * options
            total_consonants = len([char for char in self.alphabet if char not in self.vowels]) * options
            if start == 10:
                consonant_range = random.sample([f"{i:02}" for i in range(100)], total_consonants)  # 2-digit
                vowel_range = random.sample([f"{i:03}" for i in range(1000)], total_vowels)  # 3-digit
            elif start == 100:
                consonant_range = random.sample([f"{i:03}" for i in range(1000)], total_consonants)  # 3-digit
                vowel_range = random.sample([f"{i:02}" for i in range(100)], total_vowels)  # 2-digit
            elif start == 1000:
                consonant_range = random.sample([f"{i:04}" for i in range(10000)], total_consonants)  # 4-digit
                vowel_range = random.sample([f"{i:03}" for i in range(1000)], total_vowels)

            C_index = 0
            V_index = 0
            encryption_dict = {}

            for char in self.alphabet:
                if char in self.vowels:
                    encrypts = [str(num) for num in vowel_range[V_index:V_index + options]]
                    V_index += options
                else:
                    encrypts = [str(num) for num in consonant_range[C_index:C_index + options]]
                    C_index += options

                encryption_dict[char] = encrypts

        else: # self.mix_code == False
            if start == 10:
                random_unique_numbers = random.sample([f"{i:02}" for i in range(100)], total)
            elif start == 100:
                random_unique_numbers = random.sample([f"{i:03}" for i in range(1000)], total)  # random.sample(range(start, stop), total)
            elif start == 1000:
                random_unique_numbers = random.sample([f"{i:04}" for i in range(10000)], total)

            starting_index = 0
            encryption_dict = {}

            for char in self.alphabet:
                encrypts = [str(num) for num in random_unique_numbers[starting_index:starting_index + options]]
                encryption_dict[char] = encrypts
                starting_index += options

        self.pt_ct_dict[category_name] = encryption_dict


    def _set_encryption_dict_uneven(self, start: int, stop: int, total: int,
                                options: dict, category_name: str):
        """
            Creates an encryption dictionary for uneven key types.

            This method assigns a varying number of random unique numbers to each character in
            `self.alphabet` based on its frequency, as specified in `self.frequency_dict`.

            Parameters:
            - start (int): The starting range of random numbers.
            - stop (int): The ending range of random numbers (exclusive).
            - total (int): The total number of random numbers required.
            - options (dict): A mapping of frequencies to the number of random numbers to assign.
            - category_name (str): The name under which the dictionary is stored in `self.pt_ct_dict`.

            Sets:
            - self.pt_ct_dict[category_name]: A dictionary mapping each character in `self.alphabet`
              to a list of random unique numbers.
        """

        random.seed(self.seed)

        if self.mix_code == True:
            total_vowels = 0
            total_consonants = 0

            for char in self.alphabet:
                freq = self.frequency_dict.get(char.lower()) or self.frequency_dict.get(char.upper())
                if freq is None:
                    raise KeyError(f"Frequency for character '{char}' not found in frequency dictionary.")

                if freq not in options:
                    raise KeyError(f"Frequency '{freq}' not found in options dictionary.")

                num_option = options[freq]
                if char in self.vowels:
                    total_vowels += num_option
                else:
                    total_consonants += num_option

            if start == 10:
                consonant_range = random.sample([f"{i:02}" for i in range(100)], total_consonants)  # 2-digit
                vowel_range = random.sample([f"{i:03}" for i in range(1000)], total_vowels)     # 3-digit
            elif start == 100:
                consonant_range = random.sample([f"{i:03}" for i in range(1000)], total_consonants)  # 3-digit
                vowel_range = random.sample([f"{i:02}" for i in range(100)], total_vowels)       # 2-digit
            elif start == 1000:
                consonant_range = random.sample([f"{i:04}" for i in range(10000)], total_consonants)  # 4-digit
                vowel_range = random.sample([f"{i:03}" for i in range(1000)], total_vowels)       # 3-digit

            C_index = 0
            V_index = 0
            encryption_dict = {}

            for char in self.alphabet:
                freq = self.frequency_dict.get(char.lower()) or self.frequency_dict.get(char.upper())
                num_option = options[freq]

                if char in self.vowels:
                    encrypts = [str(num) for num in vowel_range[V_index:V_index + num_option]]
                    V_index += num_option
                else:
                    encrypts = [str(num) for num in consonant_range[C_index:C_index + num_option]]
                    C_index += num_option

                encryption_dict[char] = encrypts

        else: # (self.mix_code == False)
            if start == 10:
                random_unique_numbers = random.sample([f"{i:02}" for i in range(100)], total)
            elif start == 100:
                random_unique_numbers = random.sample([f"{i:03}" for i in range(1000)], total) # random.sample(range(start, stop), total)
            elif start == 1000:
                random_unique_numbers = random.sample([f"{i:04}" for i in range(10000)], total)

            starting_index = 0
            encryption_dict = {}

            for char in self.alphabet:
                freq = self.frequency_dict.get(char.lower()) or self.frequency_dict.get(char.upper())
                if freq is None:
                    raise KeyError(f"Frequency for character '{char}' not found in frequency dictionary.")

                if freq not in options:
                    raise KeyError(f"Frequency '{freq}' not found in options dictionary.")

                num_option = options[freq]

                encrypts = [str(num) for num in random_unique_numbers[starting_index:starting_index + num_option]]
                encryption_dict[char] = encrypts
                starting_index += num_option

        self.pt_ct_dict[category_name] = encryption_dict


    def _set_index(self, sorted_frequencies: list, average_frequency: float) -> tuple:
        """
        Determines indices for splitting the list of sorted frequencies into categories.

        The "under" group (frequencies below or equal to the average) is split into two parts,
        while the "over" group (frequencies above the average) is split into three parts.

        Parameters:
        - sorted_frequencies (list of float): A list of frequencies sorted in ascending order.
        - average_frequency (float): The average frequency to divide the groups.

        Returns:
        - tuple: A tuple containing two integers:
            - The first integer represents the division point (index) in the "under" group.
            - The second integer represents the division point in the "over" group.

        """

        total_under = sum(1 for freq in sorted_frequencies if freq <= average_frequency)
        total_over = len(sorted_frequencies) - total_under

        # Calculate splits
        under_option_split = round(total_under / 2)
        over_option_split = round(total_over / 3)

        return under_option_split, over_option_split


    def _frequency_to_options_dict(self, low_freq_split_index,
                                   high_freq_split_index, sorted_frequencies):
        """
        Creates a dictionary mapping each unique frequency to a specified number of
        options based on its position. Frequencies are categorized into five groups.

        Parameters:
        - low_freq_split_index (int): The index used to determine the split point
                                      for lower frequencies.
        - high_freq_split_index (int): The index used to determine the split point
                                       for higher frequencies.
        - sorted_frequencies (list of int/float): A list of unique frequencies
                                                  sorted in ascending order.

        Returns:
        - options_dict: A dictionary where each key is a unique frequency from
                        `sorted_frequencies` and each value is an integer from 1 to
                        5, representing the number of options allocated to that
                        frequency category.

        """

        options_dictionary = dict()

        for i, freq in enumerate(sorted_frequencies):
            if i < low_freq_split_index:
                options_dictionary[freq] = 1
            elif i < (low_freq_split_index * 2):
                options_dictionary[freq] = 2
            elif i < ((low_freq_split_index * 2) + high_freq_split_index):
                options_dictionary[freq] = 3
            elif i < ((low_freq_split_index * 2) + (high_freq_split_index * 2)):
                options_dictionary[freq] = 4
            else:
                options_dictionary[freq] = 5

        return options_dictionary

    def _encryption_homophonic(self, plaintext: str, encryption_dictionary: dict):
        """
        Encrypts a given plaintext using a homophonic substitution cipher.

        Each letter in the plaintext is substituted with a random choice from the
        corresponding list of codes in the encryption dictionary. Characters not found
        in the encryption dictionary are left unchanged.

        Parameters:
        - plaintext (str): The message to be encrypted.
        - encryption_dictionary (dict): A dictionary where each key is a plaintext
                                         character and each value is a list of encryption
                                         options for that character.

        Returns:
        - str or list: The encrypted message. If `self.ct_as_int` is False, the message is
                       returned as a string with encrypted characters separated by
                       "_". If `self.ct_as_int` is True, the message is returned
                       as a list of string integers.

        """

        ciphertext = []

        for let in plaintext:
            if let in encryption_dictionary:
                cipher_let = random.choice(encryption_dictionary[let])
                ciphertext.append(cipher_let if self.ct_as_int else str(cipher_let))
            else:
                ciphertext.append(let)

        return ciphertext if self.ct_as_int else "_".join(ciphertext)

"""
if __name__ == "__main__":
    e_or_une = "uneven"
    obj = ChronoFidelius("helloWorldyY", include_errors=True, error_type="all", # set_seed=9,
                         set_case="no_change", error_frequency=0.5)
    print(obj.errors)

    obj.encrypt_homophonic(lang_code="sv", mix_code=True, key_type=e_or_une, freq_year="all") # , set_frequencies={"h": 0.5, "e": 0.1, "l" : 0.4})
    print(obj.alphabet)

    print(obj.pt_ct_dict["0"])
    pt = obj.pt_ct_dict["0"]["plaintext"]
    pt_err = obj.pt_ct_dict["0"]["plaintext_errors_included"]
    pt_hash = obj.pt_ct_dict["0"]["plaintext_errors_hashed"]
    if e_or_une == "even" or e_or_une == "both":
        ct = obj.pt_ct_dict["0"]["ciphertext_even_len_4_5opt"]
    elif e_or_une == "uneven":
        ct = obj.pt_ct_dict["0"]["ciphertext_uneven_len_4_uneven"]


    print(f"{len(pt)=}, {len(pt_err)=}, {len(pt_hash)=}, {len(ct)=}")
"""