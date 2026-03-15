import os
import subprocess
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys


current = Path(__file__).resolve().parent
PROJECT_ROOT = None
for _ in range(5):
    if current.name == "project_root":
        PROJECT_ROOT = current
        break
    current = current.parent

if not PROJECT_ROOT:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

SCRAPER_DIR = PROJECT_ROOT / "Machine Learning and Data Cleaning" / "data" / "raw" / "scrapers"
DATA_DIR = PROJECT_ROOT / "Machine Learning and Data Cleaning" / "data" / "raw" / "jobs"
LOG_DIR = PROJECT_ROOT / "Machine Learning and Data Cleaning" / "data" / "logs"

# ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)

# setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "scraper_status.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ScraperOrchestrator")

def cleanup_old_files(directory, days=30):
    # delete jobs older ththan 30 days
    logger.info(f"starting cleanup in {directory} (older than {days} days)")
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    
    count = 0
    if not directory.exists():
        return
        
    for item in directory.glob("*"):
        if item.is_file():
            # check modification time
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if mtime < cutoff:
                try:
                    item.unlink()
                    count += 1
                    logger.info(f"deleted expired: {item.name}")
                except Exception as e:
                    logger.error(f"failed to delete {item.name}: {e}")
    
    logger.info(f"cleanup finished. removed {count} files.")

def run_scraper(name, script_path, args=None):
    """run a python scraper script and stream output in real-time"""
    logger.info(f"starting scraper: {name}")
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
        
    start_time = time.time()
    # Ensure subprocesses use UTF-8
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    try:
        # stream output in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(script_path.parent),
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace',
            env=env
        )

        for line in process.stdout:
            print(f"[{name}] {line.strip()}", flush=True)
            # optionally log important lines
            if any(kw in line.lower() for kw in ["error", "success", "scraped", "saving"]):
                logger.info(f"{name}: {line.strip()}")

        process.wait()
        duration = time.time() - start_time
        
        if process.returncode == 0:
            logger.info(f"scraper {name} finished successfully in {duration:.1f}s")
            return True
        else:
            logger.error(f"scraper {name} failed with exit code {process.returncode}")
            return False
            
    except Exception as e:
        logger.error(f"unexpected error running {name}: {e}")
        return False

def validate_data(file_path, min_rows=1):
    """Basic data validation check."""
    if not file_path.exists():
        logger.error(f"Validation failed: File not found {file_path}")
        return False
    
    # Check file size
    if file_path.stat().st_size < 100:
        logger.warning(f"Validation warning: File seems too small {file_path}")
        
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        row_count = len(df)
        if row_count < min_rows:
            logger.error(f"Validation failed: {file_path.name} has only {row_count} rows (min: {min_rows})")
            return False
        logger.info(f"Validation passed: {file_path.name} has {row_count} rows")
        return True
    except Exception as e:
        logger.error(f"Validation error for {file_path.name}: {e}")
        return False

def orchestrate():
    """main orchestration flow"""
    logger.info("="*50)
    logger.info("SCHEDULED SCRAPING START")
    logger.info("="*50)
    
    try:
        #  cleanup old raw files
        cleanup_old_files(DATA_DIR, days=30)
        
        scrapers = [
            ("TopJobs", SCRAPER_DIR / "topjobs.py", ["2"]), # run 2 pages in auto mode
            ("Ikman", SCRAPER_DIR / "ikmanjobs.py", []),
            ("Xpress", SCRAPER_DIR / "generalxpess.py", ["2"]) # run 2 pages in auto mode
        ]
        
        results = {}
        for name, path, args in scrapers:
            if path.exists():
                success = run_scraper(name, path, args)
                results[name] = "SUCCESS" if success else "FAILED"
            else:
                logger.warning(f"scraper script not found: {path}")
                results[name] = "NOT FOUND"
                
    except KeyboardInterrupt:
        logger.warning("Orchestration interrupted by user. Proceeding to merge available data...")
    except Exception as e:
        logger.error(f"Critical error during orchestration: {e}")
    finally:
        #  merge all jobs (even if some failed or we were interrupted)
        logger.info("Starting final data merge (Safety Flow)...")
        merge_script = PROJECT_ROOT / "Machine Learning and Data Cleaning" / "scripts" / "merge_all_jobs.py"
        if merge_script.exists():
            run_scraper("MergeAllJobs", merge_script, [])
            
            #  Final validation of master file
            master_file = PROJECT_ROOT / "Machine Learning and Data Cleaning" / "data" / "processed" / "all_jobs_master.csv"
            if validate_data(master_file, min_rows=100):
                logger.info("Pipeline completed successfully with valid data.")
            else:
                logger.error("Pipeline finished but master data failed validation!")
        else:
            logger.warning(f"merge script not found: {merge_script}")

        #  Regenerate model artifacts (.pt embedding cache) now that data is fresh
        logger.info("="*50)
        logger.info("REGENERATING MODEL ARTIFACTS (Embedding Cache)")
        artifact_script = Path(__file__).parent / "generate_model_artifacts.py"
        if artifact_script.exists():
            run_scraper("ArtifactGenerator", artifact_script, [])
            logger.info("Embedding cache updated — next engine load will be fast.")
        else:
            logger.warning(f"Artifact generator not found: {artifact_script}")
                
        #  summary
        logger.info("="*50)
        logger.info("SCRAPING SUMMARY")
        if 'results' in locals():
            for name, status in results.items():
                logger.info(f"- {name}: {status}")
        else:
            logger.info("- Scraper loop did not complete.")
        logger.info("="*50)

if __name__ == "__main__":
    orchestrate()
