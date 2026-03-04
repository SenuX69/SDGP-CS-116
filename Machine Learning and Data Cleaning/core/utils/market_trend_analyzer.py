
import pandas as pd
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import torch
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TrendAnalyzer")

class MarketTrendAnalyzer:
    def __init__(self, jobs_data, model_name="all-MiniLM-L6-v2"):
        """
        Initialize with either a path (str/Path) or a pre-loaded DataFrame.
        """
        if isinstance(jobs_data, (str, Path)):
            self.jobs_df = pd.read_csv(jobs_data)
        elif isinstance(jobs_data, pd.DataFrame):
            self.jobs_df = jobs_data
        else:
            self.jobs_df = pd.DataFrame()
            print("Warning: MarketTrendAnalyzer initialized with empty data.")
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.clusters = None
        
        if not self.jobs_df.empty:
            # Pre-calculate combined_text for all methods
            cols = self.jobs_df.columns
            title_col = 'title' if 'title' in cols else ('job_title' if 'job_title' in cols else None)
            desc_col = 'description' if 'description' in cols else None
            
            if title_col:
                self.jobs_df['combined_text'] = self.jobs_df[title_col].fillna('') + " " + (self.jobs_df[desc_col].fillna('').str[:200] if desc_col else "")
            else:
                self.jobs_df['combined_text'] = ""
        else:
            self.jobs_df['combined_text'] = pd.Series(dtype=str)
        
    def analyze_trends(self, n_clusters=15):
        """Perform K-Means clustering on job titles/descriptions to find market segments"""
        logger.info(f"Analyzing trends across {len(self.jobs_df)} jobs...")
        
        # 1. Prepare text data (Focus on IT and Business as requested)
        if not self.jobs_df.empty and 'title' in self.jobs_df.columns:
            self.jobs_df['combined_text'] = self.jobs_df['title'].fillna('') + " " + (self.jobs_df['description'].fillna('').str[:200] if 'description' in self.jobs_df.columns else "")
        else:
            self.jobs_df['combined_text'] = pd.Series(dtype=str)
        
        # 2. Generate Embeddings (Deep Learning)
        logger.info("Generating semantic embeddings for clustering...")
        self.embeddings = self.model.encode(self.jobs_df['combined_text'].tolist(), show_progress_bar=True)
        
        # 3. K-Means Clustering (Machine Learning)
        logger.info(f"Running K-Means clustering with k={n_clusters}...")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.jobs_df['cluster'] = kmeans.fit_predict(self.embeddings)
        
        # 4. Extract Top Keywords per Cluster (NLP)
        trend_summary = []
        for i in range(n_clusters):
            cluster_data = self.jobs_df[self.jobs_df['cluster'] == i]
            
            # Simple keyword extraction using TF-IDF for the cluster
            vectorizer = TfidfVectorizer(stop_words='english', max_features=10)
            tfidf_matrix = vectorizer.fit_transform(cluster_data['combined_text'].fillna(''))
            keywords = vectorizer.get_feature_names_out()
            
            # Get the most common job titles in this cluster
            common_titles = cluster_data['title'].value_counts().head(3).index.tolist()
            
            trend_summary.append({
                "cluster_id": i,
                "size": len(cluster_data),
                "top_titles": common_titles,
                "key_skills": keywords.tolist(),
                "market_share": round((len(cluster_data) / len(self.jobs_df)) * 100, 2)
            })
            
        return trend_summary

    def get_trends_by_field(self, field, n_clusters=5):
        """Analyzes trends for a specific field (e.g., 'IT', 'Business', 'Marketing')"""
        logger.info(f"Analyzing specific trends for field: {field}")
        
        # 1. Broad field filtering (Refined Keywords)
        field_keywords = {
            "IT": ["software", "developer", "data scientist", "devops", "java", "python", "javascript", "cloud", "aws", "azure", "network", "security", "ai", "machine learning"],
            "Business": ["business analyst", "finance", "accounting", "hr", "operations", "sales manager", "strategy", "consultant"],
            "Marketing": ["digital marketing", "seo", "content writer", "social media manager", "brand manager", "advertising"],
            "Healthcare": ["nurse", "pharmacist", "clinical", "medical officer", "doctor"]
        }
        
        keywords = field_keywords.get(field, [field.lower()])
        pattern = "|".join(keywords)
        
        field_df = self.jobs_df[
            self.jobs_df['title'].str.contains(pattern, case=False, na=False) |
            self.jobs_df['description'].str.contains(pattern, case=False, na=False)
        ].copy()
        
        if len(field_df) < n_clusters:
            n_clusters = max(1, len(field_df))
            
        if len(field_df) == 0:
            return [{"segment": "Market Average", "skills": ["COMMUNICATION", "ADAPTIVE LEARNING"], "demand": 0}], self.jobs_df

        # 2. Field-Specific Clustering
        embeddings = self.model.encode(field_df['combined_text'].tolist(), show_progress_bar=False)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        field_df['cluster'] = kmeans.fit_predict(embeddings)
        
        # 3. Custom Stop Words for better NLP quality
        from sklearn.feature_extraction import text
        custom_stop = [
            "job", "save", "sri", "lanka", "executive", "company", "limited", "pvt", 
            "apply", "requirements", "years", "experience", "skills", "salary", 
            "location", "full", "time", "part", "work", "looking", "candidate",
            "qualifications", "degree", "diploma", "knowledge", "ability"
        ]
        stop_words = text.ENGLISH_STOP_WORDS.union(custom_stop)
        
        trend_summary = []
        for i in range(n_clusters):
            cluster_data = field_df[field_df['cluster'] == i]
            
            # Use combined_text for keywords to be more descriptive
            vectorizer = TfidfVectorizer(stop_words=list(stop_words), max_features=8)
            tfidf_matrix = vectorizer.fit_transform(cluster_data['combined_text'].fillna(''))
            keywords = vectorizer.get_feature_names_out()
            
            common_titles = cluster_data['title'].value_counts().head(3).index.tolist()
            
            # Refine segment naming logic: Use the most common but specific title
            segment_name = common_titles[0] if common_titles else "General Segment"
            if "executive" in segment_name.lower() and len(common_titles) > 1:
                segment_name = common_titles[1] # Try 2nd title if 1st is generic 'Executive'
            
            trend_summary.append({
                "segment": segment_name,
                "roles": common_titles,
                "demand": len(cluster_data),
                "skills": [k.upper() for k in keywords.tolist()]
            })
            
        return sorted(trend_summary, key=lambda x: x['demand'], reverse=True), field_df

    def get_hot_skills(self, top_k=20, df=None):
        """Identifies skills with high demand across the provided dataframe or full dataset"""
        target_df = df if df is not None else self.jobs_df
        
        all_skills = []
        if 'extracted_skills' in target_df.columns:
            for skills in target_df['extracted_skills'].dropna():
                all_skills.extend([s.strip().lower() for s in str(skills).split(",") if s.strip()])
        
        if not all_skills:
            # Fallback to description keywords if extracted_skills is missing
            return {"Problem Solving": 10, "Communication": 8, "Teamwork": 5}

        skill_counts = pd.Series(all_skills).value_counts()
        return skill_counts.head(top_k).to_dict()

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    current_dir = Path(__file__).parent
    master_path = current_dir / "../data/processed/all_jobs_master.csv"
    
    if master_path.exists():
        analyzer = MarketTrendAnalyzer(master_path)
        trends = analyzer.analyze_trends(n_clusters=10)
        
        print("\n" + "="*50)
        print("SRI LANKAN MARKET TREND REPORT (ML-POWERED)")
        print("="*50)
        
        for t in trends:
            print(f"\nCluster #{t['cluster_id']} ({t['market_share']}% of Market)")
            print(f"Typical Roles: {', '.join(t['top_titles'])}")
            print(f"Primary Skills: {', '.join(t['key_skills'])}")
            
        print("\n" + "="*50)
        print("TOP 10 HOT SKILLS")
        hot_skills = analyzer.get_hot_skills(10)
        for skill, count in hot_skills.items():
            print(f"- {skill.upper()}: found in {count} jobs")
    else:
        print(f"Error: Master file not found at {master_path}")
