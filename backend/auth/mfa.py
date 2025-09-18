import random

user_challenges = {}

def generate_challenge(username: str) -> str:
    challenge = str(random.randint(100000, 999999))
    user_challenges[username] = challenge
    return challenge

def verify_token(username: str, token: str) -> bool:
    expected = user_challenges.get(username)
    return expected == token
