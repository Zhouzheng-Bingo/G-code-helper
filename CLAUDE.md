# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a G-Code programming assistant system for the GJ306 CNC system. It combines a knowledge graph with RAG (Retrieval Augmented Generation) capabilities to provide intelligent assistance for G-code programming, machining processes, and CNC operations.

## Key Architecture Components

### Core Services
- **FastAPI Backend** (`api_backend.py`): REST API server running on port 18881
- **Gradio WebUI** (`webui.py`): Chat interface with voice input support on port 7860
- **Main Application** (`app.py`): Orchestrates both services in separate threads

### Knowledge Systems
- **Knowledge Graph** (`dao/graph/`): Neo4j-based graph database for entity relationships
- **RAG System** (`model/rag/`): Document retrieval with FAISS indexing
- **Entity Search** (`model/graph_entity/`): Specialized search for manufacturing entities

### LLM Integration
- **Multi-provider Support** (`lang_chain/client/`): Supports Ollama, Zhipu, Qwen, DeepSeek, Baichuan, and others
- **Factory Pattern**: `ClientFactory` manages different LLM clients
- **Streaming Support**: Both regular and streaming chat completions

### Processing Pipeline
- **Question Analysis** (`qa/question_parser.py`): Classifies user queries by type
- **Template Processing** (`qa/process_templates/`): G-code generation templates
- **Parameter Extraction** (`qa/interaction.py`): Extracts machining parameters from user input

## Development Commands

### Running the Application
```bash
# Main application (starts both API and WebUI)
python app.py

# Individual services
python api_backend.py  # API only
python webui.py       # WebUI only

# Background service management
./restart.sh          # Restart with process management
```

### Testing
```bash
# Run comprehensive test suite
python test.py

# Specific test modules
python test_gcode_generation.py
python test_process_recognition.py
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PY_ENVIRONMENT=local
export KMP_DUPLICATE_LIB_OK=TRUE
```

## Configuration

### Environment Configuration
- Configuration files: `config/config-{environment}.yaml`
- Default environment: `local` (set in `app.py`)
- Database connections: Neo4j, Redis, MongoDB, Elasticsearch support

### Key Configuration Sections
- **Server ports**: API (18881), WebUI (7860)
- **Database connections**: Neo4j for knowledge graph, FAISS for vector search
- **Model settings**: Embedding models, TTS voices, LLM clients
- **Audio processing**: Whisper model configuration for speech-to-text

## Important File Locations

### Core Logic
- `qa/interaction.py`: Main chat interaction handler with G-code generation
- `qa/answer.py`: Question processing and response generation
- `lang_chain/rag_chain.py`: RAG implementation for document retrieval

### Data Management
- `data/model/`: Trained models and indices (FAISS, entity searchers)
- `data/corpus/`: Document corpus for RAG (PDFs, Word docs)
- `data/cache/`: Cached entities and processing results

### Templates and Resources
- `qa/process_templates/`: G-code generation templates for different machining processes
- `resource/avatar/`: UI avatars and assets
- `templates/`: HTML templates for web interface

## Process Types and Mapping

The system recognizes these machining process categories:
- **外圆工艺** (External turning): 外圆, 外锥面, 外圆弧
- **端面工艺** (Face turning): 端面, 切槽, 内端面
- **里孔工艺** (Internal boring): 内圆, 内锥面, 内槽, 内弧, 中心孔
- **锥面工艺** (Taper turning): Various internal/external tapers
- **螺纹工艺** (Threading): Internal/external threads
- **倒角工艺** (Chamfering): Various chamfer operations

## Development Notes

- The system uses a singleton pattern for configuration (`config/config.py`)
- Voice input is processed using Whisper (configurable model size)
- Knowledge graph entities are cached and versioned for performance
- All LLM clients implement a common interface (`llm_client_base.py`)
- Parameter extraction from user messages supports various Chinese language patterns
- The application includes comprehensive logging with Loguru