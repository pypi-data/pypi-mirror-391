import json
import logging

from google.adk.agents import RunConfig
from google.adk.agents.run_config import StreamingMode
from google.genai.types import Content, Part
from veadk import Agent, Runner

from agentkit.apps import AgentkitSimpleApp
from veadk.prompts.agent_default_prompt import DEFAULT_DESCRIPTION, DEFAULT_INSTRUCTION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = AgentkitSimpleApp()

app_name = "simple_streamable_app"

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
agent.model._additional_args["stream_options"] = {"include_usage": True}
runner = Runner(agent=agent, app_name=app_name)


@app.entrypoint
async def run(payload: dict, headers: dict):
    prompt = payload["prompt"]
    user_id = headers["user_id"]
    session_id = headers["session_id"]

    logger.info(
        f"Running agent with prompt: {prompt}, user_id: {user_id}, session_id: {session_id}"
    )

    session_service = runner.short_term_memory.session_service  # type: ignore

    # prevent session recreation
    session = await session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    if not session:
        await session_service.create_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

    new_message = Content(role="user", parts=[Part(text=prompt)])
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        ):
            # Format as SSE data
            sse_event = event.model_dump_json(exclude_none=True, by_alias=True)
            logger.debug("Generated event in agent run streaming: %s", sse_event)
            yield f"data: {sse_event}\n\n"
    except Exception as e:
        logger.exception("Error in event_generator: %s", e)
        # You might want to yield an error event here
        error_data = json.dumps({"error": str(e)})
        yield f'data: {error_data}\n\n'


@app.ping
def ping() -> str:
    return "pong!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
