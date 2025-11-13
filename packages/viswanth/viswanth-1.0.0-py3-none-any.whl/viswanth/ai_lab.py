# === Conversational AI Combined Experiments 7, 8, 9, 10 ===
# Author: Viswanth S S
# Works offline on Jupyter / Anaconda / Lab systems

from flask import Flask, request, jsonify
from nltk.chat.util import Chat, reflections
from werkzeug.serving import run_simple
import pyttsx3, sqlite3
from datetime import datetime

app = Flask(__name__)
engine = pyttsx3.init()

# Create Databases
sqlite3.connect('classroom.db').execute(
    "CREATE TABLE IF NOT EXISTS discussions(id INTEGER PRIMARY KEY, question TEXT, reply TEXT)"
).close()
sqlite3.connect('medical.db').execute(
    "CREATE TABLE IF NOT EXISTS diagnoses(id INTEGER PRIMARY KEY, symptoms TEXT, diagnosis TEXT)"
).close()

# Common Medical dictionary
symptom_diagnosis = {
    "fever": "Possible Flu or Viral Infection",
    "cough": "Respiratory Infection or Cold",
    "headache": "Migraine or Stress",
    "fatigue": "Anemia or Exhaustion",
    "sore throat": "Tonsillitis or Throat Infection"
}

# Common Voice speaking function
def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except:
        pass

# ----------------- EXPERIMENT 7: GENERIC CHATBOT -----------------
def exp7():
    pairs = [
        (r"hi|hello|hey", ["Hello! How can I assist you?"]),
        (r"what is your name", ["I am a generic chatbot."]),
        (r"how are you", ["I am functioning as expected!"]),
        (r"bye", ["Goodbye! Have a nice day!"])
    ]
    chatbot = Chat(pairs, reflections)

    @app.route("/chatbot", methods=["POST"])
    def chatbot_api():
        user_input = request.json.get("message", "")
        reply = chatbot.respond(user_input)
        speak(reply)
        return jsonify({"response": reply or "I didn't understand that."})

# ----------------- EXPERIMENT 8: VOICE BOT -----------------
def exp8():
    @app.route("/voice", methods=["POST"])
    def voice_bot():
        user_input = request.json.get("message", "").lower()
        if "hello" in user_input:
            reply = "Hello! How can I help you?"
        elif "time" in user_input:
            reply = f"The current time is {datetime.now().strftime('%H:%M:%S')}"
        elif "bye" in user_input:
            reply = "Goodbye!"
        else:
            reply = "I am your voice assistant."
        speak(reply)
        return jsonify({"response": reply})

# ----------------- EXPERIMENT 9: CLASSROOM BOT -----------------
def exp9():
    @app.route("/classroom", methods=["POST"])
    def classroom_bot():
        msg = request.json.get("message", "").lower()
        if "assignment" in msg:
            reply = "Assignments are due on Friday."
        elif "topic" in msg or "lecture" in msg:
            reply = "Today's topic is Natural Language Processing."
        else:
            reply = "I will get back to you on that."
        sqlite3.connect("classroom.db").execute(
            "INSERT INTO discussions(question, reply) VALUES(?,?)", (msg, reply)
        ).close()
        speak(reply)
        return jsonify({"response": reply})

# ----------------- EXPERIMENT 10: MEDICAL BOT -----------------
def exp10():
    @app.route("/medical", methods=["POST"])
    def medical_bot():
        msg = request.json.get("symptoms", "").lower()
        reply = "Consult a doctor for detailed diagnosis."
        for s, d in symptom_diagnosis.items():
            if s in msg:
                reply = d
                break
        sqlite3.connect("medical.db").execute(
            "INSERT INTO diagnoses(symptoms, diagnosis) VALUES(?,?)", (msg, reply)
        ).close()
        speak(reply)
        return jsonify({"response": reply})

# ----------------- RUN FUNCTION -----------------
def run_experiment(exp_no):
    if exp_no == "7":
        exp7()
    elif exp_no == "8":
        exp8()
    elif exp_no == "9":
        exp9()
    elif exp_no == "10":
        exp10()
    else:
        print("Invalid experiment number.")
        return
    run_simple("localhost", 5000, app, use_reloader=False)

# ----------------- PRINT FUNCTION -----------------
def show_code():
    print(open(__file__).read())
