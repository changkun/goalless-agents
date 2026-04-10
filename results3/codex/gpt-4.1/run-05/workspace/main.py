import sys

def to_palindrome(s: str) -> str:
    return s[::-1]

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <string>")
        sys.exit(1)
    input_str = sys.argv[1]
    palindrome = to_palindrome(input_str)
    print(palindrome)

if __name__ == "__main__":
    main()
