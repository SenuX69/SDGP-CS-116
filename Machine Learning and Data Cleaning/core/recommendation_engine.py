import pandas as pd
import numpy as np
import sys
import json
import re
import torch
import fitz # PyMuPDF for Resume Parsing
from sentence_transformers import SentenceTransformer, util
from pathlib import Path
import traceback
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from dotenv import load_dotenv
import os

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# Add utils to path for trend analyzer
try:
    from .utils.market_trend_analyzer import MarketTrendAnalyzer
except (ImportError, ValueError):
    try:
        from utils.market_trend_analyzer import MarketTrendAnalyzer
    except ImportError:
        import sys
        sys.path.append(str(Path(__file__).parent / "utils"))
        from market_trend_analyzer import MarketTrendAnalyzer


class RecommendationEngine:
    def __init__(self, jobs_path=None, courses_path=None, esco_dir=None, models_dir=None, force_refresh=False, show_progress=True, from_mongo=False):
        # Global Root Detection (Relative to core/)
        self.ml_root = Path(__file__).resolve().parent.parent
        self.show_progress = show_progress
        
        #State Initialization 
        self.jobs_df = pd.DataFrame()
        self.courses_df = pd.DataFrame()
        self.academic_df = pd.DataFrame()
        self.career_progressions_df = pd.DataFrame()
        self.esco_occ = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
        self.esco_skills = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
        self.occ_skill_rel = pd.DataFrame(columns=["occupationUri", "skillUri", "relationType"])
        self.broader_occ = pd.DataFrame(columns=["conceptUri", "broaderUri"])
        self.mentors_data = []
        self.salary_data = {}
        self.pricing_config = {}
        self.assessment_config = {}
        self.assessment_questions = {}
        self.market_skills = []
        self._trend_cache = {}
        
        #  Heavy Model Loading
        try:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            if self.show_progress: print(f"CRITICAL: Failed to load Transformer model: {e}")
            raise
        
        #  Data Loading Logic
        try:
            if from_mongo:
                self.load_from_mongo()
            else:
                # Default local paths if none provided
                jobs_path = jobs_path or str(self.ml_root / "data/processed/all_jobs_master.csv")
                courses_path = courses_path or str(self.ml_root / "data/processed/all_courses_master.csv")
                esco_dir = esco_dir or str(self.ml_root / "data/raw/esco")
                self._load_from_local(jobs_path, courses_path, esco_dir)
        except Exception as e:
            if self.show_progress: 
                print(f"Warning: Primary data loading interrupted: {e}")

        #  Common Post-Load Setup
        # Use ML root for models if not specified
        models_dir = models_dir or str(self.ml_root / "models")
        self._initialize_common(models_dir, force_refresh, courses_path)

    @classmethod
    def from_mongo(cls):
        """Factory method to initialize engine from MongoDB cloud data."""
        return cls(from_mongo=True)

    def load_from_mongo(self):
        """Fetches all primary datasets and configs from MongoDB Atlas."""
        if self.show_progress: print(" FETCHING DATA FROM MONGODB ATLAS")
        try:
            # Check for .env in current root
            env_path = self.ml_root / ".env"
            load_dotenv(dotenv_path=env_path if env_path.exists() else None)
            
            client = MongoClient(os.getenv("MONGO_URI"))
            db = client[os.getenv("DATABASE_NAME", "pathfinder_plus")]
            
            #  Load Jobs
            self.jobs_df = pd.DataFrame(list(db.jobs.find({}, {'_id': 0})))
            syn_jobs = pd.DataFrame(list(db.jobs_synthetic.find({}, {'_id': 0})))
            if not syn_jobs.empty:
                self.jobs_df = pd.concat([self.jobs_df, syn_jobs], ignore_index=True)
            
            # Load Courses
            self.courses_df = pd.DataFrame(list(db.courses.find({}, {'_id': 0})))
            self.academic_df = pd.DataFrame(list(db.courses_academic.find({}, {'_id': 0})))

            # Standardization Helper for Courses
            for df in [self.courses_df, self.academic_df]:
                if not df.empty:
                    if "course_title" not in df.columns and "course_name" in df.columns:
                        df.rename(columns={"course_name": "course_title"}, inplace=True)
                    if "provider" not in df.columns and "institute" in df.columns:
                        df.rename(columns={"institute": "provider"}, inplace=True)
            
            if self.show_progress:
                print(f"DEBUG: courses_df columns: {self.courses_df.columns.tolist()}")
                print(f"DEBUG: academic_df columns: {self.academic_df.columns.tolist()}")
            
            #  Load Mentors
            self.mentors_data = list(db.mentors.find({}, {'_id': 0}))
            
            #  Load Progressions
            self.career_progressions_df = pd.DataFrame(list(db.career_paths.find({}, {'_id': 0})))
            
            #  Load Salary Data
            salary_list = list(db.salary_data.find({}, {'_id': 0}))
            self.salary_data = {}
            for item in salary_list:
                title = item.get('job_title', item.get('title', 'Unknown'))
                min_s = item.get('salary_min', 0) or 0
                max_s = item.get('salary_max', 0) or 0
                # Only store if we have actual data
                if min_s > 0 or max_s > 0:
                    self.salary_data[str(title).lower()] = f"{min_s} - {max_s} LKR"
            
            #  Load Configs from app_configs collection
            configs = list(db.app_configs.find({}, {'_id': 0}))
            config_dict = {cfg['config_key']: cfg['data'] for cfg in configs}
            self.pricing_config = config_dict.get('pricing_estimates', {})
            self.assessment_config = config_dict.get('scoring_config', {})
            self.assessment_questions = config_dict.get('assessment_questions', {})

            #  Load ESCO dataframes from Cloud
            self.esco_occ = pd.DataFrame(list(db.esco_occupations.find({}, {'_id': 0})))
            self.esco_skills = pd.DataFrame(list(db.esco_skills.find({}, {'_id': 0})))
            self.occ_skill_rel = pd.DataFrame(list(db.esco_relations.find({}, {'_id': 0})))
            self.broader_occ = pd.DataFrame(list(db.esco_broader.find({}, {'_id': 0})))

            # Fallback to empty DFs if collections missing
            if self.esco_occ.empty:
                self.esco_occ = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            if self.esco_skills.empty:
                self.esco_skills = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            if self.occ_skill_rel.empty:
                self.occ_skill_rel = pd.DataFrame(columns=["occupationUri", "skillUri", "relationType"])
            if self.broader_occ.empty:
                self.broader_occ = pd.DataFrame(columns=["conceptUri", "broaderUri"])

            # Ensure columns exist even if DF is empty
            for df_name, df_obj in [("courses_df", self.courses_df), ("academic_df", self.academic_df)]:
                 if df_obj.empty:
                     print(f"WARNING: {df_name} is EMPTY after cloud load.")
                 else:
                     print(f"INFO: {df_name} loaded with {len(df_obj)} rows. Columns: {df_obj.columns.tolist()}")

            if self.show_progress: print(f"Cloud Load Complete: {len(self.jobs_df)} jobs, {len(self.courses_df)} courses.")
            
        except Exception as e:
            if self.show_progress: print(f"Cloud Load Failed: {e}. Falling back to empty data.")
            import traceback
            traceback.print_exc()
            self.jobs_df = pd.DataFrame()
            self.courses_df = pd.DataFrame(columns=["course_title", "provider", "category", "description"])
            self.academic_df = pd.DataFrame(columns=["course_title", "provider", "category", "description"])
            self.mentors_data = []
            self.career_progressions_df = pd.DataFrame()
            self.salary_data = {}
            self.pricing_config = {}
            self.assessment_config = {}
            self.assessment_questions = {}
            self.esco_occ = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            self.esco_skills = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            self.occ_skill_rel = pd.DataFrame(columns=["occupationUri", "skillUri", "relationType"])
            self.broader_occ = pd.DataFrame(columns=["conceptUri", "broaderUri"])


    def _load_from_local(self, jobs_path, courses_path, esco_dir):
        """Legacy local CSV loading logic."""
        if not jobs_path or not courses_path or not esco_dir:
            if self.show_progress: print("Warning: Local paths missing. Initialize with from_mongo=True or provide paths.")
            self.jobs_df = pd.DataFrame()
            self.courses_df = pd.DataFrame()
            self.academic_df = pd.DataFrame()
            self.mentors_data = []
            self.career_progressions_df = pd.DataFrame()
            self.salary_data = {}
            self.pricing_config = {}
            self.assessment_config = {}
            self.esco_occ = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            self.esco_skills = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            self.occ_skill_rel = pd.DataFrame(columns=["occupationUri", "skillUri", "relationType"])
            self.broader_occ = pd.DataFrame(columns=["conceptUri", "broaderUri"])
            return

        # Load pricing config
        self.pricing_config = {}
        config_path = Path(jobs_path).parent.parent / "config" / "pricing_estimates.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.pricing_config = json.load(f)
        else:
             if self.show_progress: print(f"Warning: Pricing config not found at {config_path}")

        # Load datasets
        self.jobs_df = pd.read_csv(jobs_path)
        self.courses_df = pd.read_csv(courses_path)
        self.courses_df['source_file'] = 'professional'
        
        # Standardize main courses_df
        if not self.courses_df.empty:
            if "course_title" not in self.courses_df.columns and "course_name" in self.courses_df.columns:
                self.courses_df.rename(columns={"course_name": "course_title"}, inplace=True)
            if "provider" not in self.courses_df.columns and "institute" in self.courses_df.columns:
                self.courses_df.rename(columns={"institute": "provider"}, inplace=True)

        #  Load Academic Courses separately
        self.academic_df = pd.DataFrame()
        academic_path = Path(courses_path).parent / "academic_courses_master.csv"
        if academic_path.exists():
            if self.show_progress: print(f"Loading academic courses ({academic_path.name})...")
            self.academic_df = pd.read_csv(academic_path)
            self.academic_df['source_file'] = 'academic'
            # Ensure naming consistency
            if "course_title" not in self.academic_df.columns and "course_name" in self.academic_df.columns:
                self.academic_df.rename(columns={"course_name": "course_title"}, inplace=True)
            if "provider" not in self.academic_df.columns and "institute" in self.academic_df.columns:
                self.academic_df.rename(columns={"institute": "provider"}, inplace=True)
        else:
            if self.show_progress: print(f"Warning: {academic_path} not found.")

        # Load Salary Data
        self.salary_mapping = {}
        salary_cfg_path = Path(jobs_path).parent.parent / "config" / "salary_config.json"
        if salary_cfg_path.exists():
            try:
                with open(salary_cfg_path, 'r') as f:
                    self.salary_mapping = json.load(f)
            except Exception:
                pass

        #  Load Synthetic Jobs if available (Demo Enhancement)
        syn_jobs_path = Path(jobs_path).parent / "synthetic_jobs.csv"
        if syn_jobs_path.exists():
            if self.show_progress: print(f"Merging synthetic jobs ({syn_jobs_path.name})...")
            syn_df = pd.read_csv(syn_jobs_path)
            self.jobs_df = pd.concat([self.jobs_df, syn_df], ignore_index=True)

        #  Load Synthetic Mentors
        self.mentors_data = []
        mentors_path = Path(jobs_path).parent / "mentors.json"
        if mentors_path.exists():
            try:
                with open(mentors_path, 'r') as f:
                    self.mentors_data = json.load(f)
                if self.show_progress: print(f"Loaded {len(self.mentors_data)} mentors.")
            except Exception:
                pass

        #  Load Career Progressions
        prog_path = Path(jobs_path).parent / "career_progressions.csv"
        if prog_path.exists():
            self.career_progressions_df = pd.read_csv(prog_path)
            if self.show_progress: print(f"Loaded {len(self.career_progressions_df)} career progression paths.")
        else:
            self.career_progressions_df = pd.DataFrame()
            if self.show_progress: print("Warning: career_progressions.csv not found.")

        # Load market context advice
        advice_path = Path(esco_dir).parent / "market_context" / "sl_sector_advice.csv"
        if advice_path.exists():
            self.market_advice_df = pd.read_csv(advice_path)
        else:
            self.market_advice_df = None

        # LOAD ESCO DATA 
        try:
            esco_path = Path(esco_dir)
            if (esco_path / "occupations_en.csv").exists():
                self.esco_occ = pd.read_csv(esco_path / "occupations_en.csv")
                self.esco_skills = pd.read_csv(esco_path / "skills_en.csv")
                self.occ_skill_rel = pd.read_csv(esco_path / "occupationSkillRelations_en.csv")
            else:
                if self.show_progress: print("WARNING: ESCO files not found. Using empty dataframes.")
                self.esco_occ = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
                self.esco_skills = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
                self.occ_skill_rel = pd.DataFrame(columns=["occupationUri", "skillUri", "relationType"])
        except Exception as e:
            if self.show_progress: print(f"ERROR loading ESCO: {e}. Falling back to empty data.")
            self.esco_occ = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            self.esco_skills = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            self.occ_skill_rel = pd.DataFrame(columns=["occupationUri", "skillUri", "relationType"])
        # load broader occupations for progression (With Fallbacks)
        try:
            if (esco_path / "broaderRelationsOccPillar_en.csv").exists():
                self.broader_occ = pd.read_csv(esco_path / "broaderRelationsOccPillar_en.csv")
            else:
                self.broader_occ = pd.DataFrame(columns=["conceptUri", "broaderUri"])
        except Exception:
            self.broader_occ = pd.DataFrame(columns=["conceptUri", "broaderUri"])

 
    def _initialize_common(self, models_dir, force_refresh, courses_path):
        """Standard setup logic for both local and cloud modes."""
        #  Models Path
        if models_dir is None:
            models_path = Path(__file__).parent.parent / "models"
        else:
            models_path = Path(models_dir)
        models_path.mkdir(parents=True, exist_ok=True)

        #  Extract Market Skills (Critical for matching logic)
        self.market_skills = []
        
        # 1. Primary Source: ESCO Skills
        if hasattr(self, 'esco_skills') and not self.esco_skills.empty:
            self.market_skills = self.esco_skills['preferredLabel'].dropna().str.lower().tolist()
        
        # 2. Supplementary: Extracted from jobs (if available)
        if hasattr(self, 'jobs_df') and not self.jobs_df.empty and 'extracted_skills' in self.jobs_df.columns:
            job_skills = []
            for s in self.jobs_df['extracted_skills'].dropna():
                if isinstance(s, str):
                    job_skills.extend([sk.strip().lower() for sk in s.split(',')])
            self.market_skills = list(set(self.market_skills + job_skills))
        
        # Remove duplicates and extremely short terms (e.g. "it", "at") to avoid noisy matching
        self.market_skills = list(set([s for s in self.market_skills if isinstance(s, str) and len(s) > 3]))
            
        #  Initialize Trend Analyzer
        try:
             # In cloud mode, courses_path might be None, but analyzer needs jobs data
             # We use jobs_df directly from the engine
            self.trend_analyzer = MarketTrendAnalyzer(self.jobs_df)
        except Exception as e:
            if self.show_progress: print(f"Warning: Trend Analyzer failed: {e}")
            self.trend_analyzer = None

        self._trend_cache = {}

        #  Load or Build Embeddings
        self._load_or_build_embeddings(models_path, force_refresh, courses_path)

    def _load_or_build_embeddings(self, models_path, force_refresh, courses_path):
        """Logic moved from legacy init into a dedicated method."""
        # Ensure courses_path is string-safe for filename generation
        course_filename = Path(courses_path).stem if courses_path else "cloud_courses"
        
        if self.show_progress:
            print(f"DEBUG EMBED: jobs_df columns: {self.jobs_df.columns.tolist() if not self.jobs_df.empty else 'EMPTY'}")
            print(f"DEBUG EMBED: courses_df columns: {self.courses_df.columns.tolist() if not self.courses_df.empty else 'EMPTY'}")
     
        # Load assessment config
        config_path = Path(__file__).parent.parent / "data" / "raw" / "assessment" / "scoring_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.assessment_config = json.load(f)
        else:
            self.assessment_config = {}

        # load esco embeddings
        esco_emb_file = models_path / "esco_occ_embeddings.pt"
        rebuild_esco = True
        
        if esco_emb_file.exists() and not force_refresh:
            if self.show_progress: print(f"Loading pre-computed ESCO embeddings from {esco_emb_file}")
            try:
                loaded_esco = torch.load(esco_emb_file)
                if len(loaded_esco) == len(self.esco_occ):
                    self.esco_occ_embs = loaded_esco
                    rebuild_esco = False
                else:
                    print(f"WARNING: ESCO Embedding size ({len(loaded_esco)}) != Dataframe size ({len(self.esco_occ)}). Rebuilding...")
            except Exception as e:
                print(f"Error loading ESCO embeddings: {e}. Rebuilding...")

        if rebuild_esco:
            if self.show_progress: print("Encoding ESCO occupations...")
            self.esco_occ_embs = self.model.encode(
                self.esco_occ["preferredLabel"].tolist(),
                convert_to_tensor=True,
                show_progress_bar=self.show_progress,
            )
            torch.save(self.esco_occ_embs, esco_emb_file)

        # load Embeddings for (Professional)
        course_emb_file = models_path / f"course_embeddings_{course_filename}.pt"
        
        rebuild_courses = True
        if course_emb_file.exists() and not force_refresh:
            if self.show_progress: print(f"Loading pre-computed course embeddings from {course_emb_file}")
            try:
                loaded_embs = torch.load(course_emb_file)
                if len(loaded_embs) == len(self.courses_df):
                    self.course_embs = loaded_embs
                    rebuild_courses = False
                else:
                    print(f"WARNING: Embedding size ({len(loaded_embs)}) != Dataframe size ({len(self.courses_df)}). Rebuilding...")
            except Exception:
                pass
        
        if rebuild_courses:
            if self.show_progress: print(f"Encoding professional courses for {course_filename}...")
            course_texts = (
                self.courses_df["course_title"].fillna("")
                + " "
                + self.courses_df["category"].fillna("")
                + " "
                + self.courses_df["description"].fillna("")
            ).tolist()

            self.course_embs = self.model.encode(
                course_texts, convert_to_tensor=True, show_progress_bar=self.show_progress
            )
            torch.save(self.course_embs, course_emb_file)

        # laoding acadmeic embeddings
        academic_emb_file = models_path / "academic_embeddings.pt"
        rebuild_academic = True
        
        if not self.academic_df.empty:
            if academic_emb_file.exists() and not force_refresh:
                if self.show_progress: print(f"Loading pre-computed academic embeddings from {academic_emb_file}")
                try:
                    loaded_acad = torch.load(academic_emb_file)
                    if len(loaded_acad) == len(self.academic_df):
                        self.academic_embs = loaded_acad
                        rebuild_academic = False
                    else:
                        print(f"WARNING: Academic Embedding size ({len(loaded_acad)}) != Dataframe size ({len(self.academic_df)}). Rebuilding...")
                except Exception:
                    pass

            if rebuild_academic:
                if self.show_progress: print("Encoding academic degree programs...")
                acad_texts = (
                    self.academic_df["course_title"].fillna("")
                    + " "
                    + self.academic_df["category"].fillna("")
                    + " "
                    + self.academic_df["description"].fillna("")
                ).tolist()
                
                self.academic_embs = self.model.encode(
                    acad_texts, convert_to_tensor=True, show_progress_bar=self.show_progress
                )
                torch.save(self.academic_embs, academic_emb_file)
        else:
            self.academic_embs = None

        # Job emddding load
        job_emb_file = models_path / "job_embeddings.pt"
        rebuild_jobs = True
        
        if not self.jobs_df.empty and "title" in self.jobs_df.columns:
            # We only use titles for the moment for semantic search speed
            self.job_titles_list = self.jobs_df["title"].fillna("").tolist()
            
            if job_emb_file.exists() and not force_refresh:
                if self.show_progress: print(f"Loading pre-computed Job embeddings from {job_emb_file}")
                try:
                    loaded_jobs = torch.load(job_emb_file)
                    if len(loaded_jobs) == len(self.job_titles_list):
                        self.job_embs = loaded_jobs
                        rebuild_jobs = False
                    else:
                        print(f"WARNING: Job Embedding size ({len(loaded_jobs)}) != Dataframe size ({len(self.job_titles_list)}). Rebuilding...")
                except Exception as e:
                    print(f"Error loading Job embeddings: {e}. Rebuilding...")

            if rebuild_jobs:
                if self.show_progress: print(f"Encoding {len(self.job_titles_list)} jobs...")
                self.job_embs = self.model.encode(
                    self.job_titles_list,
                    convert_to_tensor=True,
                    show_progress_bar=self.show_progress
                )
                torch.save(self.job_embs, job_emb_file)
        else:
            self.job_embs = None
            self.job_titles_list = []

    def get_salary_for_role(self, role_title, experience_level="Entry"):
        """Retrieves salary range from config (fuzzy match)"""
        if not hasattr(self, "salary_mapping") or not self.salary_mapping:
            return "Data Not Available"
            
        role_map = self.salary_mapping.get("roles", {})
        role_key_raw = str(role_title).strip()
        
        # 1. Exact Match
        if role_key_raw in role_map:
            return role_map[role_key_raw].get(experience_level, "Data Not Available")
            
        # 2. Fuzzy Match (Contains)
        role_key_lower = role_key_raw.lower()
        for known_role, levels in role_map.items():
            if known_role.lower() in role_key_lower or role_key_lower in known_role.lower():
                return levels.get(experience_level, "Data Not Available")
                
        # 3. Sector Fallback
        sectors = self.salary_mapping.get("sectors", {})
        if any(kw in role_key_lower for kw in ["software", "developer", "engineer", "data", "it"]):
            return sectors.get("IT", "Data Not Available")
        if any(kw in role_key_lower for kw in ["account", "finance", "bank"]):
            return sectors.get("Finance", "Data Not Available")
            
        return "Data Not Available"

    def process_comprehensive_assessment(self, answers: Dict[str, Any]):
        """
        Processes the 18-point comprehensive assessment into a Feature Vector for ML.
        """
        vector = {}
        #  Normalize strings to handle hyphen/en-dash variations (e.g. 1-3 vs 1–3)
        norm_answers = {k: str(v).replace('–', '-').replace('—', '-') if isinstance(v, str) else v for k, v in answers.items()}
        
        #  Base Levels
        status_map = self.assessment_config.get("mapping", {}).get("status", {
            "O/L Student": 0, "A/L Student": 0, "Undergraduate": 1, "Graduate": 2,
            "Working Professional": 3, "Career Transitioning": 3
        })
        status = norm_answers.get("status", "Undergraduate")
        vector["status_level"] = status_map.get(status, 1)
        
        experience_map = self.assessment_config.get("mapping", {}).get("experience", {
            "None": 0, "< 1 year": 0.5, "1-3 years": 2, "3-5 years": 4, "5+ years": 6
        })
        experience = norm_answers.get("total_experience", "None")
        vector["experience_years"] = experience_map.get(experience, 0)
        
        #  Responsibility Band (0-4)
        resp_level = norm_answers.get("responsibility_level", "Followed instructions")
        band_map = {
            "Followed instructions": 0,
            "Completed independent tasks": 1,
            "Planned tasks": 2,
            "Supervised others": 3,
            "Managed outcomes / budgets": 4
        }
        vector["responsibility_band"] = band_map.get(resp_level, 0)
        
        # Behavioral Scores (0-3)
        logic = self.assessment_config.get("assessment_logic", {})
        vector["problem_solving_score"] = logic.get("problem_solving", {}).get(norm_answers.get("q7"), 0)
        vector["decision_making_score"] = logic.get("decision_making", {}).get(norm_answers.get("q8"), 0)
        vector["leadership_score"] = logic.get("team_role", {}).get(norm_answers.get("q9"), 0)
        vector["adaptability_score"] = logic.get("adaptability", {}).get(norm_answers.get("q10"), 0)
        vector["initiative_score"] = logic.get("efficiency", {}).get(norm_answers.get("q11"), 0)
        vector["conflict_score"] = logic.get("conflict", {}).get(norm_answers.get("q12"), 0)
        
        #  Semantic Intent (Open Prompts)
        prompts = [
            norm_answers.get("career_background", ""),
            norm_answers.get("interests", ""),
            norm_answers.get("q13", ""), # Proud project
            norm_answers.get("q14", ""), # Environment
            norm_answers.get("q15", ""), # Success outcome
            norm_answers.get("q16", "")  # Obstacles
        ]
        full_text = " ".join([p for p in prompts if p])
        if full_text:
            vector["intent_embedding"] = self.model.encode(full_text).tolist()
            # Robust keyword extraction: check for presence of market skills
            full_text_lower = full_text.lower()
            extracted = []
            
            # Optimization: Pre-filter potential skills to avoid O(N*M) bottlenecks if market_skills is huge
            # For public use, we check both exact and partial matches for critical terms
            for s in self.market_skills:
                s_low = s.lower()
                # 1. Direct match
                if s_low in full_text_lower:
                    extracted.append(s)
                # 2. Token-based match for longer skills (e.g. "software development" matches "developing software")
                elif len(s_low) > 10 and all(word in full_text_lower for word in s_low.split() if len(word) > 3):
                    extracted.append(s)
                    
            vector["extracted_intent_skills"] = sorted(list(set(extracted)))
        else:
            vector["intent_embedding"] = []
            vector["extracted_intent_skills"] = []

        # Constraints
        vector["budget_category"] = norm_answers.get("budget_range", "None")
        vector["time_commitment"] = norm_answers.get("weekly_time", "None")
        vector["education_preference"] = norm_answers.get("education_type", "None")
        
        return vector

    def _should_recommend_internships(self, assessment_vector: Dict[str, Any]) -> bool:
        """Strict check to ensure professionals don't get internship paths//"""
        exp = assessment_vector.get("experience_years", 0)
        status = assessment_vector.get("status_level", 0)
        # Professionals (> 0 exp or status level 3) should usually bypass internships
        return exp == 0 and status <= 1

    def get_recommendations_from_assessment(self, assessment_vector: Dict[str, Any], target_job: str):
        """
        Entry point for the new Assessment-driven recommendation logic.
        gives a complete Dashboard Bundle for UI/Chatbot display.
        """
        #  Determine segment and user_level
        status_level = assessment_vector.get("status_level", 0)
        segment = "Student" if status_level <= 2 else "Professional"
        user_skills = assessment_vector.get("extracted_intent_skills", [])
        
        # Mapping user levels for better course query results
        user_level = "Entry"
        if status_level == 0: user_level = "O/L or School Level"
        elif status_level == 1: user_level = "A/L or Undergraduate"
        elif status_level == 2: user_level = "Professional"
        elif status_level >= 3: user_level = "Senior / Expert"

        #  Parse Constraints
        budget_str = str(assessment_vector.get("budget_category", "")).replace("–", "-")
        budget_map = {"< 50k": 50000, "50k-200k": 200000, "200k-500k": 500000, "500k+": 2000000}
        max_budget = budget_map.get(budget_str)
        
        #  Fetch Components
        # Use specific preference mapping
        pref = assessment_vector.get("education_preference")
        if not pref or pref == "None":
            if status_level == 0: pref = "Diploma"
            elif status_level == 1: pref = "BSc"
            elif status_level >= 2: pref = "MSc"

        courses = self.recommend_courses(
            user_skills=user_skills,
            target_job=target_job,
            user_level=user_level,
            segment=segment,
            preference=pref,
            max_budget=max_budget,
            top_n=5,
            assessment_vector=assessment_vector  # Pass full context
        )
        return courses

    def recommend_jobs(self, user_skills, target_role, top_n=5):
        """Matches users to real-time job openings from the database."""
        if self.jobs_df.empty or not hasattr(self, 'job_embs') or self.job_embs is None:
             return []
        
        try:
            # . Build Query text
            query = f"{target_role} " + " ".join(user_skills[:5])
            query_emb = self.model.encode(query, convert_to_tensor=True)
            
            # Semantic Search
            hits = util.semantic_search(query_emb, self.job_embs, top_k=top_n*2)[0]
            
            results = []
            for hit in hits:
                idx = hit['corpus_id']
                if idx >= len(self.jobs_df): continue
                job = self.jobs_df.iloc[idx]
                
                results.append({
                    "job_title": job["title"],
                    "company": job.get("company", "Confidential"),
                    "location": job.get("location", "Sri Lanka"),
                    "link": job.get("job_url", "#"),
                    "relevance_score": round(float(hit['score']) * 100, 1)
                })
                
            return results[:top_n]
        except Exception as e:
            if self.show_progress: print(f"Error matching jobs: {e}")
            return []

    
    # course classificatin
   
    # classify course level (updated for msc/degree)
    def classify_course_level(self, title, duration):
        title = str(title).lower()
        duration = str(duration).lower()

        # separate postgrad from undergrad
        if any(x in title for x in ["msc", "master", "phd", "doctorate", "postgraduate", "mba"]):
            return "Postgraduate"

        if any(x in title for x in ["degree", "bsc", "bachelor", "undergraduate"]):
            return "Academic (Degree)"
        
        if any(x in title for x in ["diploma", "hnd", "foundation"]):
            return "Academic (Diploma)"

        if any(x in title for x in ["advanced", "professional", "expert", "architect", "management"]):
            return "Professional"

        if any(x in title for x in ["intro", "basic", "beginner", "fundamental", "bootcamp"]):
            return "Beginner"

        return "Mid-Level"

    
    # get skills for job
    def get_skills_for_job(self, job_title):
        # try to find skills from local jobs first
        local_matches = self.jobs_df[
            self.jobs_df["title"].str.contains(job_title, case=False, na=False)
        ]
        
        local_skills = []
        if not local_matches.empty:
            # aggregate skills from top matches
            for idx, row in local_matches.head(10).iterrows():
                if pd.notna(row.get("extracted_skills")):
                    # assuming extracted_skills is a string
                    skills = row["extracted_skills"]
                    if isinstance(skills, str):
                        local_skills.extend([s.strip() for s in skills.split(",")])
                    elif isinstance(skills, list):
                        local_skills.extend(skills)
        
        local_skills = list(set(s for s in local_skills if len(s) > 2))
        
        # esco fallback using essential relations
        job_emb = self.model.encode(job_title, convert_to_tensor=True)
        hit = util.semantic_search(job_emb, self.esco_occ_embs, top_k=1)[0][0]
        occ = self.esco_occ.iloc[hit["corpus_id"]]

        # only pick essential skills to avoid random languages
        rel = self.occ_skill_rel[
            (self.occ_skill_rel["occupationUri"] == occ["conceptUri"]) & 
            (self.occ_skill_rel["relationType"] == "essential")
        ]
        esco_skills_all = self.esco_skills[
            self.esco_skills["conceptUri"].isin(rel["skillUri"])
        ]["preferredLabel"].tolist()

        #  Cross reference with available jobs
        if self.market_skills:
            esco_skills = [s for s in esco_skills_all if s.lower() in self.market_skills or any(ms in s.lower() for ms in self.market_skills)]
           
            if len(esco_skills) < 5:
                esco_skills = esco_skills_all
        else:
            esco_skills = esco_skills_all

        combined_skills = list(set(local_skills + esco_skills[:12]))
        
        return combined_skills, occ["preferredLabel"]
    
    
    def estimate_responsibility_band(self, user_skills, years_exp=0):
        """Estimate Responsibility Band (0-4) based on skills and years of experience"""
        band = 0
        
        # Base on years of experience
        if years_exp >= 10: band = 4
        elif years_exp >= 6: band = 3
        elif years_exp >= 3: band = 2
        elif years_exp >= 1: band = 1
        
        #  Skill-based adjustments 
        complexity_signals = {
            "strategy": 3, "leadership": 3, "architecture": 3, "management": 3,
            "budgeting": 3, "transformation": 4, "board": 4, "design patterns": 2,
            "refactoring": 2, "deployment": 1
        }
        
        for skill in user_skills:
            skill_lower = skill.lower()
            for signal, level in complexity_signals.items():
                if signal in skill_lower:
                    band = max(band, level)
                    
        return band

    def get_career_progression(self, current_role, current_band, user_skills, assessment_vector=None):
        """Generates progression paths using data-driven career maps and internship logic"""
        progression = []
        
        # Check for Internship/Entry Level Recommendation
        if assessment_vector and self._should_recommend_internships(assessment_vector):
            # Find internship paths matching interest or generic IT
            intern_paths = self.career_progressions_df[
                self.career_progressions_df['current_role'].str.contains('Intern', case=False, na=False)
            ]
            
            # Rank internships by relevance to User Skills & Intent
            scored_paths = []
            
            # Combine explicit skills and partial matches from role names
            search_terms = [s.lower() for s in user_skills]
            if current_role and current_role != "None":
                search_terms.append(current_role.lower())
                
            for _, row in intern_paths.iterrows():
                score = 0
                row_text = f"{row['track_name']} {row['next_role']} {row['requirements']}".lower()
                
                #  Keyword Matching (Skills & Interests)
                for term in search_terms:
                    if term in row_text:
                        score += 5  # Strong match
                    elif any(t in row_text for t in term.split()):
                        score += 1  # Partial match
                
                #  Track Name Priority
                if current_role and current_role.lower() in str(row['track_name']).lower():
                    score += 10
                    
                scored_paths.append((score, row))
            
            # Sort by score descending
            scored_paths.sort(key=lambda x: x[0], reverse=True)
            
            # Return top 3 filtered paths (or defaults if no match found)
            top_paths = [p[1] for p in scored_paths[:3]] if scored_paths and scored_paths[0][0] > 0 else intern_paths.head(3).iterrows()
            
            # Handle the iteration difference (list vs generator)
            iterable_paths = top_paths if isinstance(top_paths, list) else [r for _, r in top_paths]

            for row in iterable_paths:
                progression.append({
                    "type": "Entry Level (Internship)",
                    "role": row['next_role'], # The target is the Junior role
                    "current_step": row['current_role'],
                    "target_band": 1,
                    "typical_years": row['typical_years'],
                    "advice": f"Start here: {row['requirements'] or 'Gain foundational skills'}"
                })

        # Data-Driven Paths (Primary Method)
        found_data_driven = False
        if not self.career_progressions_df.empty:
            matches = self.career_progressions_df[
                self.career_progressions_df['current_role'].str.contains(current_role, case=False, na=False)
            ]
            
            if not matches.empty:
                found_data_driven = True
                for _, row in matches.head(2).iterrows():
                    progression.append({
                        "type": "Vertical (Promotion)",
                        "role": row['next_role'],
                        "target_band": current_band + 1,
                        "typical_years": row['typical_years'],
                        "advice": f"Progression path: {row['requirements']}"
                    })

        # 3. Fallback: Band-based Vertical Promotion (Legacy Logic)
        # Only add if we didn't find specific data-driven vertical paths
        if not found_data_driven and current_band < 4:
            target_band = current_band + 1
            band_labels = ["Intern", "Independent", "Professional", "Lead", "Executive"]
            
            curr_label = band_labels[current_band] if current_band < len(band_labels) else "Expert"
            target_label = band_labels[target_band] if target_band < len(band_labels) else "Leader"
            
            target_role = f"{target_label} {current_role}"
            
            progression.append({
                "type": "Vertical (Promotion)",
                "role": target_role,
                "target_band": target_band,
                "typical_years": "2-4 years",
                "advice": f"Focus on moving from {curr_label} to {target_label} responsibilities."
            })
            
        # 4. Horizontal Transition (Always suggest alternatives)
        alternates = self.suggest_alternate_paths(current_role, top_n=2)
        for alt in alternates:
            progression.append({
                "type": "Horizontal (Pivot)",
                "role": alt['title'],
                "target_band": current_band,
                "typical_years": "0-1 year (Transition)",
                "advice": f"Leverage your existing skills in {alt['title']}. Similarity: {alt['similarity']*100:.1f}%"
            })
            
        return progression

    def get_top_up_recommendations(self, current_band, target_band, segment):
        """Suggests specific course types (Top-ups) based on the band leap"""
        top_ups = []
        
        if current_band < 2 and target_band >= 2:
            top_ups.append("Professional Certifications (AWS, PMP, etc.)")
        if target_band >= 3:
            top_ups.append("Postgraduate Studies (MSc, MBA)")
        if segment == "Student" and current_band == 0:
            top_ups.append("Academic Degree (BSc/BEng)")
            
        return top_ups
        # Determine context-specific advice and top companies from dataset
        advice = f"Target {mapped_occ_name} roles in leading Sri Lankan organizations. Focus on professional certifications to advance."
        sector_name = "General"
        source_citation = "ESCO Hierarchy"

        if self.market_advice_df is not None:
            l_label = label.lower()
            for _, row in self.market_advice_df.iterrows():
                keywords = [k.strip().lower() for k in str(row['Keyword']).split(',')]
                if any(k in l_label for k in keywords):
                    sector_name = row['Sector']
                    advice = f"Target {sector_name} roles in {row['Companies']}. {row['Advice']}"
                    source_citation = row['Source']
                    break

        # Official Description from ESCO
        occ_desc_matches = self.esco_occ[self.esco_occ["conceptUri"] == uri]
        role_desc = occ_desc_matches["description"].iloc[0] if not occ_desc_matches.empty else ""

        progression.append({
            "target_role": sl_label,
            "estimated_years": years,
            "additional_info": advice,
            "role_description": role_desc,
            "source": f"ESCO Hierarchy / {source_citation}"
        })

        return progression
    def parse_resume(self, file_path):
        """Unified entry point for all resume types (PDF, JPG, PNG, AVIF)"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == ".pdf":
            return self.parse_resume_pdf(file_path)
        elif ext in [".jpg", ".jpeg", ".png", ".avif", ".webp"]:
            return self.parse_resume_image(file_path)
        else:
            if self.show_progress: print(f"Unsupported file format: {ext}")
            return []

    def parse_resume_image(self, image_path):
        """Extracts text from images using OCR (Tesseract)"""
        if not HAS_OCR:
            if self.show_progress: print("OCR libraries (PIL/pytesseract) not found. Cannot parse image.")
            return []
        
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return self.parse_resume_text(text)
        except Exception as e:
            if self.show_progress: print(f"Error parsing image resume: {e}")
            return []

    def auto_profile(self, resume_path):
        """Suggests a target job based on skills extracted from a resume (PDF or Image)"""
        
        #  Extract skills (routes to PDF or OCR)
        skills = self.parse_resume(resume_path)
        if not skills:
            return {"extracted_skills": [], "suggested_target": "Unknown"}

        #  Convert skills into a "Profile Vector"
        # We join the skills into a single sentence so the model understands the context
        skill_text = "Experienced professional skilled in: " + ", ".join(skills)
        skill_emb = self.model.encode(skill_text, convert_to_tensor=True)
        
        #  Semantic Comparison
        # We compare your profile meaning against the pre-calculated meanings of 
        # every job title in our ESCO dataset (self.esco_occ_embs)
        hits = util.semantic_search(skill_emb, self.esco_occ_embs, top_k=1)[0]
        
        #  Return the Label
        # We get the index of the best match and pull its human-readable name
        best_match_idx = hits[0]["corpus_id"]
        suggested_job = self.esco_occ.iloc[best_match_idx]["preferredLabel"]
        
        return {
            "extracted_skills": skills,
            "suggested_target": suggested_job
        }

    def generate_skill_assessment_questions(self, skill_gap):
        """Generates interest and proficiency questions from the comprehensive assessment dataset"""
        questions = []
        
        #  Load comprehensive questions
        try:
            q_file = self.ml_root / "data" / "raw" / "assessment" / "comprehensive_questions.json"
            if q_file.exists():
                with open(q_file, 'r') as f:
                    comp_qs = json.load(f)
                
                # Add 1 random universal question from each category
                import random
                for section, categories in comp_qs.items():
                    for category, qs in categories.items():
                        if qs:
                            q = random.choice(qs)
                            questions.append({
                                "type": "General",
                                "category": category,
                                "question": q["question"],
                                "options": q["options"]
                            })
        except Exception as e:
            print(f"Error loading assessment questions: {e}")

        #  Dynamic gap-specific questions
        for skill in skill_gap[:5]:
            is_tech = any(x in skill.lower() for x in ["programming", "software", "data", "tool", "system", "engine"])
            if is_tech:
                questions.append({
                    "type": "Technical",
                    "skill": skill,
                    "question": f"How would you rate your hands-on experience with {skill}?",
                    "options": ["None", "Beginner (Basic Syntax)", "Intermediate (Used in projects)", "Advanced (Expert)"]
                })
            else:
                questions.append({
                    "type": "Soft Skill",
                    "skill": skill,
                    "question": f"Are you familiar with the concepts of {skill}?",
                    "options": ["Not at all", "Somewhat familiar", "Very familiar", "Already proficient"]
                })
        return questions

    def parse_resume_text(self, resume_text):
        """Extracts skills from resume text using market index and semantic search"""
        found_skills = []
        text_lower = resume_text.lower()
        
        # Direct Keyword Matching
        for skill in self.market_skills:
            if len(skill) > 3 and f" {skill} " in f" {text_lower} ":
                found_skills.append(skill.title())
        
        # Semantic lookup for top skills mentioned
        # chunk resume text
        chunks = [resume_text[i:i+500] for i in range(0, len(resume_text), 500)]
        if chunks:
            # check first few chunks for job title/skills
            resume_emb = self.model.encode(chunks[0], convert_to_tensor=True)
            pass 

        return list(set(found_skills))[:15]

    def parse_resume_pdf(self, pdf_path):
        """Extracts text from PDF and matches skills"""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return self.parse_resume_text(text)
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return []

    def calculate_skill_score(self, resume_skills, assessment_data, target_skills):
        """Calculates a weighted skill score using adaptive signals"""
        if not target_skills: return 0.0
        
        #  Resume Signal (0.4)
        overlap = set(s.lower() for s in resume_skills) & set(s.lower() for s in target_skills)
        resume_score = len(overlap) / len(target_skills) if target_skills else 0
        
        #  Assessment Signal (0.4)
        assess_score = 0.5 # Default middle-ground
        if assessment_data:
            correct = sum(1 for q in assessment_data if q.get('is_correct'))
            assess_score = correct / len(assessment_data)
            
        #  Task Alignment (0.2)
        task_score = 1.0 # Default
        
        # Adaptive Weighting (Scenario B: No Resume)
        if not resume_skills:
            final_score = (assess_score * 0.75) + (task_score * 0.25)
        else:
            final_score = (resume_score * 0.4) + (assess_score * 0.4) + (task_score * 0.2)
            
        return round(final_score, 2)

    def calculate_readiness_score(self, user_skills, assessment_vector, target_role):
        """
        Calculates a Career Readiness Index (0-100) based on 5 metrics:
        - Skills Match: 35%
        - Experience Level: 25%
        - Responsibility Level: 15%
        - Career Clarity: 15%
        - Communication/Behavior: 10%
        """
        all_required, _ = self.get_skills_for_job(target_role)
        
        #  Skills Match (35%)
        overlap = set(s.lower() for s in user_skills) & set(s.lower() for s in all_required)
        skill_pct = (len(overlap) / len(all_required)) if all_required else 0
        
        #  Experience Level (25%)
        exp_years = assessment_vector.get("experience_years", 0)
        # Normalize: 0=0, 5+=1.0
        exp_pct = min(exp_years / 5.0, 1.0)
        
        #  Responsibility Level (15%)
        band = self.estimate_responsibility_band(user_skills, exp_years)
        # Normalize: 0=0, 4=1.0
        resp_pct = band / 4.0
        
        #  Career Clarity (15%)
        # Based on status_level: 0 (Deciding) to 3 (Professional)
        status = assessment_vector.get("status_level", 0)
        clarity_pct = status / 3.0
        
        #  Communication/Behavior (10%)
        # Proxied by intent/open prompt completion
        comm_pct = 1.0 if assessment_vector.get("intent_embedding") else 0.5
        
        score = (skill_pct * 35) + (exp_pct * 25) + (resp_pct * 15) + (clarity_pct * 15) + (comm_pct * 10)
        
        breakdown = {
            "overall": round(score, 1),
            "skills_match": round(skill_pct * 100, 1),
            "experience": round(exp_pct * 100, 1),
            "responsibility": round(resp_pct * 100, 1),
            "clarity": round(clarity_pct * 100, 1),
            "communication": round(comm_pct * 100, 1),
            "stage": "Development Phase" if score < 70 else "Market Ready"
        }
        
        return breakdown

    def calculate_transferability_score(self, current_role, target_role):
        """Calculates skill overlap between roles for career switchers"""
        current_skills, _ = self.get_skills_for_job(current_role)
        target_skills, _ = self.get_skills_for_job(target_role)
        
        overlap = set(s.lower() for s in current_skills) & set(s.lower() for s in target_skills)
        missing = set(s.lower() for s in target_skills) - set(s.lower() for s in current_skills)
        
        diff = "Low"
        if len(missing) > 8: diff = "High"
        elif len(missing) > 4: diff = "Medium"
        
        return {
            "transferable_skills_count": len(overlap),
            "missing_core_skills_count": len(missing),
            "difficulty": diff,
            "estimated_time": "6-12 months" if diff == "Medium" else ("12+ months" if diff == "High" else "3-6 months")
        }

    def generate_action_plan(self, gap_skills, target_role="your target role"):
        """Generates a dynamic 12-month coaching roadmap based on skill gaps"""
        plan = []
        if not gap_skills:
            return [{"period": "Months 1-12", "focus": f"Maintenance: Already industry-ready for {target_role}. focus on networking."}]
        
        # Prioritize top 2 most critical skills
        core_focus = gap_skills[:2]
        remaining = gap_skills[2:5]
        
        # Group 1: Months 1-3
        plan.append({
            "period": "Months 1-3", 
            "focus": f"Foundations: Master {', '.join(core_focus)}",
            "milestone": "Complete initial technical baseline"
        })
        # Group 2: Months 4-6
        plan.append({
            "period": "Months 4-6", 
            "focus": f"Building: Portfolio projects using {core_focus[0]}",
            "milestone": "Github repository with 3+ projects"
        })
        # Group 3: Months 7-9
        plan.append({
            "period": "Months 7-9", 
            "focus": f"Visibility: Certification in {remaining[0] if remaining else 'Specialization'} and Internship hunt",
            "milestone": "Updated resume with newly acquired skills"
        })
        # Group 4: Months 10-12
        plan.append({
            "period": "Months 10-12", 
            "focus": f"Placement: Advanced {target_role} interview prep and Mentorship",
            "milestone": "Full-time role placement"
        })
        
        return plan

    def parse_resume_image(self, image_path):
        """OCR parsing for AVIF/PNG/JPG resumes"""
        try:
            from PIL import Image
            # Check for avif plugin
            try:
                import pillow_avif
            except ImportError:
                print("Warning: pillow-avif-plugin not found. AVIF support may be limited.")
            
            # Simple text extraction attempt (using fitz if it can handle images)
            import fitz
            doc = fitz.open(image_path)
            text = ""
            for page in doc:
                text += page.get_text()
            
            if len(text.strip()) < 50:
                print("Note: Image text is sparse. OCR recommended for real product.")
                # We'd plug in pytesseract here: 
                # text = pytesseract.image_to_string(Image.open(image_path))
                
            return self.parse_resume_text(text)
        except Exception as e:
            print(f"Error parsing image resume: {e}")
            return []

    def _extract_tasks_from_jd(self, jd_text):
        """Filters boilerplate and extracts core verbs/tools"""
        fluff = ["team player", "passionate", "communication", "hardworking", "responsible","caring","attentive"]
        sentences = re.split(r'[.!?\r\n]', jd_text)
        tasks = []
        for s in sentences:
            s_clean = s.lower().strip()
            if len(s_clean) < 10 or any(f in s_clean for f in fluff):
                continue
            if any(skill.lower() in s_clean for skill in self.market_skills):
                tasks.append(s.strip())
        return list(set(tasks))[:5]

    def _estimate_market_average(self, level, category, provider=None):
        """Estimates fees based on Provider first, then Level using loaded config"""
        
        #  Specific Provider Estimates
        if provider and "provider_estimates" in self.pricing_config:
            for key, val in self.pricing_config["provider_estimates"].items():
                if key.lower() in provider.lower():
                    return {"duration": "Varies", "fee": f"~{val} (Est)"}

        #  Level-based Fallbacks
        defaults = {"duration": "Contact Provider", "fee": "Contact Provider"}
        if "level_averages" in self.pricing_config:
            return self.pricing_config["level_averages"].get(level, defaults)
            
        return defaults

    # recommend courses

    def _process_one_course(self, course, similarity_score, segment, user_level, location, max_budget, max_duration, skill_gap):
        """Helper to score and format a single course/degree"""
        level = self.classify_course_level(str(course["course_title"]), str(course.get("duration", "N/A")))
        score = similarity_score

        #  Level-based Scoring
        if segment == "Student":
            if level == "Professional": score *= 0.5
            elif level == "Postgraduate": score *= 0.2
            elif level == "Academic (Degree)": score *= 1.8
            elif level == "Academic (Diploma)": score *= 1.4
        elif segment == "Professional":
            if user_level in ["Mid", "Senior", "Lead", "Manager", "Executive"]:
                if level == "Academic (Degree)": score *= 0.15
                elif level == "Postgraduate": score *= 1.8
                elif level == "Professional": score *= 1.6
            else:
                if level == "Academic (Degree)": score *= 0.8
                elif level == "Professional": score *= 1.8

        # Location Boost
        if location and pd.notna(course.get("location")):
            if str(location).lower() in str(course["location"]).lower():
                score *= 1.3

        #  Fee & Duration Penalties
        # Use numeric if available, else estimate
        current_fee = course.get("fee_numeric", 0) if "fee_numeric" in course else 0
        if current_fee == 0 and "cost" in course and pd.notna(course["cost"]):
            nums = re.findall(r'\d+', str(course["cost"]).replace(',', ''))
            if nums: current_fee = int(nums[0])
            
        if max_budget and current_fee > max_budget:
            score *= 0.1
        
        current_duration = course.get("duration_numeric", 0) if "duration_numeric" in course else 0
        if max_duration and current_duration > max_duration:
            score *= 0.1

        #  Fill in missing presentation data
        market_data = self._estimate_market_average(level, course.get("category", "General"), course.get("provider", ""))
        duration = course.get("duration") if pd.notna(course.get("duration")) and str(course.get("duration")) != "nan" else market_data["duration"]
        fee = course.get("cost") if "cost" in course and pd.notna(course["cost"]) else f"{int(current_fee):,} LKR" if current_fee > 0 else market_data["fee"]

        #  Rationale (Why Recommended)
        why = []
        
        # 1. Level fit
        if segment == "Student" and "Academic" in level:
            why.append("Strong academic foundation for entry-level")
        elif segment == "Professional" and level == "Professional":
            why.append("Fast-track upskilling for professionals")
        
        # 2. Skill coverage
        matches = 0
        for skill in skill_gap:
            if matches >= 2: break
            # Check title and (optionally) description if available
            search_space = str(course["course_title"]).lower()
            if "description" in course and pd.notna(course["description"]):
                search_space += " " + str(course["description"]).lower()
                
            if skill.lower() in search_space:
                why.append(f"Bridges gap in {skill}")
                matches += 1
                
        # 3. Location/Provider
        if location and location.lower() in str(course.get("location", "")).lower():
            why.append(f"Conveniently located in {location}")
        elif pd.notna(course.get("provider")) and similarity_score > 0.8:
            why.append(f"High relevance from {course['provider']}")

        # Final fallback if empty
        if not why:
            why.append("High semantic match to your career goals")

        return {
            "course_name": course["course_title"],
            "provider": course.get("provider", "Unknown Institution"),
            "level": level,
            "type": course.get("type", "Unknown"),
            "duration": duration,
            "fee": fee,
            "fee_numeric": current_fee,
            "location": course.get("location", "Online/Distance"),
            "relevance_score": round(score, 3),
            "url": course.get("course_url", "#"),
            "why_recommended": why[:3]
        }

    def recommend_courses(
        self,
        user_skills,
        target_job,
        user_level="Entry",
        segment="Student",
        preference=None,
        location=None,
        max_budget=None,
        max_duration=None,
        top_n=5,
        assessment_vector=None
    ):
        # get skills and wanted role
        all_required, mapped_occ = self.get_skills_for_job(target_job)
        
        # find which are essential vs optional
        occ_uri = self.esco_occ[self.esco_occ["preferredLabel"] == mapped_occ].iloc[0]["conceptUri"]
        essential_uris = self.occ_skill_rel[
            (self.occ_skill_rel["occupationUri"] == occ_uri) & 
            (self.occ_skill_rel["relationType"] == "essential")
        ]["skillUri"].tolist()
        
        essential_skills = set(self.esco_skills[self.esco_skills["conceptUri"].isin(essential_uris)]["preferredLabel"].str.lower().tolist())

        user_skill_set = set(s.lower() for s in user_skills)
        
        # split gaps into compulsory vs optional
        compulsory_gap = [s for s in all_required if s.lower() in essential_skills and s.lower() not in user_skill_set]
        optional_gap = [s for s in all_required if s.lower() not in essential_skills and s.lower() not in user_skill_set]
        
        skill_gap = compulsory_gap + optional_gap

        # 2. Calculate Signals (Bands & Multi-Signal Score)
        band = self.estimate_responsibility_band(user_skills)
        current_score_val = self.calculate_skill_score(user_skills, None, all_required)
        
        # 3. Handle Complete Match
        if not skill_gap:
            return {
                "status": "Complete",
                "message": "No skill gap detected for this role.",
                "band": band,
                "score": current_score_val
            }

        #  Build Query for Courses
        # Cleaner Query: Filter out verbose ESCO skill names (often full sentences)
        # This prevents the "cluttering" of the query
        query_skills = []
        #  ESCO Mapping & Gap Analysis
        compulsory_skills = compulsory_gap
        optional_skills = optional_gap

        # Career Banding
        band = self.estimate_responsibility_band(user_skills)
        print(f"DEBUG: Career band = {band}")

        #  Semantic Query Construction
        query_skills = []
        for s in compulsory_gap[:4]:
            if len(s) > 40: query_skills.extend(s.split()[:3])
            else: query_skills.append(s)
        
        query_terms = query_skills + optional_gap[:2]
        if segment == "Student": query_terms += ["degree", "bachelor", "bsc", "university"]
        if preference: query_terms.append(preference)
        query = " ".join(query_terms)
        print(f"DEBUG: Query = {query}")
        
        query_emb = self.model.encode(query, convert_to_tensor=True)
        print(f"DEBUG: query_emb type = {type(query_emb)}")

        #  SEMANTIC SEARCH - Combined Dataset Approach
        # We want a mix of Vocational (Professional) and Academic (Degrees)
        all_candidate_recommendations = []
        
        # 1. Search Professional Courses
        hits = util.semantic_search(query_emb, self.course_embs, top_k=top_n * 5)[0]
        for h in hits:
            course = self.courses_df.iloc[h["corpus_id"]]
            processed = self._process_one_course(course, h["score"], segment, user_level, location, max_budget, max_duration, skill_gap)
            all_candidate_recommendations.append(processed)

        # 2. Search Academic Courses
        if self.academic_embs is not None:
            acad_hits = util.semantic_search(query_emb, self.academic_embs, top_k=top_n * 5)[0]
            for h in acad_hits:
                course = self.academic_df.iloc[h["corpus_id"]]
                processed = self._process_one_course(course, h["score"], segment, user_level, location, max_budget, max_duration, skill_gap)
                all_candidate_recommendations.append(processed)

        # 3. Dynamic Selection Logic - Filter by relevance and user context
        # Only keep results with decent score
        all_candidate_recommendations = [r for r in all_candidate_recommendations if r['relevance_score'] > 0.25]
        all_candidate_recommendations = sorted(all_candidate_recommendations, key=lambda x: x['relevance_score'], reverse=True)
        
        final_picks = []
        seen_names = set()
        
        # Priority logic - Students get academic focus, Professionals get professional focus
        if segment == "Student":
            # Add academic first
            for r in all_candidate_recommendations:
                if r.get("source_file") == "academic" and r["course_name"] not in seen_names:
                    final_picks.append(r)
                    seen_names.add(r["course_name"])
                    if len(final_picks) >= 3: break # Top 3 academic
        else:
            # Add professional first
            for r in all_candidate_recommendations:
                if r.get("source_file") == "professional" and r["course_name"] not in seen_names:
                    final_picks.append(r)
                    seen_names.add(r["course_name"])
                    if len(final_picks) >= 3: break # Top 3 professional
        
        # Fill remaining slots with the best available from either source
        for r in all_candidate_recommendations:
            if r["course_name"] not in seen_names:
                final_picks.append(r)
                seen_names.add(r["course_name"])
                if len(final_picks) >= top_n: break

        # Main recommendations is the prioritized mix
        recommendations = final_picks[:top_n]
        
        # Academic recommendations - provide a dedicated list of academic paths 
        # but also fallback to mixed if academic data is sparse
        academic_recommendations = [r for r in all_candidate_recommendations if r.get("source_file") == "academic"]
        if len(academic_recommendations) < 3:
            # If few academic, fill with top general courses to avoid empty sections
            for r in all_candidate_recommendations:
                if r not in academic_recommendations:
                    academic_recommendations.append(r)
                if len(academic_recommendations) >= top_n: break
        
        academic_recommendations = academic_recommendations[:top_n]

        #  JOB FETCHING
        job_list = []
        try:
            job_hits = util.semantic_search(query_emb, self.job_embs, top_k=5)[0]
            for h in job_hits:
                j = self.jobs_df.iloc[h["corpus_id"]]
                j_raw_skills = str(j.get("extracted_skills", "")).lower()
                job_overlap = [s for s in compulsory_skills if s.lower() in j_raw_skills]
                gap_pct = 100 - round(100 * (len(job_overlap) / max(1, len(compulsory_skills))), 1)
                
                job_list.append({
                    "job_title": j["title"],
                    "company": j.get("company", "Lankan Employer"),
                    "deadline": j.get("deadline", "Apply Soon"),
                    "url": j.get("url", j.get("job_url", "#")),
                    "skill_gap_pct": gap_pct,
                    "relevance_score": round(h["score"], 3),
                    "estimated_salary": self.get_salary_for_role(j["title"])
                })
            
            if not job_list:
                job_list.append({
                    "job_title": "No specific openings found",
                    "company": "Market Research Advised",
                    "message": "We couldn't find active jobs for this specific search. Try broadening your location or role."
                })
        except Exception as e:
            print(f"INFO: Job fetching skipped: {e}")
            job_list.append({"job_title": "Job Service Busy", "message": str(e)})

        #  ADVICE BOX
        advice = []
        all_res = recommendations + academic_recommendations
        valid_fees = [r['fee_numeric'] for r in all_res if r['fee_numeric'] > 0]
        if max_budget and valid_fees and min(valid_fees) > max_budget:
            advice.append("Note: Most programs exceed your budget. Target State Universities or OUSL.")
        if location and all_res and not any(location.lower() in str(r['location']).lower() for r in all_res):
             advice.append(f"No direct matches in {location.title()}, showing Online options.")

        # Suppress jobs for O/L students — too early to apply
        current_status = 1
        if assessment_vector:
            current_status = assessment_vector.get("status_level", 1)
            
        if current_status == 0:
            job_list = [{
                "job_title": "Not applicable at this stage",
                "company": "PathFinder+ Guidance",
                "message": "You're at the learning and exploration stage. Focus on courses and building skills first. Job listings will appear once you've completed a Diploma or A/L qualification."
            }]

        #  FINAL BUNDLE
        #  Splitting Roadmap for Backend/UI Clarity
        all_progression = self.get_career_progression(target_job, band, user_skills, assessment_vector)
        vertical_roadmap = [p for p in all_progression if "Vertical" in p.get("type", "")]
        horizontal_roadmap = [p for p in all_progression if "Horizontal" in p.get("type", "")]
        
        return {
            "status": "Incomplete" if skill_gap else "Complete",
            "mapped_occupation": mapped_occ,
            "compulsory_skills": compulsory_gap[:8],
            "optional_skills": optional_gap[:8],
            "assessment_questions": self.generate_skill_assessment_questions(compulsory_gap + optional_gap),
            "recommendations": recommendations,
            "academic_recommendations": academic_recommendations,
            "job_ideas": job_list if job_list else [{"job_title": "No specific openings found for this niche", "company": "Market Research Advised", "message": "Try broadening your role or location filters."}],
            "mentors": self.match_mentors(user_skills, target_job=target_job, top_n=3),
            "alternate_paths": self.suggest_alternate_paths(target_job),
            "vertical_roadmap": vertical_roadmap,
            "horizontal_roadmap": horizontal_roadmap,
            "career_progression": all_progression, # Keep for backward compatibility
            "salary_estimate": self.get_salary_for_role(target_job),
            "readiness_score": self.calculate_readiness_score(user_skills, assessment_vector or {"status_level": 1 if segment=="Student" else 2, "experience_years": 0}, target_job),
            "action_plan": self.generate_action_plan(compulsory_gap, target_role=target_job),
            "market_trends": self.get_personalized_market_trends(target_job),
            "caveats": advice
        }

    def suggest_alternate_paths(self, job_title, top_n=3):
        """Simplified version using esco similarity, returns detailed dictionaries"""
        job_emb = self.model.encode(job_title, convert_to_tensor=True)
        hits = util.semantic_search(job_emb, self.esco_occ_embs, top_k=top_n+1)[0]
        
        paths = []
        for h in hits:
            alt_job = self.esco_occ.iloc[h["corpus_id"]]["preferredLabel"]
            # Skip the target job itself if it's the top match
            if str(alt_job).lower() == str(job_title).lower():
                continue
            paths.append({
                "title": alt_job,
                "similarity": round(float(h["score"]), 3)
            })
            if len(paths) >= top_n:
                break
        return paths

    def match_mentors(self, user_skills, target_job=None, top_n=3):
        """
        Finds mentors whose expertise overlaps with user skills.
        If no skill-based matches found, falls back to role/industry matching for 'a wider range'.
        """
        if not self.mentors_data:
            return []

        scored_mentors = []
        user_skill_set = set(s.lower() for s in user_skills)
        target_role_lower = str(target_job).lower() if target_job else ""

        for mentor in self.mentors_data:
            # Score based on skill overlap
            mentor_skills = []
            raw_skills = mentor.get('skills')
            
            if isinstance(raw_skills, list):
                mentor_skills = [str(s).lower() for s in raw_skills]
            elif isinstance(raw_skills, str):
                mentor_skills = [s.strip().lower() for s in raw_skills.split(',')]
            
            # Fallback to expertise/bio if skills are missing
            if not mentor_skills:
                 bio = str(mentor.get('bio', '')).lower()
                 expertise = str(mentor.get('expertise', '')).lower() 
                 combined = bio + " " + expertise
                 # Check if user skills appear in bio
                 match_in_bio = [s for s in user_skill_set if s in combined]
                 overlap = match_in_bio
            else:
                overlap = [s for s in mentor_skills if s in user_skill_set]
            
            score = len(overlap) * 2
            
            # Boost by specialization match
            specialization = str(mentor.get('specialization', '')).lower()
            if any(s in specialization for s in user_skill_set):
                score += 3
            
            # Role fallback boost (Semantic overlap with target role)
            current_role = mentor.get('current_role', mentor.get('title'))
            if target_role_lower and current_role:
                cr_lower = str(current_role).lower()
                if target_role_lower in cr_lower or cr_lower in target_role_lower:
                    score += 10 # Strong role match
                elif any(word in cr_lower for word in target_role_lower.split() if len(word) > 3):
                    score += 4  # Partial role match
            
            # Specialization/Industry match with target role
            if target_role_lower and specialization:
                if any(word in specialization for word in target_role_lower.split() if len(word) > 3):
                    score += 4

            # High-Quality / Active Professionals (Real working mentors)
            company = mentor.get('company')
            if current_role and company and company != "N/A" and company != "Independent":
                score += 5  # Strong boost for mentors with active workplace data

            if "senior" in str(current_role).lower() or "lead" in str(current_role).lower():
                score += 2

            # if premium
            is_premium = mentor.get('tier') == 'Premium' or mentor.get('is_premium', False)
            if is_premium:
                score += 1

            scored_mentors.append({
                "name": mentor.get('name'),
                "title": current_role or "Professional Mentor",
                "company": company or "Independent Consultant",
                "specialization": mentor.get('specialization'),
                "score": score,
                "is_premium": is_premium,
                "matched_skills": overlap
            })

        # Sort by score descending
        scored_mentors.sort(key=lambda x: x['score'], reverse=True)
        
        # Only return matches that have some relevance (score > 0)
        top_matches = [m for m in scored_mentors if m['score'] > 2]
        
        return top_matches[:top_n] if top_matches else []

    def suggest_mentor(self, sector_or_job):
        """Mental Suggestion using loaded synthetic data"""
        if not hasattr(self, 'mentors_data') or not self.mentors_data:
            return ["PathFinder+ Alumni", "Industry Professional"]
        
        # Filter by sector or keyword
        relevant = [
            f"{m['name']} ({m['title']} at {m['company']})" 
            for m in self.mentors_data 
            if sector_or_job.lower() in m['sector'].lower() or sector_or_job.lower() in m['title'].lower()
        ]
        
        if relevant:
            return relevant[:3] # Return top 3 matches
        
        # If no direct match, return randoms from same sector if possible, or just randoms
        return [f"{m['name']} ({m['title']} at {m['company']})" for m in self.mentors_data[:3]]

    def suggest_career_direction(self, interests: List[str]):
        """Interest-to-Career mapping for early students (O/L, A/L)"""
        mapping = {
            "math": "Engineering / Data Science",
            "art": "UI/UX Design / Creative Marketing",
            "business": "Management / Accounting / Logistics",
            "science": "Bio-Tech / Medicine / Engineering",
            "logic": "Software Engineering / Legal",
            "drawing": "Architecture / Graphic Design"
        }
        
        discovered = []
        for interest in interests:
            interest_lower = interest.lower()
            for key in mapping:
                if key in interest_lower:
                    discovered.append(mapping[key])
        
        return list(set(discovered)) if discovered else ["General Management / Social Sciences"]

    def get_personalized_market_trends(self, target_role):
        """Detects user field and fetches relevant market trends"""
        # Simple field detection logic
        field = "General"
        it_keywords = ["software", "developer", "data", "it", "web", "cloud", "engineer", "network", "ai", "tech", "security", "cyber"]
        biz_keywords = ["manager", "business", "analyst", "finance", "accounting", "hr", "sales", "operations"]
        marketing_keywords = ["marketing", "social media", "content", "brand", "seo","graphic","graphic design"]
        
        role_lower = str(target_role).lower()
        if any(k in role_lower for k in it_keywords): field = "IT"
        elif any(k in role_lower for k in biz_keywords): field = "Business"
        elif any(k in role_lower for k in marketing_keywords): field = "Marketing"
        
        # Check cache
        if field in self._trend_cache:
            return self._trend_cache[field]
        
        # Lazy re-init: if trend_analyzer is None or was built on empty data, rebuild now
        if self.trend_analyzer is None or (hasattr(self.trend_analyzer, 'jobs_df') and self.trend_analyzer.jobs_df.empty and not self.jobs_df.empty):
            try:
                self.trend_analyzer = MarketTrendAnalyzer(self.jobs_df)
            except Exception as e:
                if self.show_progress: print(f"Warning: Trend Analyzer re-init failed: {e}")
                return {"field": field, "segments": [], "top_demanded_skills": {}, "recommendation": "Market data not available right now."}
            
        try:
            trends, field_df = self.trend_analyzer.get_trends_by_field(field)
            hot_skills = self.trend_analyzer.get_hot_skills(5, df=field_df)
            
            result = {
                "field": field,
                "segments": trends,
                "top_demanded_skills": hot_skills,
                "recommendation": f"Focus on {', '.join(list(hot_skills.keys())[:3])} to stay competitive in {field}."
            }
            self._trend_cache[field] = result
            return result
        except Exception as e:
            return {"error": f"Could not load trends: {str(e)}", "field": field}



    def get_minimal_context(self, user_query: str, top_n: int = 3) -> str:
        """
        Generates minimal context responses for free gemini api for user
        resposnes for the chatbot.
        """
        # Fetch data
        jobs = self.recommend_jobs([], user_query, top_n=top_n)
        courses = self.recommend_courses(
            user_skills=[], 
            target_job=user_query, 
            top_n=top_n
        )
        
        # Compress into a string
        # Labels: J=Job, C=Course, P=Provider
        ctx = f"Results for: {user_query}\n"
        
        if jobs:
            ctx += "JOBS:\n"
            for j in jobs[:top_n]:
                ctx += f"- {j['job_title']} @ {j['company']}\n"
        
        rec_list = courses.get("recommendations", [])
        if rec_list:
            ctx += "COURSES:\n"
            for c in rec_list[:top_n]:
                ctx += f"- {c['course_name']} ({c['provider']})\n"
                
        return ctx.strip()



if __name__ == "__main__":
    current_dir = Path(__file__).parent
    engine = RecommendationEngine(
        jobs_path=current_dir / "../data/processed/all_jobs_master.csv",
        courses_path=current_dir / "../data/processed/all_courses_master.csv",
        esco_dir=current_dir / "../data/raw/esco",
        force_refresh=False
    )


    # print("\nTEST 1: A/L Student -> Degree")
    # try:
    #     res = engine.recommend_courses(
    #         ["Math"], "Software Engineer", segment="Student", preference="Degree"
    #     )
    # except Exception:
    #     print(traceback.format_exc())
    #     sys.exit(1)
    
    # print(f"Mapped Occupation: {res['mapped_occupation']}")
    # print(f"Career Progression: {res['career_progression']}")
    # print(f"Salary Estimate: {res['salary_estimate']}")
    
    # print("\n--- PROFESSIONAL RECOMMENDATIONS ---")
    # for r in res["recommendations"]:
    #     print(f"- {r['course_name']} | {r['provider']} ({r['level']}) [Score: {r['relevance_score']}]")
        
    # print("\n--- ACADEMIC RECOMMENDATIONS ---")
    # for r in res["academic_recommendations"]:
    #     print(f"- {r['course_name']} | {r['provider']} ({r['level']}) [Score: {r['relevance_score']}]")

    # print("\n--- RECOMMENDED MENTORS ---")
    # for m in res["mentors"]:
    #     print(f"- {m['name']} ({m['title']} at {m['company']}) [Match: {m['score']}]")
import pandas as pd
import numpy as np
import sys
import json
import re
import torch
import fitz # PyMuPDF for Resume Parsing
from sentence_transformers import SentenceTransformer, util
from pathlib import Path
import traceback
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# ── Hybrid ML Layer (RF + GBM + KNN — sits alongside SBERT)
# Graceful import: engine works in SBERT-only mode if ml_classifier is absent
try:
    from .ml_classifier import HybridMLLayer
except (ImportError, ValueError):
    try:
        from ml_classifier import HybridMLLayer
    except ImportError:
        HybridMLLayer = None  # fallback: SBERT-only mode

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# Add utils to path for trend analyzer
try:
    from .utils.market_trend_analyzer import MarketTrendAnalyzer
except (ImportError, ValueError):
    try:
        from utils.market_trend_analyzer import MarketTrendAnalyzer
    except ImportError:
        import sys
        sys.path.append(str(Path(__file__).parent / "utils"))
        from market_trend_analyzer import MarketTrendAnalyzer

# Phase 10: Modular Logic Imports
try:
    from .logic.rule_engine import RuleEngine
    from .logic.analytics import Analytics
    from .logic.recommenders import Recommender
    from .logic.action_plan import ActionPlanGenerator
except (ImportError, ValueError):
    from logic.rule_engine import RuleEngine
    from logic.analytics import Analytics
    from logic.recommenders import Recommender
    from logic.action_plan import ActionPlanGenerator


class RecommendationEngine:
    def __init__(self, jobs_path=None, courses_path=None, esco_dir=None, models_dir=None, force_refresh=False, show_progress=True, from_mongo=False):
        # Global Root Detection (Relative to core/)
        self.ml_root = Path(__file__).resolve().parent.parent
        self.show_progress = show_progress
        
        # State Initialization 
        self.jobs_df = pd.DataFrame()
        self.courses_df = pd.DataFrame()
        self.academic_df = pd.DataFrame()
        self.career_progressions_df = pd.DataFrame()
        self.esco_occ = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
        self.esco_skills = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
        self.occ_skill_rel = pd.DataFrame(columns=["occupationUri", "skillUri", "relationType"])
        self.broader_occ = pd.DataFrame(columns=["conceptUri", "broaderUri"])
        self.mentors_data = []
        self.salary_mapping = {"roles": {}, "sectors": {}}
        self.pricing_config = {}
        self.assessment_config = {}
        self.market_skills = []
        self._trend_cache = {}

        # ── Phase 10: Modular Logic Initialisation (Broken to Parts) ──
        self.rule_engine = RuleEngine()
        self.analytics = Analytics()
        self.recommender = Recommender(self)
        self.action_plan_gen = ActionPlanGenerator()

        # Shortcuts for backward compatibility or internal use
        self.domain_clusters = self.rule_engine.DOMAIN_CLUSTERS
        self.edu_levels = self.rule_engine.EDU_LEVELS

        # ── Phase 8: High-Confidence Academic Mappings (Sri Lanka) ──
        self.production_academic_programs = [
            {"level": "Bachelor", "course_name": "BSc in Data Science / Analytics", "provider": "SLIIT / NSBM / Open University", "duration": "3-4 years", "domain": "IT", "focus": ["SQL", "Statistics", "BI", "Visualization"], "notes": "Full academic pathway for career switchers", "url": "https://www.sliit.lk/computing/programmes/bsc-hons-in-information-technology-specializing-in-data-science/"},
            {"level": "Diploma", "course_name": "Diploma in Data Analytics", "provider": "National ICT Academy", "duration": "6 months", "domain": "IT", "focus": ["Analytics", "SQL"], "notes": "Fast-track entry into Data Science", "url": "https://www.nibm.lk/programmes/advanced-descriptor-in-data-science/"},
            {"level": "Postgraduate", "course_name": "MSc in Data Science", "provider": "UoM / UoC / Coursera", "duration": "1.5-2 years", "domain": "IT", "focus": ["Mastery", "Research"], "notes": "High credibility for career pivot", "url": "https://uom.lk/courses/msc-data-science-ai"},
            {"level": "Professional", "course_name": "Google Data Analytics Certificate", "provider": "Coursera", "duration": "6 months", "domain": "IT", "focus": ["Portfolio", "Skills"], "notes": "Practical transition certificate", "url": "https://www.coursera.org/professional-certificates/google-data-analytics"},
            
            {"level": "Bachelor", "course_name": "BSc in Marketing / Business Admin", "provider": "NSBM / UoC / SLIIT", "duration": "3-4 years", "domain": "Marketing", "focus": ["Analytics", "Content"], "notes": "Foundational creative marketing degree", "url": "https://www.sliit.lk/business/programmes/bba-special-honours-degree-in-marketing-management/"},
            {"level": "Postgraduate", "course_name": "MSc in Digital Marketing / MBA", "provider": "SLIIT / UoC / UK (Online)", "duration": "1-2 years", "domain": "Marketing", "focus": ["Leadership", "Strategy"], "notes": "Upskilling for senior leadership", "url": "https://www.nsbm.ac.lk/postgraduate/msc-in-business-analytics/"},
            {"level": "Diploma", "course_name": "Digital Marketing Diploma", "provider": "SLIM (Sri Lanka Institute of Marketing)", "duration": "6 months", "domain": "Marketing", "focus": ["Campaigns", "Readiness"], "notes": "High industry recognition in Sri Lanka", "url": "https://slim.lk/diploma-in-digital-marketing/"},
            {"level": "Professional", "course_name": "Google Digital Marketing Certificate", "provider": "HubSpot / Coursera", "duration": "6 months", "domain": "Marketing", "focus": ["Simulations", "Ads"], "notes": "Practical campaign skills", "url": "https://www.coursera.org/professional-certificates/google-digital-marketing-ecommerce"}
        ]
        
        #  Heavy Model Loading
        try:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            if self.show_progress: print(f"CRITICAL: Failed to load Transformer model: {e}")
            raise
        
        #  Data Loading Logic
        try:
            if from_mongo:
                self.load_from_mongo()
            else:
                # Default local paths if none provided
                jobs_path = jobs_path or str(self.ml_root / "data/processed/all_jobs_master.csv")
                courses_path = courses_path or str(self.ml_root / "data/processed/all_courses_master.csv")
                esco_dir = esco_dir or str(self.ml_root / "data/raw/esco")
                self._load_from_local(jobs_path, courses_path, esco_dir)
        except Exception as e:
            if self.show_progress: 
                print(f"Warning: Primary data loading interrupted: {e}")

        #  Common Post-Load Setup
        # Use ML root for models if not specified
        models_dir = models_dir or str(self.ml_root / "models")
        self._initialize_common(models_dir, force_refresh, courses_path)

    @classmethod
    def from_mongo(cls):
        """Factory method to initialize engine from MongoDB cloud data."""
        return cls(from_mongo=True)

    def load_from_mongo(self):
        """Fetches all primary datasets and configs from MongoDB Atlas."""
        if self.show_progress: print(" FETCHING DATA FROM MONGODB ATLAS")
        try:
            # Check for .env in current root
            env_path = self.ml_root / ".env"
            load_dotenv(dotenv_path=env_path if env_path.exists() else None)
            
            client = MongoClient(os.getenv("MONGO_URI"))
            db = client[os.getenv("DATABASE_NAME", "pathfinder_plus")]
            
            #  Load Jobs
            self.jobs_df = pd.DataFrame(list(db.jobs.find({}, {'_id': 0})))
            syn_jobs = pd.DataFrame(list(db.jobs_synthetic.find({}, {'_id': 0})))
            if not syn_jobs.empty:
                self.jobs_df = pd.concat([self.jobs_df, syn_jobs], ignore_index=True)
            
            # Load Courses
            self.courses_df = pd.DataFrame(list(db.courses.find({}, {'_id': 0})))
            self.academic_df = pd.DataFrame(list(db.courses_academic.find({}, {'_id': 0})))

            # Standardization Helper for Courses
            for df in [self.courses_df, self.academic_df]:
                if not df.empty:
                    if "course_title" not in df.columns and "course_name" in df.columns:
                        df.rename(columns={"course_name": "course_title"}, inplace=True)
                    if "provider" not in df.columns and "institute" in df.columns:
                        df.rename(columns={"institute": "provider"}, inplace=True)
            
            if self.show_progress:
                print(f"DEBUG: courses_df columns: {self.courses_df.columns.tolist()}")
                print(f"DEBUG: academic_df columns: {self.academic_df.columns.tolist()}")
            
            #  Load Mentors
            self.mentors_data = list(db.mentors.find({}, {'_id': 0}))
            
            #  Load Progressions
            self.career_progressions_df = pd.DataFrame(list(db.career_paths.find({}, {'_id': 0})))
            
            #  Load Salary Data
            salary_list = list(db.salary_data.find({}, {'_id': 0}))
            self.salary_mapping = {"roles": {}, "sectors": {}}
            for item in salary_list:
                title = str(item.get('job_title', item.get('title', 'Unknown'))).strip().lower()
                min_s = item.get('min_salary_lkr', item.get('salary_min', 0)) or 0
                max_s = item.get('max_salary_lkr', item.get('salary_max', 0)) or 0
                # Only store if we have actual data
                if min_s > 0 or max_s > 0:
                    self.salary_mapping["roles"][title] = {"min": min_s, "max": max_s}
            
            #  Load Configs from app_configs collection
            configs = list(db.app_configs.find({}, {'_id': 0}))
            config_dict = {cfg['config_key']: cfg['data'] for cfg in configs}
            self.pricing_config = config_dict.get('pricing_estimates', {})
            self.assessment_config = config_dict.get('scoring_config', {})
            self.assessment_questions = config_dict.get('assessment_questions', {})

            #  Load ESCO dataframes from Cloud
            self.esco_occ = pd.DataFrame(list(db.esco_occupations.find({}, {'_id': 0})))
            self.esco_skills = pd.DataFrame(list(db.esco_skills.find({}, {'_id': 0})))
            self.occ_skill_rel = pd.DataFrame(list(db.esco_relations.find({}, {'_id': 0})))
            self.broader_occ = pd.DataFrame(list(db.esco_broader.find({}, {'_id': 0})))

            # Fallback to empty DFs if collections missing
            if self.esco_occ.empty:
                self.esco_occ = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            if self.esco_skills.empty:
                self.esco_skills = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            if self.occ_skill_rel.empty:
                self.occ_skill_rel = pd.DataFrame(columns=["occupationUri", "skillUri", "relationType"])
            if self.broader_occ.empty:
                self.broader_occ = pd.DataFrame(columns=["conceptUri", "broaderUri"])

            # Ensure columns exist even if DF is empty
            for df_name, df_obj in [("courses_df", self.courses_df), ("academic_df", self.academic_df)]:
                 if df_obj.empty:
                     print(f"WARNING: {df_name} is EMPTY after cloud load.")
                 else:
                     print(f"INFO: {df_name} loaded with {len(df_obj)} rows. Columns: {df_obj.columns.tolist()}")

            if self.show_progress: print(f"Cloud Load Complete: {len(self.jobs_df)} jobs, {len(self.courses_df)} courses.")
            
        except Exception as e:
            if self.show_progress: print(f"Cloud Load Failed: {e}. Falling back to empty data.")
            import traceback
            traceback.print_exc()
            self.jobs_df = pd.DataFrame()
            self.courses_df = pd.DataFrame(columns=["course_title", "provider", "category", "description"])
            self.academic_df = pd.DataFrame(columns=["course_title", "provider", "category", "description"])
            self.mentors_data = []
            self.career_progressions_df = pd.DataFrame()
            self.salary_mapping = {"roles": {}, "sectors": {}}
            self.pricing_config = {}
            self.assessment_config = {}
            self.assessment_questions = {}
            self.esco_occ = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            self.esco_skills = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            self.occ_skill_rel = pd.DataFrame(columns=["occupationUri", "skillUri", "relationType"])
            self.broader_occ = pd.DataFrame(columns=["conceptUri", "broaderUri"])


    def _load_from_local(self, jobs_path, courses_path, esco_dir):
        """Legacy local CSV loading logic."""
        if not jobs_path or not courses_path or not esco_dir:
            if self.show_progress: print("Warning: Local paths missing. Initialize with from_mongo=True or provide paths.")
            self.jobs_df = pd.DataFrame()
            self.courses_df = pd.DataFrame()
            self.academic_df = pd.DataFrame()
            self.mentors_data = []
            self.career_progressions_df = pd.DataFrame()
            self.salary_mapping = {"roles": {}, "sectors": {}}
            self.pricing_config = {}
            self.assessment_config = {}
            self.esco_occ = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            self.esco_skills = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            self.occ_skill_rel = pd.DataFrame(columns=["occupationUri", "skillUri", "relationType"])
            self.broader_occ = pd.DataFrame(columns=["conceptUri", "broaderUri"])
            return

        # Load pricing config
        self.pricing_config = {}
        config_path = Path(jobs_path).parent.parent / "config" / "pricing_estimates.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.pricing_config = json.load(f)
        else:
             if self.show_progress: print(f"Warning: Pricing config not found at {config_path}")

        # Load datasets
        self.jobs_df = pd.read_csv(jobs_path)
        if not self.jobs_df.empty:
            if "title" not in self.jobs_df.columns and "Job Title" in self.jobs_df.columns:
                self.jobs_df.rename(columns={"Job Title": "title"}, inplace=True)

        #  Handle Course Data Swap (Correcting Inversion)
        # Based on file content:
        # 'academic_courses_master.csv' contains Skill Gaps (Datacamp, etc.) -> Should be Professional pool
        # 'all_courses_master.csv' contains institutional paths (AAT, Diplomas, Degrees) -> Should be Academic pool
        
        self.academic_df = pd.DataFrame()
        self.courses_df = pd.DataFrame()
        
        skill_gap_path = Path(courses_path).parent / "academic_courses_master.csv"
        academic_path = Path(courses_path).parent / "all_courses_master.csv"
        
        # 1. Load Professional Skill-Gap Pool (from academic_courses_master.csv)
        if skill_gap_path.exists():
            if self.show_progress: print(f"Loading Professional Skill-Gaps ({skill_gap_path.name})...")
            self.courses_df = pd.read_csv(skill_gap_path)
            self.courses_df['source_file'] = 'professional'
        
        # 2. Load Academic Learning Paths Pool (from all_courses_master.csv)
        if academic_path.exists():
            if self.show_progress: print(f"Loading Academic Learning Paths ({academic_path.name})...")
            self.academic_df = pd.read_csv(academic_path)
            self.academic_df['source_file'] = 'academic'
        
        # Standardize Course Columns
        for df in [self.courses_df, self.academic_df]:
            if df.empty: continue
            if "course_title" not in df.columns and "course_name" in df.columns:
                df.rename(columns={"course_name": "course_title"}, inplace=True)
            if "provider" not in df.columns and "institute" in df.columns:
                df.rename(columns={"institute": "provider"}, inplace=True)
        
        if self.academic_df.empty:
            if self.show_progress: print("Note: No academic courses found in standalone file or unified dataset.")

        # 1. Primary High-Fidelity Config (Calibrated LKR)
        # RELATIVE PATH from this file (core/recommendation_engine.py)
        # Path is ../data/config/salary_config.json
        current_file_path = Path(__file__).resolve()
        salary_json_path = current_file_path.parent.parent / "data" / "config" / "salary_config.json"
        
        # Log for debugging
        with open(current_file_path.parent / "salary_load_debug.log", "w") as logf:
            logf.write(f"Trying path: {salary_json_path}\n")
            logf.write(f"Exists: {salary_json_path.exists()}\n")
            
        if salary_json_path.exists():
            if self.show_progress: print(f"Loading Calibrated Salaries ({salary_json_path.name})...")
            with open(salary_json_path, 'r') as f:
                self.salary_mapping = json.load(f)
                if "roles" in self.salary_mapping:
                    lowered_roles = {}
                    for k, v in self.salary_mapping["roles"].items():
                        lowered_roles[k.lower()] = v
                    self.salary_mapping["roles"] = lowered_roles

        # 2. Additional Granular Mapping (Paylab)
        salary_cfg_path = self.ml_root / "data" / "config" / "paylab_salary_mapping.csv"
        if salary_cfg_path.exists():
            try:
                sal_df = pd.read_csv(salary_cfg_path)
                for _, row in sal_df.iterrows():
                    title = str(row['job_title']).strip().lower()
                    ranges = {
                        "min": row['min_salary_lkr'],
                        "avg": row['avg_salary_lkr'],
                        "max": row['max_salary_lkr']
                    }
                    self.salary_mapping["roles"][title] = ranges
                    
                # Populate sector fallback
                for _, row in sal_df.iterrows():
                    sec = str(row['paylab_category']).strip()
                    if sec not in self.salary_mapping["sectors"]:
                        self.salary_mapping["sectors"][sec] = {
                            "min": row['min_salary_lkr'],
                            "avg": row['avg_salary_lkr'],
                            "max": row['max_salary_lkr']
                        }
            except Exception:
                pass

        #  Load Synthetic Jobs if available (Demo Enhancement)
        syn_jobs_path = Path(jobs_path).parent / "synthetic_jobs.csv"
        if syn_jobs_path.exists():
            if self.show_progress: print(f"Merging synthetic jobs ({syn_jobs_path.name})...")
            syn_df = pd.read_csv(syn_jobs_path)
            self.jobs_df = pd.concat([self.jobs_df, syn_df], ignore_index=True)

        #  Load Synthetic Mentors
        self.mentors_data = []
        mentors_path = Path(jobs_path).parent / "mentors.json"
        if mentors_path.exists():
            try:
                with open(mentors_path, 'r') as f:
                    self.mentors_data = json.load(f)
                if self.show_progress: print(f"Loaded {len(self.mentors_data)} mentors.")
            except Exception:
                pass

        #  Load Career Progressions
        prog_path = Path(jobs_path).parent / "career_progressions.csv"
        if prog_path.exists():
            self.career_progressions_df = pd.read_csv(prog_path)
            if self.show_progress: print(f"Loaded {len(self.career_progressions_df)} career progression paths.")
        else:
            self.career_progressions_df = pd.DataFrame()
            if self.show_progress: print("Warning: career_progressions.csv not found.")

        # Load market context advice
        advice_path = Path(esco_dir).parent / "market_context" / "sl_sector_advice.csv"
        if advice_path.exists():
            self.market_advice_df = pd.read_csv(advice_path)
        else:
            self.market_advice_df = None

        # LOAD ESCO DATA 
        try:
            esco_path = Path(esco_dir)
            if (esco_path / "occupations_en.csv").exists():
                self.esco_occ = pd.read_csv(esco_path / "occupations_en.csv")
                self.esco_skills = pd.read_csv(esco_path / "skills_en.csv")
                self.occ_skill_rel = pd.read_csv(esco_path / "occupationSkillRelations_en.csv")
            else:
                if self.show_progress: print("WARNING: ESCO files not found. Using empty dataframes.")
                self.esco_occ = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
                self.esco_skills = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
                self.occ_skill_rel = pd.DataFrame(columns=["occupationUri", "skillUri", "relationType"])
        except Exception as e:
            if self.show_progress: print(f"ERROR loading ESCO: {e}. Falling back to empty data.")
            self.esco_occ = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            self.esco_skills = pd.DataFrame(columns=["preferredLabel", "conceptUri"])
            self.occ_skill_rel = pd.DataFrame(columns=["occupationUri", "skillUri", "relationType"])
        # load broader occupations for progression (With Fallbacks)
        try:
            if (esco_path / "broaderRelationsOccPillar_en.csv").exists():
                self.broader_occ = pd.read_csv(esco_path / "broaderRelationsOccPillar_en.csv")
            else:
                self.broader_occ = pd.DataFrame(columns=["conceptUri", "broaderUri"])
        except Exception:
            self.broader_occ = pd.DataFrame(columns=["conceptUri", "broaderUri"])

 
    def _initialize_common(self, models_dir, force_refresh, courses_path):
        """Standard setup logic for both local and cloud modes."""
        #  Models Path
        if models_dir is None:
            models_path = Path(__file__).parent.parent / "models"
        else:
            models_path = Path(models_dir)
        models_path.mkdir(parents=True, exist_ok=True)

        #  Extract Market Skills (Critical for matching logic)
        self.market_skills = []
        
        # 1. Primary Source: ESCO Skills
        if hasattr(self, 'esco_skills') and not self.esco_skills.empty:
            self.market_skills = self.esco_skills['preferredLabel'].dropna().str.lower().tolist()
        
        # 2. Supplementary: Extracted from jobs (if available)
        if hasattr(self, 'jobs_df') and not self.jobs_df.empty and 'extracted_skills' in self.jobs_df.columns:
            job_skills = []
            for s in self.jobs_df['extracted_skills'].dropna():
                if isinstance(s, str):
                    job_skills.extend([sk.strip().lower() for sk in s.split(',')])
            self.market_skills = list(set(self.market_skills + job_skills))
        
        # Remove duplicates and extremely short terms (e.g. "it", "at") to avoid noisy matching
        self.market_skills = list(set([s for s in self.market_skills if isinstance(s, str) and len(s) > 3]))
            
        #  Initialize Trend Analyzer
        try:
             # In cloud mode, courses_path might be None, but analyzer needs jobs data
             # We use jobs_df directly from the engine
            self.trend_analyzer = MarketTrendAnalyzer(self.jobs_df)
        except Exception as e:
            if self.show_progress: print(f"Warning: Trend Analyzer failed: {e}")
            self.trend_analyzer = None

        self._trend_cache = {}

        #  Load or Build Embeddings
        self._load_or_build_embeddings(models_path, force_refresh, courses_path)

        # ── Load / Train Hybrid ML Layer ──────────────────────────────────────
        # Augments SBERT with structured ML signal (RF + GBM + KNN)
        self.ml_layer = None
        if HybridMLLayer is not None:
            try:
                ml = HybridMLLayer(models_dir=models_path)
                loaded = ml.load()  # Try to load pre-trained models
                if not loaded:
                    if self.show_progress:
                        print("[HybridML] Pre-trained models not found — training now...")
                    ml.train(verbose=self.show_progress)
                    ml.save()
                else:
                    if self.show_progress:
                        print(f"[HybridML] ✓ Loaded: {ml}")
                self.ml_layer = ml
            except Exception as e:
                if self.show_progress:
                    print(f"[HybridML] ⚠ Could not init ML layer: {e} — SBERT-only mode.")
                self.ml_layer = None

    def _load_or_build_embeddings(self, models_path, force_refresh, courses_path):
        """Logic moved from legacy init into a dedicated method."""
        # Ensure courses_path is string-safe for filename generation
        course_filename = Path(courses_path).stem if courses_path else "cloud_courses"
        
        if self.show_progress:
            print(f"DEBUG EMBED: jobs_df columns: {self.jobs_df.columns.tolist() if not self.jobs_df.empty else 'EMPTY'}")
            print(f"DEBUG EMBED: courses_df columns: {self.courses_df.columns.tolist() if not self.courses_df.empty else 'EMPTY'}")
     
        # Load assessment config
        config_path = Path(__file__).parent.parent / "data" / "raw" / "assessment" / "scoring_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.assessment_config = json.load(f)
        else:
            self.assessment_config = {}

        # load esco embeddings
        esco_emb_file = models_path / "esco_occ_embeddings.pt"
        rebuild_esco = True
        
        if esco_emb_file.exists() and not force_refresh:
            if self.show_progress: print(f"Loading pre-computed ESCO embeddings from {esco_emb_file}")
            try:
                loaded_esco = torch.load(esco_emb_file)
                if len(loaded_esco) == len(self.esco_occ):
                    self.esco_occ_embs = loaded_esco
                    rebuild_esco = False
                else:
                    print(f"WARNING: ESCO Embedding size ({len(loaded_esco)}) != Dataframe size ({len(self.esco_occ)}). Rebuilding...")
            except Exception as e:
                print(f"Error loading ESCO embeddings: {e}. Rebuilding...")

        if rebuild_esco:
            if self.show_progress: print("Encoding ESCO occupations...")
            self.esco_occ_embs = self.model.encode(
                self.esco_occ["preferredLabel"].tolist(),
                convert_to_tensor=True,
                show_progress_bar=self.show_progress,
            )
            torch.save(self.esco_occ_embs, esco_emb_file)

        # load Embeddings for (Professional)
        course_emb_file = models_path / f"course_embeddings_{course_filename}.pt"
        
        rebuild_courses = True
        if course_emb_file.exists() and not force_refresh:
            if self.show_progress: print(f"Loading pre-computed course embeddings from {course_emb_file}")
            try:
                loaded_embs = torch.load(course_emb_file)
                if len(loaded_embs) == len(self.courses_df):
                    self.course_embs = loaded_embs
                    rebuild_courses = False
                else:
                    print(f"WARNING: Embedding size ({len(loaded_embs)}) != Dataframe size ({len(self.courses_df)}). Rebuilding...")
            except Exception:
                pass
        
        if rebuild_courses:
            if self.show_progress: print(f"Encoding professional courses for {course_filename}...")
            # Use 'cat' instead of 'category' if available, as 'category' might be missing in unified CSV
            cat_col = "cat" if "cat" in self.courses_df.columns else "category"
            desc_cols = ["description", "course_title"] # Try description, fallback to title for text
            
            course_texts = (
                self.courses_df["course_title"].fillna("")
                + " "
                + self.courses_df[cat_col].fillna("")
                + " "
                + self.courses_df[desc_cols[0] if desc_cols[0] in self.courses_df.columns else desc_cols[1]].fillna("")
            ).tolist()

            self.course_embs = self.model.encode(
                course_texts, convert_to_tensor=True, show_progress_bar=self.show_progress
            )
            torch.save(self.course_embs, course_emb_file)

        # loading academic embeddings
        academic_emb_file = models_path / "academic_embeddings.pt"
        rebuild_academic = True
        
        if not self.academic_df.empty:
            if academic_emb_file.exists() and not force_refresh:
                if self.show_progress: print(f"Loading pre-computed academic embeddings from {academic_emb_file}")
                try:
                    loaded_acad = torch.load(academic_emb_file)
                    if len(loaded_acad) == len(self.academic_df):
                        self.academic_embs = loaded_acad
                        rebuild_academic = False
                    else:
                        print(f"WARNING: Academic Embedding size ({len(loaded_acad)}) != Dataframe size ({len(self.academic_df)}). Rebuilding...")
                except Exception:
                    pass

            if rebuild_academic:
                if self.show_progress: print("Encoding academic degree programs...")
                cat_col = "cat" if "cat" in self.academic_df.columns else "category"
                
                acad_texts = (
                    self.academic_df["course_title"].fillna("")
                    + " "
                    + self.academic_df[cat_col].fillna("")
                    + " "
                    + self.academic_df["description"].fillna("")
                ).tolist()
                
                self.academic_embs = self.model.encode(
                    acad_texts, convert_to_tensor=True, show_progress_bar=self.show_progress
                )
                torch.save(self.academic_embs, academic_emb_file)
        else:
            self.academic_embs = None

        # Job emddding load
        job_emb_file = models_path / "job_embeddings.pt"
        rebuild_jobs = True
        
        if not self.jobs_df.empty and "title" in self.jobs_df.columns:
            # We only use titles for the moment for semantic search speed
            self.job_titles_list = self.jobs_df["title"].fillna("").tolist()
            
            if job_emb_file.exists() and not force_refresh:
                if self.show_progress: print(f"Loading pre-computed Job embeddings from {job_emb_file}")
                try:
                    loaded_jobs = torch.load(job_emb_file)
                    if len(loaded_jobs) == len(self.job_titles_list):
                        self.job_embs = loaded_jobs
                        rebuild_jobs = False
                    else:
                        print(f"WARNING: Job Embedding size ({len(loaded_jobs)}) != Dataframe size ({len(self.job_titles_list)}). Rebuilding...")
                except Exception as e:
                    print(f"Error loading Job embeddings: {e}. Rebuilding...")

            if rebuild_jobs:
                if self.show_progress: print(f"Encoding {len(self.job_titles_list)} jobs...")
                self.job_embs = self.model.encode(
                    self.job_titles_list,
                    convert_to_tensor=True,
                    show_progress_bar=self.show_progress
                )
                torch.save(self.job_embs, job_emb_file)
        else:
            self.job_embs = None
            self.job_titles_list = []

    def get_salary_for_role(self, role_title, experience_level="Entry"):
        """Retrieves salary range from config (fuzzy match)"""
        if not hasattr(self, "salary_mapping") or not self.salary_mapping:
            return {}
            
        role_map = self.salary_mapping.get("roles", {})
        role_key_raw = str(role_title).strip()
        role_key_lower = role_key_raw.lower()
        
        # helper to process level dicts (V3 Gold Logic)
        def resolve_level(data, level):
            import re
            
            def parse_salary_string(s):
                nums = re.findall(r'\d+', str(s).replace(',', ''))
                if len(nums) >= 2:
                    min_val = int(nums[0])
                    max_val = int(nums[1])
                    return {"min": min_val, "avg": (min_val + max_val) // 2, "max": max_val}
                elif len(nums) == 1:
                    return {"min": int(nums[0]), "avg": int(nums[0]), "max": int(nums[0])}
                return {"min": 50000, "avg": 80000, "max": 120000}
                
            raw_val = None
            if isinstance(data, dict):
                keys = [k.lower() for k in data.keys()]
                if level.lower() in keys:
                    raw_val = data.get(next(k for k in data.keys() if k.lower() == level.lower()))
                elif any(kw in role_key_lower for kw in ["senior", "lead", "chief", "cto", "manager"]):
                    if "senior" in keys: raw_val = data.get(next(k for k in data.keys() if k.lower() == "senior"))
                    elif "mid" in keys: raw_val = data.get(next(k for k in data.keys() if k.lower() == "mid"))
                elif "avg" in data:
                    return {"avg": data["avg"], "min": data["min"], "max": data["max"]}
                
                if raw_val is None:
                    raw_val = list(data.values())[0]
            else:
                raw_val = data
                
            return parse_salary_string(raw_val)

        # 1. Exact Match
        if role_key_lower in role_map:
            return resolve_level(role_map[role_key_lower], experience_level)
            
        # 2. Fuzzy Match (Contains)
        for known_role, levels in role_map.items():
            if known_role.lower() in role_key_lower or role_key_lower in known_role.lower():
                return resolve_level(levels, experience_level)
                
        # 3. Sector Fallback (V3 Priority Mapping)
        sectors = self.salary_mapping.get("sectors", {})
        
        # Priority 1: Management/Executive (Chief, CTO, CEO, Manager)
        if any(kw in role_key_lower for kw in ["manag", "product", "project", "strategy", "director", "executive", "chief", "cto", "ceo", "cio"]):
            return resolve_level(sectors.get("Management", "250,000 - 600,000 LKR"), experience_level)
            
        # Priority 2: Technical/IT
        if any(kw in role_key_lower for kw in ["software", "developer", "engineer", "data", "it", "ict", "technology", "tech"]):
            return resolve_level(sectors.get("IT", "180,000 - 450,000 LKR"), experience_level)
            
        # Priority 3: Other Sectors
        if any(kw in role_key_lower for kw in ["account", "finance", "bank", "audit", "tax"]):
            return resolve_level(sectors.get("Finance", "150,000 - 350,000 LKR"), experience_level)
        if any(kw in role_key_lower for kw in ["nurse", "health", "hospital", "care", "doctor", "medical", "pharmacist"]):
            return resolve_level(sectors.get("Healthcare", "150,000 - 400,000 LKR"), experience_level)
        if any(kw in role_key_lower for kw in ["market", "pr", "advertis", "seo", "social"]):
            return resolve_level(sectors.get("Marketing", "120,000 - 300,000 LKR"), experience_level)
            
        return {}

    def _infer_domain(self, text: str) -> str:
        """Delegated to Phase 10 RuleEngine."""
        return self.rule_engine.infer_domain(text)

    def calculate_local_demand_score(self, domain: str) -> float:
        """Delegated to Phase 10 Analytics."""
        return self.analytics.calculate_local_demand_score(domain, self.jobs_df, self.salary_mapping, self.rule_engine)

    def process_comprehensive_assessment(self, answers: Dict[str, Any]):
        """
        Processes the assessment into a Feature Vector for the Rule Engine.
        """
        # Aliasing for 12-question and varied assessment compatibility
        alias_map = {
            "career_stage": "current_status",
            "status": "current_status",
            "career_background": "self_bio",
            "q13": "self_bio",
            "key_achievements": "ideal_workday",
            "q15": "ideal_workday",
            "total_experience": "experience_years",
            "budget_range": "upskilling_budget",
            "weekly_time": "weekly_availability",
            "education_type": "education_preference"
        }
        
        # Merge aliases into a copy of answers
        remapped_answers = answers.copy()
        for old, new in alias_map.items():
            if old in answers and new not in answers:
                remapped_answers[new] = answers[old]

        vector = {}
        # Normalize strings and handle specific characters
        norm_answers = {k: str(v).replace('–', '-').replace('—', '-').strip() if isinstance(v, str) else v for k, v in remapped_answers.items()}
        
        # 1. Experience Years (Absolute mapped values)
        experience_map = {
            "0 (None)": 0, "1-2 years": 1.5, "3-5 years": 4, "6-10 years": 8, "10+ years": 12
        }
        experience = norm_answers.get("experience_years", "0 (None)")
        vector["experience_years"] = experience_map.get(experience, 0)
        
        # 2. Responsibility Band (0-4)
        resp_level = norm_answers.get("responsibility_level", "Followed instructions")
        band_map = {
            "Followed instructions": 0, "Completed independent tasks": 1, "Planned tasks": 2, 
            "Supervised others": 3, "Managed outcomes / budgets": 4
        }
        vector["responsibility_band"] = band_map.get(resp_level, 0)
        
        # 3. Highest Education (0-6)
        edu_str = norm_answers.get("highest_education", "O/L or School Level").lower()
        vector["highest_education"] = edu_str
        edu_val = 1
        for k, v in self.edu_levels.items():
            if k in edu_str: edu_val = max(edu_val, v)
        vector["education_level"] = edu_val
        
        # 4. Status Level (0-3)
        # 0: Student, 1: Uni/Graduate, 2: Professional, 3: Switcher
        status_raw = norm_answers.get("current_status", "Student / School Leaver")
        status_map = {
            "Student / School Leaver": 0, "University Student": 1, 
            "Working Professional": 2, "Career Switcher": 3
        }
        vector["status_level"] = status_map.get(status_raw, 0)
        
        # 5. Domain & Education Preference
        vector["target_role"] = norm_answers.get("target_role", "General")
        vector["domain"] = norm_answers.get("domain", self._infer_domain(vector["target_role"]))
        vector["education_preference"] = norm_answers.get("education_preference", "None")
        
        # 6. Skill Extraction (With Domain Guard)
        full_text = f"{norm_answers.get('self_bio', '')} {norm_answers.get('ideal_workday', '')} {vector['target_role']}"
        if full_text.strip():
            vector["intent_embedding"] = self.model.encode(full_text).tolist()
            
            # Rule Engine Blacklist (Hallucination Prevention)
            blacklist = [
                "air traffic management", "cad software", "cam software", "cae software", 
                "technical drawing", "traffic management", "aerospace", "mechanical drawing"
            ]
            
            full_text_lower = full_text.lower()
            extracted = []
            
            for s in self.market_skills:
                s_low = s.lower().strip()
                if len(s_low) < 5 or s_low in blacklist:
                    continue
                
                # Rule: Check against Hallucination Blacklist
                if any(b in s_low for b in RuleEngine.HALLUCINATION_BLACKLIST):
                    continue

                # Rule: No cross-domain skills (e.g. Nursing for IT)
                s_domain = self.rule_engine.infer_domain(s_low)
                if vector["domain"] != "General" and s_domain != "General" and s_domain != vector["domain"]:
                    continue

                words = s_low.split()
                if len(words) == 1:
                    if re.search(r'\b' + re.escape(s_low) + r'\b', full_text_lower):
                        extracted.append(s)
                else:
                    meaningful = [w for w in words if len(w) > 3]
                    if meaningful and all(re.search(r'\b' + re.escape(w) + r'\b', full_text_lower) for w in meaningful):
                        extracted.append(s)
            
            vector["extracted_intent_skills"] = sorted(list(set(extracted)))
        else:
            vector["intent_embedding"] = []
            vector["extracted_intent_skills"] = []

        # 7. Constraints
        vector["budget_category"] = norm_answers.get("upskilling_budget", "< 50k")
        vector["time_commitment"] = norm_answers.get("weekly_availability", "5-10 hours")
        vector["education_preference"] = norm_answers.get("education_preference", "None")

        # 8. Normalized Soft Skills for UI (0-100)
        ps_map = {
            "Search for similar issues and try common fixes": 40,
            "Analyze the root cause and propose a new approach": 70,
            "Collaborate with others to find the most efficient fix": 90,
            "Escalate immediately": 20
        }
        ad_map = {
            "Follow the new directives strictly": 50,
            "Pivot quickly while documenting the change": 80,
            "Assess the impact on goals and align the team": 90,
            "Resist changes that disrupt workflow": 20
        }
        
        ps_val = norm_answers.get("problem_solving", "Search for similar issues and try common fixes")
        ad_val = norm_answers.get("adaptability", "Follow the new directives strictly")
        
        # Estimate teamwork based on problem solving choice
        teamwork_val = 80 if "Collaborate" in ps_val else 50
        
        vector["normalized_soft_skills"] = {
            "problem_solving": ps_map.get(ps_val, 50),
            "adaptability": ad_map.get(ad_val, 50),
            "teamwork": teamwork_val
        }

        return vector

    def _should_recommend_internships(self, assessment_vector: Dict[str, Any]) -> bool:
        """Strict check to ensure professionals don't get internship paths//"""
        exp = assessment_vector.get("experience_years", 0)
        status = assessment_vector.get("status_level", 0)
        # Professionals (> 0 exp or status level 3) should usually bypass internships
        return exp == 0 and status <= 1

    def get_recommendations_from_assessment(self, assessment_vector: Dict[str, Any], target_job: str):
        """
        Phase 7: Production Entry Point (V3 Gold).
        Returns the definitive 11-Point Dashboard Bundle.
        """
        user_skills = assessment_vector.get("extracted_intent_skills", [])
        
        # recommend_courses now orchestrates the entire V3 Gold Bundle internally
        bundle = self.recommend_courses(
            user_skills=user_skills,
            target_job=target_job,
            top_n=8,
            assessment_vector=assessment_vector
        )
        return bundle

    def _get_salary_intelligence(self, domain: str, seniority: str) -> Dict[str, Any]:
        """Provides simulated local Paylab salary intelligence based on domain and seniority."""
        salary_matrix = {
            "IT": {
                "School Level": {"min": 30000, "avg": 45000, "max": 75000},
                "Entry": {"min": 80000, "avg": 120000, "max": 250000},
                "Professional": {"min": 250000, "avg": 450000, "max": 800000},
            },
            "Healthcare": {
                "School Level": {"min": 25000, "avg": 35000, "max": 50000},
                "Entry": {"min": 45000, "avg": 75000, "max": 120000},
                "Professional": {"min": 120000, "avg": 250000, "max": 600000},
            },
            "Marketing": {
                "School Level": {"min": 20000, "avg": 35000, "max": 50000},
                "Entry": {"min": 60000, "avg": 90000, "max": 180000},
                "Professional": {"min": 180000, "avg": 350000, "max": 700000},
            },
            "Finance": {
                "School Level": {"min": 25000, "avg": 40000, "max": 60000},
                "Entry": {"min": 70000, "avg": 110000, "max": 200000},
                "Professional": {"min": 200000, "avg": 400000, "max": 900000},
            },
            "General": {
                "School Level": {"min": 20000, "avg": 30000, "max": 45000},
                "Entry": {"min": 50000, "avg": 80000, "max": 150000},
                "Professional": {"min": 150000, "avg": 250000, "max": 500000},
            }
        }
        
        domain_data = salary_matrix.get(domain, salary_matrix["General"])
        
        seniority_cat = "Professional"
        if "Entry" in seniority or "Undergraduate" in seniority or "Graduate" in seniority:
            seniority_cat = "Entry"
        elif "School" in seniority:
            seniority_cat = "School Level"
            
        return {
            "source": "Paylab Sri Lanka Local Estimate",
            "currency": "LKR/Month",
            "domain": domain,
            "seniority_tier": seniority_cat,
            "min_salary": domain_data[seniority_cat]["min"],
            "avg_salary": domain_data[seniority_cat]["avg"],
            "max_salary": domain_data[seniority_cat]["max"]
        }

    def _get_career_roadmap(self, domain: str) -> List[Dict[str, Any]]:
        """Provides heuristic vertical and horizontal career progression for the roadmap."""
        roadmaps = {
            "IT": [
                {"title": "Senior Developer", "type": "Vertical", "similarity": 0.9},
                {"title": "Software Architect", "type": "Vertical", "similarity": 0.8},
                {"title": "Product Manager (Tech)", "type": "Horizontal", "similarity": 0.7},
                {"title": "DevOps Engineer", "type": "Horizontal", "similarity": 0.75}
            ],
            "Healthcare": [
                {"title": "Senior Nurse / Ward Manager", "type": "Vertical", "similarity": 0.9},
                {"title": "Nurse Practitioner", "type": "Vertical", "similarity": 0.85},
                {"title": "Clinical Research Coordinator", "type": "Horizontal", "similarity": 0.7},
                {"title": "Healthcare Administrator", "type": "Horizontal", "similarity": 0.65}
            ],
            "Marketing": [
                {"title": "Marketing Manager", "type": "Vertical", "similarity": 0.9},
                {"title": "Growth Lead", "type": "Vertical", "similarity": 0.8},
                {"title": "Data Analyst (Marketing)", "type": "Horizontal", "similarity": 0.75},
                {"title": "PR / Communications Specialist", "type": "Horizontal", "similarity": 0.7}
            ],
            "Finance": [
                {"title": "Senior Accountant / Auditor", "type": "Vertical", "similarity": 0.9},
                {"title": "Financial Controller", "type": "Vertical", "similarity": 0.8},
                {"title": "Risk Analyst", "type": "Horizontal", "similarity": 0.75},
                {"title": "Investment Consultant", "type": "Horizontal", "similarity": 0.7}
            ]
        }
        return roadmaps.get(domain, roadmaps["IT"])

    def recommend_jobs(self, user_skills, target_role, top_n=5):
        """Matches users to real-time job openings from the database with domain fallback."""
        if self.jobs_df is None or self.jobs_df.empty:
             return []
        
        # 1. Try SBERT Semantic Search
        if hasattr(self, 'job_embs') and self.job_embs is not None:
            try:
                query = f"{target_role} " + " ".join(user_skills[:5])
                query_emb = self.model.encode(query, convert_to_tensor=True)
                hits = util.semantic_search(query_emb, self.job_embs, top_k=top_n*2)[0]
                
                results = []
                for hit in hits:
                    idx = hit['corpus_id']
                    if idx >= len(self.jobs_df): continue
                    job = self.jobs_df.iloc[idx]
                    results.append({
                        "job_title": job["title"],
                        "company": job.get("company", "Confidential"),
                        "location": job.get("location", "Sri Lanka"),
                        "link": job.get("job_url", job.get("url", "#")),
                        "relevance_score": round(float(hit['score']) * 100, 1)
                    })
                return results[:top_n]
            except Exception as e:
                pass # Fallback to keyword search

        # 2. Fallback: Keyword-based Domain Search (if embeddings missing)
        return self.recommender.recommend_jobs_domain_filtered(user_skills, target_role, top_n)

    
    # course classificatin
   
    # classify course level (updated for msc/degree)
    def classify_course_level(self, title, duration):
        title = str(title).lower()
        duration = str(duration).lower()

        # separate postgrad from undergrad
        if any(x in title for x in ["msc", "master", "phd", "doctorate", "postgraduate", "mba"]):
            return "Postgraduate"

        if any(x in title for x in ["degree", "bsc", "bachelor", "undergraduate"]):
            return "Academic (Degree)"
        
        if any(x in title for x in ["diploma", "hnd", "foundation"]):
            return "Academic (Diploma)"

        if any(x in title for x in ["advanced", "professional", "expert", "architect", "management"]):
            return "Professional"

        if any(x in title for x in ["intro", "basic", "beginner", "fundamental", "bootcamp"]):
            return "Beginner"

        return "Mid-Level"

    
    # get skills for job
    def get_skills_for_job(self, job_title):
        # try to find skills from local jobs first
        local_matches = self.jobs_df[
            self.jobs_df["title"].str.contains(job_title, case=False, na=False)
        ]
        
        local_skills = []
        if not local_matches.empty:
            # aggregate skills from top matches
            for idx, row in local_matches.head(10).iterrows():
                if pd.notna(row.get("extracted_skills")):
                    # assuming extracted_skills is a string
                    skills = row["extracted_skills"]
                    if isinstance(skills, str):
                        local_skills.extend([s.strip() for s in skills.split(",")])
                    elif isinstance(skills, list):
                        local_skills.extend(skills)
        
        local_skills = list(set(s for s in local_skills if len(s) > 2))
        
        # esco fallback using essential relations
        job_emb = self.model.encode(job_title, convert_to_tensor=True)
        hit = util.semantic_search(job_emb, self.esco_occ_embs, top_k=1)[0][0]
        occ = self.esco_occ.iloc[hit["corpus_id"]]

        # only pick essential skills to avoid random languages
        rel = self.occ_skill_rel[
            (self.occ_skill_rel["occupationUri"] == occ["conceptUri"]) & 
            (self.occ_skill_rel["relationType"] == "essential")
        ]
        esco_skills_all = self.esco_skills[
            self.esco_skills["conceptUri"].isin(rel["skillUri"])
        ]["preferredLabel"].tolist()

        #  Cross reference with available jobs
        if self.market_skills:
            esco_skills = [s for s in esco_skills_all if s.lower() in self.market_skills or any(ms in s.lower() for ms in self.market_skills)]
           
            if len(esco_skills) < 5:
                esco_skills = esco_skills_all
        else:
            esco_skills = esco_skills_all

        combined_skills = list(set(local_skills + esco_skills[:12]))
        
        return combined_skills, occ["preferredLabel"]
    
    
    def estimate_responsibility_band(self, user_skills, years_exp=0):
        """Estimate Responsibility Band (0-4) based on skills and years of experience"""
        band = 0
        
        # Base on years of experience
        if years_exp >= 10: band = 4
        elif years_exp >= 6: band = 3
        elif years_exp >= 3: band = 2
        elif years_exp >= 1: band = 1
        
        #  Skill-based adjustments 
        complexity_signals = {
            "strategy": 3, "leadership": 3, "architecture": 3, "management": 3,
            "budgeting": 3, "transformation": 4, "board": 4, "design patterns": 2,
            "refactoring": 2, "deployment": 1
        }
        
        for skill in user_skills:
            skill_lower = skill.lower()
            for signal, level in complexity_signals.items():
                if signal in skill_lower:
                    band = max(band, level)
                    
        # Cap band by practical experience to prevent Juniors from becoming 'Leads'
        max_allowed = 1 if years_exp < 2 else (2 if years_exp < 4 else 4)
        band = min(band, max_allowed)
                    
        return band

    def get_career_progression(self, current_role, current_band, user_skills, assessment_vector=None, top_n=5):
        """Returns 5 vertical and 5 horizontal path steps."""
        progression = []
        
        # Check for Internship/Entry Level Recommendation
        if assessment_vector and self._should_recommend_internships(assessment_vector):
            # Find internship paths matching interest or generic IT
            intern_paths = self.career_progressions_df[
                self.career_progressions_df['current_role'].str.contains('Intern', case=False, na=False)
            ]
            
            # Rank internships by relevance to User Skills & Intent
            scored_paths = []
            
            # Combine explicit skills and partial matches from role names
            search_terms = [s.lower() for s in user_skills]
            if current_role and current_role != "None":
                search_terms.append(current_role.lower())
                
            for _, row in intern_paths.iterrows():
                score = 0
                row_text = f"{row['track_name']} {row['next_role']} {row['requirements']}".lower()
                
                #  Keyword Matching (Skills & Interests)
                for term in search_terms:
                    if term in row_text:
                        score += 5  # Strong match
                    elif any(t in row_text for t in term.split()):
                        score += 1  # Partial match
                
                #  Track Name Priority
                if current_role and current_role.lower() in str(row['track_name']).lower():
                    score += 10
                    
                scored_paths.append((score, row))
            
            # Sort by score descending
            scored_paths.sort(key=lambda x: x[0], reverse=True)
            
            # Return top 5 filtered paths (or defaults if no match found)
            top_paths = [p[1] for p in scored_paths[:5]] if scored_paths and scored_paths[0][0] > 0 else intern_paths.head(5).iterrows()
            
            # Handle the iteration difference (list vs generator)
            iterable_paths = top_paths if isinstance(top_paths, list) else [r for _, r in top_paths]

            for row in iterable_paths:
                progression.append({
                    "type": "Entry Level (Internship)",
                    "role": row['next_role'], # The target is the Junior role
                    "current_step": row['current_role'],
                    "target_band": 1,
                    "typical_years": row['typical_years'],
                    "advice": f"Start here: {row['requirements'] or 'Gain foundational skills'}"
                })

        # Data-Driven Paths (Primary Method)
        found_data_driven = False
        if not self.career_progressions_df.empty:
            matches = self.career_progressions_df[
                self.career_progressions_df['current_role'].str.contains(current_role, case=False, na=False)
            ]
            
            if not matches.empty:
                found_data_driven = True
                for _, row in matches.head(5).iterrows():
                    progression.append({
                        "type": "Vertical (Promotion)",
                        "role": row['next_role'],
                        "target_band": current_band + 1,
                        "typical_years": row['typical_years'],
                        "advice": f"Progression path: {row['requirements']}"
                    })

        # 3. Fallback: Band-based Vertical Promotion
        # Needing 7+ years experience and a Master's degree. Now we use status_level
        # AND experience_years together to pick the correct target label.
        if not found_data_driven and current_band < 4:
            target_band  = current_band + 1
            status_level = assessment_vector.get("status_level", 0) if assessment_vector else 0
            exp_years    = assessment_vector.get("experience_years", 0) if assessment_vector else 0
            highest_edu  = str(assessment_vector.get("highest_education", "")).lower() if assessment_vector else ""
            has_postgrad = any(k in highest_edu for k in ["master", "msc", "mba", "phd", "postgrad"])

            # Pick target label based on ACTUAL seniority — not just status_level alone
            if exp_years >= 8 or (exp_years >= 5 and has_postgrad):
                # Clearly Senior/Lead territory
                target_label = "Senior"
                curr_label   = "Mid-Level"
            elif exp_years >= 4 or status_level >= 2:
                # Professional → Senior step
                target_label = "Lead"
                curr_label   = "Professional"
            elif exp_years >= 1 or status_level == 1:
                # Graduate → Professional step
                target_label = "Senior"
                curr_label   = "Junior"
            else:
                # True entry level  school leaver or no exp
                prefixes = ["Junior", "Associate", "Assistant", "Trainee"]
                curr_label   = "Entry/Student"
                target_label = "Junior" if not any(p in current_role for p in prefixes) else ""

            target_role = f"{target_label} {current_role}".strip()
            
            progression.append({
                "type": "Vertical (Promotion)",
                "role": target_role,
                "target_band": target_band,
                "typical_years": "2-4 years",
                "advice": f"Focus on moving from {curr_label} to {target_label} responsibilities."
            })
            
        # 4. Horizontal Transition (Always suggest alternatives)
        alternates = self.suggest_alternate_paths(current_role, top_n=5)
        for alt in alternates:
            progression.append({
                "type": "Horizontal (Pivot)",
                "role": alt['title'],
                "target_band": current_band,
                "typical_years": "0-1 year (Transition)",
                "advice": f"Leverage your existing skills in {alt['title']}. Similarity: {alt['similarity']*100:.1f}%"
            })
            
        return progression

    def get_top_up_recommendations(self, current_band, target_band, segment):
        """Suggests specific course types (Top-ups) based on the band leap"""
        top_ups = []
        
        if current_band < 2 and target_band >= 2:
            top_ups.append("Professional Certifications (AWS, PMP, etc.)")
        if target_band >= 3:
            top_ups.append("Postgraduate Studies (MSc, MBA)")
        if segment == "Student" and current_band == 0:
            top_ups.append("Academic Degree (BSc/BEng)")
            
        return top_ups
        # Determine context-specific advice and top companies from dataset
        advice = f"Target {mapped_occ_name} roles in leading Sri Lankan organizations. Focus on professional certifications to advance."
        sector_name = "General"
        source_citation = "ESCO Hierarchy"

        if self.market_advice_df is not None:
            l_label = label.lower()
            for _, row in self.market_advice_df.iterrows():
                keywords = [k.strip().lower() for k in str(row['Keyword']).split(',')]
                if any(k in l_label for k in keywords):
                    sector_name = row['Sector']
                    advice = f"Target {sector_name} roles in {row['Companies']}. {row['Advice']}"
                    source_citation = row['Source']
                    break

        # Official Description from ESCO
        occ_desc_matches = self.esco_occ[self.esco_occ["conceptUri"] == uri]
        role_desc = occ_desc_matches["description"].iloc[0] if not occ_desc_matches.empty else ""

        progression.append({
            "target_role": sl_label,
            "estimated_years": years,
            "additional_info": advice,
            "role_description": role_desc,
            "source": f"ESCO Hierarchy / {source_citation}"
        })

        return progression
    def parse_resume(self, file_path):
        """Unified entry point for all resume types (PDF, JPG, PNG, AVIF)"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == ".pdf":
            return self.parse_resume_pdf(file_path)
        elif ext in [".jpg", ".jpeg", ".png", ".avif", ".webp"]:
            return self.parse_resume_image(file_path)
        else:
            if self.show_progress: print(f"Unsupported file format: {ext}")
            return []

    def parse_resume_image(self, image_path):
        """Extracts text from images using OCR (Tesseract)"""
        if not HAS_OCR:
            if self.show_progress: print("OCR libraries (PIL/pytesseract) not found. Cannot parse image.")
            return []
        
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return self.parse_resume_text(text)
        except Exception as e:
            if self.show_progress: print(f"Error parsing image resume: {e}")
            return []

    def auto_profile(self, resume_path):
        """Suggests a target job based on skills extracted from a resume (PDF or Image)"""
        
        #  Extract skills (routes to PDF or OCR)
        skills = self.parse_resume(resume_path)
        if not skills:
            return {"extracted_skills": [], "suggested_target": "Unknown"}

        #  Convert skills into a "Profile Vector"
        # We join the skills into a single sentence so the model understands the context
        skill_text = "Experienced professional skilled in: " + ", ".join(skills)
        skill_emb = self.model.encode(skill_text, convert_to_tensor=True)
        
        #  Semantic Comparison
        # We compare your profile meaning against the pre-calculated meanings of 
        # every job title in our ESCO dataset (self.esco_occ_embs)
        hits = util.semantic_search(skill_emb, self.esco_occ_embs, top_k=1)[0]
        
        #  Return the Label
        # We get the index of the best match and pull its human-readable name
        best_match_idx = hits[0]["corpus_id"]
        suggested_job = self.esco_occ.iloc[best_match_idx]["preferredLabel"]
        
        return {
            "extracted_skills": skills,
            "suggested_target": suggested_job
        }

    def generate_skill_assessment_questions(self, skill_gap):
        """Generates interest and proficiency questions from the comprehensive assessment dataset"""
        questions = []
        
        #  Load comprehensive questions
        try:
            q_file = self.ml_root / "data" / "raw" / "assessment" / "comprehensive_questions.json"
            if q_file.exists():
                with open(q_file, 'r') as f:
                    comp_qs = json.load(f)
                
                # Add 1 random universal question from each category
                import random
                for section, categories in comp_qs.items():
                    for category, qs in categories.items():
                        if qs:
                            q = random.choice(qs)
                            questions.append({
                                "type": "General",
                                "category": category,
                                "question": q["question"],
                                "options": q["options"]
                            })
        except Exception as e:
            print(f"Error loading assessment questions: {e}")

        #  Dynamic gap-specific questions
        for skill in skill_gap[:5]:
            is_tech = any(x in skill.lower() for x in ["programming", "software", "data", "tool", "system", "engine"])
            if is_tech:
                questions.append({
                    "type": "Technical",
                    "skill": skill,
                    "question": f"How would you rate your hands-on experience with {skill}?",
                    "options": ["None", "Beginner (Basic Syntax)", "Intermediate (Used in projects)", "Advanced (Expert)"]
                })
            else:
                questions.append({
                    "type": "Soft Skill",
                    "skill": skill,
                    "question": f"Are you familiar with the concepts of {skill}?",
                    "options": ["Not at all", "Somewhat familiar", "Very familiar", "Already proficient"]
                })
        return questions

    def parse_resume_text(self, resume_text):
        """Extracts skills from resume text using market index and semantic search"""
        found_skills = []
        text_lower = resume_text.lower()
        
        # Direct Keyword Matching
        for skill in self.market_skills:
            if len(skill) > 3 and f" {skill} " in f" {text_lower} ":
                found_skills.append(skill.title())
        
        # Semantic lookup for top skills mentioned
        # chunk resume text
        chunks = [resume_text[i:i+500] for i in range(0, len(resume_text), 500)]
        if chunks:
            # check first few chunks for job title/skills
            resume_emb = self.model.encode(chunks[0], convert_to_tensor=True)
            pass 

        return list(set(found_skills))[:15]

    def parse_resume_pdf(self, pdf_path):
        """Extracts text from PDF and matches skills"""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return self.parse_resume_text(text)
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return []

    def calculate_skill_score(self, resume_skills, assessment_data, target_skills):
        """Calculates a weighted skill score using adaptive signals"""
        if not target_skills: return 0.0
        
        #  Resume Signal (0.4)
        overlap = set(s.lower() for s in resume_skills) & set(s.lower() for s in target_skills)
        resume_score = len(overlap) / len(target_skills) if target_skills else 0
        
        #  Assessment Signal (0.4)
        assess_score = 0.5 # Default middle-ground
        if assessment_data:
            correct = sum(1 for q in assessment_data if q.get('is_correct'))
            assess_score = correct / len(assessment_data)
            
        #  Task Alignment (0.2)
        task_score = 1.0 # Default
        
        # Adaptive Weighting (Scenario B: No Resume)
        if not resume_skills:
            final_score = (assess_score * 0.75) + (task_score * 0.25)
        else:
            final_score = (resume_score * 0.4) + (assess_score * 0.4) + (task_score * 0.2)
            
        return round(final_score, 2)

    def calculate_readiness_score(self, user_skills, assessment_vector, target_role):
        """Delegated to Phase 10 Analytics."""
        return self.analytics.calculate_readiness_score(user_skills, assessment_vector, target_role, self.jobs_df, self.salary_mapping, self.rule_engine)

    def calculate_transferability_score(self, current_role, target_role):
        """Calculates skill overlap between roles for career switchers"""
        current_skills, _ = self.get_skills_for_job(current_role)
        target_skills, _ = self.get_skills_for_job(target_role)
        
        overlap = set(s.lower() for s in current_skills) & set(s.lower() for s in target_skills)
        missing = set(s.lower() for s in target_skills) - set(s.lower() for s in current_skills)
        
        diff = "Low"
        if len(missing) > 8: diff = "High"
        elif len(missing) > 4: diff = "Medium"
        
        return {
            "transferable_skills_count": len(overlap),
            "missing_core_skills_count": len(missing),
            "difficulty": diff,
            "estimated_time": "6-12 months" if diff == "Medium" else ("12+ months" if diff == "High" else "3-6 months")
        }

    def generate_action_plan(self, gap_skills, target_role="your target role",
                             assessment_vector: Optional[Dict] = None):
        """Delegated to Phase 10 ActionPlanGenerator. Returns the complete action plan dict."""
        res = self.action_plan_gen.generate_action_plan(gap_skills, target_role, assessment_vector)
        return res

    def parse_resume_image(self, image_path):
        """OCR parsing for AVIF/PNG/JPG resumes"""
        try:
            from PIL import Image
            # Check for avif plugin
            try:
                import pillow_avif
            except ImportError:
                print("Warning: pillow-avif-plugin not found. AVIF support may be limited.")
            
            # Simple text extraction attempt (using fitz if it can handle images)
            import fitz
            doc = fitz.open(image_path)
            text = ""
            for page in doc:
                text += page.get_text()
            
            if len(text.strip()) < 50:
                print("Note: Image text is sparse. OCR recommended for real product.")
                # We'd plug in pytesseract here: 
                # text = pytesseract.image_to_string(Image.open(image_path))
                
            return self.parse_resume_text(text)
        except Exception as e:
            print(f"Error parsing image resume: {e}")
            return []

    def _extract_tasks_from_jd(self, jd_text):
        """Filters boilerplate and extracts core verbs/tools"""
        fluff = ["team player", "passionate", "communication", "hardworking", "responsible","caring","attentive"]
        sentences = re.split(r'[.!?\r\n]', jd_text)
        tasks = []
        for s in sentences:
            s_clean = s.lower().strip()
            if len(s_clean) < 10 or any(f in s_clean for f in fluff):
                continue
            if any(skill.lower() in s_clean for skill in self.market_skills):
                tasks.append(s.strip())
        return list(set(tasks))[:5]

    def _estimate_market_average(self, level, category, provider=None):
        """Estimates fees and durations based on Level for Sri Lanka market."""
        # Specific Provider Estimates (Already in Pricing Config)
        if provider and "provider_estimates" in self.pricing_config:
            for key, val in self.pricing_config["provider_estimates"].items():
                if key.lower() in provider.lower():
                    return {"duration": "1-2 years", "fee": f"~{val} (Est)"}

        # Level-based Fallbacks - Sri Lanka Market Averages
        level_map = {
            "Professional": {"duration": "3-6 months", "fee": "~45,000 LKR"},
            "Academic (Diploma)": {"duration": "6-12 months", "fee": "~150,000 LKR"},
            "Academic (Degree)": {"duration": "3-4 years", "fee": "~1,800,000 LKR"},
            "Postgraduate": {"duration": "1-2 years", "fee": "~600,000 LKR"},
            "Certification": {"duration": "2 months", "fee": "Free / Online"}
        }
        
        return level_map.get(level, {"duration": "Contact Provider", "fee": "Contact Provider"})

    # recommend courses

    def _process_one_course(self, course, similarity_score, segment, user_level, location, max_budget, max_duration, skill_gap, assessment_vector=None):
        """Helper to score and format a single course/degree"""
        level = self.classify_course_level(str(course["course_title"]), str(course.get("duration", "N/A")))
        
        #  Phase 10: Hybrid ML Scoring (0.6 SBERT + 0.4 ML) 
        score = similarity_score
        if self.ml_layer and assessment_vector:
            try:
                score = self.ml_layer.score_course_fit(
                    assessment_vector, 
                    level, 
                    float(similarity_score)
                )
            except Exception:
                pass # Fallback to pure similarity/rules

        #  Level-based Scoring
        if segment == "Student":
            if level == "Professional": score *= 0.5
            elif level == "Postgraduate": score *= 0.2
            elif level == "Academic (Degree)": score *= 1.8
            elif level == "Academic (Diploma)": score *= 1.4
        elif segment == "Professional":
            if user_level in ["Mid", "Senior", "Lead", "Manager", "Executive"]:
                if level == "Academic (Degree)": score *= 0.15
                elif level == "Postgraduate": score *= 1.8
                elif level == "Professional": score *= 1.6
            else:
                if level == "Academic (Degree)": score *= 0.8
                elif level == "Professional": score *= 1.8

        # Location Boost
        if location and pd.notna(course.get("location")):
            if str(location).lower() in str(course["location"]).lower():
                score *= 1.3

        #  Fee & Duration Penalties
        # Use numeric if available, else estimate
        current_fee = course.get("fee_numeric", 0) if "fee_numeric" in course else 0
        if current_fee == 0 and "cost" in course and pd.notna(course["cost"]):
            nums = re.findall(r'\d+', str(course["cost"]).replace(',', ''))
            if nums: current_fee = int(nums[0])
            
        if max_budget and isinstance(max_budget, (int, float)) and current_fee > max_budget:
            score *= 0.1
        
        current_duration = course.get("duration_numeric", 0) if "duration_numeric" in course else 0
        
        # Handle max_duration as either number or semantic string
        if max_duration:
            if isinstance(max_duration, (int, float)):
                if current_duration > max_duration:
                    score *= 0.1
            elif isinstance(max_duration, str):
                # Semantic boosting for "Full-time" vs "Part-time"
                course_text = str(course.get("course_title", "")).lower() + " " + str(course.get("duration", "")).lower()
                if max_duration.lower() in course_text:
                    score *= 1.2

        #  Fill in missing presentation data
        category = course.get("cat", course.get("category", "General"))
        market_data = self._estimate_market_average(level, str(category), course.get("provider", ""))
        
        raw_dur = course.get("duration")
        duration = str(raw_dur) if pd.notna(raw_dur) and str(raw_dur).lower() != "nan" else market_data["duration"]
        
        raw_cost = course.get("cost")
        fee = str(raw_cost) if pd.notna(raw_cost) and str(raw_cost).lower() != "nan" else f"{int(current_fee):,} LKR" if current_fee > 0 else market_data["fee"]

        #  Rationale (Why Recommended)
        why = []
        
        # 1. Level fit
        if segment == "Student" and "Academic" in level:
            why.append("Strong academic foundation for entry-level")
        elif segment == "Professional" and level == "Professional":
            why.append("Fast-track upskilling for professionals")
        
        # 2. Skill coverage
        matches = 0
        for skill in skill_gap:
            if matches >= 2: break
            # Check title and (optionally) description if available
            search_space = str(course["course_title"]).lower()
            if "description" in course and pd.notna(course["description"]):
                search_space += " " + str(course["description"]).lower()
                
            if skill.lower() in search_space:
                why.append(f"Bridges gap in {skill}")
                matches += 1
                
        # 3. Location/Provider
        if location and location.lower() in str(course.get("location", "")).lower():
            why.append(f"Conveniently located in {location}")
        elif pd.notna(course.get("provider")) and similarity_score > 0.8:
            why.append(f"High relevance from {course['provider']}")

        # Final fallback if empty
        if not why:
            why.append("High semantic match to your career goals")

        return {
            "course_name": course["course_title"],
            "provider": course.get("provider", "Unknown Institution"),
            "level": level,
            "type": course.get("type", "Unknown"),
            "duration": duration,
            "fee": fee,
            "fee_numeric": current_fee,
            "location": course.get("location", "Online/Distance"),
            "relevance_score": round(score, 3),
            "url": course.get("course_url", "#"),
            "why_recommended": why[:3]
        }

    def recommend_courses(
        self,
        user_skills,
        target_job,
        user_level="Entry",
        segment="Student",
        preference=None,
        location=None,
        max_budget=None,
        max_duration=None,
        top_n=8,
        assessment_vector=None
    ):
        # get skills and wanted role
        all_required, mapped_occ = self.get_skills_for_job(target_job)
        
        # find which are essential vs optional
        occ_uri = self.esco_occ[self.esco_occ["preferredLabel"] == mapped_occ].iloc[0]["conceptUri"]
        essential_uris = self.occ_skill_rel[
            (self.occ_skill_rel["occupationUri"] == occ_uri) & 
            (self.occ_skill_rel["relationType"] == "essential")
        ]["skillUri"].tolist()
        
        essential_skills = set(self.esco_skills[self.esco_skills["conceptUri"].isin(essential_uris)]["preferredLabel"].str.lower().tolist())

        user_skill_set = set(s.lower() for s in user_skills)
        
        # split gaps into compulsory vs optional
        compulsory_gap = [s for s in all_required if s.lower() in essential_skills and s.lower() not in user_skill_set]
        optional_gap = [s for s in all_required if s.lower() not in essential_skills and s.lower() not in user_skill_set]
        
        skill_gap = compulsory_gap + optional_gap

        # 2. Calculate Signals (Bands & Multi-Signal Score)
        band = self.estimate_responsibility_band(user_skills)
        current_score_val = self.calculate_skill_score(user_skills, None, all_required)
        
        # 3. Handle Complete Match (Transition to Action Plan later, no early return)
        is_complete = not skill_gap

        #  Build Query for Courses
        # Cleaner Query: Filter out verbose ESCO skill names (often full sentences)
        # This prevents the "cluttering" of the query
        query_skills = []
        #  ESCO Mapping & Gap Analysis
        compulsory_skills = compulsory_gap
        optional_skills = optional_gap

        # Career Banding
        band = self.estimate_responsibility_band(user_skills)
        print(f"DEBUG: Career band = {band}")

        #  Semantic Query Construction
        query_skills = []
        for s in compulsory_gap[:4]:
            if len(s) > 40: query_skills.extend(s.split()[:3])
            else: query_skills.append(s)
        
        query_terms = query_skills + optional_gap[:2]
        
        # FIX: Auto-prioritize Time Commitment based on segment
        status_level = assessment_vector.get("status_level", 0) if assessment_vector else 0
        if status_level <= 1: # Students/School Leavers
            max_duration = max_duration or "Full-time"
        else: # Working Professionals
            query_terms += ["part-time", "online", "evening"]

        #  Career-Stage Keyword Boosting
        user_edu = str(assessment_vector.get("highest_education", "")).lower() if assessment_vector else ""
        has_bsc = "bachelor" in user_edu or "degree" in user_edu or "bsc" in user_edu
        
        # ── Rule Engine: Stage-Based Level Mapping Strategy ──
        target_domain = assessment_vector.get("domain", self._infer_domain(target_job))
        exp_years = float(assessment_vector.get("experience_years", 0))
        status_level = assessment_vector.get("status_level", 0)
        
        # Determine strategy levels
        strategy_levels = []
        if segment == "Student": strategy_levels = ["Bachelor", "Diploma"]
        elif status_level == 3: # Switcher
            strategy_levels = ["Diploma", "Professional", "Bachelor"]
        elif exp_years >= 6: # Experienced
            strategy_levels = ["Postgraduate", "Professional", "Diploma"]
        elif status_level == 4: # Executive
            strategy_levels = ["Postgraduate", "Professional"]
        else:
            strategy_levels = ["Diploma", "Professional"]

        if preference and preference != "None":
            query_terms.append(preference)
                
        query = " ".join(query_terms)
        print(f"DEBUG: Query = {query}")
        
        query_emb = self.model.encode(query, convert_to_tensor=True)
        print(f"DEBUG: query_emb type = {type(query_emb)}")

        #  SEMANTIC SEARCH - Combined Dataset Approach
        # We want a mix of Vocational (Professional) and Academic (Degrees)
        all_candidate_recommendations = []
        
        # 1. Inject High-Confidence Production Programs (Auth-Rule)
        for p in self.production_academic_programs:
            if p['domain'] == target_domain and p['level'] in strategy_levels:
                # Simple injection: Treat as highly relevant match
                # Budget check: If budget is restricted, skip if likely expensive (e.g., Masters)
                if max_budget and max_budget < 200000 and p['level'] in ["Bachelor", "Postgraduate"]:
                    continue
                
                # Numeric mapping for filtering safety
                fee_val = 50000
                if p['level'] == "Bachelor": fee_val = 800000
                elif p['level'] == "Postgraduate": fee_val = 600000
                elif p['level'] == "Diploma": fee_val = 150000
                
                dur_val = 0.5
                if "3-4" in p['duration']: dur_val = 3.5
                elif "1-2" in p['duration']: dur_val = 1.5
                
                all_candidate_recommendations.append({
                    "course_name": p["course_name"],
                    "provider": p["provider"],
                    "level": f"{p['level']} (High-Confidence Path)",
                    "type": "Academic" if p['level'] != "Professional" else "Certification",
                    "duration": p["duration"],
                    "duration_numeric": dur_val,
                    "fee": "Varies",
                    "fee_numeric": fee_val,
                    "location": "Sri Lanka / Online",
                    "relevance_score": 0.95, # Rule engine priority
                    "url": p.get("url", "#"),
                    "why_recommended": [f"Authoritative path for {target_domain}", f"Bridges: {', '.join(p['focus'][:2])}", p["notes"]],
                    "source_file": "production_rule"
                })

        # 2. Search Professional Courses
        hits = util.semantic_search(query_emb, self.course_embs, top_k=top_n * 5)[0]
        for h in hits:
            course = self.courses_df.iloc[h["corpus_id"]]
            processed = self._process_one_course(course, h["score"], segment, user_level, location, max_budget, max_duration, skill_gap, assessment_vector)
            all_candidate_recommendations.append(processed)

        # . Search Academic Courses
        if self.academic_embs is not None:
            acad_hits = util.semantic_search(query_emb, self.academic_embs, top_k=top_n * 5)[0]
            for h in acad_hits:
                course = self.academic_df.iloc[h["corpus_id"]]
                processed = self._process_one_course(course, h["score"], segment, user_level, location, max_budget, max_duration, skill_gap, assessment_vector)
                all_candidate_recommendations.append(processed)

        # ─Rule Engine: Domain & Education Invariants ──
        user_domain = assessment_vector.get("domain", self._infer_domain(target_job))
        user_edu_lvl = assessment_vector.get("education_level", 1)
        
        filtered_candidates = []
        for r in all_candidate_recommendations:
            r_name = str(r.get("course_name", "")).lower()
            r_lvl_str = str(r.get("level", "Entry")).lower()
            
            # invariant 1: Domain Isolation
            r_domain = self._infer_domain(r_name)
            if user_domain != "General" and r_domain != "General" and r_domain != user_domain:
                continue
                
            # Invariant 2: Qualification Floor
            # Map course semantic level to numeric
            r_edu_val = 1
            if "diploma" in r_lvl_str: r_edu_val = 3
            elif "degree" in r_lvl_str or "bachelor" in r_lvl_str or "bsc" in r_lvl_str: r_edu_val = 4
            elif "master" in r_lvl_str or "postgraduate" in r_lvl_str or "msc" in r_lvl_str: r_edu_val = 5
            
            # Do not recommend lower qualification than current
            # Exception: Professional certifications/short courses are always allowed
            is_professional = "professional" in r_lvl_str or "certification" in r_lvl_str or r.get("source_file") == "professional"
            if not is_professional and r_edu_val < user_edu_lvl:
                continue
                
            filtered_candidates.append(r)
            
        all_candidate_recommendations = sorted(filtered_candidates, key=lambda x: x['relevance_score'], reverse=True)
        
        final_picks = []
        seen_names = set()
        
        # Priority logic - Students get academic focus, Professionals get professional focus
        if segment == "Student":
            # Add academic first
            for r in all_candidate_recommendations:
                is_acad = r.get("source_file") == "academic" or "Academic" in str(r.get("level", ""))
                if is_acad and r["course_name"] not in seen_names:
                    final_picks.append(r)
                    seen_names.add(r["course_name"])
                    if len(final_picks) >= 3: break 
        
        # Fill remaining slots (up to top_n)
        for r in all_candidate_recommendations:
            if r["course_name"] not in seen_names:
                final_picks.append(r)
                seen_names.add(r["course_name"])
                if len(final_picks) >= top_n: break

        # ── Gold Logic: Explicit Category Separation ──
        # 1. Academic recommendations - institutional degrees/diplomas
        academic_recommendations = [
            r for r in all_candidate_recommendations 
            if r.get("source_file") == "academic" or any(kw in str(r.get("level", "")).lower() for kw in ["degree", "diploma", "bachelor", "master", "postgraduate", "academic"])
        ]
        
        # 2. Skill-Gap Courses - online learning aggregators (Coursera, Udemy, etc.)
        skill_gap_courses = [
            r for r in all_candidate_recommendations
            if any(agg in str(r.get("url", "")).lower() for agg in ["class-central", "coursera", "udemy", "datacamp", "edx", "linkedin", "google", "pickacourse"])
            or any(agg in str(r.get("provider", "")).lower() for agg in ["class central", "coursera", "udemy", "datacamp", "edx", "linkedin", "google", "pickacourse"])
            or "professional" in str(r.get("level", "")).lower()
        ]

        # ── MSc / Diploma Rules ──
        pref = assessment_vector.get("education_preference", "").lower() if assessment_vector else ""
        user_edu = assessment_vector.get("education_level", 1) if assessment_vector else 1
        
        if "msc" in pref or "master" in pref:
            # Prioritize Master/Postgraduate in academic pool
            academic_recommendations = sorted(academic_recommendations, 
                                             key=lambda x: 1 if "master" in str(x.get("level","")).lower() or "postgraduate" in str(x.get("level","")).lower() else 0,
                                             reverse=True)
        elif "diploma" in pref:
             academic_recommendations = sorted(academic_recommendations, 
                                             key=lambda x: 1 if "diploma" in str(x.get("level","")).lower() else 0,
                                             reverse=True)

        # Fill Academic if sparse
        if len(academic_recommendations) < 5:
            for r in all_candidate_recommendations:
                if r["course_name"] not in [a["course_name"] for a in academic_recommendations] and r not in skill_gap_courses:
                    academic_recommendations.append(r)
                if len(academic_recommendations) >= 8: break
        
        # Fill Skill-Gap if sparse
        if len(skill_gap_courses) < 5:
            for r in all_candidate_recommendations:
                if r["course_name"] not in [s["course_name"] for s in skill_gap_courses] and r not in academic_recommendations:
                    skill_gap_courses.append(r)
                if len(skill_gap_courses) >= 12: break

        academic_recommendations = academic_recommendations[:8]
        skill_gap_courses = skill_gap_courses[:12] # Richer skill-gap list
        recommendations = skill_gap_courses[:top_n]

        # Ensure all courses have apply_url
        for c_list in [recommendations, academic_recommendations, skill_gap_courses]:
            for c in c_list:
                c["apply_url"] = c.get("url", "#")

        #  JOB FETCHING
        job_list = []
        try:
            job_hits = util.semantic_search(query_emb, self.job_embs, top_k=5)[0]
            for h in job_hits:
                j = self.jobs_df.iloc[h["corpus_id"]]
                j_raw_skills = str(j.get("extracted_skills", "")).lower()
                user_skills_lower = [s.lower() for s in user_skills]
                
                # Check user overlap with the specific job's requirements
                if j_raw_skills and j_raw_skills != "nan":
                    # Simple heuristic: clean and split the string list from pandas
                    job_skills_list = [s.strip().strip("'") for s in j_raw_skills.strip("[]").split(',')]
                    user_overlap = [s for s in job_skills_list if s and any(s in u or u in s for u in user_skills_lower)]
                    fit_pct = round(100 * (len(user_overlap) / max(1, len(job_skills_list))), 1)
                    missing_skills = [s for s in job_skills_list if s and s not in user_overlap][:4]
                else:
                    # Fallback to ESCO mapping match
                    fallback_skills = list(all_required) if 'all_required' in locals() else compulsory_gap + optional_gap
                    user_matches = [s for s in fallback_skills if s.lower() in user_skills_lower]
                    fit_pct = round(100 * (len(user_matches) / max(1, len(fallback_skills))), 1)
                    missing_skills = [s for s in fallback_skills if s and s not in user_matches][:4]
                
                gap_pct = max(0, 100 - fit_pct)
                
                j_url = j.get("url")
                if pd.isna(j_url): j_url = "#"
                
                job_list.append({
                    "job_title": j["title"],
                    "company": j.get("company", "Lankan Employer"),
                    "deadline": j.get("deadline", "Apply Soon"),
                    "url": j_url,
                    "apply_url": j_url,
                    "skill_gap_pct": gap_pct,
                    "missing_skills": missing_skills,
                    "relevance_score": round(h["score"], 3),
                    "estimated_salary": self.get_salary_for_role(j["title"], user_level)
                })
            
            if not job_list:
                job_list.append({
                    "job_title": "No specific openings found",
                    "company": "Market Research Advised",
                    "message": "We couldn't find active jobs for this specific search. Try broadening your location or role."
                })
        except Exception as e:
            print(f"INFO: Job fetching skipped: {e}")
            job_list.append({"job_title": "Job Service Busy", "message": str(e)})

        #  ADVICE BOX
        advice = []
        all_res = recommendations + academic_recommendations
        valid_fees = [r['fee_numeric'] for r in all_res if r['fee_numeric'] > 0]
        if max_budget and valid_fees and min(valid_fees) > max_budget:
            advice.append("Note: Most programs exceed your budget. Target State Universities or OUSL.")
        if location and all_res and not any(location.lower() in str(r['location']).lower() for r in all_res):
             advice.append(f"No direct matches in {location.title()}, showing Online options.")

        # Suppress jobs for O/L students — too early to apply
        current_status = 1
        if assessment_vector:
            current_status = assessment_vector.get("status_level", 1)
            
        if current_status == 0:
            job_list = [{
                "job_title": "Not applicable at this stage",
                "company": "PathFinder+ Guidance",
                "message": "You're at the learning and exploration stage. Focus on courses and building skills first. Job listings will appear once you've completed a Diploma or A/L qualification."
            }]

        # ── V3 Dashboard Alignment (11-Point Bundle) ──
        all_progression = self.get_career_progression(target_job, band, user_skills, assessment_vector)
        vertical_roadmap = [p for p in all_progression if "Vertical" in p.get("type", "")]
        horizontal_roadmap = [p for p in all_progression if "Horizontal" in p.get("type", "")]
        
        readiness = self.calculate_readiness_score(user_skills, assessment_vector or {"status_level": 1 if segment=="Student" else 2, "experience_years": 0}, target_job)
        
        # Skill Intelligence (Point 3)
        current_skills = user_skills[:10]
        skills_to_strengthen = compulsory_gap[:8]
        
        # Skill Gap Insights (Point 4)
        skill_gap_insights = {
            "critical_skills": compulsory_gap[:5] if compulsory_gap else ["None - strong alignment detected"],
            "beneficial_skills": optional_gap[:5] if optional_gap else ["None at this stage"],
            "status": "Green" if not compulsory_gap else "Yellow" if len(compulsory_gap) < 5 else "Red"
        }

        # 10. Personalized Action Plan
        action_roadmap = self.generate_action_plan(gap_skills=compulsory_gap, target_role=target_job, assessment_vector=assessment_vector)
        
        # AI Explainability (Point 11)
        demand_pct = readiness.get("demand_score", 0)
        explainability = [
            f"• {demand_pct}% market demand for {target_job} roles in Sri Lanka",
            "• Education match detected based on institutional alignment",
            "• Skill alignment detected via advanced ESCO semantic mapping",
            "• Personalized roadmap generated using V2 Transition Formula"
        ]

        snapshot_domain = assessment_vector.get("domain", self._infer_domain(target_job)) if assessment_vector else self._infer_domain(target_job)

        return {
            # 1. Career Snapshot (CRI)
            "career_snapshot": {
                "target_role": target_job,
                "score": readiness.get("overall", 0),
                "stage": readiness.get("stage", "Development Phase"),
                "estimated_transition_weeks": action_roadmap.get("estimated_weeks", 0),
                "preferred_industry": snapshot_domain,
                "sub_metrics": {
                    "Skills Alignment": readiness.get("skills_match", 0),
                    "Experience Level": readiness.get("experience", 0),
                    "Demand Score": readiness.get("demand_score", 0),
                    "Qualification": readiness.get("qualification", 0),
                    "Gap Coverage": readiness.get("gap_coverage", 0)
                }
            },
            # 2. AI Career Path Recommendation
            "career_path_recommendation": {
                "current_role": target_job,
                "vertical": vertical_roadmap,
                "horizontal": horizontal_roadmap
            },
            # 3. Skill Intelligence
            "skill_intelligence": {
                "current_skills": current_skills,
                "strengthen": skills_to_strengthen,
                "soft_skills": assessment_vector.get("normalized_soft_skills", {}) if assessment_vector else {}
            },
            # 4. Skill Gap Insights
            "skill_gap_insights": skill_gap_insights,
            # 5. Recommended Education
            "recommended_education": academic_recommendations[:5],
            "skill_gap_courses": skill_gap_courses[:5],
            # 6. Real Job Opportunities 
            "job_opportunities": job_list[:5],
            # 7. Salary Intelligence
            "salary_intelligence": self.get_salary_for_role(target_job),
            # 8. Market Demand Insights
            "market_demand": self.get_personalized_market_trends(target_job, domain=snapshot_domain),
            # 9. Mentor Recommendations
            "mentor_recommendations": self.match_mentors(user_skills, target_job=target_job, top_n=3),
            # 10. Personalized Action Plan
            "action_roadmap": action_roadmap,
            # 11. AI Explainability
            "ai_explainability": explainability,

            
            # Legacy compatibility / Extra data
            "status": "Incomplete" if skill_gap else "Complete",
            "mapped_occupation": mapped_occ,
            "skill_gap": compulsory_gap,
            "recommendations": skill_gap_courses[:top_n],
            "caveats": advice,
            "ml_diagnostics": self._get_ml_diagnostics(assessment_vector, compulsory_gap)
        }

    def _get_ml_diagnostics(self, assessment_vector, gap_skills):
        """
        Returns a diagnostics dict for the ML layer, shown in report section M.
        If ML layer is not available, returns a note about SBERT-only mode.
        """
        if not assessment_vector:
            return {"mode": "SBERT-only (no assessment vector)"}

        if self.ml_layer is None or not self.ml_layer.is_trained:
            return {
                "mode":    "SBERT-only",
                "note":    "Run scripts/train_ml_models.py to enable hybrid scoring"
            }

        seg = self.ml_layer.predict_segment(assessment_vector)
        similar = self.ml_layer.find_similar_profiles(assessment_vector, top_n=2)
        acc = self.ml_layer.training_accuracy

        return {
            "mode":             "Hybrid (SBERT + RF + GBM + KNN)",
            "predicted_segment": seg["segment"],
            "confidence":        f"{seg['confidence']:.1%}",
            "all_segment_probs": seg.get("all_probs", {}),
            "similar_profiles":  similar,
            "model_accuracies": {
                "RandomForest (career segment)": f"{acc.get('segment_rf', 0):.1%}",
                "GradientBoosting (course fit)": f"{acc.get('fit_gbm', 0):.1%}",
                "KNN (profile similarity)":      f"{acc.get('profile_knn', 0):.1%}"
            },
            "hybrid_formula":   "hybrid_score = 0.60 × SBERT + 0.40 × GBM_fit",
            "gap_skills_count":  len(gap_skills)
        }

    def suggest_alternate_paths(self, job_title, top_n=5):
        """Simplified version using esco similarity, returns detailed dictionaries"""
        job_emb = self.model.encode(job_title, convert_to_tensor=True)
        hits = util.semantic_search(job_emb, self.esco_occ_embs, top_k=top_n+1)[0]
        
        paths = []
        for h in hits:
            alt_job = self.esco_occ.iloc[h["corpus_id"]]["preferredLabel"]
            # Skip the target job itself if it's the top match
            if str(alt_job).lower() == str(job_title).lower():
                continue
            paths.append({
                "title": alt_job,
                "similarity": round(float(h["score"]), 3)
            })
            if len(paths) >= top_n:
                break
        return paths

    def match_mentors(self, user_skills, target_job, top_n=3, assessment_vector=None):
        """Delegated to Phase 10 Recommender."""
        if not self.mentors_data: return []
        return self.recommender.match_mentors_full(user_skills, target_job, self.mentors_data, top_n, assessment_vector)

    def validate_output(self, recommendations: Dict[str, Any], assessment_vector: Dict[str, Any]) -> Dict[str, Any]:
        """Delegated to Phase 10 RuleEngine."""
        return self.rule_engine.validate_output_full(recommendations, assessment_vector)

    def get_personalized_market_trends(self, target_role, domain=None):
        """Detects user field and fetches relevant market trends using Rule Engine."""
        field = domain or self._infer_domain(target_role)
        if field == "General": field = "IT" # Fallback for trends
        
        # Check cache
        if field in self._trend_cache:
            return self._trend_cache[field]
        
        # Lazy re-init: if trend_analyzer is None or was built on empty data, rebuild now
        if self.trend_analyzer is None or (hasattr(self.trend_analyzer, 'jobs_df') and self.trend_analyzer.jobs_df.empty and not self.jobs_df.empty):
            try:
                self.trend_analyzer = MarketTrendAnalyzer(self.jobs_df)
            except Exception as e:
                if self.show_progress: print(f"Warning: Trend Analyzer re-init failed: {e}")
                return {"field": field, "segments": [], "top_demanded_skills": {}, "recommendation": "Market data not available right now."}
            
        try:
            trends, field_df = self.trend_analyzer.get_trends_by_field(field)
            hot_skills = self.trend_analyzer.get_hot_skills(5, df=field_df)
            
            result = {
                "field": field,
                "segments": trends,
                "top_demanded_skills": hot_skills,
                "recommendation": f"Focus on {', '.join(list(hot_skills.keys())[:3])} to stay competitive in {field}."
            }
            self._trend_cache[field] = result
            return result
        except Exception as e:
            return {"error": f"Could not load trends: {str(e)}", "field": field}



    def get_minimal_context(self, user_query: str, top_n: int = 3) -> str:
        """
        Generates minimal context responses for free gemini api for user
        resposnes for the chatbot.
        """
        # Fetch data
        jobs = self.recommend_jobs([], user_query, top_n=top_n)
        courses = self.recommend_courses(
            user_skills=[], 
            target_job=user_query, 
            top_n=top_n
        )
        
        # Compress into a string
        # Labels: J=Job, C=Course, P=Provider
        ctx = f"Results for: {user_query}\n"
        
        if jobs:
            ctx += "JOBS:\n"
            for j in jobs[:top_n]:
                ctx += f"- {j['job_title']} @ {j['company']}\n"
        
        rec_list = courses.get("recommendations", [])
        if rec_list:
            ctx += "COURSES:\n"
            for c in rec_list[:top_n]:
                ctx += f"- {c['course_name']} ({c['provider']})\n"
                
        return ctx.strip()



if __name__ == "__main__":
    current_dir = Path(__file__).parent
    engine = RecommendationEngine(
        jobs_path=current_dir / "../data/processed/all_jobs_master.csv",
        courses_path=current_dir / "../data/processed/all_courses_master.csv",
        esco_dir=current_dir / "../data/raw/esco",
        force_refresh=False
    )

