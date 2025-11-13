# ISC Playbook MCP Server

Model Context Protocol (MCP) server for searching and browsing the IBM ISC Playbook with hybrid search capabilities.

## Features

- **Hybrid Search**: Combines semantic (dense vectors) and keyword (sparse vectors) search using Milvus Lite
- **1,358 Indexed Pages**: Complete IBM ISC Playbook content (1,091 documents + 266 folders)
- **Natural Language Queries**: Search using conversational questions
- **GitHub Copilot Integration**: Access playbook directly from VS Code

## Architecture

- **Vector Database**: Milvus Lite (embedded, no external service needed)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2, 384-dim)
- **Search Algorithm**: RRF (Reciprocal Rank Fusion) for result merging
- **MCP Framework**: FastMCP (Python SDK)

## Installation

### Option 1: Using uvx (Recommended)

The easiest way to use this MCP server is with `uvx`:

```bash
# Install and run directly with uvx
uvx isc-playbook-mcp-server
```

### Option 2: From PyPI

```bash
# Install from PyPI
pip install isc-playbook-mcp-server

# Run the server
isc-playbook-mcp-server
```

### Option 3: From Source (Development)

1. **Clone the repository**:
   ```bash
   git clone git@github.ibm.com:kirtijha/isc-playbook-mcp-server.git
   cd isc-playbook-mcp-server
   ```

2. **Install with uv**:
   ```bash
   uv pip install -e .
   ```

   Or with pip:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   pip install -e .
   ```

## Usage

### MCP Server Configuration

Add to your MCP settings file (e.g., `~/.config/mcp/mcp.json` or VS Code's MCP settings):

#### Using uvx (Recommended):

```json
{
  "mcpServers": {
    "isc-playbook": {
      "command": "uvx",
      "args": ["isc-playbook-mcp-server"]
    }
  }
}
```

#### Using installed package:

```json
{
  "mcpServers": {
    "isc-playbook": {
      "command": "isc-playbook-mcp-server"
    }
  }
}
}
```

### Available Tools

1. **search_playbook**: Natural language search across all pages using hybrid search (semantic + keyword)
2. **get_document**: Retrieve full content of a specific document by URL
3. **browse_by_type**: List all documents or folders
4. **search_by_path**: Find documents by navigation path pattern (e.g., "UPX > PRM DevOps")
5. **get_related_documents**: Find semantically similar documents to a given document
6. **get_index_stats**: Get statistics about indexed content (total pages, documents, folders)

### Example Queries

**Natural Language Search:**
- "How do I troubleshoot production issues in ISC?"
- "What is the process for onboarding new team members?"
- "How to create and manage Salesforce packages?"
- "Deployment process to staging environment"

**Path-based Search:**
- "Show me all documents in UPX > PRM DevOps"
- "Find everything under ISC Sales > Development"
- "What's in the Salesforce Admin section?"

**Related Documents:**
- "Find documents similar to the deployment guide"
- "What else should I read after the onboarding doc?"

## Project Structure

```
playbook-mcp-server/
├── src/
│   ├── server.py           # FastMCP server
│   ├── hybrid_indexer.py   # Milvus Lite hybrid search
│   ├── scraper.py          # Playbook scraper
│   └── cleaner.py          # HTML cleaner
├── data/
│   ├── cleaned/            # Cleaned JSON data
│   └── index/              # Milvus database
├── requirements.txt
└── README.md
```

## Technical Details

- **Vocabulary Size**: 100K terms for sparse vectors (BM25-like)
- **Text Limit**: 65,535 characters per document (Milvus VARCHAR limit)
- **Preview Size**: 1,000 chars in search results, 500 in browse
- **Batch Size**: 100 documents per indexing batch

## Production Ready

✅ Comprehensive data coverage (3.2x more than initial version)  
✅ No data loss or unnecessary truncation  
✅ Accurate hybrid search with RRF fusion  
✅ Error handling and logging  
✅ Optimized for performance  

## License

IBM Internal Use Only

## Authors

- Kirti Jha (kirtijha@in.ibm.com)

## Last Updated

November 12, 2025
