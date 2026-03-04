
import pandas as pd
from pathlib import Path

def check_health():
    print("Checking data files and health\n")
    
    # 1. Paths
    root = Path(__file__).parent.parent
    jobs_path = root / "data/processed/all_jobs_master.csv"
    courses_path = root / "data/processed/all_courses_master.csv"
    
    # 2. Jobs Analysis
    if jobs_path.exists():
        print(f"Loading Jobs: {jobs_path.name}")
        df_jobs = pd.read_csv(jobs_path)
        print(f"Total Rows: {len(df_jobs)}")
        
        # Duplicates
        subset_cols = ['title', 'company', 'location']
        # filter out cols that exist
        subset_cols = [c for c in subset_cols if c in df_jobs.columns]
        dupes = df_jobs.duplicated(subset=subset_cols, keep=False).sum()
        print(f"Potential Duplicates (based on {subset_cols}): {dupes}")
        
        # Missing Data
        missing_skills = df_jobs['extracted_skills'].isna().sum()
        print(f"Missing 'extracted_skills': {missing_skills} ({missing_skills/len(df_jobs)*100:.1f}%)")
        
        missing_desc = df_jobs['description'].isna().sum()
        print(f"Missing 'description': {missing_desc}")
        
        print(f"Unique Job Titles: {df_jobs['title'].nunique()}")
        print("-" * 30)
    else:
        print(f"CRITICAL: Jobs file not found at {jobs_path}")

    # 3. Courses Analysis
    if courses_path.exists():
        print(f"\nLoading Courses: {courses_path.name}")
        df_courses = pd.read_csv(courses_path)
        print(f"Total Rows: {len(df_courses)}")
        
        # Duplicates
        subset_cols = ['course_name', 'institute', 'duration']
        # normalize col names if needed (script handles this but we check raw here)
        if 'course_title' in df_courses.columns: subset_cols[0] = 'course_title'
        if 'provider' in df_courses.columns: subset_cols[1] = 'provider'
        
        subset_cols = [c for c in subset_cols if c in df_courses.columns]
        dupes = df_courses.duplicated(subset=subset_cols, keep=False).sum()
        print(f"Potential Duplicates (based on {subset_cols}): {dupes}")
        
        print(f"Unique Providers: {df_courses[subset_cols[1]].nunique() if len(subset_cols)>1 else 'N/A'}")
        
        # Check for Fee/Duration availability
        print("\n--- FEATURE READINESS (Budget & Duration) ---")
        if 'fee' in df_courses.columns:
            missing_fee = df_courses['fee'].isna().sum()
            print(f"Missing 'fee': {missing_fee} ({missing_fee/len(df_courses)*100:.1f}%)")
        else:
             print("Column 'fee' NOT FOUND.")

        if 'duration' in df_courses.columns:
            missing_dur = df_courses['duration'].isna().sum()
            print(f"Missing 'duration': {missing_dur} ({missing_dur/len(df_courses)*100:.1f}%)")
        else:
             print("Column 'duration' NOT FOUND.")
             
        print("-" * 30)
    else:
        print(f"CRITICAL: Courses file not found at {courses_path}")

    # 4. New Data Assets Check
    print("\n NEW ASSETS CHECK")
    
    # Internship Paths (part of career progressions)
    prog_path = root / "data/processed/career_progressions.csv"
    if prog_path.exists():
        df_prog = pd.read_csv(prog_path)
        intern_count = df_prog['current_role'].str.contains('Intern', na=False).sum()
        print(f"Career Progressions: {len(df_prog)} paths")
        print(f"Internship Paths: {intern_count} (Should be > 20)")
    else:
        print(" career_progressions.csv NOT FOUND")

    # Paylab Data
    paylab_path = root / "data/config/paylab_salary_mapping_full.csv"
    if paylab_path.exists():
        df_paylab = pd.read_csv(paylab_path)
        print(f"Paylab Salary Data: {len(df_paylab)} roles (Should be ~400)")
    else:
        print("paylab_salary_mapping_full.csv NOT FOUND")

    # Mentors
    mentors_path = root / "data/processed/mentors.json"
    if mentors_path.exists():
        import json
        with open(mentors_path, 'r') as f:
            mentors = json.load(f)
        print(f"Mentors Loaded: {len(mentors)} (Should be > 50)")
    else:
        print(" mentors.json NOT FOUND")

    # 5. ML Models Check
    print("\n ML ARTIFACTS CHECK ")
    models_dir = root / "../models" # Check parent dir if not in root
    if not models_dir.exists():
         models_dir = root / "models"
    
    if models_dir.exists():
        print(f"Models Directory Found: {models_dir}")
        required_models = ["job_embeddings.pt", "course_embeddings.pt", "esco_occ_embeddings.pt"]
        for m in required_models:
            m_path = models_dir / m
            if m_path.exists():
                print(f"{m} found ({m_path.stat().st_size / 1024 / 1024:.2f} MB)")
            else:
                print(f"{m} is missing")
    else:
        print(f"Models directory found neither at {root}/models nor {root.parent}/models")
