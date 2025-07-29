from typing import List, Dict, Optional, Type
from pydantic import BaseModel, Field, create_model
from pyvis.network import Network
import os
import pandas as pd

#########################
### Class Definitions ###
#########################

class Qa_type(BaseModel):
    """
    Schema for investor QA call section categories
    Attributes:
        text_1_class (str): Category for the first text.
        text_2_class (str): Category for the second text.
        text_3_class (str): Category for the third text.
    Example:
        Qa_type(text_1_class="Financial", text_2_class="Market Analysis", text_3_class="Company Overview")
    """
    text_1_class: str = Field(description="Category for the first text")
    text_2_class: str = Field(description="Category for the second text")
    text_3_class: str = Field(description="Category for the third text")

class NodeSchema:
    """
    Schema for defining node types and their properties in the knowledge graph.
    Attributes:
        type (str): The type or label of the node (e.g., "Person", "Company").
        properties (List[str]): A list of property names associated with the node type.
        description (str): A description of the node type.
    Example:
        NodeSchema(type="Person", properties=["name", "age"], description="A person in the knowledge graph.")
    """
    def __init__(self, type: str, properties: List[str]= [], description: str= ""):
        self.type = type
        self.description = description 
        self.properties = properties 

class RelationshipSchema:
    """
    Schema for defining relationship types and their properties in the knowledge graph.
    Attributes:
        source (str): The source node type for the relationship (e.g., "Person").
        target (str): The target node type for the relationship (e.g., "Company").
        type (str): The type of the relationship (e.g., "SPOUSE_OF").
        properties (List[str]): A list of property names associated with the relationship type.
    Example:
        RelationshipSchema(source="Person", type="SPOUSE_OF", target="Person", properties=["since", "location"])
    """
    def __init__(self, source: str, type: str, target: str, properties: List[str]= []):
        self.source = source
        self.target = target
        self.type = type
        self.properties = properties 


# Create a generic Node model that includes type and properties
class Node(BaseModel):
    """
    A generic Node model that includes id, type, and properties.
    Attributes:
        id (str): A unique identifier for the node.
        type (str): The type or label of the node (e.g., "Person").
        properties (Dict[str, Optional[str]]): A dictionary of additional metadata where keys are strings and values are optional strings.
    Example:
        Node(id="123", type="Person", properties={"name": "John Doe", "age": "30"})

    """
    id: str
    type: str
    properties: Dict[str, Optional[str]]  # Properties are a dictionary of optional strings

# Create a generic Relationship model that includes type, source_type, target_type, and properties
class Relationship(BaseModel):
    """
    A generic Relationship model that includes source, target, type, source_type, target_type, and properties.
    Attributes:
        source (str): The id of the source node.
        target (str): The id of the target node.
        type (str): The type of the relationship (e.g., "SPOUSE_OF").
        source_type (str): The type of the source node (e.g., "Person").
        target_type (str): The type of the target node (e.g., "Company").
        properties (Dict[str, Optional[str]]): A dictionary of additional metadata where keys are strings and values are optional strings.
    Example:
        Relationship(
            source="123", target="456", type="SPOUSE_OF", source_type="Person",
            target_type="Person", properties={"since": "2010", "location": "New York"}
        )
    """
    source: str
    target: str
    type: str
    source_type: str  # Source node type (e.g., "Person")
    target_type: str  # Target node type (e.g., "Company")
    properties: Dict[str, Optional[str]]  # Properties are a dictionary of optional strings


# Create the Graph model
class Graph(BaseModel):
    """
    A model representing a knowledge graph containing nodes and relationships.
    Attributes:
        nodes (List[Node]): A list of nodes in the graph.
        relationships (List[Relationship]): A list of relationships in the graph.
    Example:
        Graph(
            nodes=[
                Node(id="123", type="Person", properties={"name": "John Doe", "age": "30"})
            ],
            relationships=[
                Relationship(
                    source="123", target="456", type="SPOUSE_OF",
                    source_type="Person", target_type="Person",
                    properties={"since": "2010", "location": "New York"}
                )
            ]
        )
    """
    nodes: List[Node]
    relationships: List[Relationship]

### Functions



def visualize_graph(graph_documents):
    """
    Visualizes a knowledge graph using PyVis based on the extracted graph documents.

    Args:
        graph_documents (list): A list of GraphDocument objects with nodes and relationships.

    Returns:
        pyvis.network.Network: The visualized network graph object.
    """
    # Create network
    net = Network(height="1200px", width="100%", directed=True,
                  notebook=False, bgcolor="#222222", font_color="white", filter_menu=True, cdn_resources='remote')

    nodes = graph_documents.nodes
    relationships = graph_documents.relationships

    # Build lookup for valid nodes
    node_dict = {node.id: node for node in nodes}

    # Filter out invalid edges and collect valid node IDs
    valid_edges = []
    valid_node_ids = set()
    for rel in relationships:
        if rel.source in node_dict and rel.target in node_dict:
            valid_edges.append(rel)
            valid_node_ids.update([rel.source, rel.target])

    # Track which nodes are part of any relationship
    connected_node_ids = set()
    for rel in relationships:
        connected_node_ids.add(rel.source)
        connected_node_ids.add(rel.target)

    # Add valid nodes to the graph
    for node_id in valid_node_ids:
        node = node_dict[node_id]
        try:
            net.add_node(node.id, label=node.id, title=node.type, group=node.type)
        except:
            continue  # Skip node if error occurs

    # Add valid edges to the graph
    for rel in valid_edges:
        try:
            net.add_edge(rel.source, rel.target, label=rel.type.lower())
        except:
            continue  # Skip edge if error occurs

    # Configure graph layout and physics
    net.set_options("""
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -100,
                    "centralGravity": 0.01,
                    "springLength": 200,
                    "springConstant": 0.08
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based"
            }
        }
    """)

    output_file = "knowledge_graph.html"
    try:
        net.save_graph(output_file)
        print(f"Graph saved to {os.path.abspath(output_file)}")
        return net
    except Exception as e:
        print(f"Error saving graph: {e}")
        return None


# from https://github.com/dhiaaeddine16/LLMGraphTransformer/blob/main/src/LLMGraphTransformer/prompt_generation.py
def format_node_schemas(schemas: List[NodeSchema]) -> str:
    """
    Formats a list of NodeSchema objects into a string representation for the prompt.
    Args:
        schemas (List[NodeSchema]): A list of NodeSchema objects.
    Returns:
        str: A formatted string representation of the node schemas.
    """
    lines = []
    for node in schemas:
        if node.description:
            lines.append(f"- {node.type}: {node.description}")
        else:
            lines.append(f"- {node.type}")
    return "\n".join(lines)

def format_node_properties_schemas(schemas: List[NodeSchema]) -> str:
    """
    Formats a list of NodeSchema objects into a string representation of their properties for the prompt.
    Args:
        schemas (List[NodeSchema]): A list of NodeSchema objects.
    Returns:
        str: A formatted string representation of the node properties schemas.
    """
    lines = []
    for node in schemas:
        if node.properties:
            props = '", "'.join(node.properties)
            lines.append(f"- {node.type}: \"{props}\"")
    return "\n".join(lines)

def format_relationship_schemas(schemas: List[RelationshipSchema]) -> str:
    """
    Formats a list of RelationshipSchema objects into a string representation for the prompt.
    Args:
        schemas (List[RelationshipSchema]): A list of RelationshipSchema objects.
    Returns:
        str: A formatted string representation of the relationship schemas.
    """
    lines = []
    for rel in schemas:
        lines.append(f"- {rel.source}, {rel.type}, {rel.target}")
    return "\n".join(lines)

def format_relationship_properties_schemas(schemas: List[RelationshipSchema]) -> str:
    """
    Formats a list of RelationshipSchema objects into a string representation of their properties for the prompt.
    Args:
        schemas (List[RelationshipSchema]): A list of RelationshipSchema objects.
    Returns:
        str: A formatted string representation of the relationship properties schemas.
    """
    lines = []
    for rel in schemas:
        if rel.properties:
            props = '", "'.join(rel.properties)
            lines.append(f"- {rel.type}: \"{props}\"")
    return "\n".join(lines)


def generate_graph_class(
        node_schemas: List[NodeSchema],
        relationship_schemas: List[RelationshipSchema]
) -> Type[BaseModel]:
    """
    Dynamically generates a Graph class with Node and Relationship models based on provided schemas.
    Args:
        node_schemas (List[NodeSchema]): A list of NodeSchema objects defining the node types and properties.
        relationship_schemas (List[RelationshipSchema]): A list of RelationshipSchema objects defining the relationship types and properties.
    Returns:
        Type[BaseModel]: A dynamically created Graph class with Node and Relationship models.
    """
    # Dynamically create Node models based on node_schemas
    node_models = {}
    for schema in node_schemas:
        properties = {prop: (Optional[str], None) for prop in schema.properties}  # All properties are optional strings
        node_model = create_model(
            schema.type,  # Model name
            **properties,  # Dynamically add properties
            __base__=BaseModel  # Base class
        )
        node_models[schema.type] = node_model

    # Dynamically create Relationship models based on relationship_schemas
    relationship_models = {}
    for schema in relationship_schemas:
        properties = {prop: (Optional[str], None) for prop in schema.properties}  # All properties are optional strings
        relationship_model = create_model(
            schema.type,  # Model name
            source=(str, ...),  # Source node ID
            target=(str, ...),  # Target node ID
            source_type=(str, schema.source),  # Source node type (e.g., "Person")
            target_type=(str, schema.target),  # Target node type (e.g., "Company")
            **properties,  # Dynamically add properties
            __base__=BaseModel  # Base class
        )
        relationship_models[schema.type] = relationship_model

    return Graph

def merge_graphs(graphs: List[Graph]) -> Graph:
    """
    Merges multiple Graph objects into a single Graph object, ensuring uniqueness of nodes and relationships.
    Args:
        graphs (List[Graph]): A list of Graph objects to be merged.
    Returns:
        Graph: A new Graph object containing unique nodes and relationships from all input graphs.
    """
    # Use dictionaries to ensure uniqueness of nodes and relationships
    unique_nodes = {}
    unique_relationships = {}

    for graph in graphs:
        # Add nodes to the unique_nodes dictionary (keyed by node ID)
        for node in graph.nodes:
            if node.id not in unique_nodes:
                unique_nodes[node.id] = node
            else:
                # Merge properties if the node already exists
                existing_node = unique_nodes[node.id]
                for key, value in node.properties.items():
                    if key not in existing_node.properties:
                        existing_node.properties[key] = value

        # Add relationships to the unique_relationships dictionary
        for relationship in graph.relationships:
            # Use a tuple of (source, target, type) as a unique identifier for relationships
            relationship_key = (relationship.source, relationship.target, relationship.type)
            if relationship_key not in unique_relationships:
                unique_relationships[relationship_key] = relationship
            else:
                # Merge properties if the relationship already exists
                existing_relationship = unique_relationships[relationship_key]
                for key, value in relationship.properties.items():
                    if key not in existing_relationship.properties:
                        existing_relationship.properties[key] = value

    # Convert the unique nodes and relationships back to lists
    merged_nodes = list(unique_nodes.values())
    merged_relationships = list(unique_relationships.values())

    # Return the merged Graph
    return Graph(nodes=merged_nodes, relationships=merged_relationships)

########################################
### Function to help to load to Kuzu ###
########################################

def detect_primary_key(nodes: List[Node]) -> Dict[str, Optional[List[str]]]:
    """
    Detects if any property in the list of Node objects has a value equal to the Node's id.

    Args:
        nodes (List[Node]): A list of Node objects.

    Returns:
        Dict[str, Optional[List[str]]]: A dictionary with two keys:
            - "primary_key": A list of property keys that are equal to the id for all nodes, or None if no such property exists.
            - "not_primary_key": A list of property keys that are not equal to the id for all nodes.
    """
    if not nodes:
        return {"primary_key": None, "not_primary_key": []}

    # Initialize sets to track primary and non-primary keys
    primary_key_candidates = set(nodes[0].properties.keys())
    not_primary_keys = set()

    for node in nodes:
        current_primary_candidates = set()
        for key, value in node.properties.items():
            if value == node.id:
                current_primary_candidates.add(key)
            else:
                not_primary_keys.add(key)
        # Intersect with the current node's primary key candidates
        primary_key_candidates &= current_primary_candidates

    # If no primary key candidates remain, set primary_key to None
    primary_key = list(primary_key_candidates) if primary_key_candidates else None

    return {
        "primary_key": primary_key,
        "not_primary_key": list(not_primary_keys)
    }

def pandas_to_sql_types(df: pd.DataFrame) -> dict:
    """
    Transforms pandas DataFrame column dtypes to SQL column types as strings.

    Args:
        df (pd.DataFrame): The pandas DataFrame whose column dtypes need to be converted.

    Returns:
        dict: A dictionary where keys are column names and values are SQL column types as strings.
    """
    # Mapping of pandas dtypes to SQL types
    dtype_mapping = {
        "int64": "BIGINT",
        "int32": "INTEGER",
        "float64": "DOUBLE PRECISION",
        "float32": "FLOAT",
        "object": "STRING",
        "bool": "BOOLEAN",
        "datetime64[ns]": "TIMESTAMP",
        "timedelta[ns]": "INTERVAL",
        "category": "STRING",  # Categories are typically stored as TEXT in SQL
        "string": "STRING",    # Pandas string dtype
        "Int64": "BIGINT",   # Nullable integer type in pandas
        "UInt64": "BIGINT",  # Unsigned integer type in pandas
    }

    # Convert DataFrame dtypes to SQL types
    sql_types = {}
    for column, dtype in df.dtypes.items():
        dtype_str = str(dtype)
        sql_type = dtype_mapping.get(dtype_str, "TEXT")  # Default to TEXT if dtype is not in the mapping
        sql_types[column] = sql_type

    return sql_types
