# GitHub Repository RAG Assistant

**An adaptive Retrieval-Augmented Generation (RAG) system for exploring GitHub repositories through natural language queries, with source-grounded answers and file-level traceability.**

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white" alt="Python 3.11"/>
  <img src="https://img.shields.io/badge/LangChain-RAG-1C3C3C?logo=langchain&logoColor=white" alt="LangChain"/>
  <img src="https://img.shields.io/badge/ChromaDB-Vector%20Store-5B4DBC" alt="ChromaDB"/>
  <img src="https://img.shields.io/badge/Hugging%20Face-Embeddings-FFD21E?logo=huggingface&logoColor=black" alt="Hugging Face"/>
  <img src="https://img.shields.io/badge/Ollama-Local%20LLMs-black?logo=ollama&logoColor=white" alt="Ollama"/>
  <img src="https://img.shields.io/badge/Groq-LLM%20API-F55036" alt="Groq"/>
  <img src="https://img.shields.io/badge/RAGAS-Evaluation-249E8A" alt="RAGAS"/>
  <img src="https://img.shields.io/badge/pytest-Testing-0A9EDC?logo=pytest&logoColor=white" alt="pytest"/>
</p>

## Project Overview

Understanding an unfamiliar codebase often requires navigating multiple files, tracing dependencies, and searching through source code and documentation to find relevant information. Traditional keyword-based search can be insufficient when questions involve concepts, implementation details, or relationships between components.

**GitHub Repository RAG Assistant** addresses this challenge by combining semantic retrieval with Large Language Models (LLMs) to answer natural language questions about public GitHub repositories. Rather than relying exclusively on the model's internal knowledge, the system retrieves relevant repository content and uses it as contextual evidence for answer generation.

The system features a **modular architecture** designed to facilitate maintainability and future extensions. Particular emphasis is placed on systematic evaluation, combining quantitative retrieval metrics, such as **Recall@k** and **Average Precision@k**, with **LLM-as-a-Judge** approach to assess the quality of generated responses and the overall effectiveness of the RAG pipeline.

## System Architecture

The system follows an end-to-end RAG architecture organized into two main pipelines. The **Ingestion Pipeline** processes GitHub repositories and indexes their content in a ChromaDB vector store, while the **Query Pipeline** retrieves relevant context and generates source-grounded answers to user queries.

![Architecture design](images/architecture_design.png)

## Technical Design & Key Decisions

The main design constraint was to build a competitive RAG system for repository-level question answering while ensuring it could run efficiently on *Streamlit Community Cloud*. The system therefore prioritizes a balance between retrieval quality, answer reliability, computational efficiency, and response latency, enabling public access without requiring excessive resources or introducing unnecessary delays.

The following sections describe the technical design and key decisions in each component.

### Repository Ingestion

[Code: `src/github_rag/ingestion/`](src/github_rag/ingestion/) · [Walkthrough `Notebook 01`](notebooks/01_ingestion.ipynb)

Given a public GitHub repository URL, the ingestion component retrieves the repository files and converts their contents into LangChain `Document` objects. Each document preserves the raw file content and metadata identifying its origin, including the repository, branch, file name, and source URL.

### Document Processing

[Code: `src/github_rag/processing/`](src/github_rag/processing/) · [Walkthrough `Notebook 02`](notebooks/02_processing.ipynb)

A modular preprocessing stage applies file-specific transformations before chunking when needed. Currently, Jupyter notebooks (`.ipynb`) are parsed into individual LangChain `Document` objects, one per non-empty Markdown or code cell, replacing the original JSON representation with content that can be processed more effectively. The modular design allows additional file-specific processors to be introduced easily.

### Chunking

[Code: `src/github_rag/chunking/`](src/github_rag/chunking/) · [Walkthrough `Notebook 03`](notebooks/03_chunking.ipynb)

File-specific chunking strategies preserve the structure of different content types:
- **Code:** language-aware recursive splitting.
- **Markdown:** heading-based splitting followed by recursive character splitting.
- **Plain text and structured files** (e.g., JSON and YAML): recursive character splitting.

### Embedding Generation

[Code: `src/github_rag/embedding/`](src/github_rag/embedding/) · [Walkthrough `Notebook 04`](notebooks/04_embedding.ipynb)

The system uses Hugging Face's `paraphrase-multilingual-MiniLM-L12-v2` model to generate dense vector representations. Its compact size enables local embedding generation, making it suitable for resource-constrained deployment environments such as *Streamlit Community Cloud*.

### Vector DataBase

[Code: `src/github_rag/vectordatabase/`](src/github_rag/vectordatabase/) · [Walkthrough `Notebook 05`](notebooks/05_VectorDatabase.ipynb)

*ChromaDB* was selected for its straightforward integration with *LangChain* and support for both persistent local storage during development and in-memory storage for *Streamlit Community Cloud* deployment. 


### Adaptive Retrieval

[Code: `src/github_rag/retrieval/`](src/github_rag/retrieval/) · [Walkthrough `Notebook 06`](notebooks/06_Retrieval_design.ipynb)

The retrieval strategy first detects whether the user query references specific repository files to provide targeted context, then adapts the retrieval method and number of retrieved chunks to the query scope:

- **Single-file queries**: metadata-filtered semantic similarity search retrieves the top 5 chunks ($k=5$), prioritizing the most relevant content within the referenced file.
- **Multi-file queries**: metadata-filtered Maximal Marginal Relevance (*MMR*) retrieves 10 chunks ($k=10$), balancing relevance and diversity to capture complementary information across the referenced files.
- **General queries**: repository-wide *MMR* retrieval selects the top 5 chunks ($k=5$), promoting diversity across the repository while keeping the retrieved context focused.

### Prompt Engineering 

[Code: `src/github_rag/prompt_engineering/`](src/github_rag/prompt_engineering/) · [Walkthrough `Notebook 08`](notebooks/08_Prompt_and_LLM_generation.ipynb)

A custom prompt template instructs the LLM to use the retrieved context, avoid unsupported claims, and follow a defined citation format. Retrieved chunks are provided alongside their file names and source URLs, enabling traceable, source-grounded answers.

### LLM Generation

[Code: `src/github_rag/LLM_generation/`](src/github_rag/LLM_generation/) · [Walkthrough `Notebook 08`](notebooks/08_Prompt_and_LLM_generation.ipynb)

Supports *Ollama* models for local development and *Groq* API-hosted LLMs for deployment on *Streamlit Community Cloud*. *Groq* integration requires an **API key** and is subject to daily usage limits 


## RAG Evaluation

The system is evaluated at two levels: **retrieval quality** and **end-to-end RAG performance**. The evaluation datasets and their construction process are documented in [`evaluation/`](evaluation/).

### Retrieval Evaluation

The adaptive retriever is compared against a semantic search baseline using a manually curated ground-truth dataset of $20$ questions with their expected relevant chunks.

| Query Type | Retriever | Recall@5 | MRR@5 | AP@5 |
|:--|:--|--:|--:|--:|
| File(s) reference | Baseline | 0.361 | 0.153 | 0.110 |
| | **Adaptive** | **0.694** | **0.722** | **0.565** |
| General | Baseline | 0.857 | 0.750 | 0.655 |
| | **Adaptive** | **0.869** | **0.800** | **0.679** |

The results, analyzed in detail in [`07_Retrieval_evaluation.ipynb`](notebooks/07_Retrieval_evaluation.ipynb), show larger improvements for queries referencing specific repository files, where metadata filtering enhances both the coverage and ranking of relevant chunks. For general queries, the gains are smaller but consistent, indicating that MMR improves retrieval diversity without compromising retrieval performance.

### End-to-End RAG Evaluation

The complete RAG pipeline is evaluated using *RAGAS* with an **LLM-as-a-judge** approach. A dataset of $20$ questions, retrieved contexts, and generated answers is used to assess answer grounding and relevance.

| Metric | Mean ± Std. |
|:--|--:|
| Faithfulness | **0.856 ± 0.215** |
| Answer Relevancy | **0.700 ± 0.207** |

The results, analyzed in detail in [`10_RAG_evaluation.ipynb`](notebooks/10_RAG_evaluation.ipynb), suggest that generated answers are generally well grounded in the retrieved context, while answer relevance remains more variable. Manual inspection also highlights limitations of LLM-as-a-judge evaluation, particularly for open-ended queries where useful answers may receive lower relevance scores than expected.

## Installation & Usage

### 1. Environment Setup

Clone the repository and create the Conda environment using the provided [`environment.yml`](environment.yml) file, which specifies the Python version and project dependencies.

```bash
git clone https://github.com/davidfernxndez/github-repository-rag.git
cd github-rag

conda env create -f environment.yml
conda activate github-rag
```

### 2. LLM Configuration

The `LLMGenerator` class, defined in [`src/github_rag/LLM_generation/generator.py`](src/github_rag/LLM_generation/generator.py), supports two inference modes through its `mode` parameter: `local` and `API`.

#### Local Inference with Ollama

[Ollama](https://ollama.com/download) enables local inference without requiring an external LLM API key.

1. Download and install *Ollama* for your operating system from the [official download page](https://ollama.com/download).
2. Download the default model used by the system:

   ```bash
   ollama pull qwen3:1.7b
   ```

To use a different model, download it through *Ollama* and update the model configuration in `LLMGenerator`.

#### API Inference with Groq

Groq provides hosted LLM inference, making it suitable for deployment environments with limited computational resources.

1. Create an API key through the [Groq Console](https://console.groq.com/).
2. Configure the key in a `.env` file using the variable shown in [`.env.example`](.env.example):

   ```dotenv
   GROQ_API_KEY=your_groq_api_key
   ```

API usage is subject to Groq's rate limits and account quotas.

> **Note:** The complete RAG evaluation uses **RAGAS** with an **LLM-as-a-judge** approach. Due to its computational cost, the evaluator in [`src/github_rag/evaluator/`](src/github_rag/evaluator/) uses Groq for judge-model inference instead of a locally hosted Ollama model.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for the full license text.