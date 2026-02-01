from flask import Flask, render_template, request, jsonify
import json, os, random, string

app = Flask(__name__)

DB_PATH = "database.json"
def load_db():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

def find_user_by_name(name):
    db = load_db()
    for u in db["users"]:
        if u["name"].lower() == name.lower():
            return u
    return None


def get_patient_profile(user_id):
    db = load_db()
    for p in db["patient_profile"]:
        if p["user_id"] == user_id:
            return p
    return None


def get_patient_info_by_name(name):
    user = find_user_by_name(name)
    if not user:
        return None

    profile = get_patient_profile(user["user_id"])
    if not profile:
        return None

    return {
        "name": user["name"],
        "age": profile["age"],
        "gender": profile["gender"],
        "contact": profile["contact_no"]
    }


def extract_name(text):
    db = load_db()
    names = [u["name"].lower() for u in db["users"]]

    for w in text.split():
        if w.lower() in names:
            return w.title()
    return None


#                   ALL PATIENTS LIST

def get_all_patients():
    db = load_db()
    output = "All Patients\n------------\n"

    for index, user in enumerate(db["users"], start=1):
        profile = get_patient_profile(user["user_id"])
        if profile:
            output += (
                f"{index}.\n"
                f"  Name: {user['name']}\n"
                f"  Age: {profile['age']}\n"
                f"  Gender: {profile['gender']}\n"
                f"  Contact: {profile['contact_no']}\n\n"
            )

    return output




#                 PRESCRIPTIONS & MEDICINES


def get_prescriptions_by_patient(patient_id):
    db = load_db()
    return [p for p in db["prescriptions"] if p["patient_id"] == patient_id]


def get_medicines_by_prescription(prescription_id):
    db = load_db()
    return [m for m in db["prescription_medicines"] if m["prescription_id"] == prescription_id]


def add_medicine_to_patient(name, med_name, time):
    db = load_db()
    user = find_user_by_name(name)

    if not user:
        return f"No profile found for {name}."

    patient = get_patient_profile(user["user_id"])
    prescriptions = get_prescriptions_by_patient(patient["patient_id"])

    if not prescriptions:
        new_id = len(db["prescriptions"]) + 1
        db["prescriptions"].append({
            "prescription_id": new_id,
            "patient_id": patient["patient_id"],
            "doctor_id": None,
            "notes": "Auto-created prescription",
            "created_date": "2026-01-01"
        })
        prescription_id = new_id
    else:
        prescription_id = prescriptions[0]["prescription_id"]

    db["prescription_medicines"].append({
        "medicine_id": len(db["prescription_medicines"]) + 1,
        "prescription_id": prescription_id,
        "medicine_name": med_name,
        "dosage": "1 tablet",
        "frequency": "Once",
        "timing": time,
        "duration_days": 1
    })

    save_db(db)
    return f"Saved! Added {med_name} for {name} at {time}."


def get_next_dose(name):
    user = find_user_by_name(name)
    if not user:
        return f"No profile found for {name}."

    patient = get_patient_profile(user["user_id"])
    prescriptions = get_prescriptions_by_patient(patient["patient_id"])

    if not prescriptions:
        return f"No prescription found for {name}."

    meds = get_medicines_by_prescription(prescriptions[0]["prescription_id"])
    if not meds:
        return f"No medicines found for {name}."

    reply = f"Here are {name}'s medicines:\n"
    for m in meds:
        reply += f"- {m['medicine_name']} at {m['timing']}\n"

    return reply



#                   INTENT MATCHING


with open("intents.json", "r") as f:
    intents = json.load(f)


def tokenize(sentence):
    sentence = sentence.lower()
    sentence = sentence.translate(str.maketrans("", "", string.punctuation))
    return sentence.split()


def word_similarity(w1, w2):
    return w1.startswith(w2[:2]) or w2.startswith(w1[:2])



#                MAIN CHATBOT LOGIC

def get_response(user_input):
    text = user_input.lower()

    #            REMEDIES FIRST (to avoid conflicts)
    if "cough" in text or "cold" in text or "fever" in text or "headache" in text \
       or "stomach" in text or "burn" in text or "cut" in text:
        # Let intent system handle the correct specific remedy
        pass

    #            PATIENT COUNT
    if "how many patients" in text or "total patients" in text or "number of patients" in text:
        db = load_db()
        total = len(db["users"])
        return f"There are currently {total} patients registered in the system."

    #            ALL PATIENTS LIST
    if "all patients" in text:
        return get_all_patients()

    #            PATIENT PROFILE
    if "profile" in text or "details" in text:
        name = extract_name(text)
        if not name:
            return "Please specify the patient's name."

        info = get_patient_info_by_name(name)
        if not info:
            return f"No profile found for {name}."

        return (
            "Patient Profile\n"
            "---------------\n"
            f"Name: {info['name']}\n"
            f"Age: {info['age']}\n"
            f"Gender: {info['gender']}\n"
            f"Contact: {info['contact']}"
        )

    #            CONTACT NUMBER
    if "contact" in text.split():
        name = extract_name(text)
        if not name:
            return "Please specify the patient's name."

        info = get_patient_info_by_name(name)
        return f"{name}'s Contact Number: {info['contact']}"

    #            AGE
    if "age" in text:
        name = extract_name(text)
        info = get_patient_info_by_name(name)
        return f"{name}'s Age: {info['age']}"

    #            GENDER
    if "gender" in text:
        name = extract_name(text)
        info = get_patient_info_by_name(name)
        return f"{name}'s Gender: {info['gender']}"

    #            ADD MEDICINE
    if "add" in text and "at" in text:
        try:
            name = extract_name(text)
            med = text.split("add")[1].split("at")[0].strip().title()
            time = text.split("at")[1].strip()
            return add_medicine_to_patient(name, med, time)
        except:
            return "Use: add Paracetamol at 6 PM for Sasmita"

    #            NEXT DOSE
    if "next dose" in text or "next medicine" in text:
        name = extract_name(text)
        return get_next_dose(name)

    #            INTENT MATCHING
    user_tokens = tokenize(user_input)
    best, best_score = None, 0

    for intent in intents["intents"]:
        for p in intent["patterns"]:
            pattern_words = tokenize(p)
            score = 0

            for pw in pattern_words:
                for uw in user_tokens:
                    if pw == uw or word_similarity(pw, uw):
                        score += 1

            if score > best_score:
                best_score = score
                best = intent

    if best and best_score > 0:
        resp = random.choice(best["responses"])
        return resp

    return "Sorry, I didn't understand that."



#                   FLASK ROUTES

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json["message"]
    reply = get_response(msg)
    return jsonify({"reply": reply})


#                   RUN SERVER

if __name__ == "__main__":
    app.run(debug=True)
