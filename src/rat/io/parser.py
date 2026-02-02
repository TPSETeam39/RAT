import json
import os

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
            if "Antwort ID" in sample_entry:
                self.column_map_used = self.column_map_2
            else:
                self.column_map_used = self.column_map_1

            for entry in responses:
                #extract only the keys we care about
                filtered_entry = {
                    # KNF Key NOT FOUND DEBUG PRINT in case of missing keys, check mapping correctness
                    self.column_map_used[k]: entry.get(k, "KNF")
                    for k in self.column_map_used
                }
                self.parsed_data.append(filtered_entry)

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


    

