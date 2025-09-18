def scan_url(url: str) -> bool:
    phishing_keywords = ["phish", "login", "bank"]
    return any(keyword in url.lower() for keyword in phishing_keywords)
