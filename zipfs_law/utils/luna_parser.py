import glob
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from zipfs_law.constants import UTTERANCE_SPLIT_CHARACTER
from zipfs_law.utils.helpers import init_token_dict, init_turn_dict


class LunaParser:
    def __init__(
        self,
        data_path: str,
        include_low_grade_recordings: bool = True,
        speaker_id_mapping: Optional[Dict[str, str]] = None,
        dialogue_id_to_custom_speaker_id_mapping: Optional[
            Dict[str, Dict[str, str]]
        ] = None,
        genders: Optional[List[str]] = None,
    ):
        if not Path(data_path).is_dir():
            raise ValueError("LunaParser expects a data directory as input path.")
        self.data_path = data_path
        self.include_low_grade_recordings = include_low_grade_recordings
        if speaker_id_mapping is None:
            self.speaker_id_mapping = {
                "spk1": "AGENT",
                "spk2": "CLIENT",
                "spk3": "CLIENT",
            }
        else:
            self.speaker_id_mapping = speaker_id_mapping
        if dialogue_id_to_custom_speaker_id_mapping is None:
            self.dialogue_id_to_custom_speaker_id_mapping = dict()
        else:
            self.dialogue_id_to_custom_speaker_id_mapping = (
                dialogue_id_to_custom_speaker_id_mapping
            )
        if genders is None:
            self.genders = ["F", "M"]
        else:
            self.genders = genders

    def parse(self) -> Union[List[Any], Dict[Any, Any]]:
        output_dialogues = []
        grades = ["DOBRAJAKOSC"]
        if self.include_low_grade_recordings:
            grades.append("KIEPSKAJAKOSC")
        category_dirs = glob.glob(os.path.join(self.data_path, "*/"))
        for category_dir in category_dirs:
            category = Path(category_dir).name
            domains = [category]
            for grade in grades:
                for gender in self.genders:
                    recordings_dirs_dir = os.path.join(category_dir, grade, gender)
                    recordings_dirs = glob.glob(os.path.join(recordings_dirs_dir, "*/"))
                    for recording_dir in recordings_dirs:
                        recording_name = Path(recording_dir).stem
                        words = ET.parse(
                            os.path.join(recording_dir, f"{recording_name}_words.xml")
                        ).getroot()
                        turns = ET.parse(
                            os.path.join(recording_dir, f"{recording_name}_turns.xml")
                        ).getroot()
                        conversation = self._parse_recording(words=words, turns=turns)
                        turns = []
                        for turn_id, turn_dict in enumerate(conversation):
                            turn_dict["turn_id"] = turn_id
                            turns.append(
                                self._parse_turn_dict(
                                    turn_dict=turn_dict, dialogue_id=recording_name
                                )
                            )
                        dialogue = {
                            "dialogue_id": recording_name,
                            "domains": domains,
                            "turns": turns,
                        }
                        output_dialogues.append(dialogue)
        return output_dialogues

    def _parse_turn_dict(
        self, turn_dict: Dict[str, Union[str, int]], dialogue_id: str
    ) -> Dict[str, Any]:
        turn_id = turn_dict["turn_id"]
        if dialogue_id in self.dialogue_id_to_custom_speaker_id_mapping:
            speaker_id_mapping = self.dialogue_id_to_custom_speaker_id_mapping[
                dialogue_id
            ]
        else:
            speaker_id_mapping = self.speaker_id_mapping
        speaker_id = speaker_id_mapping[turn_dict["role"]]
        utterance = turn_dict["text"]
        tokens = []
        for token in utterance.split(UTTERANCE_SPLIT_CHARACTER):
            tokens.append(init_token_dict(token=token))
        return init_turn_dict(
            turn_id=turn_id, speaker_id=speaker_id, utterance=utterance, tokens=tokens
        )

    def _parse_recording(
        self, words: ET.ElementTree, turns: ET.ElementTree
    ) -> List[dict]:
        word_id_to_word = dict()
        for word in words:
            attributes = word.attrib
            word_id = int(attributes["id"])
            text = attributes["word"]
            word_id_to_word[word_id] = text
        turns_dicts = []
        for turn in turns:
            attributes = turn.attrib
            turn_id = attributes["id"]
            start_timestamp_ms = float(attributes["startTime"]) * 1000
            end_timestamp_ms = float(attributes["endTime"]) * 1000
            speaker_id = attributes["speaker"]
            words = attributes["words"]
            boundary_words = words.split("..")
            if "empty" in boundary_words:
                continue
            start_word_id, end_word_id = boundary_words[0], boundary_words[-1]
            start_word_id = int(start_word_id.split("_")[-1])
            end_word_id = int(end_word_id.split("_")[-1])
            text = []
            for word_id in range(start_word_id, end_word_id + 1):
                text.append(word_id_to_word[word_id])
            word_count = len(text)
            text = " ".join(text)
            turns_dicts.append(
                {
                    "turn_id": turn_id,
                    "role": speaker_id,
                    "start": start_timestamp_ms,
                    "end": end_timestamp_ms,
                    "word_count": word_count,
                    "text": text,
                }
            )
        return turns_dicts
