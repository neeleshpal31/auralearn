import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'elearning.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            skill_level TEXT,
            learning_goals TEXT,
            interests TEXT,
            onboarded INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0
        )
    ''')
    
    # 2. Create Courses Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            tags TEXT NOT NULL,
            skill_level TEXT NOT NULL,
            duration TEXT NOT NULL,
            rating REAL DEFAULT 0.0,
            enrolled_count INTEGER DEFAULT 0
        )
    ''')
    
    # 3. Create Lessons Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            order_num INTEGER NOT NULL,
            duration TEXT,
            content TEXT,
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
        )
    ''')
    
    # 4. Create Enrollments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            progress_percent REAL DEFAULT 0.0,
            date_enrolled TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
            UNIQUE(user_id, course_id)
        )
    ''')
    
    # 5. Create Lesson Progress Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lesson_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
            FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE,
            UNIQUE(user_id, lesson_id)
        )
    ''')
    
    # 6. Create Ratings / Reviews Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            review_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
            UNIQUE(user_id, course_id)
        )
    ''')
    
    # 7. Create Study Notes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            lesson_id INTEGER UNIQUE NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
            FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE
        )
    ''')

    # 8. Create XP Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS xp_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            reference_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # 9. Create User Streaks Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_streaks (
            user_id INTEGER PRIMARY KEY,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_active_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # 10. Create Daily Challenges Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_date TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            time_estimate TEXT NOT NULL,
            xp_reward INTEGER DEFAULT 20,
            challenge_type TEXT NOT NULL,
            question_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 11. Create User Challenge Attempts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_challenge_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            completed INTEGER DEFAULT 1,
            submitted_answer TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (challenge_id) REFERENCES daily_challenges (id) ON DELETE CASCADE,
            UNIQUE(user_id, challenge_id)
        )
    ''')

    # 12. Create Module Discussions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
            FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # 13. Create Discussion Replies Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discussion_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discussion_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (discussion_id) REFERENCES discussions (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # 14. Create Discussion Likes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discussion_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discussion_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (discussion_id) REFERENCES discussions (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(discussion_id, user_id)
        )
    ''')

    # 15. Create User Badges Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            badge_id TEXT NOT NULL,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, badge_id)
        )
    ''')

    # 16. Create Quiz Attempts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            xp_earned INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
            FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE,
            UNIQUE(user_id, lesson_id)
        )
    ''')

    # 17. Create In-App Notifications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            icon TEXT DEFAULT 'fa-bell',
            notification_type TEXT DEFAULT 'general',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # 18. Create Quiz Battles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_battles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenger_id INTEGER NOT NULL,
            opponent_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            challenger_score INTEGER DEFAULT 0,
            opponent_score INTEGER DEFAULT 0,
            winner_id INTEGER,
            questions_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (challenger_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (opponent_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
        )
    ''')

    # 19. Create Certificates Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            exam_score INTEGER NOT NULL,
            total_score INTEGER DEFAULT 100,
            grade TEXT NOT NULL,
            certificate_code TEXT UNIQUE NOT NULL,
            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
            UNIQUE(user_id, course_id)
        )
    ''')

    # 20. Create Exam Attempts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            passed INTEGER DEFAULT 0,
            security_violations INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
        )
    ''')
    
    # Safe migrations for lesson_progress
    try:
        cursor.execute("ALTER TABLE lesson_progress ADD COLUMN audio_completed INTEGER DEFAULT 0")
    except Exception:
        pass

    conn.commit()
    conn.close()

def seed_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if courses are already seeded
    cursor.execute("SELECT COUNT(*) FROM courses")
    if cursor.fetchone()[0] > 0:
        print("Database already contains data. Seeding skipped.")
        conn.close()
        return

    print("Seeding database with realistic courses, lessons, and mock users...")
    
    # 1. Insert Courses
    courses_data = [
        # Programming & Web Dev (7 courses)
        ("Python Programming for Beginners", "Learn the fundamentals of Python programming language. Build games, automate tasks, and write your first scripts from scratch.", "Programming", "Python,Programming,Fundamentals", "Beginner", "10 hours"),
        ("Intermediate Python and OOP Concepts", "Elevate your Python skills by mastering Object-Oriented Programming (OOP), decorators, generators, and packaging.", "Programming", "Python,Programming,OOP,Advanced Python", "Intermediate", "12 hours"),
        ("Modern Full-Stack JavaScript with Node.js", "Master JavaScript from frontend to backend. Learn modern ES6+, Node.js, Express, and DOM manipulation to construct applications.", "Web Development", "JavaScript,Node.js,Express,Full-Stack", "Intermediate", "16 hours"),
        ("HTML5 and CSS3: Building Responsive Web Designs", "Understand modern HTML5 structures and CSS3 layouts like Flexbox and Grid. Build beautiful, high-quality responsive websites.", "Web Development", "HTML,CSS,Responsive Design,Frontend", "Beginner", "8 hours"),
        ("React.js: Build Production-Ready Interfaces", "Deep dive into component architecture, state management (hooks), routers, and custom styling to build robust frontend web apps.", "Web Development", "React,JavaScript,Frontend,Web Apps", "Intermediate", "14 hours"),
        ("Advanced SQL for Databases and Data Analysis", "Master complex queries, subqueries, CTEs, indexes, window functions, and database performance tuning for scalable databases.", "Programming", "SQL,Database,Analytics,Backend", "Advanced", "9 hours"),
        ("Building RESTful APIs with Flask and Python", "Learn how to build, document, and deploy production-grade REST APIs using Python, Flask, and Flask-RESTful.", "Web Development", "Flask,Python,API,Backend", "Intermediate", "10 hours"),
        
        # AI & Machine Learning (5 courses)
        ("Introduction to Machine Learning with Scikit-Learn", "Learn supervised and unsupervised learning algorithms including linear regression, decision trees, and clustering using Python.", "Data Science & AI", "Python,Machine Learning,Data Science,Scikit-Learn", "Beginner", "15 hours"),
        ("Deep Learning and Neural Networks with PyTorch", "Understand neural network structures, backpropagation, and build custom convolutional and recurrent networks using PyTorch.", "Data Science & AI", "Deep Learning,PyTorch,AI,Neural Networks", "Advanced", "18 hours"),
        ("Data Analysis and Visualization with Pandas", "Clean, manipulate, and explore data. Build beautiful dynamic charts using Pandas, NumPy, Matplotlib, and Seaborn in Jupyter notebooks.", "Data Science & AI", "Python,Data Analysis,Pandas,Visualization", "Intermediate", "8 hours"),
        ("Natural Language Processing (NLP) in Python", "Process text, perform sentiment analysis, build text classification models, and explore modern LLMs using NLTK and Spacy.", "Data Science & AI", "NLP,Python,AI,Data Science", "Advanced", "12 hours"),
        ("Prompt Engineering for AI Applications", "Master prompt patterns, system prompts, few-shot prompting, and safety filters for ChatGPT, Claude, and Gemini API integration.", "Data Science & AI", "AI,Prompt Engineering,Generative AI", "Beginner", "6 hours"),
        
        # UX/UI & Design (4 courses)
        ("Introduction to UX/UI Design Principles", "Learn color theory, typography, spacing, visual hierarchies, and user research principles to design stunning software interfaces.", "Design", "UX,UI,Figma,Design System", "Beginner", "8 hours"),
        ("Figma Mastery: High-Fidelity Prototyping", "Design reusable components, auto-layouts, variants, and interactive prototypes to create clickable, animations-rich mockups.", "Design", "Figma,UI,Design,Prototyping", "Intermediate", "10 hours"),
        ("Mobile App Design and Micro-Interactions", "Understand mobile design paradigms, navigation flows, touch patterns, and how subtle micro-animations enhance user experience.", "Design", "Design,Mobile,UX,Micro-interactions", "Intermediate", "7 hours"),
        ("Design Systems: Scale UI across Teams", "Build robust tokenized design systems in Figma, bridging the gap between design specs and atomic code implementation.", "Design", "Design System,UX,UI,Scale", "Advanced", "12 hours"),

        # Business & Management (4 courses)
        ("Agile and Scrum Product Management", "Learn backlog grooming, sprint planning, writing user stories, and managing teams using Jira and Scrum frameworks.", "Business", "Agile,Scrum,Product Management,Jira", "Beginner", "6 hours"),
        ("Product Marketing Strategy and Analytics", "Understand go-to-market strategies, customer acquisition channels, metrics tracking, conversion funnels, and A/B testing.", "Business", "Marketing,Product,Analytics,Growth", "Intermediate", "9 hours"),
        ("Startup Essentials: Concept to Launch", "Learn validation techniques, market sizing, financial modeling, pitching to VCs, and agile startup execution practices.", "Business", "Startup,Business,Entrepreneurship,Finance", "Beginner", "10 hours"),
        ("Financial Modeling and Excel for Decision Making", "Master advanced Excel formulas, pivot tables, building financial forecast charts, and preparing capital tables for investors.", "Business", "Excel,Finance,Business,Modeling", "Intermediate", "11 hours")
    ]
    
    for title, desc, category, tags, skill_level, duration in courses_data:
        cursor.execute('''
            INSERT INTO courses (title, description, category, tags, skill_level, duration, rating, enrolled_count)
            VALUES (?, ?, ?, ?, ?, ?, 0.0, 0)
        ''', (title, desc, category, tags, skill_level, duration))
        
    # Get inserted course IDs
    cursor.execute("SELECT id, title FROM courses")
    courses = cursor.fetchall()
    
    # 2. Insert Lessons for each course (Custom Syllabus details)
    custom_syllabus = {
        "Python Programming for Beginners": [
            ("Introduction to Python and Setup", "1.5 hours", "Setting up Python, VS Code, and running your first print statement."),
            ("Variables, Data Types, and Operators", "2 hours", "Understanding integers, floats, strings, booleans, and mathematical operators."),
            ("Control Flow: If Conditions and Loops", "2 hours", "Mastering if-else statements, while loops, and for loops with range."),
            ("Functions and Scope", "2 hours", "Defining functions, parameters, return values, and global vs local variables."),
            ("Working with Lists and Dictionaries", "1.5 hours", "Using Python lists, tuples, dictionaries, and set operations."),
            ("Final Project: Calculator & Guessing Game", "1 hour", "Putting it all together to build a terminal game and basic utility.")
        ],
        "Intermediate Python and OOP Concepts": [
            ("Object-Oriented Programming (OOP) Fundamentals", "2.5 hours", "Understanding Classes, Objects, attributes, and methods in Python."),
            ("Inheritance, Polymorphism, and Encapsulation", "2.5 hours", "Extending classes, writing magic methods, and variable privacy."),
            ("Advanced Functions: Decorators & Generators", "2.5 hours", "Writing decorators, understanding closures, and using yield generators."),
            ("File Handling & Error Exception Blocks", "2 hours", "Working with files, try-except-finally blocks, and custom exceptions."),
            ("Iterators and Context Managers", "1.5 hours", "Creating custom iterators and using the with statement context managers."),
            ("Packaging and Virtual Environments", "1 hour", "Setting up pip, venv, and creating a distributable Python package.")
        ],
        "Modern Full-Stack JavaScript with Node.js": [
            ("Modern JS: ES6+ Syntax & Features", "2.5 hours", "Arrow functions, destructuring, template literals, and spread operators."),
            ("Asynchronous JavaScript & Promises", "3 hours", "Understanding event loop, callbacks, Promises, and Async/Await."),
            ("DOM Manipulation & Web API Fetch", "2.5 hours", "Interacting with page elements and loading external API data."),
            ("Introduction to Node.js & Express Basics", "3 hours", "Creating a local backend server, routing, and HTTP methods."),
            ("Middleware and Database Integration", "3 hours", "Adding middleware, handling form data, and reading database files."),
            ("Deployment to Production", "2 hours", "Hosting static frontend pages and deploying Node app to cloud systems.")
        ],
        "HTML5 and CSS3: Building Responsive Web Designs": [
            ("HTML5 Semantic Structure", "1.5 hours", "Using header, nav, section, article, and footer elements correctly."),
            ("CSS3 Box Model & Layout Basics", "1.5 hours", "Understanding margins, padding, borders, display, and positioning."),
            ("Flexbox: Flexible Box Layouts", "1.5 hours", "Mastering flex container, directions, alignments, and sizing."),
            ("CSS Grid: Custom Page Layouts", "1.5 hours", "Creating columns, rows, grid areas, and gap properties."),
            ("Responsive Web Design & Media Queries", "1.5 hours", "Writing mobile-first CSS styling rules using breakpoints."),
            ("Final Project: Responsive landing page", "0.5 hours", "Creating a fully responsive corporate website layout.")
        ],
        "React.js: Build Production-Ready Interfaces": [
            ("React Core: JSX & Components", "2 hours", "Writing components, rendering JSX, and using props."),
            ("State Management with useState Hooks", "2.5 hours", "Handling user actions, form inputs, and state updates."),
            ("Side Effects with useEffect hook", "2.5 hours", "Fetching API data and synchronizing component lifecycles."),
            ("Custom Hooks & Context API", "2.5 hours", "Sharing global user states and writing custom hooks."),
            ("Routing with React Router Dom", "2.5 hours", "Setting up multiple pages and dynamic URL parameters."),
            ("Performance & Code Splitting", "2 hours", "Using React.lazy, memoization hooks, and optimizing bundle sizes.")
        ],
        "Advanced SQL for Databases and Data Analysis": [
            ("Advanced Joins and Subqueries", "1.5 hours", "Using self joins, cross joins, and nested subqueries in SQL."),
            ("Common Table Expressions (CTEs)", "1.5 hours", "Writing cleaner queries using WITH clauses and recursive CTEs."),
            ("Window Functions for Analytics", "2 hours", "Using ROW_NUMBER, RANK, DENSE_RANK, and running aggregates."),
            ("Indexes and Query Optimization", "1.5 hours", "Understanding index types, execution plans, and query speedups."),
            ("Database Schema Design & Normalization", "1.5 hours", "Creating tables, primary/foreign keys, and 1NF, 2NF, 3NF design."),
            ("Stored Procedures and Triggers", "1 hour", "Writing reusable database routines and automated actions.")
        ],
        "Building RESTful APIs with Flask and Python": [
            ("Flask Routing and HTTP Methods", "2 hours", "Handling requests, dynamic URL routing, and returning JSON."),
            ("Request Parsing and Serialization", "2 hours", "Extracting POST JSON parameters, data validation, and structures."),
            ("ORM and Database with Flask-SQLAlchemy", "2 hours", "Interfacing SQLite with objects, models, and migrations."),
            ("User Authentication with JWT Tokens", "2 hours", "Implementing signup, login, password encryption, and authorization headers."),
            ("API Documentation with Swagger/OpenAPI", "1 hour", "Documenting route endpoints and formats."),
            ("Unit Testing & Deployment", "1 hour", "Writing pytest cases for endpoints and hosting on Render.")
        ],
        "Introduction to Machine Learning with Scikit-Learn": [
            ("Supervised Learning: Linear Regression", "3 hours", "Core mathematical equations, modeling, and fitting with scikit-learn."),
            ("Classification: Logistic Regression & SVM", "3 hours", "Predicting binary outcomes, decision boundaries, and support vectors."),
            ("Decision Trees & Random Forests", "3 hours", "Understanding tree nodes, splitting indices, and ensemble methods."),
            ("Unsupervised Learning: KMeans Clustering", "2.5 hours", "Finding patterns, clusters, and dimensions in data without labels."),
            ("Model Evaluation & Hyperparameter Tuning", "2 hours", "Using cross-validation, grid search, and confusion matrix indicators."),
            ("Feature Engineering & Pipelines", "1.5 hours", "Scaling data, transforming categories, and constructing pipelines.")
        ],
        "Deep Learning and Neural Networks with PyTorch": [
            ("Tensors & PyTorch Autograd Engine", "3 hours", "Setting up torch tensors, GPU arrays, and backpropagation gradients."),
            ("Building a Simple Multi-Layer Perceptron", "3 hours", "Designing feed-forward layers, activation functions, and optimizer loops."),
            ("Convolutional Neural Networks (CNNs) for Images", "4 hours", "Applying convolutions, pooling, and training image classifiers."),
            ("Recurrent Neural Networks (RNNs) for Sequences", "3 hours", "Processing timeseries data and text using LSTM cells."),
            ("Transfer Learning & Pretrained Models", "3 hours", "Finetuning ResNet and custom models for custom datasets."),
            ("Model Saving and ONNX Export", "2 hours", "Saving weights and converting to formats for backend deployment.")
        ],
        "Data Analysis and Visualization with Pandas": [
            ("Pandas Series & DataFrames", "1.5 hours", "Creating series, indexing columns, and reading CSV files."),
            ("Data Cleaning: Missing Values & Outliers", "1.5 hours", "Handling nulls, filling defaults, and casting data types."),
            ("Filtering & Grouping Operations", "1.5 hours", "Performing groupbys, pivots, and cross-tabulations."),
            ("Merging and Joining DataFrames", "1.5 hours", "Combining tables using inner, outer, left, and right joins."),
            ("Plotting with Matplotlib & Seaborn", "1.5 hours", "Creating line plots, bar charts, scatterplots, and heatmaps."),
            ("Exporting Reports and Notebooks", "0.5 hours", "Saving clean datasets to Excel, SQL, and sharing Jupyter notebooks.")
        ],
        "Natural Language Processing (NLP) in Python": [
            ("Text Preprocessing & Tokenization", "2 hours", "Cleaning HTML, stopword removal, stemming, and lemmatization."),
            ("Bag of Words & TF-IDF Vectorization", "2 hours", "Representing text document matrices numerically for models."),
            ("Word Embeddings: Word2Vec & GloVe", "2.5 hours", "Capturing semantic word relationships in vector spaces."),
            ("Sentiment Analysis & Text Classification", "2.5 hours", "Building sentiment classifiers using scikit-learn classifiers."),
            ("Sequence Modeling with Transformers", "2 hours", "Understanding self-attention mechanisms and HuggingFace models."),
            ("Fine-tuning BERT for Custom NLP Tasks", "1 hour", "Adapting pretrained BERT for specific document classification.")
        ],
        "Prompt Engineering for AI Applications": [
            ("Foundations of LLMs & System Prompts", "1 hour", "Understanding temperature, tokens, and roles (System, User, Assistant)."),
            ("Zero-Shot and Few-Shot Prompting", "1 hour", "Guiding models with zero examples vs. listing dynamic inputs."),
            ("Chain of Thought (CoT) Prompting", "1 hour", "Forcing reasoning steps to improve logical task outputs."),
            ("Handling Formats: JSON & Structured Returns", "1 hour", "Extracting schemas and validating API outputs."),
            ("Prompt Hacking, Injection & Mitigations", "1 hour", "Securing LLM applications from malicious prompt inputs."),
            ("Building a Simple RAG Chatbot", "1 hour", "Combining search contexts with prompts to answer questions.")
        ],
        "Introduction to UX/UI Design Principles": [
            ("UX Research: Personas & Journeys", "1.5 hours", "Conducting interviews, defining personas, and map flows."),
            ("Information Architecture & Wireframing", "1.5 hours", "Structuring site maps and sketching low-fidelity screens."),
            ("Color Theory & Spacing Systems", "1.5 hours", "Selecting palettes, contrast ratios, and grid structures."),
            ("Typography & Hierarchies", "1.5 hours", "Choosing font pairings, font weights, and layout headings."),
            ("Accessibility: Web Content Guidelines", "1 hour", "Ensuring designs are accessible to color-blind and screen-reader users."),
            ("Testing UI designs with Real Users", "1 hour", "Running usability testing and iterating on layout flaws.")
        ],
        "Figma Mastery: High-Fidelity Prototyping": [
            ("Figma Interfaces & Vector Networks", "1.5 hours", "Navigating layers, shapes, frames, and drawing paths."),
            ("Auto Layout & Responsive Components", "2 hours", "Designing buttons, cards, and headers that resize automatically."),
            ("Variants and Component Sets", "2 hours", "Creating state variants like hover, active, disabled, and focus."),
            ("Advanced Prototyping & Smart Animate", "2 hours", "Creating slide-ins, morph animations, and dynamic overlays."),
            ("Interactive Variables and Logic", "1.5 hours", "Using Figma variables to store counts, item lists, and states."),
            ("Exporting Specs & Developer Handout", "1 hour", "Preparing redlines, sharing assets, and utilizing Dev Mode.")
        ],
        "Mobile App Design and Micro-Interactions": [
            ("iOS vs. Android Design Paradigms", "1.5 hours", "Comparing navigation bars, tab bars, and material styling."),
            ("Designing Custom Mobile Navigation Flows", "1.5 hours", "Creating bottom tab bars, drawer menus, and modal views."),
            ("Micro-Interactions: Triggers and Rules", "1.5 hours", "Defining how buttons bounce, toggles switch, and items scale."),
            ("Lottie Animations and Vector Assets", "1 hour", "Importing lightweight animations into Figma and code projects."),
            ("Designing Mobile App Store Screens", "1 hour", "Creating preview screens, screenshots, and visual branding assets."),
            ("Mobile Usability Checklists", "0.5 hours", "Verifying tap targets, readability on devices, and layout constraints.")
        ],
        "Design Systems: Scale UI across Teams": [
            ("Atomic Design Principles", "2 hours", "Structuring components into atoms, molecules, organisms, and pages."),
            ("Design Tokens & Variable Mappings", "2 hours", "Defining names for colors, spacing, and sizing variables."),
            ("Creating a Component Library in Figma", "2 hours", "Designing a unified system library of inputs, buttons, and dialogs."),
            ("Mapping Figma Assets to CSS/React Code", "2.5 hours", "Ensuring names match code constants and styles."),
            ("Documenting Components & Guidelines", "2 hours", "Writing usage instructions, rules, and best practices."),
            ("Design System Maintenance and Versioning", "1.5 hours", "Publishing updates and handling breaking changes safely.")
        ],
        "Agile and Scrum Product Management": [
            ("The Scrum Values and Roles", "1 hour", "Defining roles of Product Owner, Scrum Master, and Developers."),
            ("Writing Effective User Stories", "1 hour", "Defining user value, acceptance criteria, and INVEST checkmarks."),
            ("Backlog Prioritization Methods", "1 hour", "Using MoSCoW, RICE, and value vs. effort matrixes."),
            ("Sprint Planning & Estimation", "1 hour", "Running story pointing sessions, sprint planning, and target tracking."),
            ("Daily Scrum, Reviews, and Retros", "1 hour", "Structuring effective check-ins, demos, and retro items."),
            ("Tracking Progress with Burndowns", "1 hour", "Measuring velocity, using Jira reports, and identifying blockers.")
        ],
        "Product Marketing Strategy and Analytics": [
            ("Customer Segmentation & Persona Alignment", "1.5 hours", "Defining target audiences and unique value propositions."),
            ("Go-to-Market (GTM) Launch Blueprints", "1.5 hours", "Drafting launch timelines, launch assets, and messaging matrices."),
            ("Growth Marketing Funnels: AARRR framework", "1.5 hours", "Optimizing Acquisition, Activation, Retention, Referral, Revenue."),
            ("A/B Testing Campaigns & Layouts", "1.5 hours", "Formulating hypotheses, selecting sample size, and reviewing results."),
            ("Tracking Conversion and Funnel Drops", "1.5 hours", "Using Google Analytics and Mixpanel to map screen exits."),
            ("Final Project: GTM Strategy Deck", "1.5 hours", "Preparing a launch plan presentation for stakeholders.")
        ],
        "Startup Essentials: Concept to Launch": [
            ("Problem Validation & Customer Discovery", "1.5 hours", "Running interviews, verifying problems, and mapping user pain points."),
            ("Minimum Viable Product (MVP) Blueprints", "2 hours", "Designing simple, functional MVPs using no-code tools."),
            ("Market Sizing: TAM, SAM, SOM", "1.5 hours", "Calculating addressable market sizes and target audiences."),
            ("Startup Business Models & Unit Economics", "2 hours", "Analyzing SaaS subscriptions, transaction fees, and cost per acquisition."),
            ("Pitch Deck & VC Storytelling Frameworks", "1.5 hours", "Writing slides for problem, solution, market size, and financials."),
            ("Agile Growth & Early Sales Funnels", "1.5 hours", "Finding your first 100 customers and scaling early sales.")
        ],
        "Financial Modeling and Excel for Decision Making": [
            ("Excel Foundations: Formulas & Shortcuts", "2 hours", "Using index-match, vlookup, xlookup, and structural formatting."),
            ("Pivot Tables & Dynamic Dashboarding", "2 hours", "Summarizing datasets, charts, and slicers in Excel dashboards."),
            ("Building 3-Statement Financial Models", "2.5 hours", "Linking Income Statements, Balance Sheets, and Cash Flow Statements."),
            ("Valuation Methods: Discounted Cash Flow", "2 hours", "Calculating WACC, terminal value, and present values of startups."),
            ("Sensitivity Tables and Scenario Analysis", "1.5 hours", "Setting up Excel data tables to compare outcome metrics."),
            ("Cap Tables & Startup Dilution Analysis", "1 hour", "Modeling equity funding rounds, options pools, and capitalization tables.")
        ]
    }
    
    for course in courses:
        c_id = course[0]
        c_title = course[1]
        
        # Get custom syllabus or fallback to default lists
        selected_lessons = custom_syllabus.get(c_title, [
            ("Overview & Introduction", "20 mins", "Introduction to core concepts."),
            ("Detailed Architecture", "30 mins", "Theory and setup instructions."),
            ("Practical Lab", "40 mins", "Run actual codes and tasks."),
            ("Quiz and Summary", "30 mins", "Verify key skills learned.")
        ])
        
        for idx, (title, duration, content) in enumerate(selected_lessons):
            cursor.execute('''
                INSERT INTO lessons (course_id, title, order_num, duration, content)
                VALUES (?, ?, ?, ?, ?)
            ''', (c_id, title, idx + 1, duration, content))

    # 3. Insert Mock Users
    # 10 mock users representing different learner archetypes with mock XP values
    mock_users = [
        ("alex_dev", "Alex Rivera", "Intermediate", "Become a full-stack engineer", "Python,JavaScript,HTML,CSS,React,SQL", 1, 350),
        ("maria_ds", "Maria Thorne", "Beginner", "Pivot into machine learning and analytics", "Python,Data Science,Machine Learning,SQL", 1, 580),
        ("sam_ux", "Sam Chen", "Beginner", "Transition to product and UI/UX design", "UX,UI,Figma,Design System", 1, 290),
        ("elena_mgr", "Elena Popova", "Intermediate", "Learn agile management and marketing analytics", "Agile,Product Management,Marketing,Analytics", 1, 210),
        ("john_beg", "John Doe", "Beginner", "Learn programming basics from scratch", "Python,HTML,CSS", 1, 20),
        ("tariq_adv", "Tariq Mahmood", "Advanced", "Deepen deep learning and backend skills", "Deep Learning,PyTorch,SQL,Flask,API", 1, 720),
        ("sophie_web", "Sophie Dubois", "Intermediate", "Master frontend design and react development", "JavaScript,React,HTML,CSS,Figma", 1, 420),
        ("raj_finance", "Raj Patel", "Intermediate", "Build finance startup and modeling sheets", "Startup,Finance,Excel,SQL", 1, 120),
        ("olivia_growth", "Olivia Taylor", "Beginner", "Start product marketing and growth strategies", "Marketing,Product,Analytics", 1, 70),
        ("david_ml", "David Kim", "Intermediate", "Apply machine learning and data tools", "Python,Data Science,Machine Learning,Pandas", 1, 180)
    ]
    
    user_ids = {}
    for username, name, skill, goals, interests, onboarded, xp in mock_users:
        hashed_pw = generate_password_hash("password123")
        cursor.execute('''
            INSERT INTO users (username, password_hash, full_name, skill_level, learning_goals, interests, onboarded, xp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, hashed_pw, name, skill, goals, interests, onboarded, xp))
        user_ids[username] = cursor.lastrowid
        
    # Get courses dict
    cursor.execute("SELECT id, title, category, tags FROM courses")
    courses_rows = cursor.fetchall()
    c_dict = {row['title']: row['id'] for row in courses_rows}
    
    # 4. Insert Enrollments, Lesson Progress and Ratings for Mock Users
    # We construct realistic patterns:
    # Alex: Full stack developer.
    # Enrolls: HTML & CSS, JavaScript, React, SQL, Flask APIs
    # Ratings: Rates HTML&CSS (4), JavaScript (5), React (5), SQL (4)
    alex_ratings = [
        ("HTML5 and CSS3: Building Responsive Web Designs", 4, "Great foundations of layouts and CSS Grid."),
        ("Modern Full-Stack JavaScript with Node.js", 5, "Amazing comprehensive course. Clean examples!"),
        ("React.js: Build Production-Ready Interfaces", 5, "The state management concepts were extremely clear."),
        ("Advanced SQL for Databases and Data Analysis", 4, "Good advanced tips on query optimization.")
    ]
    
    # Maria: Data Scientist.
    # Enrolls: Python Programming, Data Analysis with Pandas, ML with Scikit-Learn, Deep Learning, SQL
    # Ratings: Python Programming (5), Data Analysis (5), Machine Learning (5), Deep Learning (4)
    maria_ratings = [
        ("Python Programming for Beginners", 5, "Best introductory course. Walkthroughs are practical."),
        ("Data Analysis and Visualization with Pandas", 5, "Using Jupyter notebooks with Pandas made analytics very simple."),
        ("Introduction to Machine Learning with Scikit-Learn", 5, "Crystal clear mathematical explanations."),
        ("Deep Learning and Neural Networks with PyTorch", 4, "Hard concepts, but deep explanation was well worth it.")
    ]
    
    # Sam: UX/UI Design.
    # Enrolls: UX/UI Design Principles, Figma Mastery, Mobile Design, Responsive Designs
    # Ratings: UX/UI (5), Figma Mastery (5), Mobile Design (4)
    sam_ratings = [
        ("Introduction to UX/UI Design Principles", 5, "Insightful guidelines about spacing and typography."),
        ("Figma Mastery: High-Fidelity Prototyping", 5, "I loved building reusable UI components and variants."),
        ("Mobile App Design and Micro-Interactions", 4, "Engaging styling tips on animations.")
    ]
    
    # Tariq: Advanced Backend/ML.
    # Enrolls: Advanced Python, Deep Learning, NLP, REST APIs
    # Ratings: Deep Learning (5), NLP (5), Intermediate Python (4), Building RESTful APIs with Flask and Python (5)
    tariq_ratings = [
        ("Deep Learning and Neural Networks with PyTorch", 5, "Exactly what I was looking for. Highly recommend."),
        ("Natural Language Processing (NLP) in Python", 5, "Outstanding coverage of embeddings and NLP pipelines."),
        ("Intermediate Python and OOP Concepts", 4, "Solid refresher on Python decorators."),
        ("Building RESTful APIs with Flask and Python", 5, "Very practical structure for Flask backend apps.")
    ]
    
    # Sophie: Frontend & React.
    # Enrolls: HTML & CSS, JavaScript, React, Figma Mastery
    # Ratings: HTML & CSS (5), JavaScript (4), React (5), Figma Mastery (4)
    sophie_ratings = [
        ("HTML5 and CSS3: Building Responsive Web Designs", 5, "Perfect layouts instructions."),
        ("Modern Full-Stack JavaScript with Node.js", 4, "Excellent content on async await and REST APIs."),
        ("React.js: Build Production-Ready Interfaces", 5, "Highly reusable custom hooks code examples!"),
        ("Figma Mastery: High-Fidelity Prototyping", 4, "Helps bridge frontend code with layout prototype design.")
    ]
    
    # David: Machine learning.
    # Enrolls: Python Programming, Data Analysis, ML with Scikit-Learn
    # Ratings: Python Programming (4), Data Analysis (4), Machine Learning (5)
    david_ratings = [
        ("Python Programming for Beginners", 4, "Solid course for basic concepts."),
        ("Data Analysis and Visualization with Pandas", 4, "Very helpful tools for pandas cleaning."),
        ("Introduction to Machine Learning with Scikit-Learn", 5, "Excellent algorithms coverage!")
    ]

    all_user_ratings = {
        "alex_dev": alex_ratings,
        "maria_ds": maria_ratings,
        "sam_ux": sam_ratings,
        "tariq_adv": tariq_ratings,
        "sophie_web": sophie_web_ratings if 'sophie_web_ratings' in locals() else sophie_ratings,
        "david_ml": david_ratings
    }
    
    for username, ratings in all_user_ratings.items():
        u_id = user_ids[username]
        for course_title, rating_val, review in ratings:
            c_id = c_dict.get(course_title)
            if c_id:
                # 1. Enroll
                # Simulate progress: complete 50% or 100%
                completed = 1 if rating_val >= 5 else 0
                progress = 100.0 if completed else 50.0
                cursor.execute('''
                    INSERT INTO enrollments (user_id, course_id, progress_percent, completed)
                    VALUES (?, ?, ?, ?)
                ''', (u_id, c_id, progress, completed))
                
                # Update course enrolled count
                cursor.execute('''
                    UPDATE courses SET enrolled_count = enrolled_count + 1 WHERE id = ?
                ''', (c_id,))
                
                # 2. Add Rating
                cursor.execute('''
                    INSERT INTO ratings (user_id, course_id, rating, review_text)
                    VALUES (?, ?, ?, ?)
                ''', (u_id, c_id, rating_val, review))
                
                # 3. Add Lesson progress for first 2 lessons (50% progress) or all 4 lessons (100% progress)
                cursor.execute("SELECT id FROM lessons WHERE course_id = ? ORDER BY order_num ASC", (c_id,))
                lessons = cursor.fetchall()
                lessons_to_complete = lessons if completed else lessons[:2]
                for l in lessons_to_complete:
                    cursor.execute('''
                        INSERT INTO lesson_progress (user_id, course_id, lesson_id, completed)
                        VALUES (?, ?, ?, 1)
                    ''', (u_id, c_id, l['id']))
                    
    # Recalculate courses overall ratings in courses table
    cursor.execute("SELECT id FROM courses")
    all_c = cursor.fetchall()
    for c in all_c:
        cid = c[0]
        cursor.execute("SELECT AVG(rating) FROM ratings WHERE course_id = ?", (cid,))
        avg_rating = cursor.fetchone()[0]
        if avg_rating is not None:
            cursor.execute("UPDATE courses SET rating = ? WHERE id = ?", (round(avg_rating, 1), cid))
        else:
            # Random default ratings for unrated courses to make it look realistic
            import random
            random_rating = round(random.uniform(4.0, 4.8), 1)
            cursor.execute("UPDATE courses SET rating = ? WHERE id = ?", (random_rating, cid))
            
    conn.commit()
    conn.close()
    print("Database seeding completed.")

if __name__ == "__main__":
    init_db()
    seed_db()
