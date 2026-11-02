import database

# Pre-defined QA Knowledge Base and Quiz questions for each course to make it feel high-fidelity and real
COURSES_CONTENT = {
    "Python Programming for Beginners": {
        "faqs": [
            ("setup", "To setup Python, download the installer from python.org, run it, and make sure to check 'Add Python to PATH'. Then install VS Code and add the Python extension."),
            ("variables", "In Python, variables are created the moment you assign a value to them (e.g., x = 5, name = 'Aura'). Python is dynamically typed, so you don't need to declare types."),
            ("loops", "Python has two loop commands: 'while' loops (runs as long as a condition is true) and 'for' loops (used for iterating over a sequence like a list, tuple, or range)."),
            ("functions", "Define a function using the 'def' keyword followed by the function name and parentheses (e.g., def my_function():). Use the 'return' keyword to send values back.")
        ],
        "quiz": [
            {
                "question": "What is the correct syntax to output 'Hello World' in Python?",
                "options": ["print('Hello World')", "echo('Hello World')", "printf('Hello World')", "console.log('Hello World')"],
                "answer": "print('Hello World')"
            },
            {
                "question": "Which of the following data types is mutable (can be changed) in Python?",
                "options": ["Tuple", "List", "String", "Integer"],
                "answer": "List"
            },
            {
                "question": "How do you start writing a for loop in Python?",
                "options": ["for x in y:", "for (x = 0; x < y; x++)", "foreach x in y", "for x to y:"],
                "answer": "for x in y:"
            }
        ]
    },
    "Modern Full-Stack JavaScript with Node.js": {
        "faqs": [
            ("es6", "ES6 introduced let and const for block-scoped variables, arrow functions (() => {}), template literals (`${}`), and destructuring assignments."),
            ("async", "Asynchronous JavaScript uses Callbacks, Promises, and modern Async/Await syntax to perform non-blocking operations like fetching API data."),
            ("node", "Node.js is a JavaScript runtime built on Chrome's V8 engine that allows developers to run JavaScript on the server side to build fast network APIs.")
        ],
        "quiz": [
            {
                "question": "Which keyword is used to declare a variable that cannot be reassigned?",
                "options": ["let", "var", "const", "static"],
                "answer": "const"
            },
            {
                "question": "What does DOM stand for?",
                "options": ["Document Object Model", "Data Object Management", "Dynamic Output Module", "Desktop Operations Manager"],
                "answer": "Document Object Model"
            },
            {
                "question": "Which Node.js core module is used to create an HTTP server?",
                "options": ["fs", "path", "http", "url"],
                "answer": "http"
            }
        ]
    },
    "HTML5 and CSS3: Building Responsive Web Designs": {
        "faqs": [
            ("flexbox", "Flexbox is a one-dimensional layout model. Use display: flex on parent, then align-items and justify-content to control spacing and axes."),
            ("grid", "CSS Grid is a two-dimensional layout system. Use display: grid on parent, and define rows/columns using grid-template-columns: repeat(3, 1fr)."),
            ("responsive", "Responsive design ensures layouts adapt to mobile screen viewports. Write media queries: @media (max-width: 768px) { ... }.")
        ],
        "quiz": [
            {
                "question": "Which HTML5 element is semantic for navigation links?",
                "options": ["<nav>", "<links>", "<menu>", "<header>"],
                "answer": "<nav>"
            },
            {
                "question": "How do you apply a flexbox layout to a container in CSS?",
                "options": ["layout: flex", "display: flexbox", "display: flex", "align: flex"],
                "answer": "display: flex"
            },
            {
                "question": "Which tag is used to reference an external CSS stylesheet?",
                "options": ["<script>", "<link>", "<style>", "<css>"],
                "answer": "<link>"
            }
        ]
    }
}

# Fallback assistant generator for any other course dynamically using SQLite database schema
def generate_dynamic_quiz(course_id, course_title):
    # If pre-defined exists
    if course_title in COURSES_CONTENT:
        return COURSES_CONTENT[course_title]["quiz"]
        
    # Else generate dynamic based on syllabus
    conn = database.get_db_connection()
    lessons = conn.execute("SELECT title FROM lessons WHERE course_id = ? ORDER BY order_num ASC", (course_id,)).fetchall()
    conn.close()
    
    quiz = []
    for idx, l in enumerate(lessons[:3]):
        q_text = f"Which of the following core topics is directly covered in Chapter {idx+1}: '{l['title']}'?"
        opts = [l['title'], "Advanced Deployment Frameworks", "Theoretical Architecture Analysis", "Standard Performance Auditing"]
        # shuffle options or keep the first as answer
        quiz.append({
            "question": q_text,
            "options": opts,
            "answer": l['title']
        })
        
    if not quiz:
        # Fallback if no lessons
        quiz = [
            {
                "question": f"What is the target skill level for '{course_title}'?",
                "options": ["Beginner", "Intermediate", "Advanced", "All Levels"],
                "answer": "All Levels"
            }
        ]
    return quiz

def generate_dynamic_slides(course_id, course_title, course_description):
    conn = database.get_db_connection()
    lessons = conn.execute("SELECT title, content, duration FROM lessons WHERE course_id = ? ORDER BY order_num ASC", (course_id,)).fetchall()
    conn.close()
    
    slides = []
    # Title slide
    slides.append({
        "title": course_title,
        "subtitle": "Course Lecture Deck",
        "points": [
            "Overview: " + course_description,
            "Structure: " + f"{len(lessons)} comprehensive chapters",
            "Target: Learn core workflows step-by-step"
        ]
    })
    
    # Lesson slides
    for l in lessons:
        slides.append({
            "title": l['title'],
            "subtitle": f"Syllabus Module | Duration: {l['duration']}",
            "points": [
                l['content'],
                "Key objective: Practice code examples matching " + l['title'],
                "Time allocated: " + l['duration']
            ]
        })
        
    # Conclusion slide
    slides.append({
        "title": "Conclusion & Next Steps",
        "subtitle": "Course Completion Goal",
        "points": [
            "Review code files in your workspaces.",
            "Take the Course Evaluation Skill check to update recommendations.",
            "Obtain your credential certificate upon completing 100%!"
        ]
    })
    
    return slides

def get_assistant_response(course_id, course_title, message):
    msg_lower = message.lower().strip()
    
    # Check pre-defined FAQs
    reply = ""
    if course_title in COURSES_CONTENT:
        faqs = COURSES_CONTENT[course_title]["faqs"]
        for keyword, explanation in faqs:
            if keyword in msg_lower:
                reply = f"Here is some information about **{keyword.capitalize()}** from the syllabus:\n\n{explanation}\n\nIs there anything else you would like to clarify?"
                break
                
    if not reply:
        # Try fetching course details
        conn = database.get_db_connection()
        lessons = conn.execute("SELECT title, content FROM lessons WHERE course_id = ? ORDER BY order_num ASC", (course_id,)).fetchall()
        conn.close()
        
        # Check lesson keywords
        matched_lesson = None
        for l in lessons:
            if l['title'].lower() in msg_lower or any(word in msg_lower for word in l['title'].lower().split()):
                matched_lesson = l
                break
                
        if matched_lesson:
            reply = f"According to Chapter **'{matched_lesson['title']}'** of this course:\n\n\"{matched_lesson['content']}\"\n\nWould you like me to generate a quick practice quiz or slide deck for this course?"
        else:
            # Fallback general answer
            reply = f"Hello! I am your AI learning assistant for **{course_title}**. I can guide you through the syllabus:\n\n- Type **'quiz'** or click the button below to generate a custom practice test.\n- Type **'slides'** or click the button to view interactive lecture presentation slides.\n- Ask me specific questions about the course modules."
            
    return reply
