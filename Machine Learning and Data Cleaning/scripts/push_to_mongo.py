import pandas as pd
import json
from pymongo import MongoClient
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "pathfinder_plus")

def connect_to_mongo():
    """Establish MongoDB connection"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        print(f" Connected to MongoDB: {DATABASE_NAME}")
        return db
    except Exception as e:
        print(f" Failed to connect to MongoDB: {e}")
        return None

def upload_jobs(db, jobs_path):
    """Upload jobs from CSV to MongoDB"""
    print(f"\n Uploading Jobs from {jobs_path.name}...")
    
    df = pd.read_csv(jobs_path)
    
    # Convert to dict and handle NaN
    records = df.to_dict('records')
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    
    collection = db['jobs']

    
    # Insert with duplicate handling
    inserted = 0
    for record in records:
        try:
            # Use URL as unique identifier
            collection.update_one(
                {'url': record.get('url')},
                {'$set': record},
                upsert=True
            )
            inserted += 1
        except Exception as e:
            print(f" Error inserting job: {e}")
    
    print(f" Uploaded {inserted} jobs")

def upload_courses(db, courses_path):
    """Upload courses from CSV to MongoDB"""
    print(f"\n Uploading Courses from {courses_path.name}...")
    
    df = pd.read_csv(courses_path)
    
    records = df.to_dict('records')
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    
    collection = db['courses']
    
    inserted = 0
    for record in records:
        try:
            # Use course_url as unique identifier
            collection.update_one(
                {'course_url': record.get('course_url')},
                {'$set': record},
                upsert=True
            )
            inserted += 1
        except Exception as e:
            print(f" Error inserting course: {e}")
    
    print(f" Uploaded {inserted} courses")

def upload_mentors(db, mentors_path):
    """Upload mentors from JSON to MongoDB"""
    print(f"\n Uploading Mentors from {mentors_path.name}...")
    
    with open(mentors_path, 'r') as f:
        mentors = json.load(f)
    
    collection = db['mentors']
    
    inserted = 0
    for mentor in mentors:
        try:
            collection.update_one(
                {'id': mentor.get('id')},
                {'$set': mentor},
                upsert=True
            )
            inserted += 1
        except Exception as e:
            print(f" Error inserting mentor: {e}")
    
    print(f" Uploaded {inserted} mentors")

def upload_career_paths(db, progressions_path):
    """Upload career progressions to MongoDB"""
    print(f"\n Uploading Career Paths from {progressions_path.name}...")
    
    df = pd.read_csv(progressions_path)
    records = df.to_dict('records')
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    
    collection = db['career_paths']
    inserted = 0
    for record in records:
        try:
            # Composite key for career paths
            collection.update_one(
                {'current_role': record.get('current_role'), 'next_role': record.get('next_role')},
                {'$set': record},
                upsert=True
            )
            inserted += 1
        except Exception as e:
            print(f" Error inserting career path: {e}")
    
    print(f" Uploaded {inserted} career paths")

def upload_internships(db, internships_path):
    """Upload internship tracks to MongoDB"""
    print(f"\n Uploading Internship Tracks from {internships_path.name}...")
    
    df = pd.read_csv(internships_path)
    records = df.to_dict('records')
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    
    collection = db['internship_tracks']
    inserted = 0
    for record in records:
        try:
            #Use track_id and current_role as unique identifier
            collection.update_one(
                {'track_id': record.get('track_id'), 'current_role': record.get('current_role')},
                {'$set': record},
                upsert=True
            )
            inserted += 1
        except Exception as e:
            print(f" Error inserting internship track: {e}")
    
    print(f" Uploaded {inserted} internship tracks")

def upload_academic_courses(db, academic_path):
    """Upload academic degree courses to MongoDB"""
    print(f"\n Uploading Academic Courses from {academic_path.name}...")
    
    df = pd.read_csv(academic_path)
    records = df.to_dict('records')
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    
    collection = db['courses_academic']
    inserted = 0
    for record in records:
        try:
            #Use course_title and provider as unique identifier
            collection.update_one(
                {'course_title': record.get('course_title'), 'provider': record.get('provider')},
                {'$set': record},
                upsert=True
            )
            inserted += 1
        except Exception as e:
            print(f" Error inserting academic course: {e}")
    
    print(f" Uploaded {inserted} academic courses")

def upload_synthetic_jobs(db, synthetic_path):
    """Upload synthetic jobs to MongoDB"""
    print(f"\n Uploading Synthetic Jobs from {synthetic_path.name}...")
    
    df = pd.read_csv(synthetic_path)
    records = df.to_dict('records')
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    
    collection = db['jobs_synthetic']
    inserted = 0
    for record in records:
        try:
            collection.update_one(
                {'title': record.get('title'), 'company': record.get('company')},
                {'$set': record},
                upsert=True
            )
            inserted += 1
        except Exception as e:
            print(f" Error inserting synthetic job: {e}")
    
    print(f" Uploaded {inserted} synthetic jobs")

def upload_skill_matrix(db, matrix_path):
    """Upload course-skill matrix to MongoDB"""
    print(f"\n Uploading Skill Matrix from {matrix_path.name}...")
    
    df = pd.read_csv(matrix_path)
    records = df.to_dict('records')
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    
    collection = db['course_skill_matrix']
    inserted = 0
    for record in records:
        try:
            collection.update_one(
                {'course_id': record.get('course_id')},
                {'$set': record},
                upsert=True
            )
            inserted += 1
        except Exception as e:
            print(f" Error inserting skill matrix record: {e}")
    
    print(f" Uploaded {inserted} matrix records")

def upload_salary_data(db, paylab_path):
    """Upload Paylab salary mappings to MongoDB"""
    print(f"\n Uploading Salary Data from {paylab_path.name}...")
    
    df = pd.read_csv(paylab_path)
    records = df.to_dict('records')
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    
    collection = db['salary_data']
    inserted = 0
    for record in records:
        try:
            collection.update_one(
                {'job_title': record.get('job_title')},
                {'$set': record},
                upsert=True
            )
            inserted += 1
        except Exception as e:
            print(f" Error inserting salary record: {e}")
    
    print(f" Uploaded {inserted} salary records")

def upload_esco(db, esco_dir):
    """Upload essential ESCO datasets to MongoDB using batch insertions for speed"""
    print(f"\n Uploading ESCO datasets from {esco_dir}...")
    
    esco_files = [
        {"file": "occupations_en.csv", "coll": "esco_occupations"},
        {"file": "skills_en.csv", "coll": "esco_skills"},
        {"file": "occupationSkillRelations_en.csv", "coll": "esco_relations"},
        {"file": "broaderRelationsOccPillar_en.csv", "coll": "esco_broader"}
    ]
    
    for item in esco_files:
        p = esco_dir / item["file"]
        if p.exists():
            print(f"  Processing {item['file']}...")
            df = pd.read_csv(p)
            
            # 1. Clear existing collection for fresh batch sync
            db[item["coll"]].delete_many({})
            
            # 2. Batch process records (handling NaN)
            records = df.to_dict('records')
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
            
            # 3. Insert Many (in chunks of 1000 to prevent BSON limits)
            chunk_size = 1000
            for i in range(0, len(records), chunk_size):
                chunk = records[i:i + chunk_size]
                try:
                    db[item["coll"]].insert_many(chunk)
                except Exception as e:
                    print(f"  Error inserting chunk into {item['coll']}: {e}")
            
            print(f"  Uploaded {len(records)} records to {item['coll']}")
        else:
            print(f"  Warning: {item['file']} not found in {esco_dir}")

def upload_configs(db, config_dir, raw_dir):
    """Upload JSON configurations to a dedicated 'configs' collection"""
    print(f"\n Uploading Configuration Files")
    collection = db['app_configs']
    
    configs = [
        {"path": config_dir / "pricing_estimates.json", "key": "pricing_estimates"},
        {"path": config_dir / "internship_requirements.json", "key": "internship_requirements"},
        {"path": raw_dir / "assessment" / "scoring_config.json", "key": "scoring_config"},
        {"path": raw_dir / "assessment" / "comprehensive_questions.json", "key": "assessment_questions"}
    ]
    
    for cfg in configs:
        if cfg['path'].exists():
            try:
                with open(cfg['path'], 'r') as f:
                    data = json.load(f)
                collection.update_one(
                    {'config_key': cfg['key']},
                    {'$set': {'config_key': cfg['key'], 'data': data}},
                    upsert=True
                )
                print(f"  Uploaded {cfg['key']}")
            except Exception as e:
                print(f"  Error uploading {cfg['key']}: {e}")

def main():
    # Paths
    root = Path(__file__).parent.parent
    data_dir = root / "data"
    processed_dir = data_dir / "processed"
    config_dir = data_dir / "config"
    raw_dir = data_dir / "raw"

    jobs_path = processed_dir / "all_jobs_master.csv"
    courses_path = processed_dir / "all_courses_master.csv"
    academic_path = processed_dir / "academic_courses_master.csv"
    synthetic_path = processed_dir / "synthetic_jobs.csv"
    matrix_path = processed_dir / "course_skill_matrix.csv"
    mentors_path = processed_dir / "mentors.json"
    progressions_path = processed_dir / "career_progressions.csv"
    internships_path = processed_dir / "internship_paths.csv"
    paylab_path = config_dir / "paylab_salary_mapping_full.csv"
    
    # Connecting to mono db
    db = connect_to_mongo()
    if db is None:
        return
    
    try:
        # Upload Jobs
        if jobs_path.exists():
            upload_jobs(db, jobs_path)
        if synthetic_path.exists():
            upload_synthetic_jobs(db, synthetic_path)
        
        # Upload Courses
        if courses_path.exists():
            upload_courses(db, courses_path) # Skill-gap courses
        if academic_path.exists():
            upload_academic_courses(db, academic_path) # Degree courses
        if matrix_path.exists():
            upload_skill_matrix(db, matrix_path)
        
        # Upload Salary & Configs
        if paylab_path.exists():
            upload_salary_data(db, paylab_path)
        upload_configs(db, config_dir, raw_dir)
        
        # Upload Metadata
        if mentors_path.exists():
            upload_mentors(db, mentors_path)
        if progressions_path.exists():
            upload_career_paths(db, progressions_path)
        if internships_path.exists():
            upload_internships(db, internships_path)
        
        # Upload ESCO 
        esco_dir = raw_dir / "esco"
        if esco_dir.exists():
            upload_esco(db, esco_dir)

        print("\nMongoDB upload complete!")

    except KeyboardInterrupt:
        print("\n\n Process stopped by user.")
        print(" Some data may have been partially uploaded. Run again to sync remaining records.")
    except Exception as e:
        print(f"\n Critical failure: {e}")
    finally:
        print("\n MongoDB Connection Closed.")

if __name__ == "__main__":
    main()
