import pytest

from src.operank_scheduling.algo.patient_assignment import (
    get_surgery_by_patient,
    sort_patients_by_priority,
)
from src.operank_scheduling.models.operank_models import Patient, Surgery


def test_patient_sorting():
    p1 = Patient(
        priority=1,
        name="a",
        patient_id="a",
        surgery_name="a",
        referrer="a",
        estimated_duration_m=3,
        uuid=1,
    )
    p2 = Patient(
        priority=7,
        name="a",
        patient_id="a",
        surgery_name="a",
        referrer="a",
        estimated_duration_m=3,
        uuid=2,
    )
    p3 = Patient(
        priority=5,
        name="a",
        patient_id="a",
        surgery_name="a",
        referrer="a",
        estimated_duration_m=3,
        uuid=3,
    )
    p4 = Patient(
        priority=4,
        name="a",
        patient_id="a",
        surgery_name="a",
        referrer="a",
        estimated_duration_m=3,
        uuid=4,
    )

    patients = [p1, p2, p3, p4]
    expected = [1, 4, 5, 7]
    sorted_patients_list = sort_patients_by_priority(patient_list=patients)
    for idx, patient in enumerate(sorted_patients_list):
        assert patient.priority == expected[idx]


def test_surgery_to_patient_link():
    p1 = Patient(
        priority=1,
        name="a",
        patient_id="a",
        surgery_name="a",
        referrer="a",
        estimated_duration_m=3,
        uuid=1,
    )
    s1 = Surgery(name="a", duration_in_minutes=65, uuid=1)
    surgeries = [s1]
    assert get_surgery_by_patient(p1, surgeries) == s1


def test_surgery_to_patient_link_exception():
    p1 = Patient(
        priority=1,
        name="a",
        patient_id="a",
        surgery_name="a",
        referrer="a",
        estimated_duration_m=3,
        uuid=1,
    )
    s1 = Surgery(name="a", duration_in_minutes=65, uuid=2)
    s2 = Surgery(name="a", duration_in_minutes=95, uuid=3)
    surgeries = [s1, s2]
    with pytest.raises(ValueError):
        get_surgery_by_patient(p1, surgeries) == s2
