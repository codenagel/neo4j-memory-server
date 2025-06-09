# Neo4j Memory Server


[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **Model Context Protocol (MCP) server** that provides persistent memory for AI agents using a local **Neo4j graph database**. Store entities, relationships, and observations that persist across conversations. You can see and interact with the knowledge graph using Neo4j webbrowser.

## Quick Start

### 1. Install
```bash
pip install neo4j-memory-server
```

### 2. Start Neo4j
```bash
docker-compose up -d
```

### 3. Configure Your MCP Client

**Claude Desktop** (`~/.config/claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "neo4j-memory": {
	"type": "stdio",
	"command": "python",
	"args": ["/path/to/project/neo4j-memory-server/src/neo4j_memory_server/server.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j", 
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```


### 4. Start Using
Your AI agent can now:
- **Create entities**: People, companies, concepts, etc.
- **Add relationships**: "Alice works at Acme Corp"
- **Store observations**: Facts, notes, and insights
- **Search knowledge**: Find information across conversations
- **Build context**: Rich, persistent memory

## Memory Utilization

The effectiveness of this memory system depends on how the AI agent uses it. Here's an example prompt for optimal memory utilization:

### Recommended AI Instructions

```
Follow these steps for each interaction:

1. **User Identification**: 
   - You should assume you are interacting with the primary user
   - If you haven't identified the user, proactively try to do so

2. **Memory Retrieval**: 
   - Always begin by saying "Remembering..." and retrieve relevant information
   - Search your knowledge graph using relevant keywords
   - Always refer to your knowledge graph as your "memory"

3. **Memory Creation**: 
   - Be attentive to new information in these categories:
     a) Basic Identity (age, gender, location, job title, education)
     b) Behaviors (interests, habits, preferences)  
     c) Goals (aspirations, targets, objectives)
     d) Relationships (personal and professional connections)
     e) Context (projects, events, significant interactions)

4. **Memory Updates**:
   - Create entities for recurring people, organizations, and concepts
   - Connect them using meaningful relationships
   - Store facts as observations with specific, descriptive details
```

### Example Usage

**User**: "Remember that Alice is a software engineer at Acme Corp who specializes in Python and lives in San Francisco."

**AI Response**: "Remembering... I'll store this information about Alice.

*[Creates entity: Alice (Person) with observations: "Software engineer", "Works at Acme Corp", "Specializes in Python", "Lives in San Francisco"]*
*[Creates entity: Acme Corp (Company) if not exists]*
*[Creates relation: Alice -> works_at -> Acme Corp]*

I've stored the information about Alice in my memory. I now know she's a Python-focused software engineer at Acme Corp in San Francisco."

**Later conversation**: "What do you know about Alice?"

**AI Response**: "Remembering... Let me search my memory for Alice.

I know Alice is a software engineer who works at Acme Corp. She specializes in Python programming and lives in San Francisco. Would you like me to retrieve any specific information about her or her work?"

## API Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `create_entities` | Add new people, places, concepts | Create "Alice (Person)" |
| `create_relations` | Link entities together | "Alice works_at Acme_Corp" |
| `add_observations` | Store facts and insights | "Prefers morning meetings" |
| `search_nodes` | Find relevant information | Search for "python engineer" |
| `read_graph` | Get complete knowledge map | Full memory dump |
| `delete_entities` | Remove outdated information | Delete old contacts |

## Features

- 🧠 **Persistent Memory** - Knowledge survives across conversations
- 🔗 **Rich Relationships** - Connect entities with meaningful relationships  
- 🔍 **Advanced Search** - Neo4j-powered graph queries and full-text search
- ⚡ **High Performance** - Handles millions of entities efficiently
- 🔒 **ACID Transactions** - Guaranteed data consistency
- 📈 **Scalable** - Enterprise-grade Neo4j backend
- 🎯 **Semantic Queries** - Complex graph traversals and pattern matching

## Configuration

Set environment variables or create `.env` file:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j
```


## License

MIT License - see [LICENSE](LICENSE) file for details.

