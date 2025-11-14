# # agent.py
# from dotenv import load_dotenv
# import os
# import asyncio
# from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
# from agents.mcp import MCPServerStdio
# from config import playWright_MCP_params
# from userProfile import user_profile

# load_dotenv(override=True)

# MODEL_URL = os.getenv('GEMINI_API_URL')
# MODEL_KEY = os.getenv('GEMINI_API_KEY')
# MODEL_NAME = os.getenv('GEMINI_MODEL_NAME')

# # Model initialization
# model_client = AsyncOpenAI(base_url=MODEL_URL, api_key=MODEL_KEY)
# model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=model_client)



# # ==============================
# # UPDATED SYSTEM INSTRUCTIONS
# # ==============================
# instructions = f"""
# You are a MULTI-PURPOSE AI AGENT with three roles:

# 1. **Normal AI Assistant**
#    - Answer questions.
#    - Help with general tasks.
#    - Provide explanations.

# 2. **Smart Web Summarizer (via Playwright MCP)**
#    - When the user asks to summarize a webpage, you MUST:
#      - Navigate to the provided URL.
#      - Extract the main content.
#      - Summarize it concisely.
#      - Ignore ads, navigation bars, footers, popups.
#      - Include the URL at the end of the summary.

# 3. **Form Filling Automation Agent**
#    - You MUST fill browser forms using ONLY the stored profile.
#    - NEVER ask the user for information that exists in the profile.
#    - NEVER say "give me your details" or “provide information”.
#    - Fill out EVERY visible field.
#    - DO NOT click submit unless user explicitly says "submit".
#    - Use this exact profile:

# {user_profile}

# Behavior Rules:
# - When unsure, act as a normal assistant.
# - dont say words like "As an AI model" or "As a helpful AI assistant". just answer directly.
# - When user asks summary → use page reading.
# - When user asks form filling → use profile.
# - Otherwise → behave like a normal assistant.
# """


# # ==============================
# # USER INTENT DETECTION
# # ==============================
# def wants_form_fill(text: str) -> bool:
#     """Detect if user wants form auto-fill."""
#     keywords = [
#         "fill the form", "fill this form", "fill form",
#         "auto fill", "autofill", "complete form",
#         "enter my details", "register me",
#         "sign me up", "create account", "apply for",
#         "apply now", "sign up for me"
#     ]
#     t = text.lower()
#     return any(k in t for k in keywords)


# def wants_summarize(text: str) -> bool:
#     """Detect if user wants a page summary."""
#     keywords = ["summarize", "summary", "brief", "tl;dr", "short summary"]
#     t = text.lower()
#     return any(k in t for k in keywords)


# # ==============================
# # BUILD FORM INSTRUCTIONS
# # ==============================
# def build_form_instruction():
#     lines = ["Fill every visible form field using ONLY this profile data:\n"]

#     for key, value in user_profile.items():
#         lines.append(f"{key}: {value}")

#     lines.append("\nIMPORTANT RULES:")
#     lines.append("- Do NOT ask the user for additional information.")
#     lines.append("- Do NOT skip any field.")
#     lines.append("- Do NOT click submit unless the user explicitly requests.")

#     return "\n".join(lines)


# # ==============================
# # MAIN CONTROLLER
# # ==============================
# async def browser_controller(tab_url: str = None, user_input: str = None):
#     """
#     Handles requests from the extension.
#     Controls Playwright MCP and performs browser actions.
#     """

#     if not user_input:
#         raise ValueError("user_input cannot be empty")

#     async with MCPServerStdio(
#         params=playWright_MCP_params,
#         client_session_timeout_seconds=0
#     ) as playWrightServer:

#         browser_agent = Agent(
#             name="browser_agent",
#             model=model,
#             instructions=instructions,
#             mcp_servers=[playWrightServer]
#         )

#         # Default prompt = normal assistant
#         prompt = user_input

#         # -------------------------
#         # FORM FILL LOGIC
#         # -------------------------
#         if wants_form_fill(user_input):
#             form_task = build_form_instruction()
#             if tab_url:
#                 prompt = f"Go to {tab_url}. Then: {form_task}"
#             else:
#                 prompt = form_task

#         # -------------------------
#         # SUMMARIZATION LOGIC
#         # -------------------------
#         elif wants_summarize(user_input) and tab_url:
#             prompt = (
#                 f"Go to {tab_url}. "
#                 f"Read the entire webpage. Extract ONLY the main readable content. "
#                 f"Ignore ads, headers, sidebars, comments, navigation, and popups. "
#                 f"Then provide a clean, well-structured summary. "
#                 f"Finally include this text at the bottom: 'Source: {tab_url}'"
#             )

#         # -------------------------
#         # BROWSER ACTION (NON-SUMMARY)
#         # -------------------------
#         elif tab_url:
#             prompt = f"Go to {tab_url} and {user_input}"

#         # Run agent through Runner
#         response = await Runner.run(
#             starting_agent=browser_agent,
#             input=prompt
#         )


#         return response.final_output


# # ==============================
# # DEBUG RUN (CLI)
# # ==============================
# async def main():
#     tab_url = input("Enter URL (optional): ").strip() or None
#     text = input("Say something: ").strip()
#     result = await browser_controller(tab_url, text)
#     print("\nResponse:\n", result)

# if __name__ == "__main__":
#     asyncio.run(main())



# agent.py
from dotenv import load_dotenv
import os
import asyncio
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.mcp import MCPServerStdio
from config import playWright_MCP_params
from userProfile import user_profile

load_dotenv(override=True)

MODEL_URL = os.getenv('GEMINI_API_URL')
MODEL_KEY = os.getenv('GEMINI_API_KEY')
MODEL_NAME = os.getenv('GEMINI_MODEL_NAME')

# Model initialization
model_client = AsyncOpenAI(base_url=MODEL_URL, api_key=MODEL_KEY)
model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=model_client)

# ==============================
# UPDATED SYSTEM INSTRUCTIONS
# ==============================
instructions = f"""
You are a MULTI-PURPOSE AI AGENT with three roles:

1. **Normal AI Assistant**
   - Answer general knowledge questions, coding, math, science, history, etc.
   - Explain concepts clearly and directly.

2. **Smart Web Summarizer (via Playwright MCP)**
   - When asked to summarize a webpage:
     - Navigate to the provided URL.
     - Extract main readable content.
     - Ignore ads, navigation bars, footers, popups.
     - Summarize concisely and include URL at the end.

3. **Form Filling Automation Agent**
   - Fill browser forms using ONLY the stored profile.
   - NEVER ask the user for info that exists in the profile.
   - Fill every visible field.
   - Do NOT click submit unless user explicitly says "submit".
   - Use this exact profile:

{user_profile}

Behavior Rules:
- Only use MCP server when performing browser actions, summarization, or form filling.
- Otherwise, respond directly as a normal AI assistant.
- Avoid phrases like "As an AI model"; just answer directly.
"""

# ==============================
# USER INTENT DETECTION
# ==============================
def wants_form_fill(text: str) -> bool:
    keywords = [
        "fill the form", "fill this form", "fill form",
        "auto fill", "autofill", "complete form",
        "enter my details", "register me",
        "sign me up", "create account", "apply for",
        "apply now", "sign up for me"
    ]
    t = text.lower()
    return any(k in t for k in keywords)


def wants_summarize(text: str) -> bool:
    keywords = ["summarize", "summary", "brief", "tl;dr", "short summary"]
    t = text.lower()
    return any(k in t for k in keywords)

# ==============================
# BUILD FORM INSTRUCTIONS
# ==============================
def build_form_instruction():
    lines = ["Fill every visible form field using ONLY this profile data:\n"]
    for key, value in user_profile.items():
        lines.append(f"{key}: {value}")

    lines.append("\nIMPORTANT RULES:")
    lines.append("- Do NOT ask the user for additional information.")
    lines.append("- Do NOT skip any field.")
    lines.append("- Do NOT click submit unless the user explicitly requests.")
    return "\n".join(lines)

# ==============================
# MAIN CONTROLLER
# ==============================
async def browser_controller(tab_url: str = None, user_input: str = None):
    if not user_input:
        raise ValueError("user_input cannot be empty")

    # Decide if MCP is needed
    use_mcp = wants_form_fill(user_input) or wants_summarize(user_input) or tab_url is not None

    async with MCPServerStdio(
        params=playWright_MCP_params,
        client_session_timeout_seconds=0
    ) as playWrightServer:

        mcp_servers = [playWrightServer] if use_mcp else []

        browser_agent = Agent(
            name="browser_agent",
            model=model,
            instructions=instructions,
            mcp_servers=mcp_servers
        )

        prompt = user_input

        # -------------------------
        # FORM FILL LOGIC
        # -------------------------
        if wants_form_fill(user_input):
            form_task = build_form_instruction()
            if tab_url:
                prompt = f"Go to {tab_url}. Then: {form_task}"
            else:
                prompt = form_task

        # -------------------------
        # SUMMARIZATION LOGIC
        # -------------------------
        elif wants_summarize(user_input) and tab_url:
            prompt = (
                f"Go to {tab_url}. "
                f"Read the entire webpage. Extract ONLY the main readable content. "
                f"Ignore ads, headers, sidebars, comments, navigation, and popups. "
                f"Then provide a clean, well-structured summary. "
                f"Finally include this text at the bottom: 'Source: {tab_url}'"
            )

        # -------------------------
        # BROWSER ACTION (NON-SUMMARY)
        # -------------------------
        elif tab_url:
            prompt = f"Go to {tab_url} and {user_input}"

        # -------------------------
        # NORMAL ASSISTANT (no MCP)
        # -------------------------
        # if use_mcp is False, it will answer normal questions

        response = await Runner.run(
            starting_agent=browser_agent,
            input=prompt
        )

        return response.final_output

# ==============================
# DEBUG RUN (CLI)
# ==============================
async def main():
    tab_url = input("Enter URL (optional): ").strip() or None
    text = input("Say something: ").strip()
    result = await browser_controller(tab_url, text)
    print("\nResponse:\n", result)

if __name__ == "__main__":
    asyncio.run(main())
