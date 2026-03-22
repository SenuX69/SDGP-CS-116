<<<<<<< HEAD
# PathFinder+ — Machine Learning & Data Cleaning Module

This directory contains the complete **Data Science Component** of the PathFinder+ career guidance system. It is responsible for data collection, cleaning, embedding generation, and producing real-time, personalized career recommendations.

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Folder Structure](#folder-structure)
3. [Core Component: Recommendation Engine](#core-component-recommendation-engine)
4. [ML Models & Embeddings](#ml-models--embeddings)
5. [Data Pipeline](#data-pipeline)
6. [Scripts Reference](#scripts-reference)
7. [Tests & Verification](#tests--verification)
8. [How to Run](#how-to-run)
9. [Cloud (MongoDB Atlas) Integration](#cloud-mongodb-atlas-integration)
10. [Key Design Decisions](#key-design-decisions)

---

## Architecture Overview

```
User Input (Skills, Target Job, Level)
            │
            ▼
┌─────────────────────────────────────────────┐
│         RecommendationEngine (core/)         │
│                                             │
│  SBERT ──► Semantic Vector Matching         │
│  ESCO  ──► Occupation Taxonomy Mapping      │
│  PayLab──► Salary Benchmarking              │
│                                             │
│  Outputs:                                   │
│  ├── Courses (ranked by relevance & ROI)    │
│  ├── Jobs (ESCO-mapped with salary)         │
│  ├── Mentors (professional matching)        │
│  ├── Skill Gap Assessment Questions         │
│  ├── Career Readiness Index (0-100)         │
│  └── 12-Month Action Plan                  │
└─────────────────────────────────────────────┘
            │
            ▼
     MongoDB Atlas (Cloud)
```

---

## Folder Structure

```
Machine Learning and Data Cleaning/
│
├── core/                          # Engine logic
│   └── recommendation_engine.py  # Main recommendation engine (~2,000 lines)
│
├── models/                        # Pre-computed ML embeddings (.pt files)
│   ├── job_embeddings.pt
│   ├── esco_occ_embeddings.pt
│   ├── course_embeddings_all_courses_master.pt
│   ├── course_embeddings_cloud_courses.pt
│   ├── course_embeddings_academic_courses_master.pt
│   └── academic_embeddings.pt
│
├── data/
│   ├── raw/                       # Scraped raw data from job/course sites
│   │   ├── scrapers/              # Individual scraper scripts (Ikman, LinkedIn etc.)
│   │   ├── esco/                  # ESCO taxonomy CSVs (occupations, skills, relations)
│   │   └── assessment/            # Assessment question bank JSON files
│   ├── processed/                 # Cleaned, merged master CSV files
│   │   ├── all_jobs_master.csv
│   │   ├── all_courses_master.csv
│   │   ├── academic_courses_master.csv
│   │   ├── career_progressions.csv
│   │   ├── mentors.json
│   │   └── synthetic_jobs.csv
│   └── config/                    # Pricing estimates, salary mappings
│       ├── paylab_salary_mapping.csv
│       └── pricing_estimates.json
│
├── scripts/                       # Data operations and automation
│   ├── orchestrate_scraping.py    # Master pipeline runner
│   ├── push_to_mongo.py           # Cloud database sync (CRUD)
│   ├── clean_and_refine_jobs.py   # Job data normalization
│   ├── refine_course_data.py      # Course data normalization
│   ├── merge_all_jobs.py          # Merges scraped jobs into master CSV
│   ├── consolidate_courses.py     # Merges course sources
│   ├── market_trend_analyzer.py   # Field-specific market trend analysis
│   ├── generate_model_artifacts.py# Rebuilds .pt embedding files
│   ├── generate_more_mentors.py   # Synthetic mentor data generation
│   ├── synthetic_market_generator.py # Augments job listings
│   ├── check_cloud_data.py        # Cloud data health check
│   └── spam_detector.py           # Filters low-quality job listings
│
├── tests/                         # Verification and simulation scripts
│   ├── interactive_playground.py  # Manual prompt-and-try testing tool
│   ├── professional_interactive_demo.py # Pre-scripted multi-persona demo
│   ├── final_system_verification.py     # 5-persona automated test suite
│   ├── final_user_simulation_test.py    # Detailed simulation with logs
│   └── multi_industry_test.py     # Business, Healthcare, IT persona tests
│
├── notebooks/                     # Jupyter notebooks for exploration
├── .env                           # MongoDB URI (not committed to Git)
└── requirements.txt               # All Python dependencies
```

---

## Core Component: Recommendation Engine

**File**: `core/recommendation_engine.py`

This is the central brain of the system. It is a ~2,000-line class that handles the entire recommendation lifecycle.

### Key Methods

| Method | Description |
|---|---|
| `from_mongo()` | Loads all data directly from MongoDB Atlas (production mode) |
| `get_recommendations_from_assessment(assessment_vector, target_job)` | Main entry point — generates the full dashboard bundle |
| `recommend_courses(...)` | Ranks courses via SBERT similarity + ROI scoring |
| `match_jobs(...)` | Finds ESCO-mapped jobs with salary from PayLab data |
| `match_mentors(...)` | Finds professional mentors by industry and seniority |
| `generate_skill_assessment_questions(skill_gap)` | Produces dynamic assessment questions from the skill gap |
| `calculate_readiness_index(...)` | Computes a 0-100 Career Readiness Score |
| `generate_action_plan(...)` | Produces a monthly 12-step career roadmap |
| `get_personalized_market_trends(...)` | Returns field-specific salary and trend insights |

### Recommendation Output Bundle (Dashboard Format)

```python
{
  "mapped_occupation": "...",           # ESCO-matched job title
  "compulsory_skills": [...],           # Required skill gaps
  "optional_skills": [...],             # Nice-to-have skills
  "assessment_questions": [...],        # Personalized quiz questions
  "recommendations": [                  # Ranked courses
    {
      "course_name": "...",
      "provider": "...",
      "fee": "...",
      "relevance_score": 0.92,
      "url": "...",
      "why_recommended": [...]
    }
  ],
  "job_ideas": [...],                   # Relevant job listings
  "mentors": [...],                     # Professional mentors
  "readiness_score": {
    "overall": 65,
    "stage": "Mid-level Readiness",
    "breakdown": {...}
  },
  "salary_estimate": "150,000 - 250,000 LKR",
  "market_trends": {...},
  "action_plan": [...]                  # 12-month milestone roadmap
}
```

---

## ML Models & Embeddings

All `.pt` files in `models/` are **pre-computed PyTorch tensors** generated from the `all-MiniLM-L6-v2` Sentence-BERT model. They store dense vector representations of jobs, courses, and ESCO occupations, enabling fast cosine similarity matching at runtime without re-encoding the entire dataset on every API call.

| File | Contents | Size |
|---|---|---|
| `job_embeddings.pt` | Vectors for all scraped job listings | ~3.1 MB |
| `esco_occ_embeddings.pt` | Vectors for all ESCO occupation titles | ~4.5 MB |
| `course_embeddings_all_courses_master.pt` | Vectors for all skill-gap courses | ~5.6 MB |
| `course_embeddings_academic_courses_master.pt` | Vectors for university degree programmes | ~2.2 MB |
| `course_embeddings_cloud_courses.pt` | Cloud-synced course vectors | ~5.6 MB |
| `academic_embeddings.pt` | Dedicated academic institution embeddings | ~112 KB |

> **Important for Backend Developers**: These `.pt` files **must be included** in your deployment package. Without them, the engine will attempt to rebuild them on startup, which takes ~5-10 minutes and requires all CSV data to be locally available. With them, startup is near-instant.

To rebuild them manually, run:
```bash
python scripts/generate_model_artifacts.py
```

---

## Data Pipeline

The full data lifecycle from scraping to recommendation works as follows:

```
1. SCRAPE       scrapers/ scripts (Ikman, GeneralExpress, LinkedIn, etc.)
      │
      ▼
2. MERGE        scripts/merge_all_jobs.py / consolidate_courses.py
      │          → Output: data/processed/all_jobs_master.csv
      │
      ▼
3. CLEAN        scripts/clean_and_refine_jobs.py / refine_course_data.py
      │          → Normalizes titles, removes spam, maps ESCO categories
      │
      ▼
4. EMBED        scripts/generate_model_artifacts.py
      │          → Produces .pt vector files in models/
      │
      ▼
5. SYNC         scripts/push_to_mongo.py
                 → Uploads all processed data to MongoDB Atlas
```

**To run the entire pipeline in one command:**
```bash
python scripts/orchestrate_scraping.py
```

---

## Scripts Reference

| Script | Purpose |
|---|---|
| `orchestrate_scraping.py` | Runs the full pipeline end-to-end |
| `push_to_mongo.py` | CRUD operations: Creates, Updates, and Deletes records in MongoDB Atlas |
| `clean_and_refine_jobs.py` | Normalizes job titles, maps ESCO codes, removes duplicates |
| `refine_course_data.py` | Standardizes fee formats, duration, and provider names |
| `market_trend_analyzer.py` | Generates salary/growth trend data per industry field |
| `generate_model_artifacts.py` | Rebuilds all `.pt` embedding files from CSVs |
| `generate_more_mentors.py` | Augments mentor pool with synthetic professional profiles |
| `spam_detector.py` | Identifies and removes low-quality or irrelevant job posts |
| `check_cloud_data.py` | Verifies integrity of all MongoDB Atlas collections |

---

## Tests & Verification

| Script | What it Tests |
|---|---|
| `interactive_playground.py` | **Manual testing tool** — input any career scenario and get results live |
| `professional_interactive_demo.py` | Runs 3 pre-scripted personas (O/L Student, A/L Student, Career Switcher) |
| `final_system_verification.py` | Automated 5-persona suite (IT, Business, Healthcare, Student, Pro) |
| `multi_industry_test.py` | Stress-tests recommendations across non-IT industries |
| `final_user_simulation_test.py` | Produces detailed, human-readable logs for each persona |

---

## How to Run

### 1. Setup Environment
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows

# Install all dependencies
pip install -r requirements.txt
```

### 2. Configure MongoDB Connection
Create a `.env` file in this directory with:
```
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
DATABASE_NAME=pathfinder_plus
```

### 3. Run Interactive Demo (Quickest way to verify the system)
```bash
python tests/interactive_playground.py
```

### 4. Run Full Verification Suite
```bash
python tests/final_system_verification.py
```

### 5. Use the Engine in Your Code (Backend Integration)
```python
from core.recommendation_engine import RecommendationEngine

# Initialize from cloud (production mode)
engine = RecommendationEngine(from_mongo=True)

# Get a full career recommendation dashboard
bundle = engine.get_recommendations_from_assessment(
    assessment_vector={
        "status_level": 2,          # 0=O/L, 1=A/L, 2=Undergraduate, 3=Professional
        "experience_years": 2,
        "extracted_intent_skills": ["Python", "SQL"],
    },
    target_job="Data Scientist"
)
```

---

## Cloud (MongoDB Atlas) Integration

All production data is stored in the `pathfinder_plus` database on MongoDB Atlas. The following collections are managed by this module:

| Collection | Contents |
|---|---|
| `jobs` | Scraped and cleaned job listings |
| `jobs_synthetic` | AI-augmented job listings for rare roles |
| `courses` | Professional skill-gap courses |
| `courses_academic` | University degree programmes |
| `mentors` | Professional mentor profiles |
| `career_paths` | Role-to-role progression mappings |
| `salary_data` | PayLab industry salary benchmarks |
| `esco_occupations` | ESCO occupation taxonomy |
| `esco_skills` | ESCO skill taxonomy |
| `esco_relations` | Occupation-to-skill relationships |
| `app_configs` | Pricing estimates, assessment questions, scoring config |

---

## Key Design Decisions

| Decision | Justification |
|---|---|
| **SBERT over TF-IDF** | Captures semantic meaning (e.g., "software engineer" ≈ "backend developer"), not just keyword overlap |
| **ESCO taxonomy** | Provides a standardised, industry-neutral framework for skill and occupation mapping |
| **PayLab for salaries** | Only publicly available Sri Lanka-specific salary dataset |
| **`upsert=True` in MongoDB** | Allows the scraping pipeline to run repeatedly without creating duplicate records |
| **Pre-computed embeddings** | Moves heavy computation offline — API response time is milliseconds, not minutes |
| **`from_mongo=True` flag** | Decouples the engine from local file paths, enabling cloud-native deployment |
=======
# PathFinder+ — Machine Learning & Data Cleaning Module

This directory contains the complete **Data Science Component** of the PathFinder+ career guidance system. It is responsible for data collection, cleaning, embedding generation, and producing real-time, personalized career recommendations.

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Folder Structure](#folder-structure)
3. [Core Component: Recommendation Engine](#core-component-recommendation-engine)
4. [ML Models & Embeddings](#ml-models--embeddings)
5. [Data Pipeline](#data-pipeline)
6. [Scripts Reference](#scripts-reference)
7. [Tests & Verification](#tests--verification)
8. [How to Run](#how-to-run)
9. [Cloud (MongoDB Atlas) Integration](#cloud-mongodb-atlas-integration)
10. [Key Design Decisions](#key-design-decisions)

---

## Architecture Overview

```
User Input (Skills, Target Job, Level)
            │
            ▼
┌─────────────────────────────────────────────┐
│         RecommendationEngine (core/)         │
│                                             │
│  SBERT ──► Semantic Vector Matching         │
│  ESCO  ──► Occupation Taxonomy Mapping      │
│  PayLab──► Salary Benchmarking              │
│                                             │
│  Outputs:                                   │
│  ├── Courses (ranked by relevance & ROI)    │
│  ├── Jobs (ESCO-mapped with salary)         │
│  ├── Mentors (professional matching)        │
│  ├── Skill Gap Assessment Questions         │
│  ├── Career Readiness Index (0-100)         │
│  └── 12-Month Action Plan                  │
└─────────────────────────────────────────────┘
            │
            ▼
     MongoDB Atlas (Cloud)
```

---

## Folder Structure

```
Machine Learning and Data Cleaning/
│
├── core/                          # Engine logic
│   └── recommendation_engine.py  # Main recommendation engine (~2,000 lines)
│
├── models/                        # Pre-computed ML embeddings (.pt files)
│   ├── job_embeddings.pt
│   ├── esco_occ_embeddings.pt
│   ├── course_embeddings_all_courses_master.pt
│   ├── course_embeddings_cloud_courses.pt
│   ├── course_embeddings_academic_courses_master.pt
│   └── academic_embeddings.pt
│
├── data/
│   ├── raw/                       # Scraped raw data from job/course sites
│   │   ├── scrapers/              # Individual scraper scripts (Ikman, LinkedIn etc.)
│   │   ├── esco/                  # ESCO taxonomy CSVs (occupations, skills, relations)
│   │   └── assessment/            # Assessment question bank JSON files
│   ├── processed/                 # Cleaned, merged master CSV files
│   │   ├── all_jobs_master.csv
│   │   ├── all_courses_master.csv
│   │   ├── academic_courses_master.csv
│   │   ├── career_progressions.csv
│   │   ├── mentors.json
│   │   └── synthetic_jobs.csv
│   └── config/                    # Pricing estimates, salary mappings
│       ├── paylab_salary_mapping.csv
│       └── pricing_estimates.json
│
├── scripts/                       # Data operations and automation
│   ├── orchestrate_scraping.py    # Master pipeline runner
│   ├── push_to_mongo.py           # Cloud database sync (CRUD)
│   ├── clean_and_refine_jobs.py   # Job data normalization
│   ├── refine_course_data.py      # Course data normalization
│   ├── merge_all_jobs.py          # Merges scraped jobs into master CSV
│   ├── consolidate_courses.py     # Merges course sources
│   ├── market_trend_analyzer.py   # Field-specific market trend analysis
│   ├── generate_model_artifacts.py# Rebuilds .pt embedding files
│   ├── generate_more_mentors.py   # Synthetic mentor data generation
│   ├── synthetic_market_generator.py # Augments job listings
│   ├── check_cloud_data.py        # Cloud data health check
│   └── spam_detector.py           # Filters low-quality job listings
│
├── tests/                         # Verification and simulation scripts
│   ├── interactive_playground.py  # Manual prompt-and-try testing tool
│   ├── professional_interactive_demo.py # Pre-scripted multi-persona demo
│   ├── final_system_verification.py     # 5-persona automated test suite
│   ├── final_user_simulation_test.py    # Detailed simulation with logs
│   └── multi_industry_test.py     # Business, Healthcare, IT persona tests
│
├── notebooks/                     # Jupyter notebooks for exploration
├── .env                           # MongoDB URI (not committed to Git)
└── requirements.txt               # All Python dependencies
```

---

## Core Component: Recommendation Engine

**File**: `core/recommendation_engine.py`

This is the central brain of the system. It is a ~2,000-line class that handles the entire recommendation lifecycle.

### Key Methods

| Method | Description |
|---|---|
| `from_mongo()` | Loads all data directly from MongoDB Atlas (production mode) |
| `get_recommendations_from_assessment(assessment_vector, target_job)` | Main entry point — generates the full dashboard bundle |
| `recommend_courses(...)` | Ranks courses via SBERT similarity + ROI scoring |
| `match_jobs(...)` | Finds ESCO-mapped jobs with salary from PayLab data |
| `match_mentors(...)` | Finds professional mentors by industry and seniority |
| `generate_skill_assessment_questions(skill_gap)` | Produces dynamic assessment questions from the skill gap |
| `calculate_readiness_index(...)` | Computes a 0-100 Career Readiness Score |
| `generate_action_plan(...)` | Produces a monthly 12-step career roadmap |
| `get_personalized_market_trends(...)` | Returns field-specific salary and trend insights |

### Recommendation Output Bundle (Dashboard Format)

```python
{
  "mapped_occupation": "...",           # ESCO-matched job title
  "compulsory_skills": [...],           # Required skill gaps
  "optional_skills": [...],             # Nice-to-have skills
  "assessment_questions": [...],        # Personalized quiz questions
  "recommendations": [                  # Ranked courses
    {
      "course_name": "...",
      "provider": "...",
      "fee": "...",
      "relevance_score": 0.92,
      "url": "...",
      "why_recommended": [...]
    }
  ],
  "job_ideas": [...],                   # Relevant job listings
  "mentors": [...],                     # Professional mentors
  "readiness_score": {
    "overall": 65,
    "stage": "Mid-level Readiness",
    "breakdown": {...}
  },
  "salary_estimate": "150,000 - 250,000 LKR",
  "market_trends": {...},
  "action_plan": [...]                  # 12-month milestone roadmap
}
```

---

## ML Models & Embeddings

All `.pt` files in `models/` are **pre-computed PyTorch tensors** generated from the `all-MiniLM-L6-v2` Sentence-BERT model. They store dense vector representations of jobs, courses, and ESCO occupations, enabling fast cosine similarity matching at runtime without re-encoding the entire dataset on every API call.

| File | Contents | Size |
|---|---|---|
| `job_embeddings.pt` | Vectors for all scraped job listings | ~3.1 MB |
| `esco_occ_embeddings.pt` | Vectors for all ESCO occupation titles | ~4.5 MB |
| `course_embeddings_all_courses_master.pt` | Vectors for all skill-gap courses | ~5.6 MB |
| `course_embeddings_academic_courses_master.pt` | Vectors for university degree programmes | ~2.2 MB |
| `course_embeddings_cloud_courses.pt` | Cloud-synced course vectors | ~5.6 MB |
| `academic_embeddings.pt` | Dedicated academic institution embeddings | ~112 KB |

> **Important for Backend Developers**: These `.pt` files **must be included** in your deployment package. Without them, the engine will attempt to rebuild them on startup, which takes ~5-10 minutes and requires all CSV data to be locally available. With them, startup is near-instant.

To rebuild them manually, run:
```bash
python scripts/generate_model_artifacts.py
```

---

## Data Pipeline

The full data lifecycle from scraping to recommendation works as follows:

```
1. SCRAPE       scrapers/ scripts (Ikman, GeneralExpress, LinkedIn, etc.)
      │
      ▼
2. MERGE        scripts/merge_all_jobs.py / consolidate_courses.py
      │          → Output: data/processed/all_jobs_master.csv
      │
      ▼
3. CLEAN        scripts/clean_and_refine_jobs.py / refine_course_data.py
      │          → Normalizes titles, removes spam, maps ESCO categories
      │
      ▼
4. EMBED        scripts/generate_model_artifacts.py
      │          → Produces .pt vector files in models/
      │
      ▼
5. SYNC         scripts/push_to_mongo.py
                 → Uploads all processed data to MongoDB Atlas
```

**To run the entire pipeline in one command:**
```bash
python scripts/orchestrate_scraping.py
```

---

## Scripts Reference

| Script | Purpose |
|---|---|
| `orchestrate_scraping.py` | Runs the full pipeline end-to-end |
| `push_to_mongo.py` | CRUD operations: Creates, Updates, and Deletes records in MongoDB Atlas |
| `clean_and_refine_jobs.py` | Normalizes job titles, maps ESCO codes, removes duplicates |
| `refine_course_data.py` | Standardizes fee formats, duration, and provider names |
| `market_trend_analyzer.py` | Generates salary/growth trend data per industry field |
| `generate_model_artifacts.py` | Rebuilds all `.pt` embedding files from CSVs |
| `generate_more_mentors.py` | Augments mentor pool with synthetic professional profiles |
| `spam_detector.py` | Identifies and removes low-quality or irrelevant job posts |
| `check_cloud_data.py` | Verifies integrity of all MongoDB Atlas collections |

---

## Tests & Verification

| Script | What it Tests |
|---|---|
| `interactive_playground.py` | **Manual testing tool** — input any career scenario and get results live |
| `professional_interactive_demo.py` | Runs 3 pre-scripted personas (O/L Student, A/L Student, Career Switcher) |
| `final_system_verification.py` | Automated 5-persona suite (IT, Business, Healthcare, Student, Pro) |
| `multi_industry_test.py` | Stress-tests recommendations across non-IT industries |
| `final_user_simulation_test.py` | Produces detailed, human-readable logs for each persona |

---

## How to Run

### 1. Setup Environment
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows

# Install all dependencies
pip install -r requirements.txt
```

### 2. Configure MongoDB Connection
Create a `.env` file in this directory with:
```
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
DATABASE_NAME=pathfinder_plus
```

### 3. Run Interactive Demo (Quickest way to verify the system)
```bash
python tests/interactive_playground.py
```

### 4. Run Full Verification Suite
```bash
python tests/final_system_verification.py
```

### 5. Use the Engine in Your Code (Backend Integration)
```python
from core.recommendation_engine import RecommendationEngine

# Initialize from cloud (production mode)
engine = RecommendationEngine.from_mongo()

# Get a full career recommendation dashboard bundle
# assessment_vector is typically created via process_comprehensive_assessment
bundle = engine.get_recommendations_from_assessment(
    assessment_vector={
        "status_level": 2,          # 0=O/L, 1=A/L, 2=Undergraduate, 3=Professional
        "experience_years": 2,
        "responsibility_band": 1,
        "education_level": 3,
        "extracted_intent_skills": ["Python", "SQL"],
        "domain": "IT"
    },
    target_job="Data Scientist"
)
```

---

## Cloud (MongoDB Atlas) Integration

All production data is stored in the `pathfinder_plus` database on MongoDB Atlas. The following collections are managed by this module:

| Collection | Contents |
|---|---|
| `jobs` | Scraped and cleaned job listings |
| `jobs_synthetic` | AI-augmented job listings for rare roles |
| `courses` | Professional skill-gap courses |
| `courses_academic` | University degree programmes |
| `mentors` | Professional mentor profiles |
| `career_paths` | Role-to-role progression mappings |
| `salary_data` | PayLab industry salary benchmarks |
| `esco_occupations` | ESCO occupation taxonomy |
| `esco_skills` | ESCO skill taxonomy |
| `esco_relations` | Occupation-to-skill relationships |
| `app_configs` | Pricing estimates, assessment questions, scoring config |

---

## Key Design Decisions

| Decision | Justification |
|---|---|
| **SBERT over TF-IDF** | Captures semantic meaning (e.g., "software engineer" ≈ "backend developer"), not just keyword overlap |
| **ESCO taxonomy** | Provides a standardised, industry-neutral framework for skill and occupation mapping |
| **PayLab for salaries** | Only publicly available Sri Lanka-specific salary dataset |
| **`upsert=True` in MongoDB** | Allows the scraping pipeline to run repeatedly without creating duplicate records |
| **Pre-computed embeddings** | Moves heavy computation offline — API response time is milliseconds, not minutes |
| **`from_mongo=True` flag** | Decouples the engine from local file paths, enabling cloud-native deployment |
>>>>>>> bfbe53ef6bb934196fb2650c10feae91997773ff
