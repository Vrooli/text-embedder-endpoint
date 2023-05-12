import os
import hashlib
import json
import logging
from flask import Flask, request, jsonify, abort
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
    logger.info('Loading model...')
    model = INSTRUCTOR('hkunlp/instructor-base')
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None
logger.info('Model loaded!')

# If API_KEY environment variable is set, require it in the request headers
@app.before_request
def check_api_key():
    api_key = request.headers.get('key')
    if os.environ.get('API_KEY'):
        if not api_key:
            abort(401, 'API Key required')
        elif not api_key == os.environ.get('API_KEY'):
            abort(401, 'Invalid API Key')

@app.route('/', methods=['POST'])
def embed():
    instruction = request.json.get('instruction')
    sentences = request.json.get('sentences')

    all_embeddings = []
    for sentence in sentences:
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

        all_embeddings.extend(embeddings)

    return jsonify({"embeddings": all_embeddings, "model": "instructor-base"})

@app.route('/help', methods=['GET'])
def help():
    help_text = """
    To use this API, send a POST request to the root endpoint '/' with the following JSON body:

    {
      "instruction": "<your instruction here>",
      "sentences": ["sentence1", "sentence2", "..."]
    }

    The API will return a JSON with the embeddings for each sentence and the model name.

    For more information, check out the GitHub repository: https://github.com/Vrooli/text-embedder-endpoint
    """
    return jsonify({"Help": help_text})

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "healthy"})

try:
    port = os.environ['PORT_EMBEDDINGS']
    if os.environ.get('API_KEY'):
        logger.info(f"Starting server on port {port} in private mode")
    else:
        logger.info(f"Starting server on port {port} in public mode")
    if os.environ['FLASK_ENV'] == 'development':
        app.run(host='0.0.0.0', port=port)
except Exception as e:
    logger.error(f"Error starting server: {e}")