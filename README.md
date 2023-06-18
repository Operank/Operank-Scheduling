<div align="center"><img width=600 height=300 src="https://i.imgur.com/PmBU9fO.png"></img></div>

# Overview
**Operank Scheduling** is a system for scheduling patients' surgeries, while optimizing the hospital's timetable. 

The system was developed as part of a final project in Electrical and Electronics Engineering, Tel-Aviv University, in collaboration with the Tel-Aviv 'Souraski' Medical Center (Ichilov Hospital).

Using an XGBoost prediction model trained on real data, along with an optimization approach with Google's `CP-SAT` solver, the system achieved an **increase of 25% in operating room utilization** and a subsequent **increase of 40% in the amount of surgeries scheduled** per unit of time - in comparison with the current schedules of Tel-Aviv 'Souraski' Medical Center.

# Design

The general design is summarized in the following diagram:
<div align="center"><img width=600 height=300 src="https://i.imgur.com/u3YPw4G.png"></img></div>


# Installation

## 🛠 Development Environment

To work on this repo as a developer, make sure to perform an **editable** install with pip, using `pip install -e .` 

This installs the package in 'editable' mode, allowing for the inner imports to work as intended.

Other requirements are needed, as specified in the `requirements.txt` file.

```
python -m venv venv

.\venv\Scripts\activate             (on windows, or)
source ./venv/bin/activate          (on unix)

pip install -e .
pip install -r requirements.txt
```

The code can now be edited, with changes being reflected immediately.

## 📑 Additional Assets
Some hospital-specific assets are needed for the program to run, including the surgeon schedules and some patients.

An example of all these assets can be found in the [following link](https://drive.google.com/file/d/1MYzh3KfzBntz8F8Gp7heoMNBkF-xx4bU/view?usp=sharing).

## 🚨 Tests

The package also contains unit tests for some of the functionality of the system. All tests needs to pass.

# Open Source Compliance

A list of all dependencies and their licenses are given in the `THIRDPARTYLICENSES` file.