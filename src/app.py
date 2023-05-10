import os
import hashlib
import json
import logging
from flask import Flask, request, jsonify
from InstructorEmbedding import INSTRUCTOR
from dotenv import load_dotenv
import redis

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Connect to Redis
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

try:
    # Load the model
    logger.info('Loading model. This might take a while...')
    model = INSTRUCTOR('hkunlp/instructor-base')
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None
logger.info('Model loaded!')

@app.route('/embed', methods=['POST'])
def embed():
    instruction = request.json.get('instruction')
    sentence = request.json.get('sentence')

    # Create a hash from the input
    input_hash = hashlib.sha256(f"{instruction}{sentence}".encode()).hexdigest()

    # Check if Redis has a key with that hash
    if r.exists(input_hash):
        # If so, use that data
        embeddings = json.loads(r.get(input_hash))
    else:
        # If not, compute the embeddings
        embeddings = model.encode([[instruction, sentence]])

        # Convert tensor to list
        embeddings = embeddings.tolist()

        # Store the embeddings in Redis
        r.set(input_hash, json.dumps(embeddings))

        # Set a reasonable expiry time if you want to delete old data
        # Here, for example, 24 hours (86400 seconds)
        r.expire(input_hash, 86400)

    return jsonify(embeddings)

try:
    port = os.environ['PORT_EMBEDDINGS']
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
except Exception as e:
    logger.error(f"Error starting server: {e}")
