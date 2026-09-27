# Evaluation set — for review

27 questions, 73 labels. Every `(page, section)` pair is
verified to be a real heading in the cleaned corpus.

**How to review:** for each question ask (a) would a Flask user actually ask this, and (b) is any
page missing from *Relevant*? A missing label counts as a false miss later and makes every variant
look worse than it is. Mark anything to reword, drop, or relabel.

`Primary` is the one section a reader most wants (used for a stricter P@1). `Relevant` are all
sections that genuinely answer it — the Flask docs cover much of this twice (tutorial vs reference).

## conceptual (4)

**1. What is the application context in Flask?**  `easy`
- Primary: `appcontext` > The Application Context
- Also: `appcontext` > Purpose of the Context, `appcontext` > Lifetime of the Context

**3. Why does Flask use thread locals and what are the downsides?**  `medium`
- Primary: `design` > Thread Locals

**4. What does the 'micro' in microframework actually mean?**  `easy`
- Primary: `design` > What does "micro" mean?

**27. What is the instance folder and what should I keep in it?**  `medium`
- Primary: `config` > Instance Folders
- Also: `tutorial/factory` > The Application Factory

## identifier (8)

**6. What does url_for do and how do I build URLs with it?**  `medium`
- Primary: `quickstart` > URL Building
- Also: `blueprints` > Building URLs
- Note: url_for appears in 39 sections; only these two explain it

**7. How do I register a custom Jinja filter with template_filter?**  `easy`
- Primary: `templating` > Registering Filters
- Note: template_filter occurs in exactly one section - a clean single-label case

**8. What is secure_filename for when handling uploads?**  `easy`
- Primary: `patterns/fileuploads` > A Gentle Introduction
- Also: `quickstart` > File Uploads

**9. How do I use teardown_appcontext to close a database connection?**  `hard`
- Primary: `tutorial/database` > Register with the Application
- Also: `appcontext` > Storing Data, `patterns/sqlite3` > Using SQLite 3 with Flask, `patterns/sqlite3` > Connect on Demand
- Note: scattered across 10 sections; these are the ones that actually show the pattern

**10. What is ProxyFix and when do I need it?**  `easy`
- Primary: `deploying/proxy_fix` > Tell Flask it is Behind a Proxy
- Also: `quickstart` > Hooking in WSGI Middleware

**11. How do I use MethodView to build a class-based view?**  `medium`
- Primary: `views` > Method Dispatching and APIs
- Also: `views` > Class-based Views, `views` > Basic Reusable View

**12. What does stream_with_context do?**  `easy`
- Primary: `patterns/streaming` > Streaming with Context

**13. What is the g object used for?**  `medium`
- Primary: `appcontext` > Storing Data
- Also: `api` > Application Globals, `quickstart` > Context Locals

## howto (11)

**14. How do I register a blueprint on an application?**  `medium`
- Primary: `blueprints` > Registering Blueprints
- Also: `blueprints` > My First Blueprint, `tutorial/views` > Create a Blueprint, `patterns/appfactories` > Basic Factories
- Note: currently ranks tutorial/views above the reference - the re-ranking target

**15. How do I handle a file upload from a form?**  `easy`
- Primary: `patterns/fileuploads` > A Gentle Introduction
- Also: `patterns/fileuploads` > Uploading Files, `patterns/fileuploads` > Improving Uploads, `quickstart` > File Uploads

**16. How do I add my own command to the flask CLI?**  `medium`
- Primary: `cli` > Custom Commands
- Also: `cli` > Registering Commands with Blueprints

**17. How do I show a custom 404 error page?**  `medium`
- Primary: `errorhandling` > Custom Error Pages
- Also: `errorhandling` > Error Handlers, `errorhandling` > Registering, `quickstart` > Redirects and Errors

**18. How do I set the secret key so sessions work?**  `hard`
- Primary: `quickstart` > Sessions
- Also: `tutorial/deploy` > Configure the Secret Key, `config` > Configuring from Environment Variables, `api` > Sessions
- Note: spread over 10 sections; config page discusses it without being the how-to

**19. How do I flash a message to the user after a redirect?**  `easy`
- Primary: `patterns/flashing` > Simple Flashing
- Also: `patterns/flashing` > Message Flashing, `quickstart` > Message Flashing

**20. How do I write tests using the Flask test client?**  `medium`
- Primary: `testing` > Sending Requests with the Test Client
- Also: `testing` > Fixtures, `tutorial/tests` > Setup and Fixtures

**21. How do I use an application factory instead of a global app?**  `medium`
- Primary: `patterns/appfactories` > Basic Factories
- Also: `patterns/appfactories` > Application Factories, `tutorial/factory` > The Application Factory

**22. How do I deploy a Flask app with Gunicorn?**  `easy`
- Primary: `deploying/gunicorn` > Running
- Also: `deploying/gunicorn` > Gunicorn, `deploying/gunicorn` > Installing, `deploying/gunicorn` > Binding Externally

**23. How do I make a URL parameter an integer instead of a string?**  `medium`
- Primary: `quickstart` > Variable Rules
- Also: `views` > URL Variables

**26. How do I turn off autoescaping for a block of a template?**  `medium`
- Primary: `templating` > Controlling Autoescaping
- Also: `templating` > Jinja Setup

## security (1)

**25. Does Flask protect against CSRF attacks by default?**  `easy`
- Primary: `web-security` > Cross-Site Request Forgery (CSRF)

## multihop (3)

**2. What is the difference between the application context and the request context?**  `hard`
- Primary: `appcontext` > The Application Context
- Also: `appcontext` > Purpose of the Context, `reqcontext` > The Request Context, `reqcontext` > Purpose of the Context
- Note: answer genuinely spans two pages; neither alone is complete

**5. Why can't I access the request object outside of a request?**  `hard`
- Primary: `reqcontext` > Purpose of the Context
- Also: `reqcontext` > The Request Context, `reqcontext` > Lifetime of the Context, `reqcontext` > Manually Push a Context, `reqcontext` > Notes On Proxies
- Note: phrased as an error symptom, not as the doc's own wording

**24. How do I run a long background task without blocking the request?**  `hard`
- Primary: `patterns/celery` > Background Tasks with Celery
- Also: `patterns/celery` > Defining Tasks, `async-await` > Background tasks
- Note: celery page is the real answer; async-await explicitly warns against await for this
