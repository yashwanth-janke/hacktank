import os
from typing import Union, List, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import logging

from src.data_processing.hire3x_models import CandidateProfile, JobDescription

# Configure logging
logger = logging.getLogger("hire3x.embeddings")

class EmbeddingGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = "./models"):
        """
        Initialize the embedding generator with a pre-trained model.
        
        Args:
            model_name: The name of the sentence-transformers model to use
            cache_dir: Directory to cache the model
        """
        os.makedirs(cache_dir, exist_ok=True)
        
        logger.info(f"Initializing EmbeddingGenerator with model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dimension}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate an embedding for the given text.
        
        Args:
            text: The text to embed
            
        Returns:
            A numpy array containing the embedding
        """
        try:
            embedding = self.model.encode(text, show_progress_bar=False)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            logger.error(f"Text length: {len(text)} characters")
            # Return zero embedding as fallback
            return np.zeros(self.embedding_dimension)
    
    def generate_candidate_embedding(self, candidate: CandidateProfile) -> np.ndarray:
        """
        Generate an embedding for a candidate profile.
        
        Args:
            candidate: The candidate profile
            
        Returns:
            A numpy array containing the embedding
        """
        logger.info(f"Generating embedding for candidate: {candidate.name}")
        text = candidate.to_text()
        return self.generate_embedding(text)
    
    def generate_job_embedding(self, job: JobDescription) -> np.ndarray:
        """
        Generate an embedding for a job description.
        
        Args:
            job: The job description
            
        Returns:
            A numpy array containing the embedding
        """
        logger.info(f"Generating embedding for job: {job.title}")
        text = job.to_text()
        return self.generate_embedding(text)
    
    def generate_batch_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            A numpy array containing the embeddings
        """
        logger.info(f"Generating batch embeddings for {len(texts)} texts")
        try:
            embeddings = self.model.encode(texts, show_progress_bar=True)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            # Return zero embeddings as fallback
            return np.zeros((len(texts), self.embedding_dimension))
    
    def get_model_name(self) -> str:
        """
        Get the name of the sentence transformer model being used.
        
        Returns:
            The model name
        """
        return self.model.get_sentence_embedding_dimension_name()
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings produced by the model.
        
        Returns:
            The embedding dimension
        """
        return self.embedding_dimension
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score (0-1)
        """
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(embedding1, embedding2) / (norm1 * norm2)