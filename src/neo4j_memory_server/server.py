import asyncio
import json
import sys
from typing import Any, Dict, List

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from neo4j_memory_server.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
from neo4j_memory_server.manager import Neo4jKnowledgeGraphManager
from neo4j_memory_server.models import Entity, Relation

# Initialize the knowledge graph manager
knowledge_graph_manager = Neo4jKnowledgeGraphManager(
    uri=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE
)

# Create the MCP server
server = Server("neo4j-memory-server")


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="create_entities",
            description="Create multiple new entities in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "The name of the entity"},
                                "entityType": {"type": "string", "description": "The type of the entity"},
                                "observations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "An array of observation contents associated with the entity"
                                },
                            },
                            "required": ["name", "entityType", "observations"],
                        },
                    },
                },
                "required": ["entities"],
            },
        ),
        types.Tool(
            name="create_relations",
            description="Create multiple new relations between entities in the knowledge graph. Relations should be in active voice",
            inputSchema={
                "type": "object",
                "properties": {
                    "relations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from": {"type": "string",
                                         "description": "The name of the entity where the relation starts"},
                                "to": {"type": "string",
                                       "description": "The name of the entity where the relation ends"},
                                "relationType": {"type": "string", "description": "The type of the relation"},
                            },
                            "required": ["from", "to", "relationType"],
                        },
                    },
                },
                "required": ["relations"],
            },
        ),
        types.Tool(
            name="add_observations",
            description="Add new observations to existing entities in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "observations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entityName": {"type": "string",
                                               "description": "The name of the entity to add the observations to"},
                                "contents": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "An array of observation contents to add"
                                },
                            },
                            "required": ["entityName", "contents"],
                        },
                    },
                },
                "required": ["observations"],
            },
        ),
        types.Tool(
            name="delete_entities",
            description="Delete multiple entities and their associated relations from the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entityNames": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An array of entity names to delete"
                    },
                },
                "required": ["entityNames"],
            },
        ),
        types.Tool(
            name="delete_observations",
            description="Delete specific observations from entities in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "deletions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entityName": {"type": "string",
                                               "description": "The name of the entity containing the observations"},
                                "observations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "An array of observations to delete"
                                },
                            },
                            "required": ["entityName", "observations"],
                        },
                    },
                },
                "required": ["deletions"],
            },
        ),
        types.Tool(
            name="delete_relations",
            description="Delete multiple relations from the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "relations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from": {"type": "string",
                                         "description": "The name of the entity where the relation starts"},
                                "to": {"type": "string",
                                       "description": "The name of the entity where the relation ends"},
                                "relationType": {"type": "string", "description": "The type of the relation"},
                            },
                            "required": ["from", "to", "relationType"],
                        },
                        "description": "An array of relations to delete"
                    },
                },
                "required": ["relations"],
            },
        ),
        types.Tool(
            name="read_graph",
            description="Read the entire knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="search_nodes",
            description="Search for nodes in the knowledge graph based on a query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string",
                              "description": "The search query to match against entity names, types, and observation content"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="open_nodes",
            description="Open specific nodes in the knowledge graph by their names",
            inputSchema={
                "type": "object",
                "properties": {
                    "names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An array of entity names to retrieve",
                    },
                },
                "required": ["names"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls."""
    try:
        if name == "create_entities":
            entities = [
                Entity(
                    name=e["name"],
                    entity_type=e["entityType"],
                    observations=e["observations"]
                )
                for e in arguments["entities"]
            ]
            result = await knowledge_graph_manager.create_entities(entities)
            return [types.TextContent(
                type="text",
                text=json.dumps([{
                    "name": e.name,
                    "entityType": e.entity_type,
                    "observations": e.observations
                } for e in result], indent=2)
            )]

        elif name == "create_relations":
            relations = [
                Relation(
                    from_entity=r["from"],
                    to_entity=r["to"],
                    relation_type=r["relationType"]
                )
                for r in arguments["relations"]
            ]
            result = await knowledge_graph_manager.create_relations(relations)
            return [types.TextContent(
                type="text",
                text=json.dumps([{
                    "from": r.from_entity,
                    "to": r.to_entity,
                    "relationType": r.relation_type
                } for r in result], indent=2)
            )]

        elif name == "add_observations":
            result = await knowledge_graph_manager.add_observations(arguments["observations"])
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "delete_entities":
            await knowledge_graph_manager.delete_entities(arguments["entityNames"])
            return [types.TextContent(type="text", text="Entities deleted successfully")]

        elif name == "delete_observations":
            await knowledge_graph_manager.delete_observations(arguments["deletions"])
            return [types.TextContent(type="text", text="Observations deleted successfully")]

        elif name == "delete_relations":
            relations = [
                Relation(
                    from_entity=r["from"],
                    to_entity=r["to"],
                    relation_type=r["relationType"]
                )
                for r in arguments["relations"]
            ]
            await knowledge_graph_manager.delete_relations(relations)
            return [types.TextContent(type="text", text="Relations deleted successfully")]

        elif name == "read_graph":
            result = await knowledge_graph_manager.read_graph()
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "entities": [{
                        "name": e.name,
                        "entityType": e.entity_type,
                        "observations": e.observations
                    } for e in result.entities],
                    "relations": [{
                        "from": r.from_entity,
                        "to": r.to_entity,
                        "relationType": r.relation_type
                    } for r in result.relations]
                }, indent=2)
            )]

        elif name == "search_nodes":
            result = await knowledge_graph_manager.search_nodes(arguments["query"])
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "entities": [{
                        "name": e.name,
                        "entityType": e.entity_type,
                        "observations": e.observations
                    } for e in result.entities],
                    "relations": [{
                        "from": r.from_entity,
                        "to": r.to_entity,
                        "relationType": r.relation_type
                    } for r in result.relations]
                }, indent=2)
            )]

        elif name == "open_nodes":
            result = await knowledge_graph_manager.open_nodes(arguments["names"])
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "entities": [{
                        "name": e.name,
                        "entityType": e.entity_type,
                        "observations": e.observations
                    } for e in result.entities],
                    "relations": [{
                        "from": r.from_entity,
                        "to": r.to_entity,
                        "relationType": r.relation_type
                    } for r in result.relations]
                }, indent=2)
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as error:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(error)}"
        )]


async def main():
    """Main entry point for the server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="neo4j-memory-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as error:
        print(f"Fatal error in main(): {error}", file=sys.stderr)
        sys.exit(1)
    finally:
        knowledge_graph_manager.close()
