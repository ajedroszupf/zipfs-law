import argparse
from pathlib import Path
from typing import List, Any, Callable
from collections import Counter
from functools import partial

import nltk
from nltk.tokenize import word_tokenize
from scipy.stats import pearsonr
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from zipfs_law.utils.luna_parser import LunaParser
from zipfs_law.utils.multiwoz_parser import MultiwozParser
from zipfs_law.utils.helpers import expand_contractions, remove_punctuation

nltk.download("punkt")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--luna-dataset-dirpath",
        type=Path,
        required=True,
        help="Path to a home directory of the LUNA dataset "
             "(directory LUNA.PL from http://zil.ipipan.waw.pl/LUNA?action=AttachFile&do=view&target=LUNA.PL.zip).",
    )
    parser.add_argument(
        "--multiwoz-dataset-dirpath",
        type=Path,
        required=True,
        help="Path to MultiWOZ_2.2 (https://github.com/budzianowski/multiwoz/tree/master/data/MultiWOZ_2.2).",
    )
    return parser.parse_args()


def dialogues_to_tokens(
        dialogues: List[Any],
        tokenizer: Callable[[str], List[str]],
        remove_punctuation_: bool = True,
        expand_contractions_: bool = False,
) -> List[str]:
    tokens = []
    for dialogue in dialogues:
        for turn in dialogue['turns']:
            utterance = turn['utterance']
            if expand_contractions_:
                utterance = expand_contractions(utterance)
            if remove_punctuation_:
                utterance = remove_punctuation(utterance)
            utterance_tokens = tokenizer(utterance)
            tokens.extend(utterance_tokens)
    return tokens


def main(luna_dataset_dirpath: Path, multiwoz_dataset_dirpath: Path) -> None:
    luna_parser = LunaParser(data_path=luna_dataset_dirpath)
    multiwoz_parser = MultiwozParser(data_path=multiwoz_dataset_dirpath)
    luna_dialogues = luna_parser.parse()
    multiwoz_dialogues = multiwoz_parser.parse()
    tokenizer_en = word_tokenize
    tokenizer_pl = partial(word_tokenize, language="polish")
    luna_tokens = dialogues_to_tokens(
        dialogues=luna_dialogues,
        tokenizer=tokenizer_pl,
        remove_punctuation_=True,
        expand_contractions_=False
    )
    multiwoz_tokens = dialogues_to_tokens(
        dialogues=multiwoz_dialogues,
        tokenizer=tokenizer_en,
        remove_punctuation_=True,
        expand_contractions_=True
    )
    luna_counter = Counter(luna_tokens)
    luna_lengths_and_frequencies = [(len(k), v) for k, v in luna_counter.items()]
    luna_lengths = [item for item, _ in luna_lengths_and_frequencies]
    luna_frequencies = [item for _, item in luna_lengths_and_frequencies]
    multiwoz_counter = Counter(multiwoz_tokens)
    multiwoz_lengths_and_frequencies = [(len(k), v) for k, v in multiwoz_counter.items()]
    multiwoz_lengths = [item for item, _ in multiwoz_lengths_and_frequencies]
    multiwoz_frequencies = [item for _, item in multiwoz_lengths_and_frequencies]

    luna_r = pearsonr(luna_lengths, luna_frequencies)
    multiwoz_r = pearsonr(multiwoz_lengths, multiwoz_frequencies)
    print(f"LUNA Pearson's r: {luna_r}")
    print(f"MultiWOZ Pearson's r: {multiwoz_r}")


if __name__ == "__main__":
    args = parse_args()
    main(
        luna_dataset_dirpath=args.luna_dataset_dirpath,
        multiwoz_dataset_dirpath=args.multiwoz_dataset_dirpath,
    )
