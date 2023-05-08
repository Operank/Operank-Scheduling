# Operank

## Installation (on dev environment)
To work on this repo as a developer, make sure to perform an **editable** install with pip, using `pip install -e .` 

This installes the package in 'editable' mode, allowing for the correct imports to work :)
Other requirements are needed, as specified in the `requirements.txt` file.

Currently, it's OK to install from that file, with the whole procedure looking something like this

```
python -m venv venv

.\venv\Scripts\activate             (on windows, or)
source ./venv/bin/activate          (on unix)

pip install -e .
pip install -r requirements.txt

```
