from setuptools import setup, find_packages

setup(name='ms_identity_web',
      version='0.16.6',
      description='MSAL Identity Utilities',
      author='Azure Samples',
      url='https://github.com/azure-samples/ms-identity-python-utilities',
      packages=find_packages(),
      install_requires=['msal>=1.6.0,<2'],
     )


