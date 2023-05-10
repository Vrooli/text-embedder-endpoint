import os
import redis
from flask import Flask, request, jsonify
from InstructorEmbedding import INSTRUCTOR
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load the model
model = INSTRUCTOR('hkunlp/instructor-base')

@app.route('/embed', methods=['POST'])
def embed():
    instruction = request.json.get('instruction')
    sentence = request.json.get('sentence')

    # Get the embeddings
    embeddings = model.encode([[instruction, sentence]])

    # Convert tensor to list and return
    return jsonify(embeddings.tolist())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ['PORT_EMBEDDINGS'])