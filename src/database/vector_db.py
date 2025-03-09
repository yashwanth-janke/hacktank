import os
from typing import List, Dict, Any, Tuple, Optional
import chromadb
from chromadb.utils import embedding_functions
import numpy as np
import logging

from src.data_processing.hire3x_models import CandidateProfile, JobDescription
from src.embeddings.generator import EmbeddingGenerator

# Configure logging
logger = logging.getLogger("hire3x.vector_db")

class VectorDatabase:
    def __init__(
        self, 
        collection_name: str = "candidates", 
        persist_directory: str = "./data/chroma",
        embedding_generator: Optional[EmbeddingGenerator] = None
    ):
        """
        Initialize the vector database with ChromaDB.
        
        Args:
            collection_name: Name of the collection to use
            persist_directory: Directory to persist the database
            embedding_generator: EmbeddingGenerator instance to use
        """
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        logger.info(f"Initializing ChromaDB client with persistence at {persist_directory}")
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            logger.info("ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
        
        # Store the embedding generator
        self.embedding_generator = embedding_generator
        
        # Initialize collection with embedding function
        try:
            if embedding_generator:
                # Create a custom embedding function that uses our embedding generator
                def generate_embeddings(texts):
                    return [self.embedding_generator.generate_embedding(text).tolist() for text in texts]
                
                # Create a wrapper class for ChromaDB
                class CustomEmbeddingFunction(embedding_functions.EmbeddingFunction):
                    def __call__(self, texts):
                        return generate_embeddings(texts)
                
                logger.info(f"Creating/getting collection '{collection_name}' with custom embedding function")
                self.collection = self.client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=CustomEmbeddingFunction()
                )
            else:
                # Use default embedding function
                logger.info(f"Creating/getting collection '{collection_name}' with default embedding function")
                self.collection = self.client.get_or_create_collection(
                    name=collection_name
                )
            
            logger.info(f"Collection initialized with {self.collection.count()} documents")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise
    
    def add_candidate(self, candidate: CandidateProfile) -> None:
        """
        Add a candidate to the database.
        
        Args:
            candidate: The candidate profile to add
        """
        try:
            logger.info(f"Adding candidate: {candidate.name}")
            
            # Generate embedding if we have an embedding generator
            embedding = None
            if self.embedding_generator:
                embedding = self.embedding_generator.generate_candidate_embedding(candidate).tolist()
            
            # Convert candidate to text for embedding
            text = candidate.to_text()
            
            # Get metadata
            metadata = candidate.get_metadata()
            
            # Add to collection
            self.collection.add(
                ids=[candidate.id],
                embeddings=[embedding] if embedding else None,
                documents=[text],
                metadatas=[metadata]
            )
            
            logger.info(f"Successfully added candidate: {candidate.name}")
        except Exception as e:
            logger.error(f"Failed to add candidate {candidate.name}: {e}")
            raise
    
    def add_candidates_batch(self, candidates: List[CandidateProfile]) -> None:
        """
        Add multiple candidates to the database.
        
        Args:
            candidates: List of candidate profiles to add
        """
        if not candidates:
            logger.warning("No candidates provided to add_candidates_batch")
            return
            
        try:
            logger.info(f"Adding batch of {len(candidates)} candidates")
            
            ids = []
            texts = []
            metadatas = []
            embeddings = []
            
            for candidate in candidates:
                ids.append(candidate.id)
                texts.append(candidate.to_text())
                metadatas.append(candidate.get_metadata())
                
                if self.embedding_generator:
                    embedding = self.embedding_generator.generate_candidate_embedding(candidate).tolist()
                    embeddings.append(embedding)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings if embeddings else None,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully added {len(candidates)} candidates")
        except Exception as e:
            logger.error(f"Failed to add candidates batch: {e}")
            raise
    
    def search_candidates(
        self, 
        job: JobDescription, 
        top_k: int = 10, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for candidates matching a job description.

        Args:
            job: The job description to search with
            top_k: Number of top results to return
            filters: Optional filters to apply
        Returns:
            List of matching candidates with scores
        """
        try:
            logger.info(f"Searching for candidates matching job: {job.title}")
            
            job_text = job.to_text()
            job_embedding = None
            
            if self.embedding_generator:
                job_embedding = self.embedding_generator.generate_job_embedding(job).tolist()
            
            # Prepare where clause for filters
            where_clause = None
            if filters:
                # ChromaDB expects combined filters in a specific format
                if len(filters) > 1:
                    # For multiple conditions, use $and operator
                    where_clause = {"$and": []}
                    for key, value in filters.items():
                        where_clause["$and"].append({key: value})
                else:
                    # For single condition, use as is
                    where_clause = filters
        
        # Run the query
            logger.info(f"Executing query with top_k={top_k}, filters={where_clause}")
            results = self.collection.query(
                query_embeddings=[job_embedding] if job_embedding else None,
                query_texts=[job_text] if not job_embedding else None,
                n_results=top_k,
                where=where_clause
            )
        
            formatted_results = self._format_results(results)
            logger.info(f"Query returned {len(formatted_results)} results")
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching candidates: {e}")
            raise
        
    def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format the query results.
        
        Args:
            results: The raw query results from ChromaDB
            
        Returns:
            Formatted results
        """
        formatted_results = []
        
        if not results or not results.get("ids") or not results["ids"][0]:
            logger.warning("No results to format")
            return formatted_results
        
        for i in range(len(results["ids"][0])):
            result = {
                "id": results["ids"][0][i],
                "score": results["distances"][0][i] if "distances" in results else None,
                "metadata": results["metadatas"][0][i] if "metadatas" in results else {},
                "document": results["documents"][0][i] if "documents" in results else ""
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def delete_candidate(self, candidate_id: str) -> None:
        """
        Delete a candidate from the database.
        
        Args:
            candidate_id: ID of the candidate to delete
        """
        try:
            logger.info(f"Deleting candidate with ID: {candidate_id}")
            self.collection.delete(ids=[candidate_id])
            logger.info(f"Successfully deleted candidate {candidate_id}")
        except Exception as e:
            logger.error(f"Failed to delete candidate {candidate_id}: {e}")
            raise
    
    def get_candidate_count(self) -> int:
        """
        Get the number of candidates in the database.
        
        Returns:
            Number of candidates
        """
        try:
            count = self.collection.count()
            logger.info(f"Database contains {count} candidates")
            return count
        except Exception as e:
            logger.error(f"Failed to get candidate count: {e}")
            raise
    
    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific candidate by ID.
        
        Args:
            candidate_id: ID of the candidate to retrieve
            
        Returns:
            Candidate data or None if not found
        """
        try:
            logger.info(f"Retrieving candidate with ID: {candidate_id}")
            result = self.collection.get(ids=[candidate_id])
            
            if not result or not result["ids"]:
                logger.warning(f"Candidate {candidate_id} not found")
                return None
            
            candidate_data = {
                "id": result["ids"][0],
                "metadata": result["metadatas"][0] if "metadatas" in result else {},
                "document": result["documents"][0] if "documents" in result else ""
            }
            
            logger.info(f"Successfully retrieved candidate {candidate_id}")
            return candidate_data
        except Exception as e:
            logger.error(f"Failed to retrieve candidate {candidate_id}: {e}")
            return None
    
    def update_candidate(self, candidate: CandidateProfile) -> None:
        """
        Update an existing candidate in the database.
        
        Args:
            candidate: The updated candidate profile
        """
        try:
            logger.info(f"Updating candidate: {candidate.name}")
            
            # Check if candidate exists
            existing = self.get_candidate(candidate.id)
            if not existing:
                logger.warning(f"Candidate {candidate.id} not found, adding as new")
                self.add_candidate(candidate)
                return
            
            # Delete the existing candidate
            self.delete_candidate(candidate.id)
            
            # Add the updated candidate
            self.add_candidate(candidate)
            
            logger.info(f"Successfully updated candidate: {candidate.name}")
        except Exception as e:
            logger.error(f"Failed to update candidate {candidate.name}: {e}")
            raise