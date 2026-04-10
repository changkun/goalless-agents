from main import to_palindrome

def test_to_palindrome():
    assert to_palindrome('racecar') == 'racecar'
    assert to_palindrome('hello') == 'olleh'
    assert to_palindrome('12345') == '54321'
    assert to_palindrome('') == ''
