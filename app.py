from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Default JSONL file
jsonl_file = "chat_data.jsonl"

# Load responses with a guaranteed fallback
responses = {"": "I don’t get it"}  # Default fallback
if os.path.exists(jsonl_file):
    with open(jsonl_file, "r") as f:
        for line in f:
            data = json.loads(line.strip())
            responses[data["prompt"].lower()] = data["response"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.form.get("message", "").lower()
    if not msg:
        return jsonify({"user": "", "bot": "Say something!"}), 400
    reply = responses.get(msg, responses[""])
    return jsonify({"user": msg, "bot": reply})

@app.route("/upload", methods=["POST"])
def upload():
    global responses
    if "file" not in request.files:
        return jsonify({"status": "No file sent"}), 400
    file = request.files["file"]
    if not file or not file.filename.endswith(".jsonl"):
        return jsonify({"status": "Invalid file—use .jsonl"}), 400
    try:
        file.save(jsonl_file)
        responses = {"": "I don’t get it"}  # Reset with fallback
        with open(jsonl_file, "r") as f:
            for line in f:
                data = json.loads(line.strip())
                responses[data["prompt"].lower()] = data["response"]
        return jsonify({"status": "JSONL loaded!"})
    except Exception as e:
        return jsonify({"status": f"Error: {str(e)}"}), 500

@app.route("/train", methods=["POST"])
def train():
    prompt = request.form.get("prompt", "").lower()
    response = request.form.get("response", "")
    if prompt and response:
        responses[prompt] = response
        with open(jsonl_file, "a") as f:
            f.write(json.dumps({"prompt": prompt, "response": response}) + "\n")
        return jsonify({"status": f"Trained: '{prompt}' -> '{response}'"})
    return jsonify({"status": "Missing input"}), 400

if __name__ == "__main__":
    app.run(debug=True)