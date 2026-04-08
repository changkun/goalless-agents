import os
import sys
import anthropic

# Get the API key from environment variables
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY environment variable not set.")
    sys.exit(1)

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=api_key)

def explain_command(command):
    """
    Uses the Anthropic API to explain a shell command.
    """
    if os.environ.get("ANTHROPIC_API_KEY") == "sk-dummy-key":
        return f"This is a simulated explanation for the command: '{command}'"

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": f"Explain the following shell command in a clear and concise way:\n\nCommand: {command}"
                }
            ]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python explain.py \"your-command-here\"")
        sys.exit(1)

    command_to_explain = sys.argv[1]
    explanation = explain_command(command_to_explain)
    print(explanation)
