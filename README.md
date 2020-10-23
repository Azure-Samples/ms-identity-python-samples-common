# MS Identity Python Common

This repository contains a set of code that is shared amongst the various Python samples for the Microsoft Identity Platform. This is a work in progress and we'd love to hear your feedback, comments and contributions.

## Features

The code present makes available or aims to make available the following features to the developers: 
- Allow for (but not require) automatic Flask/Django/other framework integration (implemented for flask)
- Allow for (but not require) automatic endpoint protection (implemented for flask)
- Catch AAD errors and handle them properly, e.g.:
    - password reset flow and edit profile flow (implemented)
    - insufficient / incremental consent (needs implementation)
- Token cache handling (implemeted)
- authN enforcement by decorator (implemented)
- Allow multiple identity sessions per user browser session (i.e., multiple logged in users in one browser session) (not yet implemented)
- Abstract authN and authZ implementation details away from developer
- authZ enforcement by decorator (not yet implented)

## Getting Started

### Prerequisites

- Python 3.8
- A virtual env for your own webapp project
- A flask project (currently implemented) or other web framework (not yet implemented) or desktop app (not yet implemented)

### Installation

##### 1. Activate a virtual environment

<details> <summary>Linux/OSX:</summary>
Open a terminal and type the following:
    
```Shell
# go to your web app directory on dev machine
cd your-flask-app-root-directory
python3 -m venv path-to-venv # only required if you don't have a venv already
# activate your virtual env
source path-to-venv/bin/activate
```
    
</details>

<details> <summary>Windows:</summary>
Open a terminal and type the following:
    
```PowerShell
# go to your web app directory on dev machine
cd your-flask-app-root-directory
python3 -m venv path-to-venv # only required if you don't have a venv already
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
. path-to-venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
    
</details>

##### 2. Now install the utils:
Use **only one** of the following two options:
- via https://
```
pip install git+https://github.com/azure-samples/ms-identity-python-utilities.git@idgsam
```
- via ssh://
```
pip install git+ssh://git@github.com/azure-samples/ms-identity-python-utilities.git@idgsam
```

##### 3. copy a config template (e.g. `aad.config.json`) from the repo and in to your project root dir, and fill in the details

### Quickstart


don't forget to import the required modules into your application as necessary:
```
from ms_identity_web import IdentityWebPython
from ms_identity_web.adapters import FlaskContextAdapter
from ms_identity_web.configuration import AADConfig
```

hook up the utils to your flask app:
```
adapter = FlaskContextAdapter(app)    # we are using flask
ms_identity_web = IdentityWebPython(AADConfig.parse_json('aad.config.json'), adapter) # instantiate utils
```

add the @ms_identity_web.login_required decorator to protect your routes:
```
@app.route('/my_protected_route')
@ms_identity_web.login_required # <-- developer only needs to hook up this decorator to any login_required endpoint like this
def my_protected_route():
    return render_template('my_protected_route.html')
```

## Demo

see: https://github.com/azure-samples/ms-identity-b2c-python-flask-webapp-authentication/tree/idgsam  (@ idgsam branch) for a demo

## Project Structure
#### __init__.py
    - main common code API is here.
#### adapters.py
    - FlaskContextAdapter for handling interaction between the API and flask context (e.g. session, request)
    - An ABC defining the interface for writing more adapters
    - Django adapter will go here.
    - Should be re-organised into folders on a per-framework basis?
#### flask_blueprint
    - a class that implemets all aad-specific endpoints. support for multiple instances with different prefixes if necessary
    - all bindings are automatic with flaskcontextadapter
#### blueprint-like functionality for django (`reusable django app`)
    - not yet implemented
#### context.py
    - IdentityContext class that holds ID-specific info (simple class with attributes and has_changed function for write-to-session decision)
#### configuration.py
    - simple configuration parser and sanity checker
#### constants.py
    - AAD constants
#### errors.py
    - AAd error classes
    
## Resources


