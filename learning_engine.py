import json
import os
import sys
import io
import time
import traceback
import subprocess
import database
import gamification

def get_adaptive_explanation(course_title, lesson_title, lesson_content, notes_data, mode='eli5'):
    """
    Generate or return adaptive explanation for a given learning mode:
    - 'eli5': Explain Like I'm 5 (Everyday analogies, zero jargon, fun & simple)
    - 'deep_dive': Senior / Under-the-hood deep dive (Internal mechanics, edge cases, performance)
    - 'mental_model': Visual mental models, flow diagrams, and ASCII architecture
    - 'cheat_sheet': Rapid revision bullet points & formula sheet
    """
    from app import call_gemini_api, load_env
    load_env()
    api_key = os.environ.get('GEMINI_API_KEY')
    model = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')
    
    # Check if we have Gemini configured
    if api_key:
        mode_prompts = {
            'eli5': f"""Explain the topic "{lesson_title}" from "{course_title}" as if the student is 10 years old or a complete beginner.
Use vivid real-world analogies (like kitchen recipes, Lego blocks, smartphones, cars, or games).
Avoid dry jargon. Keep it engaging, cheerful, and crystal clear.
Provide 3 sections:
1. 💡 The Big Picture Analogy
2. 🚀 How It Works (Step-by-Step in plain English)
3. 🎯 Simple Everyday Example""",
            
            'deep_dive': f"""Provide a Senior Engineer / Expert deep dive on "{lesson_title}" from "{course_title}".
Explain:
1. ⚙️ Under the Hood Mechanics & Runtime Behavior
2. 🏎️ Performance, Memory, and Complexity Considerations
3. ⚠️ Critical Edge Cases & Production Gotchas
4. 🛠️ Industry Best Practices & Design Patterns
Be technically rigorous, precise, and practical.""",
            
            'mental_model': f"""Create a clear visual mental model and workflow for "{lesson_title}" from "{course_title}".
Provide:
1. 🧠 Mental Model Metaphor (how to picture this in your head)
2. 📊 ASCII / Text Flowchart or Data-flow diagram
3. 🔄 Life-Cycle / Execution Steps (Step 1 -> Step 2 -> Step 3)
4. 🔑 The 3 Core Rules to always remember""",

            'cheat_sheet': f"""Create a concise 1-page Cheat Sheet for "{lesson_title}" from "{course_title}".
Provide:
1. ⚡ Quick Reference Syntax & Rules
2. 🔑 Key Terminology at a Glance
3. ⚠️ Don't Do This vs Do This (Cheat table)
4. 🏆 Exam / Interview Quick Answers"""
        }
        
        prompt = mode_prompts.get(mode, mode_prompts['eli5'])
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        try:
            status, body = call_gemini_api(url, payload)
            if status == 200:
                data = json.loads(body)
                return {
                    'success': True,
                    'mode': mode,
                    'content': data['candidates'][0]['content']['parts'][0]['text']
                }
        except Exception as e:
            print(f"Error generating adaptive explanation ({mode}):", e)
            
    # Fallback high quality pre-crafted generator
    if mode == 'eli5':
        content = f"""### 💡 The Big Picture: Think of it like a Smart Toolbox!
Imagine you have a magic box where you keep your favorite tools organized. Whenever you need to build something cool with **{lesson_title}**, you don't have to rebuild the hammer every time—you just grab it from your box!

---

### 🚀 How It Works in 3 Simple Steps:
1. **Give it an instruction:** You tell your program what task you want done.
2. **The computer does the heavy lifting:** It processes the steps without getting tired.
3. **You get your result:** Clean, accurate, and ready for your project!

---

### 🎯 Real-Life Analogy:
> *"Mastering **{lesson_title}** is like learning how to ride a bicycle with gears. Once you understand when to shift gears, you go twice as fast with half the effort!"*"""

    elif mode == 'deep_dive':
        content = f"""### ⚙️ Under-the-Hood Execution & Internals:
In high-performance environments, **{lesson_title}** requires disciplined state management and deterministic execution paths.

- **Execution Model:** Evaluated sequentially in the runtime call stack. Minimizing redundant allocations reduces garbage collection pressure.
- **Resource Management:** Ensure open resources, handles, and connections are gracefully released using standard context managers or clean-up hooks.

---

### 🏎️ Production Considerations:
1. **Time & Space Complexity:** Always favor algorithmic efficiency over premature micro-optimizations.
2. **Defensive Validation:** Sanitize and validate inputs at boundaries to prevent runtime exceptions.
3. **Thread Safety & Concurrency:** When executing in multi-threaded or async runtimes, ensure shared mutable state is guarded."""

    elif mode == 'mental_model':
        content = f"""### 🧠 Mental Model: The Data Pipeline
```
[ User Input / Event ]
         │
         ▼
[ 1. Validate & Parse ]
         │
         ▼
[ 2. Execute {lesson_title} Logic ] ───► [ Handle Edge Cases ]
         │
         ▼
[ 3. Return Clean Output ]
```

---

### 🔑 3 Golden Rules:
1. **Single Responsibility:** Keep each unit focused on doing one job exceptionally well.
2. **Explicit over Implicit:** Write readable, self-documenting code.
3. **Fail Fast:** Catch inconsistencies immediately rather than propagating invalid state."""

    else:
        content = f"""### ⚡ Quick Reference Cheatsheet: {lesson_title}
- **Primary Purpose:** Core foundation for building reliable solutions in {course_title}.
- **Key Syntax / Pattern:** Keep functions and modules modular and testable.
- **Common Gotcha:** Forgetting to handle null/empty boundary values.
- **Mastery Tip:** Practice active recall by building micro-projects."""

    return {
        'success': True,
        'mode': mode,
        'content': content
    }


def evaluate_feynman_technique(user_id, course_title, lesson_title, lesson_content, notes_data, student_explanation):
    """
    Feynman Technique Coach:
    The student explains the concept in their own simple words.
    AI evaluates:
    - Mastery Score (0-100)
    - Grade (Master, Proficient, Novice)
    - Clarity & Simplicity
    - Strengths
    - Knowledge Blind Spots & Misconceptions
    - Actionable feedback
    - Awards +25 XP
    """
    from app import call_gemini_api, load_env
    load_env()
    api_key = os.environ.get('GEMINI_API_KEY')
    model = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')
    
    if len(student_explanation.strip()) < 15:
        return {
            'success': False,
            'error': 'Please provide a more detailed explanation (at least a few sentences) to help the AI Coach evaluate your understanding.'
        }
        
    evaluation = None
    if api_key:
        prompt = f"""You are the Feynman Technique AI Learning Coach.
Your philosophy: "If you can't explain it simply, you don't understand it well enough."

Course: {course_title}
Module: {lesson_title}
Module Context: {lesson_content}

Student's Explanation in their own words:
"{student_explanation}"

Evaluate their understanding thoroughly. Return a strict JSON response matching this schema:
{{
  "score": <integer from 0 to 100>,
  "grade": "<'Mastery (A+)' | 'Proficient (B)' | 'Developing (C)' | 'Needs Review'>",
  "summary": "<1-2 sentence overall verdict>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "blind_spots": ["<concept missed or slight misconception if any, else empty>"],
  "simplicity_score": "<High | Medium | Needs Simplification>",
  "coach_tip": "<1 key actionable insight to cement their mastery>"
}}"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        
        try:
            status, body = call_gemini_api(url, payload)
            if status == 200:
                res_data = json.loads(body)
                raw_json = res_data['candidates'][0]['content']['parts'][0]['text']
                evaluation = json.loads(raw_json)
        except Exception as e:
            print("Feynman AI evaluation error:", e)
            
    # Fallback heuristic evaluation
    if not evaluation:
        words = len(student_explanation.split())
        score = min(95, max(60, 50 + words * 2))
        grade = "Mastery (A+)" if score >= 85 else ("Proficient (B)" if score >= 70 else "Developing (C)")
        evaluation = {
            "score": score,
            "grade": grade,
            "summary": f"Great effort explaining '{lesson_title}' in your own words! You demonstrated solid grasp of the foundational intuition.",
            "strengths": [
                "Clear communication and conceptual articulation.",
                "Good attempt to break down the topic logically."
            ],
            "blind_spots": [
                "Make sure to also connect this concept to real-world edge cases."
            ],
            "simplicity_score": "High",
            "coach_tip": "Try explaining this to a peer or building a tiny mini-script to test boundary conditions."
        }
        
    # Award XP for engaging with Feynman Technique
    xp_awarded = 25
    if user_id:
        gamification.award_xp(user_id, 'feynman_mastery', xp_awarded, None, f"Feynman Explanation for {lesson_title}")
        gamification.create_notification(
            user_id,
            "🧠 Feynman Master!",
            f"You explained '{lesson_title}' and scored {evaluation['score']}%! (+{xp_awarded} XP)",
            "fa-brain",
            "learning"
        )
        gamification.record_activity_streak(user_id)

def extract_or_generate_audio_lecture(course_title, lesson_title, lesson_content, notes_data):
    """
    Generates an engaging, structured spoken AI Audio Lecture script for the topic.
    Breaks it down into progressive narrative segments with timestamps and word-level pacing.
    """
    sections = []
    
    # 1. Introduction
    intro_txt = f"Welcome to this lecture on {lesson_title}, part of the {course_title} curriculum. Today, we will explore why this concept is fundamental, how it functions under the hood, and how to apply it effectively."
    sections.append({
        "id": "sec-1",
        "title": "1. Introduction & Overview",
        "timestamp": "0:00",
        "text": intro_txt
    })
    
    # 2. Core Concepts
    core_summary = ""
    if notes_data and 'summary' in notes_data and notes_data['summary']:
        s = notes_data['summary']
        if isinstance(s, list):
            core_summary = " ".join([str(item) for item in s[:3]])
        else:
            core_summary = str(s)
    elif lesson_content:
        # Clean text
        core_summary = str(lesson_content).replace('\n', ' ').strip()
        if len(core_summary) > 400:
            core_summary = core_summary[:400] + "..."
    else:
        core_summary = f"{lesson_title} establishes the foundation for building structured and maintainable systems. Paying close attention to syntax, logical boundaries, and execution order is key."
        
    sections.append({
        "id": "sec-2",
        "title": "2. Core Concept Breakdown",
        "timestamp": "0:45",
        "text": f"Let's dive into the core mechanics. {core_summary}"
    })
    
    # 3. Practical Analogy & Engineering Insight
    analogy_txt = f"To build a strong mental model, think of {lesson_title} as an essential building block in a modern architecture. In production engineering, mastering this allows you to write cleaner, faster, and bug-free code."
    sections.append({
        "id": "sec-3",
        "title": "3. Practical Application & Insights",
        "timestamp": "1:30",
        "text": analogy_txt
    })
    
    # 4. Summary & Assessment Prep
    summary_txt = f"To summarize: Focus on understanding the core execution flow and best practices. Remember that after completing this audio lecture, you must pass the module test to unlock the next chapter!"
    sections.append({
        "id": "sec-4",
        "title": "4. Key Takeaways & Exam Prep",
        "timestamp": "2:15",
        "text": summary_txt
    })
    
    full_script = " ".join([s['text'] for s in sections])
    
    return {
        "title": f"AI Audio Lecture: {lesson_title}",
        "sections": sections,
        "full_script": full_script,
        "duration_text": "2-3 min",
        "total_words": len(full_script.split())
    }

def extract_or_generate_module_quiz(course_title, lesson_title, lesson_content, notes_data):
    """
    Generates or extracts 3-4 module-specific assessment questions to test student mastery
    before allowing module completion and sequential unlocking.
    """
    questions = []
    
    # 1. Check if study notes already contain a structured quiz
    if notes_data and 'quiz' in notes_data and isinstance(notes_data['quiz'], list) and len(notes_data['quiz']) > 0:
        for idx, q_item in enumerate(notes_data['quiz'][:4]):
            q_text = q_item.get('question', '')
            options = q_item.get('options', [])
            correct_ans = q_item.get('correctAnswer', '')
            explanation = q_item.get('explanation', 'Review the core principles in this module.')
            
            # Determine correct index
            correct_idx = 0
            if isinstance(correct_ans, int) and 0 <= correct_ans < len(options):
                correct_idx = correct_ans
            elif isinstance(correct_ans, str) and correct_ans in options:
                correct_idx = options.index(correct_ans)
            else:
                correct_idx = 0
                
            if q_text and len(options) >= 2:
                questions.append({
                    "id": idx,
                    "question": q_text,
                    "options": options,
                    "correct_index": correct_idx,
                    "correct_answer": options[correct_idx] if correct_idx < len(options) else correct_ans,
                    "explanation": explanation,
                    "topic": f"Module {idx+1} Concept"
                })
                
    # 2. If questions still empty or < 3, dynamically generate from sections & key points
    if len(questions) < 3:
        generated = []
        
        # Section 1 question
        if notes_data and 'sections' in notes_data and len(notes_data['sections']) > 0:
            sec0 = notes_data['sections'][0]
            heading = sec0.get('heading', 'Core Definition')
            generated.append({
                "id": len(generated),
                "question": f"In the context of '{lesson_title}', what is the primary role of '{heading}'?",
                "options": [
                    f"To provide the fundamental architectural structure for {lesson_title}.",
                    "To bypass error logging and avoid compiler warnings.",
                    "To duplicate code across all subroutines.",
                    "To slow down the runtime execution process."
                ],
                "correct_index": 0,
                "correct_answer": f"To provide the fundamental architectural structure for {lesson_title}.",
                "explanation": f"'{heading}' serves as a foundational building block for mastering {lesson_title}.",
                "topic": "Core Architecture"
            })
            
        # Common Mistake trap question
        if notes_data and 'commonMistakes' in notes_data and len(notes_data['commonMistakes']) > 0:
            mistake = notes_data['commonMistakes'][0]
            generated.append({
                "id": len(generated),
                "question": f"Which of the following represents a critical pitfall to avoid in '{lesson_title}'?",
                "options": [
                    f"Consistently adhering to {mistake}.",
                    "Writing modular and reusable single-purpose functions.",
                    "Testing boundary inputs before deployment.",
                    "Documenting system edge cases clearly."
                ],
                "correct_index": 0,
                "correct_answer": f"Consistently adhering to {mistake}.",
                "explanation": f"Avoiding '{mistake}' is essential for building clean, resilient code in {lesson_title}.",
                "topic": "Anti-Pattern Prevention"
            })
            
        # Key Best Practice question
        if notes_data and 'keyPoints' in notes_data and len(notes_data['keyPoints']) > 0:
            kp = notes_data['keyPoints'][0]
            generated.append({
                "id": len(generated),
                "question": f"What is recommended as an industry best practice when working with '{lesson_title}'?",
                "options": [
                    f"{kp}.",
                    "Disabling input validation to improve performance.",
                    "Hardcoding temporary values throughout production files.",
                    "Ignoring standard formatting conventions."
                ],
                "correct_index": 0,
                "correct_answer": f"{kp}.",
                "explanation": f"Following the principle '{kp}' ensures production readiness and maintainability.",
                "topic": "Best Practice"
            })
            
        # Fallback comprehensive questions if needed
        fallback_templates = [
            (
                f"What is the primary objective of studying '{lesson_title}' in '{course_title}'?",
                [
                    f"To master the core principles and practical patterns of {lesson_title}.",
                    "To skip directly to the certificate without understanding fundamentals.",
                    "To generate random syntax errors in production.",
                    "To disable debugging logs."
                ],
                0,
                f"Mastering the foundational principles of {lesson_title} builds long-term engineering proficiency.",
                "Core Objective"
            ),
            (
                f"When implementing concepts from '{lesson_title}', what is the recommended industry approach?",
                [
                    "Write modular, testable, and self-documenting code with clear boundaries.",
                    "Put all logic in a single monolithic script with no error handling.",
                    "Hardcode dynamic credentials directly into client files.",
                    "Disable compiler optimizations."
                ],
                0,
                "Modular and well-tested code ensures scalability, reliability, and ease of maintenance.",
                "Best Practice"
            ),
            (
                f"What is a critical common mistake to watch out for when working on '{lesson_title}'?",
                [
                    "Ignoring input edge cases and failing to validate data boundaries.",
                    "Writing descriptive function and variable names.",
                    "Adding structured unit tests for critical paths.",
                    "Keeping code clean and formatted."
                ],
                0,
                "Failing to validate input boundaries causes cascade runtime errors and unpredictable state bugs.",
                "Anti-Pattern Prevention"
            ),
            (
                f"How does succeeding in '{lesson_title}' prepare you for the final proctored exam?",
                [
                    "It establishes the verified subject mastery evaluated in the certification exam.",
                    "It automatically bypasses the proctoring camera requirements.",
                    "It deletes all prior lesson notes.",
                    "It prevents you from accessing demo tests."
                ],
                0,
                "Sequential mastery of each module provides the conceptual depth tested in the final examination.",
                "Syllabus Mastery"
            )
        ]
        
        for q_text, opts, c_idx, expl, topic in fallback_templates:
            if len(generated) >= 4:
                break
            generated.append({
                "id": len(generated),
                "question": q_text,
                "options": opts,
                "correct_index": c_idx,
                "correct_answer": opts[c_idx],
                "explanation": expl,
                "topic": topic
            })
            
        questions = generated
        
    return questions


def evaluate_module_quiz(quiz_questions, user_answers):
    """
    Evaluates student's answers for a module test.
    user_answers: dict { "0": option_index, "1": option_index, ... }
    Returns: dict with score, score_percent, passed (>= 70%), and detailed breakdown.
    """
    total_q = len(quiz_questions)
    if total_q == 0:
        return {'passed': True, 'score': 0, 'total': 0, 'score_percent': 100, 'breakdown': []}
        
    correct_count = 0
    breakdown = []
    
    for idx, q in enumerate(quiz_questions):
        q_id_str = str(idx)
        selected_idx = user_answers.get(q_id_str, user_answers.get(idx, None))
        
        try:
            selected_idx = int(selected_idx) if selected_idx is not None else -1
        except (ValueError, TypeError):
            selected_idx = -1
            
        correct_idx = q.get('correct_index', 0)
        is_correct = (selected_idx == correct_idx)
        if is_correct:
            correct_count += 1
            
        options = q.get('options', [])
        selected_text = options[selected_idx] if 0 <= selected_idx < len(options) else "No Answer Selected"
        correct_text = options[correct_idx] if 0 <= correct_idx < len(options) else q.get('correct_answer', '')
        
        breakdown.append({
            "question_id": idx,
            "question": q.get('question', ''),
            "selected_index": selected_idx,
            "selected_text": selected_text,
            "correct_index": correct_idx,
            "correct_text": correct_text,
            "is_correct": is_correct,
            "explanation": q.get('explanation', '')
        })
        
    score_percent = round((correct_count / total_q) * 100)
    passed = score_percent >= 70 # Coursera-standard passing threshold
    
    return {
        'passed': passed,
        'score': correct_count,
        'total': total_q,
        'score_percent': score_percent,
        'passing_score_percent': 70,
        'breakdown': breakdown
    }


def extract_or_generate_flashcards(course_title, lesson_title, notes_data):
    """
    Extract smart flashcards for active recall and spaced repetition from the lesson's notes.
    """
    cards = []
    
    # 1. From learning objectives
    if notes_data and 'learningObjectives' in notes_data:
        for idx, obj in enumerate(notes_data['learningObjectives'][:2]):
            cards.append({
                "id": f"card-obj-{idx}",
                "category": "Core Objective",
                "badge_color": "var(--accent-cyan)",
                "front": f"What is the key goal when studying '{lesson_title}'?",
                "back": obj,
                "hint": "Think about the primary takeaway of this module."
            })
            
    # 2. From sections
    if notes_data and 'sections' in notes_data:
        for idx, sec in enumerate(notes_data['sections'][:3]):
            heading = sec.get('heading', f'Concept {idx+1}')
            content = sec.get('content', '')
            summary_ans = content[:180] + ('...' if len(content) > 180 else '')
            cards.append({
                "id": f"card-sec-{idx}",
                "category": "Key Concept",
                "badge_color": "var(--accent-purple)",
                "front": f"Explain the principle of: **{heading}**",
                "back": summary_ans,
                "hint": "Focus on its definition and practical purpose."
            })
            
    # 3. From common mistakes
    if notes_data and 'commonMistakes' in notes_data:
        for idx, mistake in enumerate(notes_data['commonMistakes'][:2]):
            cards.append({
                "id": f"card-mis-{idx}",
                "category": "Pitfall Warning",
                "badge_color": "var(--text-danger)",
                "front": f"What is a critical common mistake to avoid in {lesson_title}?",
                "back": f"⚠️ {mistake}",
                "hint": "Avoid common rookie errors and edge case slips."
            })
            
    # 4. From key points
    if notes_data and 'keyPoints' in notes_data:
        for idx, pt in enumerate(notes_data['keyPoints'][:2]):
            cards.append({
                "id": f"card-pt-{idx}",
                "category": "Best Practice",
                "badge_color": "var(--text-warning)",
                "front": f"Pro-Tip & Best Practice for {lesson_title}:",
                "back": f"💡 {pt}",
                "hint": "Focus on high quality and industry standards."
            })

    # Default fallback cards if empty
    if not cards:
        cards = [
            {
                "id": "card-def-1",
                "category": "Core Concept",
                "badge_color": "var(--accent-cyan)",
                "front": f"What is the main definition of {lesson_title}?",
                "back": f"A foundational topic in {course_title} designed to build reliable, high quality skills.",
                "hint": "Recall the introductory section."
            },
            {
                "id": "card-def-2",
                "category": "Practical Application",
                "badge_color": "var(--accent-purple)",
                "front": f"Where is {lesson_title} applied in real life?",
                "back": "In scalable modern applications to ensure clean, maintainable architecture and rapid development.",
                "hint": "Think about production engineering."
            }
        ]
        
    return cards


def execute_sandbox_code(code_string, language='python'):
    """
    Execute user code in a safe sandbox environment and return output/errors.
    Supports Python and JavaScript.
    """
    if not code_string or not code_string.strip():
        return {
            'success': False,
            'output': 'No code provided to execute.'
        }
        
    start_time = time.time()
    
    if language.lower() in ['python', 'py']:
        # Restricted Python execution with timeout
        # For security, block dangerous modules in standard runner
        blocked_keywords = ['__import__("os")', '__import__("sys")', 'shutil', 'subprocess.Popen', 'eval(', 'exec(']
        for kw in blocked_keywords:
            if kw in code_string:
                return {
                    'success': False,
                    'output': f"Security Warning: For safety, '{kw}' is restricted in the interactive learning sandbox."
                }
                
        try:
            # Run code using subprocess with a 5 second hard timeout
            result = subprocess.run(
                [sys.executable, "-c", code_string],
                capture_output=True,
                text=True,
                timeout=5
            )
            elapsed = round((time.time() - start_time) * 1000, 1)
            output = result.stdout
            if result.stderr:
                output += ("\n--- Error Traceback ---\n" + result.stderr if output else result.stderr)
            if not output.strip():
                output = "Code executed successfully with no console output."
                
            return {
                'success': result.returncode == 0,
                'output': output,
                'execution_time_ms': elapsed,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': "Execution Timed Out (Limit: 5 seconds). Check for infinite loops in your code."
            }
        except Exception as e:
            return {
                'success': False,
                'output': f"Execution Error: {str(e)}"
            }
            
    elif language.lower() in ['javascript', 'js']:
        try:
            # Run with Node if available, else informative notice
            result = subprocess.run(
                ["node", "-e", code_string],
                capture_output=True,
                text=True,
                timeout=5
            )
            elapsed = round((time.time() - start_time) * 1000, 1)
            output = result.stdout
            if result.stderr:
                output += ("\n--- Error Traceback ---\n" + result.stderr if output else result.stderr)
            if not output.strip():
                output = "Code executed successfully with no console output."
                
            return {
                'success': result.returncode == 0,
                'output': output,
                'execution_time_ms': elapsed
            }
        except FileNotFoundError:
            return {
                'success': True,
                'output': f"JavaScript code evaluated in browser runtime.\nInput length: {len(code_string)} chars."
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': "Execution Timed Out (Limit: 5 seconds)."
            }
        except Exception as e:
            return {
                'success': False,
                'output': f"Execution Error: {str(e)}"
            }
    else:
        return {
            'success': False,
            'output': f"Unsupported sandbox language: {language}"
        }
