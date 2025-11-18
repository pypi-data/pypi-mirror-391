import getpass
from bhavani.core import greet

def test_greet_with_name():
    result = greet("bunny")
    assert result == "Hello, bunny — from bhavani!"

def test_greet_auto_username():
    username = getpass.getuser()
    result = greet()
    assert result == f"Hello, {username} — from bhavani!"
