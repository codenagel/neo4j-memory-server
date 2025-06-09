from typing import Any, Dict, List

from neo4j import GraphDatabase, basic_auth

from neo4j_memory_server.models import Relation, Entity, KnowledgeGraph


class Neo4jKnowledgeGraphManager:
    """Manages knowledge graph operations using Neo4j as the backend."""

    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=basic_auth(username, password))
        self.database = database
        self._ensure_constraints()

    def _ensure_constraints(self):
        """Create necessary constraints and indexes."""
        with self.driver.session(database=self.database) as session:
            # Create unique constraint on entity name
            try:
                session.run(
                    "CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
            except Exception:
                pass  # Constraint might already exist

    def close(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()

    async def create_entities(self, entities: List[Entity]) -> List[Entity]:
        """Create new entities in the knowledge graph."""
        new_entities = []

        with self.driver.session(database=self.database) as session:
            for entity in entities:
                # Check if entity already exists
                result = session.run(
                    "MATCH (e:Entity {name: $name}) RETURN e",
                    name=entity.name
                )
                if not result.single():
                    # Create new entity
                    session.run(
                        """
                        CREATE (e:Entity {
                            name: $name,
                            entity_type: $entity_type,
                            observations: $observations
                        })
                        """,
                        name=entity.name,
                        entity_type=entity.entity_type,
                        observations=entity.observations
                    )
                    new_entities.append(entity)

        return new_entities

    async def create_relations(self, relations: List[Relation]) -> List[Relation]:
        """Create new relations between entities."""
        new_relations = []

        with self.driver.session(database=self.database) as session:
            for relation in relations:
                # Check if relation already exists
                result = session.run(
                    """
                    MATCH (from:Entity {name: $from_name})-[r]-(to:Entity {name: $to_name})
                    WHERE type(r) = $relation_type
                    RETURN r
                    """,
                    from_name=relation.from_entity,
                    to_name=relation.to_entity,
                    relation_type=relation.relation_type.upper().replace(' ', '_')
                )

                if not result.single():
                    # Create new relation
                    session.run(
                        f"""
                        MATCH (from:Entity {{name: $from_name}})
                        MATCH (to:Entity {{name: $to_name}})
                        CREATE (from)-[r:{relation.relation_type.upper().replace(' ', '_')}]->(to)
                        """,
                        from_name=relation.from_entity,
                        to_name=relation.to_entity
                    )
                    new_relations.append(relation)

        return new_relations

    async def add_observations(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add new observations to existing entities."""
        results = []

        with self.driver.session(database=self.database) as session:
            for obs in observations:
                entity_name = obs['entityName']
                contents = obs['contents']

                # Get current observations
                result = session.run(
                    "MATCH (e:Entity {name: $entity_name}) RETURN e.observations as observations",
                    entity_name=entity_name
                )
                record = result.single()

                if not record:
                    raise ValueError(f"Entity with name {entity_name} not found")

                current_observations = record['observations'] or []
                new_observations = [content for content in contents if content not in current_observations]

                if new_observations:
                    updated_observations = current_observations + new_observations
                    session.run(
                        "MATCH (e:Entity {name: $entity_name}) SET e.observations = $observations",
                        entity_name=entity_name,
                        observations=updated_observations
                    )

                results.append({
                    'entityName': entity_name,
                    'addedObservations': new_observations
                })

        return results

    async def delete_entities(self, entity_names: List[str]) -> None:
        """Delete entities and their associated relations."""
        with self.driver.session(database=self.database) as session:
            session.run(
                "MATCH (e:Entity) WHERE e.name IN $entity_names DETACH DELETE e",
                entity_names=entity_names
            )

    async def delete_observations(self, deletions: List[Dict[str, Any]]) -> None:
        """Delete specific observations from entities."""
        with self.driver.session(database=self.database) as session:
            for deletion in deletions:
                entity_name = deletion['entityName']
                observations_to_delete = deletion['observations']

                # Get current observations
                result = session.run(
                    "MATCH (e:Entity {name: $entity_name}) RETURN e.observations as observations",
                    entity_name=entity_name
                )
                record = result.single()

                if record:
                    current_observations = record['observations'] or []
                    updated_observations = [obs for obs in current_observations if obs not in observations_to_delete]

                    session.run(
                        "MATCH (e:Entity {name: $entity_name}) SET e.observations = $observations",
                        entity_name=entity_name,
                        observations=updated_observations
                    )

    async def delete_relations(self, relations: List[Relation]) -> None:
        """Delete specific relations from the knowledge graph."""
        with self.driver.session(database=self.database) as session:
            for relation in relations:
                session.run(
                    f"""
                    MATCH (from:Entity {{name: $from_name}})-[r:{relation.relation_type.upper().replace(' ', '_')}]->(to:Entity {{name: $to_name}})
                    DELETE r
                    """,
                    from_name=relation.from_entity,
                    to_name=relation.to_entity
                )

    async def read_graph(self) -> KnowledgeGraph:
        """Read the entire knowledge graph."""
        entities = []
        relations = []

        with self.driver.session(database=self.database, fetch_size=10000) as session:
            # Get all entities
            result = session.run(
                "MATCH (e:Entity) RETURN e.name as name, e.entity_type as entity_type, e.observations as observations")
            for record in result:
                entities.append(Entity(
                    name=record['name'],
                    entity_type=record['entity_type'],
                    observations=record['observations'] or []
                ))

            # Get all relations
            result = session.run(
                """
                MATCH (from:Entity)-[r]->(to:Entity)
                RETURN from.name as from_name, to.name as to_name, type(r) as relation_type
                """
            )
            for record in result:
                relations.append(Relation(
                    from_entity=record['from_name'],
                    to_entity=record['to_name'],
                    relation_type=record['relation_type'].replace('_', ' ').lower()
                ))

        return KnowledgeGraph(entities=entities, relations=relations)

    async def search_nodes(self, query: str) -> KnowledgeGraph:
        """Search for nodes based on a query string."""
        entities = []
        relations = []

        with self.driver.session(database=self.database) as session:
            # Search entities by name, type, or observations
            result = session.run(
                """
                MATCH (e:Entity)
                WHERE toLower(e.name) CONTAINS toLower($search_query)
                   OR toLower(e.entity_type) CONTAINS toLower($search_query)
                   OR any(obs IN e.observations WHERE toLower(obs) CONTAINS toLower($search_query))
                RETURN e.name as name, e.entity_type as entity_type, e.observations as observations
                """,
                search_query=query
            )

            entity_names = set()
            for record in result:
                entities.append(Entity(
                    name=record['name'],
                    entity_type=record['entity_type'],
                    observations=record['observations'] or []
                ))
                entity_names.add(record['name'])

            # Get relations between filtered entities
            if entity_names:
                result = session.run(
                    """
                    MATCH (from:Entity)-[r]->(to:Entity)
                    WHERE from.name IN $entity_names AND to.name IN $entity_names
                    RETURN from.name as from_name, to.name as to_name, type(r) as relation_type
                    """,
                    entity_names=list(entity_names)
                )
                for record in result:
                    relations.append(Relation(
                        from_entity=record['from_name'],
                        to_entity=record['to_name'],
                        relation_type=record['relation_type'].replace('_', ' ').lower()
                    ))

        return KnowledgeGraph(entities=entities, relations=relations)

    async def open_nodes(self, names: List[str]) -> KnowledgeGraph:
        """Open specific nodes by their names."""
        entities = []
        relations = []

        with self.driver.session(database=self.database) as session:
            # Get specified entities
            result = session.run(
                "MATCH (e:Entity) WHERE e.name IN $entity_names RETURN e.name as name, e.entity_type as entity_type, e.observations as observations",
                entity_names=names
            )

            found_names = set()
            for record in result:
                entities.append(Entity(
                    name=record['name'],
                    entity_type=record['entity_type'],
                    observations=record['observations'] or []
                ))
                found_names.add(record['name'])

            # Get relations between specified entities
            if found_names:
                result = session.run(
                    """
                    MATCH (from:Entity)-[r]->(to:Entity)
                    WHERE from.name IN $entity_names AND to.name IN $entity_names
                    RETURN from.name as from_name, to.name as to_name, type(r) as relation_type
                    """,
                    entity_names=list(found_names)
                )
                for record in result:
                    relations.append(Relation(
                        from_entity=record['from_name'],
                        to_entity=record['to_name'],
                        relation_type=record['relation_type'].replace('_', ' ').lower()
                    ))

        return KnowledgeGraph(entities=entities, relations=relations)
