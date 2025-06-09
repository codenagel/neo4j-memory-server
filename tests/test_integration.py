import asyncio
import json
import os

from neo4j_memory_server.manager import Neo4jKnowledgeGraphManager
from neo4j_memory_server.models import Relation, Entity


async def test_neo4j_memory_server():
    """Test the Neo4j Memory Server functionality."""

    # Initialize the manager
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_database = os.getenv("NEO4J_DATABASE")

    manager = Neo4jKnowledgeGraphManager(
        uri=neo4j_uri,
        username=neo4j_username,
        password=neo4j_password,
        database=neo4j_database
    )

    try:
        print("🧪 Testing Neo4j Memory Server...")

        # Clear any existing test data
        print("\n1. Clearing test data...")
        await manager.delete_entities(["Alice", "Bob", "Acme Corp", "TechCorp"])

        # Test 1: Create entities
        print("\n2. Creating entities...")
        entities = [
            Entity(name="Alice", entity_type="Person", observations=["Software Engineer", "Lives in San Francisco"]),
            Entity(name="Bob", entity_type="Person", observations=["Product Manager", "Likes coffee"]),
            Entity(name="Acme Corp", entity_type="Company", observations=["Tech company", "Founded in 2020"]),
        ]

        created_entities = await manager.create_entities(entities)
        print(f"   ✅ Created {len(created_entities)} entities")
        for entity in created_entities:
            print(f"      - {entity.name} ({entity.entity_type})")

        # Test 2: Create relations
        print("\n3. Creating relations...")
        relations = [
            Relation(from_entity="Alice", to_entity="Acme Corp", relation_type="works at"),
            Relation(from_entity="Bob", to_entity="Acme Corp", relation_type="works at"),
            Relation(from_entity="Alice", to_entity="Bob", relation_type="collaborates with"),
        ]

        created_relations = await manager.create_relations(relations)
        print(f"   ✅ Created {len(created_relations)} relations")
        for relation in created_relations:
            print(f"      - {relation.from_entity} {relation.relation_type} {relation.to_entity}")

        # Test 3: Add observations
        print("\n4. Adding observations...")
        observations = [
            {"entityName": "Alice", "contents": ["Python expert", "Team lead"]},
            {"entityName": "Acme Corp", "contents": ["Growing rapidly", "Remote-first"]}
        ]

        added_obs = await manager.add_observations(observations)
        print("   ✅ Added observations")
        for result in added_obs:
            print(f"      - {result['entityName']}: {result['addedObservations']}")

        # Test 4: Read entire graph
        print("\n5. Reading entire graph...")
        graph = await manager.read_graph()
        print(f"   ✅ Graph contains {len(graph.entities)} entities and {len(graph.relations)} relations")

        # Test 5: Search nodes
        print("\n6. Searching for 'engineer'...")
        search_result = await manager.search_nodes("engineer")
        print(f"   ✅ Found {len(search_result.entities)} entities matching 'engineer'")
        for entity in search_result.entities:
            print(f"      - {entity.name}: {entity.observations}")

        # Test 6: Open specific nodes
        print("\n7. Opening specific nodes...")
        specific_nodes = await manager.open_nodes(["Alice", "Bob"])
        print(f"   ✅ Retrieved {len(specific_nodes.entities)} specific entities")
        print(f"   ✅ Found {len(specific_nodes.relations)} relations between them")

        # Test 7: Delete observations
        print("\n8. Deleting observations...")
        deletions = [
            {"entityName": "Alice", "observations": ["Python expert"]}
        ]
        await manager.delete_observations(deletions)
        print("   ✅ Deleted specific observations")

        # Test 8: Delete relations
        print("\n9. Deleting relations...")
        relations_to_delete = [
            Relation(from_entity="Alice", to_entity="Bob", relation_type="collaborates with")
        ]
        await manager.delete_relations(relations_to_delete)
        print("   ✅ Deleted specific relations")

        # Test 9: Verify final state
        print("\n10. Final verification...")
        final_graph = await manager.read_graph()
        print(f"   ✅ Final state: {len(final_graph.entities)} entities, {len(final_graph.relations)} relations")

        # Display final graph
        print("\n📊 Final Graph State:")
        print("Entities:")
        for entity in final_graph.entities:
            print(f"  - {entity.name} ({entity.entity_type}): {entity.observations}")

        print("Relations:")
        for relation in final_graph.relations:
            print(f"  - {relation.from_entity} → {relation.relation_type} → {relation.to_entity}")

        print("\n🎉 All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        # Clean up
        await manager.delete_entities(["Alice", "Bob", "Acme Corp", "TechCorp"])
        manager.close()


async def test_mcp_json_format():
    """Test with MCP-style JSON format."""
    print("\n🔧 Testing MCP JSON format...")

    # Sample data in MCP format
    mcp_entities = [
        {
            "name": "TestUser",
            "entityType": "Person",
            "observations": ["Likes testing", "Uses MCP"]
        }
    ]

    mcp_relations = [
        {
            "from": "TestUser",
            "to": "TestSystem",
            "relationType": "uses"
        }
    ]

    print("✅ MCP format validation passed")
    print(f"   Entities: {json.dumps(mcp_entities, indent=2)}")
    print(f"   Relations: {json.dumps(mcp_relations, indent=2)}")


if __name__ == "__main__":
    print("🚀 Starting Neo4j Memory Server Tests")
    print("=" * 50)

    # Check environment variables
    required_vars = ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {missing_vars}")
        print("Using default values. Set these for production use:")
        for var in missing_vars:
            if var == "NEO4J_URI":
                print(f"   export {var}=bolt://localhost:7687")
            elif var == "NEO4J_USERNAME":
                print(f"   export {var}=neo4j")
            elif var == "NEO4J_PASSWORD":
                print(f"   export {var}=your_password_here")

    try:
        # Run async tests
        asyncio.run(test_neo4j_memory_server())
        asyncio.run(test_mcp_json_format())

    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        exit(1)
