---
page_type: sample
languages:
  - python
products:
  - azure-active-directory  
  - azure-active-directory-b2c
  - azure-active-directory-domain
name: Python flask webapp utilizing MSAL for Python to authenticate users with Azure Active Directory B2C (Azure AD B2C)
urlFragment: ms-identity-b2c-python-flask-webapp-authentication
description: "This sample demonstrates a Python Flask webapp that signs in users with Azure AD B2C"
---
# Python Flask webapp using MSAL for Python to authenticate users with Azure Active Directory B2C

 1. [Overview](#overview)
 1. [Scenario](#scenario)
 1. [Contents](#contents)
 1. [Prerequisites](#prerequisites)
 1. [Setup](#setup)
 1. [Registration](#register-the-sample-application-with-your-azure-ad-b2c-tenant)
 1. [Running the sample](#running-the-sample)
 1. [Explore the sample](#explore-the-sample)
 1. [About the code](#about-the-code)
 1. [Deployment](#deployment)
 1. [More information](#more-information)
 1. [Community Help and Support](#community-help-and-support)
 1. [Contributing](#contributing)
 1. [Code of Conduct](#code-of-conduct)


<!-- ![Build badge](https://identitydivision.visualstudio.com/_apis/public/build/definitions/a7934fdd-dcde-4492-a406-7fad6ac00e17/<BuildNumber>/badge)
// TODO: COMMENT OUT BUILD BADGE UNTIL WE FIND A PURPOSE FOR IT-->
## Overview
This sample demonstrates a Python Flask webapp that authenticates users with Azure Active Directory B2C (Azure AD B2C) using the the [Microsoft Authentication Library \(MSAL\) for Python](https://github.com/AzureAD/microsoft-authentication-library-for-python).



## Scenario

1. The client web application uses **MSAL for Python** to sign-in users and obtains an [ID Token](https://docs.microsoft.com/azure/active-directory/develop/id-tokens) from **Azure AD B2C**:
2. The **ID Token** proves that the user has successfully authenticated against a **Azure AD B2C** tenant.
3. The web application protects one of its routes according to user's authentication status.

![Overview](./ReadmeFiles/sign-in.png)

## Contents

| File/folder       | Description                                |
|-------------------|--------------------------------------------|
|`authenticate_users_b2c.py` | The sample app code.              |
|`msid_web_python`  | The auth-related utility code.             |
|`CHANGELOG.md`     | List of changes to the sample.             |
|`CONTRIBUTING.md`  | Guidelines for contributing to the sample. |
|`LICENSE`          | The license for the sample.                |

## Prerequisites

- [Python 3](https://www.python.org/downloads/)
- A virtual environment to install packages from [requirements.txt](requirements.txt)
- An **Azure AD B2C** tenant. For more information see: [How to get an Azure AD B2C tenant](https://docs.microsoft.com/azure/active-directory-b2c/tutorial-create-tenant) (optional)

## Setup

### Step 1: Clone or download this repository

From your shell or command line:

```Shell
git clone https://github.com/Azure-Samples/ms-identity-b2c-python-flask-webapp-authentication.git
```

or download and extract the repository .zip file.

### Step 2: Install project dependencies

1. navigate to the project folder
2. activate a Python 3 virtual environment
3. install project dependencies

- In Linux/OSX via the terminal:
```Shell
  cd project-root-directory
  python3 -m venv venv # only required to create the venv if you don't have a venv already
  source venv/bin/activate # activates the venv
  pip install -r requirements.txt
```
- In Windows via PowerShell:
```PowerShell
  cd project-root-directory
  python3 -m venv venv # only required to create the venv if you don't have a venv already
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
  . .\venv\Scripts\Activate.ps1 # activates the venv
  pip install -r requirements.txt
```

### Register the sample application with your Azure AD B2C tenant

:warning: This sample comes with a pre-registered application for testing purposes. If you would like to use your own **Azure AD B2C** tenant and application, follow the steps below to register and configure the application in the **Azure Portal**. Otherwise, continue with the steps for [Running the sample](#running-the-sample).
<details>
  <summary>Expand this section to see manual steps for configuring your own tenant:</summary>

### Choose the Azure AD B2C tenant where you want to create your applications

As a first step you'll need to:

1. Sign in to the [Azure portal](https://portal.azure.com).
1. If your account is present in more than one **Azure AD B2C** tenant, select your profile at the top right corner in the menu on top of the page, and then **switch directory** to change your portal session to the desired Azure AD B2C tenant.

### Create User Flows and Custom Policies

Please refer to [Tutorial: Create user flows in Azure Active Directory B2C](https://docs.microsoft.com/azure/active-directory-b2c/tutorial-create-user-flows) to create common user flows like sign up, sign in, edit profile, and passowrd reset.

You may consider creating [Custom policies in Azure Active Directory B2C](https://docs.microsoft.com/en-us/azure/active-directory-b2c/custom-policy-overview) as well, however, this is beyond the scope of this tutorial.

### Add External Identity Providers

Please refer to: [Tutorial: Add identity providers to your applications in Azure Active Directory B2C](https://docs.microsoft.com/azure/active-directory-b2c/tutorial-add-identity-providers)

### Register the webapp (ms-identity-b2c-python-flask-webapp-authentication)


1. Navigate to the [Azure portal](https://portal.azure.com) and select the **Azure AD B2C** service.
1. Select the **App Registrations** blade on the left, then select **New registration**.
1. In the **Register an application page** that appears, enter your application's registration information:
   - In the **Name** section, enter a meaningful application name that will be displayed to users of the app, for example `ms-identity-b2c-python-flask-webapp-authentication`.
   - Under **Supported account types**, select **Accounts in any organizational directory and personal Microsoft accounts (e.g. Skype, Xbox, Outlook.com)**.
   - In the **Redirect URI (optional)** section, select **Web** in the combo-box and enter the following redirect URI: `http://localhost:8080/ms-identity-b2c-python-flask-webapp-authentication/auth_redirect`.
1. Select **Register** to create the application.
1. In the app's registration screen, find and note the **Application (client) ID**. You use this value in your app's configuration file(s) later in your code.
1. Select **Save** to save your changes.

1. In the app's registration screen, click on the **Certificates & secrets** blade in the left to open the page where we can generate secrets and upload certificates.
1. In the **Client secrets** section, click on **New client secret**:
   - Type a key description (for instance `app secret`),
   - Select one of the available key durations (**In 1 year**, **In 2 years**, or **Never Expires**) as per your security concerns.
   - The generated key value will be displayed when you click the **Add** button. Copy the generated value for use in the steps later.
   - You'll need this key later in your code's configuration files. This key value will not be displayed again, and is not retrievable by any other means, so make sure to note it from the Azure portal before navigating to any other screen or blade.



#### Configure the webapp (ms-identity-b2c-python-flask-webapp-authentication) to use your app registration

Open the project in your IDE (like **Visual Studio Code**) to configure the code.

> In the steps below, "ClientID" is the same as "Application ID" or "AppId".

1. Open the [aad_config.py](aad_config.py) file.
1. Find the key `client['client_id']: str =` and replace the existing value with the application ID (clientId) of the `ms-identity-b2c-python-flask-webapp-authentication` application from the Azure portal.
1. Find the key `client['client_credential']: str =` and replace the existing value with the key you saved during the creation of the `ms-identity-b2c-python-flask-webapp-authentication` application from the Azure portal.
1. Find the key `client['authority']: str =` and replace the first instance of `fabrikamb2c` with the name of the AAD B2C tenant in which you created the `ms-identity-b2c-python-flask-webapp-authentication` application in the Azure portal.
1. Find the key `client['authority']: str =` and replace the second instance of `fabrikamb2c` with the name of the AAD B2C tenant in which you created the `ms-identity-b2c-python-flask-webapp-authentication` application in the Azure portal.
<!-- 1. Find the app key `auth_request['scopes']: list =` and place into the array the clientId value you placed into `auth_request['scopes']` in step 1 of this section. -->
1. Find the key `b2c_policy[str(Policy.SUSI_KEY)]: str =` and replace the value with the name of the sign-up/sign-in userflow policy you created in the AAD B2C tenant in which you created the `ms-identity-b2c-python-flask-webapp-authentication` application in the Azure portal.
1. Find the key `b2c_policy[str(Policy.PASSWORD_KEY)]: str =` and replace the value with the name of the password reset userflow policy you created in the AAD B2C tenant in which you created the `ms-identity-b2c-python-flask-webapp-authentication` application in the Azure portal.
1. Find the key `2c_policy[str(Policy.PROFILE_KEY)]: str =` and replace the value with the name of the edit profile userflow policy you created in the AAD B2C tenant in which you created the `ms-identity-b2c-python-flask-webapp-authentication` application in the Azure portal.

</details>

## Running the sample

- To run the sample, open a terminal window. Navigate to the root of the project. Be sure your virtual environment with dependencies is activated ([Prerequisites](#prerequisites)). 
- In Linux/OSX via the terminal:
  ```Shell
    export FLASK_APP=authenticate_users_in_my_tenant.py
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    export FLASK_RUN_CERT=adhoc
    flask run
  ```
- In Windows via PowerShell:
  ```PowerShell
    set FLASK_APP=authenticate_users_in_my_tenant.py
    set FLASK_ENV=development
    set FLASK_DEBUG=1
    set FLASK_RUN_CERT=adhoc
    flask run
  ```
- Alternatively, you may use `python -m flask run` instead of `flask run`
- Navigate to [https://127.0.0.1:5000](https://127.0.0.1:5000) in your browser

![Experience](./ReadmeFiles/app.png)

## Explore the sample

- Note the signed-in or signed-out status displayed at the center of the screen.
- Click the context-sensitive button at the top right (it will read `Sign In` on first run)
- Follow the instructions on the next page to sign in with an account of your chosen identity provider.
- Note the context-sensitive button now says `Sign out` and displays your username to its left.
- The middle of the screen now has an option to click for ID Token Details: click it to see some of the ID token's decoded claims.
- You also have the option of editing your profile. Click the link to edit details like your display name, place of residence, and profession.
- You can also use the button on the top right to sign out.
- After signing out, click this link to the [token details page](https://127.0.0.1:5000/auth/token_details) to observe how the app displays a `401: unauthorized` error instead of the ID token claims.

> :information_source: Did the sample not work for you as expected? Did you encounter issues trying this sample? Then please reach out to us using the [GitHub Issues](../issues) page.

## About the code

This sample shows how to use [Microsoft Authentication Library \(MSAL\) for Python](https://github.com/AzureAD/microsoft-authentication-library-for-python) to sign in users from your Azure AD B2C tenant. 

The following parameters need to be provided upon instantiation via config dictionaries:

- The **Client ID** of the app
- The **Client Secret**, which is a requirement for Confidential Client Applications
- The **Azure AD B2C Authority** concatenated with the appropriate **UserFlowPolicy** for sign-up/sign-in or profile-edit or password-reset.

1. The first step of the sign-in process is to send a request to the /authorize endpoint on Azure Active Directory B2C. Our MSAL(Python) ConfidentialClientApplication instance is leveraged to construct an authorization request URL, and our app redirects the browser to this URL.
1. The user is presented with a sign-in prompt by Azure Active Directory B2C. If the sign-in attempt is successful, the user's browser is redirected to our app's redirect endpoint. A valid request to this endpoint will contain an [**authorization code**](https://docs.microsoft.com/en-us/azure/active-directory-b2c/authorization-code-flow).
1. Our ConfidentialClientApplication instance then exchanges this authorization code for an ID Token and Access Token from Azure Active Directory B2C.
1. If acquireToken is successful, MSAL for Python validates the signature and nonce of the incoming token. If these checks succeed, it returns the resulting tokens and ID token claims as a dictionary.
1. It is the application's responsibility to store these tokens securely.

## More information

- [Microsoft Authentication Library \(MSAL\) for Python](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [MSAL Python ReadTheDocs](https://msal-python.readthedocs.io/en/latest/)
- [What is Azure Active Directory B2C?](https://docs.microsoft.com/azure/active-directory-b2c/overview)
- [Application types that can be used in Active Directory B2C](https://docs.microsoft.com/azure/active-directory-b2c/application-types)
- [Recommendations and best practices for Azure Active Directory B2C](https://docs.microsoft.com/azure/active-directory-b2c/best-practices)
- [Azure AD B2C session](https://docs.microsoft.com/azure/active-directory-b2c/session-overview)
- [MSAL code samples](https://docs.microsoft.com/azure/active-directory/develop/sample-v2-code)

## Community Help and Support

Use [Stack Overflow](https://stackoverflow.com/questions/tagged/msal) to get support from the community.
Ask your questions on Stack Overflow first and browse existing issues to see if someone has asked your question before.
Make sure that your questions or comments are tagged with [`azure-active-directory` `ms-identity` `adal` `msal`].

If you find a bug in the sample, please raise the issue on [GitHub Issues](../../issues).

To provide a recommendation, visit the following [User Voice page](https://feedback.azure.com/forums/169401-azure-active-directory).

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

## Code of Conduct

This project has adopted the Microsoft Open Source Code of Conduct. For more information see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.
