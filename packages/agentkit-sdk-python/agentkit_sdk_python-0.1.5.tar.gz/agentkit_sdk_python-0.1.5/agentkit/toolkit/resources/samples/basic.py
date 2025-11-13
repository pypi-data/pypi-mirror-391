'''
**simple agent demo app**

Before running, the user must set the following environment variables; otherwise, runtime exceptions will inevitably occur:
- MODEL_AGENT_NAME  # model id in Volcano Engine Ark platform
- MODEL_AGENT_API_KEY  # model api key in Volcano Engine Ark platform

MODEL_AGENT_NAME and MODEL_AGENT_API_KEY are used to access the model service of the Volcano Engine Ark platform.
'''
import logging

from veadk import Agent, Runner

from agentkit.apps import AgentkitSimpleApp
from veadk.prompts.agent_default_prompt import DEFAULT_DESCRIPTION, DEFAULT_INSTRUCTION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


app = AgentkitSimpleApp()

agent_name = "{{ agent_name | default('Agent') }}"
{% if description %}description = "{{ description }}" {% else %}description = DEFAULT_DESCRIPTION {% endif %}
{% if system_prompt %}system_prompt = "{{ system_prompt }}" {% else %}system_prompt = DEFAULT_INSTRUCTION {% endif %}
model_name = "{{ model_name | default('doubao-seed-1-6-250615') }}"

tools = []
{% if tools %}
{% if 'web_search' in tools %}
from veadk.tools.builtin_tools.web_search import web_search
tools.append(web_search)
{% endif %}
{% if 'run_code' in tools %}
from veadk.tools.builtin_tools.run_code import run_code
tools.append(run_code)
{% endif %}
{% if 'get_weather' in tools %}
# from veadk.tools.builtin_tools.get_weather import get_weather
# tools.append(get_weather)
{% endif %}
{% else %}
# from veadk.tools.builtin_tools.web_search import web_search
# tools.append(web_search)
{% endif %}

agent = Agent(
    name=agent_name,
    description=description,
    instruction=system_prompt,
    model_name=model_name,
    tools=tools,
)
runner = Runner(agent=agent)


@app.entrypoint
async def run(payload: dict, headers: dict) -> str:
    prompt = payload["prompt"]
    user_id = headers["user_id"]
    session_id = headers["session_id"]

    logger.info(
        f"Running agent with prompt: {prompt}, user_id: {user_id}, session_id: {session_id}"
    )
    response = await runner.run(messages=prompt, user_id=user_id, session_id=session_id)

    logger.info(f"Run response: {response}")
    return response


@app.ping
def ping() -> str:
    return "pong!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

