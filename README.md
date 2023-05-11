# Ready-to-Use Text Embedding API
This repository contains a simple Flask API for generating text embeddings from the [instructor-embedding](https://github.com/HKUNLP/instructor-embedding) base model. As of 2023-05-11, this model is 6th on the [Massive Text Embedding Benchmark (MTEB) Leaderboard](https://huggingface.co/spaces/mteb/leaderboard). The application is dockerized and is designed to be deployed using Docker Compose. It features Redis for caching embeddings to improve performance, and uses nginx-proxy for handling incoming requests.

## [👩🏼‍💻 Developer setup][setup-guide]
Here is our setup guide for setting up, developing with, and deploying all Vrooli repos. The setup is almost identical for this repo, but with even less steps.

### Minimum requirements for Virtual Private Server (VPS)
- Memory: 2GB  
- CPUs: 1

## Usage
Send a POST request to `http://localhost:<PORT_EMBEDDING>/embed` if testing locally, or `https://<your-domain>/embed` if testing on a Virtual Private Server (VPS). The request must contain the following structure:

```json
{
    "instruction": "Hello, world!",
    "sentence": "The text you are creating an embedding for"
}
```

Feel free to change `instruction` depending on your specific use case. If you are embedding multiple fields at once, you'll have to convert the fields to a single string. One way to do is is by using yaml:

```yaml
title: "The title with characters escaped correctly"
description: "the description with characters escaped correctly"
```

## Notes
This is a basic setup and might need additional features like logging, error handling, environment-specific configurations, and authentication for a production setup. Also, ensure your server has enough resources (RAM, disk space) to host the model and perform inference.


[setup-guide]: https://github.com/MattHalloran/ReactGraphQLTemplate#how-to-start
