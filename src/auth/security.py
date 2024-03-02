import bcrypt


def hash_password(password: str) -> bytes:
  """
  Hashes a password using bcrypt.

  Args:
    password (str): The password to be hashed.

  Returns:
    bytes: The hashed password.
  """
  pw = bytes(password, "utf-8")
  salt = bcrypt.gensalt()
  return bcrypt.hashpw(pw, salt)


def check_password(password: str, password_in_db: bytes) -> bool:
  """
  Checks if a password matches the hashed password stored in the database.

  Args:
    password (str): The password to be checked.
    password_in_db (bytes): The hashed password stored in the database.

  Returns:
    bool: True if the password matches, False otherwise.
  """
  password_bytes = bytes(password, "utf-8")
  return bcrypt.checkpw(password_bytes, password_in_db)
