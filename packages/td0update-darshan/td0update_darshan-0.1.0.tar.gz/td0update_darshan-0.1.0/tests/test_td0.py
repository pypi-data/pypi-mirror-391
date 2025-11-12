import math
from td0update import td0_update

def test_basic_update():
    new_v, err, target = td0_update(0.0, 1.0, 0.5, alpha=0.1, gamma=0.9)
    # target = 1 + 0.9*0.5 = 1.45
    assert math.isclose(target, 1.45, rel_tol=1e-9)
    assert math.isclose(err, 1.45, rel_tol=1e-9)
    # new_v = 0 + 0.1*1.45 = 0.145
    assert math.isclose(new_v, 0.145, rel_tol=1e-9)

def test_input_bounds():
    try:
        td0_update(0.0, 0.0, 0.0, alpha=0.0)
        assert False, "alpha=0 should raise"
    except ValueError:
        pass
    try:
        td0_update(0.0, 0.0, 0.0, gamma=1.1)
        assert False, "gamma>1 should raise"
    except ValueError:
        pass
