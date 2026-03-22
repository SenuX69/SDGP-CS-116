
import requests
import json

def test_api():
    url = "http://127.0.0.1:8001/api/v1/mentors/recommend"
    test_data = {
        "skills": ["Python", "SQL", "Tableau"],
        "target_role": "Data Analyst",
        "domain": "Data Science"
    }
    
    print(f"Sending test request to {url}...")
    try:
        response = requests.post(url, json=test_data)
        if response.status_code == 200:
            results = response.json()
            print(f"Success! Found {len(results)} matches:\n")
            for m in results:
                print(f"--- {m['name']} ---")
                print(f"Role: {m['title']} @ {m['company']}")
                print(f"Score: {m['matching_score']} | Skills: {', '.join(m['matched_skills'])}")
                print(f"Bio: {m['bio']}\n")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        print("Tip: Run 'python main.py' in the Mentor-Backend folder first!")

if __name__ == "__main__":
    test_api()
