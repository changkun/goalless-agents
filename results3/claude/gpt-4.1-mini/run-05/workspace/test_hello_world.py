import unittest
import hello_world

class TestHelloWorld(unittest.TestCase):
    def test_get_greeting(self):
        self.assertEqual(hello_world.get_greeting(), "Hello, world!")

if __name__ == "__main__":
    unittest.main()
