import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv() # We are not using this


app = Flask(__name__)

# Initialize the Groq client
# client = Groq(api_key=GROQ_API_KEY)
# print(f"Loaded API Key: {GROQ_API_KEY}")
client = Groq(
    api_key="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",  # Here I pasted an API key to use Groq AI
)

# Render the index.html file (main page)
@app.route("/")
def index():
    return render_template("index.html") 


# process the text input and send it to Groq API for evaluation
@app.route("/evaluate", methods=["POST"])
def evaluate_text():
    # get the user text from the textbox
    data = request.get_json()
    user_text = data.get("text")

    # if there is no text print this
    if not user_text:
        return jsonify({"feedback": "Text is required for evaluation."}), 400

    try:
        # Groq API request
        # It will say to Groq to be an evaluator
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an evaluator using the 6P method "
                        "(Certainty, Variation, Connectedness, Significance, Contrubutions, and Growth). "
                         "Provide constructive feedback based on this method. The desired values are: Certainty = 40 percent, Variation = 25 percent, Connectedness = 15 percent, Significance = 10 percent, Contrubutions = 6 percent, and Growth = 4 percent ."
                    ),
                },
                {"role": "user", "content": user_text},
            ],
        )

        # Extract feedback from the API response
        feedback = response.choices[0].message.content
        return jsonify({"feedback": feedback})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"feedback": "Failed to evaluate text. Please try again."}), 500


if __name__ == "__main__":
    app.run(debug=True)
