import database
import gamification
import json
import random
import uuid
import datetime

# Comprehensive Question Banks mapped by Course Title keywords or Categories
COURSE_EXAM_BANKS = {
    "python": [
        {
            "id": 1,
            "question": "What will be the output of `print(type([1, 2, 3]))` in Python 3?",
            "options": ["<class 'list'>", "<class 'array'>", "<class 'tuple'>", "<class 'set'>"],
            "answer": 0,
            "explanation": "In Python, square brackets `[]` define a built-in `list` object."
        },
        {
            "id": 2,
            "question": "Which keyword is used to define an anonymous or inline function in Python?",
            "options": ["def", "lambda", "func", "inline"],
            "answer": 1,
            "explanation": "`lambda` is used in Python to create small, one-line anonymous functions."
        },
        {
            "id": 3,
            "question": "How do you achieve method inheritance in a Python class definition?",
            "options": ["class Child(Parent):", "class Child extends Parent:", "class Child implements Parent:", "class Child -> Parent:"],
            "answer": 0,
            "explanation": "In Python, inheritance is declared by passing the parent class name in parentheses: `class Child(Parent):`."
        },
        {
            "id": 4,
            "question": "What is the primary difference between a Python `list` and a `tuple`?",
            "options": [
                "Lists are immutable, tuples are mutable",
                "Lists are mutable, tuples are immutable",
                "Lists can only store numbers, tuples can store any data type",
                "There is no difference in memory or mutability"
            ],
            "answer": 1,
            "explanation": "Python lists can be modified after creation (mutable), whereas tuples cannot be altered (immutable)."
        },
        {
            "id": 5,
            "question": "What does the `*args` syntax in a function parameter list accomplish?",
            "options": [
                "Allows passing a dictionary of named keyword arguments",
                "Allows passing a variable number of non-keyword positional arguments as a tuple",
                "Forces the function to execute asynchronously",
                "Imports external module arguments automatically"
            ],
            "answer": 1,
            "explanation": "`*args` allows a function to accept any number of positional arguments, collected as a tuple."
        },
        {
            "id": 6,
            "question": "What is the result of the expression `'hello'.upper()[::-1]`?",
            "options": ["'OLLEH'", "'HELLO'", "'olleh'", "Throws an IndexError"],
            "answer": 0,
            "explanation": "`.upper()` converts the string to `'HELLO'`, and `[::-1]` slices and reverses it to `'OLLEH'`."
        },
        {
            "id": 7,
            "question": "Which Python keyword is executed in a `try-except` block regardless of whether an exception was raised?",
            "options": ["catch", "always", "finally", "ensure"],
            "answer": 2,
            "explanation": "The `finally` block is always executed after the try and except blocks, ensuring clean-up operations."
        },
        {
            "id": 8,
            "question": "What is a Python decorator and how is it syntactically applied?",
            "options": [
                "A visual CSS rule applied via `#decorator`",
                "A function that takes another function and extends its behavior, prefixed with `@`",
                "A built-in garbage collector command",
                "A specialized loop for dictionary keys"
            ],
            "answer": 1,
            "explanation": "A decorator wraps a function to extend or modify its behavior without modifying the source function directly, using `@decorator_name`."
        },
        {
            "id": 9,
            "question": "What does a generator function use instead of the standard `return` statement to stream values lazily?",
            "options": ["yield", "emit", "stream", "next"],
            "answer": 0,
            "explanation": "The `yield` keyword suspends a function's execution and sends a value back to the caller, producing an iterator."
        },
        {
            "id": 10,
            "question": "Which of the following creates a clean virtual environment using Python's standard library?",
            "options": ["pip create env", "python -m venv myenv", "npm init venv", "python --make-virtual-dir"],
            "answer": 1,
            "explanation": "`python -m venv <name>` creates an isolated Python virtual environment using the built-in `venv` module."
        }
    ],

    "javascript": [
        {
            "id": 1,
            "question": "What is the difference between `let`, `const`, and `var` in modern JavaScript?",
            "options": [
                "`var` is block-scoped, while `let` and `const` are function-scoped",
                "`let` and `const` are block-scoped, while `var` is function-scoped",
                "`const` variables can be freely reassigned anywhere",
                "`let` is hoisted globally without a temporal dead zone"
            ],
            "answer": 1,
            "explanation": "Modern ES6 `let` and `const` are strictly block-scoped `{...}`, whereas legacy `var` is function-scoped."
        },
        {
            "id": 2,
            "question": "What is the result of `typeof null` in standard JavaScript?",
            "options": ["'null'", "'undefined'", "'object'", "'boolean'"],
            "answer": 2,
            "explanation": "`typeof null` returning `'object'` is a historical quirk and official standard behavior of JavaScript since its inception."
        },
        {
            "id": 3,
            "question": "How does the JavaScript Event Loop handle asynchronous promises?",
            "options": [
                "By placing Promise `.then()` callbacks in the Microtask Queue",
                "By creating a new operating system thread for each promise",
                "By executing them synchronously and blocking the main thread",
                "By delegating them to the CSS rendering engine"
            ],
            "answer": 0,
            "explanation": "Promise callbacks are placed into the Microtask queue, which has higher priority than the standard Macrotask queue (e.g., setTimeout)."
        },
        {
            "id": 4,
            "question": "What does the array method `.map()` return?",
            "options": [
                "The sum of all items in the array",
                "A new array populated with the results of calling a provided function on every element",
                "The first index matching the predicate function",
                "A mutated in-place reference of the original array"
            ],
            "answer": 1,
            "explanation": "`.map()` returns a new array with transformed elements without mutating the original input array."
        },
        {
            "id": 5,
            "question": "Which syntax correctly destructures `name` and `age` from an object `user`?",
            "options": [
                "const [name, age] = user;",
                "const { name, age } = user;",
                "const user -> (name, age);",
                "const name, age = extract(user);"
            ],
            "answer": 1,
            "explanation": "Object destructuring uses curly braces matching the key names: `const { name, age } = user;`."
        },
        {
            "id": 6,
            "question": "What is the purpose of `async/await` in modern JavaScript?",
            "options": [
                "To compile JavaScript into machine code ahead of time",
                "To write asynchronous Promise-based code in a clean, synchronous-looking style",
                "To prevent any errors from ever being thrown",
                "To force synchronous multi-threading on CPU cores"
            ],
            "answer": 1,
            "explanation": "`async/await` provides clean syntactic sugar over Promises, making asynchronous code easier to read and maintain."
        },
        {
            "id": 7,
            "question": "Which Node.js core module is used to create an HTTP web server without external frameworks?",
            "options": ["fs", "http", "path", "net/socket"],
            "answer": 1,
            "explanation": "The built-in `http` module (`http.createServer(...)`) enables creating HTTP web servers directly in Node.js."
        },
        {
            "id": 8,
            "question": "What does `===` (strict equality) check in JavaScript compared to `==` (loose equality)?",
            "options": [
                "It checks value equality with automatic type coercion",
                "It checks both value and data type equality without type coercion",
                "It only checks object memory addresses",
                "It performs a cryptographic hash comparison"
            ],
            "answer": 1,
            "explanation": "`===` checks that both the value and the type are identical, without performing implicit type coercion."
        },
        {
            "id": 9,
            "question": "What is a closure in JavaScript?",
            "options": [
                "A function that has access to variables in its outer lexical scope even after that parent function has closed",
                "A method to terminate the browser window",
                "A syntax error caused by an unclosed curly bracket",
                "A private variable only accessible by the browser engine"
            ],
            "answer": 0,
            "explanation": "A closure is the combination of a function bundled together with references to its surrounding lexical environment."
        },
        {
            "id": 10,
            "question": "In Express.js, what is middleware?",
            "options": [
                "A database driver plugin",
                "A function that has access to the request (`req`), response (`res`), and the next middleware (`next`) in the request-response cycle",
                "A frontend CSS library",
                "An automated load-balancer"
            ],
            "answer": 1,
            "explanation": "Middleware functions in Express execute during the request-response lifecycle and can modify `req`/`res` or terminate requests."
        }
    ],

    "web": [
        {
            "id": 1,
            "question": "Which HTML5 semantic element is recommended for independent, self-contained content such as a blog post or news card?",
            "options": ["<div>", "<section>", "<article>", "<aside>"],
            "answer": 2,
            "explanation": "The `<article>` element represents a complete, or self-contained, composition in a document."
        },
        {
            "id": 2,
            "question": "In the CSS Box Model, which layer is immediately surrounding the content area before border and margin?",
            "options": ["Padding", "Margin", "Border", "Outline"],
            "answer": 0,
            "explanation": "The box model layers from inside out are: Content -> Padding -> Border -> Margin."
        },
        {
            "id": 3,
            "question": "Which CSS Flexbox property aligns items along the cross axis (vertical when flex-direction is row)?",
            "options": ["justify-content", "align-items", "flex-wrap", "align-content"],
            "answer": 1,
            "explanation": "`align-items` governs the alignment of flex items along the perpendicular cross axis."
        },
        {
            "id": 4,
            "question": "What is the purpose of the CSS `box-sizing: border-box;` rule?",
            "options": [
                "It makes borders 3D styled",
                "It includes padding and border in the element's total calculated width and height",
                "It forces all elements to behave as inline tags",
                "It hides any overflow beyond the screen boundary"
            ],
            "answer": 1,
            "explanation": "`border-box` includes padding and borders in the element's declared width and height, preventing layout breakage."
        },
        {
            "id": 5,
            "question": "Which CSS Grid property specifies equal multi-column fraction distribution across available space?",
            "options": [
                "grid-template-columns: repeat(3, 1fr);",
                "grid-columns: 3 auto;",
                "display: multi-grid(3);",
                "column-count: 3fr;"
            ],
            "answer": 0,
            "explanation": "`grid-template-columns: repeat(3, 1fr);` creates 3 flexible fractional tracks sharing space evenly."
        },
        {
            "id": 6,
            "question": "How do you write a media query in CSS targeting mobile screens with a max width of 768px?",
            "options": [
                "@media screen and (max-width: 768px) { ... }",
                "@screen-width (<= 768px) { ... }",
                "@mobile (768px) { ... }",
                "@device-query (max: 768) { ... }"
            ],
            "answer": 0,
            "explanation": "`@media screen and (max-width: 768px)` defines standard responsive CSS rules for screen viewports up to 768px."
        },
        {
            "id": 7,
            "question": "What does the `rem` unit in CSS measure relative to?",
            "options": [
                "The font-size of the immediate parent element",
                "The font-size of the root `<html>` element",
                "The viewport height (1% of viewport)",
                "The physical millimeters of the screen display"
            ],
            "answer": 1,
            "explanation": "`rem` stands for Root EM and calculates proportional sizing relative to the root `<html>` element's font size."
        },
        {
            "id": 8,
            "question": "Which meta tag is critical in HTML `<head>` to ensure proper mobile viewport scaling?",
            "options": [
                "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
                "<meta http-equiv='responsive' content='mobile=true'>",
                "<meta name='scale' content='auto'>",
                "<meta layout='flex'>"
            ],
            "answer": 0,
            "explanation": "The viewport meta tag instructs mobile browsers to render at device width with an initial 1.0 zoom scale."
        }
    ],

    "react": [
        {
            "id": 1,
            "question": "What is the Virtual DOM in React and why does React use it?",
            "options": [
                "A direct replica of the server filesystem for hot reloading",
                "A lightweight in-memory representation of the real DOM used to compute minimal DOM updates via diffing",
                "A proprietary browser plugin required to run JSX",
                "A database indexing engine for web browsers"
            ],
            "answer": 1,
            "explanation": "React uses the Virtual DOM to batch and reconcile UI changes efficiently before updating the real browser DOM."
        },
        {
            "id": 2,
            "question": "Which React hook is used to manage local component state?",
            "options": ["useEffect", "useReducer", "useState", "useRef"],
            "answer": 2,
            "explanation": "`useState` is the fundamental hook for declaring and updating reactive state inside functional components."
        },
        {
            "id": 3,
            "question": "What does an empty dependency array `[]` in `useEffect(() => { ... }, [])` mean?",
            "options": [
                "The effect will run after every single component render",
                "The effect will only run once when the component mounts",
                "The effect is disabled and will never execute",
                "The effect will cause an infinite re-render loop"
            ],
            "answer": 1,
            "explanation": "An empty dependency array `[]` tells React to run the effect only on the initial mount, similar to `componentDidMount`."
        },
        {
            "id": 4,
            "question": "Why is it important to provide a unique `key` prop when rendering lists of elements in React?",
            "options": [
                "To apply unique CSS styles to each list item",
                "To help React identify which items have changed, been added, or been removed during reconciliation",
                "To encrypt data passed to child components",
                "To enable automatic database caching"
            ],
            "answer": 1,
            "explanation": "Keys give elements a stable identity across renders, allowing React to minimize re-renders when lists change."
        },
        {
            "id": 5,
            "question": "How do you pass data from a parent component down to a child component in React?",
            "options": ["Using Props", "Using HTML cookies", "Using global window variables", "Using SQL queries"],
            "answer": 0,
            "explanation": "Props (short for properties) are the standard way data flows downwards from parent to child in React."
        },
        {
            "id": 6,
            "question": "What is the purpose of React Context (`createContext` & `useContext`)?",
            "options": [
                "To share state globally across the component tree without prop drilling",
                "To create WebGL graphics animations",
                "To connect directly to a remote SQLite database",
                "To replace all standard HTML elements with custom canvas tags"
            ],
            "answer": 0,
            "explanation": "React Context provides a way to pass data through the component tree without manually passing props at every level."
        },
        {
            "id": 7,
            "question": "What is a React Custom Hook?",
            "options": [
                "A native browser C++ extension",
                "A JavaScript function whose name starts with 'use' and that can call other React hooks",
                "A special CSS animation transition",
                "An automated test runner"
            ],
            "answer": 1,
            "explanation": "Custom hooks allow you to extract and reuse stateful logic across multiple components into clean functions starting with `use`."
        },
        {
            "id": 8,
            "question": "What is the correct way to update state that depends on the previous state value in `useState`?",
            "options": [
                "setCount(count + 1)",
                "setCount(prevCount => prevCount + 1)",
                "count = count + 1",
                "this.state.count++"
            ],
            "answer": 1,
            "explanation": "Passing an updater function `prev => prev + 1` guarantees access to the latest state value even during batched asynchronous updates."
        }
    ],

    "sql": [
        {
            "id": 1,
            "question": "Which SQL clause is used to filter records resulting from a `GROUP BY` aggregate function?",
            "options": ["WHERE", "HAVING", "LIMIT", "FILTER"],
            "answer": 1,
            "explanation": "`HAVING` filters rows after aggregation (`GROUP BY`), whereas `WHERE` filters rows before aggregation."
        },
        {
            "id": 2,
            "question": "What does an `INNER JOIN` return in SQL?",
            "options": [
                "All rows from the left table and matched rows from the right table",
                "Only the rows that have matching values in both tables",
                "All possible cartesian product combinations of both tables",
                "All rows from both tables including non-matching NULL rows"
            ],
            "answer": 1,
            "explanation": "An `INNER JOIN` selects records that have matching values in both joined tables based on the join predicate."
        },
        {
            "id": 3,
            "question": "What is a Common Table Expression (CTE) in SQL?",
            "options": [
                "A temporary named result set defined using the `WITH` keyword",
                "A permanent table stored on physical disk",
                "A database user privilege setting",
                "A hardware caching mechanism"
            ],
            "answer": 0,
            "explanation": "A CTE is defined using `WITH cte_name AS (...)` to create a temporary, readable result set for the query."
        },
        {
            "id": 4,
            "question": "Which window function assigns a unique sequential integer to each row within a partition?",
            "options": ["RANK()", "DENSE_RANK()", "ROW_NUMBER()", "COUNT_DISTINCT()"],
            "answer": 2,
            "explanation": "`ROW_NUMBER() OVER (...)` assigns an uninterrupted sequential number (1, 2, 3...) to each row in the partition."
        },
        {
            "id": 5,
            "question": "What is database normalization and what is the primary benefit of Third Normal Form (3NF)?",
            "options": [
                "Increasing table duplication to speed up read operations",
                "Organizing table columns to reduce data redundancy and eliminate transitive dependencies",
                "Converting all text columns into binary blob formats",
                "Encrypting user passwords at the database level"
            ],
            "answer": 1,
            "explanation": "Normalization organizes database structures to eliminate data redundancy and anomalies; 3NF removes transitive dependencies."
        },
        {
            "id": 6,
            "question": "What is the role of a Database Index (e.g., B-Tree index)?",
            "options": [
                "To speed up data retrieval operations at the cost of additional storage and slower writes",
                "To automatically compress image files",
                "To translate SQL syntax into Python scripts",
                "To prevent any DELETE operations from executing"
            ],
            "answer": 0,
            "explanation": "Indexes provide fast lookup paths (B-Trees) to locate rows quickly without scanning the entire table."
        },
        {
            "id": 7,
            "question": "What are the ACID properties in relational database transactions?",
            "options": [
                "Atomicity, Consistency, Isolation, Durability",
                "Access, Control, Integrity, Data",
                "Async, Cache, Index, Distribution",
                "Authentication, Cipher, Identity, Decryption"
            ],
            "answer": 0,
            "explanation": "ACID guarantees that database transactions are processed reliably: Atomicity, Consistency, Isolation, and Durability."
        },
        {
            "id": 8,
            "question": "Which SQL constraint ensures that all values in a specific column are unique and not NULL?",
            "options": ["FOREIGN KEY", "PRIMARY KEY", "CHECK", "DEFAULT"],
            "answer": 1,
            "explanation": "A `PRIMARY KEY` constraint uniquely identifies each record in a table and implicitly enforces NOT NULL and UNIQUE."
        }
    ],

    "data_ai": [
        {
            "id": 1,
            "question": "What is the primary difference between Supervised and Unsupervised Learning?",
            "options": [
                "Supervised learning uses labeled training data, while unsupervised learning discovers patterns in unlabeled data",
                "Supervised learning requires GPU hardware, unsupervised only runs on CPU",
                "Supervised learning only predicts text, unsupervised only handles audio",
                "There is no difference; they are interchangeable terms"
            ],
            "answer": 0,
            "explanation": "Supervised learning trains models on input-output pairs with known targets, while unsupervised learning finds clusters and patterns without labels."
        },
        {
            "id": 2,
            "question": "What metric is commonly used to evaluate a binary classification model when class distribution is highly imbalanced?",
            "options": ["Accuracy", "F1-Score / Precision-Recall AUC", "Mean Squared Error", "R-squared"],
            "answer": 1,
            "explanation": "F1-score (harmonic mean of precision and recall) is far more informative than raw accuracy on skewed or imbalanced datasets."
        },
        {
            "id": 3,
            "question": "In deep learning, what is the role of the Backpropagation algorithm?",
            "options": [
                "To compute the gradient of the loss function with respect to weights using the chain rule for gradient descent optimization",
                "To convert RGB images into grayscale tensors",
                "To initialize random weights before training",
                "To visualize neural network activations on screen"
            ],
            "answer": 0,
            "explanation": "Backpropagation computes partial derivatives of the loss function with respect to network parameters to update weights via gradient descent."
        },
        {
            "id": 4,
            "question": "In Pandas, which method is used to aggregate data by one or more categories and calculate group summaries?",
            "options": [".groupby()", ".pivot_table()", ".aggregate_rows()", ".category_split()"],
            "answer": 0,
            "explanation": "`.groupby(['column']).mean()` or `.groupby(['column']).agg(...)` splits data into groups for summary operations."
        },
        {
            "id": 5,
            "question": "What is Overfitting in machine learning and how can it be mitigated?",
            "options": [
                "When a model performs poorly on training data; mitigated by reducing dataset size",
                "When a model memorizes training noise and fails to generalize to unseen test data; mitigated by regularization, dropout, and cross-validation",
                "When computer RAM runs out during training; mitigated by buying more RAM",
                "When data has too few features; mitigated by adding polynomial terms"
            ],
            "answer": 1,
            "explanation": "Overfitting occurs when a model fits training data too closely. It is mitigated by regularization (L1/L2), dropout, and cross-validation."
        },
        {
            "id": 6,
            "question": "What core mechanism enables Transformer architectures (such as BERT, GPT) to process entire sequences in parallel?",
            "options": ["Self-Attention Mechanism", "Recurrent LSTM Gates", "Random Forest Ensembles", "Markov Decision Chains"],
            "answer": 0,
            "explanation": "Self-attention computes dynamic weights between all tokens in a sequence simultaneously without sequential recurrence."
        },
        {
            "id": 7,
            "question": "In Natural Language Processing (NLP), what does TF-IDF represent?",
            "options": [
                "TensorFlow Image Data Format",
                "Term Frequency - Inverse Document Frequency, measuring how important a word is to a document within a corpus",
                "Text Formatting and International Display Feature",
                "Token Filtering with Iterative Decay Factor"
            ],
            "answer": 1,
            "explanation": "TF-IDF quantifies the relative importance of words by scaling frequency against how common the word is across all documents."
        },
        {
            "id": 8,
            "question": "What is Few-Shot Prompting in Generative AI?",
            "options": [
                "Giving the model a few input-output demonstration examples within the prompt context before the target task",
                "Limiting the model to generating only 3 words",
                "Re-training the neural network parameters with few epochs",
                "Asking the user to prompt the AI 3 times repeatedly"
            ],
            "answer": 0,
            "explanation": "Few-shot prompting provides a few explicit example demonstrations in the prompt to steer the LLM towards the desired response format."
        }
    ],

    "design": [
        {
            "id": 1,
            "question": "In UX/UI design, what is the 'F-Shaped' reading pattern?",
            "options": [
                "A keyboard layout standard for designers",
                "A visual scanning behavior where users primarily read horizontal top lines followed by shorter horizontal glances down the left edge",
                "A grid layout structure for photo galleries",
                "A color palette formula using complementary hues"
            ],
            "answer": 1,
            "explanation": "Eye-tracking studies show web readers often scan pages in an F-shaped pattern: top horizontal bar, second shorter bar, and vertical left stripe."
        },
        {
            "id": 2,
            "question": "What does the WCAG AA accessibility guideline recommend as the minimum contrast ratio for normal text?",
            "options": ["2:1", "3:1", "4.5:1", "7:1"],
            "answer": 2,
            "explanation": "WCAG 2.1 Level AA requires a minimum contrast ratio of 4.5:1 for normal body text and 3:1 for large text."
        },
        {
            "id": 3,
            "question": "In Figma, what feature allows components to automatically adjust their dimensions and padding when content changes?",
            "options": ["Auto Layout", "Smart Animate", "Vector Pen", "Boolean Union"],
            "answer": 0,
            "explanation": "Auto Layout enables responsive component frames that resize dynamically according to their inner content and defined padding."
        },
        {
            "id": 4,
            "question": "What are Design Tokens in modern design systems?",
            "options": [
                "Cryptocurrency coins used to purchase Figma plugins",
                "Centralized, named variables storing design values (colors, spacing, typography, elevation) shared across design and code",
                "Icons representing team member roles",
                "Authentication keys for web apps"
            ],
            "answer": 1,
            "explanation": "Design tokens are semantic key-value pairs (e.g. `color-primary: #3b82f6`) ensuring brand consistency across platforms."
        },
        {
            "id": 5,
            "question": "What is a Micro-Interaction in mobile and web UX?",
            "options": [
                "A 1-second video advertisement",
                "Subtle, functional animations or feedback moments triggered by user actions (such as a heart toggle, button ripple, or progress pulse)",
                "A survey popup asking for app store ratings",
                "A miniature layout icon on mobile screens"
            ],
            "answer": 1,
            "explanation": "Micro-interactions are subtle visual or haptic feedback animations that inform users about system state changes and delight the user."
        },
        {
            "id": 6,
            "question": "What is the difference between a Wireframe and a High-Fidelity Prototype?",
            "options": [
                "Wireframes focus on structure and layout hierarchy without detailed styling; prototypes include full visuals, colors, and interactive click flows",
                "Wireframes are written in Python; prototypes are built in HTML",
                "Prototypes are only for mobile apps; wireframes are for desktop",
                "There is no difference"
            ],
            "answer": 0,
            "explanation": "Wireframes represent low-fidelity skeletal layouts, whereas high-fidelity prototypes simulate the final look, feel, and interactive behavior."
        },
        {
            "id": 7,
            "question": "What is Atomic Design methodology?",
            "options": [
                "A nuclear physics theory applied to software",
                "A design system hierarchy organizing UI elements into Atoms, Molecules, Organisms, Templates, and Pages",
                "A responsive design rule for ultra-small smartwatches",
                "A color system based on elemental spectra"
            ],
            "answer": 1,
            "explanation": "Atomic Design breaks down UI components hierarchically from foundational atoms up to full pages."
        },
        {
            "id": 8,
            "question": "What is visual hierarchy in interface design?",
            "options": [
                "Arranging elements in order of visual importance using scale, contrast, color, weight, and white space",
                "Listing user permissions alphabetically",
                "Hiding buttons until the mouse hovers over them",
                "Placing the largest graphic at the bottom of the page"
            ],
            "answer": 0,
            "explanation": "Visual hierarchy guides the user's attention through a layout in order of priority using size, contrast, and spacing."
        }
    ],

    "business": [
        {
            "id": 1,
            "question": "In Agile and Scrum methodology, what is the role of the Product Owner?",
            "options": [
                "To manage daily developer schedules and code reviews",
                "To represent stakeholder/customer interests, define user stories, and maintain/prioritize the Product Backlog",
                "To write unit tests and manage cloud deployments",
                "To resolve HR disputes within the engineering team"
            ],
            "answer": 1,
            "explanation": "The Product Owner is accountable for maximizing product value and managing the prioritized Product Backlog."
        },
        {
            "id": 2,
            "question": "What is a Sprint Retrospective meeting in Scrum?",
            "options": [
                "A live demonstration of product features to executive leadership",
                "A team meeting held at the end of a sprint to inspect what went well, what can be improved, and create action items for the next sprint",
                "A quarterly budget forecasting session with investors",
                "A code refactoring hackathon"
            ],
            "answer": 1,
            "explanation": "The Retrospective is dedicated to continuous team improvement, reflecting on processes, tools, and team collaboration."
        },
        {
            "id": 3,
            "question": "In the AARRR (Pirate Metrics) growth framework, what do the letters stand for?",
            "options": [
                "Acquisition, Activation, Retention, Referral, Revenue",
                "Assets, Accounts, Returns, Risk, Resilience",
                "Action, Attention, Reach, Rating, ROI",
                "Agile, Automation, Realtime, Reliability, Release"
            ],
            "answer": 0,
            "explanation": "Dave McClure's AARRR framework tracks customer lifecycle stages: Acquisition, Activation, Retention, Referral, and Revenue."
        },
        {
            "id": 4,
            "question": "What is a Minimum Viable Product (MVP)?",
            "options": [
                "The cheapest product possible with low quality standards",
                "A version of a new product that allows a team to collect the maximum amount of validated customer learning with the least effort",
                "A finished software suite ready for IPO launch",
                "A product design mockup with zero working features"
            ],
            "answer": 1,
            "explanation": "An MVP delivers core value to early adopters to validate market hypotheses with minimum required engineering investment."
        },
        {
            "id": 5,
            "question": "What is CAC (Customer Acquisition Cost) and how is it calculated?",
            "options": [
                "Total sales divided by number of products",
                "Total sales and marketing expenses divided by the number of new customers acquired during that period",
                "The server cost per active web session",
                "The salary of the chief sales officer"
            ],
            "answer": 1,
            "explanation": "CAC measures how much a business spends in marketing and sales to acquire a single paying customer."
        },
        {
            "id": 6,
            "question": "In Excel financial modeling, which modern formula is recommended to search a table both vertically and horizontally?",
            "options": ["VLOOKUP", "HLOOKUP", "XLOOKUP", "INDEX(ONLY)"],
            "answer": 2,
            "explanation": "`XLOOKUP` provides a robust, two-way search replacement for legacy VLOOKUP and HLOOKUP without requiring sorted data."
        },
        {
            "id": 7,
            "question": "What is Discounted Cash Flow (DCF) valuation used for?",
            "options": [
                "Estimating the present value of an investment based on its expected future cash flows discounted back to present value",
                "Calculating employee tax deductions",
                "Counting warehouse physical inventory",
                "Balancing monthly credit card statements"
            ],
            "answer": 0,
            "explanation": "DCF determines what future cash flows generated by a business are worth today by applying a discount rate (WACC)."
        },
        {
            "id": 8,
            "question": "What is TAM, SAM, and SOM in market sizing for startup ventures?",
            "options": [
                "Total Addressable Market, Serviceable Available Market, Serviceable Obtainable Market",
                "Target Audience Metrics, Sales Analytics Model, Standard Operating Metric",
                "Technical Architecture Map, System Admin Module, Server Operation Memory",
                "Tax Allocation Model, Shareholder Asset Measure, Startup Output Margin"
            ],
            "answer": 0,
            "explanation": "TAM = total global demand; SAM = segment targeted by your products; SOM = realistic portion of SAM your startup can capture."
        }
    ]
}

def generate_40_course_questions(course, primary_bank):
    """
    Generate a rigorous, 40-question comprehensive exam pool for any course.
    Combines primary domain curated questions with structured domain questions
    to cover Fundamentals, Advanced Patterns, Problem Solving, and Industry Best Practices.
    """
    title = course['title']
    category = course['category']
    skill_level = course['skill_level']
    
    questions = []
    # 1. Add all primary bank questions
    for q in primary_bank:
        questions.append({
            'question': q['question'],
            'options': q['options'],
            'answer': q['answer'],
            'explanation': q['explanation']
        })
        
    # Domain specific supplemental question templates to reach exactly 40 questions
    domain_topic = title.lower()
    
    # Supplemental Question Pools by Domain
    supplemental_pools = {
        'python': [
            ("What is the time complexity of searching for a key in a standard Python `dict` on average?", ["O(1)", "O(n)", "O(log n)", "O(n^2)"], 0, "Python dictionaries use hash tables under the hood, offering O(1) average lookup time."),
            ("Which built-in Python module is used for serializing and deserializing complex Python objects into byte streams?", ["json", "pickle", "marshal", "struct"], 1, "`pickle` provides Python-specific object serialization and deserialization."),
            ("What is the difference between `deepcopy` and `copy` in Python's `copy` module?", ["`deepcopy` recursively copies all nested objects, whereas `copy` creates a shallow reference", "`deepcopy` is only for strings", "There is no difference in execution", "`copy` is thread-safe while `deepcopy` is not"], 0, "`deepcopy` copies all nested child objects recursively, preventing side-effect mutations."),
            ("What does the `@property` decorator do in a Python class?", ["Makes a method private", "Allows a method to be accessed like an attribute without calling with parentheses", "Caches the return value permanently", "Forces static execution"], 1, "`@property` turns an instance method into a readable attribute getter."),
            ("In Python, how can you open a file safely ensuring it closes automatically even if an exception occurs?", ["open(file).close()", "Using the `with open(...) as f:` context manager statement", "try: open() except: exit()", "file.open_safe()"], 1, "Context managers with `with` guarantee automatic resource cleanup via `__exit__`."),
            ("What will `[x**2 for x in range(5) if x % 2 != 0]` evaluate to in Python?", ["[1, 9]", "[0, 4, 16]", "[1, 4, 9, 16]", "[0, 1, 9]"], 0, "Odd numbers in range(5) are 1 and 3. Their squares are 1 and 9."),
            ("What does the Global Interpreter Lock (GIL) in CPython prevent?", ["Multiple Python processes from running concurrently", "Multiple native threads from executing Python bytecodes simultaneously in a single process", "Garbage collection from running", "File I/O operations from blocking"], 1, "The GIL synchronizes execution of threads so only one thread executes Python bytecode at a time."),
            ("Which keyword is used to raise a user-defined custom exception in Python?", ["throw", "raise", "error", "catch"], 1, "In Python, `raise` is the keyword used to trigger and propagate exceptions."),
            ("What is the output of `bool([])` and `bool([0])` in Python?", ["False, True", "True, True", "False, False", "True, False"], 0, "An empty list is falsy (`False`), while a non-empty list containing `[0]` is truthy (`True`)."),
            ("What is the purpose of `__init__.py` in a Python directory?", ["It acts as the program entry point", "It marks the directory as an importable Python package", "It clears temporary byte code", "It compiles C extensions"], 1, "`__init__.py` designates a directory as a Python package module namespace."),
            ("What does `functools.lru_cache` accomplish when decorating a recursive function?", ["Limits recursion depth to 10", "Memoizes and caches the function's return values for recent input arguments", "Executes the function in WebAssembly", "Logs execution memory"], 1, "LRU cache memoizes recent function calls to prevent redundant re-computation."),
            ("How do `is` and `==` differ in Python comparisons?", ["`is` compares object memory identity (`id`), while `==` compares value equality", "`is` checks types only", "`==` is only for numbers", "They are 100% synonymous in Python 3"], 0, "`is` checks if two references point to the exact same object in memory, while `==` checks value equality."),
            ("What will `sorted(['10', '2', '100'])` return in Python?", ["['2', '10', '100']", "['10', '100', '2']", "['100', '10', '2']", "Throws a TypeError"], 1, "Lexicographical string sorting compares characters from left to right: `'10'` < `'100'` < `'2'`."),
            ("Which built-in function returns both the index and the value when iterating over a sequence?", ["range()", "enumerate()", "zip()", "map()"], 1, "`enumerate(iterable)` yields `(index, item)` tuples during iteration."),
            ("What is the result of `'--'.join(['A', 'B', 'C'])`?", ["'A--B--C'", "'--A--B--C--'", "'A,B,C'", "'ABC--'"], 0, "`.join()` places the delimiter string between elements of the iterable."),
            ("Which method removes and returns the last element from a Python `list` in O(1) time?", ["pop()", "remove()", "delete()", "shift()"], 0, "`list.pop()` removes and returns the trailing item in constant time O(1)."),
            ("What is a generator expression in Python syntactically enclosed by?", ["Curly braces `{}`", "Parentheses `()`", "Angle brackets `<>`", "Square brackets `[]`"], 1, "Generator expressions use parentheses `(x for x in data)` to produce lazy iterators."),
            ("Which magic method is called when an object is used inside a `with` statement block?", ["__enter__", "__start__", "__open__", "__init__"], 0, "`__enter__` is executed at the start of a context manager block."),
            ("How can you unpack a dictionary into keyword arguments when calling a function?", ["*dict", "**dict", "&dict", "%dict"], 1, "`**kwargs` unpacks dictionary key-value pairs as keyword arguments."),
            ("What does `sys.argv` contain in a Python script?", ["System environment variables", "Command-line arguments passed to the script", "Installed package list", "CPU core usage statistics"], 1, "`sys.argv` stores the list of command-line arguments provided at execution time."),
            ("What does the `pass` statement in Python signify?", ["A null operation / placeholder where code is syntactically required", "Exits the entire program", "Skips to the next file", "Resets the CPU cache"], 0, "`pass` is a placeholder that does nothing when executed."),
            ("What is the purpose of `collections.defaultdict`?", ["Sorts dictionary keys automatically", "Provides a default value for non-existent keys instead of raising a KeyError", "Encrypts dictionary values", "Limits dictionary size"], 1, "`defaultdict` calls a factory function when accessing missing keys to supply default values."),
            ("What will `set([1, 2, 2, 3, 4, 4, 5])` contain?", ["{1, 2, 3, 4, 5}", "[1, 2, 3, 4, 5]", "{1: 2, 3: 4}", "Throws an exception"], 0, "Python sets store only unique distinct elements, discarding duplicates."),
            ("Which module in Python is used for executing asynchronous I/O and event loops?", ["threading", "multiprocessing", "asyncio", "concurrent.futures"], 2, "`asyncio` provides the framework for writing concurrent code using `async`/`await`."),
            ("How do you convert a string `'123'` into an integer safely?", ["int('123')", "str.to_int('123')", "Number('123')", "Integer.parse('123')"], 0, "`int('123')` is the standard type constructor for converting strings to integers."),
            ("What is the output of `5 // 2` in Python 3?", ["2.5", "2", "3", "2.0"], 1, "`//` is the floor division operator which rounds down to the nearest integer `2`."),
            ("Which standard library module is used for generating cryptographically strong random numbers?", ["random", "secrets", "hashlib", "crypto"], 1, "`secrets` is specifically designed for generating secure tokens, keys, and passwords."),
            ("What is a docstring in Python?", ["A comment starting with `#`", "A string literal specified as the first statement in a module, function, class, or method for documentation", "A text file named `doc.txt`", "A compiler directive"], 1, "Triple-quoted docstrings provide structured documentation accessible via `help()` and `.__doc__`."),
            ("What does `os.path.join('folder', 'file.txt')` do?", ["Concatenates paths using the correct OS-specific directory separator (`/` or `\\`)", "Creates the physical file on disk", "Deletes existing folders", "Opens the file in binary mode"], 0, "`os.path.join` creates cross-platform safe file system paths."),
            ("What is the primary benefit of list comprehensions in Python?", ["They bypass the GIL", "They provide a concise and optimized syntax for creating new lists from iterables", "They prevent memory leakage", "They compile into C++ headers"], 1, "List comprehensions offer concise, highly optimized syntax for transforming collections.")
        ],
        'default': [
            ("What is the primary purpose of version control systems like Git?", ["To compile source code into binaries", "To track changes, collaborate across branches, and maintain code history", "To host database servers", "To format HTML code"], 1, "Git tracks revisions, manages branches, and facilitates multi-developer collaboration."),
            ("What does API stand for in software engineering?", ["Application Programming Interface", "Automated Program Integration", "Advanced Process Intelligence", "Application Protocol Index"], 0, "An API defines protocols and tools for building and integrating application software."),
            ("Which HTTP status code signifies a successful request?", ["404", "500", "200", "301"], 2, "HTTP 200 OK indicates that the request has succeeded."),
            ("What is the role of continuous integration (CI) in software development?", ["Deploying hardware servers", "Automatically building, testing, and verifying code changes frequently", "Writing marketing copy", "Manual database backups"], 1, "CI automates build and test workflows to detect bugs early in development."),
            ("What is the purpose of unit testing?", ["Testing the entire system with end users", "Testing individual isolated units/functions of code for expected behavior", "Testing network cable bandwidth", "Testing database server cooling"], 1, "Unit tests verify that individual small units of source code perform correctly in isolation."),
            ("What is JSON?", ["JavaScript Object Notation - a lightweight data-interchange format", "A Java server engine", "A CSS preprocessor", "A database query optimizer"], 0, "JSON is an open standard file and data format used for serializing structured data."),
            ("What is the primary advantage of RESTful architecture?", ["Strictly stateful connections", "Stateless client-server communication using standard HTTP methods", "Requires binary encoding", "Only works on Windows"], 1, "REST relies on stateless requests and standard HTTP verbs (GET, POST, PUT, DELETE)."),
            ("What is the purpose of an index in a database table?", ["To encrypt column values", "To speed up the retrieval of rows by providing fast pointer lookups", "To enforce HTML formatting", "To limit database user logins"], 1, "Indexes create fast lookup data structures (e.g., B-Trees) to accelerate SQL query execution."),
            ("What is SQL injection?", ["A method to speed up database queries", "A security vulnerability where malicious SQL commands are injected into input fields to manipulate the database", "An automated database backup process", "A tool for creating database tables"], 1, "SQL injection occurs when untrusted user input is concatenated directly into SQL queries."),
            ("How do parameter-bound prepared statements prevent SQL injection?", ["By encrypting the entire database", "By treating user input strictly as data parameters rather than executable SQL code", "By deleting user accounts", "By blocking HTTP requests"], 1, "Prepared statements separate query structure from parameter values, rendering injection impossible."),
            ("What is the purpose of HTTPS over HTTP?", ["Faster download speeds", "Encrypting data in transit using TLS/SSL to provide confidentiality and integrity", "Free web hosting", "Removing JavaScript errors"], 1, "HTTPS secures data transmitted between client and server against eavesdropping and tampering."),
            ("What is a responsive web design?", ["A website that loads within 1 second", "A web design approach where layout dynamically adapts to different screen sizes and devices", "A website with dark mode only", "A website that only works on desktop"], 1, "Responsive design uses fluid grids, flexible images, and CSS media queries for all devices."),
            ("What does DRY stand for in software engineering?", ["Don't Repeat Yourself", "Data Realignment Yield", "Dynamic Runtime Yield", "Direct Resource Yield"], 0, "DRY is a fundamental principle aimed at reducing repetition of software patterns."),
            ("What is refactoring?", ["Rewriting code in a different programming language", "Restructuring existing computer code without changing its external behavior to improve maintainability", "Adding new features for clients", "Deleting old databases"], 1, "Refactoring cleans, simplifies, and enhances internal code structure while preserving functionality."),
            ("What is the difference between synchronous and asynchronous code?", ["Synchronous blocks execution until a task finishes; asynchronous allows other tasks to continue while waiting", "Synchronous is only for frontend", "Asynchronous cannot handle errors", "There is no functional difference"], 0, "Synchronous code executes sequentially and blocks, while asynchronous non-blocking code handles concurrency."),
            ("What is the purpose of caching in web systems?", ["To store redundant copies permanently", "To store frequently accessed data in high-speed memory (RAM) to reduce latency and database load", "To format JSON responses", "To compress video files"], 1, "Caching stores hot data in fast storage (e.g. Redis, Memory) to accelerate response times."),
            ("What is an algorithm's Big-O time complexity measure?", ["The exact execution time in milliseconds on Intel CPUs", "The asymptotic upper bound of time required as the input size `n` grows", "The number of lines of code", "The file size in kilobytes"], 1, "Big-O characterizes the worst-case runtime growth rate relative to input scale `n`."),
            ("What is a Binary Search algorithm's time complexity for a sorted array of size n?", ["O(1)", "O(log n)", "O(n)", "O(n^2)"], 1, "Binary search repeatedly divides the search interval in half, yielding O(log n) efficiency."),
            ("Which data structure operates on a First-In-First-Out (FIFO) principle?", ["Stack", "Queue", "Binary Tree", "Hash Map"], 1, "A Queue processes elements in the order they arrived (FIFO)."),
            ("Which data structure operates on a Last-In-First-Out (LIFO) principle?", ["Queue", "Stack", "Linked List", "Graph"], 1, "A Stack retrieves the most recently added item first (LIFO)."),
            ("What is the primary benefit of containerization (e.g. Docker)?", ["Replaces operating systems entirely", "Packages applications with all their dependencies to run reliably across any environment", "Increases CPU clock speed", "Enforces static typing"], 1, "Containers ensure uniform, isolated execution environments across development and production."),
            ("What is an environment variable used for in web applications?", ["Storing public HTML templates", "Configuring sensitive credentials, API keys, and environment-specific settings securely", "Styling CSS buttons", "Counting page views"], 1, "Environment variables store configuration secrets outside of committed source code."),
            ("What does CORS stand for in web security?", ["Cross-Origin Resource Sharing", "Central Operating Request Server", "Content Object Rendering System", "Cryptographic Open Routing Standard"], 0, "CORS is a browser security mechanism that controls resource access across different origins."),
            ("What is JWT (JSON Web Token) commonly used for?", ["Database indexing", "Stateless authentication and secure transmission of claims between parties", "Compressing image files", "CSS layout styling"], 1, "JWT tokens securely encode user claims for stateless API authentication."),
            ("What is technical debt in software development?", ["The financial cost of purchasing computers", "The implied cost of future rework caused by choosing an easy or quick solution now instead of a better approach", "A loan from a technology bank", "The electricity cost of running cloud servers"], 1, "Technical debt represents the long-term maintenance overhead of suboptimal code compromises."),
            ("What is a microservice architecture?", ["An app built inside a smartwatch", "An architectural style that structures an application as a collection of small, independently deployable services", "A single monolithic executable file", "A database with one table"], 1, "Microservices decouple large systems into focused, independently scalable services."),
            ("What is the purpose of semantic versioning (SemVer: MAJOR.MINOR.PATCH)?", ["To count total downloads", "To clearly communicate breaking changes (MAJOR), new features (MINOR), and bug fixes (PATCH)", "To track marketing campaigns", "To schedule server reboots"], 1, "SemVer communicates the nature of code modifications clearly across dependencies."),
            ("What is the principle of least privilege in security engineering?", ["Giving all users administrator access", "Granting only the minimum necessary permissions required to perform a specific task", "Allowing public write access to databases", "Disabling password requirements"], 1, "Least privilege minimizes damage from accidents or attacks by restricting unnecessary access."),
            ("What is the purpose of a CDN (Content Delivery Network)?", ["To build SQL databases", "To distribute static assets globally closer to end-users, reducing latency and bandwidth", "To compile Python code", "To design user interfaces"], 1, "CDNs cache and deliver static content from edge servers worldwide."),
            ("Why is code documentation essential in production software engineering?", ["It is required by the operating system compiler", "It explains architectural decisions, API contracts, and usage patterns for team collaboration and maintainability", "It replaces the need for writing tests", "It increases website Google PageRank automatically"], 1, "Documentation enables developers to understand, maintain, and safely extend complex codebases.")
        ]
    }
    
    # Pick supplemental pool
    pool_key = 'python' if ('python' in domain_topic or 'backend' in category.lower()) else 'default'
    pool_items = supplemental_pools.get(pool_key, supplemental_pools['default'])
    
    # Fill up to 40 questions
    idx = len(questions) + 1
    for item in pool_items:
        if len(questions) >= 40:
            break
        questions.append({
            'id': idx,
            'question': item[0],
            'options': item[1],
            'answer': item[2],
            'explanation': item[3]
        })
        idx += 1
        
    # If still need to reach 40, pull from the other pool
    if len(questions) < 40:
        other_key = 'default' if pool_key == 'python' else 'python'
        other_items = supplemental_pools.get(other_key, [])
        for item in other_items:
            if len(questions) >= 40:
                break
            questions.append({
                'id': idx,
                'question': item[0],
                'options': item[1],
                'answer': item[2],
                'explanation': item[3]
            })
            idx += 1
            
    # Normalize IDs from 1 to 40
    for i, q in enumerate(questions[:40]):
        q['id'] = i + 1
        
    return questions[:40]

def get_course_exam_questions(course_id):
    """
    Retrieve comprehensive 40-question exam pool for a specific course.
    Matches course title and category to select the best matching curated questions.
    """
    conn = database.get_db_connection()
    course = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    conn.close()

    if not course:
        return []

    title_lower = course['title'].lower()
    category_lower = course['category'].lower()
    tags_lower = (course['tags'] or '').lower()

    # Determine primary bank
    selected_bank = None
    if 'python' in title_lower or 'python' in tags_lower:
        selected_bank = COURSE_EXAM_BANKS['python']
    elif 'react' in title_lower or 'react' in tags_lower:
        selected_bank = COURSE_EXAM_BANKS['react']
    elif 'sql' in title_lower or 'sql' in tags_lower:
        selected_bank = COURSE_EXAM_BANKS['sql']
    elif 'javascript' in title_lower or 'node' in title_lower:
        selected_bank = COURSE_EXAM_BANKS['javascript']
    elif 'html' in title_lower or 'css' in title_lower or 'web development' in category_lower:
        selected_bank = COURSE_EXAM_BANKS['web']
    elif 'data' in category_lower or 'ai' in category_lower or 'machine learning' in title_lower or 'deep learning' in title_lower or 'nlp' in title_lower:
        selected_bank = COURSE_EXAM_BANKS['data_ai']
    elif 'design' in category_lower or 'ux' in title_lower or 'figma' in title_lower:
        selected_bank = COURSE_EXAM_BANKS['design']
    elif 'business' in category_lower or 'agile' in title_lower or 'marketing' in title_lower or 'finance' in title_lower or 'startup' in title_lower:
        selected_bank = COURSE_EXAM_BANKS['business']
    else:
        selected_bank = COURSE_EXAM_BANKS['python']

    return generate_40_course_questions(course, selected_bank)

def get_sanitized_exam(course_id):
    """
    Return exam metadata and 40 questions WITHOUT exposing correct answers to client-side.
    Time limit: 60 minutes (1 hour), Passing criteria: 70%.
    """
    conn = database.get_db_connection()
    course = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    conn.close()

    if not course:
        return None

    full_questions = get_course_exam_questions(course_id)
    sanitized_questions = []
    for q in full_questions:
        sanitized_questions.append({
            'id': q['id'],
            'question': q['question'],
            'options': q['options']
        })

    return {
        'is_demo': False,
        'course_id': course['id'],
        'course_title': course['title'],
        'course_category': course['category'],
        'skill_level': course['skill_level'],
        'duration': course['duration'],
        'total_questions': len(sanitized_questions),
        'passing_percentage': 70,
        'time_limit_minutes': 60,
        'questions': sanitized_questions
    }

def get_sanitized_demo_exam(course_id):
    """
    Return demo/practice exam metadata and questions WITHOUT exposing correct answers.
    Students can take this anytime to prepare and experience the real proctored exam interface.
    """
    conn = database.get_db_connection()
    course = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    conn.close()

    if not course:
        return None

    full_questions = get_course_exam_questions(course_id)
    demo_count = min(len(full_questions), 10)
    demo_questions = full_questions[:demo_count]

    sanitized_questions = []
    for q in demo_questions:
        sanitized_questions.append({
            'id': q['id'],
            'question': q['question'],
            'options': q['options']
        })

    return {
        'is_demo': True,
        'course_id': course['id'],
        'course_title': course['title'],
        'course_category': course['category'],
        'skill_level': course['skill_level'],
        'duration': course['duration'],
        'total_questions': len(sanitized_questions),
        'passing_percentage': 70,
        'time_limit_minutes': 15,
        'questions': sanitized_questions
    }


def generate_certificate_code(course_id, user_id):
    """
    Generate a verifiable, official certificate serial code.
    Format: AL-CERT-2026-XXXXX
    """
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"AL-CERT-2026-{course_id}{user_id}-{unique_suffix}"

def calculate_grade(percentage):
    """
    Calculate academic grade based on final exam percentage score.
    Strict passing criteria is >= 70%.
    """
    if percentage >= 90:
        return "A+", "Distinction (Honors)"
    elif percentage >= 80:
        return "A", "Excellence"
    elif percentage >= 70:
        return "B", "Passing (Certified)"
    else:
        return "F", "Needs Improvement (Retake Required)"


def evaluate_exam_submission(user_id, course_id, submitted_answers, violations_count=0, disqualified=False, disqualification_reason=None):
    """
    Evaluate submitted answers against the course question key.
    If disqualified is True (screen-switch, tab-switch, exiting fullscreen), force 0 score, 0%, and Grade F.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # 1. Fetch Course details
    course = cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    if not course:
        conn.close()
        return {'success': False, 'error': 'Course not found'}

    # 2. Verify 100% completion in enrollments
    enrollment = cursor.execute(
        "SELECT * FROM enrollments WHERE user_id = ? AND course_id = ?",
        (user_id, course_id)
    ).fetchone()

    if not enrollment or enrollment['progress_percent'] < 100:
        conn.close()
        return {'success': False, 'error': 'Course must be 100% completed before taking the Final Certification Exam.'}

    # 3. Grade answers
    questions = get_course_exam_questions(course_id)
    total_questions = len(questions)
    correct_count = 0
    feedback = []

    for q in questions:
        q_id = str(q['id'])
        user_choice = submitted_answers.get(q_id)
        is_correct = False
        if not disqualified and user_choice is not None:
            try:
                user_choice_idx = int(user_choice)
                if user_choice_idx == q['answer']:
                    correct_count += 1
                    is_correct = True
            except (ValueError, TypeError):
                pass

        feedback.append({
            'question_id': q['id'],
            'question': q['question'],
            'user_answer': int(user_choice) if user_choice is not None else None,
            'correct_answer': q['answer'],
            'is_correct': is_correct,
            'explanation': q['explanation']
        })

    violations_count = int(violations_count or 0)
    if disqualified:
        violations_count = max(1, violations_count)
        correct_count = 0
        raw_percentage = 0.0
        final_percentage = 0.0
        passed = False
        grade_letter = "F"
        grade_title = "Disqualified (0 Marks - Cheating/Screen-Switch Detected)"
    else:
        raw_percentage = round((correct_count / total_questions) * 100, 1) if total_questions > 0 else 0
        final_percentage = raw_percentage
        if violations_count >= 3:
            final_percentage = max(0.0, raw_percentage - 10.0)

        passed = final_percentage >= 60.0
        grade_letter, grade_title = calculate_grade(final_percentage)

    # 4. Record Attempt in exam_attempts table
    cursor.execute('''
        INSERT INTO exam_attempts (user_id, course_id, score, total_questions, percentage, passed, security_violations)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, course_id, correct_count, total_questions, final_percentage, 1 if passed else 0, violations_count))

    cert_code = None
    already_had_cert = False

    if passed and not disqualified:
        # Check if user already holds a certificate for this course
        existing_cert = cursor.execute(
            "SELECT certificate_code, grade FROM certificates WHERE user_id = ? AND course_id = ?",
            (user_id, course_id)
        ).fetchone()

        if existing_cert:
            already_had_cert = True
            cert_code = existing_cert['certificate_code']
            # Update score and grade if improved
            cursor.execute('''
                UPDATE certificates 
                SET exam_score = ?, grade = ?, issued_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND course_id = ?
            ''', (int(final_percentage), grade_letter, user_id, course_id))
        else:
            cert_code = generate_certificate_code(course_id, user_id)
            cursor.execute('''
                INSERT INTO certificates (user_id, course_id, exam_score, total_score, grade, certificate_code)
                VALUES (?, ?, ?, 100, ?, ?)
            ''', (user_id, course_id, int(final_percentage), grade_letter, cert_code))

        conn.commit()

        # Award Gamification XP for passing certification (+100 XP)
        gamification.award_xp(
            user_id,
            'final_exam_passed',
            100,
            course_id,
            f"Earned Verified Certificate for {course['title']} (Grade: {grade_letter})"
        )

        # In-App notification
        gamification.create_notification(
            user_id,
            "🎓 Certificate Issued!",
            f"Congratulations! You passed the Final Exam for '{course['title']}' with Grade {grade_letter} ({final_percentage}%). Your verified credential is now active!",
            "fa-certificate",
            "certificate"
        )
    elif disqualified:
        conn.commit()
        # Create Security Violation notification
        gamification.create_notification(
            user_id,
            "🚨 Exam Disqualified (0 Marks)",
            f"Your exam for '{course['title']}' was auto-submitted with 0 Marks due to screen/tab change detection: {disqualification_reason or 'Unauthorized window or tab switch'}.",
            "fa-triangle-exclamation",
            "system"
        )
    else:
        conn.commit()

    conn.close()

    return {
        'success': True,
        'disqualified': disqualified,
        'disqualification_reason': disqualification_reason if disqualified else None,
        'passed': passed,
        'score': correct_count,
        'total_questions': total_questions,
        'raw_percentage': raw_percentage,
        'final_percentage': final_percentage,
        'violations_count': violations_count,
        'grade': grade_letter,
        'grade_title': grade_title,
        'certificate_code': cert_code,
        'course_title': course['title'],
        'feedback': feedback
    }

def evaluate_demo_exam_submission(user_id, course_id, submitted_answers, violations_count=0, disqualified=False, disqualification_reason=None):
    """
    Evaluate submitted answers for Demo / Practice Exam.
    If disqualified is True (screen-switch, tab-switch), forces 0 score and Grade F.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()

    course = cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    conn.close()
    if not course:
        return {'success': False, 'error': 'Course not found'}

    full_questions = get_course_exam_questions(course_id)
    demo_count = min(len(full_questions), 6)
    questions = full_questions[:demo_count]

    total_questions = len(questions)
    correct_count = 0
    feedback = []

    for q in questions:
        q_id = str(q['id'])
        user_choice = submitted_answers.get(q_id)
        is_correct = False
        if not disqualified and user_choice is not None:
            try:
                user_choice_idx = int(user_choice)
                if user_choice_idx == q['answer']:
                    correct_count += 1
                    is_correct = True
            except (ValueError, TypeError):
                pass

        feedback.append({
            'question_id': q['id'],
            'question': q['question'],
            'user_answer': int(user_choice) if user_choice is not None else None,
            'correct_answer': q['answer'],
            'is_correct': is_correct,
            'explanation': q['explanation']
        })

    violations_count = int(violations_count or 0)
    if disqualified:
        violations_count = max(1, violations_count)
        correct_count = 0
        raw_percentage = 0.0
        final_percentage = 0.0
        passed = False
        grade_letter = "F"
        grade_title = "Disqualified (0 Marks - Screen Change/Cheating Detected)"
    else:
        raw_percentage = round((correct_count / total_questions) * 100, 1) if total_questions > 0 else 0
        final_percentage = raw_percentage
        if violations_count >= 3:
            final_percentage = max(0.0, raw_percentage - 10.0)

        passed = final_percentage >= 60.0
        grade_letter, grade_title = calculate_grade(final_percentage)

        # Award Practice XP (+25 XP) only if not disqualified
        gamification.award_xp(
            user_id,
            'demo_exam_completed',
            25,
            course_id,
            f"Completed Demo Practice Exam for {course['title']} ({final_percentage}%)"
        )

    return {
        'success': True,
        'is_demo': True,
        'disqualified': disqualified,
        'disqualification_reason': disqualification_reason if disqualified else None,
        'passed': passed,
        'score': correct_count,
        'total_questions': total_questions,
        'raw_percentage': raw_percentage,
        'final_percentage': final_percentage,
        'violations_count': violations_count,
        'grade': grade_letter,
        'grade_title': grade_title,
        'certificate_code': None,
        'course_title': course['title'],
        'feedback': feedback,
    }


def get_certificate_details(cert_code):
    """
    Fetch comprehensive details for an issued certificate by its unique verification code.
    """
    conn = database.get_db_connection()
    cert = conn.execute('''
        SELECT c.*, u.full_name, u.username, co.title as course_title, co.category as course_category, 
               co.skill_level as course_skill_level, co.duration as course_duration
        FROM certificates c
        JOIN users u ON c.user_id = u.id
        JOIN courses co ON c.course_id = co.id
        WHERE c.certificate_code = ?
    ''', (cert_code,)).fetchone()
    conn.close()

    if not cert:
        return None

    # Format issuance date nicely
    issued_date_str = cert['issued_at']
    try:
        dt_obj = datetime.datetime.strptime(issued_date_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
        formatted_date = dt_obj.strftime("%B %d, %Y")
    except Exception:
        formatted_date = issued_date_str

    grade_letter, grade_title = calculate_grade(cert['exam_score'])

    return {
        'id': cert['id'],
        'user_id': cert['user_id'],
        'student_name': cert['full_name'],
        'username': cert['username'],
        'course_id': cert['course_id'],
        'course_title': cert['course_title'],
        'course_category': cert['course_category'],
        'course_skill_level': cert['course_skill_level'],
        'course_duration': cert['course_duration'],
        'exam_score': cert['exam_score'],
        'grade': cert['grade'],
        'grade_title': grade_title,
        'certificate_code': cert['certificate_code'],
        'issued_date': formatted_date
    }

def get_user_certificates(user_id):
    """
    Retrieve all earned certificates for a given user.
    """
    conn = database.get_db_connection()
    certs = conn.execute('''
        SELECT c.*, co.title as course_title, co.category as course_category, co.skill_level, co.duration
        FROM certificates c
        JOIN courses co ON c.course_id = co.id
        WHERE c.user_id = ?
        ORDER BY c.issued_at DESC
    ''', (user_id,)).fetchall()
    conn.close()

    result = []
    for c in certs:
        issued_date_str = c['issued_at']
        try:
            dt_obj = datetime.datetime.strptime(issued_date_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
            formatted_date = dt_obj.strftime("%B %d, %Y")
        except Exception:
            formatted_date = issued_date_str

        result.append({
            'id': c['id'],
            'course_id': c['course_id'],
            'course_title': c['course_title'],
            'course_category': c['course_category'],
            'skill_level': c['skill_level'],
            'duration': c['duration'],
            'exam_score': c['exam_score'],
            'grade': c['grade'],
            'certificate_code': c['certificate_code'],
            'issued_date': formatted_date
        })

    return result
