import json
import os

from io.__init__ import Student

class survey_parser:
    def __init__(self, file_path):
        self.file_path = file_path

        self.parsed_data = []

        # result question codes.json mapping
        self.column_map_1 = {
            "id"    : "Teilnehmer_ID",
            "Q001[SQ001]": "Vorname",
            "Q001[SQ002]": "Nachname",
            "Q002" : "Selbs_zugeschriebenes_Geschlecht",
            "Q003[SQ001]": "Maennlich",
            "Q003[SQ002]": "Weiblich",
            "Q003[SQ003]": "Divers",
            "seed"  : "Zufallsstartwert",
        }
        # result default settings.json mapping
        self.column_map_2 = {
            "Antwort ID": "Teilnehmer_ID",
            "Bitte geben Sie Ihren Vor- und Nachnamen an. [Vorname]": "Vorname",
            "Bitte geben Sie Ihren Vor- und Nachnamen an. [Nachname]": "Nachname",
            "Mit welchem Geschlecht identifizieren Sie sich?": "Selbs_zugeschriebenes_Geschlecht",
            "Welche Geschlechter sind Sie nicht in der Lage zu spielen? [M\u00e4nnlich]": "Maennlich",
            "Welche Geschlechter sind Sie nicht in der Lage zu spielen? [Weiblich]": "Weiblich",
            "Welche Geschlechter sind Sie nicht in der Lage zu spielen? [Divers]": "Divers",
            "Zufallsstartwert": "Zufallsstartwert",
        }
        # add more mappings as needed

    def load_and_parse(self):
        """Loads and parses the JSON survey data."""
        if not os.path.exists(self.file_path):
            print(f"Error: {self.file_path} not found.")
            return False
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                ls_data = json.load(file)
            # loading LimeSurvey JSON structure
            # next step unloading nested 'responses' key
            responses = ls_data.get("responses", ls_data) if isinstance(ls_data, dict) else ls_data
            
            # finding out which column map to use
            sample_entry = responses[0] if len(responses) > 0 else {}
            match sample_entry:
                case {"Antwort ID": _}:
                    self.column_map_used = self.column_map_2
                case {"id": _}:
                    self.column_map_used = self.column_map_1
                case _:
                    return "Parsing error: Unknown survey format."

            for entry in responses:
                # determining veto options
                veto_m = True if entry.get(self.column_map_used[4], "Nein") == "Ja" else False,
                veto_f = True if entry.get(self.column_map_used[5], "Nein") == "Ja" else False,
                veto_nb = True if entry.get(self.column_map_used[6], "Nein") == "Ja" else False,
                
                veto_option = "6" # default no vetoes
                if veto_m and not veto_f and not veto_nb:
                    veto_option="1" # male
                elif not veto_m and veto_f and not veto_nb: 
                    veto_option="2" # female
                elif not veto_m and not veto_f and veto_nb: 
                    veto_option="0" # non-binary
                elif veto_m and not veto_f and veto_nb: 
                    veto_option="3" # male and non-binary
                elif not veto_m and veto_f and veto_nb: 
                    veto_option="4" # female and non-binary

                # parsing the survey data into student objects
                student_new = Student(
                    
                    last_name=entry.get(self.column_map_used[2], "N/A"),
                    first_name=entry.get(self.column_map_used[1], "N/A"),
                    id=entry.get(self.column_map_used[0], -1),
                    gender=entry.get(self.column_map_used[3], "N/A"),
                    gender_veto_option=veto_option,
                )
                # checking if student already exists in parsed data
                if any(s.last_name == student_new.last_name and s.first_name == student_new.first_name for s in self.parsed_data):
                    # old entry will be deleted
                    self.parsed_data.pop(
                        self.parsed_data.index(
                            next(
                                    s for s in self.parsed_data if s.last_name == student_new.last_name and s.first_name == student_new.first_name
                                )
                            )
                        )
                # putting students into the parsed data list
                self.parsed_data.append(student_new)

            return f"Parsed {len(self.parsed_data)} survey responses."
        except Exception as e:
            return f"Parsing error: {e}"
        
    def show_parsed_data(self):
        """Displays the parsed survey data."""
        for i, entry in enumerate(self.parsed_data):
            print(f"Response #{i}: {entry}")

#if __name__ == "__main__":
#    parser = survey_parser("test_data/result_default_settings.json")
#    result = parser.load_and_parse()
#    print(result)
#    parser.show_parsed_data()


    

