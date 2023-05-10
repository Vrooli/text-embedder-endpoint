import os
import logging
from flask import Flask, request, jsonify
from InstructorEmbedding import INSTRUCTOR
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

try:
    # Load the model
    logger.info('Loading model. This might take a while...')
    model = INSTRUCTOR('hkunlp/instructor-base')
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

@app.route('/embed', methods=['POST'])
def embed():
    instruction = request.json.get('instruction')
    sentence = request.json.get('sentence')

    # Get the embeddings
    embeddings = model.encode([[instruction, sentence]])

    # Convert tensor to list and return
    return jsonify(embeddings.tolist())

if __name__ == "__main__":
    try:
        port = os.environ['PORT_EMBEDDINGS']
        logger.info(f"Starting server on port {port}")
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
