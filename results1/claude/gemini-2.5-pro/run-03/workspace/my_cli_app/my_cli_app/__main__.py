#!/usr/bin/env python3
import argparse
import configparser
import os
import sys
from my_cli_app.commands import hello, goodbye

def main():
    """
    A simple CLI application that prints a greeting or a farewell.
    """
    config = configparser.ConfigParser()
    config_file = os.path.expanduser("~/.my-cli-app-rc")
    if os.path.exists(config_file):
        config.read(config_file)

    defaults = config['defaults'] if 'defaults' in config else {}

    parser = argparse.ArgumentParser(description="A simple CLI greeting application.")
    subparsers = parser.add_subparsers(dest="command", help='Sub-command help')

    # Hello command
    parser_hello = subparsers.add_parser('hello', help='Prints a greeting.')
    parser_hello.add_argument("name", nargs='*', help="The name to greet.")
    parser_hello.add_argument("--reverse", action="store_true", help="Reverse the name in the greeting.")

    # Goodbye command
    parser_goodbye = subparsers.add_parser('goodbye', help='Prints a farewell.')
    parser_goodbye.add_argument("name", nargs='*', help="The name for the farewell.")
    parser_goodbye.add_argument("--reverse", action="store_true", help="Reverse the name in the farewell.")

    # Set defaults from config
    if 'name' in defaults:
        parser.set_defaults(name=defaults['name'].split())
    else:
        parser.set_defaults(name=['World'])

    if 'reverse' in defaults:
        parser.set_defaults(reverse=defaults.getboolean('reverse'))
    else:
        parser.set_defaults(reverse=False)

    # Ugly hack to get the subcommand's arguments
    args = parser.parse_args()

    # Check if a subcommand was used
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Check if name was provided for subcommands
    if not args.name:
        if 'name' in defaults:
            args.name = defaults['name'].split()
        else:
            args.name = ["World"]

    name = ' '.join(args.name)
    if args.reverse:
        name = name[::-1]

    if args.command == 'hello':
        hello(name)
    elif args.command == 'goodbye':
        goodbye(name)

if __name__ == "__main__":
    main()
