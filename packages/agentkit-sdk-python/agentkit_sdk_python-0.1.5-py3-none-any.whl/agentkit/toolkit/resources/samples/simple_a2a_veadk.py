import logging

from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor
from veadk import Agent, Runner
from veadk.a2a.agent_card import get_agent_card
from veadk.tools.demo_tools import get_city_weather

from agentkit.apps import AgentkitA2aApp

logger = logging.getLogger(__name__)


a2a_app = AgentkitA2aApp()

app_name = "weather_reporter"
agent = Agent(tools=[get_city_weather])
runner = Runner(agent=agent)


@a2a_app.agent_executor(runner=runner)
class MyAgentExecutor(A2aAgentExecutor):
    """Use Google ADK A2aAgentExecutor directly."""

    pass


if __name__ == "__main__":
    a2a_app.run(
        agent_card=get_agent_card(agent=agent, url="http://0.0.0.0:8000"),
        host="0.0.0.0",
        port=8000,
    )
