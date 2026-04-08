import subprocess
import re

def get_rtk_history():
    try:
        result = subprocess.run(['rtk', 'gain', '--history'], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running rtk gain --history: {e}")
        return None

def parse_rtk_history(history_output):
    if not history_output:
        return None

    total_commands_match = re.search(r"Total commands:\s+(\d+)", history_output)
    input_tokens_match = re.search(r"Input tokens:\s+(\d+)", history_output)
    output_tokens_match = re.search(r"Output tokens:\s+(\d+)", history_output)
    tokens_saved_match = re.search(r"Tokens saved:\s+(\d+)", history_output)
    percentage_saved_match = re.search(r"\((\d+\.\d+)%\)", history_output)

    total_commands = int(total_commands_match.group(1)) if total_commands_match else 0
    input_tokens = int(input_tokens_match.group(1)) if input_tokens_match else 0
    output_tokens = int(output_tokens_match.group(1)) if output_tokens_match else 0
    tokens_saved = int(tokens_saved_match.group(1)) if tokens_saved_match else 0
    percentage_saved = float(percentage_saved_match.group(1)) if percentage_saved_match else 0.0

    recent_commands = []
    recent_commands_block_start = history_output.find("Recent Commands")
    if recent_commands_block_start != -1:
        lines = history_output[recent_commands_block_start:].splitlines()
        for line in lines:
            match = re.search(r"(\d{2}-\d{2}\s\d{2}:\d{2})\s([▲•])\s(.*)\s+(-?\d+)%", line)
            if match:
                timestamp, arrow, command, savings = match.groups()
                recent_commands.append({"timestamp": timestamp, "command": command.strip(), "savings": int(savings)})
    return {
        "total_commands": total_commands,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tokens_saved": tokens_saved,
        "percentage_saved": percentage_saved,
        "recent_commands": recent_commands,
    }

def display_summary(parsed_data):
    if not parsed_data:
        print("No RTK history data found.")
        return

    print("RTK Token Usage Summary")
    print("-----------------------")
    print(f"Total commands: {parsed_data['total_commands']}")
    print(f"Input tokens: {parsed_data['input_tokens']}")
    print(f"Output tokens: {parsed_data['output_tokens']}")
    print(f"Tokens saved: {parsed_data['tokens_saved']} ({parsed_data['percentage_saved']}%)")
    print("\\nRecent Commands:")
    for command in parsed_data['recent_commands']:
        print(f"  {command['timestamp']} - {command['command']} ({command['savings']}%)")

if __name__ == "__main__":
    history_output = get_rtk_history()
    parsed_data = parse_rtk_history(history_output)
    display_summary(parsed_data)
