import json
import random
import string

patients = {
    "total_patients": 42,
    "active_patients": 35
}

prescriptions = {
    "total_prescriptions": 120
}

medications = {
    "most_prescribed": "Paracetamol"
}

with open("intents.json") as file:
    data = json.load(file)

def tokenize(sentence):
    sentence = sentence.lower()
    sentence = sentence.translate(str.maketrans("", "", string.punctuation))
    return sentence.split()

def get_response(user_input):
    user_tokens = tokenize(user_input)

    best_match = None
    max_match_count = 0

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            pattern_tokens = tokenize(pattern)

            match_count = sum(
                1 for word in pattern_tokens if word in user_tokens
            )

            if match_count > max_match_count:
                max_match_count = match_count
                best_match = intent

    if best_match:
        response = random.choice(best_match["responses"])
        response = response.format(
            total_patients=patients["total_patients"],
            active_patients=patients["active_patients"],
            total_prescriptions=prescriptions["total_prescriptions"],
            most_prescribed=medications["most_prescribed"]
        )
        return response

    return "Sorry, I didn't understand that. Can you please rephrase?"

print("Medication Tracker Chatbot (type 'quit' to stop)")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("Bot: Take care! Stay healthy.")
        break

    print("Bot:", get_response(user_input))
