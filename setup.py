from setuptools import setup, find_packages

setup(name='ms_identity_web',
      version='0.13.20',
      description='MSAL Identity Utilties',
      author='Azure Samples',
      url='https://github.com/azure-samples/ms-identity-python-utilities',
      packages=find_packages(),
      install_requires=['msal>=1.6.0,<2'],
     )


