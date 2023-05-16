import datetime
from operank_scheduling.models.operank_models import (
    Surgery,
    Timeslot,
    get_all_surgeons,
)
from operank_scheduling.models.parse_data_to_models import (
    parse_single_json_block,
    load_patients_from_json,
    load_operating_rooms_from_json,
)

from operank_scheduling.models.parse_hopital_data import load_surgeon_schedules
from operank_scheduling.models.io_utilities import find_project_root
import pytest

root_dir = find_project_root()


def test_timeslot():
    new_timeslot = Timeslot(duration=60)
    assert repr(new_timeslot) == "Timeslot (60)"
    assert 43 in new_timeslot
    assert 184 not in new_timeslot


def test_timeslot_surgery_interaction():
    s = Surgery(name="Colostomy", duration_in_minutes=75, uuid=1, patient=None)
    t1 = Timeslot(duration=60)
    t2 = Timeslot(duration=120)

    assert s.can_fit_in(t1) is False
    assert s.can_fit_in(t2) is True


def test_parse_patient_data():
    patient_block_example_list = [
        {
            "name": "Mr. Man",
            "patient_id": "000000000",
            "surgery_name": "Kidney transplant",
            "referrer": "Dr. Guy",
            "estimated_duration_m": 165,
            "phone_number": "050-2222222",
            "priority": 7,
        },
        {
            "name": "Ms. Woman",
            "patient_id": "000000500",
            "surgery_name": "Loop colostomy",
            "referrer": "Dr. Dude",
            "estimated_duration_m": 55,
            "phone_number": "050-2222222",
            "priority": 5,
        },
    ]
    patients = list()

    for patient_block in patient_block_example_list:
        patient, surgery, timeslot = parse_single_json_block(patient_block)
        patients.append(patient)
        assert patient.uuid == surgery.uuid
        assert timeslot.duration >= surgery.duration

    assert patients[0].uuid is not patients[1].uuid


def test_get_all_surgeons():
    get_all_surgeons()


def test_get_earliest_timeslot_for_surgeon():
    surgeons = get_all_surgeons()
    load_surgeon_schedules(surgeons)
    surgeon = surgeons[0]

    date = datetime.datetime.now().date()
    timeslot = surgeon.get_earliest_open_timeslot(date, 120)
    pass


@pytest.mark.skip(reason="Soon to be deprecated...")
def test_load_patients_from_json():
    _, _, _ = load_patients_from_json(root_dir / "assets" / "example_patient_data.json")


def test_load_operating_rooms_from_json():
    _ = load_operating_rooms_from_json(
        root_dir / "assets" / "example_operating_room_schedule.json"
    )
