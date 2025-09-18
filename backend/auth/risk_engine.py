import datetime
import ipaddress

def calculate_risk(username: str) -> int:
    # Backward-compatible shim
    return 42

def calculate_risk_v2(
    *,
    username: str,
    ip: str | None = None,
    user_agent: str | None = None,
    login_time: datetime.datetime | None = None,
) -> int:
    score = 0

    # Time-based heuristic: late night/early morning riskier
    lt = login_time or datetime.datetime.utcnow()
    if lt.hour < 6 or lt.hour >= 22:
        score += 20

    # IP-based heuristic: non-routable/private is neutral; malformed slightly risky
    if ip:
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_global:
                score += 10
        except ValueError:
            score += 5
    else:
        score += 5

    # User-Agent heuristic: missing/very short UA is suspicious
    if not user_agent or len(user_agent) < 12:
        score += 15

    # Cap score 0..100
    return max(0, min(score, 100))
