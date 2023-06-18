<div align="center"><img width=600 height=300 src="https://i.imgur.com/PmBU9fO.png"></img></div>

# Overview
**Operank Scheduling** is a system for scheduling patients' surgeries, while optimizing the hospital's timetable. 

The system was developed as part of a final project in Electrical Engineering, Tel-Aviv University, in collaboration with the Tel-Aviv 'Souraski' Medical Center (Ichilov Hospital).

Using an XGBoost prediction model trained on real data, along with an optimization approach with Google-OR's CP-SAT solver, the system achieved an **increase of 25% in operating room utilization** and a subsequent **increase of 40% in the amount of surgeries scheduled** per unit of time - in comparison with the current schedules of Tel-Aviv 'Souraski' Medical Center.

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

## 🚨 Tests

The package also contains unit tests for some of the functionality of the system. All tests needs to pass.