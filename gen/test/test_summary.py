from model.summary import Summary


def test_summary():
    s = Summary()
    s.workloads = ["wl1", 'wl2']
    s.pvcs = ["pvc1", "pvc2"]
    exp_result = 'WLs:\n  wl1\n  wl2\n\nPVCs:\n  pvc1\n  pvc2'
    assert s.__repr__() == exp_result
