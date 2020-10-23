# Ms Identity Python Utils

Python MSAL helper utilities, work in progress

## Features

- Abstract authN and authZ implementation details away from developer
- authN enforcement by decorator
- authZ enforcement by decorator (not yet implented)

## Getting Started

### Prerequisites

- Python 3.8
- A virtual env for your own webapp project
- A flask project (currently implemented) or a Django project (not yet implemented)

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

##### 3. copy a config template (e.g. `aad.config.ini`) from the repo and in to your project root dir, and fill in the details

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
ms_identity_web = IdentityWebPython(AADConfig(file_path='aad.config.ini'), adapter) # instantiate utils
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

## Resources


