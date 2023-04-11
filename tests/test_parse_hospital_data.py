from operank_scheduling.models.parse_hopital_data import (
    load_surgeon_data,
    map_surgery_to_team,
    load_surgeon_schedules,
)

from operank_scheduling.models.operank_models import get_all_surgeons


def test_map_surgery_to_team():
    mapping = map_surgery_to_team()
    assert mapping.get("Colectomy".upper()) == ["1", "2"]
    assert mapping.get("Laparoscopic adrenalectomy".upper()) == ["robotic"]
    assert mapping.get("Sentinal lymph node biopsy".upper()) == ["1"]
    assert mapping.get("Liver transplant,".upper()) is None


def test_surgeon_creation():
    load_surgeon_data()


def test_load_surgeon_schedules():
    surgeons = get_all_surgeons()
    # Test on only a few surgeons
    load_surgeon_schedules(surgeons[:5])
    pass
