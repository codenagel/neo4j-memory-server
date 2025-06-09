from typing import List
from dataclasses import dataclass

@dataclass
class Entity:
    name: str
    entity_type: str
    observations: List[str]


@dataclass
class Relation:
    from_entity: str
    to_entity: str
    relation_type: str


@dataclass
class KnowledgeGraph:
    entities: List[Entity]
    relations: List[Relation]
