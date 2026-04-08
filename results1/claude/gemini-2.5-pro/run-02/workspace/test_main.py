import unittest
from unittest.mock import patch
from io import StringIO
from main import Chatbot

class TestChatbot(unittest.TestCase):

    def setUp(self):
        self.bot = Chatbot()

    def test_greet(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.bot.handle_input("hello")
            self.assertEqual(fake_out.getvalue().strip(), "Hello there!")

    def test_tell_weather(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.bot.handle_input("what is the weather?")
            self.assertEqual(fake_out.getvalue().strip(), "I'm sorry, I cannot provide real-time weather information.")

    def test_echo(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.bot.handle_input("test")
            self.assertEqual(fake_out.getvalue().strip(), "You said: test")

    def test_calculate_simple_addition(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.bot.handle_input("calculate 2 + 2")
            self.assertEqual(fake_out.getvalue().strip(), "The result is: 4")

    def test_calculate_invalid_expression(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.bot.handle_input("calculate two plus two")
            self.assertIn("Error:", fake_out.getvalue().strip())

    def test_calculate_division_by_zero(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.bot.handle_input("calculate 5 / 0")
            self.assertIn("Error: Division by zero.", fake_out.getvalue().strip())

    def test_show_help(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.bot.handle_input("help")
            output = fake_out.getvalue().strip()
            self.assertIn("Available commands:", output)
            self.assertIn("- greet: Greets the user.", output)
            self.assertIn("- weather: Provides a static weather message.", output)
            self.assertIn("- time: Tells the current time.", output)
            self.assertIn("- calculate: Performs a simple arithmetic calculation (e.g., 'calculate 2 + 2').", output)
            self.assertIn("- help: Shows this help message.", output)

    def test_tell_joke(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.bot.handle_input("tell me a joke")
            output = fake_out.getvalue().strip()
            self.assertIn(output, self.bot.jokes)

if __name__ == '__main__':
    unittest.main()
