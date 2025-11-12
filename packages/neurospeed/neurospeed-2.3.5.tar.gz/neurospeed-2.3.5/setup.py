from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
   name='neurospeed',
   version='2.3.5',
   author='NeuroBrave',
   contact_email='oleg@neurobrave.com',
   long_description = long_description,
   long_description_content_type="text/markdown",
   packages=find_packages(),
   scripts=[],
   package_data={'neurospeed': ['config/*']},
   url='https://bitbucket.org/neurobrave/neurospeed_python_api',
   classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
   ],
   license='LICENSE.txt',
   description='NeuroSpeed Python API',
   install_requires=[
       "python-socketio[client]==5.3.0"
   ],
)

