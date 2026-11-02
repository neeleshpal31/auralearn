import database
import recommender

def test_recommendations():
    print("=== Testing Recommendation Engine ===")
    
    # Establish connection
    conn = database.get_db_connection()
    users = conn.execute("SELECT id, username, full_name, skill_level, interests FROM users").fetchall()
    
    for u in users:
        print(f"\nUser: {u['full_name']} (@{u['username']})")
        print(f"Skill Level: {u['skill_level']} | Interests: {u['interests']}")
        
        # Check enrolled courses
        enrollments = conn.execute(
            "SELECT c.title FROM enrollments e JOIN courses c ON e.course_id = c.id WHERE e.user_id = ?",
            (u['id'],)
        ).fetchall()
        enrolled_titles = [e['title'] for e in enrollments]
        print(f"Enrolled in: {enrolled_titles}")
        
        # Fetch recommendations
        recs = recommender.get_recommendations(u['id'], limit=3)
        print("Recommended Courses:")
        for idx, r in enumerate(recs):
            print(f"  {idx+1}. {r['title']} ({r['category']} - {r['skill_level']})")
            print(f"     Why: {r['explanation']} | Score: {r['score']:.4f}")
            
    # Test similar courses lookup
    print("\n=== Testing Similar Courses API ===")
    course = conn.execute("SELECT id, title FROM courses LIMIT 1").fetchone()
    if course:
        print(f"Source Course: {course['title']}")
        similar = recommender.get_similar_courses(course['id'], limit=3)
        for idx, s in enumerate(similar):
            print(f"  {idx+1}. {s['title']} | Sim: {s['similarity_score']:.4f}")
            
    conn.close()

if __name__ == "__main__":
    test_recommendations()
