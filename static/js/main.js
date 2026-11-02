// Theme Management
document.addEventListener("DOMContentLoaded", () => {
    const themeToggleBtn = document.getElementById("theme-toggle");
    const themeToggleTop = document.getElementById("theme-toggle-top");
    const themeCheckbox = document.getElementById("theme-switch-checkbox");
    
    // Default to light theme as requested
    const savedTheme = localStorage.getItem("theme") || "light";
    setAppTheme(savedTheme);

    function setAppTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("theme", theme);
        
        // Update topbar icon
        const topIcon = document.getElementById("theme-icon-top");
        if (topIcon) {
            topIcon.className = theme === "light" ? "fa-regular fa-sun" : "fa-solid fa-moon";
        }
        
        // Update sidebar toggle switch
        if (themeCheckbox) {
            themeCheckbox.checked = (theme === "dark");
        }
        
        // Update legacy button if present
        if (themeToggleBtn) {
            updateThemeBtnIcon(themeToggleBtn, theme);
        }
    }

    if (themeToggleTop) {
        themeToggleTop.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
            const newTheme = currentTheme === "light" ? "dark" : "light";
            setAppTheme(newTheme);
        });
    }

    if (themeCheckbox) {
        themeCheckbox.addEventListener("change", () => {
            const newTheme = themeCheckbox.checked ? "dark" : "light";
            setAppTheme(newTheme);
        });
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
            const newTheme = currentTheme === "light" ? "dark" : "light";
            setAppTheme(newTheme);
        });
    }
});

function updateThemeBtnIcon(btn, theme) {
    const icon = btn.querySelector("i");
    const label = btn.querySelector("span");
    if (icon) {
        icon.className = theme === "light" ? "fa-solid fa-sun" : "fa-solid fa-moon";
    }
    if (label) {
        label.textContent = theme === "light" ? "Light Mode" : "Dark Mode";
    }
}

// Asynchronous Lesson Progress toggling
function toggleLesson(courseId, lessonId) {
    const url = `/course/${courseId}/lesson/${lessonId}/toggle`;
    const row = document.getElementById(`lesson-row-${lessonId}`);

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update UI class
            if (data.completed) {
                row.classList.add("completed");
            } else {
                row.classList.remove("completed");
            }

            // Update progress bar and texts if they exist on page
            const progressVal = document.getElementById("detail-progress-val");
            const progressBar = document.getElementById("detail-progress-bar");
            const completionStatusText = document.getElementById("completion-status-text");

            if (progressVal && progressBar) {
                const percent = Math.round(data.progress_percent);
                progressVal.textContent = `${percent}%`;
                progressBar.style.width = `${percent}%`;

                if (completionStatusText) {
                    if (percent >= 100) {
                        completionStatusText.textContent = "Completed (Graduate!)";
                    } else {
                        completionStatusText.textContent = `In Progress (${data.completed_count} / ${data.total_count} lessons)`;
                    }
                }

                // Update sidebar Exam CTA visibility
                const certClaimZone = document.getElementById("certificate-claim-zone");
                if (certClaimZone) {
                    if (percent >= 100) {
                        certClaimZone.style.display = "block";
                    } else {
                        certClaimZone.style.display = "none";
                    }
                }
            }
        } else {
            console.error("Failed to toggle lesson progress:", data.error);
        }
    })
    .catch(err => {
        console.error("Error updating lesson progress:", err);
    });
}

// Interactive Assessment Quiz System
const QUIZ_QUESTIONS = {
    "programming": {
        q: "What is the output of print(2 ** 3) in Python?",
        opts: ["6", "8", "9", "5"],
        ans: "8"
    },
    "web development": {
        q: "Which keyword defines block-scoped local variables in modern JavaScript (ES6)?",
        opts: ["var", "let", "const", "local"],
        ans: "let"
    },
    "data science & ai": {
        q: "Which library is primary used in Python to manipulate structured tables & dataframes?",
        opts: ["Pandas", "Scikit-Learn", "NumPy", "Matplotlib"],
        ans: "Pandas"
    },
    "design": {
        q: "What does UI stand for in interface engineering?",
        opts: ["User Interface", "User Integration", "Unique Interaction", "Unified Layout"],
        ans: "User Interface"
    },
    "business": {
        q: "In Scrum Agile framework, who is responsible for maximizing product value & prioritizing backlog?",
        opts: ["Scrum Master", "Product Owner", "Software Lead", "Stakeholder"],
        ans: "Product Owner"
    }
};

function openQuizModal() {
    const modal = document.getElementById("quiz-modal");
    if (!modal) return;

    // Determine course category to select relevant question
    const categoryBadge = document.querySelector(".course-category-badge");
    const category = categoryBadge ? categoryBadge.textContent.toLowerCase().trim() : "programming";
    
    // Fallback if category question not found
    const quizData = QUIZ_QUESTIONS[category] || QUIZ_QUESTIONS["programming"];

    // Populate question label
    document.getElementById("quiz-question-lbl").textContent = quizData.q;
    
    // Clear & Populate options
    const container = document.getElementById("quiz-options-container");
    container.innerHTML = "";
    
    quizData.opts.forEach((opt, idx) => {
        const optionId = `quiz-opt-${idx}`;
        const optionDiv = document.createElement("div");
        optionDiv.className = "select-card";
        optionDiv.style.padding = "0.75rem 1rem";
        optionDiv.onclick = () => selectQuizOption(optionDiv, optionId);
        
        optionDiv.innerHTML = `
            <input type="radio" name="quiz_answer" id="${optionId}" value="${opt}">
            <i class="fa-solid fa-circle-question select-card-icon" style="font-size: 1.1rem;"></i>
            <span style="font-size: 0.9rem; font-weight: 500;">${opt}</span>
        `;
        container.appendChild(optionDiv);
    });

    // Reset feedback box
    const fbBox = document.getElementById("quiz-feedback-box");
    fbBox.style.display = "none";
    fbBox.className = "";
    
    modal.classList.add("active");
}

function selectQuizOption(card, inputId) {
    document.querySelectorAll("#quiz-options-container .select-card").forEach(el => el.classList.remove("selected"));
    card.classList.add("selected");
    const input = document.getElementById(inputId);
    if(input) input.checked = true;
}

function closeQuizModal() {
    const modal = document.getElementById("quiz-modal");
    if (modal) modal.classList.remove("active");
}

function submitQuiz(event, courseId) {
    event.preventDefault();
    const selectedInput = document.querySelector('input[name="quiz_answer"]:checked');
    if (!selectedInput) {
        alert("Please select an answer option!");
        return;
    }

    const userAnswer = selectedInput.value;
    
    const categoryBadge = document.querySelector(".course-category-badge");
    const category = categoryBadge ? categoryBadge.textContent.toLowerCase().trim() : "programming";
    const quizData = QUIZ_QUESTIONS[category] || QUIZ_QUESTIONS["programming"];
    
    const isCorrect = (userAnswer === quizData.ans);
    
    const fbBox = document.getElementById("quiz-feedback-box");
    fbBox.style.display = "block";
    
    if (isCorrect) {
        fbBox.className = "alert alert-success";
        fbBox.innerHTML = `<i class="fa-solid fa-circle-check"></i> <strong>Correct!</strong> Calibrating your recommendations...`;
    } else {
        fbBox.className = "alert alert-danger";
        fbBox.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> <strong>Incorrect.</strong> The correct answer is <strong>${quizData.ans}</strong>. Calibrating level goals...`;
    }

    // Submit results to server to update recommendations
    fetch(`/course/${courseId}/quiz`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            correct: isCorrect,
            category: category
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Show alert alert in top layout
            setTimeout(() => {
                closeQuizModal();
                // Add window alert or reload to show updated recommendations
                window.location.reload();
            }, 2000);
        }
    })
    .catch(err => {
        console.error("Error submitting quiz results:", err);
    });
}

// Toggle Chat Assistant Panel visibility
function toggleChatPanel() {
    const panel = document.getElementById("chat-assistant-panel");
    if (panel) {
        panel.classList.toggle("active");
    }
}

// Key handler for chat input field
function handleChatKey(event, courseId) {
    if (event.key === "Enter") {
        sendChatMessage(courseId);
    }
}

// Append a message bubble to the chat log
function appendChatBubble(sender, text, isMarkdown = false) {
    const log = document.getElementById("chat-history-log");
    if (!log) return;

    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${sender}`;
    
    // basic bold formatter
    let cleanText = text;
    if (isMarkdown) {
        cleanText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        cleanText = cleanText.replace(/- (.*?)\n/g, '<li>$1</li>');
        cleanText = cleanText.replace(/\n/g, '<br>');
    } else {
        cleanText = cleanText.replace(/\n/g, '<br>');
    }
    
    bubble.innerHTML = cleanText;
    log.appendChild(bubble);
    log.scrollTop = log.scrollHeight;
    return bubble;
}

// Send standard chat message to backend endpoint
function sendChatMessage(courseId) {
    const input = document.getElementById("chat-message-input");
    if (!input) return;

    const message = input.value.trim();
    if (!message) return;

    // Clear input
    input.value = "";

    // Append user message
    appendChatBubble("user", message);

    // Call API
    fetch(`/course/${courseId}/assistant/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            appendChatBubble("assistant", data.reply, true);
        } else {
            appendChatBubble("assistant", "Sorry, I encountered an issue processing your request.");
        }
    })
    .catch(err => {
        console.error("Chat API error:", err);
        appendChatBubble("assistant", "Network error. Please try again.");
    });
}

// Interactive Quiz States
let currentQuiz = [];
let quizIndex = 0;
let score = 0;

function triggerQuizAction(courseId) {
    appendChatBubble("user", "Generate Quiz");
    appendChatBubble("assistant", "Generating your practice quiz based on the course chapters...");
    
    fetch(`/course/${courseId}/assistant/quiz`)
    .then(res => res.json())
    .then(data => {
        if (data.success && data.quiz && data.quiz.length > 0) {
            currentQuiz = data.quiz;
            quizIndex = 0;
            score = 0;
            renderNextQuizQuestion(courseId);
        } else {
            appendChatBubble("assistant", "Could not load quiz questions.");
        }
    })
    .catch(err => {
        console.error("Quiz API error:", err);
        appendChatBubble("assistant", "Error loading quiz.");
    });
}

function renderNextQuizQuestion(courseId) {
    if (quizIndex >= currentQuiz.length) {
        appendChatBubble("assistant", `**Quiz Complete!** 🎉\n\nYou scored **${score} out of ${currentQuiz.length}**. Keep up the great work! You can take it again or proceed with other chapters.`);
        return;
    }
    
    const q = currentQuiz[quizIndex];
    appendChatBubble("assistant", `**Question ${quizIndex + 1}:** ${q.question}`);
    
    // Render options as interactive buttons in a custom bubble
    const log = document.getElementById("chat-history-log");
    const optContainer = document.createElement("div");
    optContainer.className = "chat-bubble assistant";
    optContainer.style.background = "transparent";
    optContainer.style.border = "none";
    optContainer.style.width = "100%";
    optContainer.style.maxWidth = "100%";
    optContainer.style.display = "flex";
    optContainer.style.flexDirection = "column";
    optContainer.style.gap = "0.5rem";
    optContainer.style.padding = "0";
    
    q.options.forEach(opt => {
        const btn = document.createElement("button");
        btn.className = "chat-action-btn";
        btn.style.width = "100%";
        btn.style.textAlign = "left";
        btn.textContent = opt;
        btn.onclick = () => selectQuizAnswer(courseId, btn, opt, q.answer);
        optContainer.appendChild(btn);
    });
    
    log.appendChild(optContainer);
    log.scrollTop = log.scrollHeight;
}

function selectQuizAnswer(courseId, clickedBtn, selectedValue, correctValue) {
    // Disable all options in the container parent
    const container = clickedBtn.parentElement;
    container.querySelectorAll("button").forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = "0.6";
        btn.style.cursor = "not-allowed";
        if (btn.textContent === correctValue) {
            btn.style.borderColor = "var(--text-success)";
            btn.style.color = "var(--text-success)";
            btn.style.background = "rgba(16, 185, 129, 0.1)";
        }
    });
    
    // Add user response bubble
    appendChatBubble("user", selectedValue);
    
    if (selectedValue === correctValue) {
        score++;
        appendChatBubble("assistant", "⭐ **Correct!** Great job.");
    } else {
        appendChatBubble("assistant", `❌ **Incorrect.** The correct answer is **${correctValue}**.`);
    }
    
    quizIndex++;
    // Delay slightly to show feedback before next question
    setTimeout(() => {
        renderNextQuizQuestion(courseId);
    }, 1500);
}

// Dynamic Slides / PPT Deck states
let lectureSlides = [];
let slideIndex = 0;

function triggerSlidesAction(courseId) {
    appendChatBubble("user", "Create PPT Slides");
    appendChatBubble("assistant", "Assembling lecture slide deck according to the syllabus...");
    
    fetch(`/course/${courseId}/assistant/slides`)
    .then(res => res.json())
    .then(data => {
        if (data.success && data.slides && data.slides.length > 0) {
            lectureSlides = data.slides;
            slideIndex = 0;
            openSlidesModal();
            appendChatBubble("assistant", "Presentation Deck ready! I have opened the slideshow viewer.");
        } else {
            appendChatBubble("assistant", "Could not generate lecture slides.");
        }
    })
    .catch(err => {
        console.error("Slides API error:", err);
        appendChatBubble("assistant", "Error generating slide deck.");
    });
}

function openSlidesModal() {
    const modal = document.getElementById("slides-deck-modal");
    if (modal) {
        modal.classList.add("active");
        renderSlide();
    }
}

function closeSlidesModal() {
    const modal = document.getElementById("slides-deck-modal");
    if (modal) {
        modal.classList.remove("active");
    }
}

function renderSlide() {
    const container = document.getElementById("slides-deck-container");
    const counter = document.getElementById("slide-deck-counter");
    if (!container || lectureSlides.length === 0) return;
    
    const slide = lectureSlides[slideIndex];
    counter.textContent = `Slide ${slideIndex + 1} of ${lectureSlides.length}`;
    
    // Build bullets list HTML
    let bulletsHTML = "";
    slide.points.forEach(pt => {
        bulletsHTML += `
            <li class="slide-bullet-item">
                <i class="fa-solid fa-angle-right"></i>
                <span>${pt}</span>
            </li>
        `;
    });
    
    container.innerHTML = `
        <div class="slide-card">
            <h2 class="slide-title">${slide.title}</h2>
            <h4 class="slide-subtitle">${slide.subtitle}</h4>
            <ul class="slide-bullets">
                ${bulletsHTML}
            </ul>
        </div>
    `;
    
    // Toggle navigation button disabled states
    document.getElementById("prev-slide-btn").disabled = (slideIndex === 0);
    document.getElementById("next-slide-btn").disabled = (slideIndex === lectureSlides.length - 1);
}

function changeSlide(direction) {
    slideIndex += direction;
    if (slideIndex < 0) slideIndex = 0;
    if (slideIndex >= lectureSlides.length) slideIndex = lectureSlides.length - 1;
    renderSlide();
}

function downloadSlides() {
    if (lectureSlides.length === 0) return;
    
    let textContent = "";
    lectureSlides.forEach((slide, idx) => {
        textContent += `========================================\n`;
        textContent += `SLIDE ${idx + 1}: ${slide.title.toUpperCase()}\n`;
        textContent += `SUBTITLE: ${slide.subtitle}\n`;
        textContent += `========================================\n`;
        slide.points.forEach(pt => {
            textContent += `• ${pt}\n`;
        });
        textContent += `\n\n`;
    });
    
    const blob = new Blob([textContent], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `AuraLearn_Lecture_Slides.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/* ==========================================================================
   GAMIFICATION SYSTEMS & INTERACTIVE CLIENT CODE PREVIEWERS
   ========================================================================== */

// Certificate Modal controllers
function openCertificateModal() {
    const modal = document.getElementById("certificate-modal");
    if (modal) {
        // Populate date dynamically on load
        const dateText = document.getElementById("cert-date-text");
        if (dateText) {
            dateText.textContent = new Date().toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric"
            });
        }
        modal.classList.add("active");
    }
}

function closeCertificateModal() {
    const modal = document.getElementById("certificate-modal");
    if (modal) {
        modal.classList.remove("active");
    }
}

function printCertificate() {
    window.print();
}

// Sandbox Practice Templates Dictionary
const EDITOR_TEMPLATES = {
    "python_basics": `# Python Basics: Variables and Loops
name = "AuraLearn Student"
xp_gained = 50

print("Welcome to your coding sandbox, " + name + "!")
print("Completing dynamic lessons will level up your profile.")

print("\\nExecuting quick loop:")
for i in range(1, 4):
    print("Code Module " + str(i) + " active...")

print("\\nReady! Update your code and click Run Code above.")`,

    "javascript_dom": `// JavaScript DOM Manipulation Example
// This code will run in the Visual Preview window!
document.body.style.backgroundColor = "#0e0e16";
document.body.style.color = "#f8fafc";
document.body.style.fontFamily = "'Outfit', sans-serif";
document.body.style.display = "flex";
document.body.style.flexDirection = "column";
document.body.style.alignItems = "center";
document.body.style.justifyContent = "center";
document.body.style.height = "100vh";
document.body.style.margin = "0";

const heading = document.createElement("h2");
heading.textContent = "Hello from JavaScript!";
heading.style.background = "linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%)";
heading.style.webkitBackgroundClip = "text";
heading.style.webkitTextFillColor = "transparent";
document.body.appendChild(heading);

const btn = document.createElement("button");
btn.textContent = "Trigger Magic Sparkle Alert";
btn.style.padding = "0.75rem 1.5rem";
btn.style.marginTop = "1rem";
btn.style.background = "#8b5cf6";
btn.style.border = "none";
btn.style.color = "#ffffff";
btn.style.borderRadius = "8px";
btn.style.cursor = "pointer";
btn.onclick = () => {
    alert("✨ Coding Challenge completed successfully! +10 XP awarded! ✨");
};
document.body.appendChild(btn);`,

    "html_css": `<!-- Glassmorphic Button Visual Preview -->
<style>
  body {
    background: radial-gradient(circle, #1a1a2e 0%, #0c0c14 100%);
    color: #ffffff;
    font-family: sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
  }
  .glass-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    padding: 2.5rem;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  }
  .btn-sparkle {
    background: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%);
    border: none;
    color: white;
    padding: 0.8rem 2rem;
    font-weight: bold;
    border-radius: 50px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    transition: transform 0.2s;
  }
  .btn-sparkle:hover {
    transform: scale(1.05);
  }
</style>

<div class="glass-card">
  <h3>Interactive UI Sandbox</h3>
  <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem;">Responsive component preview</p>
  <button class="btn-sparkle">Sparkle Now</button>
</div>`,

    "c_basics": `#include <stdio.h>

int main() {
    char name[] = "AuraLearn Student";
    int modules = 5;
    
    printf("Hello from C Language compiler sandbox, %s!\\n", name);
    printf("Syllabus modules active: %d\\n", modules);
    
    for(int i = 1; i <= 3; i++) {
        printf("C compiler iteration count: %d\\n", i);
    }
    return 0;
}`,

    "cpp_basics": `#include <iostream>
using namespace std;

class Learner {
public:
    string name = "AuraLearn Student";
    int current_level = 2;
    
    void showStatus() {
        cout << "C++ Compiler active in Sandbox!" << endl;
        cout << "Learner: " << name << " | Academic Level: " << current_level << endl;
    }
};

int main() {
    Learner student;
    student.showStatus();
    return 0;
}`,

    "java_basics": `public class Main {
    public static void main(String[] args) {
        String student = "AuraLearn Student";
        int currentXP = 450;
        
        System.out.println("Java Sandbox active and running!");
        System.out.println("Learner Profile: " + student);
        System.out.println("Current XP: " + currentXP);
        
        for (int i = 1; i <= 3; i++) {
            System.out.println("Java compilation module: " + i);
        }
    }
}`,

    "sql_basics": `-- SQL Database Simulator
-- Write standard SQL queries to select from courses table
SELECT id, title, category, skill_level, enrolled_count
FROM courses
WHERE category = 'Programming' OR category = 'Web Development'
ORDER BY enrolled_count DESC;`
};

// Sandbox runtime binder
document.addEventListener("DOMContentLoaded", () => {
    const templateSelect = document.getElementById("editor-template-select");
    const runBtn = document.getElementById("run-code-btn");
    const resetBtn = document.getElementById("reset-code-btn");
    const textarea = document.getElementById("editor-textarea");
    const terminal = document.getElementById("playground-terminal");
    const previewFrame = document.getElementById("playground-preview-frame");
    const previewWrapper = document.getElementById("playground-preview-wrapper");
    
    const consoleTab = document.getElementById("console-tab-btn");
    const previewTab = document.getElementById("preview-tab-btn");
    
    if (textarea && runBtn) {
        // Switch templates
        if (templateSelect) {
            templateSelect.addEventListener("change", () => {
                const val = templateSelect.value;
                textarea.value = EDITOR_TEMPLATES[val] || "";
                
                // Set default focus tab
                if (val === "javascript_dom" || val === "html_css") {
                    switchPlaygroundTab("preview");
                } else {
                    switchPlaygroundTab("console");
                }
            });
        }
        
        // Reset code block
        if (resetBtn) {
            resetBtn.addEventListener("click", () => {
                const val = templateSelect ? templateSelect.value : "python_basics";
                textarea.value = EDITOR_TEMPLATES[val] || "";
                terminal.innerHTML = '<div class="terminal-line system">&gt; Workspace reset to template default...</div>';
                if (previewFrame) previewFrame.srcdoc = "";
            });
        }
        
        // Compile trigger
        runBtn.addEventListener("click", () => {
            const val = templateSelect ? templateSelect.value : "python_basics";
            const code = textarea.value;
            
            if (val === "javascript_dom" || val === "html_css") {
                switchPlaygroundTab("preview");
                executeJSHTMLCode(code);
            } else {
                switchPlaygroundTab("console");
                executeBackendLanguageMock(val, code);
            }
        });
        
        // Tab triggers
        if (consoleTab && previewTab) {
            consoleTab.addEventListener("click", () => switchPlaygroundTab("console"));
            previewTab.addEventListener("click", () => switchPlaygroundTab("preview"));
        }
    }
    
    function switchPlaygroundTab(tab) {
        if (!consoleTab || !previewTab) return;
        if (tab === "console") {
            consoleTab.classList.add("active");
            previewTab.classList.remove("active");
            terminal.style.display = "block";
            previewWrapper.style.display = "none";
        } else {
            consoleTab.classList.remove("active");
            previewTab.classList.add("active");
            terminal.style.display = "none";
            previewWrapper.style.display = "block";
        }
    }
    
    function executeBackendLanguageMock(lang, code) {
        terminal.innerHTML = `<div class="terminal-line system">&gt; Initializing local ${lang.replace('_basics','').toUpperCase()} compiler/sandbox...</div>`;
        setTimeout(() => {
            terminal.innerHTML += `<div class="terminal-line system">&gt; Running local application script:</div>`;
            
            try {
                const cleanCode = code.replace(/\r/g, "");
                const lines = cleanCode.split("\n");
                let variables = {};
                let inLoop = false;
                let loopRange = 0;
                let loopVar = "";
                let loopBody = [];
                
                if (lang === "sql_basics") {
                    // SQL query simulation
                    if (cleanCode.toLowerCase().includes("select") && cleanCode.toLowerCase().includes("from courses")) {
                        setTimeout(() => {
                            appendTerminalLine("+----+--------------------------------------------+-----------------+-------------+----------+");
                            appendTerminalLine("| ID | Title                                      | Category        | Skill Level | Enrolled |");
                            appendTerminalLine("+----+--------------------------------------------+-----------------+-------------+----------+");
                            appendTerminalLine("| 3  | Modern Full-Stack JavaScript with Node.js  | Web Development | Intermediate| 16       |");
                            appendTerminalLine("| 1  | Python Programming for Beginners           | Programming     | Beginner    | 12       |");
                            appendTerminalLine("| 7  | Building RESTful APIs with Flask and Python| Web Development | Intermediate| 10       |");
                            appendTerminalLine("+----+--------------------------------------------+-----------------+-------------+----------+");
                            terminal.innerHTML += '<div class="terminal-line system" style="color:var(--text-success); font-weight:bold; margin-top:0.50rem;">&gt; SQL Query executed successfully. +10 XP earned!</div>';
                        }, 200);
                    } else {
                        appendTerminalLine("Error: Only SELECT queries from table 'courses' are supported in this sandbox environment.");
                    }
                    return;
                }
                
                lines.forEach(line => {
                    const l = line.trim();
                    if (!l || l.startsWith("//") || l.startsWith("#include") || l.startsWith("using namespace") || l.startsWith("import ")) return;
                    
                    // Python compiler logic
                    if (lang === "python_basics") {
                        if (l.includes("=") && !l.startsWith("for") && !l.includes("==")) {
                            const parts = l.split("=");
                            variables[parts[0].trim()] = parts[1].trim().replace(/['"]/g, "");
                            return;
                        }
                        if (l.startsWith("print(") && l.endsWith(")")) {
                            const expr = l.slice(6, -1);
                            let val = evaluatePrintExpression(expr, variables);
                            if (inLoop) loopBody.push(val);
                            else appendTerminalLine(val);
                            return;
                        }
                        if (l.startsWith("for ") && l.includes(" in range(") && l.endsWith(":")) {
                            inLoop = true;
                            loopVar = l.split(" ")[1];
                            const rangeStr = l.substring(l.indexOf("range(") + 6, l.lastIndexOf("):"));
                            const rangeParts = rangeStr.split(",");
                            let end = rangeParts.length > 1 ? parseInt(rangeParts[1].trim()) : parseInt(rangeParts[0].trim());
                            let start = rangeParts.length > 1 ? parseInt(rangeParts[0].trim()) : 0;
                            loopRange = end - start;
                            return;
                        }
                    }
                    
                    // C Compiler logic
                    if (lang === "c_basics") {
                        if ((l.startsWith("char ") || l.startsWith("int ")) && l.includes("=")) {
                            const assignStr = l.substring(l.indexOf(" ") + 1).replace(";", "").trim();
                            const parts = assignStr.split("=");
                            let varName = parts[0].trim();
                            if (varName.includes("[")) varName = varName.substring(0, varName.indexOf("["));
                            let varVal = parts[1].trim().replace(/['"]/g, "");
                            variables[varName] = varVal;
                            return;
                        }
                        if (l.startsWith("printf(") && l.endsWith(");")) {
                            const inner = l.slice(7, -2);
                            let val = evaluateCPrintf(inner, variables);
                            if (inLoop) loopBody.push(val);
                            else appendTerminalLine(val);
                            return;
                        }
                        if (l.startsWith("for") && l.includes("int ") && l.includes("<=")) {
                            inLoop = true;
                            const loopExpr = l.substring(l.indexOf("(") + 1, l.lastIndexOf(")"));
                            const loopParts = loopExpr.split(";");
                            const initPart = loopParts[0].trim();
                            loopVar = initPart.substring(initPart.indexOf("int ") + 4, initPart.indexOf("=")).trim();
                            const condPart = loopParts[1].trim();
                            const limitVal = parseInt(condPart.substring(condPart.indexOf("<=") + 2).trim());
                            const initVal = parseInt(initPart.substring(initPart.indexOf("=") + 1).trim());
                            loopRange = limitVal - initVal + 1;
                            return;
                        }
                    }
                    
                    // C++ Compiler logic
                    if (lang === "cpp_basics") {
                        if ((l.startsWith("string ") || l.startsWith("int ")) && l.includes("=")) {
                            const assignStr = l.substring(l.indexOf(" ") + 1).replace(";", "").trim();
                            const parts = assignStr.split("=");
                            variables[parts[0].trim()] = parts[1].trim().replace(/['"]/g, "");
                            return;
                        }
                        if (l.startsWith("cout ") && l.includes("<<")) {
                            let val = evaluateCppCout(l, variables);
                            if (inLoop) loopBody.push(val);
                            else appendTerminalLine(val);
                            return;
                        }
                    }
                    
                    // Java Compiler logic
                    if (lang === "java_basics") {
                        if ((l.startsWith("String ") || l.startsWith("int ")) && l.includes("=")) {
                            const assignStr = l.substring(l.indexOf(" ") + 1).replace(";", "").trim();
                            const parts = assignStr.split("=");
                            variables[parts[0].trim()] = parts[1].trim().replace(/['"]/g, "");
                            return;
                        }
                        if (l.startsWith("System.out.println(") && l.endsWith(");")) {
                            const inner = l.slice(19, -2);
                            let val = evaluateJavaPrint(inner, variables);
                            if (inLoop) loopBody.push(val);
                            else appendTerminalLine(val);
                            return;
                        }
                        if (l.startsWith("for") && l.includes("int ") && l.includes("<=")) {
                            inLoop = true;
                            const loopExpr = l.substring(l.indexOf("(") + 1, l.lastIndexOf(")"));
                            const loopParts = loopExpr.split(";");
                            const initPart = loopParts[0].trim();
                            loopVar = initPart.substring(initPart.indexOf("int ") + 4, initPart.indexOf("=")).trim();
                            const condPart = loopParts[1].trim();
                            const limitVal = parseInt(condPart.substring(condPart.indexOf("<=") + 2).trim());
                            const initVal = parseInt(initPart.substring(initPart.indexOf("=") + 1).trim());
                            loopRange = limitVal - initVal + 1;
                            return;
                        }
                    }
                });
                
                if (inLoop) {
                    for (let step = 1; step <= loopRange; step++) {
                        loopBody.forEach(exprTemplate => {
                            let output = exprTemplate.replace("str(" + loopVar + ")", step).replace(loopVar, step);
                            appendTerminalLine(output);
                        });
                    }
                }
                
                terminal.innerHTML += `<div class="terminal-line system" style="color:var(--text-success); font-weight:bold; margin-top:0.50rem;">&gt; ${lang.replace('_basics','').toUpperCase()} program execution successful. +10 XP earned!</div>`;
            } catch (e) {
                terminal.innerHTML += `<div class="terminal-line error">CompilationError: Failed to compile statements: ${e.message}</div>`;
            }
        }, 300);
    }
    
    function evaluatePrintExpression(expr, variables) {
        const parts = expr.split("+");
        let output = "";
        parts.forEach(p => {
            let val = p.trim();
            if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
                output += val.slice(1, -1);
            } else if (val.startsWith("str(") && val.endsWith(")")) {
                const varInner = val.slice(4, -1);
                output += variables[varInner] !== undefined ? variables[varInner] : varInner;
            } else if (variables[val] !== undefined) {
                output += variables[val];
            } else {
                output += val.replace(/\\n/g, "\n");
            }
        });
        return output;
    }
    
    function evaluateCPrintf(expr, variables) {
        const commaIndex = expr.indexOf(",");
        if (commaIndex === -1) {
            return expr.replace(/['"]/g, "").replace(/\\n/g, "\n");
        }
        
        let formatStr = expr.substring(0, commaIndex).trim().replace(/['"]/g, "");
        const argsStr = expr.substring(commaIndex + 1).trim();
        const args = argsStr.split(",").map(a => a.trim());
        
        args.forEach(arg => {
            const val = variables[arg] !== undefined ? variables[arg] : arg;
            if (formatStr.includes("%s")) formatStr = formatStr.replace("%s", val);
            else if (formatStr.includes("%d")) formatStr = formatStr.replace("%d", val);
        });
        return formatStr.replace(/\\n/g, "\n");
    }
    
    function evaluateCppCout(line, variables) {
        const streamParts = line.substring(line.indexOf("<<") + 2).replace(";", "").split("<<").map(p => p.trim());
        let output = "";
        streamParts.forEach(p => {
            if (p === "endl") {
                output += "\n";
            } else if ((p.startsWith('"') && p.endsWith('"')) || (p.startsWith("'") && p.endsWith("'"))) {
                output += p.slice(1, -1);
            } else if (variables[p] !== undefined) {
                output += variables[p];
            } else {
                output += p;
            }
        });
        return output;
    }
    
    function evaluateJavaPrint(expr, variables) {
        const parts = expr.split("+");
        let output = "";
        parts.forEach(p => {
            let val = p.trim();
            if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
                output += val.slice(1, -1);
            } else if (variables[val] !== undefined) {
                output += variables[val];
            } else {
                output += val;
            }
        });
        return output;
    }
    
    function appendTerminalLine(text) {
        const line = document.createElement("div");
        line.className = "terminal-line";
        line.innerHTML = text.replace(/\n/g, "<br>");
        terminal.appendChild(line);
        terminal.scrollTop = terminal.scrollHeight;
    }
    
    function executeJSHTMLCode(code) {
        if (!previewFrame) return;
        previewFrame.srcdoc = code;
    }
});

