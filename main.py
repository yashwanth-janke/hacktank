import uvicorn
import os
import argparse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("hire3x")

def create_directories():
    """Create necessary directories for the application."""
    logger.info("Creating application directories...")
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./data/chroma", exist_ok=True)
    os.makedirs("./models", exist_ok=True)
    os.makedirs("./pdfs", exist_ok=True)
    os.makedirs("./frontend", exist_ok=True)

def setup_environment():
    """Set up environment variables and check for dependencies."""
    # Check if ChromaDB is available
    try:
        import chromadb
        logger.info("ChromaDB is available.")
    except ImportError:
        logger.error("ChromaDB is not installed. Please install it using 'pip install chromadb'.")
        exit(1)
    
    # Check if SentenceTransformers is available
    try:
        import sentence_transformers
        logger.info("SentenceTransformers is available.")
    except ImportError:
        logger.error("SentenceTransformers is not installed. Please install it using 'pip install sentence-transformers'.")
        exit(1)
    
    # Check if frontend files exist
    frontend_path = Path("frontend/index.html")
    if not frontend_path.exists():
        logger.warning("Frontend files not found in 'frontend' directory. The API will work, but you might need to setup the frontend separately.")

def main():
    """Main entry point for the application."""
    logger.info("Starting Hire3x AI-Powered Candidate Matching System...")
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Hire3x AI-Powered Candidate Matching System")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--log-level", type=str, default="info", choices=["debug", "info", "warning", "error", "critical"], 
                        help="Set the logging level")
    args = parser.parse_args()
    
    # Create necessary directories
    create_directories()
    
    # Set up environment variables and check dependencies
    setup_environment()
    
    # Configure logging level
    log_level = getattr(logging, args.log_level.upper())
    logger.setLevel(log_level)
    
    # Log startup information
    logger.info(f"Server starting on http://{args.host}:{args.port}")
    
    # Run the FastAPI app
    uvicorn.run(
        "src.api.enhanced_app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level.lower()
    )

if __name__ == "__main__":
    main()