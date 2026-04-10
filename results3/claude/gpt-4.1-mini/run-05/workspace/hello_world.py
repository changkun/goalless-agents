import sys

def get_greeting(name=None):
    if name:
        return f"Hello, {name}!"
    return "Hello, world!"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(get_greeting(sys.argv[1]))
    else:
        print(get_greeting())
