from src.sprint_manager import SprintManager


def test_spr_001_create(tmp_path):
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("S1", "2025-12-01", "2025-12-07", 10)
    assert sp["name"] == "S1"
