import pytest
from typing import List, Tuple
import datetime

from operank_scheduling.algo.patient_assignment import (
    get_surgery_by_patient,
    sort_patients_by_priority,
    suggest_feasible_dates,
    get_surgeons_by_team,
    find_suitable_surgeons,
    find_suitable_operating_rooms,
    find_suitable_timeslots,
)

from operank_scheduling.models.parse_data_to_models import (
    load_operating_rooms_from_json,
    load_patients_from_json,
)

from operank_scheduling.algo.surgery_distribution_models import (
    distribute_timeslots_to_operating_rooms,
    distribute_timeslots_to_days,
)

from operank_scheduling.models.operank_models import (
    Patient,
    Surgery,
    OperatingRoom,
    Surgeon,
    Timeslot,
    get_all_surgeons,
)

from operank_scheduling.models.io_utilities import find_project_root


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


@pytest.fixture
def create_dummy_patient_and_surgeries():
    patient = Patient(
        priority=1,
        name="a",
        patient_id="a",
        surgery_name="a",
        referrer="a",
        estimated_duration_m=3,
        uuid=1,
    )
    s1 = Surgery(name="a", duration_in_minutes=65, uuid=1)
    s2 = Surgery(name="a", duration_in_minutes=95, uuid=2)
    surgeries = [s1, s2]
    return (patient, surgeries)


def test_surgery_to_patient_link(create_dummy_patient_and_surgeries):
    patient, surgeries = create_dummy_patient_and_surgeries
    assert get_surgery_by_patient(patient, surgeries) == surgeries[0]


def test_surgery_to_patient_link_exception(create_dummy_patient_and_surgeries):
    patient = Patient(
        priority=1,
        name="a",
        patient_id="a",
        surgery_name="a",
        referrer="a",
        estimated_duration_m=3,
        uuid=7,
    )
    _, surgeries = create_dummy_patient_and_surgeries
    with pytest.raises(ValueError):
        get_surgery_by_patient(patient, surgeries)


@pytest.fixture
def load_patients_and_surgeons_from_example_config() -> (
    Tuple[
        List[Patient], List[Surgery], List[Timeslot], List[OperatingRoom], List[Surgeon]
    ]
):
    assets_dir = find_project_root() / "assets"
    patient_list, surgery_list, timeslot_list = load_patients_from_json(
        assets_dir / "example_patient_data.json"
    )
    operating_rooms = load_operating_rooms_from_json(
        assets_dir / "example_operating_room_schedule.json"
    )
    surgeons = get_all_surgeons()
    return patient_list, surgery_list, timeslot_list, operating_rooms, surgeons


@pytest.fixture
def schedule_patients(load_patients_and_surgeons_from_example_config):
    (
        patient_list,
        surgery_list,
        timeslot_list,
        operating_rooms,
        surgeon_list,
    ) = load_patients_and_surgeons_from_example_config

    operating_rooms = operating_rooms[:2]
    distribute_timeslots_to_operating_rooms(timeslot_list, operating_rooms)
    distribute_timeslots_to_days(operating_rooms)

    for operating_room in operating_rooms:
        operating_room.schedule_timeslots_to_days(datetime.datetime.now())

    return (
        patient_list,
        surgery_list,
        timeslot_list,
        operating_rooms,
        surgeon_list,
    )


def test_get_surgeons_by_team():
    surgeons = get_all_surgeons()
    breast_team = get_surgeons_by_team("breast", surgeons)
    for surgeon in breast_team:
        assert surgeon.team == "breast".upper()


def test_find_suitable_operating_rooms(load_patients_and_surgeons_from_example_config):
    (
        patient_list,
        surgery_list,
        _,
        operating_rooms,
        _,
    ) = load_patients_and_surgeons_from_example_config

    for patient in patient_list:
        procedure = get_surgery_by_patient(patient, surgery_list)
        _ = find_suitable_operating_rooms(procedure, operating_rooms)


def test_find_suitable_surgeons(load_patients_and_surgeons_from_example_config):
    (
        patient_list,
        surgery_list,
        _,
        _,
        surgeon_list,
    ) = load_patients_and_surgeons_from_example_config
    for patient in patient_list:
        procedure = get_surgery_by_patient(patient, surgery_list)
        _ = find_suitable_surgeons(procedure, surgeon_list)


def test_find_suitable_timeslots(schedule_patients):
    (
        patient_list,
        surgery_list,
        _,
        operating_rooms,
        surgeon_list,
    ) = schedule_patients

    for patient in patient_list:
        procedure = get_surgery_by_patient(patient, surgery_list)
        suitable_rooms = find_suitable_operating_rooms(procedure, operating_rooms)
        suitable_surgeons = find_suitable_surgeons(procedure, surgeon_list)
        _ = find_suitable_timeslots(procedure, suitable_rooms, suitable_surgeons)


def test_suggest_feasible_dates(schedule_patients):
    (
        patient_list,
        surgery_list,
        _,
        operating_rooms,
        surgeon_list,
    ) = schedule_patients
    for patient in patient_list:
        available_dates = suggest_feasible_dates(
            patient, surgery_list, operating_rooms, surgeon_list
        )
        assert len(available_dates) > 0
