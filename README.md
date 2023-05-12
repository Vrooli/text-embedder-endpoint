# Ready-to-Use Text Embedding API
This repository contains a simple Flask API for generating text embeddings from the [instructor-embedding](https://github.com/HKUNLP/instructor-embedding) base model. As of 2023-05-11, this model is 6th on the [Massive Text Embedding Benchmark (MTEB) Leaderboard](https://huggingface.co/spaces/mteb/leaderboard). The application is dockerized and is designed to be deployed using Docker Compose. It features Redis for caching embeddings to improve performance, and uses nginx-proxy for handling incoming requests.

## [👩🏼‍💻 Developer setup][setup-guide]
Linked is our guide for setting up all Vrooli repos. No extra steps are required.

### Minimum requirements for Virtual Private Server (VPS)
- Memory: 2GB  
- CPUs: 1

## Usage
Send a POST request to `http://localhost:<PORT_EMBEDDING>` if testing locally, or `https://<your-domain>` if testing on a Virtual Private Server (VPS). The request must contain the following structure:

```json
{
    "key": "<your-api-key>", // Only if API_KEY environment variable is set
    "instruction": "Hello, world!",
    "sentences": ["First text you are creating an embedding for", "Another text that needs embeddings"]
}
```

As a curl request, it looks like this:

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -H "key: <your_api_key>" \
     -d '{"instruction":"Hello, world!", "sentences": ["First text you are creating an embedding for", "Another text that needs embeddings"]}' \
     http://localhost:3369
```

If you are authenticated, it will return an object of this shape:

```
{
    "embeddings": [[0.5000, 0.3456, ..., 0.1234]], // 768-dimensional vector for each sentence
    "model": "instructor-embedding",
}
```

Feel free to change `instruction` depending on your specific use case. If you are embedding multiple fields at once, you'll have to convert the fields to a single string. One way to do is is by using yaml:

```yaml
title: "The title with characters escaped correctly"
description: "the description with characters escaped correctly"
```

## License
This project is licensed under the terms of the GNU General Public License v3.0. You can check out the full license in the [LICENSE](./LICENSE) file.

This project uses the unmodified [instructor-embedding](https://github.com/HKUNLP/instructor-embedding) base model, which is licensed under Apache License 2.0. The license for this model can be found in the [LICENSE.instructor-embedding](./LICENSE.instructor-embedding) file.

## Contributions
Contributions are always welcome! If you have suggestions for improvements, please create an issue or a pull request💖


[setup-guide]: https://docs.vrooli.com/setup/getting_started.html
