import json
import os
from dataclasses import dataclass

from rat.io import Student, GenderVetoOption, StudentGender

@dataclass(frozen=True)
class Mapping:
    key_id: str
    key_submitdate: str
    key_first_name: str
    key_last_name: str
    key_gender: str
    key_veto_female: str
    key_veto_male: str
    key_veto_non_binary: str
    value_gender_map: dict
    value_no: str
    value_yes: str

NOT_AVAILABLE_STR = "N/A"

class SurveyParser:
    # result_question_codes.json mapping
    MAPPING_1 = Mapping(
        key_id="id",
        key_submitdate="submitdate",
        key_first_name="Q001[SQ001]",
        key_last_name="Q001[SQ002]",
        key_gender="Q002",
        key_veto_female="Q003[SQ003]",
        key_veto_male="Q003[SQ002]",
        key_veto_non_binary="Q003[SQ001]",
        value_gender_map={
            "Weiblich": StudentGender.FEMALE,
            "Männlich": StudentGender.MALE,
            "Divers": StudentGender.NON_BINARY
        },
        value_no="Nein",
        value_yes="Ja"
    )

    # result_default_settings.json mapping
    MAPPING_2 = Mapping(
        key_id="Antwort ID",
        key_submitdate="Datum Abgeschickt",
        key_first_name="Bitte geben Sie Ihren Vor- und Nachnamen an. [Vorname]",
        key_last_name="Bitte geben Sie Ihren Vor- und Nachnamen an. [Nachname]",
        key_gender="Mit welchem Geschlecht identifizieren Sie sich?",
        key_veto_male="Welche Geschlechter sind Sie nicht in der Lage zu spielen? [M\u00e4nnlich]",
        key_veto_female="Welche Geschlechter sind Sie nicht in der Lage zu spielen? [Weiblich]",
        key_veto_non_binary="Welche Geschlechter sind Sie nicht in der Lage zu spielen? [Divers]",
        value_gender_map={
            "Weiblich": StudentGender.FEMALE,
            "Männlich": StudentGender.MALE,
            "Divers": StudentGender.NON_BINARY
        },
        value_no="Nein",
        value_yes="Ja"
    )

    MAPPINGS = [MAPPING_1, MAPPING_2]

    def __init__(self, file_path: str):
        self._file_path: str = file_path
        self._mapping_used: Mapping

    def load_and_parse(self) -> set[Student]:
        """Loads and parses the JSON survey data."""
        if not os.path.exists(self._file_path):
            raise Exception(f"File {self._file_path} not found")
        
        try:
            with open(self._file_path, 'r', encoding='utf-8') as file:
                ls_data = json.load(file)
            
            # loading LimeSurvey JSON structure
            # next step unloading nested 'responses' key
            responses: list[dict] = ls_data.get("responses", ls_data) if isinstance(ls_data, dict) else ls_data

            if len(responses) < 1:
                return set()
            
            # finding out mapping to use
            if not self.try_detect_mapping(responses[0]):
                raise Exception("Unknown survey format")

            students = set()
            for entry in responses:                
                # skip unfinished responses
                if not entry[self._mapping_used.key_submitdate]:
                    continue

                # determining veto options
                veto_m = True if entry.get(self._mapping_used.key_veto_male) == self._mapping_used.value_yes else False
                veto_f = True if entry.get(self._mapping_used.key_veto_female) == self._mapping_used.value_yes else False
                veto_nb = True if entry.get(self._mapping_used.key_veto_non_binary) == self._mapping_used.value_yes else False

                veto_option = GenderVetoOption.NO_VETOES # default no vetoes
                if veto_m and not veto_f and not veto_nb:
                    veto_option=GenderVetoOption.MALE_ONLY
                elif not veto_m and veto_f and not veto_nb: 
                    veto_option=GenderVetoOption.FEMALE_ONLY
                elif not veto_m and not veto_f and veto_nb: 
                    veto_option=GenderVetoOption.NON_BINARY_ONLY
                elif veto_m and veto_f and not veto_nb: 
                    veto_option=GenderVetoOption.FEMALE_AND_MALE
                elif veto_m and not veto_f and veto_nb: 
                    veto_option=GenderVetoOption.MALE_AND_NON_BINARY
                elif not veto_m and veto_f and veto_nb: 
                    veto_option=GenderVetoOption.FEMALE_AND_NON_BINARY
                
                # parsing the survey data into student objects
                student_new = Student(
                    last_name=entry.get(self._mapping_used.key_last_name, NOT_AVAILABLE_STR),
                    first_name=entry.get(self._mapping_used.key_first_name, NOT_AVAILABLE_STR),
                    id=entry.get(self._mapping_used.key_id, -1),
                    gender=self._mapping_used.value_gender_map[entry.get(self._mapping_used.key_gender, NOT_AVAILABLE_STR)],
                    gender_veto_option=veto_option,
                )

                students.add(student_new)
            return students
        except Exception as e:
            raise Exception(f"Parsing error: {e}")

    def try_detect_mapping(self, example_response: dict) -> bool:
        for mapping in self.MAPPINGS:
            if mapping.key_id in example_response:
                self._mapping_used = mapping
                return True
        return False
