import random
import string

def generate_password(length: int = 12) -> str:
    """
    Generates a random password with letters, digits, and punctuation.
    """
    if length < 4:
        raise ValueError("Password length should be at least 4")

    # Define character sets
    letters = string.ascii_letters
    digits = string.digits
    punctuation = string.punctuation

    # Ensure at least one of each
    pwd = [
        random.choice(letters),
        random.choice(digits),
        random.choice(punctuation)
    ]

    # Fill the rest of the password
    all_chars = letters + digits + punctuation
    pwd.extend(random.choice(all_chars) for _ in range(length - len(pwd)))

    # Shuffle to make it random
    random.shuffle(pwd)

    return "".join(pwd)