#!/usr/bin/env python
# coding: utf-8

# lib imports
import json
from time import sleep
from crewai.knowledge.storage.knowledge_storage import KnowledgeStorage
from crewai.utilities.paths import db_storage_path
from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings
import pymilvus
from pymilvus import model as pymilvus_model
import hashlib
import sys
from typing import Any, Dict, List, Optional, Union, cast
from mlx_lm import load, generate
from openinference.semconv.trace import SpanAttributes
from opentelemetry.trace import Status, StatusCode
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor

# import own utility functions
from pdf_preprocessing import *
from agentic_chunker import load_template

# settings
version = '1.1.0'
test = False
# Cut the input text to paragraph, if False it will cut to PDF pages
cut_in_paragraph = False


class MilvusKnowledgeStorage:
    """
    Extends Storage to handle embeddings for memory entries, improving
    search efficiency.
    """

    def __init__(
        self,
        embedder: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = "knowledge",
    ):
        """
        Initializes the MilvusKnowledgeStorage with an optional embedder and collection name.

        Args:
            embedder (Optional[Dict[str, Any]]): An optional embedder for encoding documents
                into embeddings. If not provided, a default embedder will be created.
            collection_name (Optional[str]): The name of the collection to use in Milvus.
                If not provided, it defaults to "knowledge".
        """

        self.collection_name = collection_name
        self.db_path = os.path.join("knowledge_milvus.db")
        self.app = pymilvus.MilvusClient(self.db_path)

        # load collection if exist
        if self.app.has_collection(collection_name=self.collection_name):
            self.app.load_collection(collection_name=self.collection_name)

        if embedder is not None:
            self.embedder = embedder
        else:
            # use default embedder
            # this will use HuggingFace FinLang embeddings
            # see: https://huggingface.co/FinLang/finance-embeddings-investopedia
            # for more details
            self.embedder = self._create_default_embedding_function()

    def search(
        self,
        query: List[str],
        limit: int = 0,
        filter: Optional[dict] = None, # not used at this moment
        score_threshold: float = 0.35,
    ) -> List[Dict[str, Any]]:
        """
        Searches the Milvus collection for documents similar to the provided query.

        Args:
            query (List[str]): A list of query strings to search for in the collection.
            limit (int): The maximum number of results to return. If 0, returns all results.
            filter (Optional[dict]): A filter to apply to the search results. Not used
                in this implementation, but can be extended in the future.
            score_threshold (float): The minimum score threshold for results to be included.
                Results with a score below this threshold will be excluded.
        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the search results,
                where each dictionary contains the document ID, metadata, context, and score.
        """

        fetched = self.app.search(
            collection_name=self.collection_name,
            data=self.embedder.encode_documents(query),
            limit=30,
            search_params={"metric_type": "COSINE", "params": {}},
            output_fields=[
                    "text", 
            ],
        )

        results = []

        for one_query_result in fetched:  
            for doc in one_query_result:
                result = {
                    'id': doc['id'],  
                    'context': doc['entity']['text'],
                    'score': doc['distance']
                }
                if result["score"] >= score_threshold:
                    results.append(result)
                if limit > 0 and len(results) >= limit:
                    break

        return results

    def initialize_knowledge_storage(self):
        """
        Initializes the Milvus knowledge storage by creating a collection if it does not exist.
        If the collection already exists, it resets the storage by dropping existing collections
        and creating a new one.
        """

        # clear previous dataset if exist
        if self.app.has_collection(collection_name=self.collection_name):
            self.reset()

        if not self.app.has_collection(collection_name=self.collection_name):
            print(f'Create {self.collection_name} collection')

            # Create schema
            schema = self.app.create_schema(
                auto_id=True,
                enable_dynamic_field=True,
            )

            dimension = 768 # dimension for HuggingFace FinLang

            # add fields to schema
            schema.add_field(field_name="id", datatype=pymilvus.DataType.INT64, is_primary=True)
            schema.add_field(field_name="vector", datatype=pymilvus.DataType.FLOAT_VECTOR, dim=dimension)
            schema.add_field(field_name="text", datatype=pymilvus.DataType.VARCHAR, max_length=20000)

            index_params = self.app.prepare_index_params()
            index_params.add_index(
                field_name="vector",
                index_type="AUTOINDEX",
                metric_type="COSINE"
            )

            # Collection does not exist create it
            self.app.create_collection(
                collection_name=self.collection_name,
                dimension=dimension,
                schema=schema,
                index_params=index_params,
                consistency_level='Strong', # need for hybrid search,
                vector_field=["vector"],
            )

        if self.app:
            self.app.load_collection(collection_name=self.collection_name)

    def reset(self):
        """
        Resets the Milvus knowledge storage by dropping all collections and creating a new one.
        """
        if not self.app:
            self.app = pymilvus.MilvusClient(self.db_path)

        # delete collections
        collections = self.app.list_collections()
        for collection in collections:
            self.app.drop_collection(collection_name=collection)

        # create new app
        self.app.close()
        sleep(3)
        self.app = pymilvus.MilvusClient(self.db_path)


    def save(
            self,
            documents: List[str],
            metadata: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ):
        """
        Saves documents and their metadata to the Milvus collection.

        Args:
            documents (List[str]): A list of document strings to be saved.
            metadata (Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]): Optional metadata associated with the documents.
                If provided as a list, it should match the length of the documents list.
                If provided as a single dictionary, it will be applied to all documents.

        """
        if not self.app:
            self.app = pymilvus.MilvusClient(self.db_path)

        # Create a dictionary to store unique documents
        unique_docs = {}

        # Generate IDs and create a mapping of id -> (document, metadata)
        for idx, doc in enumerate(documents):
            doc_id = hashlib.sha256(doc.encode("utf-8")).hexdigest()
            doc_metadata = None
            if metadata is not None:
                if isinstance(metadata, list):
                    doc_metadata = metadata[idx]
                else:
                    doc_metadata = metadata
            unique_docs[doc_id] = (doc, doc_metadata)

        # prepare data
        data = []
        data_size = 0
        unique_docs = [ {'text': doc, 'metadata': meta} for doc, meta in unique_docs.values() ]

        uniques_texts = [ doc['text'] for doc in unique_docs ]
        uniques_docs_embeddings = self.embedder.encode_documents(uniques_texts)
        for i in range(len(unique_docs)):
            this_doc = {
                'vector': uniques_docs_embeddings[i],
                'text': unique_docs[i]['text'],
            }            

            data.append(this_doc)
            data_size += sys.getsizeof(this_doc)

        print(f'Loading data. Size: {data_size}')
        try:
            # batch load as Milvus has a 64Mb load limit, 
            # see: https://milvus.io/docs/limitations.md#Input-and-Output-per-RPC
            avg = len(data)/ 2
            last = 0
            while last < len(data):
                slice = data[int(last):int(last + avg)]
                self.app.insert(collection_name=self.collection_name, data=slice)
                last += avg
        except Exception as e:
            print(f"Failed to upsert documents: {e}")
            raise

    def _create_default_embedding_function(self) -> pymilvus_model.dense.SentenceTransformerEmbeddingFunction:
        """
        Creates a default embedding function using the HuggingFace FinLang embeddings.
        This function uses the 'FinLang/finance-embeddings-investopedia' model to encode
        documents into embeddings.

        Returns:
            pymilvus_model.dense.SentenceTransformerEmbeddingFunction: An instance of the embedding function.
        """
        return pymilvus_model.dense.SentenceTransformerEmbeddingFunction(
            model_name='FinLang/finance-embeddings-investopedia'
        )


# In[8]:


if test:
    # Initialize Milvus DB
    knowledge = MilvusKnowledgeStorage()
    knowledge.initialize_knowledge_storage()

    # load data
    documents = [ doc.page_content for doc in paragraphs]
    metadata = [ doc.metadata for doc in paragraphs]
    knowledge.save(documents=documents, metadata=metadata)

    # search in the DB
    print(json.dumps(knowledge.search(
        ["My first question is on the smelter and refinery expansion at Olympic Dam, the first phase of FID by 2027. What could be the order of magnitude of capex for that? Is it very simplistically to reduce the uranium levels and take more ore from the OZ Minerals assets? When would that expansion be ready, assuming it is approved? Are we talking by 2030, or beyond that"],
        limit=10,
        score_threshold=0.35
    ), indent=4))


# # Implement RAG


class MyRAG:
    """
    A simple RAG implementation that uses Milvus as a knowledge base.
    """
    def __init__(
        self, 
        tracer=None,
        data: List[Document]=None, 
        model_name: str="qwen/qwen3-30b-a3b:free",
    ):
        """
        Initializes the MyRAG instance with the provided data.
        Args:
            tracer: the openinference tracer
            data (List[Document]): A list of Langchain Document objects containing the knowledge base.
            model_name (str): a LLM model name

        """
        self.tracer = tracer
        self.model_name = model_name
        # Initialize Milvus DB
        self.knowledge = MilvusKnowledgeStorage()

        if data is not None:
            self.knowledge.initialize_knowledge_storage()
            # load data
            documents = [ doc.page_content for doc in data]
            metadata = [ doc.metadata for doc in data]
            self.knowledge.save(documents=documents, metadata=metadata)

        # system prompt
        system_prompt_template = load_template("basic_rag_system.yaml")
        self.system_prompt = system_prompt_template({})

        # LLM
        self.llm = define_llm(model_name)

    def invoke(self, question: str) -> str:
        """
        Invokes the RAG system to answer a question using the knowledge base.

        Args:
            question (str): The question to be answered.
        Returns:
            str: The answer to the question generated by the RAG system.
        Raises:
            ValueError: If the question is empty or not provided.
        """
        # get result from knowledge 
        context = json.dumps(
            self.knowledge.search(
                [question],
                limit=10,
                score_threshold=0.15
            ),
            indent=4
        )
        user_prompt_template = load_template("basic_rag_user.yaml")
        user_prompt = user_prompt_template({
            "context": context,
            "question": question
        })

        messages = [
            ('system', self.system_prompt),
            ('user', user_prompt)
        ]

        if self.tracer is not None:
            print("tracing")
            # set up tracing
            with self.tracer.start_as_current_span("rag_invoke") as child_span:
                child_span.set_attribute(SpanAttributes.INPUT_VALUE, context)
                child_span.set_attribute(SpanAttributes.LLM_MODEL_NAME, self.model_name)

                try:
                    rag_answer = self.llm.invoke(messages).content
                except Exception as e:
                    child_span.set_attribute(SpanAttributes.OUTPUT_VALUE, str(e))
                    child_span.set_status(Status(StatusCode.ERROR))
                    return f"Error in LLM invocation: {f}"

                child_span.set_attribute(SpanAttributes.OUTPUT_VALUE, rag_answer)
                child_span.set_status(Status(StatusCode.OK))
                return rag_answer
        else:
            try:
                rag_answer = self.llm.invoke(messages).content
                return rag_answer
            except Exception as e:
                return f"Error in LLM invocation: {e}"







