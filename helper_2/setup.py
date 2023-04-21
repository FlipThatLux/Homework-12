from setuptools import setup, find_namespace_packages

setup(name='helper_2',
      version='1.0',
      description='Just a little guy',
      packages=find_namespace_packages(),
      entry_points={'console_scripts': ['helper = helper_2.helper_2']})