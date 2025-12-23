from src.sprint_manager import SprintManager


def test_spr_006_retrospective_concolic(tmp_path):
    sm = SprintManager(data_file=str(tmp_path / "sprints.json"))
    sp = sm.create_sprint("RC", "2025-12-01", "2025-12-07", 10)
    res = sm.track_sprint_retrospective(sp["id"], [], [], [])
    assert "retrospective" in res
