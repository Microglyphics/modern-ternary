import json
import random

class QuestionManager:
    def __init__(self, json_file_path):
        # Load questions and responses from a JSON file
        with open(json_file_path, "r") as file:
            self.data = json.load(file)["questions"]

    def get_all_question_keys(self):
        # Return a list of question keys (Q1, Q2, etc.)
        return list(self.data.keys())

    def get_question_text(self, q_key):
        # Get the question text for a given question key
        return self.data[q_key]["text"]

    def get_responses(self, q_key):
        """
        Returns the list of responses for a given question key.
        Extracts 'r_value' from the 'id' field.
        """
        return [
            {
                "text": response["text"],
                "r_value": int(response["id"].split("R")[1]),  # Extract R-value
                "scores": response["scores"]
            }
            for response in self.data[q_key]["responses"]
        ]

    def get_randomized_responses(self, q_key, session_state):
        """
        Randomize responses for a given question key, keeping the first response static.
        Ensure responses include 'r_value' fields.
        """
        responses = self.get_responses(q_key)  # Get raw responses
        top_option = {"text": "Please select a response", "r_value": None}
        if f"{q_key}_randomized" not in session_state:
            randomized_responses = responses.copy()
            random.shuffle(randomized_responses)
            session_state[f"{q_key}_randomized"] = [top_option] + randomized_responses

        return session_state[f"{q_key}_randomized"]