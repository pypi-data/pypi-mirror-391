from __future__ import annotations

def td0_update(v_s: float, r: float, v_next: float, *, alpha: float = 0.1, gamma: float = 0.99):
    """Perform a single TD(0) value update.

    Parameters
    ----------
    v_s : float
        Current estimate V(s).
    r : float
        Immediate reward observed after transitioning from s.
    v_next : float
        Current estimate V(s') for the next state.
    alpha : float, optional
        Learning rate in (0,1], by default 0.1.
    gamma : float, optional
        Discount factor in [0,1], by default 0.99.

    Returns
    -------
    tuple[float, float, float]
        (new_value, td_error, td_target)
    """
    if not (0 < alpha <= 1):
        raise ValueError("alpha must be in (0, 1].")
    if not (0 <= gamma <= 1):
        raise ValueError("gamma must be in [0, 1].")

    td_target = r + gamma * v_next
    td_error = td_target - v_s
    new_value = v_s + alpha * td_error
    return new_value, td_error, td_target
