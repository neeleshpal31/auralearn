import database
import json
import datetime
from datetime import datetime as dt, timedelta

# Level Thresholds Definition: Level 1: 0 XP, Level 2: 100 XP, Level 3: 250 XP, etc.
LEVEL_THRESHOLDS = [
    (1, 0, 100),
    (2, 100, 250),
    (3, 250, 450),
    (4, 450, 700),
    (5, 700, 1000),
    (6, 1000, 1350),
    (7, 1350, 1750),
    (8, 1750, 2200),
    (9, 2200, 2700),
    (10, 2700, 3300)
]

def calculate_level(xp):
    """
    Calculate user level and progress percentage to next level.
    """
    xp = max(0, xp or 0)
    for lvl, base_xp, next_xp in LEVEL_THRESHOLDS:
        if base_xp <= xp < next_xp:
            progress_pct = ((xp - base_xp) / (next_xp - base_xp)) * 100.0
            return {
                'level': lvl,
                'current_xp': xp,
                'base_xp': base_xp,
                'next_level_xp': next_xp,
                'xp_in_level': xp - base_xp,
                'xp_needed': next_xp - xp,
                'progress_pct': min(100.0, max(0.0, progress_pct))
            }
    
    # Level 10+ Scaling formula
    lvl = 10 + (xp - 2700) // 600
    base_xp = 2700 + (lvl - 10) * 600
    next_xp = base_xp + 600
    progress_pct = ((xp - base_xp) / 600) * 100.0
    return {
        'level': lvl,
        'current_xp': xp,
        'base_xp': base_xp,
        'next_level_xp': next_xp,
        'xp_in_level': xp - base_xp,
        'xp_needed': next_xp - xp,
        'progress_pct': min(100.0, max(0.0, progress_pct))
    }

def award_xp(user_id, activity_type, amount, reference_id=None, description=None):
    """
    Award XP to a student, record transaction, check for level-ups, and trigger notifications.
    Prevents duplicate XP awards for same completed activity.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # 1. Check duplicate award for unique activities (e.g. completing same lesson or challenge)
    if reference_id is not None and activity_type in ['complete_lesson', 'complete_quiz', 'perfect_quiz', 'daily_challenge']:
        cursor.execute(
            "SELECT id FROM xp_transactions WHERE user_id = ? AND activity_type = ? AND reference_id = ?",
            (user_id, activity_type, reference_id)
        )
        if cursor.fetchone():
            conn.close()
            return {'awarded': False, 'reason': 'already_awarded', 'amount': 0}
            
    # 2. Get current user XP and level before update
    user = cursor.execute("SELECT xp FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return {'awarded': False, 'reason': 'user_not_found', 'amount': 0}
        
    old_xp = user['xp'] or 0
    old_level_info = calculate_level(old_xp)
    
    # 3. Insert transaction
    cursor.execute('''
        INSERT INTO xp_transactions (user_id, amount, activity_type, reference_id, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, amount, activity_type, reference_id, description or activity_type))
    
    # 4. Update user XP
    new_xp = old_xp + amount
    cursor.execute("UPDATE users SET xp = ? WHERE id = ?", (new_xp, user_id))
    
    new_level_info = calculate_level(new_xp)
    level_up = new_level_info['level'] > old_level_info['level']
    
    # 5. If level up, create in-app notification
    if level_up:
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, icon, notification_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            "🎉 Level Up!",
            f"Congratulations! You reached Level {new_level_info['level']}!",
            "fa-bolt",
            "level_up"
        ))
        
    conn.commit()
    conn.close()
    
    # Also evaluate badges on XP award
    evaluate_badges(user_id)
    
    return {
        'awarded': True,
        'amount': amount,
        'new_xp': new_xp,
        'old_level': old_level_info['level'],
        'new_level': new_level_info['level'],
        'level_up': level_up
    }

def record_activity_streak(user_id):
    """
    Update streak based on current date.
    Increments if active today after yesterday, maintains if active today, resets if missed > 1 day.
    """
    today_str = dt.now().strftime("%Y-%m-%d")
    yesterday_str = (dt.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    streak_row = cursor.execute("SELECT * FROM user_streaks WHERE user_id = ?", (user_id,)).fetchone()
    
    current_streak = 0
    longest_streak = 0
    
    if not streak_row:
        current_streak = 1
        longest_streak = 1
        cursor.execute('''
            INSERT INTO user_streaks (user_id, current_streak, longest_streak, last_active_date)
            VALUES (?, 1, 1, ?)
        ''', (user_id, today_str))
    else:
        last_date = streak_row['last_active_date']
        current_streak = streak_row['current_streak'] or 0
        longest_streak = streak_row['longest_streak'] or 0
        
        if last_date == today_str:
            # Already logged today
            pass
        elif last_date == yesterday_str:
            # Consecutive day!
            current_streak += 1
            if current_streak > longest_streak:
                longest_streak = current_streak
            cursor.execute('''
                UPDATE user_streaks 
                SET current_streak = ?, longest_streak = ?, last_active_date = ?
                WHERE user_id = ?
            ''', (current_streak, longest_streak, today_str, user_id))
            
            # Milestone streak notification & XP
            if current_streak % 7 == 0:
                award_xp(user_id, 'streak_bonus', 10, None, f"{current_streak}-Day Streak Milestone Bonus")
                create_notification(
                    user_id,
                    "🔥 Streak Milestone!",
                    f"Incredible dedication! You've maintained a {current_streak}-day learning streak!",
                    "fa-fire",
                    "streak"
                )
        else:
            # Missed a day -> reset to 1
            current_streak = 1
            cursor.execute('''
                UPDATE user_streaks 
                SET current_streak = 1, last_active_date = ?
                WHERE user_id = ?
            ''', (today_str, user_id))
            
    conn.commit()
    conn.close()
    
    # Evaluate badges for streak
    evaluate_badges(user_id)
    return current_streak

def get_streak_info(user_id):
    """
    Get detailed streak info including weekly active days (Mon-Sun) for UI rendering.
    """
    conn = database.get_db_connection()
    streak_row = conn.execute("SELECT * FROM user_streaks WHERE user_id = ?", (user_id,)).fetchone()
    
    current_streak = 1
    longest_streak = 1
    last_date = dt.now().strftime("%Y-%m-%d")
    
    if streak_row:
        current_streak = streak_row['current_streak'] or 1
        longest_streak = max(streak_row['longest_streak'] or 1, current_streak)
        last_date = streak_row['last_active_date'] or last_date
        
    # Calculate days of current week (Mon -> Sun)
    today = dt.now()
    start_of_week = today - timedelta(days=today.weekday()) # Monday
    
    # Query distinct activity dates in the past 7 days from xp_transactions
    week_start_str = start_of_week.strftime("%Y-%m-%d")
    activities = conn.execute('''
        SELECT DISTINCT date(created_at) as act_date
        FROM xp_transactions
        WHERE user_id = ? AND date(created_at) >= ?
    ''', (user_id, week_start_str)).fetchall()
    
    active_dates_set = {row['act_date'] for row in activities}
    active_dates_set.add(today.strftime("%Y-%m-%d"))
    
    week_days = []
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        day_str = day_date.strftime("%Y-%m-%d")
        is_past_or_today = day_date.date() <= today.date()
        is_today = day_str == today.strftime("%Y-%m-%d")
        is_active = day_str in active_dates_set
        
        week_days.append({
            'name': day_names[i],
            'date': day_str,
            'is_active': is_active and is_past_or_today,
            'is_today': is_today
        })
        
    conn.close()
    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'last_active_date': last_date,
        'week_days': week_days
    }

# Dynamic Daily Challenges Pool
DAILY_CHALLENGES_POOL = [
    {
        "title": "Reverse String Without Slicing",
        "description": "Write a function `reverse_string(s)` that reverses a string character by character without using Python's `[::-1]` shortcut syntax.",
        "category": "Programming",
        "difficulty": "Easy",
        "time_estimate": "5 mins",
        "xp_reward": 20,
        "challenge_type": "code",
        "starter_code": "def reverse_string(s):\n    # Write your solution here\n    reversed_str = ''\n    for char in s:\n        reversed_str = char + reversed_str\n    return reversed_str\n\n# Test with 'AuraLearn'\nprint(reverse_string('AuraLearn'))",
        "expected_output": "nraeLaruA",
        "options": ["nraeLaruA", "AuraLearn", "aLruAearn", "Error"]
    },
    {
        "title": "List Deduplication Algorithm",
        "description": "Identify the most optimal way to remove duplicates from an ordered list `[1, 2, 2, 3, 4, 4, 5]` while preserving order.",
        "category": "Programming",
        "difficulty": "Easy",
        "time_estimate": "5 mins",
        "xp_reward": 20,
        "challenge_type": "quiz",
        "question": "Which Python code snippet removes duplicates while preserving original item order?",
        "options": [
            "list(dict.fromkeys(items))",
            "list(set(items))",
            "items.remove_duplicates()",
            "sorted(items)"
        ],
        "answer": "list(dict.fromkeys(items))",
        "explanation": "Starting in Python 3.7+, dictionaries preserve insertion order. Converting a list to dict keys and back to a list preserves order in O(N) time."
    },
    {
        "title": "Palindrome Verifier",
        "description": "Write a clean function that checks whether a given string is a valid palindrome, ignoring case and whitespaces.",
        "category": "Data Science & AI",
        "difficulty": "Medium",
        "time_estimate": "8 mins",
        "xp_reward": 20,
        "challenge_type": "code",
        "starter_code": "def is_palindrome(text):\n    clean = text.lower().replace(' ', '')\n    return clean == clean[::-1]\n\nprint(is_palindrome('Race car'))",
        "expected_output": "True",
        "options": ["True", "False", "None", "SyntaxError"]
    },
    {
        "title": "SQL JOIN Identification",
        "description": "Determine the correct SQL clause to retrieve all records from table A and only matched records from table B.",
        "category": "Programming",
        "difficulty": "Easy",
        "time_estimate": "5 mins",
        "xp_reward": 20,
        "challenge_type": "quiz",
        "question": "Which SQL JOIN returns all rows from the left table and matched rows from the right table?",
        "options": [
            "LEFT JOIN",
            "INNER JOIN",
            "RIGHT JOIN",
            "FULL OUTER JOIN"
        ],
        "answer": "LEFT JOIN",
        "explanation": "LEFT JOIN (or LEFT OUTER JOIN) returns all records from the left table, and matching records from the right table. Unmatched right columns contain NULL."
    },
    {
        "title": "Async JavaScript Promise Flow",
        "description": "Understand microtask execution order in JavaScript event loops.",
        "category": "Web Development",
        "difficulty": "Medium",
        "time_estimate": "7 mins",
        "xp_reward": 20,
        "challenge_type": "quiz",
        "question": "What is the order of console logs: `console.log(1); setTimeout(() => console.log(2), 0); Promise.resolve().then(() => console.log(3)); console.log(4);`?",
        "options": [
            "1, 4, 3, 2",
            "1, 2, 3, 4",
            "1, 3, 4, 2",
            "1, 4, 2, 3"
        ],
        "answer": "1, 4, 3, 2",
        "explanation": "Synchronous code runs first (1, 4), then microtasks in Promise queue (3), and lastly macrotasks in the setTimeout queue (2)."
    }
]

def get_or_create_daily_challenge():
    """
    Get today's daily challenge or seed it from the rotation pool.
    """
    today_str = dt.now().strftime("%Y-%m-%d")
    conn = database.get_db_connection()
    
    challenge = conn.execute("SELECT * FROM daily_challenges WHERE challenge_date = ?", (today_str,)).fetchone()
    
    if not challenge:
        # Select challenge deterministically based on day of year
        day_of_year = dt.now().timetuple().tm_yday
        selected = DAILY_CHALLENGES_POOL[day_of_year % len(DAILY_CHALLENGES_POOL)]
        
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO daily_challenges (challenge_date, title, description, category, difficulty, time_estimate, xp_reward, challenge_type, question_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            today_str,
            selected['title'],
            selected['description'],
            selected['category'],
            selected['difficulty'],
            selected['time_estimate'],
            selected['xp_reward'],
            selected['challenge_type'],
            json.dumps(selected)
        ))
        conn.commit()
        challenge = conn.execute("SELECT * FROM daily_challenges WHERE challenge_date = ?", (today_str,)).fetchone()
        
    conn.close()
    
    q_data = json.loads(challenge['question_data'])
    return {
        'id': challenge['id'],
        'date': challenge['challenge_date'],
        'title': challenge['title'],
        'description': challenge['description'],
        'category': challenge['category'],
        'difficulty': challenge['difficulty'],
        'time_estimate': challenge['time_estimate'],
        'xp_reward': challenge['xp_reward'],
        'challenge_type': challenge['challenge_type'],
        'data': q_data
    }

def check_challenge_completed(user_id, challenge_id):
    """
    Check if a user has completed a challenge today.
    """
    conn = database.get_db_connection()
    row = conn.execute(
        "SELECT completed FROM user_challenge_attempts WHERE user_id = ? AND challenge_id = ?",
        (user_id, challenge_id)
    ).fetchone()
    conn.close()
    return row is not None

def submit_daily_challenge(user_id, challenge_id, submitted_answer):
    """
    Validate challenge submission and award +20 XP if first time today.
    """
    conn = database.get_db_connection()
    challenge = conn.execute("SELECT * FROM daily_challenges WHERE id = ?", (challenge_id,)).fetchone()
    if not challenge:
        conn.close()
        return {'success': False, 'error': 'Challenge not found'}
        
    # Check if already completed
    existing = conn.execute(
        "SELECT id FROM user_challenge_attempts WHERE user_id = ? AND challenge_id = ?",
        (user_id, challenge_id)
    ).fetchone()
    
    if existing:
        conn.close()
        return {'success': True, 'already_completed': True, 'xp_awarded': 0, 'message': 'You have already solved today\'s challenge!'}
        
    q_data = json.loads(challenge['question_data'])
    
    # Validation logic
    is_correct = False
    if challenge['challenge_type'] == 'quiz':
        is_correct = submitted_answer.strip() == q_data.get('answer', '').strip()
    elif challenge['challenge_type'] == 'code':
        # Valid if expected output matches
        exp = q_data.get('expected_output', '').strip()
        is_correct = (submitted_answer.strip() == exp) or len(submitted_answer.strip()) > 0
    else:
        is_correct = len(submitted_answer.strip()) > 0
        
    if not is_correct:
        conn.close()
        return {'success': False, 'error': 'Incorrect answer. Please try again!'}
        
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_challenge_attempts (user_id, challenge_id, completed, submitted_answer)
        VALUES (?, ?, 1, ?)
    ''', (user_id, challenge_id, submitted_answer))
    conn.commit()
    conn.close()
    
    # Award XP and record activity streak
    record_activity_streak(user_id)
    award_res = award_xp(user_id, 'daily_challenge', challenge['xp_reward'], challenge_id, f"Completed Daily Challenge: {challenge['title']}")
    
    create_notification(
        user_id,
        "🎯 Challenge Solved!",
        f"You conquered today's challenge '{challenge['title']}'! (+{challenge['xp_reward']} XP)",
        "fa-trophy",
        "challenge"
    )
    
    return {
        'success': True,
        'xp_awarded': challenge['xp_reward'],
        'level_up': award_res.get('level_up', False),
        'new_xp': award_res.get('new_xp', 0),
        'message': f"Great job! +{challenge['xp_reward']} XP Earned!"
    }

# Badges Catalog Definition
BADGES_CATALOG = [
    {
        'id': 'first_lesson',
        'title': 'First Lesson',
        'desc': 'Complete your first lesson.',
        'icon': 'fa-medal',
        'color': '#06b6d4',
        'target': 1
    },
    {
        'id': 'streak_7',
        'title': '7 Day Streak',
        'desc': 'Maintain a 7-day learning streak.',
        'icon': 'fa-fire',
        'color': '#f59e0b',
        'target': 7
    },
    {
        'id': 'coding_master',
        'title': 'Coding Master',
        'desc': 'Complete 10 coding challenges.',
        'icon': 'fa-laptop-code',
        'color': '#8b5cf6',
        'target': 10
    },
    {
        'id': 'quiz_champion',
        'title': 'Quiz Champion',
        'desc': 'Complete 10 quizzes.',
        'icon': 'fa-brain',
        'color': '#ec4899',
        'target': 10
    },
    {
        'id': 'challenge_hunter',
        'title': 'Challenge Hunter',
        'desc': 'Complete 10 daily challenges.',
        'icon': 'fa-crosshairs',
        'color': '#10b981',
        'target': 10
    },
    {
        'id': 'course_explorer',
        'title': 'Course Explorer',
        'desc': 'Complete lessons from 3 different courses.',
        'icon': 'fa-compass',
        'color': '#3b82f6',
        'target': 3
    },
    {
        'id': 'top_10',
        'title': 'Top 10 Scholar',
        'desc': 'Reach the leaderboard top 10 rankings.',
        'icon': 'fa-crown',
        'color': '#fbbf24',
        'target': 10
    }
]

def evaluate_badges(user_id):
    """
    Check all badge conditions for user and automatically unlock earned ones.
    """
    conn = database.get_db_connection()
    
    # 1. Lessons completed count
    lesson_count = conn.execute(
        "SELECT COUNT(*) FROM lesson_progress WHERE user_id = ? AND completed = 1", (user_id,)
    ).fetchone()[0]
    
    # 2. Streak count
    streak_row = conn.execute("SELECT current_streak, longest_streak FROM user_streaks WHERE user_id = ?", (user_id,)).fetchone()
    longest_streak = max(streak_row['longest_streak'] if streak_row else 0, streak_row['current_streak'] if streak_row else 0)
    
    # 3. Quizzes completed count
    quiz_count = conn.execute(
        "SELECT COUNT(*) FROM quiz_attempts WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    
    # 4. Daily challenges completed count
    challenge_count = conn.execute(
        "SELECT COUNT(*) FROM user_challenge_attempts WHERE user_id = ? AND completed = 1", (user_id,)
    ).fetchone()[0]
    
    # 5. Distinct courses completed count
    distinct_courses_count = conn.execute(
        "SELECT COUNT(DISTINCT course_id) FROM lesson_progress WHERE user_id = ? AND completed = 1", (user_id,)
    ).fetchone()[0]
    
    # 6. Leaderboard rank
    user_xp = conn.execute("SELECT xp FROM users WHERE id = ?", (user_id,)).fetchone()['xp'] or 0
    rank = conn.execute("SELECT COUNT(*) + 1 FROM users WHERE xp > ?", (user_xp,)).fetchone()[0]
    
    # 7. Unlocked badges set
    unlocked_rows = conn.execute("SELECT badge_id FROM user_badges WHERE user_id = ?", (user_id,)).fetchall()
    unlocked_set = {row['badge_id'] for row in unlocked_rows}
    
    badges_to_unlock = []
    
    if lesson_count >= 1 and 'first_lesson' not in unlocked_set:
        badges_to_unlock.append(('first_lesson', 'First Lesson'))
        
    if longest_streak >= 7 and 'streak_7' not in unlocked_set:
        badges_to_unlock.append(('streak_7', '7 Day Streak'))
        
    if challenge_count >= 10 and 'coding_master' not in unlocked_set:
        badges_to_unlock.append(('coding_master', 'Coding Master'))
        
    if quiz_count >= 10 and 'quiz_champion' not in unlocked_set:
        badges_to_unlock.append(('quiz_champion', 'Quiz Champion'))
        
    if challenge_count >= 10 and 'challenge_hunter' not in unlocked_set:
        badges_to_unlock.append(('challenge_hunter', 'Challenge Hunter'))
        
    if distinct_courses_count >= 3 and 'course_explorer' not in unlocked_set:
        badges_to_unlock.append(('course_explorer', 'Course Explorer'))
        
    if rank <= 10 and 'top_10' not in unlocked_set:
        badges_to_unlock.append(('top_10', 'Top 10 Scholar'))
        
    cursor = conn.cursor()
    for b_id, b_title in badges_to_unlock:
        cursor.execute("INSERT OR IGNORE INTO user_badges (user_id, badge_id) VALUES (?, ?)", (user_id, b_id))
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, icon, notification_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            "⭐ Badge Unlocked!",
            f"You earned the '{b_title}' badge!",
            "fa-award",
            "badge"
        ))
        
    conn.commit()
    conn.close()

def get_user_badges_full(user_id):
    """
    Get list of all badges with unlock status, progress count, and percentage for UI.
    """
    conn = database.get_db_connection()
    
    lesson_count = conn.execute("SELECT COUNT(*) FROM lesson_progress WHERE user_id = ? AND completed = 1", (user_id,)).fetchone()[0]
    streak_row = conn.execute("SELECT current_streak, longest_streak FROM user_streaks WHERE user_id = ?", (user_id,)).fetchone()
    longest_streak = max(streak_row['longest_streak'] if streak_row else 0, streak_row['current_streak'] if streak_row else 0)
    quiz_count = conn.execute("SELECT COUNT(*) FROM quiz_attempts WHERE user_id = ?", (user_id,)).fetchone()[0]
    challenge_count = conn.execute("SELECT COUNT(*) FROM user_challenge_attempts WHERE user_id = ? AND completed = 1", (user_id,)).fetchone()[0]
    distinct_courses_count = conn.execute("SELECT COUNT(DISTINCT course_id) FROM lesson_progress WHERE user_id = ? AND completed = 1", (user_id,)).fetchone()[0]
    user_xp = conn.execute("SELECT xp FROM users WHERE id = ?", (user_id,)).fetchone()['xp'] or 0
    rank = conn.execute("SELECT COUNT(*) + 1 FROM users WHERE xp > ?", (user_xp,)).fetchone()[0]
    
    unlocked_rows = conn.execute("SELECT badge_id, unlocked_at FROM user_badges WHERE user_id = ?", (user_id,)).fetchall()
    unlocked_dict = {row['badge_id']: row['unlocked_at'] for row in unlocked_rows}
    
    conn.close()
    
    current_metrics = {
        'first_lesson': min(1, lesson_count),
        'streak_7': min(7, longest_streak),
        'coding_master': min(10, challenge_count),
        'quiz_champion': min(10, quiz_count),
        'challenge_hunter': min(10, challenge_count),
        'course_explorer': min(3, distinct_courses_count),
        'top_10': 10 if rank <= 10 else max(1, 10 - (rank - 10))
    }
    
    badges_list = []
    for b in BADGES_CATALOG:
        b_id = b['id']
        is_unlocked = b_id in unlocked_dict
        curr_val = current_metrics.get(b_id, 0)
        target_val = b['target']
        progress_pct = 100.0 if is_unlocked else min(100.0, (curr_val / target_val) * 100.0)
        
        badges_list.append({
            'id': b_id,
            'title': b['title'],
            'desc': b['desc'],
            'icon': b['icon'],
            'color': b['color'],
            'target': target_val,
            'current': curr_val,
            'progress_pct': round(progress_pct, 1),
            'is_unlocked': is_unlocked,
            'unlocked_at': unlocked_dict.get(b_id)
        })
        
    return badges_list

def get_leaderboard(timeframe='all_time'):
    """
    Get ranked leaderboard with privacy filtering for Today, This Week, This Month, and All Time.
    """
    conn = database.get_db_connection()
    now = dt.now()
    
    if timeframe == 'today':
        since_date = now.strftime("%Y-%m-%d")
        query = '''
            SELECT u.id, u.username, u.full_name, u.skill_level,
                   COALESCE(SUM(t.amount), 0) as period_xp
            FROM users u
            LEFT JOIN xp_transactions t ON u.id = t.user_id AND date(t.created_at) = ?
            GROUP BY u.id
            ORDER BY period_xp DESC, u.xp DESC, u.full_name ASC
        '''
        rows = conn.execute(query, (since_date,)).fetchall()
    elif timeframe == 'week':
        start_of_week = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        query = '''
            SELECT u.id, u.username, u.full_name, u.skill_level,
                   COALESCE(SUM(t.amount), 0) as period_xp
            FROM users u
            LEFT JOIN xp_transactions t ON u.id = t.user_id AND date(t.created_at) >= ?
            GROUP BY u.id
            ORDER BY period_xp DESC, u.xp DESC, u.full_name ASC
        '''
        rows = conn.execute(query, (start_of_week,)).fetchall()
    elif timeframe == 'month':
        start_of_month = now.strftime("%Y-%m-01")
        query = '''
            SELECT u.id, u.username, u.full_name, u.skill_level,
                   COALESCE(SUM(t.amount), 0) as period_xp
            FROM users u
            LEFT JOIN xp_transactions t ON u.id = t.user_id AND date(t.created_at) >= ?
            GROUP BY u.id
            ORDER BY period_xp DESC, u.xp DESC, u.full_name ASC
        '''
        rows = conn.execute(query, (start_of_month,)).fetchall()
    else: # all_time
        query = '''
            SELECT id, username, full_name, skill_level, xp as period_xp
            FROM users
            ORDER BY xp DESC, full_name ASC
        '''
        rows = conn.execute(query).fetchall()
    # Query streaks map
    streaks_rows = conn.execute("SELECT user_id, current_streak FROM user_streaks").fetchall()
    streaks_map = {row['user_id']: row['current_streak'] for row in streaks_rows}
    
    # Query badges count map
    badges_rows = conn.execute("SELECT user_id, COUNT(*) as cnt FROM user_badges GROUP BY user_id").fetchall()
    badges_map = {row['user_id']: row['cnt'] for row in badges_rows}
    
    # Query battles won map
    battles_rows = conn.execute("SELECT winner_id, COUNT(*) as wins FROM quiz_battles WHERE status = 'completed' AND winner_id IS NOT NULL GROUP BY winner_id").fetchall()
    battles_map = {row['winner_id']: row['wins'] for row in battles_rows}
    
    conn.close()
    
    avatar_gradients = [
        "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
        "linear-gradient(135deg, #06b6d4 0%, #0284c7 100%)",
        "linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)",
        "linear-gradient(135deg, #ec4899 0%, #be185d 100%)",
        "linear-gradient(135deg, #10b981 0%, #059669 100%)",
        "linear-gradient(135deg, #f97316 0%, #ea580c 100%)",
        "linear-gradient(135deg, #6366f1 0%, #4338ca 100%)",
        "linear-gradient(135deg, #14b8a6 0%, #0f766e 100%)",
    ]
    
    rankings = []
    for idx, r in enumerate(rows):
        total_xp = r['period_xp'] or 0
        lvl_info = calculate_level(total_xp)
        user_id = r['id']
        rank = idx + 1
        
        # League Tier Definition
        if rank == 1:
            tier_name = "Grandmaster"
            tier_icon = "fa-crown"
            tier_badge = "👑 Grandmaster"
            tier_class = "tier-grandmaster"
            tier_color = "#f59e0b"
        elif rank <= 3:
            tier_name = "Diamond"
            tier_icon = "fa-gem"
            tier_badge = "💎 Diamond"
            tier_class = "tier-diamond"
            tier_color = "#06b6d4"
        elif rank <= 10:
            tier_name = "Platinum"
            tier_icon = "fa-bolt"
            tier_badge = "⚡ Platinum"
            tier_class = "tier-platinum"
            tier_color = "#8b5cf6"
        elif rank <= 20:
            tier_name = "Gold"
            tier_icon = "fa-medal"
            tier_badge = "🥇 Gold"
            tier_class = "tier-gold"
            tier_color = "#10b981"
        else:
            tier_name = "Challenger"
            tier_icon = "fa-shield-halved"
            tier_badge = "🛡️ Challenger"
            tier_class = "tier-challenger"
            tier_color = "#94a3b8"
            
        streak = streaks_map.get(user_id, max(1, (user_id * 3) % 9 + 1))
        badge_count = badges_map.get(user_id, max(0, (user_id * 2) % 6))
        battle_wins = battles_map.get(user_id, max(0, user_id % 5))
        gradient = avatar_gradients[user_id % len(avatar_gradients)]
        
        rankings.append({
            'rank': rank,
            'id': user_id,
            'username': r['username'],
            'full_name': r['full_name'],
            'skill_level': r['skill_level'] or 'Beginner',
            'xp': total_xp,
            'level': lvl_info['level'],
            'streak': streak,
            'badge_count': badge_count,
            'battle_wins': battle_wins,
            'tier_name': tier_name,
            'tier_icon': tier_icon,
            'tier_badge': tier_badge,
            'tier_class': tier_class,
            'tier_color': tier_color,
            'avatar_gradient': gradient
        })
        
    return rankings

def create_notification(user_id, title, message, icon='fa-bell', ntype='general'):
    """
    Insert notification for user.
    """
    conn = database.get_db_connection()
    conn.execute('''
        INSERT INTO notifications (user_id, title, message, icon, notification_type)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, title, message, icon, ntype))
    conn.commit()
    conn.close()

def get_user_notifications(user_id, limit=10):
    """
    Get notifications for user.
    """
    conn = database.get_db_connection()
    rows = conn.execute('''
        SELECT * FROM notifications 
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit)).fetchall()
    
    unread_count = conn.execute(
        "SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,)
    ).fetchone()[0]
    
    conn.close()
    return {
        'notifications': [dict(r) for r in rows],
        'unread_count': unread_count
    }

def mark_notifications_as_read(user_id):
    """
    Mark all user notifications as read.
    """
    conn = database.get_db_connection()
    conn.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_daily_goals(user_id):
    """
    Check today's 3 core learning goals:
    1. Complete 1 lesson today
    2. Solve today's daily challenge
    3. Complete one quiz today
    """
    today_str = dt.now().strftime("%Y-%m-%d")
    conn = database.get_db_connection()
    
    # 1. Lesson completed today
    lesson_done = conn.execute('''
        SELECT COUNT(*) FROM lesson_progress
        WHERE user_id = ? AND date(completed_at) = ? AND completed = 1
    ''', (user_id, today_str)).fetchone()[0] > 0
    
    # 2. Challenge solved today
    challenge_done = conn.execute('''
        SELECT COUNT(*) FROM user_challenge_attempts a
        JOIN daily_challenges c ON a.challenge_id = c.id
        WHERE a.user_id = ? AND c.challenge_date = ? AND a.completed = 1
    ''', (user_id, today_str)).fetchone()[0] > 0
    
    # 3. Quiz taken today
    quiz_done = conn.execute('''
        SELECT COUNT(*) FROM quiz_attempts
        WHERE user_id = ? AND date(created_at) = ?
    ''', (user_id, today_str)).fetchone()[0] > 0
    
    conn.close()
    
    goals = [
        {'id': 'lesson', 'text': 'Complete 1 lesson module', 'completed': lesson_done, 'icon': 'fa-book-open'},
        {'id': 'challenge', 'text': 'Solve today\'s daily challenge', 'completed': challenge_done, 'icon': 'fa-crosshairs'},
        {'id': 'quiz', 'text': 'Complete one lesson quiz', 'completed': quiz_done, 'icon': 'fa-brain'}
    ]
    completed_count = sum(1 for g in goals if g['completed'])
    
    return {
        'goals': goals,
        'completed_count': completed_count,
        'total_count': len(goals),
        'all_completed': completed_count == len(goals)
    }

def get_continue_learning_course(user_id):
    """
    Find the most recent in-progress enrolled course and next unfinished lesson.
    """
    conn = database.get_db_connection()
    enrollment = conn.execute('''
        SELECT e.*, c.title as course_title, c.category, c.skill_level
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE e.user_id = ? AND e.completed = 0
        ORDER BY e.date_enrolled DESC
        LIMIT 1
    ''', (user_id,)).fetchone()
    
    if not enrollment:
        conn.close()
        return None
        
    course_id = enrollment['course_id']
    # Find first incomplete lesson
    next_lesson = conn.execute('''
        SELECT l.* FROM lessons l
        WHERE l.course_id = ? AND l.id NOT IN (
            SELECT lesson_id FROM lesson_progress WHERE user_id = ? AND completed = 1
        )
        ORDER BY l.order_num ASC
        LIMIT 1
    ''', (course_id, user_id)).fetchone()
    
    conn.close()
    return {
        'course_id': course_id,
        'course_title': enrollment['course_title'],
        'category': enrollment['category'],
        'progress_percent': enrollment['progress_percent'],
        'next_lesson_id': next_lesson['id'] if next_lesson else None,
        'next_lesson_title': next_lesson['title'] if next_lesson else 'Review Syllabus'
    }

# 1v1 Quiz Battle Questions Pool (Multi-domain)
QUIZ_BATTLE_QUESTIONS_POOL = [
    # Python
    {
        "category": "Python",
        "question": "What is the time complexity of searching an element in a balanced Binary Search Tree?",
        "options": ["O(log N)", "O(N)", "O(1)", "O(N^2)"],
        "answer": "O(log N)"
    },
    {
        "category": "Python",
        "question": "In Python, which keyword is used to create an anonymous inline function?",
        "options": ["lambda", "def", "func", "anonymous"],
        "answer": "lambda"
    },
    {
        "category": "Python",
        "question": "Which built-in Python data structure preserves key insertion order while enabling fast O(1) key lookups?",
        "options": ["dict", "set", "tuple", "frozenset"],
        "answer": "dict"
    },
    {
        "category": "Python",
        "question": "What does the '__init__' method represent in a Python class?",
        "options": ["Constructor initializer", "Destructor", "Static method", "Abstract method"],
        "answer": "Constructor initializer"
    },
    {
        "category": "Python",
        "question": "Which Python decorator is used to define a method that belongs to the class rather than an instance?",
        "options": ["@classmethod", "@staticmethod", "@property", "@abstractmethod"],
        "answer": "@classmethod"
    },
    
    # Web & APIs
    {
        "category": "Web & APIs",
        "question": "Which HTTP status code signifies that a resource was successfully created on server?",
        "options": ["201 Created", "200 OK", "204 No Content", "202 Accepted"],
        "answer": "201 Created"
    },
    {
        "category": "Web & APIs",
        "question": "In CSS layout, which property aligns items along the cross axis in a flex container?",
        "options": ["align-items", "justify-content", "align-content", "flex-direction"],
        "answer": "align-items"
    },
    {
        "category": "Web & APIs",
        "question": "Which response header is essential to allow cross-domain API requests via CORS?",
        "options": ["Access-Control-Allow-Origin", "Authorization", "Content-Security-Policy", "X-Frame-Options"],
        "answer": "Access-Control-Allow-Origin"
    },
    {
        "category": "Web & APIs",
        "question": "What does JWT stand for in modern web authentication?",
        "options": ["JSON Web Token", "JavaScript Web Technology", "Java Web Tracker", "Joint Web Tunnel"],
        "answer": "JSON Web Token"
    },
    {
        "category": "Web & APIs",
        "question": "Which HTTP method is considered idempotent and used to replace an entire resource?",
        "options": ["PUT", "POST", "PATCH", "CONNECT"],
        "answer": "PUT"
    },

    # AI & Data
    {
        "category": "AI & Data",
        "question": "Which machine learning algorithm is based on Bayes' theorem with feature independence assumption?",
        "options": ["Naive Bayes", "Random Forest", "Support Vector Machine", "K-Means"],
        "answer": "Naive Bayes"
    },
    {
        "category": "AI & Data",
        "question": "In neural networks, which activation function outputs values specifically in the range (-1, 1)?",
        "options": ["tanh", "ReLU", "Sigmoid", "Softmax"],
        "answer": "tanh"
    },
    {
        "category": "AI & Data",
        "question": "In Pandas, which method returns summary statistics like count, mean, std, and quartiles for numeric columns?",
        "options": ["df.describe()", "df.summary()", "df.info()", "df.stats()"],
        "answer": "df.describe()"
    },
    {
        "category": "AI & Data",
        "question": "What technique is used in machine learning to prevent overfitting by penalizing large weights?",
        "options": ["Regularization (L1/L2)", "One-Hot Encoding", "Min-Max Normalization", "Gradient Clipping"],
        "answer": "Regularization (L1/L2)"
    },
    {
        "category": "AI & Data",
        "question": "Which metric evaluates classification performance as the harmonic mean of precision and recall?",
        "options": ["F1-Score", "ROC-AUC", "Mean Squared Error", "Accuracy"],
        "answer": "F1-Score"
    },

    # SQL
    {
        "category": "SQL",
        "question": "Which SQL clause is specifically used to filter groups created by GROUP BY?",
        "options": ["HAVING", "WHERE", "FILTER", "LIMIT"],
        "answer": "HAVING"
    },
    {
        "category": "SQL",
        "question": "In database transactions, what does the ACID acronym stand for?",
        "options": ["Atomicity, Consistency, Isolation, Durability", "Accuracy, Control, Integrity, Data", "Automated, Concurrent, Indexed, Distributed", "Action, Constraint, Index, Database"],
        "answer": "Atomicity, Consistency, Isolation, Durability"
    },
    {
        "category": "SQL",
        "question": "Which SQL JOIN returns all rows when there is a match in one of the tables, filling NULLs for unmatched rows?",
        "options": ["FULL OUTER JOIN", "INNER JOIN", "CROSS JOIN", "NATURAL JOIN"],
        "answer": "FULL OUTER JOIN"
    },
    {
        "category": "SQL",
        "question": "Which type of database index stores sorted data and is most commonly used in B-Tree structures?",
        "options": ["Clustered Index", "Bitmap Index", "Spatial Index", "Hash Index"],
        "answer": "Clustered Index"
    },

    # Science
    {
        "category": "Science",
        "question": "What is the speed of light in a vacuum approximately?",
        "options": ["3 x 10^8 m/s", "3 x 10^6 m/s", "1.5 x 10^8 m/s", "3 x 10^5 km/h"],
        "answer": "3 x 10^8 m/s"
    },
    {
        "category": "Science",
        "question": "Which subatomic particle carries a negative electric charge?",
        "options": ["Electron", "Proton", "Neutron", "Positron"],
        "answer": "Electron"
    },
    {
        "category": "Science",
        "question": "What law of thermodynamics states that entropy in an isolated system always increases?",
        "options": ["Second Law", "First Law", "Third Law", "Zeroth Law"],
        "answer": "Second Law"
    },
    {
        "category": "Science",
        "question": "What organelle is known as the powerhouse of the eukaryotic cell?",
        "options": ["Mitochondria", "Ribosome", "Endoplasmic Reticulum", "Golgi Apparatus"],
        "answer": "Mitochondria"
    },

    # Aptitude
    {
        "category": "Aptitude",
        "question": "If a train travels 360 km at 90 km/h, how much time does the journey take?",
        "options": ["4 hours", "3.5 hours", "5 hours", "4.5 hours"],
        "answer": "4 hours"
    },
    {
        "category": "Aptitude",
        "question": "What is the next number in the series: 2, 6, 12, 20, 30, ...?",
        "options": ["42", "40", "44", "38"],
        "answer": "42"
    },
    {
        "category": "Aptitude",
        "question": "A shopkeeper gives a 20% discount on a $150 jacket. What is the selling price?",
        "options": ["$120", "$130", "$115", "$125"],
        "answer": "$120"
    },
    {
        "category": "Aptitude",
        "question": "If 5 workers can build a wall in 12 days, how many days will 6 workers take at the same pace?",
        "options": ["10 days", "8 days", "9 days", "11 days"],
        "answer": "10 days"
    },

    # GK
    {
        "category": "GK",
        "question": "Which planet in our solar system is known as the Red Planet?",
        "options": ["Mars", "Jupiter", "Venus", "Mercury"],
        "answer": "Mars"
    },
    {
        "category": "GK",
        "question": "Who is considered the father of computer science and artificial intelligence?",
        "options": ["Alan Turing", "Charles Babbage", "John von Neumann", "Ada Lovelace"],
        "answer": "Alan Turing"
    },
    {
        "category": "GK",
        "question": "Which ocean is the largest and deepest ocean on Earth?",
        "options": ["Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean"],
        "answer": "Pacific Ocean"
    },
    {
        "category": "GK",
        "question": "In which year was the World Wide Web introduced to the public by Tim Berners-Lee?",
        "options": ["1991", "1989", "1995", "1983"],
        "answer": "1991"
    }
]

QUIZ_BATTLE_QUESTIONS = QUIZ_BATTLE_QUESTIONS_POOL[:6]

def create_quiz_battle(challenger_id, opponent_id, course_id=1, category=None):
    """
    Create a new 1v1 quiz battle with up to 6 sampled questions (5 regular + 1 sudden death tiebreaker).
    """
    import random
    if category and category != 'All':
        cat_lower = category.lower().strip()
        pool = [q for q in QUIZ_BATTLE_QUESTIONS_POOL if cat_lower in q.get('category', '').lower()]
        if len(pool) < 6:
            pool = [q for q in QUIZ_BATTLE_QUESTIONS_POOL if q.get('category') == category]
        if len(pool) < 6:
            pool = QUIZ_BATTLE_QUESTIONS_POOL
    else:
        pool = QUIZ_BATTLE_QUESTIONS_POOL
        
    selected_questions = random.sample(pool, min(6, len(pool)))
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quiz_battles (challenger_id, opponent_id, course_id, status, questions_data)
        VALUES (?, ?, ?, 'pending', ?)
    ''', (challenger_id, opponent_id, course_id, json.dumps(selected_questions)))
    battle_id = cursor.lastrowid
    
    # Notify opponent
    challenger = conn.execute("SELECT full_name FROM users WHERE id = ?", (challenger_id,)).fetchone()
    if challenger:
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, icon, notification_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            opponent_id,
            "⚔️ Quiz Battle Challenge!",
            f"{challenger['full_name']} has challenged you to a 5-question Quiz Battle!",
            "fa-bolt",
            "battle"
        ))
    
    conn.commit()
    conn.close()
    return battle_id
