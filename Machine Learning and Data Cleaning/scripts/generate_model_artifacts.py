import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from pathlib import Path
import sys
import os


def generate_artifacts():
    """
    Pre-computes all SBERT embeddings matching EXACTLY the logic in recommendation_engine.py.
    Saves .pt files to models/ dir to prevent slow reloads on every test run.
    Called automatically after scraping completes via orchestrate_scraping.py.
    """
    # --- Paths ---
    SCRIPTS_DIR = Path(__file__).resolve().parent
    ML_ROOT = SCRIPTS_DIR.parent
    PROCESSED_DIR = ML_ROOT / "data" / "processed"
    ESCO_DIR = ML_ROOT / "data" / "raw" / "esco"
    MODELS_DIR = ML_ROOT / "models"
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # NOTE: Engine swaps these - academic_courses is actually the professional/skill-gap pool
    PROFESSIONAL_COURSES_PATH = PROCESSED_DIR / "academic_courses_master.csv"  # -> courses_df
    ACADEMIC_COURSES_PATH = PROCESSED_DIR / "all_courses_master.csv"           # -> academic_df
    JOBS_PATH = PROCESSED_DIR / "all_jobs_master.csv"

    print("\n" + "="*60)
    print("   PATHFINDER+ MODEL ARTIFACT GENERATOR")
    print("   Regenerating .pt embedding cache files...")
    print("="*60)

    print("\n[1/4] Loading Transformer model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # ------------------------------------------------------------------
    # 2. ESCO Occupation Embeddings
    # ------------------------------------------------------------------
    esco_emb_file = MODELS_DIR / "esco_occ_embeddings.pt"
    print(f"\n[2/4] Processing ESCO Occupations from {ESCO_DIR}...")
    esco_occ_path = ESCO_DIR / "occupations_en.csv"
    if esco_occ_path.exists():
        esco_occ = pd.read_csv(esco_occ_path)
        esco_titles = esco_occ["preferredLabel"].fillna("").tolist()
        print(f"       Encoding {len(esco_titles)} occupations...")
        esco_embs = model.encode(esco_titles, convert_to_tensor=True, show_progress_bar=True)
        torch.save(esco_embs, esco_emb_file)
        print(f"       Saved -> {esco_emb_file.name} ({len(esco_embs)} embeddings)")
    else:
        print(f"       [WARN] ESCO file not found: {esco_occ_path}")

    # ------------------------------------------------------------------
    # 3. Professional Course Embeddings (from academic_courses_master.csv)
    #    Engine logic: course_title + cat/category + description
    # ------------------------------------------------------------------
    print(f"\n[3/4] Processing Professional Skill-Gap Courses ({PROFESSIONAL_COURSES_PATH.name})...")
    if PROFESSIONAL_COURSES_PATH.exists():
        courses_df = pd.read_csv(PROFESSIONAL_COURSES_PATH)

        # Standardize column names (engine does this too)
        if "course_title" not in courses_df.columns and "course_name" in courses_df.columns:
            courses_df.rename(columns={"course_name": "course_title"}, inplace=True)

        cat_col = "cat" if "cat" in courses_df.columns else "category"
        if cat_col not in courses_df.columns:
            courses_df[cat_col] = ""
        if "description" not in courses_df.columns:
            courses_df["description"] = ""

        course_texts = (
            courses_df["course_title"].fillna("")
            + " " + courses_df[cat_col].fillna("")
            + " " + courses_df["description"].fillna("")
        ).tolist()

        print(f"       Encoding {len(course_texts)} professional courses...")
        course_embs = model.encode(course_texts, convert_to_tensor=True, show_progress_bar=True)

        # Engine looks for course_embeddings_{stem}.pt
        prof_emb_file = MODELS_DIR / f"course_embeddings_{PROFESSIONAL_COURSES_PATH.stem}.pt"
        torch.save(course_embs, prof_emb_file)
        print(f"       Saved -> {prof_emb_file.name} ({len(course_embs)} embeddings)")
    else:
        print(f"       [WARN] Professional courses not found: {PROFESSIONAL_COURSES_PATH}")

    # ------------------------------------------------------------------
    # 4. Academic Degree Program Embeddings (from all_courses_master.csv)
    #    Engine logic: course_title + cat/category + description
    # ------------------------------------------------------------------
    academic_emb_file = MODELS_DIR / "academic_embeddings.pt"
    print(f"\n[4/4] Processing Academic Degree Programs ({ACADEMIC_COURSES_PATH.name})...")
    if ACADEMIC_COURSES_PATH.exists():
        academic_df = pd.read_csv(ACADEMIC_COURSES_PATH)

        # Standardize
        if "course_title" not in academic_df.columns and "course_name" in academic_df.columns:
            academic_df.rename(columns={"course_name": "course_title"}, inplace=True)

        cat_col = "cat" if "cat" in academic_df.columns else "category"
        if cat_col not in academic_df.columns:
            academic_df[cat_col] = ""
        if "description" not in academic_df.columns:
            academic_df["description"] = ""

        acad_texts = (
            academic_df["course_title"].fillna("")
            + " " + academic_df[cat_col].fillna("")
            + " " + academic_df["description"].fillna("")
        ).tolist()

        print(f"       Encoding {len(acad_texts)} academic programs...")
        academic_embs = model.encode(acad_texts, convert_to_tensor=True, show_progress_bar=True)
        torch.save(academic_embs, academic_emb_file)
        print(f"       Saved -> {academic_emb_file.name} ({len(academic_embs)} embeddings)")
    else:
        print(f"       [WARN] Academic courses not found: {ACADEMIC_COURSES_PATH}")

    # ------------------------------------------------------------------
    # 5. Job Embeddings (title column)
    # ------------------------------------------------------------------
    job_emb_file = MODELS_DIR / "job_embeddings.pt"
    print(f"\n[BONUS] Processing Jobs ({JOBS_PATH.name})...")
    if JOBS_PATH.exists():
        jobs_df = pd.read_csv(JOBS_PATH)
        if "title" not in jobs_df.columns and "Job Title" in jobs_df.columns:
            jobs_df.rename(columns={"Job Title": "title"}, inplace=True)

        job_titles = jobs_df["title"].fillna("").tolist()
        print(f"       Encoding {len(job_titles)} jobs...")
        job_embs = model.encode(job_titles, convert_to_tensor=True, show_progress_bar=True)
        torch.save(job_embs, job_emb_file)
        print(f"       Saved -> {job_emb_file.name} ({len(job_embs)} embeddings)")
    else:
        print(f"       [WARN] Jobs not found: {JOBS_PATH}")

    print("\n" + "="*60)
    print("   ARTIFACT GENERATION COMPLETE")
    print(f"   All .pt files saved to: {MODELS_DIR}")
    print("   Next engine load will use cache — significantly faster!")
    print("="*60 + "\n")


if __name__ == "__main__":
    generate_artifacts()
