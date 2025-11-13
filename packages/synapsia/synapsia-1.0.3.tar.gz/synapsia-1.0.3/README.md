# SynapsIA ✍️

**SynapsIA** is the digital scribe of the new era. Its name comes from the fusion of **Synapse**, the neural connections where knowledge resides, and **AI**, the intelligence that brings it to life.

It is not a simple reader; it is a craftsman of knowledge. Just as an ancient scribe forged texts that would last for centuries, **SynapsIA** ingests your documents and forges an intricate network of synaptic connections. The result is a coherent, living digital mind, ready to be interrogated by other AI systems.

> **SynapsIA: Forging knowledge, one synapse at a time.**

---

## 🚀 Features

* **Ollama-Powered:** Leverages local Ollama services for all embedding tasks, keeping your data private.
* **RAG-Ready:** Processes your documents into a persistent, optimized vector index, creating the "knowledge base" for any RAG application (like [Kondoo](https://github.com/sysadminctl-services/kondoo)).
* **Tunable Ingestion:** Provides fine-grained control over `chunk-size` and `chunk-overlap` so you can optimize your knowledge base for Q&A, summarization, or other tasks.
* **Built-in Query Tool:** Includes a companion script, `synapsia_query.py`, to immediately test and debug your new knowledge base with your local LLMs.

## ⚡ Prerequisites

Before you begin, ensure you have the following installed and running:

1.  **Python 3.9+**: A recent version of Python. We highly recommend using a virtual environment (`python -m venv .venv`).
2.  **Python Dependencies**: Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Ollama Service**: The script needs to connect to a running Ollama instance. You can launch one using Podman:
    ```bash
    # Launch the Ollama container in the background
    # This uses a persistent volume to save your models
    podman run -d --rm -p 11434:11434 --name ollama-synapsia -v synapsia_storage:/root/.ollama ollama/ollama
    ```
4.  **Embedding Model**: After starting the container, pull your desired embedding model:
    ```bash
    # Tell the running 'ollama-synapsia' container to download the model
    podman exec -it ollama-synapsia ollama pull mxbai-embed-large
    ```

---

## ✍️ Ingesting Knowledge (`synapsia.py`)

This is the main script for processing your documents.

**Command Syntax:**
```bash
python synapsia.py --docs <path_to_docs> --knowledge <path_to_knowledge_base> [OPTIONS]
```

### Required Arguments
* `--docs <path>`: The relative or absolute path to the directory containing your source documents.

* `--knowledge <path>`: The relative or absolute path to the output directory where the knowledge base will be saved.

### Options
* `--embed-model <model_name>`: The name of the embedding model to use from Ollama.
    Default: `mxbai-embed-large`

* `--ollama-url <url>`: The base URL of the Ollama API service.
    Default: `http://localhost:11434`

* `--embed-batch-size <number>`: Number of chunks to process at a time.
    Default: `5`

* `--chunk-size <number>`: The size of text chunks in tokens.
    Default: `1024`

* `--chunk-overlap <number>`: The number of overlapping tokens between consecutive chunks.
    Default: `20`

* `-h`, `--help`: Show the help message and exit.

### Ingestion Examples

#### 1. Basic Usage
Process documents from `./my_docs/` and save the index to `./my_kb/`.

```bash
python synapsia.py --docs ./my_docs/ --knowledge ./my_kb/
```

#### 2. Advanced Usage (Custom Model)

Use a different embedding model.

```bash
python synapsia.py --docs ./my_docs/ --knowledge ./my_kb/ --embed-model nomic-embed-text
```

#### 3. Advanced Usage (Tuned for Q&A)
Optimized for dense, factual documents. Uses a smaller chunk size for more precise answers.

```bash
python synapsia.py \
    --docs ./faq_docs/ \
    --knowledge ./faq_kb/ \
    --chunk-size 256 \
    --chunk-overlap 25
```

---

## ❓ Querying Knowledge (synapsia_query.py)

Use this script to test your new knowledge base. It loads the index, sends your query to a local LLM (via Ollama), and provides a RAG-generated answer.

**Command Syntax**:

```bash
python synapsia_query.py --knowledge <path_to_knowledge_base> --query "Your question here" [OPTIONS]
```

### Required Arguments
* `--knowledge <path>`: The path to the directory where the knowledge base was saved.

* `--query <question>`: The question you want to ask, enclosed in quotes.

### Options

* `--llm-model <model_name>`: The name of the LLM to use from Ollama for generating the answer.
    Default: `llama3`

* `--top-k <number>`: The number of relevant text chunks to retrieve.
    Default: `3`

* `--show-context`: A flag that displays the source text chunks and their relevance scores. Extremely useful for debugging.

* `--embed-model`, `--ollama-url`: These should match the values used during the ingestion process.

### Query Examples

#### 1. Basic Question

Get a direct answer from the knowledge base.

```bash
python synapsia_query.py \
    --knowledge ./my_kb/ \
    --query "What is the main purpose of Ansible?"
```

#### 2. Debugging Query

Get an answer and see the top 2 source chunks used as context.

```bash
python synapsia_query.py \
    --knowledge ./faq_kb/ \
    --query "How do I reset my password?" \
    --top-k 2 \
    --show-context
```

## ⚖️ License

This project is licensed under the MIT License. See the LICENSE file for details.