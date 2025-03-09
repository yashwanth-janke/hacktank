import json
import os
import sys
from pathlib import Path
import logging

# Add the project root to the Python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.data_processing.hire3x_models import CandidateProfile
from src.embeddings.generator import EmbeddingGenerator
from src.database.vector_db import VectorDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("hire3x.init_db")

def load_candidates(file_path):
    """Load candidate profiles from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            candidates_data = json.load(f)
        
        # Handle both single candidate and list of candidates
        if isinstance(candidates_data, dict):
            candidates_data = [candidates_data]
            
        # Convert to CandidateProfile objects
        candidates = []
        for data in candidates_data:
            try:
                # Convert the candidate data to a CandidateProfile object
                candidate_obj = CandidateProfile(**data)
                candidates.append(candidate_obj)
            except Exception as e:
                logger.error(f"Error parsing candidate data: {e}")
                logger.error(f"Problematic data: {data.get('name', 'Unknown')}")
                continue
                
        return candidates
    except Exception as e:
        logger.error(f"Error loading candidates from {file_path}: {e}")
        return []

def main():
    """Initialize the database with sample data."""
    logger.info("Initializing the Hire3x database with sample data...")
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/chroma", exist_ok=True)
    
    # Check if sample data exists or generate it
    sample_candidates_path = "data/sample_candidates.json"
    if not os.path.exists(sample_candidates_path):
        logger.info("Sample data not found. Generating sample data...")
        try:
            from scripts.generate_realistic_data import generate_realistic_candidates
            generate_realistic_candidates()
            logger.info("Sample data generated successfully.")
        except Exception as e:
            logger.error(f"Failed to generate sample data: {e}")
            logger.error("Please run 'python scripts/generate_realistic_data.py' first.")
            sys.exit(1)
    
    # Initialize components
    logger.info("Initializing embedding generator...")
    embedding_generator = EmbeddingGenerator()
    
    logger.info("Initializing vector database...")
    vector_db = VectorDatabase(embedding_generator=embedding_generator)
    
    # Load and add candidates
    logger.info("Loading and embedding sample candidates...")
    candidates = load_candidates(sample_candidates_path)
    
    if not candidates:
        logger.error("No valid candidates found. Please check your sample data.")
        sys.exit(1)
        
    # Add candidates in smaller batches to avoid memory issues
    batch_size = 5
    total_candidates = len(candidates)
    
    for i in range(0, total_candidates, batch_size):
        end = min(i + batch_size, total_candidates)
        logger.info(f"Adding candidates {i+1} to {end} of {total_candidates}...")
        try:
            vector_db.add_candidates_batch(candidates[i:end])
        except Exception as e:
            logger.error(f"Error adding candidates batch: {e}")
            continue
    
    # Verify database population
    try:
        count = vector_db.get_candidate_count()
        logger.info(f"Successfully initialized the database with {count} candidates.")
        logger.info(f"Database location: {os.path.abspath('data/chroma')}")
    except Exception as e:
        logger.error(f"Error verifying database population: {e}")
    
    logger.info("Database initialization complete.")

if __name__ == "__main__":
    main()