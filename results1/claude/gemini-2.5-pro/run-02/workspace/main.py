import datetime
import re
import random

class Chatbot:
    def __init__(self):
        self.running = True
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "Why don't skeletons fight each other? They don't have the guts.",
            "What do you call fake spaghetti? An Impasta!",
        ]
        self.commands = {
            "greet": {"keywords": ["hi", "hello", "hey"], "method": self.greet, "description": "Greets the user."},
            "weather": {"keywords": ["weather"], "method": self.tell_weather, "description": "Provides a static weather message."},
            "time": {"keywords": ["time"], "method": self.tell_time, "description": "Tells the current time."},
            "calculate": {"keywords": ["calculate"], "method": self.calculate, "description": "Performs a simple arithmetic calculation (e.g., 'calculate 2 + 2')."},
            "help": {"keywords": ["help"], "method": self.show_help, "description": "Shows this help message."},
            "joke": {"keywords": ["joke", "tell me a joke"], "method": self.tell_joke, "description": "Tells a random joke."}
        }

    def start(self):
        print("Hello! I am your friendly chatbot assistant.")
        print("Ask me anything, or type 'exit' to quit.")
        while self.running:
            user_input = input("> ")
            self.handle_input(user_input)

    def handle_input(self, user_input):
        lower_input = user_input.lower()
        if lower_input == 'exit':
            self.running = False
            print("Goodbye!")
            return

        for command, config in self.commands.items():
            for keyword in config["keywords"]:
                if keyword in lower_input:
                    if command == 'calculate':
                        config["method"](user_input)
                    else:
                        config["method"]()
                    return

        self.echo(user_input)

    def show_help(self):
        print("Available commands:")
        for command, config in self.commands.items():
            print(f"- {command}: {config['description']}")

    def greet(self):
        print("Hello there!")

    def tell_weather(self):
        print("I'm sorry, I cannot provide real-time weather information.")

    def tell_time(self):
        now = datetime.datetime.now()
        print(f"The current time is {now.strftime('%H:%M:%S')}.")

    def tell_joke(self):
        print(random.choice(self.jokes))

    def safe_eval(self, expression):
        try:
            # Remove all non-numeric/non-operator characters for safety
            expression = re.sub(r'[^\d\s+\-*/.]', '', expression)
            # Simple tokenizer and parser
            tokens = re.findall(r'(\d+\.?\d*|[+\-*/])', expression)
            if len(tokens) != 3:
                raise ValueError("Invalid expression format")

            num1, op, num2 = tokens
            num1, num2 = float(num1), float(num2)

            if op == '+':
                return num1 + num2
            elif op == '-':
                return num1 - num2
            elif op == '*':
                return num1 * num2
            elif op == '/':
                if num2 == 0:
                    return "Error: Division by zero."
                return num1 / num2
            else:
                raise ValueError("Unsupported operator")

        except Exception as e:
            return f"Error: {e}"

    def calculate(self, expression):
        expression_to_eval = re.sub(r'calculate', '', expression, flags=re.IGNORECASE).strip()
        result = self.safe_eval(expression_to_eval)
        # Check if result is a float and has no fractional part
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        print(f"The result is: {result}")

    def echo(self, text):
        print(f"You said: {text}")

if __name__ == "__main__":
    bot = Chatbot()
    bot.start()
