from enum import Enum
import string, random, os, base64, math

class CharType(Enum):
    LOWER = "lower"
    UPPER = "upper"
    DIGITS = "digits"
    PUNCTUATION = "punctuation"

type_map = {
    CharType.LOWER: string.ascii_lowercase,
    CharType.UPPER: string.ascii_uppercase,
    CharType.DIGITS: string.digits,
    CharType.PUNCTUATION: string.punctuation
}

def create(*types: CharType, length: int = 6) -> str:
    char = "".join(type_map.get(t, "") for t in types)
    return "".join(random.choices(char, k=length)) if char else ""

def secure_create(length: int = 10) -> str:
    byte_length = math.ceil(length * 3 / 4)
    raw = os.urandom(byte_length)
    token = base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")
    return token[:length]