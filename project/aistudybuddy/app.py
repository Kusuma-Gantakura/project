"""
AI Study Buddy v2.0 — Full Stack with Claude AI Integration
Features:
  - AI-powered question explanations, hints, encouragement
  - One-by-one quiz with instant AI feedback
  - Course completion certificates (downloadable)
  - Full profile with scores, certificates, achievements
  - Bigger, clearer UI
"""
import os, uuid, random, hashlib, json
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'))
app.secret_key = 'studybuddy_v2_secret_2024_xK9p'

PASS_THRESHOLD = 85

# ── Database ──────────────────────────────────────────
DB_FILE = os.path.join(BASE_DIR, 'database.json')

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "progress": {}, "results": {}, "certificates": {}}
    with open(DB_FILE) as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ── Quiz Sessions (server-side answer key) ─────────────
QUIZ_SESSIONS = {}

# ══════════════════════════════════════════════════════
#  FULL CURRICULUM
# ══════════════════════════════════════════════════════
CURRICULUM = {
  "Python": {
    "icon":"🐍","color":"#3776ab","level":"Beginner",
    "desc":"Most popular language for AI, data science & web development.",
    "topics":[
      {"id":"py_vars","title":"Variables & Data Types",
       "desc":"A variable stores data in memory. Python is dynamically typed — you don't declare types. Core types: int, float, str, bool, list, tuple, set, dict. Use type() to inspect any value. Variables are created the moment you assign a value — no declaration keyword needed.",
       "code":"# Numeric types\nage   = 25          # int\nprice = 9.99        # float\n\n# Text\nname  = 'Alice'\nmsg   = f'Hello, {name}!'   # f-string\n\n# Boolean\nis_active = True\n\n# Collections\nscores  = [90, 85, 78]              # list  – ordered, mutable\ncoords  = (10.5, 20.3)             # tuple – ordered, immutable\ntags    = {'python', 'code'}       # set   – unique values\nstudent = {'name':'Bob','age':20}  # dict  – key:value pairs\n\nprint(type(age))     # <class 'int'>\nprint(type(scores))  # <class 'list'>",
       "quiz":[
         {"q":"Which Python collection stores key-value pairs?","opts":["list","tuple","set","dict"],"ans":3},
         {"q":"What does type(3.14) return?","opts":["<class 'int'>","<class 'float'>","<class 'num'>","<class 'str'>"],"ans":1},
         {"q":"Which collection type is IMMUTABLE in Python?","opts":["list","dict","tuple","set"],"ans":2},
         {"q":"f'Hello {name}' syntax is called a...","opts":["Template string","f-string","Raw string","Format block"],"ans":1},
         {"q":"How do you create a variable x with value 10 in Python?","opts":["int x = 10","var x = 10","x = 10","let x = 10"],"ans":2}
       ]},
      {"id":"py_control","title":"Control Flow",
       "desc":"Control flow directs program execution path. if/elif/else handles branching decisions. for loops iterate over sequences. while loops repeat while a condition is true. break exits a loop, continue skips the current iteration, pass is a no-op placeholder. range() generates integer sequences efficiently.",
       "code":"# if / elif / else\nscore = 85\nif score >= 90:\n    grade = 'A'\nelif score >= 80:\n    grade = 'B'   # ← this executes\nelse:\n    grade = 'C'\n\n# for loop with range\nfor i in range(1, 6):\n    print(i)   # prints 1 2 3 4 5\n\n# while loop\ncount = 0\nwhile count < 3:\n    print(count)   # 0 1 2\n    count += 1\n\n# break / continue\nfor n in range(10):\n    if n == 3: continue   # skip 3\n    if n == 7: break      # stop before 7\n    print(n)  # 0 1 2 4 5 6",
       "quiz":[
         {"q":"What does 'break' do inside a Python loop?","opts":["Skips one iteration","Exits the loop immediately","Pauses the loop","Restarts from beginning"],"ans":1},
         {"q":"What does range(2, 8, 2) produce?","opts":["[2,4,6,8]","[2,4,6]","[2,3,4,5,6,7]","[2,8]"],"ans":1},
         {"q":"What does 'continue' do in a loop?","opts":["Exits the loop","Skips remaining code in current iteration","Pauses execution","Jumps to else block"],"ans":1},
         {"q":"The 'pass' keyword is used as...","opts":["Program exit","Loop break","A no-operation placeholder","Error handler"],"ans":2},
         {"q":"What is the output of: for i in range(3): print(i)","opts":["1 2 3","0 1 2","0 1 2 3","1 2"],"ans":1}
       ]},
      {"id":"py_functions","title":"Functions",
       "desc":"Functions are reusable code blocks defined with 'def'. They accept parameters and return values. Python supports default parameters, *args for variable positional args, **kwargs for keyword args, and lambda for anonymous one-liner functions. Functions are first-class objects — they can be passed as arguments and returned from other functions.",
       "code":"# Basic function with default parameter\ndef greet(name, msg='Hello'):\n    return f'{msg}, {name}!'\n\nprint(greet('Alice'))        # Hello, Alice!\nprint(greet('Bob', 'Hi'))   # Hi, Bob!\n\n# *args — accepts any number of positional args\ndef total(*nums):\n    return sum(nums)\nprint(total(1, 2, 3, 4))  # 10\n\n# **kwargs — keyword arguments as dict\ndef show_info(**data):\n    for k, v in data.items():\n        print(f'{k}: {v}')\nshow_info(name='Alice', age=25)\n\n# Lambda — anonymous one-liner function\nsquare = lambda x: x ** 2\nprint(square(5))   # 25\n\n# Functions as first-class objects\nresult = list(map(lambda x: x*2, [1,2,3]))\nprint(result)  # [2, 4, 6]",
       "quiz":[
         {"q":"Which keyword is used to define a function in Python?","opts":["func","function","def","fn"],"ans":2},
         {"q":"A function with no return statement returns what?","opts":["0","False","None","Raises error"],"ans":2},
         {"q":"What does *args allow in a function?","opts":["Only keyword args","Variable number of positional args","Default values","One optional arg"],"ans":1},
         {"q":"lambda x: x*2 defines a(n)...","opts":["Class method","Anonymous function","Default argument","Decorator"],"ans":1},
         {"q":"In def f(x=5): what is x=5 called?","opts":["Required parameter","*args","Default parameter","**kwargs"],"ans":2}
       ]},
      {"id":"py_oop","title":"OOP & Classes",
       "desc":"Python is object-oriented. Classes are blueprints for objects. __init__ initializes instances. self refers to the current object instance. Inheritance allows child classes to reuse parent code. Polymorphism lets subclasses override parent methods. super() calls parent class methods. Encapsulation hides internal data.",
       "code":"class Animal:\n    def __init__(self, name, sound):\n        self.name   = name\n        self._sound = sound   # _ convention = protected\n\n    def speak(self):\n        return f'{self.name} says {self._sound}'\n\n    def __str__(self):\n        return f'Animal({self.name})'\n\n# Inheritance\nclass Dog(Animal):\n    def __init__(self, name):\n        super().__init__(name, 'Woof')  # call parent\n\n    def fetch(self, item):\n        return f'{self.name} fetches {item}!'\n\n    def speak(self):  # Override parent method\n        return f'{self.name}: WOOF WOOF!'\n\nd = Dog('Rex')\nprint(d.speak())             # Rex: WOOF WOOF!\nprint(d.fetch('ball'))       # Rex fetches ball!\nprint(isinstance(d, Animal)) # True",
       "quiz":[
         {"q":"What is the purpose of __init__ in a Python class?","opts":["Destroy the object","Initialize object attributes","Import a module","Define class method"],"ans":1},
         {"q":"In a class method, 'self' refers to...","opts":["The class itself","The parent class","The current object instance","A global variable"],"ans":2},
         {"q":"Which syntax correctly inherits from a parent class?","opts":["class Child(Parent):","extends Parent","inherits Parent","class Child::Parent"],"ans":0},
         {"q":"Polymorphism in OOP means...","opts":["Multiple constructors","Same method name, different behavior per class","Multiple inheritance","Data hiding"],"ans":1},
         {"q":"super().__init__() is used to call...","opts":["Child constructor","Python built-in","Parent class constructor","A static method"],"ans":2}
       ]},
      {"id":"py_exceptions","title":"Exception Handling",
       "desc":"Exceptions are runtime errors. Handle them with try/except to prevent program crashes. except catches specific exception types. else runs only when no exception occurred. finally always runs — for cleanup like closing files. raise manually throws exceptions. Custom exceptions extend the Exception class for domain-specific errors.",
       "code":"# try / except / else / finally\ntry:\n    x = int(input('Enter number: '))\n    result = 100 / x\nexcept ValueError:\n    print('Not a valid number!')\nexcept ZeroDivisionError:\n    print('Cannot divide by zero!')\nelse:\n    print(f'Result: {result}')  # only if no exception\nfinally:\n    print('Always executes.')   # cleanup code here\n\n# raise your own exception\ndef set_age(age):\n    if age < 0:\n        raise ValueError('Age cannot be negative')\n    return age\n\n# Custom exception class\nclass InsufficientFundsError(Exception):\n    def __init__(self, amount):\n        super().__init__(f'Need ${amount} more')\n\ntry:\n    raise InsufficientFundsError(50)\nexcept InsufficientFundsError as e:\n    print(e)  # Need $50 more",
       "quiz":[
         {"q":"Which block ALWAYS executes regardless of any exception?","opts":["try","except","else","finally"],"ans":3},
         {"q":"What exception is raised when dividing by zero?","opts":["MathError","ValueError","ZeroDivisionError","ArithmeticError"],"ans":2},
         {"q":"The 'else' block in try/except runs when...","opts":["An exception is caught","finally runs","No exception occurs in try","All exceptions handled"],"ans":2},
         {"q":"How do you manually raise a custom exception?","opts":["throw MyError()","raise MyError()","except MyError()","error MyError()"],"ans":1},
         {"q":"Custom exceptions should inherit from...","opts":["BaseClass","object","Error","Exception"],"ans":3}
       ]},
      {"id":"py_libs","title":"Libraries & Modules",
       "desc":"Python modules are reusable .py files. Import with 'import'. Standard library includes: math, os, sys, random, datetime, json, re, collections. Third-party: numpy, pandas, flask, requests (install via pip). Use 'from module import name' for specific imports. Create your own modules by writing .py files and importing them.",
       "code":"import math\nprint(math.sqrt(144))   # 12.0\nprint(math.pi)          # 3.14159...\nprint(math.ceil(4.2))   # 5\n\nimport random\nprint(random.randint(1, 100))        # random 1-100\nprint(random.choice(['a','b','c']))  # random item\n\nimport os\nprint(os.getcwd())       # current working directory\nprint(os.listdir('.'))   # list all files\n\nimport json\ndata = {'name': 'Alice', 'scores': [90, 85]}\njs     = json.dumps(data)   # dict → JSON string\nparsed = json.loads(js)     # JSON string → dict\n\n# Specific import\nfrom datetime import datetime\nnow = datetime.now()\nprint(now.strftime('%Y-%m-%d'))  # 2024-01-15",
       "quiz":[
         {"q":"Which keyword is used to import a module in Python?","opts":["include","require","import","load"],"ans":2},
         {"q":"json.dumps() converts a Python object to...","opts":["Binary data","XML","JSON string","CSV"],"ans":2},
         {"q":"Which standard library provides sqrt() and pi?","opts":["numbers","calc","math","numpy only"],"ans":2},
         {"q":"random.choice(['a','b','c']) returns...","opts":["All items","A randomly selected item","The first item","An index"],"ans":1},
         {"q":"os.getcwd() returns...","opts":["OS version string","Current working directory path","List of all files","Available memory"],"ans":1}
       ]}
    ]
  },
  "JavaScript": {
    "icon":"⚡","color":"#f7df1e","level":"Beginner",
    "desc":"The language of the web — runs in browsers and on servers via Node.js.",
    "topics":[
      {"id":"js_vars","title":"Variables & Types",
       "desc":"JS has var (avoid), let (block-scoped, reassignable), const (block-scoped, fixed). 7 primitive types: string, number, bigint, boolean, undefined, null, symbol. Everything else is an object. typeof operator checks types. Template literals use backticks with ${} for interpolation. Destructuring unpacks values from arrays and objects elegantly.",
       "code":"// Prefer const, use let only when reassigning\nconst PI    = 3.14;\nlet   score = 0;\nscore = 100;  // OK — let can be reassigned\n\n// Template literals (backticks)\nconst name = 'Alice';\nconsole.log(`Hello ${name}!`); // Hello Alice!\n\n// typeof operator\nconsole.log(typeof 42);        // 'number'\nconsole.log(typeof 'hi');      // 'string'\nconsole.log(typeof null);      // 'object' ← JS quirk!\nconsole.log(typeof undefined); // 'undefined'\n\n// Array and object destructuring\nconst [a, b]  = [1, 2];\nconst {x, y}  = {x:10, y:20};\n\n// Spread operator\nconst arr1   = [1, 2, 3];\nconst arr2   = [...arr1, 4, 5]; // [1,2,3,4,5]\nconst merged = {...obj1, ...obj2};",
       "quiz":[
         {"q":"Which JS variable declaration cannot be reassigned?","opts":["var","let","const","static"],"ans":2},
         {"q":"What does typeof null return in JavaScript?","opts":["'null'","'undefined'","'object'","'error'"],"ans":2},
         {"q":"Template literals in JavaScript use...","opts":["Single quotes","Double quotes","Backticks (`)","Parentheses"],"ans":2},
         {"q":"Which of these is NOT a JavaScript primitive type?","opts":["string","boolean","array","undefined"],"ans":2},
         {"q":"The main problem with 'var' in JavaScript is...","opts":["Can't hold numbers","Function-scoped & hoisted, causes bugs","Slower than let","Can't be undefined"],"ans":1}
       ]},
      {"id":"js_functions","title":"Functions & Arrow Functions",
       "desc":"JS supports function declarations, expressions, and arrow functions (ES6+). Arrow functions bind 'this' lexically from surrounding scope — crucial for class methods and callbacks. Functions are first-class — stored in variables, passed as arguments, returned from other functions. Default params, rest params (...args), and array methods (map, filter, reduce) are essential modern patterns.",
       "code":"// Function declaration\nfunction add(a, b) { return a + b; }\n\n// Function expression\nconst multiply = function(a, b) { return a * b; };\n\n// Arrow function — implicit return (no braces)\nconst square = x => x * x;\nconst greet  = (name, msg='Hi') => `${msg}, ${name}!`;\n\n// Arrow with body block\nconst process = (items) => {\n    return items.filter(x => x > 0);\n};\n\n// Rest parameters\nconst sum = (...nums) => nums.reduce((a,b) => a+b, 0);\nsum(1,2,3,4,5);  // 15\n\n// Array higher-order methods\n[1,2,3,4].map(x => x*2);       // [2,4,6,8]\n[1,2,3,4].filter(x => x > 2);  // [3,4]\n[1,2,3,4].reduce((a,b)=>a+b);  // 10\n[1,2,3].find(x => x > 1);      // 2",
       "quiz":[
         {"q":"Arrow functions bind 'this' from...","opts":["The function itself","Lexically from surrounding scope","Global object always","The caller"],"ans":1},
         {"q":"const f = x => x*2 defines a(n)...","opts":["Class method","Arrow function","Generator function","Async function"],"ans":1},
         {"q":"[1,2,3].map(x => x*2) returns...","opts":["[1,2,3] unchanged","[2,4,6]","The number 6","undefined"],"ans":1},
         {"q":"...args in a function definition is called...","opts":["Spread parameter","Default parameter","Rest parameter","Destructuring"],"ans":2},
         {"q":"'First-class functions' means functions can be...","opts":["They execute first","Passed/returned like any other value","Faster than methods","Always global"],"ans":1}
       ]},
      {"id":"js_dom","title":"DOM Manipulation",
       "desc":"The DOM is the browser's tree representation of an HTML document. JavaScript can select, create, modify, and delete elements. querySelector returns the first match, querySelectorAll returns all matches using CSS selectors. Use textContent for plain text (safe), innerHTML for HTML parsing. addEventListener handles all user and browser events. classList manages CSS classes dynamically.",
       "code":"// Select elements by CSS selector\nconst btn  = document.querySelector('#myBtn');\nconst list = document.querySelectorAll('.item');\n\n// Change content\nbtn.textContent = 'Click Me';          // safe plain text\nbtn.innerHTML   = '<b>Click</b> Me';  // parses HTML\n\n// Modify inline styles\nbtn.style.backgroundColor = '#6c63ff';\nbtn.style.fontSize = '18px';\n\n// CSS class manipulation\nbtn.classList.add('active');\nbtn.classList.remove('inactive');\nbtn.classList.toggle('highlight');\nconst has = btn.classList.contains('active'); // true\n\n// Create and add new elements\nconst li = document.createElement('li');\nli.textContent = 'New item';\ndocument.querySelector('ul').appendChild(li);\n\n// Attach event listeners\nbtn.addEventListener('click', (e) => {\n    e.preventDefault();\n    console.log('Clicked!', e.target);\n});",
       "quiz":[
         {"q":"Which method selects ALL elements matching a CSS selector?","opts":["getElementById","querySelector","querySelectorAll","getAll"],"ans":2},
         {"q":"Which is safer to prevent XSS attacks?","opts":["innerHTML","outerHTML","textContent","innerText"],"ans":2},
         {"q":"classList.toggle('active') does what?","opts":["Always adds class","Always removes class","Adds if absent, removes if present","Lists all classes"],"ans":2},
         {"q":"How do you correctly attach a click event handler?","opts":["element.onClick=fn","element.click(fn)","element.addEventListener('click',fn)","element.on('click',fn)"],"ans":2},
         {"q":"document.createElement('div') creates...","opts":["And immediately adds to DOM","A div NOT yet attached to the DOM","A CSS class called div","An HTML template"],"ans":1}
       ]},
      {"id":"js_async","title":"Async & Promises",
       "desc":"JavaScript is single-threaded but handles async operations via the Event Loop. Promises represent future values with three states: pending, fulfilled, rejected. async/await syntax makes async code read like synchronous code — much cleaner than .then() chains. fetch() returns a Promise for HTTP requests. Promise.all() runs multiple promises in parallel for performance.",
       "code":"// Promise basics\nconst p = new Promise((resolve, reject) => {\n    setTimeout(() => resolve('Done!'), 1000);\n});\np.then(val => console.log(val))   // 'Done!'\n .catch(err => console.error(err));\n\n// async/await — recommended modern pattern\nasync function getUser(id) {\n    try {\n        const res  = await fetch(`/api/users/${id}`);\n        if (!res.ok) throw new Error('Not found');\n        const data = await res.json();\n        return data;\n    } catch (err) {\n        console.error(err.message);\n    }\n}\n\n// Promise.all — run multiple in parallel\nasync function loadAll() {\n    const [users, posts] = await Promise.all([\n        fetch('/api/users').then(r => r.json()),\n        fetch('/api/posts').then(r => r.json())\n    ]);\n    console.log(users, posts);\n}",
       "quiz":[
         {"q":"A JavaScript Promise can be in which states?","opts":["open/closed","pending/fulfilled/rejected","running/stopped","active/inactive"],"ans":1},
         {"q":"await pauses execution until the Promise...","opts":["Times out after 1 second","Resolves or rejects","The function ends","The DOM finishes loading"],"ans":1},
         {"q":"Promise.all([p1, p2, p3]) does what?","opts":["Runs them sequentially","Runs all in parallel, waits for all","Retries on any failure","Cancels others if one fails"],"ans":1},
         {"q":"What does fetch() return?","opts":["The response data directly","A Promise","An Observable","A callback function"],"ans":1},
         {"q":"Forgetting 'await' before a Promise gives you...","opts":["The resolved value","A syntax error","The Promise object itself (not the value)","undefined always"],"ans":2}
       ]},
      {"id":"js_es6","title":"ES6+ Modern Features",
       "desc":"ES6 (2015) and later versions added revolutionary features: arrow functions, let/const, template literals, destructuring, spread/rest operators, default parameters, classes, modules (import/export), optional chaining (?.), nullish coalescing (??), and powerful array methods. These are now standard in all modern JavaScript code.",
       "code":"// Destructuring with default values\nconst {name, age=18} = {name:'Alice', age:25};\nconst [first, ...rest] = [1,2,3,4];\n\n// Optional chaining — safe property access\nconst city = user?.address?.city ?? 'Unknown';\n\n// Nullish coalescing — default only for null/undefined\nconst count = data.count ?? 0;\n\n// Essential array methods\nconst nums = [1,2,3,4,5];\nnums.map(n => n*2);            // [2,4,6,8,10]\nnums.filter(n => n%2===0);    // [2,4]\nnums.reduce((a,b)=>a+b, 0);  // 15\nnums.find(n => n>3);           // 4\nnums.includes(3);              // true\nnums.every(n => n>0);          // true\nnums.some(n => n>4);           // true\n\n// ES6 Classes with private fields\nclass Person {\n    #age;   // truly private\n    constructor(name, age){\n        this.name = name;\n        this.#age = age;\n    }\n    greet(){ return `Hi, I'm ${this.name}`; }\n}",
       "quiz":[
         {"q":"What does user?.address?.city do when address is null?","opts":["Throws a TypeError","Returns undefined safely (no error)","Creates empty address object","Assigns null to city"],"ans":1},
         {"q":"The ?? operator returns the right side when the left is...","opts":["Any falsy value","Zero or empty string","Only null or undefined","The boolean false"],"ans":2},
         {"q":"const {name} = obj is called...","opts":["Spreading","Object destructuring","Object cloning","Property mapping"],"ans":1},
         {"q":"Array.filter() returns...","opts":["The first matching element","A new array with only matching elements","true or false","The original array modified"],"ans":1},
         {"q":"ES6 modules use which keywords for import/export?","opts":["require/exports","include/export","import/export","load/module"],"ans":2}
       ]},
      {"id":"js_keywords","title":"Core Concepts & Keywords",
       "desc":"Essential JS concepts: hoisting (var declarations moved to top of scope), scope (global/function/block), closures (function retaining access to outer scope variables after that scope is gone), 'this' binding (depends on how function is called), prototype chain (how inheritance works in JS), and the event loop (how async callbacks execute without blocking).",
       "code":"// Hoisting — var is hoisted, let/const are NOT\nconsole.log(x); // undefined (no error with var!)\nvar x = 5;\n// console.log(y); // ReferenceError — let not hoisted\nlet y = 10;\n\n// Closure — inner function remembers outer scope\nfunction counter() {\n    let count = 0;\n    return {\n        inc: () => ++count,\n        get: () => count\n    };\n}\nconst c = counter();\nc.inc(); c.inc();\nconsole.log(c.get());  // 2\n\n// typeof and instanceof\nconsole.log(typeof []);           // 'object'\nconsole.log([] instanceof Array); // true\n\n// for...of vs for...in\nconst obj = {a:1, b:2};\nfor (const key in obj)  { console.log(key); }   // keys: a b\nfor (const val of [1,2,3]) { console.log(val); } // values: 1 2 3\n\n'use strict'; // enables strict mode — catches silent errors",
       "quiz":[
         {"q":"Hoisting in JavaScript applies to which declaration?","opts":["let","const","var","class declarations"],"ans":2},
         {"q":"A closure is a function that...","opts":["Is anonymous","Retains access to outer scope variables","Has no parameters","Always returns undefined"],"ans":1},
         {"q":"typeof [] returns which string?","opts":["'array'","'list'","'object'","'undefined'"],"ans":2},
         {"q":"'use strict' directive...","opts":["Makes code run faster","Enables stricter parsing and error handling","Adds new ES6 syntax","Imports a strict library"],"ans":1},
         {"q":"The Event Loop in JavaScript handles...","opts":["CSS rendering pipeline","Async callbacks without blocking the main thread","Memory garbage collection","Variable declarations"],"ans":1}
       ]}
    ]
  },
  "HTML": {
    "icon":"🌐","color":"#e34f26","level":"Beginner",
    "desc":"The skeleton of every web page — structure and semantic meaning.",
    "topics":[
      {"id":"html_structure","title":"Document Structure",
       "desc":"Every HTML5 page starts with <!DOCTYPE html>. The <html> root element contains <head> (invisible metadata) and <body> (visible content). Head holds: title (browser tab text), meta tags (charset, viewport, description), link (CSS stylesheets), and script references. The viewport meta tag is essential for mobile responsiveness. Scripts go before </body> for performance.",
       "code":"<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <meta name=\"description\" content=\"Page description for SEO\">\n    <title>Page Title — shown in browser tab</title>\n    <link rel=\"stylesheet\" href=\"styles.css\">\n    <link rel=\"icon\" href=\"favicon.ico\">\n</head>\n<body>\n    <header>\n        <h1>Main Heading</h1>\n        <nav>Navigation links here</nav>\n    </header>\n\n    <main>\n        <article>\n            <h2>Article Title</h2>\n            <p>Content goes here.</p>\n        </article>\n    </main>\n\n    <footer>\n        <p>&copy; 2024 My Website</p>\n    </footer>\n\n    <script src=\"app.js\"></script>  <!-- before </body> for performance -->\n</body>\n</html>",
       "quiz":[
         {"q":"What does <!DOCTYPE html> tell the browser?","opts":["To use HTML5 mode","To load a CSS file","The page author name","The web server type"],"ans":0},
         {"q":"Where does all visible page content belong?","opts":["<head>","<meta>","<body>","<title>"],"ans":2},
         {"q":"Which meta tag is essential for responsive mobile design?","opts":["<meta charset>","<meta viewport>","<meta responsive>","<meta mobile>"],"ans":1},
         {"q":"For performance, scripts are best placed...","opts":["Inside <head>","Just before </body>","Inside <meta>","Inside <style>"],"ans":1},
         {"q":"<link rel='stylesheet' href='style.css'> is used to...","opts":["Link to JavaScript","Load images","Load an external CSS file","Define internal styles"],"ans":2}
       ]},
      {"id":"html_tags","title":"Essential Tags",
       "desc":"HTML elements define content meaning and structure. Block elements (div, p, h1-h6, ul/ol, table, section, article, header, footer) stack vertically. Inline elements (span, a, img, strong, em, code) flow within text. Self-closing tags (img, br, hr, input) don't need a closing tag. Always include the alt attribute on images for accessibility and SEO.",
       "code":"<!-- Headings: h1 is most important, use only one per page -->\n<h1>Page Title</h1>  <!-- most important -->\n<h2>Section Heading</h2>\n<h3>Sub-section</h3>\n\n<!-- Paragraph with inline formatting elements -->\n<p>This text has <strong>bold</strong> and <em>italic</em> words.\n   Visit <a href=\"https://example.com\" target=\"_blank\">Example Site</a>.\n</p>\n\n<!-- Image — alt attribute is mandatory for accessibility -->\n<img src=\"photo.jpg\" alt=\"A smiling person at a computer\" width=\"400\">\n\n<!-- Unordered (bullet) and ordered (numbered) lists -->\n<ul>\n    <li>Python</li>\n    <li>JavaScript</li>\n</ul>\n<ol>\n    <li>Install Node.js</li>\n    <li>Run npm install</li>\n</ol>\n\n<!-- Data table with proper structure -->\n<table>\n  <thead><tr><th>Name</th><th>Score</th></tr></thead>\n  <tbody>\n    <tr><td>Alice</td><td>95</td></tr>\n  </tbody>\n</table>",
       "quiz":[
         {"q":"Which HTML tag creates a clickable hyperlink?","opts":["<link>","<href>","<a>","<url>"],"ans":2},
         {"q":"Which of these is a self-closing (void) tag?","opts":["<p>","<div>","<img>","<span>"],"ans":2},
         {"q":"<strong> makes text bold and signals...","opts":["Italic style","Semantic importance","Underlined text","Color change"],"ans":1},
         {"q":"The alt attribute on images is required for...","opts":["Styling","SEO and accessibility (screen readers)","Animation","Setting image size"],"ans":1},
         {"q":"<ul> creates which type of list?","opts":["Ordered (numbered)","Definition list","Unordered (bulleted)","Data table"],"ans":2}
       ]},
      {"id":"html_forms","title":"Forms & Inputs",
       "desc":"HTML forms collect user input and send it to a server. The action attribute specifies the URL to send data to; method is GET (data in URL) or POST (data in request body). Input types: text, email, password, number, checkbox, radio, file, date, range, color, submit. The label element improves accessibility. required, minlength, pattern add built-in browser validation.",
       "code":"<form action=\"/register\" method=\"POST\">\n\n    <!-- Text input with label for accessibility -->\n    <label for=\"name\">Full Name:</label>\n    <input type=\"text\" id=\"name\" name=\"name\"\n           placeholder=\"Alice Smith\" required minlength=\"2\">\n\n    <!-- Email — browser validates format automatically -->\n    <input type=\"email\" name=\"email\" required\n           placeholder=\"alice@example.com\">\n\n    <!-- Password — hidden characters -->\n    <input type=\"password\" name=\"pwd\" minlength=\"8\" required>\n\n    <!-- Radio buttons — same name = one choice from group -->\n    <input type=\"radio\" name=\"role\" value=\"student\" checked> Student\n    <input type=\"radio\" name=\"role\" value=\"teacher\"> Teacher\n\n    <!-- Checkbox -->\n    <input type=\"checkbox\" id=\"agree\" required>\n    <label for=\"agree\">I agree to Terms</label>\n\n    <!-- Dropdown select menu -->\n    <select name=\"language\">\n        <option value=\"\">Choose language...</option>\n        <option value=\"py\">Python</option>\n    </select>\n\n    <button type=\"submit\">Register</button>\n</form>",
       "quiz":[
         {"q":"The POST method sends form data in the...","opts":["URL query string","HTTP request body","Browser cookies","Page headers"],"ans":1},
         {"q":"Which input type automatically validates email format?","opts":["type='text'","type='mail'","type='email'","type='address'"],"ans":2},
         {"q":"A label's 'for' attribute must match the input's...","opts":["name attribute","class attribute","id attribute","type attribute"],"ans":2},
         {"q":"Which HTML attribute makes a form field mandatory?","opts":["mandatory","must","obligatory","required"],"ans":3},
         {"q":"The <select> element creates a...","opts":["Checkbox group","Radio group","Dropdown list menu","Multi-line text area"],"ans":2}
       ]},
      {"id":"html_semantic","title":"Semantic HTML5",
       "desc":"Semantic tags describe the meaning and role of content — not just how it looks. Benefits: better SEO rankings, screen reader accessibility, cleaner code structure. Key semantic elements: header (intro/nav area), nav (navigation links), main (primary content), footer (closing info), article (self-contained content), section (thematic grouping), aside (sidebar/related content), figure/figcaption.",
       "code":"<!-- AVOID: non-semantic generic divs -->\n<div id=\"nav\">navigation</div>\n<div id=\"content\">page content</div>\n\n<!-- PREFER: meaningful semantic HTML5 -->\n<header>\n    <a href=\"/\"><img src=\"logo.png\" alt=\"Company Logo\"></a>\n    <nav aria-label=\"Main navigation\">\n        <ul>\n            <li><a href=\"/\">Home</a></li>\n            <li><a href=\"/about\">About</a></li>\n        </ul>\n    </nav>\n</header>\n\n<main>\n    <article>\n        <header>\n            <h1>Blog Post Title</h1>\n            <time datetime=\"2024-01-15\">January 15, 2024</time>\n        </header>\n        <p>Article body content...</p>\n        <figure>\n            <img src=\"chart.png\" alt=\"Sales chart Q1 2024\">\n            <figcaption>Q1 2024 Sales Performance</figcaption>\n        </figure>\n    </article>\n    <aside><h2>Related Posts</h2></aside>\n</main>\n\n<footer><address>contact@example.com</address></footer>",
       "quiz":[
         {"q":"The <article> element is best used for...","opts":["Any generic container","Self-contained reusable content (like a blog post)","Navigation menus","Styling wrappers"],"ans":1},
         {"q":"The <aside> element represents...","opts":["A popup dialog","Content related but separate from main content (sidebar)","The page footer","An error notification"],"ans":1},
         {"q":"Semantic HTML primarily improves...","opts":["Page load speed","SEO rankings and screen reader accessibility","JavaScript execution","CSS specificity rules"],"ans":1},
         {"q":"<time datetime='2024-01-15'> — the datetime attribute provides...","opts":["Display text format","Machine-readable date for browsers/SEO","A CSS styling class","A JavaScript event hook"],"ans":1},
         {"q":"<nav> should contain...","opts":["All links on the entire page","The site's main navigation links","Only the footer links","Social media icons only"],"ans":1}
       ]},
      {"id":"html_attrs","title":"Attributes & Accessibility",
       "desc":"HTML attributes provide extra information and behaviour to elements. Global attributes work on any element: id (unique identifier), class (CSS targeting), style (inline CSS), title (tooltip), data-* (custom data), hidden, tabindex (keyboard navigation order), contenteditable. ARIA attributes (aria-label, aria-hidden, aria-expanded, role) make pages accessible to users with disabilities.",
       "code":"<!-- Custom data attributes — accessed via JS dataset -->\n<button data-user-id=\"42\"\n        data-action=\"delete\"\n        onclick=\"handle(this.dataset.userId)\">\n    Delete User\n</button>\n\n<!-- ARIA attributes for screen reader accessibility -->\n<button aria-label=\"Close this dialog\"\n        aria-expanded=\"false\"\n        role=\"button\"\n        onclick=\"toggleMenu()\">\n    ☰ Menu\n</button>\n\n<input type=\"text\"\n       aria-required=\"true\"\n       aria-describedby=\"name-help\"\n       placeholder=\"Full name\">\n<span id=\"name-help\">Enter your full legal name</span>\n\n<!-- Global attributes -->\n<div id=\"unique-id\"          <!-- must be unique per page -->\n     class=\"card featured\"   <!-- space-separated CSS classes -->\n     title=\"Hover tooltip\"   <!-- shown on mouse hover -->\n     tabindex=\"0\"            <!-- keyboard focusable -->\n     contenteditable=\"true\" <!-- user can edit content -->\n     hidden>                 <!-- hidden from view -->\n</div>",
       "quiz":[
         {"q":"Custom data-* attributes are accessed in JavaScript via...","opts":["element.data","element.attr","element.dataset","element.custom"],"ans":2},
         {"q":"The aria-label attribute provides...","opts":["CSS styling rules","An accessible name for screen reader users","A browser tooltip","A data storage value"],"ans":1},
         {"q":"tabindex='0' makes an element...","opts":["Completely hidden","First in tab order","Focusable in natural DOM order","Disabled for interaction"],"ans":2},
         {"q":"The 'hidden' HTML attribute...","opts":["Makes element transparent","Hides element visually but keeps it in DOM","Removes element from DOM","Disables element interaction"],"ans":1},
         {"q":"The id attribute on an HTML element must be...","opts":["Reusable across elements","Always lowercase","Unique within the entire page","Always a number"],"ans":2}
       ]}
    ]
  },
  "CSS": {
    "icon":"🎨","color":"#264de4","level":"Beginner",
    "desc":"Style language that makes web pages beautiful, responsive, and animated.",
    "topics":[
      {"id":"css_selectors","title":"Selectors & Specificity",
       "desc":"CSS selectors target HTML elements for styling. Types: element (p), class (.btn), ID (#id), attribute ([type='text']), pseudo-class (:hover, :focus, :nth-child), pseudo-element (::before, ::after), combinators (> direct child, space descendant, + adjacent sibling, ~ general sibling). Specificity determines which rule wins when rules conflict. Order: inline style > ID > class > element.",
       "code":"/* Element, Class, ID selectors */\np    { color: #333; line-height: 1.6; }\n.btn { padding: 10px 20px; cursor: pointer; border-radius: 8px; }\n#nav { position: fixed; top: 0; width: 100%; z-index: 100; }\n\n/* Pseudo-classes — element state */\na:hover       { color: crimson; text-decoration: none; }\ninput:focus   { outline: 2px solid blue; box-shadow: 0 0 8px rgba(0,0,255,.3); }\nli:nth-child(odd) { background: #f5f5f5; }\nbutton:disabled   { opacity: 0.5; cursor: not-allowed; }\n\n/* Pseudo-elements — virtual elements */\n.card::before { content: '★'; color: gold; margin-right: 4px; }\np::first-letter { font-size: 2em; float: left; margin-right: 4px; }\n\n/* Combinators */\nnav > a   { color: white; }        /* only direct children */\narticle p { line-height: 1.8; }   /* all descendant p */\nh2 + p    { margin-top: 0; }      /* adjacent sibling */\n\n/* Attribute selectors */\ninput[type='email']  { border-color: blue; }\na[href^='https']     { color: green; }  /* href starts with https */",
       "quiz":[
         {"q":"Which CSS rule has the highest specificity (wins)?","opts":["p { color: red; }",".btn { color: red; }","#id { color: red; }","inline style=\"color:red\""],"ans":3},
         {"q":"The CSS combinator 'nav > a' selects...","opts":["All a tags on the page","Any a anywhere inside nav","Only direct child a elements of nav","a elements that come after nav"],"ans":2},
         {"q":"::before is classified as a CSS...","opts":["Pseudo-class","Attribute selector","Pseudo-element","Sibling combinator"],"ans":2},
         {"q":"li:nth-child(2) selects...","opts":["All li elements","The second li element","Even-numbered li elements","The first li element"],"ans":1},
         {"q":"input[type='email'] is an example of a(n)...","opts":["ID selector","Attribute selector","Class selector","Pseudo-class selector"],"ans":1}
       ]},
      {"id":"css_box","title":"Box Model & Positioning",
       "desc":"Every HTML element is a rectangular box with four layers (inside-out): content, padding (inside border), border, and margin (outside border). box-sizing: border-box makes width include padding and border — strongly recommended. display controls layout: block (full width, new line), inline (flows with text), inline-block (inline + dimensions), flex, grid, none (hidden, removed from flow). position: static (default), relative, absolute, fixed, sticky.",
       "code":"/* Box model with border-box (recommended) */\n.box {\n    width: 300px;\n    height: 200px;\n    padding: 20px;           /* inside the border */\n    border: 2px solid #333;\n    margin: 10px auto;       /* auto = center horizontally */\n    box-sizing: border-box;  /* width includes padding+border */\n    border-radius: 12px;     /* rounded corners */\n    overflow: hidden;        /* clip content that overflows */\n}\n\n/* Display types */\nspan { display: inline-block; width: 50px; height: 50px; }\n.hidden { display: none; }  /* removed from layout */\n.invisible { visibility: hidden; } /* hidden but keeps space */\n\n/* Positioning */\n.relative { position: relative; top: 10px; left: 20px; }\n\n.overlay {\n    position: absolute;\n    top: 0; left: 0; right: 0; bottom: 0;\n    background: rgba(0,0,0,0.5);\n}\n\n.navbar { position: fixed; top: 0; width: 100%; z-index: 1000; }\n\n.sticky-sidebar { position: sticky; top: 20px; }",
       "quiz":[
         {"q":"margin: 0 auto on a block element does what?","opts":["Removes all margins","Centers the element horizontally","Centers the element vertically","Sets margin to auto pixels"],"ans":1},
         {"q":"box-sizing: border-box means the element's width...","opts":["Includes only content","Includes content, padding, and border","Removes the box model","Makes border color automatic"],"ans":1},
         {"q":"position: sticky behaves as...","opts":["Always fixed at viewport top","Relative until scroll threshold, then fixed in place","Same as absolute positioning","Same as fixed positioning"],"ans":1},
         {"q":"display:none vs visibility:hidden — the key difference is...","opts":["They are identical","none removes from layout; hidden keeps space","hidden removes from layout","Both still take up space"],"ans":1},
         {"q":"The CSS z-index property controls...","opts":["Zoom level of element","Horizontal element position","Stacking order (which element appears on top)","Text size scaling"],"ans":2}
       ]},
      {"id":"css_flex","title":"Flexbox Layout",
       "desc":"Flexbox is a 1D layout model. Apply display: flex to the container. flex-direction sets the main axis (row or column). justify-content aligns items along the main axis. align-items aligns on the cross axis. flex-wrap allows multi-line flex containers. gap adds space between items without needing margins. Child items control growth with flex-grow, shrinking with flex-shrink, and base size with flex-basis (shorthand: flex).",
       "code":"/* Flex container properties */\n.container {\n    display: flex;\n    flex-direction: row;            /* row | column | row-reverse | column-reverse */\n    justify-content: space-between; /* main axis: start|center|end|space-between|space-around */\n    align-items: center;            /* cross axis: stretch|start|center|end|baseline */\n    flex-wrap: wrap;                /* allow items to wrap to next line */\n    gap: 16px;                      /* space between items (no extra margin needed) */\n}\n\n/* Perfect centering pattern */\n.center-everything {\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    min-height: 100vh;\n}\n\n/* Navbar layout pattern */\n.navbar {\n    display: flex;\n    justify-content: space-between;\n    align-items: center;\n    padding: 0 24px;\n}\n\n/* Flex item sizing */\n.item-grow  { flex: 1; }           /* grows to fill available space */\n.item-fixed { flex: 0 0 200px; }  /* always exactly 200px, no grow/shrink */\n.item-double { flex: 2; }          /* twice as wide as flex: 1 items */",
       "quiz":[
         {"q":"In a flex container, justify-content controls alignment on the...","opts":["Cross axis","Main axis (flex-direction axis)","Both axes simultaneously","The Z axis"],"ans":1},
         {"q":"align-items: center in a flex container aligns on the...","opts":["Main axis","Cross axis (perpendicular to flex-direction)","Horizontal axis always","Vertical axis only"],"ans":1},
         {"q":"Setting flex: 1 on a flex item makes it...","opts":["Exactly 1px wide","Grow to fill remaining available space","Only shrink, never grow","Not participate in flex"],"ans":1},
         {"q":"The gap property in a flex container...","opts":["Adds padding to the container itself","Adds space between each flex item","Sets the flex-direction","Enables flex-wrap"],"ans":1},
         {"q":"flex-wrap: wrap allows flex items to...","opts":["Only stay in one row","Wrap to the next line when container is full","Create vertical flexbox","Disable wrapping"],"ans":1}
       ]},
      {"id":"css_responsive","title":"Responsive Design",
       "desc":"Responsive design makes websites adapt to any screen size. Media queries apply CSS rules at specific viewport breakpoints. Mobile-first approach: write base styles for small screens, then use min-width queries to add styles for larger screens. Fluid units: % (relative to parent), vw/vh (viewport percentage), rem (root em — based on root font size), em (parent font size). CSS Grid enables complex 2D layout with rows and columns.",
       "code":"/* Mobile-first: start with small screen base styles */\n.container { width: 100%; padding: 0 16px; }\n.cards { display: flex; flex-direction: column; gap: 16px; }\n\n/* Tablet: min-width 768px and above */\n@media (min-width: 768px) {\n    .container { max-width: 720px; margin: 0 auto; }\n    .cards {\n        flex-direction: row;\n        flex-wrap: wrap;\n    }\n    .card { flex: 0 0 calc(50% - 8px); }\n}\n\n/* Desktop: min-width 1024px and above */\n@media (min-width: 1024px) {\n    .container { max-width: 960px; }\n    .cards {\n        display: grid;\n        grid-template-columns: repeat(3, 1fr);\n        gap: 24px;\n    }\n}\n\n/* Fluid typography — scales between min and max */\nh1 { font-size: clamp(24px, 5vw, 56px); }\n\n/* Always make images responsive */\nimg { max-width: 100%; height: auto; display: block; }",
       "quiz":[
         {"q":"Mobile-first CSS design means...","opts":["Design only for mobile screens","Write base styles for mobile, add min-width queries for larger screens","Use a mobile CSS framework","Test only on mobile devices"],"ans":1},
         {"q":"100vh in CSS equals...","opts":["Exactly 100 pixels","100% of the browser viewport height","100 root em units","100% of the parent element height"],"ans":1},
         {"q":"clamp(24px, 5vw, 56px) for font-size means...","opts":["A random value between those","Minimum 24px, preferred 5vw, maximum 56px","Always exactly 5vw","Clamps CSS parsing errors"],"ans":1},
         {"q":"@media (min-width: 768px) CSS rules apply when...","opts":["Viewport is less than 768px","Viewport is exactly 768px","Viewport is 768px or wider","Device is a mobile phone"],"ans":2},
         {"q":"The 1rem unit is always relative to...","opts":["The direct parent element's font size","The viewport width","The root <html> element's font size","The browser's default font only"],"ans":2}
       ]},
      {"id":"css_vars","title":"CSS Variables & Animations",
       "desc":"CSS custom properties (variables) store reusable values. Define on :root with --name: value syntax, use anywhere with var(--name). They cascade like regular properties and can be overridden for theming (like dark mode). CSS transitions animate property changes smoothly over time. @keyframes define complex multi-step animations. transform manipulates elements without reflow — more performant than changing position/size directly.",
       "code":"/* Define CSS variables on :root for global access */\n:root {\n    --color-primary: #6c63ff;\n    --color-text:    #1a1a2e;\n    --spacing-md:    16px;\n    --border-radius: 8px;\n    --shadow: 0 4px 20px rgba(0,0,0,0.1);\n}\n\n.button {\n    background:    var(--color-primary);\n    padding:       var(--spacing-md);\n    border-radius: var(--border-radius);\n    box-shadow:    var(--shadow);\n}\n\n/* Dark mode — override variables */\n[data-theme='dark'] {\n    --color-text:    #ffffff;\n    --color-primary: #a78bfa;\n}\n\n/* Smooth hover transition */\n.button {\n    transition: transform 0.2s ease, box-shadow 0.3s ease;\n}\n.button:hover {\n    transform: translateY(-3px) scale(1.02);\n    box-shadow: 0 8px 30px rgba(108,99,255,0.45);\n}\n\n/* Multi-step keyframe animation */\n@keyframes fadeSlideIn {\n    0%   { opacity: 0; transform: translateY(30px); }\n    100% { opacity: 1; transform: translateY(0); }\n}\n.card {\n    animation: fadeSlideIn 0.5s ease forwards;\n    animation-delay: 0.1s;  /* stagger with multiple delays */\n}",
       "quiz":[
         {"q":"CSS custom properties (variables) are defined using...","opts":["$name: value (like Sass)","@name: value","--name: value","var-name: value"],"ans":2},
         {"q":"To use a CSS variable named --primary-color you write...","opts":["$(--primary-color)","var(--primary-color)","@var(primary-color)","#{--primary-color}"],"ans":1},
         {"q":"transition: all 0.3s ease on an element...","opts":["Only animates color","Only applies on hover","Smoothly animates ANY property change over 0.3 seconds","Triggers on JavaScript events only"],"ans":2},
         {"q":"transform: translateY(-3px) moves the element...","opts":["3px downward","3px to the left","3px upward (negative Y = up)","3px to the right"],"ans":2},
         {"q":"@keyframes in CSS is used to define...","opts":["A media query breakpoint","A CSS custom property","A multi-step animation sequence","A CSS class selector"],"ans":2}
       ]}
    ]
  },
  "Bootstrap": {
    "icon":"🅱️","color":"#7952b3","level":"Intermediate",
    "desc":"Most popular CSS framework — build responsive, professional UIs rapidly.",
    "topics":[
      {"id":"bs_grid","title":"Grid System & Setup",
       "desc":"Bootstrap 5 uses a 12-column responsive grid system. Include via CDN links in HTML. Three container types: container (fixed max-width at breakpoints), container-fluid (always 100% width), container-{bp} (fluid until that breakpoint). Rows (row class) contain columns (col-* classes). Breakpoints: xs (<576px), sm (≥576), md (≥768), lg (≥992), xl (≥1200), xxl (≥1400).",
       "code":"<!-- Bootstrap 5 CDN (in <head>) -->\n<link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css\" rel=\"stylesheet\">\n<!-- Bootstrap JS bundle (before </body>) -->\n<script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js\"></script>\n\n<!-- Two equal columns (6+6=12) -->\n<div class=\"container\">\n  <div class=\"row\">\n    <div class=\"col-6\">Left half</div>\n    <div class=\"col-6\">Right half</div>\n  </div>\n</div>\n\n<!-- Responsive: stacked on mobile, 3 cols on md+ -->\n<div class=\"row\">\n  <div class=\"col-12 col-md-4\">Column 1</div>\n  <div class=\"col-12 col-md-4\">Column 2</div>\n  <div class=\"col-12 col-md-4\">Column 3</div>\n</div>\n\n<!-- Auto-width equal columns -->\n<div class=\"row\">\n  <div class=\"col\">Auto 1</div>\n  <div class=\"col\">Auto 2</div>\n  <div class=\"col\">Auto 3</div>\n</div>\n\n<!-- Centered column with offset -->\n<div class=\"row\">\n  <div class=\"col-md-6 offset-md-3\">Centered</div>\n</div>",
       "quiz":[
         {"q":"Bootstrap's grid system divides rows into how many columns?","opts":["10","12","16","24"],"ans":1},
         {"q":"The class col-md-6 makes an element take up...","opts":["6px wide on medium screens","6 of 12 columns wide on medium screens and above","6% of its container","Half width on mobile only"],"ans":1},
         {"q":"Which Bootstrap container class is ALWAYS 100% wide?","opts":["container","container-lg","container-fluid","container-full"],"ans":2},
         {"q":"Bootstrap 5's 'md' breakpoint starts at what width?","opts":["576px","768px","992px","1200px"],"ans":1},
         {"q":"The class offset-md-3 on a column does what?","opts":["Makes the column 3 units wide","Adds a left margin equal to 3 columns","Hides 3 columns","Makes column span 3 rows"],"ans":1}
       ]},
      {"id":"bs_components","title":"Core Components",
       "desc":"Bootstrap includes dozens of pre-built UI components. Buttons combine btn (base) with color variants (btn-primary, btn-danger, etc.) and size modifiers (btn-lg, btn-sm). Cards are flexible content containers with card-body, card-title, card-footer. Alerts show contextual messages with dismissible option. Badges show small counts or status. Progress bars show completion percentage.",
       "code":"<!-- Buttons with variants and sizes -->\n<button class=\"btn btn-primary\">Primary</button>\n<button class=\"btn btn-outline-danger btn-lg\">Large Outline Danger</button>\n<button class=\"btn btn-success btn-sm\">Small Success</button>\n\n<!-- Card component -->\n<div class=\"card shadow-sm\" style=\"width: 300px\">\n  <img src=\"img.jpg\" class=\"card-img-top\" alt=\"Card image\">\n  <div class=\"card-body\">\n    <h5 class=\"card-title\">Card Title</h5>\n    <p class=\"card-text\">Card description text goes here.</p>\n    <a href=\"#\" class=\"btn btn-primary w-100\">Go somewhere</a>\n  </div>\n  <div class=\"card-footer text-muted small\">Updated 3 days ago</div>\n</div>\n\n<!-- Dismissible alert -->\n<div class=\"alert alert-success alert-dismissible fade show\">\n  ✅ Operation completed successfully!\n  <button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\"></button>\n</div>\n\n<!-- Badge in button + Progress bar -->\n<button class=\"btn btn-primary\">\n  Inbox <span class=\"badge bg-danger rounded-pill\">5</span>\n</button>\n<div class=\"progress mt-3\" style=\"height:12px\">\n  <div class=\"progress-bar bg-success\" style=\"width:75%\">75%</div>\n</div>",
       "quiz":[
         {"q":"Which class creates a Bootstrap-styled danger button?","opts":["btn-red","btn-danger","button-danger","bs-danger"],"ans":1},
         {"q":"btn-outline-primary creates a button that is...","opts":["Solid primary color filled","Transparent background with primary colored border","Disabled state","Small sized"],"ans":1},
         {"q":"The card-body class wraps what content?","opts":["The entire card","Only the card image","Card text content (title, text, buttons)","The card footer only"],"ans":2},
         {"q":"data-bs-dismiss='alert' on a button does what?","opts":["Applies alert styling","Dismisses and hides the alert","Adds a fade animation","Opens the alert"],"ans":1},
         {"q":"Bootstrap badges are primarily used to display...","opts":["Large section labels","Tooltips on hover","Small count numbers or status indicators","Dropdown menus"],"ans":2}
       ]},
      {"id":"bs_utilities","title":"Utility Classes",
       "desc":"Bootstrap 5 utility classes apply single CSS properties instantly without writing custom CSS. Spacing uses m- (margin) and p- (padding) with side abbreviations: t (top), b (bottom), s (start/left), e (end/right), x (horizontal), y (vertical), and sizes 0-5 or auto. Colors: text-{color}, bg-{color}. Typography: fw-bold, fst-italic, fs-{1-6}, text-center/start/end/uppercase. Display: d-flex, d-none, d-block.",
       "code":"<!-- Spacing utilities: m=margin, p=padding -->\n<!-- Sides: t=top, b=bottom, s=start(left), e=end(right), x=both-x, y=both-y -->\n<!-- Sizes: 0=0, 1=0.25rem, 2=0.5rem, 3=1rem, 4=1.5rem, 5=3rem, auto=auto -->\n<div class=\"mt-3 mb-2 px-4 py-2 border\">Spaced element</div>\n<div class=\"mx-auto\" style=\"width:200px\">Horizontally centered</div>\n\n<!-- Color utilities -->\n<p class=\"text-primary fw-bold\">Bold blue text</p>\n<p class=\"text-danger fst-italic\">Italic red text</p>\n<div class=\"bg-warning text-dark p-3\">Warning background</div>\n<div class=\"bg-dark text-white p-3\">Dark background</div>\n\n<!-- Typography utilities -->\n<h1 class=\"fs-1 fw-bold text-center text-uppercase\">Big Bold Header</h1>\n<p class=\"text-muted small\">Small muted description</p>\n<p class=\"text-truncate\" style=\"width:150px\">This text is too long...</p>\n\n<!-- Flexbox utilities -->\n<div class=\"d-flex justify-content-between align-items-center gap-3\">\n  <span>Left side</span>\n  <span>Right side</span>\n</div>\n\n<!-- Responsive display -->\n<div class=\"d-none d-md-block\">Hidden on mobile, visible tablet+</div>",
       "quiz":[
         {"q":"The Bootstrap class mt-3 applies...","opts":["margin to all four sides","margin-top equal to 1rem (size 3)","padding-top","margin-bottom"],"ans":1},
         {"q":"The d-flex utility class applies which CSS property?","opts":["display: block","display: inline","display: flex","display: grid"],"ans":2},
         {"q":"The Bootstrap class fw-bold applies...","opts":["font-style: italic","font-weight: bold (700)","font-size: large","font-family change"],"ans":1},
         {"q":"text-truncate in Bootstrap...","opts":["Completely removes the text","Shows ellipsis (...) when text overflows","Centers the text","Makes text uppercase"],"ans":1},
         {"q":"The gap-3 class in a flex container...","opts":["Adds 3px of padding to container","Creates 1rem gap between flex items","Sets font size to 3","Sets z-index to 3"],"ans":1}
       ]},
      {"id":"bs_forms","title":"Bootstrap Forms",
       "desc":"Bootstrap enhances form elements with utility classes. form-control styles text inputs, textareas, and select elements. form-label styles labels. form-select styles dropdown selects. form-check styles checkboxes and radio buttons. input-group wraps inputs to add prepended/appended text or buttons. form-floating creates animated floating labels that rise when the input is focused.",
       "code":"<form class=\"needs-validation\" novalidate>\n  <!-- Standard labeled input with validation -->\n  <div class=\"mb-3\">\n    <label for=\"email\" class=\"form-label fw-semibold\">Email address *</label>\n    <input type=\"email\" class=\"form-control form-control-lg\" id=\"email\"\n           placeholder=\"name@example.com\" required>\n    <div class=\"invalid-feedback\">Please provide a valid email.</div>\n    <div class=\"valid-feedback\">Looks good!</div>\n  </div>\n\n  <!-- Input group with prepended @ symbol -->\n  <div class=\"input-group mb-3\">\n    <span class=\"input-group-text\">@</span>\n    <input type=\"text\" class=\"form-control\" placeholder=\"Username\">\n  </div>\n\n  <!-- Floating label animation -->\n  <div class=\"form-floating mb-3\">\n    <input type=\"password\" class=\"form-control\" id=\"pwd\" placeholder=\"Password\">\n    <label for=\"pwd\">Password</label>\n  </div>\n\n  <!-- Styled select dropdown -->\n  <select class=\"form-select mb-3\">\n    <option selected disabled>Choose a language...</option>\n    <option>Python</option>\n    <option>JavaScript</option>\n  </select>\n\n  <!-- Styled checkbox -->\n  <div class=\"form-check mb-3\">\n    <input class=\"form-check-input\" type=\"checkbox\" id=\"agree\" required>\n    <label class=\"form-check-label\" for=\"agree\">I agree to the Terms</label>\n  </div>\n\n  <button type=\"submit\" class=\"btn btn-primary w-100 btn-lg\">Submit</button>\n</form>",
       "quiz":[
         {"q":"The Bootstrap form-control class is applied to which elements?","opts":["Only <form> itself","Only <label> elements","<input>, <textarea>, and <select> elements","Only <button> elements"],"ans":2},
         {"q":"form-floating in Bootstrap creates...","opts":["Server-side form validation","An animated label that rises above the input when focused","Grouping multiple form sections","Adding icons to inputs"],"ans":1},
         {"q":"The input-group Bootstrap component is used to...","opts":["Group multiple separate forms","Add prepended/appended content (text, buttons) to an input","Validate form inputs automatically","Create radio button groups"],"ans":1},
         {"q":"The needs-validation class in Bootstrap enables...","opts":["Automatic server validation","CSS validation state styles (valid/invalid visual feedback)","AJAX form auto-submission","Required field asterisks"],"ans":1},
         {"q":"The form-check class is specifically for styling...","opts":["Text input fields","Checkboxes and radio buttons","Dropdown menus","Toggle switches only"],"ans":1}
       ]},
      {"id":"bs_interactive","title":"Modals & JS Components",
       "desc":"Bootstrap's interactive components require the bootstrap.bundle.min.js file. Modal dialogs are triggered by data-bs-toggle='modal' and data-bs-target='#id' attributes. Collapse shows/hides content. Dropdown shows a menu. Tooltips and Popovers add contextual information. Toast shows brief auto-dismissing notifications. All can also be controlled programmatically: new bootstrap.Modal(element).show().",
       "code":"<!-- Trigger button opens the modal -->\n<button type=\"button\" class=\"btn btn-primary\"\n        data-bs-toggle=\"modal\"\n        data-bs-target=\"#exampleModal\">\n  Open Modal\n</button>\n\n<!-- Modal HTML (place anywhere in body) -->\n<div class=\"modal fade\" id=\"exampleModal\" tabindex=\"-1\">\n  <div class=\"modal-dialog modal-dialog-centered\">\n    <div class=\"modal-content\">\n      <div class=\"modal-header\">\n        <h5 class=\"modal-title\">Modal Title</h5>\n        <button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"modal\"></button>\n      </div>\n      <div class=\"modal-body\">\n        <p>Modal body content goes here.</p>\n      </div>\n      <div class=\"modal-footer\">\n        <button class=\"btn btn-secondary\" data-bs-dismiss=\"modal\">Close</button>\n        <button class=\"btn btn-primary\">Save Changes</button>\n      </div>\n    </div>\n  </div>\n</div>\n\n<!-- Collapse / accordion panel -->\n<button class=\"btn btn-info\"\n        data-bs-toggle=\"collapse\"\n        data-bs-target=\"#collapseSection\">Toggle Content</button>\n<div class=\"collapse\" id=\"collapseSection\">\n  <div class=\"card card-body mt-2\">Revealed content!</div>\n</div>",
       "quiz":[
         {"q":"data-bs-toggle='modal' on a trigger button...","opts":["Creates a new modal element","Opens/shows the targeted modal","Closes the currently open modal","Applies modal styles to the button"],"ans":1},
         {"q":"data-bs-dismiss='modal' on a button inside a modal...","opts":["Opens the modal","Applies dismiss styles","Closes the modal","Prevents page navigation"],"ans":2},
         {"q":"modal-dialog-centered makes the modal appear...","opts":["Stretched to full screen","Vertically and horizontally centered in viewport","Left-aligned","Scrollable inside"],"ans":1},
         {"q":"A Bootstrap Toast component is used to show...","opts":["Error pages","Brief auto-dismissing notification messages","Large confirmation dialogs","Persistent popup windows"],"ans":1},
         {"q":"data-bs-toggle='collapse' with data-bs-target...","opts":["Opens a modal dialog","Shows or hides the targeted element","Creates a dropdown menu","Triggers an animation only"],"ans":1}
       ]}
    ]
  },
  "Node.js": {
    "icon":"🟢","color":"#339933","level":"Intermediate",
    "desc":"Run JavaScript on the server — build APIs, real-time apps, CLI tools.",
    "topics":[
      {"id":"node_basics","title":"Node.js Fundamentals",
       "desc":"Node.js is a runtime that executes JavaScript outside the browser, built on Chrome's V8 engine. Its defining feature is non-blocking I/O — it never waits for slow operations (file reads, network requests) to complete before handling the next task. This makes it highly efficient for I/O-heavy applications. Key globals: global, process, __dirname, __filename, Buffer, console.",
       "code":"// hello.js — run with: node hello.js\nconsole.log('Node.js version:', process.version);  // e.g. v20.10.0\nconsole.log('Platform:', process.platform);         // linux, darwin, win32\nconsole.log('Current directory:', __dirname);\nconsole.log('Current file:', __filename);\n\n// Non-blocking I/O demonstration\nconsole.log('1. Start');\n\nsetTimeout(() => {\n    console.log('3. Async callback fires after current stack clears');\n}, 0);\n\nconsole.log('2. End');  // runs before setTimeout!\n// Output order: 1 → 2 → 3\n\n// Command line arguments\n// Run: node app.js Alice 25\nconst [,, name, age] = process.argv;\nconsole.log(`Hello ${name}, you are ${age}`);\n\n// Environment variables (from .env file)\nconst PORT = process.env.PORT || 3000;\nconsole.log(`Server port: ${PORT}`);",
       "quiz":[
         {"q":"Node.js executes JavaScript using which engine?","opts":["SpiderMonkey (Firefox)","V8 (Chrome)","Chakra (Edge)","JavaScriptCore (Safari)"],"ans":1},
         {"q":"The __dirname global in Node.js provides...","opts":["The process ID","The absolute path of the current file's directory","The root directory","The OS home directory"],"ans":1},
         {"q":"Node.js handles many concurrent connections efficiently using...","opts":["Multiple operating system threads","Process forking for each request","Non-blocking I/O via the Event Loop","A thread pool for all tasks"],"ans":2},
         {"q":"process.exit(0) signals to the OS...","opts":["Error/abnormal exit","Process should pause","Successful/normal exit","Process should restart"],"ans":2},
         {"q":"To execute a Node.js script called 'server.js', you run...","opts":["npm server.js","javascript server.js","node server.js","run server.js"],"ans":2}
       ]},
      {"id":"node_modules","title":"Modules & npm",
       "desc":"Node uses CommonJS by default: require() imports modules, module.exports exports them. ES Modules are supported with import/export when using .mjs extension or 'type': 'module' in package.json. Built-in modules: fs (filesystem), http (HTTP server), path (path utilities), os (OS info), events (EventEmitter), crypto (cryptography). npm is the package manager — npm install adds to node_modules.",
       "code":"// Import built-in modules (CommonJS)\nconst fs   = require('fs');      // filesystem operations\nconst path = require('path');    // cross-platform paths\nconst os   = require('os');      // operating system info\n\n// Synchronous vs Asynchronous file operations\nconst content = fs.readFileSync('data.txt', 'utf8');    // SYNC — blocks!\n\nfs.readFile('data.txt', 'utf8', (err, data) => {       // ASYNC — non-blocking\n    if (err) throw err;\n    console.log(data);\n});\n\n// Path utilities — cross-platform safe\nconst fullPath = path.join(__dirname, 'data', 'users.json');\nconst ext      = path.extname('index.html');  // '.html'\nconst base     = path.basename('/a/b/c.js'); // 'c.js'\nconst dir      = path.dirname('/a/b/c.js');  // '/a/b'\n\n// Create and export a module (math.js)\nmodule.exports = {\n    add:      (a, b) => a + b,\n    multiply: (a, b) => a * b,\n    PI: 3.14159\n};\n// Use it: const { add, PI } = require('./math');",
       "quiz":[
         {"q":"How do you import a module in Node.js using CommonJS syntax?","opts":["import fs from 'fs'","include('fs')","const fs = require('fs')","load('fs')"],"ans":2},
         {"q":"module.exports in Node.js is used to...","opts":["Import external dependencies","Export values/functions from a module file","List installed dependencies","Load environment variables"],"ans":1},
         {"q":"Which Node.js built-in module handles file system operations?","opts":["file","io","fs","storage"],"ans":2},
         {"q":"The node_modules folder should NOT be committed to Git because...","opts":["It contains sensitive passwords","It can be fully recreated with 'npm install'","Node.js deletes it on startup","It contains compiled binary code only"],"ans":1},
         {"q":"path.join(__dirname, 'data', 'users.json') creates...","opts":["A new file at that path","An OS-safe absolute file path string","A URL for HTTP requests","A module reference name"],"ans":1}
       ]},
      {"id":"node_express","title":"Express.js Web Framework",
       "desc":"Express is Node.js's most popular web framework — minimal, fast, and flexible. Create an app with express(). Define routes with app.get/post/put/delete(path, callback). Middleware functions run between request and response — use app.use() to register them. Access data from requests via req.params (URL params), req.query (query string), req.body (POST body), req.headers. Send responses with res.json(), res.send(), res.status(), res.redirect().",
       "code":"const express = require('express');\nconst app     = express();\n\n// Built-in middleware\napp.use(express.json());           // parse JSON request bodies\napp.use(express.static('public')); // serve static files from /public\n\n// Custom middleware — runs on every request\napp.use((req, res, next) => {\n    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);\n    next();  // CRITICAL: must call next() to continue!\n});\n\n// GET route — homepage\napp.get('/', (req, res) => {\n    res.send('<h1>Hello from Express!</h1>');\n});\n\n// URL parameter — GET /api/users/42\napp.get('/api/users/:id', (req, res) => {\n    const { id } = req.params;  // '42'\n    res.json({ id, name: 'Alice', email: 'alice@example.com' });\n});\n\n// Query string — GET /api/search?q=python&limit=10\napp.get('/api/search', (req, res) => {\n    const { q, limit = 10 } = req.query;\n    res.json({ query: q, limit, results: [] });\n});\n\n// POST with body — create resource\napp.post('/api/users', (req, res) => {\n    const { name, email } = req.body;\n    if (!name || !email)\n        return res.status(400).json({ error: 'Name and email required' });\n    res.status(201).json({ id: Date.now(), name, email, created: new Date() });\n});\n\napp.listen(3000, () => console.log('🚀 Server running on http://localhost:3000'));",
       "quiz":[
         {"q":"Which Express middleware function parses JSON request bodies?","opts":["express.text()","express.urlencoded()","express.json()","bodyParser.json() only"],"ans":2},
         {"q":"In the route '/api/users/:id', the :id part is a...","opts":["Required static path segment","Query string parameter","Dynamic URL parameter accessed via req.params","Route wildcard"],"ans":2},
         {"q":"In Express middleware, calling next() does what?","opts":["Ends the request-response cycle","Sends a response to the client","Passes control to the next middleware or route handler","Logs an error message"],"ans":2},
         {"q":"res.status(201).json({data}) sends the client...","opts":["A redirect response","An error response","A JSON response with HTTP status code 201 Created","A file download"],"ans":2},
         {"q":"express.static('public') makes Express...","opts":["Serve database queries","Automatically serve files from the 'public' folder","Create API endpoints dynamically","Compile templates"],"ans":1}
       ]},
      {"id":"node_async","title":"Async Programming Patterns",
       "desc":"Node.js evolved through three async patterns. Callbacks (original): error-first convention (err, data) → lead to 'callback hell' with deep nesting. Promises (.then/.catch): chainable, avoid nesting but can get complex. async/await (modern standard): cleaner syntax, uses try/catch for error handling. fs.promises provides Promise-based file operations. Promise.all() runs operations in parallel for performance.",
       "code":"const fs = require('fs').promises;  // promise-based fs\n\n// ✅ Modern async/await pattern (recommended)\nasync function processFile(filename) {\n    try {\n        const content = await fs.readFile(filename, 'utf8');\n        const lines   = content.split('\\n').length;\n        const stats   = `Lines: ${lines}, File: ${filename}`;\n        await fs.writeFile('output.txt', stats);\n        return { lines, filename };\n    } catch (err) {\n        console.error('Error:', err.message);\n        throw err;  // re-throw so caller can handle\n    }\n}\n\n// ✅ Parallel operations — much faster than sequential await\nasync function processAllFiles() {\n    const [file1, file2, file3] = await Promise.all([\n        fs.readFile('a.txt', 'utf8'),\n        fs.readFile('b.txt', 'utf8'),\n        fs.readFile('c.txt', 'utf8')\n    ]);\n    return [file1, file2, file3];\n}\n\n// EventEmitter pattern\nconst { EventEmitter } = require('events');\nconst emitter = new EventEmitter();\n\nemitter.on('userJoined', (user) => {\n    console.log(`${user.name} joined the chat!`);\n});\n\nemitter.emit('userJoined', { name: 'Alice', id: 42 });",
       "quiz":[
         {"q":"The error-first callback convention means the callback's first argument is...","opts":["Always the result data","The error object (or null if no error)","The function name","A boolean success flag"],"ans":1},
         {"q":"Promise.all([p1, p2, p3]) rejects when...","opts":["All three promises reject","Any single one of the promises rejects","More than half reject","The last one to settle rejects"],"ans":1},
         {"q":"require('fs').promises provides...","opts":["Synchronous file operations","Callback-based async file operations","Promise-based async file operations","Stream-based file operations"],"ans":2},
         {"q":"EventEmitter's .on() method does what?","opts":["Emits/fires an event","Removes an event listener","Registers a listener function for a named event","Creates a new event type"],"ans":2},
         {"q":"'Callback hell' in Node.js refers to...","opts":["Too many event listeners","Deeply nested callbacks making code hard to read and maintain","Stack overflow from recursion","Unhandled promise rejections"],"ans":1}
       ]},
      {"id":"node_api","title":"Building REST APIs",
       "desc":"REST (Representational State Transfer) APIs use HTTP methods semantically: GET (retrieve), POST (create), PUT (replace), PATCH (partial update), DELETE (remove). HTTP status codes communicate result: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error. Express Router organizes routes into modular files. Always validate input. Never expose secrets — use environment variables.",
       "code":"const express = require('express');\nconst router  = express.Router();\n\n// In-memory store (use a real DB in production!)\nlet users = [\n    { id: 1, name: 'Alice', email: 'alice@example.com', role: 'admin' },\n    { id: 2, name: 'Bob',   email: 'bob@example.com',   role: 'user'  }\n];\n\n// GET all users — 200 OK\nrouter.get('/', (req, res) => {\n    res.json({ success: true, count: users.length, data: users });\n});\n\n// GET one user by ID — 200 OK or 404 Not Found\nrouter.get('/:id', (req, res) => {\n    const user = users.find(u => u.id === +req.params.id);\n    if (!user)\n        return res.status(404).json({ success: false, error: 'User not found' });\n    res.json({ success: true, data: user });\n});\n\n// POST create user — 201 Created or 400 Bad Request\nrouter.post('/', (req, res) => {\n    const { name, email } = req.body;\n    if (!name || !email)\n        return res.status(400).json({ error: 'name and email are required' });\n    const newUser = { id: Date.now(), name, email, role: 'user' };\n    users.push(newUser);\n    res.status(201).json({ success: true, data: newUser });\n});\n\n// DELETE — 200 OK or 404\nrouter.delete('/:id', (req, res) => {\n    const before = users.length;\n    users = users.filter(u => u.id !== +req.params.id);\n    if (users.length === before)\n        return res.status(404).json({ error: 'User not found' });\n    res.json({ success: true, message: 'User deleted' });\n});\n\nmodule.exports = router;\n// In app.js: app.use('/api/users', require('./routes/users'));",
       "quiz":[
         {"q":"Which HTTP method should be used to CREATE a new resource?","opts":["GET","PUT","POST","PATCH"],"ans":2},
         {"q":"HTTP status code 404 indicates...","opts":["Internal server error","Authentication required","The requested resource was not found","Bad request syntax"],"ans":2},
         {"q":"HTTP status code 201 means...","opts":["Request successful (OK)","Resource created successfully","No content to return","Redirect to another URL"],"ans":1},
         {"q":"express.Router() in Express is used to...","opts":["Create a new Express application","Organize related routes into separate module files","Handle all error responses","Automatically parse request data"],"ans":1},
         {"q":"CORS headers in an API are required when...","opts":["Using the HTTPS protocol","A browser makes requests from a different origin (domain/port)","Sending POST requests","Authenticating users with JWT"],"ans":1}
       ]}
    ]
  },
  "MySQL": {
    "icon":"🗄️","color":"#00758f","level":"Intermediate",
    "desc":"Most popular open-source relational database — master SQL fundamentals.",
    "topics":[
      {"id":"sql_crud","title":"CRUD Operations",
       "desc":"CRUD represents the four fundamental database operations: Create (INSERT), Read (SELECT), Update (UPDATE), Delete (DELETE). SELECT retrieves data with optional WHERE filtering, ORDER BY sorting, and LIMIT/OFFSET for pagination. Always use a WHERE clause with UPDATE and DELETE — without it, every single row in the table is affected. This is one of the most common and costly SQL mistakes.",
       "code":"-- CREATE: INSERT new rows\nINSERT INTO students (name, email, age, city)\nVALUES ('Alice', 'alice@example.com', 22, 'Hyderabad');\n\n-- INSERT multiple rows at once (efficient)\nINSERT INTO students (name, age) VALUES\n    ('Bob', 20), ('Carol', 23), ('Dave', 21);\n\n-- READ: SELECT data\nSELECT * FROM students;                   -- all columns, all rows\nSELECT name, email FROM students;          -- specific columns\nSELECT * FROM students WHERE age >= 21;   -- filtered rows\n\n-- With sorting and pagination\nSELECT * FROM students\n    WHERE city = 'Hyderabad'\n    ORDER BY name ASC\n    LIMIT 10 OFFSET 20;  -- page 3 (rows 21-30)\n\n-- UPDATE: always use WHERE!  ⚠️\nUPDATE students\nSET email = 'newemail@example.com', age = 23\nWHERE id = 1;  -- without WHERE → updates EVERY row!\n\n-- DELETE: always use WHERE!  ⚠️\nDELETE FROM students WHERE id = 5;\n-- DELETE FROM students; ← this deletes ALL rows!",
       "quiz":[
         {"q":"Which SQL statement adds new rows to a table?","opts":["ADD INTO","INSERT INTO","CREATE ROW","PUT INTO"],"ans":1},
         {"q":"Running UPDATE without a WHERE clause does what?","opts":["Updates no rows (safe)","Updates only the first row","Updates ALL rows in the table","Returns an error"],"ans":2},
         {"q":"LIMIT 10 OFFSET 20 in a SELECT query returns...","opts":["The first 10 rows","Rows 21 through 30 (skips first 20)","The last 10 rows","10 random rows"],"ans":1},
         {"q":"Which SQL clause is used to filter rows in a SELECT query?","opts":["HAVING","ORDER BY","WHERE","FILTER"],"ans":2},
         {"q":"ORDER BY name DESC sorts results...","opts":["Alphabetically A to Z","Alphabetically Z to A (reverse)","By primary key ID","In random order"],"ans":1}
       ]},
      {"id":"sql_tables","title":"Tables & Constraints",
       "desc":"Database tables have columns with specific data types: INT (whole numbers), BIGINT (large integers), VARCHAR(n) (variable text up to n chars), TEXT (unlimited text), DATE, DATETIME, DECIMAL(m,d) (precise decimals), BOOLEAN, ENUM (predefined values). Constraints enforce data integrity: PRIMARY KEY, AUTO_INCREMENT, NOT NULL, UNIQUE, DEFAULT, FOREIGN KEY (links between tables), CHECK.",
       "code":"-- Create database and select it\nCREATE DATABASE studyapp CHARACTER SET utf8mb4;\nUSE studyapp;\n\n-- Users table with various constraints\nCREATE TABLE users (\n    id         INT AUTO_INCREMENT PRIMARY KEY,  -- auto unique ID\n    username   VARCHAR(50)  UNIQUE NOT NULL,     -- must be unique\n    email      VARCHAR(150) UNIQUE NOT NULL,\n    password   VARCHAR(255) NOT NULL,\n    role       ENUM('student','teacher','admin') DEFAULT 'student',\n    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,\n    is_active  BOOLEAN DEFAULT TRUE,\n    score      DECIMAL(5,2) CHECK (score >= 0 AND score <= 100)\n);\n\n-- Courses table with FOREIGN KEY\nCREATE TABLE courses (\n    id         INT AUTO_INCREMENT PRIMARY KEY,\n    title      VARCHAR(200) NOT NULL,\n    teacher_id INT NOT NULL,\n    FOREIGN KEY (teacher_id)\n        REFERENCES users(id)\n        ON DELETE CASCADE  -- delete courses when teacher deleted\n        ON UPDATE CASCADE\n);\n\n-- Modify existing table\nALTER TABLE users ADD COLUMN phone VARCHAR(15) AFTER email;\nALTER TABLE users MODIFY COLUMN username VARCHAR(100);\nALTER TABLE users DROP COLUMN phone;\n\n-- Performance index\nCREATE INDEX idx_email ON users(email);",
       "quiz":[
         {"q":"AUTO_INCREMENT in MySQL automatically...","opts":["Duplicates the last inserted ID","Generates a unique incrementing integer for each new row","Sets a column to its default value","Creates a secondary index"],"ans":1},
         {"q":"A FOREIGN KEY constraint enforces...","opts":["Column uniqueness","Referential integrity between related tables","Non-null values","Auto-incrementing IDs"],"ans":1},
         {"q":"ON DELETE CASCADE on a foreign key means when the parent row is deleted...","opts":["The deletion is prevented","The user is asked to confirm","Child rows referencing it are automatically deleted","Child rows are set to NULL"],"ans":2},
         {"q":"ENUM('student','teacher','admin') means the column...","opts":["Accepts any string value","Only accepts one of the explicitly listed values","Stores integer codes for each option","Cannot be set to NULL"],"ans":1},
         {"q":"Adding a CREATE INDEX on a frequently searched column...","opts":["Adds a data integrity constraint","Speeds up SELECT queries filtering or sorting by that column","Automatically sorts the table","Removes duplicate values"],"ans":1}
       ]},
      {"id":"sql_joins","title":"JOINs & Relationships",
       "desc":"JOINs combine rows from two or more tables based on a related column. INNER JOIN returns only rows where there's a match in BOTH tables. LEFT JOIN returns all rows from the left table plus matching rows from the right (NULL when no match exists on the right). RIGHT JOIN is the reverse. Self JOIN joins a table with itself — useful for hierarchical data like employee-manager relationships.",
       "code":"-- Sample schema: users, courses, enrollments(user_id, course_id, score)\n\n-- INNER JOIN: only students who are enrolled\nSELECT u.name, c.title, e.score\nFROM users u\nINNER JOIN enrollments e ON u.id = e.user_id\nINNER JOIN courses c     ON c.id = e.course_id\nWHERE e.score >= 70\nORDER BY e.score DESC;\n\n-- LEFT JOIN: ALL users, with enrollment info if exists\nSELECT u.name, c.title, e.score\nFROM users u\nLEFT JOIN enrollments e ON u.id = e.user_id\nLEFT JOIN courses c     ON c.id = e.course_id;\n-- Users not enrolled will have NULL for c.title and e.score\n\n-- Find users NOT enrolled in ANY course\nSELECT u.name, u.email\nFROM users u\nLEFT JOIN enrollments e ON u.id = e.user_id\nWHERE e.user_id IS NULL;  -- NULL means no matching enrollment\n\n-- Self JOIN: employees and their managers\nSELECT e.name   AS employee,\n       m.name   AS manager,\n       m.email  AS manager_email\nFROM employees e\nLEFT JOIN employees m ON e.manager_id = m.id\nORDER BY manager;",
       "quiz":[
         {"q":"INNER JOIN returns rows where...","opts":["All left table rows appear","All right table rows appear","There is a matching row in BOTH tables","All rows from both tables appear"],"ans":2},
         {"q":"In a LEFT JOIN, NULL values appear in the result for...","opts":["Left table rows with no match on the right","Right table rows that have no matching left row","All primary key columns","The joining column itself"],"ans":1},
         {"q":"To find customers who have NEVER placed any order...","opts":["Use INNER JOIN and filter","Use LEFT JOIN then WHERE order.id IS NULL","Use RIGHT JOIN","Use CROSS JOIN"],"ans":1},
         {"q":"A Self JOIN is used when you need to...","opts":["Join two different tables","Join a table with itself (e.g., employee-manager hierarchy)","Join three or more tables","Join tables from different databases"],"ans":1},
         {"q":"Table aliases in SQL JOIN queries (like 'u' for users) are used to...","opts":["Create permanent table copies","Make queries shorter and more readable","Rename the table in the database","Define the join type"],"ans":3}
       ]},
      {"id":"sql_aggregate","title":"Aggregates & GROUP BY",
       "desc":"Aggregate functions compute a single result from multiple rows of data: COUNT(*) counts all rows, SUM() totals a numeric column, AVG() calculates the mean, MAX() finds the largest, MIN() finds the smallest. GROUP BY groups rows with the same value before applying aggregation. HAVING filters groups after aggregation (like WHERE for groups). Execution order: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT.",
       "code":"-- Simple aggregates on entire table\nSELECT\n    COUNT(*) AS total_students,\n    AVG(score) AS average_score,\n    MAX(score) AS highest_score,\n    MIN(score) AS lowest_score,\n    SUM(score) AS total_points\nFROM enrollments;\n\n-- GROUP BY: aggregate statistics per course\nSELECT\n    c.title,\n    COUNT(e.user_id) AS enrolled_students,\n    AVG(e.score)     AS avg_score,\n    MAX(e.score)     AS top_score,\n    MIN(e.score)     AS lowest_score\nFROM courses c\nJOIN enrollments e ON c.id = e.course_id\nGROUP BY c.id, c.title\nORDER BY avg_score DESC;\n\n-- HAVING: filter groups (like WHERE but after aggregation)\nSELECT c.title, COUNT(e.user_id) AS student_count\nFROM courses c\nJOIN enrollments e ON c.id = e.course_id\nGROUP BY c.id\nHAVING COUNT(e.user_id) > 10  -- only popular courses\nORDER BY student_count DESC;\n\n-- WHERE (filter rows) + GROUP BY + HAVING (filter groups)\nSELECT city, COUNT(*) AS total\nFROM users\nWHERE is_active = TRUE   -- filter individual rows first\nGROUP BY city\nHAVING COUNT(*) > 5      -- then filter the groups\nORDER BY total DESC;",
       "quiz":[
         {"q":"COUNT(*) counts...","opts":["Only non-NULL values","All rows in the group including NULLs","Only distinct values","Column names in the table"],"ans":1},
         {"q":"The HAVING clause in SQL filters...","opts":["Individual rows before grouping","Groups of rows after GROUP BY is applied","NULL values from results","ORDER BY results"],"ans":1},
         {"q":"The key difference: WHERE filters ___ while HAVING filters ___","opts":["Groups / Rows","Rows before aggregation / Groups after aggregation","NULL values / Non-null values","Same thing / Same thing"],"ans":1},
         {"q":"GROUP BY city with COUNT(*) returns...","opts":["One grand total count","One row per distinct city with its row count","All rows unchanged","City names only"],"ans":1},
         {"q":"AVG(score) used with GROUP BY course_id gives...","opts":["One overall average across all courses","The average score separately for each course group","The maximum score per course","The total of all scores"],"ans":1}
       ]},
      {"id":"sql_advanced","title":"Advanced SQL",
       "desc":"Subqueries are SELECT statements nested inside other SQL statements — used in WHERE, FROM, or SELECT clauses. LIKE enables pattern matching with % (any number of characters) and _ (exactly one character). DISTINCT removes duplicate rows from results. UNION combines results from two SELECT queries (removes duplicates by default; use UNION ALL to keep them). Views are named saved queries. Transactions with COMMIT/ROLLBACK ensure ACID properties.",
       "code":"-- Subquery: find students who scored above 90 in any course\nSELECT name, email FROM users\nWHERE id IN (\n    SELECT DISTINCT user_id\n    FROM enrollments\n    WHERE score > 90\n);\n\n-- LIKE pattern matching\nSELECT * FROM users WHERE name LIKE 'A%';       -- starts with A\nSELECT * FROM users WHERE email LIKE '%@gmail.com'; -- ends with @gmail.com\nSELECT * FROM users WHERE name LIKE 'Jo_n';    -- Jo_n matches John, Joan\n\n-- DISTINCT: remove duplicate rows\nSELECT DISTINCT city FROM users ORDER BY city;\n\n-- UNION: combine two SELECT result sets (removes duplicates)\nSELECT name, 'Student' AS type FROM students\nUNION\nSELECT name, 'Teacher' AS type FROM teachers\nORDER BY name;\n\n-- VIEW: a saved reusable query\nCREATE VIEW honor_students AS\nSELECT u.name, AVG(e.score) AS gpa\nFROM users u JOIN enrollments e ON u.id = e.user_id\nGROUP BY u.id HAVING AVG(e.score) >= 85;\n\nSELECT * FROM honor_students ORDER BY gpa DESC;\n\n-- TRANSACTION: all-or-nothing bank transfer\nSTART TRANSACTION;\n    UPDATE accounts SET balance = balance - 500 WHERE id = 1;\n    UPDATE accounts SET balance = balance + 500 WHERE id = 2;\nCOMMIT;  -- make permanent; or use ROLLBACK to undo all",
       "quiz":[
         {"q":"LIKE 'A%' matches strings that...","opts":["Contain the letter A anywhere","End with the letter A","Start with the letter A","Are exactly one character: A"],"ans":2},
         {"q":"SELECT DISTINCT city FROM users...","opts":["Counts unique cities","Returns one row per unique city value (no duplicates)","Selects unique table columns","Speeds up the query"],"ans":1},
         {"q":"A SQL VIEW is...","opts":["A physical copy of table data","A saved SELECT query treated as a virtual table","A stored procedure","A database index"],"ans":1},
         {"q":"ROLLBACK inside a transaction...","opts":["Permanently saves all changes","Undoes ALL changes made since START TRANSACTION","Deletes the entire table","Commits only partial changes"],"ans":1},
         {"q":"UNION vs UNION ALL — the difference is...","opts":["UNION is faster","UNION removes duplicate rows; UNION ALL keeps all rows including duplicates","They are identical","UNION ALL requires same column names"],"ans":1}
       ]}
    ]
  }
}

# ── Auth helpers ──────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({"error": "Login required"}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

def current_user():
    db = load_db()
    return db['users'].get(session.get('user_id'))

# ══════════════════════════════════════════════════════
#  PAGE ROUTES
# ══════════════════════════════════════════════════════
@app.route('/')
def root():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login_page'))

@app.route('/login')
def login_page():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user())

@app.route('/learn')
@login_required
def learn_page():
    return render_template('learn.html', user=current_user())

@app.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html', user=current_user())

@app.route('/certificate/<cert_id>')
@login_required
def certificate_view(cert_id):
    return render_template('certificate.html', cert_id=cert_id)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ══════════════════════════════════════════════════════
#  AUTH API
# ══════════════════════════════════════════════════════
@app.route('/api/signup', methods=['POST'])
def api_signup():
    d    = request.get_json() or {}
    name = d.get('name','').strip()
    email= d.get('email','').strip().lower()
    pw   = d.get('password','')
    if not name or not email or not pw:
        return jsonify({"error":"All fields are required"}), 400
    if len(pw) < 6:
        return jsonify({"error":"Password must be at least 6 characters"}), 400
    if '@' not in email:
        return jsonify({"error":"Invalid email address"}), 400
    db = load_db()
    if any(u['email']==email for u in db['users'].values()):
        return jsonify({"error":"Email already registered"}), 409
    uid = str(uuid.uuid4())
    db['users'][uid] = {
        "id":uid,"name":name,"email":email,"password":hash_pw(pw),
        "joined":datetime.now().strftime('%d %b %Y'),"avatar":name[0].upper()
    }
    save_db(db)
    session['user_id'] = uid
    return jsonify({"success":True,"redirect":"/dashboard"})

@app.route('/api/login', methods=['POST'])
def api_login():
    d     = request.get_json() or {}
    email = d.get('email','').strip().lower()
    pw    = d.get('password','')
    if not email or not pw:
        return jsonify({"error":"Email and password are required"}), 400
    db = load_db()
    for uid, u in db['users'].items():
        if u['email']==email and u['password']==hash_pw(pw):
            session['user_id'] = uid
            return jsonify({"success":True,"redirect":"/dashboard"})
    return jsonify({"error":"Invalid email or password"}), 401

# ══════════════════════════════════════════════════════
#  CURRICULUM API
# ══════════════════════════════════════════════════════
@app.route('/api/languages')
@login_required
def api_languages():
    db  = load_db(); uid = session['user_id']
    passed = {r['language'] for r in db.get('results',{}).get(uid,[]) if r.get('passed')}
    return jsonify([{
        "name":n,"icon":v["icon"],"color":v["color"],"level":v["level"],
        "desc":v["desc"],"topic_count":len(v["topics"]),"completed":n in passed
    } for n,v in CURRICULUM.items()])

@app.route('/api/topics/<lang>')
@login_required
def api_topics(lang):
    L = CURRICULUM.get(lang)
    if not L: return jsonify({"error":"Not found"}),404
    db=load_db(); uid=session['user_id']
    prog=db.get('progress',{}).get(uid,{}).get(lang,{})
    return jsonify({
        "language":lang,"icon":L["icon"],"color":L["color"],"desc":L["desc"],
        "topics":[{"id":t["id"],"title":t["title"],"done":prog.get(t["id"],False)} for t in L["topics"]]
    })

@app.route('/api/topic/<lang>/<tid>')
@login_required
def api_topic(lang, tid):
    L=CURRICULUM.get(lang)
    if not L: return jsonify({"error":"Not found"}),404
    for t in L["topics"]:
        if t["id"]==tid:
            return jsonify({"id":t["id"],"title":t["title"],"desc":t["desc"],"code":t["code"]})
    return jsonify({"error":"Topic not found"}),404

@app.route('/api/topic/complete', methods=['POST'])
@login_required
def api_complete():
    d=request.get_json() or {}
    lang,tid=d.get('language'),d.get('topic_id')
    db=load_db(); uid=session['user_id']
    db.setdefault('progress',{}).setdefault(uid,{}).setdefault(lang,{})[tid]=True
    save_db(db)
    return jsonify({"success":True})

# ══════════════════════════════════════════════════════
#  AI API — Claude Integration
# ══════════════════════════════════════════════════════
@app.route('/api/ai/explain', methods=['POST'])
@login_required
def api_ai_explain():
    """AI explains why an answer is correct/wrong — looks up correct answer server-side."""
    d = request.get_json() or {}
    question   = d.get('question','')
    options    = d.get('options',[])
    chosen_idx = d.get('chosen_idx')
    language   = d.get('language','')
    topic      = d.get('topic','')
    qid        = d.get('qid','')
    token      = d.get('token','')

    # Look up correct answer from server-side session (never trust client)
    correct_idx = None
    sd = QUIZ_SESSIONS.get(token)
    if sd:
        for qa in sd['ans']:
            if qa['qid'] == qid:
                correct_idx = qa['correct']
                break

    # Fallback: if session expired, try to find from curriculum
    if correct_idx is None:
        for lang_data in CURRICULUM.values():
            for t in lang_data['topics']:
                for i, q in enumerate(t['quiz']):
                    if f"{t['id']}__q{i}" == qid:
                        correct_idx = q['ans']
                        break

    if correct_idx is None:
        return jsonify({"success": True, "was_correct": False, "correct_idx": 0,
                        "explanation": "Your answer has been recorded. Review this topic for a detailed explanation."})

    was_correct  = (chosen_idx == correct_idx)
    chosen_text  = options[chosen_idx] if chosen_idx is not None and chosen_idx < len(options) else 'No answer'
    correct_text = options[correct_idx] if correct_idx < len(options) else ''

    prompt = f"""You are an expert {language} programming tutor. A student just answered a quiz question.

Question: {question}
Options: {', '.join([f'{chr(65+i)}) {o}' for i,o in enumerate(options)])}
Correct answer: {chr(65+correct_idx)}) {correct_text}
Student chose: {chr(65+chosen_idx) if chosen_idx is not None else '?'}) {chosen_text}
Student was: {'✅ CORRECT!' if was_correct else '❌ INCORRECT'}
Topic: {topic} in {language}

{'Congratulate them warmly and reinforce WHY this answer is correct with a clear, memorable explanation.' if was_correct else f'Gently explain why their answer was wrong and clearly teach why "{correct_text}" is the correct answer.'}

Keep your response:
- Friendly and encouraging (never harsh)
- Concise (2-4 sentences maximum)
- Include ONE practical real-world example if helpful
- End with an encouraging note

Do NOT use markdown formatting. Write in plain conversational text."""

    try:
        import urllib.request
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 300,
            "messages": [{"role":"user","content": prompt}]
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type":"application/json",
                "anthropic-version":"2023-06-01"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            explanation = result["content"][0]["text"]
            return jsonify({"success":True,"explanation":explanation,"was_correct":was_correct,"correct_idx":correct_idx})
    except Exception as e:
        if was_correct:
            fallback = f"Correct! '{correct_text}' is the right answer for this {topic} concept in {language}. Keep up the great work!"
        else:
            fallback = f"The correct answer is '{correct_text}'. Review the {topic} section to understand this concept better. You've got this!"
        return jsonify({"success":True,"explanation":fallback,"was_correct":was_correct,"correct_idx":correct_idx,"fallback":True})

@app.route('/api/ai/hint', methods=['POST'])
@login_required
def api_ai_hint():
    """AI gives a hint without revealing the answer."""
    d = request.get_json() or {}
    question = d.get('question','')
    options  = d.get('options',[])
    topic    = d.get('topic','')
    language = d.get('language','')

    prompt = f"""You are a helpful {language} tutor. A student needs a hint for this quiz question.

Question: {question}
Options: {', '.join([f'{chr(65+i)}) {o}' for i,o in enumerate(options)])}
Topic: {topic}

Give a helpful hint that:
- Points them in the right direction WITHOUT revealing the answer
- Reminds them of the key concept from {topic}
- Is 1-2 sentences maximum
- Is encouraging in tone

Do NOT say which option is correct. Do NOT use markdown."""

    try:
        import urllib.request
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 150,
            "messages": [{"role":"user","content": prompt}]
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"Content-Type":"application/json","anthropic-version":"2023-06-01"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            hint = result["content"][0]["text"]
            return jsonify({"success":True,"hint":hint})
    except:
        return jsonify({"success":True,"hint":f"Think about what you learned in the '{topic}' section. Focus on the key definition and how it's used in practice."})

@app.route('/api/ai/encouragement', methods=['POST'])
@login_required
def api_ai_encouragement():
    """AI gives personalized end-of-quiz encouragement."""
    d = request.get_json() or {}
    name     = d.get('name','')
    language = d.get('language','')
    overall  = d.get('overall',0)
    passed   = d.get('passed',False)
    weak     = d.get('weak_topics',[])

    prompt = f"""You are an enthusiastic coding mentor. Give personalized feedback to {name} who just completed a {language} quiz.

Score: {overall}%
Result: {'PASSED the course (85%+ overall)!' if passed else f'Did not pass yet (Overall 85%+ required). Weak topics: {", ".join(weak)}'}

Write a personalized 2-3 sentence message:
- If passed: Celebrate their achievement! Mention {language} specifically. Encourage them to try the next language.
- If not passed: Be supportive and encouraging. Say specific weak topics need review. Tell them they're very close and can do it!

Be warm, personal, and motivating. Do NOT use markdown. Address them by name."""

    try:
        import urllib.request
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 200,
            "messages": [{"role":"user","content": prompt}]
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"Content-Type":"application/json","anthropic-version":"2023-06-01"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            msg = result["content"][0]["text"]
            return jsonify({"success":True,"message":msg})
    except:
        if passed:
            msg = f"Congratulations {name}! You've mastered {language} with a score of {overall}%! Your dedication is paying off — keep going and tackle the next language!"
        else:
            msg = f"Great effort {name}! You scored {overall}% on {language}. Review {', '.join(weak[:2]) if weak else 'the weak topics'} and you'll pass on your next attempt. You're so close!"
        return jsonify({"success":True,"message":msg})

# ══════════════════════════════════════════════════════
#  QUIZ API
# ══════════════════════════════════════════════════════
@app.route('/api/quiz/start', methods=['POST'])
@login_required
def api_quiz_start():
    b=request.get_json() or {}
    lang,tids=b.get('language'),b.get('topic_ids',[])
    L=CURRICULUM.get(lang)
    if not L: return jsonify({"error":"Not found"}),404
    client,server=[],[]
    for t in L["topics"]:
        if tids and t["id"] not in tids: continue
        for i,q in enumerate(t["quiz"]):
            qid=f"{t['id']}__q{i}"
            client.append({"qid":qid,"topic_id":t["id"],"topic_title":t["title"],"question":q["q"],"options":q["opts"]})
            server.append({"qid":qid,"topic_id":t["id"],"topic_title":t["title"],"correct":q["ans"]})
    pairs=list(zip(client,server)); random.shuffle(pairs)
    if pairs: client,server=map(list,zip(*pairs))
    token=str(uuid.uuid4())
    QUIZ_SESSIONS[token]={"ans":server,"language":lang}
    return jsonify({"token":token,"questions":client})

@app.route('/api/quiz/submit', methods=['POST'])
@login_required
def api_quiz_submit():
    b=request.get_json() or {}
    token,answers=b.get('token'),b.get('answers',{})
    sd=QUIZ_SESSIONS.get(token)
    if not sd: return jsonify({"error":"Invalid session"}),400
    stats={}
    for qa in sd["ans"]:
        tid=qa["topic_id"]
        if tid not in stats: stats[tid]={"title":qa["topic_title"],"correct":0,"total":0}
        stats[tid]["total"]+=1
        user_ans=answers.get(qa["qid"])
        if user_ans is not None and int(user_ans)==int(qa["correct"]):
            stats[tid]["correct"]+=1
    results,weak=[],[]
    for tid,s in stats.items():
        pct=round(s["correct"]/s["total"]*100) if s["total"] else 0
        passed=pct>=PASS_THRESHOLD
        results.append({"topic_id":tid,"topic_title":s["title"],"correct":s["correct"],"total":s["total"],"percentage":pct,"passed":passed})
        if not passed: weak.append(tid)
    overall=round(sum(r["percentage"] for r in results)/len(results)) if results else 0
    passed_overall = overall >= PASS_THRESHOLD
    lang=sd["language"]
    
    # Save result & certificate if passed
    db=load_db(); uid=session['user_id']
    result_entry = {
        "language":lang,"overall":overall,"passed":passed_overall,
        "results":results,"date":datetime.now().strftime('%d %b %Y, %H:%M'),
        "weak_topics":weak
    }
    db.setdefault('results',{}).setdefault(uid,[]).append(result_entry)
    
    # Mark weak topics as incomplete in progress to force re-study IF overall failed
    if not passed_overall and weak:
        lang_prog = db.setdefault('progress', {}).setdefault(uid, {}).setdefault(lang, {})
        for tid in weak:
            lang_prog[tid] = False
    
    # Generate/Retrieve certificate if passed overall
    cert_id = None
    if passed_overall:
        existing_certs = db.setdefault('certificates', {}).setdefault(uid, [])
        # Find index of existing certificate for this language
        cert_idx = next((i for i, c in enumerate(existing_certs) if c['language'] == lang), None)
        
        # Determine current best score to display on certificate
        best_score = overall
        if cert_idx is not None:
            best_score = max(existing_certs[cert_idx].get('score', 0), overall)
            cert_id = existing_certs[cert_idx]['id']
        else:
            cert_id = str(uuid.uuid4())[:8].upper()
            
        # Use user joined date as start_date
        user = db['users'].get(uid, {})
        start_date = user.get('joined', datetime.now().strftime('%d %b %Y'))
        
        # Calculate performance rating
        if best_score >= 95: performance = "Outstanding"
        elif best_score >= 90: performance = "Excellent"
        else: performance = "Great"

        new_cert_data = {
            "id": cert_id,
            "language": lang,
            "score": best_score,
            "performance": performance,
            "start_date": start_date,
            "date": datetime.now().strftime('%d %b %Y'),
            "issued": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=3*365 + 1)).strftime('%d %b %Y')
        }
        
        if cert_idx is not None:
            existing_certs[cert_idx] = new_cert_data
        else:
            existing_certs.append(new_cert_data)
        
        # Pass cert_id to the response
    else:
        # Check if user ALREADY has a certificate for this language (maybe from a previous attempt)
        # We need this to return cert_id to the UI even if they didn't pass this specific time
        # (Though UI usually only shows results page on fail)
        existing_certs = db.get('certificates', {}).get(uid, [])
        cert_data = next((c for c in existing_certs if c['language'] == lang), None)
        cert_id = cert_data['id'] if cert_data else None
    
    save_db(db)
    del QUIZ_SESSIONS[token]
    return jsonify({
        "results":results,"weak_topics":weak,"overall_percentage":overall,
        "passed":passed_overall,"threshold":PASS_THRESHOLD,"cert_id":cert_id
    })

# ══════════════════════════════════════════════════════
#  PROFILE API
# ══════════════════════════════════════════════════════
@app.route('/api/profile')
@login_required
def api_profile():
    db=load_db(); uid=session['user_id']
    u=db['users'].get(uid,{})
    results =db.get('results',{}).get(uid,[])
    progress=db.get('progress',{}).get(uid,{})
    certs   =db.get('certificates',{}).get(uid,[])
    # Best score per language
    best_scores={}
    for r in results:
        lang=r['language']
        if lang not in best_scores or r['overall']>best_scores[lang]:
            best_scores[lang]=r['overall']
    completed_langs=[r['language'] for r in results if r.get('passed')]
    # Remove duplicates
    seen=set(); unique_completed=[]
    for l in completed_langs:
        if l not in seen: unique_completed.append(l); seen.add(l)
    total_topics=sum(len(v) for v in progress.values())
    return jsonify({
        "name":u.get('name'),"email":u.get('email'),
        "avatar":u.get('avatar'),"joined":u.get('joined'),
        "bio":u.get('bio',''),"education":u.get('education',''),
        "phone":u.get('phone',''),"photo":u.get('photo',''),
        "completed_langs":unique_completed,
        "total_topics":total_topics,
        "quiz_attempts":len(results),
        "best_scores":best_scores,
        "certificates":certs,
        "all_results":results[-10:][::-1]
    })

@app.route("/api/profile/update", methods=["POST"])
@login_required
def api_profile_update():
    db=load_db(); uid=session["user_id"]
    data=request.get_json(force=True)
    u=db["users"].get(uid,{})
    if data.get("name"):
        u["name"]=data["name"].strip()
        u["avatar"]=data["name"].strip()[0].upper()
    if "bio" in data: u["bio"]=data["bio"]
    if "education" in data: u["education"]=data["education"]
    if "phone" in data: u["phone"]=data["phone"]
    if "photo" in data and data["photo"]: u["photo"]=data["photo"]
    db["users"][uid]=u
    save_db(db)
    return jsonify({"success":True})

@app.route("/api/certificate/<cert_id>")
@login_required
def api_certificate(cert_id):
    db = load_db()
    uid = session['user_id']
    certs = db.get('certificates', {}).get(uid, [])
    cert = next((c for c in certs if c['id'] == cert_id), None)
    if not cert:
        return jsonify({"error": "Certificate not found"}), 404
    user = db['users'].get(uid, {})
    return jsonify({
        **cert,
        "holder_name": user.get('name', ''),
        "site_name": "AI Study Buddy"
    })

if __name__=='__main__':
    app.run(debug=True,port=5000)