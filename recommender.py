import sqlite3
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import database

def get_recommendations(user_id, limit=5):
    """
    Generate hybrid course recommendations for a specific user.
    Combines:
      1. Profile-based matching (interests & skill level selected during onboarding)
      2. Content-based filtering (TF-IDF on course text features, matching user enrollment history)
      3. User-User Collaborative Filtering (matching ratings of similar mock/real users)
    """
    conn = database.get_db_connection()
    
    # 1. Fetch current user data
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return []
    
    user_skill = user['skill_level'] or 'Beginner'
    user_interests = [tag.strip().lower() for tag in (user['interests'] or '').split(',') if tag.strip()]
    
    # 2. Fetch all courses
    courses_df = pd.read_sql_query("SELECT * FROM courses", conn)
    if courses_df.empty:
        conn.close()
        return []
    
    # Get user enrollments to exclude from recommendations
    enrolled_courses = pd.read_sql_query(
        "SELECT course_id FROM enrollments WHERE user_id = ?", conn, params=(user_id,)
    )['course_id'].tolist()
    
    # Check user ratings
    user_ratings = pd.read_sql_query(
        "SELECT course_id, rating FROM ratings WHERE user_id = ?", conn, params=(user_id,)
    )
    
    # PRE-CALCULATION A: Content-Based Similarity Scores
    # Prepare text corpus for TF-IDF
    # Feature columns: title, description, category, tags
    courses_df['corpus'] = (
        courses_df['title'] + " " + 
        courses_df['description'] + " " + 
        courses_df['category'] + " " + 
        courses_df['tags'].apply(lambda x: x.replace(',', ' '))
    )
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(courses_df['corpus'])
    course_sim_matrix = cosine_similarity(tfidf_matrix)
    
    content_scores = np.zeros(len(courses_df))
    
    # Content-based profiling: if user has rated or enrolled in courses
    if not user_ratings.empty:
        # Build user vector as weighted average of course vectors
        user_rated_cids = user_ratings['course_id'].tolist()
        user_rated_scores = user_ratings['rating'].tolist()
        
        # Calculate weights based on rating (normalize around 0 by subtracting 3)
        weights = [r - 2.5 for r in user_rated_scores] # 5 becomes 2.5, 3 becomes 0.5, 1 becomes -1.5
        
        for cid, wt in zip(user_rated_cids, weights):
            idx = courses_df[courses_df['id'] == cid].index
            if len(idx) > 0:
                idx = idx[0]
                content_scores += course_sim_matrix[idx] * wt
    elif enrolled_courses:
        # If user enrolled but hasn't rated yet, treat enrollments as weight = 1
        for cid in enrolled_courses:
            idx = courses_df[courses_df['id'] == cid].index
            if len(idx) > 0:
                idx = idx[0]
                content_scores += course_sim_matrix[idx]
                
    # Normalize content scores to [0, 1]
    if content_scores.max() != content_scores.min():
        content_scores = (content_scores - content_scores.min()) / (content_scores.max() - content_scores.min())
    else:
        content_scores = np.zeros(len(courses_df))

    # PRE-CALCULATION B: User-User Collaborative Filtering
    collaborative_scores = np.zeros(len(courses_df))
    
    # Load all ratings to construct User-Item Matrix
    all_ratings_df = pd.read_sql_query("SELECT user_id, course_id, rating FROM ratings", conn)
    
    if not all_ratings_df.empty and user_id in all_ratings_df['user_id'].values:
        # Create Pivot table
        user_item_matrix = all_ratings_df.pivot(index='user_id', columns='course_id', values='rating').fillna(0)
        
        # Calculate User Similarity
        user_sim_matrix = cosine_similarity(user_item_matrix)
        user_sim_df = pd.DataFrame(user_sim_matrix, index=user_item_matrix.index, columns=user_item_matrix.index)
        
        # Get top similar users
        similar_users = user_sim_df[user_id].sort_values(ascending=False).drop(user_id)
        similar_users = similar_users[similar_users > 0] # only positive similarity
        
        if not similar_users.empty:
            # Predict scores for each course
            for col_idx, cid in enumerate(courses_df['id']):
                if cid not in enrolled_courses and cid in user_item_matrix.columns:
                    # Weighted average rating from similar users
                    ratings = user_item_matrix.loc[similar_users.index, cid]
                    non_zero_sim = similar_users[ratings > 0]
                    if not non_zero_sim.empty:
                        pred_rating = np.dot(ratings[ratings > 0], non_zero_sim) / non_zero_sim.sum()
                        collaborative_scores[col_idx] = pred_rating
            
            # Normalize collaborative scores to [0, 1] (ratings are 1-5 scale)
            collaborative_scores = collaborative_scores / 5.0
            
    # PRE-CALCULATION C: Profile-based matching scores (Onboarding alignment)
    profile_scores = np.zeros(len(courses_df))
    
    for idx, row in courses_df.iterrows():
        score = 0.0
        # Tag matches
        c_tags = [t.strip().lower() for t in row['tags'].split(',') if t.strip()]
        matches = set(c_tags).intersection(set(user_interests))
        score += len(matches) * 1.5
        
        # Category matches
        if row['category'].lower() in user_interests:
            score += 2.0
            
        # Skill level matches
        if row['skill_level'].lower() == user_skill.lower():
            score += 1.0
        elif (user_skill.lower() == 'intermediate' and row['skill_level'].lower() == 'beginner'):
            score += 0.5 # intermediate user can take beginner course
        elif (user_skill.lower() == 'advanced' and row['skill_level'].lower() in ['beginner', 'intermediate']):
            score += 0.3
            
        profile_scores[idx] = score
        
    # Normalize profile scores to [0, 1]
    if profile_scores.max() != profile_scores.min():
        profile_scores = (profile_scores - profile_scores.min()) / (profile_scores.max() - profile_scores.min())
    else:
        profile_scores = np.zeros(len(courses_df))
        
    # HYBRID SCORE AGGREGATION
    # Weights vary based on active rating history
    if not user_ratings.empty:
        # User has ratings -> rely heavily on Content-Based & Collaborative Filtering
        w_content = 0.4
        w_collab = 0.4
        w_profile = 0.2
    else:
        # Fresh user -> rely entirely on profile selection and popular trends
        w_content = 0.0
        w_collab = 0.0
        w_profile = 1.0 # purely onboarding profile-driven
        
    final_scores = (w_content * content_scores) + (w_collab * collaborative_scores) + (w_profile * profile_scores)
    
    # Store recommendation lists
    recommendations = []
    
    for idx, row in courses_df.iterrows():
        c_id = int(row['id'])
        if c_id in enrolled_courses:
            continue
            
        # Find explanation for the recommendation
        explanation = "Popular trending course in your interest area"
        
        # Determine why it is recommended
        # Check tag overlaps
        c_tags = [t.strip() for t in row['tags'].split(',') if t.strip()]
        matched_tags = [t for t in c_tags if t.lower() in user_interests]
        
        if matched_tags:
            explanation = f"Matches your interest in {matched_tags[0]}"
        elif row['category'].lower() in user_interests:
            explanation = f"Matches your goal in {row['category']}"
        elif not user_ratings.empty:
            # If Content-Based score is high
            if content_scores[idx] > 0.6:
                # Find the highly rated course that triggered this
                user_rated_ids = user_ratings[user_ratings['rating'] >= 4]['course_id'].tolist()
                similar_rated = None
                max_sim = 0
                for r_cid in user_rated_ids:
                    r_idx = courses_df[courses_df['id'] == r_cid].index[0]
                    sim = course_sim_matrix[idx][r_idx]
                    if sim > max_sim:
                        max_sim = sim
                        similar_rated = courses_df.loc[r_idx, 'title']
                if similar_rated:
                    explanation = f"Similar to your top-rated course: {similar_rated}"
            elif collaborative_scores[idx] > 0.6:
                explanation = "Highly rated by learners with similar profiles"
                
        # Also check if it matches the skill level exactly
        if row['skill_level'].lower() == user_skill.lower() and "Matches" not in explanation:
            explanation += f" (Tailored for {user_skill}s)"
            
        recommendations.append({
            'id': c_id,
            'title': row['title'],
            'description': row['description'],
            'category': row['category'],
            'tags': row['tags'],
            'skill_level': row['skill_level'],
            'duration': row['duration'],
            'rating': float(row['rating']),
            'enrolled_count': int(row['enrolled_count']),
            'score': float(final_scores[idx]),
            'explanation': explanation
        })
        
    # Sort recommendations by final score descending
    recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)
    
    # If we don't have enough matching recommendations, append popular courses as fallback
    if len(recommendations) < limit:
        # Select popular un-enrolled courses
        popular_courses = courses_df[~courses_df['id'].isin(enrolled_courses)].sort_values(
            by=['rating', 'enrolled_count'], ascending=False
        )
        
        existing_recs_ids = {r['id'] for r in recommendations}
        for _, row in popular_courses.iterrows():
            c_id = int(row['id'])
            if c_id not in existing_recs_ids:
                recommendations.append({
                    'id': c_id,
                    'title': row['title'],
                    'description': row['description'],
                    'category': row['category'],
                    'tags': row['tags'],
                    'skill_level': row['skill_level'],
                    'duration': row['duration'],
                    'rating': float(row['rating']),
                    'enrolled_count': int(row['enrolled_count']),
                    'score': 0.0,
                    'explanation': "Popular choice on the platform"
                })
            if len(recommendations) >= limit:
                break
                
    conn.close()
    return recommendations[:limit]

def get_similar_courses(course_id, limit=4):
    """
    Get content-based similar courses for a specific course page.
    """
    conn = database.get_db_connection()
    courses_df = pd.read_sql_query("SELECT * FROM courses", conn)
    
    if courses_df.empty or course_id not in courses_df['id'].values:
        conn.close()
        return []
        
    courses_df['corpus'] = (
        courses_df['title'] + " " + 
        courses_df['description'] + " " + 
        courses_df['category'] + " " + 
        courses_df['tags'].apply(lambda x: x.replace(',', ' '))
    )
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(courses_df['corpus'])
    course_sim_matrix = cosine_similarity(tfidf_matrix)
    
    target_idx = courses_df[courses_df['id'] == course_id].index[0]
    
    # Get similarity scores
    sim_scores = list(enumerate(course_sim_matrix[target_idx]))
    # Sort by similarity score descending, exclude self (target_idx)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [item for item in sim_scores if item[0] != target_idx]
    
    similar_courses = []
    for idx, score in sim_scores[:limit]:
        row = courses_df.iloc[idx]
        similar_courses.append({
            'id': int(row['id']),
            'title': row['title'],
            'description': row['description'],
            'category': row['category'],
            'tags': row['tags'],
            'skill_level': row['skill_level'],
            'duration': row['duration'],
            'rating': float(row['rating']),
            'enrolled_count': int(row['enrolled_count']),
            'similarity_score': float(score)
        })
        
    conn.close()
    return similar_courses
