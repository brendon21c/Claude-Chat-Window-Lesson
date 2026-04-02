import os
from flask import Flask, render_template, request, Response, session
from anthropic import Anthropic
from dotenv import load_dotenv
import json

# Load environment variables from .env (including ANTHROPIC_API_KEY)
load_dotenv()

app = Flask(__name__)

# Required by Flask to sign session cookies — randomized on each server start,
# which means sessions are cleared whenever the server restarts.
app.secret_key = os.urandom(24)

# Anthropic client picks up ANTHROPIC_API_KEY from the environment automatically
client = Anthropic()

# The model to use for all chat requests.
# claude-haiku-4-5 is the fastest and cheapest — good for learning and prototyping.
MODEL = "claude-haiku-4-5"


@app.route("/")
def index():
    # Initialize an empty message history in the session if this is a new visitor
    session.setdefault("messages", [])
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    # Pull the user's message out of the JSON body sent by the frontend
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return {"error": "Empty message"}, 400

    # Add the user's message to the conversation history stored in the session
    session.setdefault("messages", [])
    session["messages"].append({"role": "user", "content": user_message})
    session.modified = True  # Tell Flask the session changed so it saves it

    # Take a snapshot of the history before streaming starts.
    # This prevents race conditions if the session is modified mid-stream.
    messages_snapshot = list(session["messages"])

    def generate():
        """
        Generator function that streams Claude's response back to the browser
        using Server-Sent Events (SSE). Each chunk is sent as soon as it arrives
        from the API, so the user sees words appearing in real time.
        """
        full_response = ""

        # Open a streaming connection to the Anthropic API
        with client.messages.stream(
            model=MODEL,
            max_tokens=1024,
            messages=messages_snapshot,
        ) as stream:
            # Yield each text chunk as an SSE event the moment it arrives
            for text in stream.text_stream:
                full_response += text
                yield f"data: {json.dumps({'text': text})}\n\n"

        # Once streaming is complete, save Claude's full reply to the session
        # so it's included in the next API call (maintaining conversation context)
        session["messages"].append({"role": "assistant", "content": full_response})
        session.modified = True

        # Send a sentinel event so the frontend knows the stream is finished
        yield "data: [DONE]\n\n"

    # Return the generator as a streaming HTTP response using the SSE MIME type
    return Response(generate(), mimetype="text/event-stream")


@app.route("/reset", methods=["POST"])
def reset():
    # Clear the conversation history — called when the user clicks "New conversation"
    session["messages"] = []
    return {"status": "ok"}


if __name__ == "__main__":
    # debug=True enables auto-reload on file changes and shows detailed error pages
    app.run(debug=True)
