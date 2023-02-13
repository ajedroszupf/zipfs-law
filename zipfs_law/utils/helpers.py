import string

import contractions

from typing import Any, Dict, List, Optional, Union


def remove_punctuation(text: str) -> str:
    return text.translate(str.maketrans("", "", string.punctuation))


def expand_contractions(text: str) -> str:
    return contractions.fix(text)


def init_token_dict(
    token: str,
    morphosyntactic_tag: Optional[str] = None,
    functional_act: Optional[str] = None,
    slot: Optional[str] = None,
    lemma: Optional[str] = None,
) -> Dict[str, Union[str, None]]:
    return {
        "token": token,
        "morphosyntactic_tag": morphosyntactic_tag,
        "functional_act": functional_act,
        "slot": slot,
        "lemma": lemma,
    }


def init_turn_dict(
    turn_id: int,
    speaker_id: str,
    utterance: str,
    tokens: List[Dict[str, str]],
    dialogue_acts: Optional[List[str]] = None,
    intents: Optional[List[str]] = None,
    state: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    if state is None:
        state = dict()
    if dialogue_acts is None:
        dialogue_acts = []
    if intents is None:
        intents = []
    return {
        "turn_id": turn_id,
        "speaker_id": speaker_id,
        "utterance": utterance,
        "dialogue_acts": dialogue_acts,
        "intents": intents,
        "tokens": tokens,
        "state": state,
    }

