import os
from flask import Flask, render_template, request, Response, session
from anthropic import Anthropic
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

client = Anthropic()
MODEL = "claude-haiku-4-5"


@app.route("/")
def index():
    session.setdefault("messages", [])
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return {"error": "Empty message"}, 400

    session.setdefault("messages", [])
    session["messages"].append({"role": "user", "content": user_message})
    session.modified = True

    messages_snapshot = list(session["messages"])

    def generate():
        full_response = ""
        with client.messages.stream(
            model=MODEL,
            max_tokens=1024,
            messages=messages_snapshot,
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                yield f"data: {json.dumps({'text': text})}\n\n"

        session["messages"].append({"role": "assistant", "content": full_response})
        session.modified = True
        yield "data: [DONE]\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/reset", methods=["POST"])
def reset():
    session["messages"] = []
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
