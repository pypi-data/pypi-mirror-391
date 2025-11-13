# synapsia_query.py
import os
import sys
import argparse
import logging
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

def run_query(knowledge, query, embed_model, llm_model, ollama_url, top_k, show_context):
    """
    Core logic to load the DB and ask the question.
    """
    if not os.path.exists(knowledge):
        print(f"❌ Error: The knowledge base directory '{knowledge}' does not exist.")
        print("Please run the ingestion script first.")
        sys.exit(1)

    print("--- 🤖 Starting Query Process ---")
    print(f"💾 Knowledge base: {knowledge}")
    print(f"🧠 LLM model: {llm_model}")
    print(f"⚙️  Similarity top_k: {top_k}")
    print(f"❓ Query: '{query}'")

    try:
        Settings.embed_model = OllamaEmbedding(model_name=embed_model, base_url=ollama_url)
        
        Settings.llm = Ollama(
            model=llm_model, 
            base_url=ollama_url, 
            request_timeout=120.0
        )

        print("\n[Step 1/3] Loading knowledge base from disk (this may take a moment)...")
        storage_context = StorageContext.from_defaults(persist_dir=knowledge)
        index = load_index_from_storage(storage_context)
        print("✅ Knowledge base loaded.")

        print("\n[Step 2/3] Creating query engine...")
        query_engine = index.as_query_engine(similarity_top_k=top_k)
        print("✅ Query engine ready.")

        print("\n[Step 3/3] Sending query to the engine...")
        response = query_engine.query(query)
        print("✅ Response received!")

        print("\n--- 💡 Answer ---")
        print(str(response))
        print("-" * 16)

        if show_context:
            print("\n--- 📚 Source Context ---")
            for i, node in enumerate(response.source_nodes, 1):
                print(f"Source {i} (Score: {node.score:.4f}):")
                print("```")
                print(node.get_content().strip())
                print("```")
                print("-" * 10)

    except Exception as e:
        print(f"❌ An error occurred: {e}")

def main():
    """
    Entry point for the CLI.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        filename="synapsia_query.log",
        filemode="w"
    )

    parser = argparse.ArgumentParser(description="Query a LlamaIndex knowledge base created by SynapsIA.")
    parser.add_argument("--knowledge", required=True, help="Path to the knowledge base directory.")
    parser.add_argument("--query", required=True, help="The question to ask.")
    parser.add_argument("--embed-model", default="mxbai-embed-large", help="Ollama embedding model.")
    parser.add_argument("--llm-model", default="llama3", help="Ollama LLM for response generation.")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama API URL.")
    
    parser.add_argument("--top-k", type=int, default=3, help="The number of most relevant chunks to retrieve for context.")
    parser.add_argument("--show-context", action="store_true", help="If set, shows the source text chunks used to generate the answer.")
    
    args = parser.parse_args()
    
    run_query(
        args.knowledge, 
        args.query, 
        args.embed_model, 
        args.llm_model, 
        args.ollama_url, 
        args.top_k, 
        args.show_context
    )

if __name__ == "__main__":
    main()