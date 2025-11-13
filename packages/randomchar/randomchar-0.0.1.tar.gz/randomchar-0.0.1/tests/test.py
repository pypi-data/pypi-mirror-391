import RandomChar
from RandomChar.Generator import CharType

a = RandomChar.create(CharType.UPPER, CharType.LOWER, length=10)
print(a)

b = RandomChar.secure_create(length=10)
print(b)