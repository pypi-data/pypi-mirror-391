# synapsia/synapsia.py
import os
import argparse
import logging
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.node_parser import SentenceSplitter

def run_ingestion(docs, knowledge, embed_model, ollama_url, embed_batch_size, chunk_size, chunk_overlap):
    """
    Contains the core logic for the ingestion process.
    """
    if not os.path.exists(docs):
        print(f"❌ Error: The document directory '{docs}' does not exist.")
        return

    print("--- 🚀 Starting Knowledge Ingestion Process ---")
    print(f"📚 Document directory: {docs}")
    print(f"💾 Knowledge base directory: {knowledge}")
    print(f"🧠 Embedding model: {embed_model}")
    print(f"🌐 Ollama URL: {ollama_url}")
    print(f"⚙️  Embedding batch size: {embed_batch_size}")
    print(f"⚙️  Chunk size: {chunk_size} tokens")
    print(f"⚙️  Chunk overlap: {chunk_overlap} tokens")

    os.makedirs(knowledge, exist_ok=True)

    try:
        # Step 1: Configure LlamaIndex settings
        print("\n[Step 1/4] Configuring LlamaIndex settings...")
        Settings.embed_model = OllamaEmbedding(
            model_name=embed_model,
            base_url=ollama_url,
            ollama_additional_kwargs={"mirostat": 0},
        )
        Settings.node_parser = SentenceSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
        print("✅ Settings configured successfully.")

        # Step 2: Load the documents
        print("\n[Step 2/4] Loading documents from the directory...")
        reader = SimpleDirectoryReader(input_dir=docs, recursive=True)
        documents = reader.load_data()
        print(f"✅ Loaded {len(documents)} document(s).")

        # Step 3: Create the vector index from the documents
        print("\n[Step 3/4] Creating the vector index (this may take a while)...")
        index = VectorStoreIndex.from_documents(
            documents, 
            show_progress=True, 
            embed_batch_size=embed_batch_size
        )
        print("✅ Index created successfully.")

        # Step 4: Persist the index to disk
        print(f"\n[Step 4/4] Saving the index to '{knowledge}'...")
        index.storage_context.persist(persist_dir=knowledge)
        print("✅ Index saved successfully.")

        print("\n--- ✨ Ingestion Process Completed ---")

    except Exception as e:
        print(f"❌ An error occurred during the ingestion process: {e}")
        print(f"Please ensure the Ollama service is running and accessible at '{ollama_url}'")

def main():
    """
    Entry point for the CLI. Parses arguments and calls the logic.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        filename="synapsia.log",
        filemode="w"
    )

    parser = argparse.ArgumentParser(
        description="Processes documents and creates a vector index using Ollama.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument("--docs", required=True, help="Path to the input documents directory.")
    parser.add_argument("--knowledge", required=True, help="Path to the output directory to save the knowledge base.")

    # Optional arguments
    parser.add_argument("--embed-model", default="mxbai-embed-large", help="The name of the embedding model to use from Ollama.")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="The base URL of the Ollama API service.")
    parser.add_argument("--embed-batch-size", type=int, default=5, dest='embed_batch_size', help="Number of chunks to process at a time.")
    parser.add_argument("--chunk-size", type=int, default=1024, help="The size of text chunks in tokens.")
    parser.add_argument("--chunk-overlap", type=int, default=20, help="The number of overlapping tokens between chunks.")

    args = parser.parse_args()
    
    run_ingestion(
        args.docs, 
        args.knowledge, 
        args.embed_model, 
        args.ollama_url, 
        args.embed_batch_size, 
        args.chunk_size, 
        args.chunk_overlap
    )

if __name__ == "__main__":
    main()