from src.operank_scheduling.models.operank_models import Patient
from src.operank_scheduling.algo.patient_assignment import sort_patients_by_priority


def test_patient_sorting():
    p1 = Patient(priority=1, name="a", patient_id="a", surgery_name="a", referrer="a", estimated_duration_m=3, uuid=1)
    p2 = Patient(priority=7, name="a", patient_id="a", surgery_name="a", referrer="a", estimated_duration_m=3, uuid=2)
    p3 = Patient(priority=5, name="a", patient_id="a", surgery_name="a", referrer="a", estimated_duration_m=3, uuid=3)
    p4 = Patient(priority=4, name="a", patient_id="a", surgery_name="a", referrer="a", estimated_duration_m=3, uuid=4)

    patients = [p1, p2, p3, p4]
    expected = [1, 4, 5, 7]
    sorted_patients_list = sort_patients_by_priority(patient_list=patients)
    for idx, patient in enumerate(sorted_patients_list):
        assert patient.priority == expected[idx]
