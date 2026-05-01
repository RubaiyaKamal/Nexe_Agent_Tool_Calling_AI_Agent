import json
import openai
from tools import TOOL_SCHEMAS, execute_tool

MAX_ITERATIONS = 5  # guard against infinite tool-call loops


class ToolCallingAgent:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def run(self, user_message: str) -> dict:
        """
        Send user_message to the model, handle tool calls, and return a
        structured JSON response.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant with access to tools. "
                    "Use tools when appropriate to answer the user's question accurately."
                ),
            },
            {"role": "user", "content": user_message},
        ]

        tools_used = []
        iterations = 0

        try:
            while iterations < MAX_ITERATIONS:
                iterations += 1

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                )

                message = response.choices[0].message

                # ── No tool call → final answer ───────────────────────────
                if message.tool_calls is None:
                    return {
                        "status": "success",
                        "response": message.content,
                        "tools_used": tools_used,
                        "iterations": iterations,
                    }

                # ── Tool call(s) detected ─────────────────────────────────
                messages.append(message)  # append assistant message with tool_calls

                for tool_call in message.tool_calls:
                    name = tool_call.function.name
                    arguments = tool_call.function.arguments

                    result = execute_tool(name, arguments)
                    tools_used.append(name)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )

            # Exceeded max iterations
            return {
                "status": "error",
                "response": "Agent exceeded maximum iterations without a final answer.",
                "tools_used": tools_used,
                "iterations": iterations,
            }

        except openai.AuthenticationError:
            return {
                "status": "error",
                "response": "Invalid OpenAI API key. Check your .env file.",
                "tools_used": tools_used,
                "iterations": iterations,
            }
        except openai.RateLimitError:
            return {
                "status": "error",
                "response": "OpenAI rate limit reached. Please wait and try again.",
                "tools_used": tools_used,
                "iterations": iterations,
            }
        except openai.OpenAIError as e:
            return {
                "status": "error",
                "response": f"OpenAI API error: {e}",
                "tools_used": tools_used,
                "iterations": iterations,
            }
