from src.operank_scheduling.models.parse_hopital_data import map_surgery_to_team


def test_map_surgery_to_team():
    mapping = map_surgery_to_team()
    assert mapping.get("Colectomy".upper()) == ["1", "2"]
    assert mapping.get("Laparoscopic adrenalectomy".upper()) == ["robotic"]
