"""
This module serves as a Flask server that converts text to embeddings using the 
InstructorEmbedding model. The model reads sentences, converts them into embeddings 
and caches the results in Redis for fast retrieval. 
"""
import hashlib
import json
import logging
import os
import time

import redis
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request
from InstructorEmbedding import INSTRUCTOR

# Maximum number of sentences that can be processed at once
MAX_SENTENCES = 100

# Configure logging. Set to DEBUG for more verbose logging. Default is INFO.
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Connect to Redis
r = redis.Redis(host='redis', port=6379, db=0,
                decode_responses=True, password=os.environ.get('REDIS_PASS'))

try:
    # Load the model
    logger.info('Loading model...')
    model = INSTRUCTOR('hkunlp/instructor-base')
except Exception as e:
    logger.error("Error loading model: %s", e)
    model = None
logger.info('Model loaded!')


@app.before_request
def check_api_key():
    """
    Middleware that checks for an API key in the request headers before processing a request.
    If the key is not present or incorrect, the request is aborted.
    """
    api_key = request.headers.get('key', '')
    if os.environ.get('API_KEY', ''):
        if not api_key:
            abort(401, 'API Key required')
        elif not api_key == os.environ.get('API_KEY', ''):
            abort(401, 'Invalid API Key')


@app.route('/', methods=['POST'])
def embed():
    """
    Endpoint that processes POST requests to generate embeddings for a list of sentences using the
    InstructorEmbedding model. The embeddings are cached in Redis for future retrieval.
    """
    try:
        start_time = time.time()  # Record the start time

        instruction = request.json.get('instruction')
        sentences = request.json.get('sentences')

        # Check if the number of sentences exceeds the limit
        if len(sentences) > MAX_SENTENCES:
            return jsonify({"error": f"Too many sentences. The maximum is {MAX_SENTENCES}."}), 400

        all_embeddings = []
        for sentence in sentences:
            input_start_time = time.time()

            # Create a hash from the input
            input_hash = hashlib.sha256(
                f"{instruction}{sentence}".encode()).hexdigest()

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

            input_end_time = time.time()
            logger.debug(
                "Time for processing input '%s': %f seconds", sentence, (input_end_time - input_start_time))

            all_embeddings.extend(embeddings)

        end_time = time.time()  # Record the end time
        logger.debug(
            "Total time for embed function: %f seconds", (end_time - start_time))

        return jsonify({"embeddings": all_embeddings, "model": "instructor-base"})
    except Exception as e:
        logger.error("Error in embed function: %s", e)
        return jsonify({"error": "An error occurred during embedding. Please check your input and try again."}), 500


@app.route('/help', methods=['GET'])
def help():
    """
    Endpoint that processes GET requests to provide instructions on how to use the API.
    """
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
    """
    Endpoint that processes GET requests to check the health status of the server.
    """
    return jsonify({"status": "healthy"})


try:
    port = os.environ['VIRTUAL_PORT']
    if os.environ.get('API_KEY'):
        logger.info("Starting server on port %s in private mode", port)
    else:
        logger.info("Starting server on port %s in public mode", port)
    if os.environ['FLASK_ENV'] == 'development':
        app.run(host='0.0.0.0', port=port)
except Exception as e:
    logger.error("Error starting server: %s", e)
