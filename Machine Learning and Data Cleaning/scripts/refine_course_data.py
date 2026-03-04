import pandas as pd
import numpy as np
import re
import random
from pathlib import Path
from datetime import datetime

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = BASE_DIR / "data/processed/academic_courses_master.csv"

# Market Researched Defaults (LKR and Days)
DEFAULTS = {
    'certificate': {'duration': 120, 'cost': 50000},
    'diploma': {'duration': 365, 'cost': 150000},
    'hnd': {'duration': 730, 'cost': 550000},
    'degree': {'duration': 1460, 'cost': 2800000},
    'bsc': {'duration': 1460, 'cost': 2800000},
    'engineering': {'duration': 1460, 'cost': 3500000},
    'masters': {'duration': 730, 'cost': 850000},
    'msc': {'duration': 730, 'cost': 850000},
    'top-up': {'duration': 365, 'cost': 650000}
}

def extract_numeric(text):
    if pd.isna(text) or not isinstance(text, str):
        return None
    nums = re.findall(r'\d+', str(text).replace(',', ''))
    return int(nums[0]) if nums else None

def get_level(row):
    """
    Determine the course level from course name and level fields.
    Checks for specific keywords in priority order to avoid misclassification.
    """
    title = str(row.get('course_name', '')).lower()
    level_text = str(row.get('level', '')).lower()
    search_text = f"{title} {level_text}"
    
    # Check for masters first (most specific - must come before 'degree')
    if "master of science" in search_text:
        print(f"DEBUG: Found 'master of science' in '{search_text}'. Returning 'masters'")
    
    if any(keyword in search_text for keyword in ['masters', 'msc', 'mba', 'ma ', 'm.sc', 'm.a', 'master of', 'postgraduate']):
        return 'masters'
    
    # Check for top-up degrees
    if 'top-up' in search_text or 'top up' in search_text:
        return 'top-up'
    
    # Check for engineering degrees (before generic degree check)
    if 'engineering' in search_text and any(kw in search_text for kw in ['beng', 'b.eng', 'bachelor']):
        return 'engineering'
    
    # Check for HND
    if 'hnd' in search_text or 'higher national diploma' in search_text:
        return 'hnd'
    
    # Check for BSc specifically
    if 'bsc' in search_text or 'b.sc' in search_text:
        return 'bsc'
    
    # Check for diploma
    if 'diploma' in search_text and 'hnd' not in search_text and 'higher national' not in search_text:
        return 'diploma'
    
    # Check for certificate
    if 'certificate' in search_text:
        return 'certificate'
    
    # Check for generic degree/bachelor (after all specific checks)
    if 'degree' in search_text or 'bachelor' in search_text:
        return 'degree'
    
    # Final fallback
    return 'certificate'


def refine_data():
    print("Starting Data Refinement for Academic Courses...")
    
    if not INPUT_FILE.exists():
        print(f" ERROR: Input file not found at {INPUT_FILE}")
        return
        
    print(f"Reading {INPUT_FILE.name}...")
    df = pd.read_csv(INPUT_FILE)
    
    if 'course_title' in df.columns:
        df = df.rename(columns={'course_title': 'course_name'})
    
    # Filter for PickACourse only - DISABLED to allow all sources
    # if 'source' in df.columns:
    #     initial_count = len(df)
    #     df = df[df['source'] == 'pickacourse.lk']
    #     print(f"Filtered to pickacourse.lk: Kept {len(df)} (Removed {initial_count - len(df)} records from other sources).")
    # else:
    #     print(" 'source' column not found! Skipping source filter.")
    if 'source' in df.columns:
        print(f"Processing all sources. Breakdown:\n{df['source'].value_counts()}")


    #  Standardize columns
    df = df.drop_duplicates(subset=['course_name'], keep='first')
    
    #  Clean numeric values
    if 'fees' in df.columns:
        df['cost_numeric'] = df['fees'].apply(extract_numeric)
    elif 'cost' in df.columns:
        df['cost_numeric'] = df['cost'].apply(extract_numeric)
    else:
        df['cost_numeric'] = np.nan
        
    if 'duration' in df.columns:
        df['duration_numeric'] = df['duration'].apply(extract_numeric)
    else:
        df['duration_numeric'] = np.nan

    #  Impute Missing Values
    print("Imputing missing values using market research.")
    df['is_estimated'] = False
    
    # Assign level column first
    df['level'] = df.apply(get_level, axis=1)

    for idx, row in df.iterrows():
        level = row['level']
        cost_text = str(row.get('cost', '')).lower()
        
        # Skip forced updates for Free or Free Trial courses - keep them as 0/Free
        if 'free' in cost_text:
             df.at[idx, 'cost_numeric'] = 0
             df.at[idx, 'is_estimated'] = False
             continue
        
        # Force update for ALL major academic levels to ensure consistency and fix 2.8M placeholders
        # We exclude 'certificate' to avoid overwriting potentially valid low/free prices for short courses
        force_clean_levels = ['masters', 'msc', 'diploma', 'hnd', 'top-up', 'engineering', 'degree', 'bsc', 'bachelor']
        
        if level in force_clean_levels:
            # Use default only if level exists in DEFAULTS, else fallback
            default_key = level if level in DEFAULTS else 'degree' 
            if level == 'bachelor': default_key = 'degree'
            
            if default_key in DEFAULTS:
                 base_cost = float(DEFAULTS[default_key]['cost'])
                 # Add +/- 15% random variation
                 variation = random.uniform(0.85, 1.15)
                 varied_cost = base_cost * variation
                 # Round to nearest 1000 for cleaner look
                 final_cost = round(varied_cost / 1000) * 1000
                 
                 df.at[idx, 'cost_numeric'] = final_cost
                 df.at[idx, 'duration_numeric'] = DEFAULTS[default_key]['duration']
                 df.at[idx, 'is_estimated'] = True
            continue

        if pd.isna(row['cost_numeric']) or row['cost_numeric'] == 0:
            df.at[idx, 'cost_numeric'] = DEFAULTS[level]['cost']
            df.at[idx, 'is_estimated'] = True
            
        if pd.isna(row['duration_numeric']) or row['duration_numeric'] == 0:
            df.at[idx, 'duration_numeric'] = DEFAULTS[level]['duration']
            df.at[idx, 'is_estimated'] = True

    #  Save to Processed folder
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f" Final dataset saved to {OUTPUT_FILE}")
    print(f" Total Records: {len(df)}")
    print(f" Estimated Records: {df['is_estimated'].sum()}")
    
    print("\n--- Final Pricing Summary (Average) ---")
    print(df.groupby('level')['cost_numeric'].mean().round(2).to_string())

if __name__ == "__main__":
    refine_data()
