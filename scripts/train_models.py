import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.pipeline.data_loader import load_all_datasets
from backend.app.pipeline.preprocessor import MiningProjectsPreprocessor
from backend.app.services.prediction_service import train_all_models
from backend.app.database import init_db, SessionLocal
from backend.app.utils.logger import logger


def main():
    logger.info("=== LCA Platform Training Script ===")

    logger.info("Step 1: Loading datasets...")
    datasets = load_all_datasets()
    for name, df in datasets.items():
        logger.info(f"  {name}: {len(df)} rows, {len(df.columns)} columns")

    logger.info("Step 2: Initializing database...")
    init_db()

    logger.info("Step 3: Training models...")
    db = SessionLocal()
    try:
        results = train_all_models(db)
        logger.info("=== Training Results ===")
        for name, metrics in results.items():
            score = metrics.get("r2", metrics.get("accuracy", 0))
            cv = metrics.get("cv_r2_mean", 0)
            logger.info(f"  {name}: score={score:.4f}, cv={cv:.4f}")
    finally:
        db.close()

    logger.info("=== Training Complete ===")


if __name__ == "__main__":
    main()
