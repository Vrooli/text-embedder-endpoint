# Text Embedder Endpoint

This repository contains a Flask API endpoint for generating text embeddings from a Hugging Face model. The application is dockerized and is designed to be deployed using Docker Compose. It features Redis for caching embeddings to improve performance, and uses nginx-proxy for handling incoming requests.

## [👩🏼‍💻 Developer setup][setup-guide]
Learn how to setup the development workflow, and general development tips.

## Usage

Send a POST request to `http://<your-server-ip>:8000/embed` with a JSON body containing a `text` field. The application will return the embeddings for the text as a JSON response. For example:

```json
{
    "text": "Hello, world!"
}
```

## Notes

This is a basic setup and might need additional features like logging, error handling, environment-specific configurations, and authentication for a production setup. Also, ensure your server has enough resources (RAM, disk space) to host the model and perform inference.
