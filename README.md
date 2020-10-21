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

1. From a linux/osx terminal window:
    ```
    # go to your web app directory on dev machine
    cd your-web-app-root-directory
    # activate your virtual env
    source path-to-virtual-env/bin/activate
    # install the utils:
    pip install git+ssh://git@github.com/azure-samples/ms-identity-python-utilities.git@idgsam
    ```
      - **Only if that doesn't work** due to not having SSH setup on your git account, continue to:
        ```
        # use the following command to clone via https://
        git clone https://github.com/azure-samples/ms-identity-python-utilities.git ms_id_py_utils
        cd ./ms_id_py_utils
        # check out the dev branch
        git checkout idgsam
        cd ..
        # install the utils
        pip install ./ms_id_py_utils
        ```
1. copy a config template (e.g. `aad.config.ini` from the repo and in to your project root dir, and fill in the details)

### Quickstart


don't forget to import the required modules as necessary:
```
from ms_identity_web import IdentityWebPython
from ms_identity_web.adapters import FlaskContextAdapter
from ms_identity_web.configuration import AADConfig
```

hook up the utils to your flask app:
```
adapter = FlaskContextAdapter(app) # we are using flask, so instantiate flask adapter
ms_identity_web = IdentityWebPython(AADConfig(file_path='aad.config.ini'), adapter) # instantiate utils by passing in config and flask adapter
```

add the @ms_identity_web.login_required decorator to protect your routes:
```
@app.route('/my_protected_route')
@ms_identity_web.login_required # <-- developer only needs to hook up this decorator to any login_required endpoint like this
def my_protected_route():
    return render_template('my_protected_route.html')
```

## Demo

see: ms-identity-b2c-python-flask-webapp-authentication @ idgsam branch for a demo

## Resources


