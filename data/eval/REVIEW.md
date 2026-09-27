# Evaluation set — for review

72 questions, 188 labels, covering 57 of 71 pages.
Every `(page, section)` pair is verified to be a real heading in the cleaned corpus.

**How to review:** for each question ask (a) would a Flask user actually ask this, and (b) is any
page missing from *Also*? A missing label counts as a false miss and makes every variant look
worse than it is.

Scoring never compares section names — a gold section is a character range on its page and a
retrieved chunk is a hit when it shares >=50 words with that range. See `src/raghood/evaluate.py`.

## conceptual (8)

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

**31. What happens step by step when a request comes in?**  `medium`
- Primary: `lifecycle` > How a Request is Handled
- Also: `lifecycle` > Serving the Application

**59. Which production server should I choose to deploy Flask?**  `medium`
- Primary: `deploying/index` > Self-Hosted Options
- Also: `deploying/index` > Deploying to Production, `deploying/index` > Hosting Platforms

**67. Why is request a proxy object and when does that matter?**  `hard`
- Primary: `reqcontext` > Notes On Proxies
- Also: `appcontext` > Storing Data
- Note: LocalProxy / _get_current_object

**68. Can I use async view functions in Flask and is it faster?**  `medium`
- Primary: `async-await` > Using `async` and `await`
- Also: `async-await` > Performance, `async-await` > When to use Quart instead

## identifier (10)

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

**42. How do I write a login_required decorator for my views?**  `medium`
- Primary: `patterns/viewdecorators` > Login Required Decorator
- Also: `patterns/viewdecorators` > View Decorators, `tutorial/views` > Require Authentication in Other Views

**45. How do I register a callback to run after this particular request?**  `hard`
- Primary: `patterns/deferredcallbacks` > Deferred Request Callbacks
- Note: after_this_request, but asked without naming it

## howto (46)

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

**28. How do I write my own Flask extension with an init_app method?**  `medium`
- Primary: `extensiondev` > The Extension Class and Initialization
- Also: `extensiondev` > Flask Extension Development, `extensiondev` > Adding Behavior

**29. What should I name my Flask extension package?**  `easy`
- Primary: `extensiondev` > Naming

**30. Where do I find Flask extensions and how do I install one?**  `easy`
- Primary: `extensions` > Finding Extensions
- Also: `extensions` > Extensions, `extensions` > Using Extensions, `quickstart` > Using Flask Extensions

**32. How do I add WSGI middleware to a Flask app?**  `medium`
- Primary: `lifecycle` > Middleware
- Also: `quickstart` > Hooking in WSGI Middleware

**33. How do I organise a large application as a Python package?**  `medium`
- Primary: `patterns/packages` > Simple Packages
- Also: `patterns/packages` > Large Applications as Packages, `patterns/packages` > Working with Blueprints

**34. How do I serve two separate Flask applications on different subdomains?**  `medium`
- Primary: `patterns/appdispatch` > Dispatch by Subdomain
- Also: `patterns/appdispatch` > Combining Applications, `patterns/appdispatch` > Dispatch by Path

**35. How can I avoid importing every view module at startup?**  `hard`
- Primary: `patterns/lazyloading` > Converting to Centralized URL Map
- Also: `patterns/lazyloading` > Lazily Loading Views, `patterns/lazyloading` > Loading Late
- Note: phrased as the motivation, never using the word 'lazy'

**36. How do I make a base template that child templates extend?**  `medium`
- Primary: `patterns/templateinheritance` > Base Template
- Also: `patterns/templateinheritance` > Template Inheritance, `patterns/templateinheritance` > Child Template, `tutorial/templates` > The Base Layout

**37. How do I return JSON from a view function?**  `hard`
- Primary: `patterns/javascript` > Return JSON from Views
- Also: `quickstart` > APIs with JSON, `quickstart` > About Responses
- Note: jsonify appears in 13 sections; errorhandling and views discuss it for other purposes

**38. How do I read JSON that was POSTed to a view?**  `medium`
- Primary: `patterns/javascript` > Receiving JSON in Views

**39. How do I call a Flask endpoint from JavaScript with fetch?**  `medium`
- Primary: `patterns/javascript` > Making a Request with `fetch`
- Also: `patterns/javascript` > JavaScript, `fetch`, and JSON, `patterns/javascript` > Generating URLs

**40. How do I add a context processor so a variable is available in all templates?**  `easy`
- Primary: `templating` > Context Processors
- Also: `templating` > Standard Context

**41. How do I validate a form with WTForms?**  `easy`
- Primary: `patterns/wtforms` > In the View
- Also: `patterns/wtforms` > Form Validation with WTForms, `patterns/wtforms` > The Forms, `patterns/wtforms` > Forms in Templates

**43. How do I subscribe to a Flask signal?**  `medium`
- Primary: `signals` > Subscribing to Signals
- Also: `signals` > Decorator Based Signal Subscriptions, `signals` > Core Signals

**44. How do I create and send my own custom signal?**  `medium`
- Primary: `signals` > Creating Signals
- Also: `signals` > Sending Signals

**46. How do I strip a language code prefix from every URL automatically?**  `hard`
- Primary: `patterns/urlprocessors` > Internationalized Application URLs
- Also: `patterns/urlprocessors` > Using URL Processors, `patterns/urlprocessors` > Internationalized Blueprint URLs
- Note: url_value_preprocessor / url_defaults, described by effect

**47. How do I support PUT and DELETE from a client that only sends POST?**  `hard`
- Primary: `patterns/methodoverrides` > Adding HTTP Method Overrides

**48. How do I verify a request body checksum?**  `easy`
- Primary: `patterns/requestchecksum` > Request Content Checksums

**49. How do I use SQLAlchemy with Flask?**  `medium`
- Primary: `patterns/sqlalchemy` > Flask-SQLAlchemy Extension
- Also: `patterns/sqlalchemy` > SQLAlchemy in Flask, `patterns/sqlalchemy` > Declarative

**50. How do I use MongoDB with Flask?**  `easy`
- Primary: `patterns/mongoengine` > MongoDB with MongoEngine
- Also: `patterns/mongoengine` > Configuration, `patterns/mongoengine` > Mapping Documents

**51. How do I email myself when the application raises an error?**  `easy`
- Primary: `logging` > Email Errors to Admins

**52. How do I configure logging for a Flask app?**  `medium`
- Primary: `logging` > Basic Configuration
- Also: `logging` > Logging, `logging` > Default Configuration, `logging` > Removing the Default Handler

**53. How do I include the request URL in my log messages?**  `medium`
- Primary: `logging` > Injecting Request Information

**54. How do I use a debugger like pdb or my IDE with Flask?**  `medium`
- Primary: `debugging` > External Debuggers
- Also: `debugging` > Debugging Application Errors, `debugging` > The Built-In Debugger

**55. I get 'Address already in use' when starting the server. What do I do?**  `easy`
- Primary: `server` > Address already in use

**56. How do I open a shell with an application context loaded?**  `medium`
- Primary: `shell` > Working with the Shell
- Also: `shell` > Command Line Interface, `shell` > Creating a Request Context, `cli` > Open a Shell

**57. Which Python version does Flask need and what does it install?**  `easy`
- Primary: `installation` > Python Version
- Also: `installation` > Dependencies, `installation` > Install Flask

**58. How do I create and activate a virtual environment for a Flask project?**  `easy`
- Primary: `installation` > Virtual environments
- Also: `installation` > Create an environment, `installation` > Activate the environment

**60. How do I deploy Flask with uWSGI?**  `easy`
- Primary: `deploying/uwsgi` > Running
- Also: `deploying/uwsgi` > uWSGI, `deploying/uwsgi` > Installing, `deploying/uwsgi` > Binding Externally

**61. How do I put nginx in front of my Flask application?**  `medium`
- Primary: `deploying/nginx` > Configuration
- Also: `deploying/nginx` > nginx, `deploying/nginx` > Domain Name

**62. How do I make my project pip-installable with a pyproject.toml?**  `medium`
- Primary: `tutorial/install` > Describe the Project
- Also: `tutorial/install` > Make the Project Installable, `tutorial/install` > Install the Project

**69. How do I stream a large response instead of building it in memory?**  `medium`
- Primary: `patterns/streaming` > Basic Usage
- Also: `patterns/streaming` > Streaming Contents, `patterns/streaming` > Streaming from Templates, `templating` > Streaming

**70. How do I serve a favicon?**  `easy`
- Primary: `patterns/favicon` > Adding a favicon

**71. How do I cache an expensive view result?**  `medium`
- Primary: `patterns/caching` > Caching
- Also: `patterns/viewdecorators` > Caching Decorator

**72. How do I reference static files like CSS from a template?**  `medium`
- Primary: `quickstart` > Static Files
- Also: `tutorial/static` > Static Files, `blueprints` > Static Files

## security (5)

**25. Does Flask protect against CSRF attacks by default?**  `easy`
- Primary: `web-security` > Cross-Site Request Forgery (CSRF)

**63. How does Flask protect against XSS and where does it not?**  `medium`
- Primary: `web-security` > Cross-Site Scripting (XSS)
- Also: `quickstart` > HTML Escaping

**64. Which HTTP security headers should I set?**  `medium`
- Primary: `web-security` > Security Headers
- Also: `web-security` > HTTP Strict Transport Security (HSTS), `web-security` > Content Security Policy (CSP), `web-security` > X-Content-Type-Options, `web-security` > X-Frame-Options

**65. How do I stop my site being shown inside someone else's iframe?**  `hard`
- Primary: `web-security` > X-Frame-Options
- Note: clickjacking, described by symptom rather than header name

**66. Is it safe to return a JSON array from an API endpoint?**  `hard`
- Primary: `web-security` > JSON Security

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
