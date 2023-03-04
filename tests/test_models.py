from src.operank_scheduling.models.operank_models import Surgery, Timeslot
from src.operank_scheduling.models.parse_patient_data import \
    parse_single_json_block


def test_timeslot():
    new_timeslot = Timeslot(duration=60)
    assert repr(new_timeslot) == "Timeslot (60)"
    assert 43 in new_timeslot
    assert 184 not in new_timeslot


def test_timeslot_surgery_interaction():
    s = Surgery(name="Colostomy", duration_in_minutes=75, uuid=1)
    t1 = Timeslot(duration=60)
    t2 = Timeslot(duration=120)

    assert s.can_fit_in(t1) is False
    assert s.can_fit_in(t2) is True


def test_parse_patient_data():
    patient_block_example_list = [
        """{
    "name" : "Mr. Man",
    "patient_id": "000000000",
    "surgery_name" : "Kidney transplant",
    "referrer" : "Dr. Guy",
    "estimated_duration_m" : 165,
    "priority" : 7}
    """,
        """
{   "name" : "Ms. Woman",
    "patient_id": "000000500",
    "surgery_name" : "Loop colostomy",
    "referrer" : "Dr. Dude",
    "estimated_duration_m" : 55,
    "priority" : 5
}
    """,
    ]
    patients = list()

    for patient_block in patient_block_example_list:
        patient, surgery, timeslot = parse_single_json_block(patient_block)
        patients.append(patient)
        assert patient.uuid == surgery.uuid
        assert timeslot.duration >= surgery.duration

    assert patients[0].uuid is not patients[1].uuid
