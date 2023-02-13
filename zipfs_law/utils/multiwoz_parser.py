import os
from glob import glob
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from zipfs_law.constants import UTTERANCE_SPLIT_CHARACTER
from zipfs_law.utils.helpers import init_token_dict, init_turn_dict
from zipfs_law.io import load_json


class MultiwozParser:
    def __init__(
        self,
        data_path: str,
        no_active_intent_token: str = "NONE",
        speaker_with_intent_id: str = "USER",
        speaker_id_mapping: Optional[Dict[str, str]] = None,
    ):
        if not Path(data_path).is_dir():
            raise ValueError("MultiwozParser expects a data directory as input path.")
        self.data_path = data_path
        if speaker_id_mapping is None:
            self.speaker_id_mapping = {"USER": "CLIENT", "SYSTEM": "AGENT"}
        else:
            self.speaker_id_mapping = speaker_id_mapping
        self.no_active_intent_token = no_active_intent_token
        self.speaker_with_intent_id = speaker_with_intent_id
        self.dialogue_id_to_dialogue_acts = load_json(
            os.path.join(data_path, "dialog_acts.json")
        )

    def parse(self) -> Union[List[Any], Dict[Any, Any]]:
        output_dialogues = []
        for split in ("train", "test", "dev"):
            for dialogues_file in glob(os.path.join(self.data_path, split, "*.json")):
                dialogues_list = load_json(dialogues_file)
                for dialogue in dialogues_list:
                    output_dialogue = self._parse_dialogue(dialogue)
                    output_dialogues.append(output_dialogue)
        return output_dialogues

    def _parse_dialogue(self, dialogue: Dict[str, Any]) -> Dict[str, Any]:
        dialogue_id = dialogue["dialogue_id"]
        domains = dialogue["services"]
        turn_id_to_dialogue_acts = self.dialogue_id_to_dialogue_acts[dialogue_id]
        output_turns = self._parse_turns(
            turn_id_to_dialogue_acts=turn_id_to_dialogue_acts, turns=dialogue["turns"]
        )
        return {"dialogue_id": dialogue_id, "domains": domains, "turns": output_turns}

    def _parse_turns(
        self,
        turn_id_to_dialogue_acts: Dict[str, Dict[str, Any]],
        turns: List[Dict[Any, Any]],
    ) -> List[Dict[str, Any]]:
        output_turns = []
        for turn_id, turn in enumerate(turns):
            turn_id = turn["turn_id"]
            speaker_id = turn["speaker"]
            mapped_speaker_id = self.speaker_id_mapping[speaker_id]
            utterance = turn["utterance"]
            dialogue_acts = turn_id_to_dialogue_acts[turn_id]["dialog_act"]
            if speaker_id == self.speaker_with_intent_id:
                intents = self._extract_intents_from_frames(turn["frames"])
            else:
                intents = None
            output_dialogue_acts = list(dialogue_acts.keys())
            # This introduces the assumption that an utterance can be split
            # into tokens on the `UTTERANCE_SPLIT_CHARACTER` character. This
            # is to avoid proper tokenization at this stage, as it is a modelling
            # step. The same space character needs to later be used to join the
            # resulting tokens into an utterance string, before any further
            # tokenization is performed.
            tokens = utterance.split(UTTERANCE_SPLIT_CHARACTER)
            output_tokens = [init_token_dict(token=token) for token in tokens]
            output_turns.append(
                init_turn_dict(
                    turn_id=int(turn_id),
                    speaker_id=mapped_speaker_id,
                    utterance=utterance,
                    tokens=output_tokens,
                    dialogue_acts=output_dialogue_acts,
                    intents=intents,
                )
            )
        return output_turns

    def _extract_intents_from_frames(self, frames: List[Dict[str, Any]]) -> List[str]:
        """Extracts intents from frames. We skip slot extraction in multiWOZ, as
        these annotations are not readily available on the token-level for most slots
        (some of these can still be heuristically extracted, but that introduces more assumptions).
        If we decide to perform clustering using token-level annotations, this can be added later.
        """
        output_intents = []
        for frame in frames:
            intent = frame["state"]["active_intent"]
            if intent != self.no_active_intent_token:
                output_intents.append(intent)
        return output_intents