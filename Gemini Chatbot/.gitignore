# PathFinder+ Mentor Backend

This is the FastAPI-based backend for the PathFinder+ Mentor Recommendation system. It provides a RESTful API for matching users with appropriate mentors based on their skills, target roles, and career domains.

## Features
- **Semantic Matching**: Matches user skills against mentor expertise.
- **Role Relevancy**: Biases results towards mentors currently in or near the user's target role.
- **Domain Isolation**: Ensures mentors and users are in compatible career sectors (e.g., Data Science, Engineering, etc.).
- **FastAPI Core**: Lightweight and high-performance, with full CORS support for the frontend.

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   ```bash
   python main.py
   ```
   The API will be available at `http://127.0.0.1:8001`.

3. **Test the API**:
   ```bash
   python test_api.py
   ```

## Endpoint Description

### `POST /api/v1/mentors/recommend`
Generates a list of recommended mentors.

**Request Body**:
```json
{
  "skills": ["Python", "SQL", "Tableau"],
  "target_role": "Data Analyst",
  "domain": "Data Science"
}
```

**Response**: Returns a JSON list of the top 3-5 matching mentors, including their matching scores and matched skills.
