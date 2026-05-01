import json
import os
from dotenv import load_dotenv
from agent import ToolCallingAgent

load_dotenv()


def print_response(result: dict) -> None:
    """Pretty-print the agent's JSON response."""
    print("\n" + "=" * 50)
    print(json.dumps(result, indent=2))
    print("=" * 50 + "\n")


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found. Copy .env.example to .env and add your key.")
        return

    agent = ToolCallingAgent(api_key=api_key)

    print("Tool-Calling AI Agent")
    print("Type 'quit' to exit.\n")
    print("Example queries:")
    print("  - What time is it?")
    print("  - What is the weather in Tokyo?")
    print("  - What day is today and what's the weather in London?\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        result = agent.run(user_input)
        print_response(result)


if __name__ == "__main__":
    main()
