import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.main import app
from backend.app.database import init_db, SessionLocal
from backend.app.services.dataset_service import load_datasets, register_datasets_in_db
from backend.app.utils.logger import logger
import argparse


def setup_database():
    logger.info("Initializing database...")
    init_db()
    db = SessionLocal()
    try:
        register_datasets_in_db(db)
    finally:
        db.close()
    logger.info("Database setup complete")


def setup_models():
    logger.info("Training ML models...")
    from backend.app.services.prediction_service import train_all_models
    db = SessionLocal()
    try:
        results = train_all_models(db)
        for name, metrics in results.items():
            score = metrics.get("r2", metrics.get("accuracy", 0))
            logger.info(f"  {name}: {score:.4f}")
    finally:
        db.close()
    logger.info("Model training complete")


def setup_all():
    logger.info("Running full project setup...")
    load_datasets()
    setup_database()
    setup_models()
    logger.info("Setup complete. Run 'python run.py' to start the application.")


def main():
    parser = argparse.ArgumentParser(description="LCA Platform Setup")
    parser.add_argument("command", choices=["db", "models", "all", "serve"], help="Setup command")
    args = parser.parse_args()

    if args.command == "db":
        setup_database()
    elif args.command == "models":
        load_datasets()
        setup_models()
    elif args.command == "all":
        setup_all()
    elif args.command == "serve":
        import uvicorn
        uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
