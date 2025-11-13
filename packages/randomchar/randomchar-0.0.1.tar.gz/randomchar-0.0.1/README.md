# RandomChar

## Install
```shell
pip install randomchar
```

## How to use

### Basic
```python
import RandomChar
from RandomChar.Generator import CharType

char = RandomChar.create(CharType.LOWER)
print(char)
```

```commandline
ex: xyfntp
```

### Length
```python
import RandomChar
from RandomChar.Generator import CharType

char = RandomChar.create(CharType.LOWER, length=10)
print(char)
```

```commandline
ex: xyfntpqncy
```
Length default: 6

### CharType
```python
import RandomChar
from RandomChar.Generator import CharType

char = RandomChar.create(CharType.LOWER, CharType.UPPER, CharType.DIGITS, CharType.PUNCTUATION)
print(char)
```

```commandline
ex: dp8N!n
```

---

### Secure
```python
import RandomChar

char = RandomChar.secure_create(length=16)
print(char)
```

```commandline
ex: nAq1s_QhWe4t-3zP
```
Length default: 10

URL-safe, base64