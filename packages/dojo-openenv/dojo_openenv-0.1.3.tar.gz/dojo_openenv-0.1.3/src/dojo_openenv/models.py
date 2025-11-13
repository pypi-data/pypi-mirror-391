from dojo_sdk_client.base_dojo_client import TaskResponse
from dojo_sdk_core.types import Action as DojoCoreAction
from openenv_core import Action, Observation
import PIL.Image


class DojoAction(Action):
    def __init__(self, action: DojoCoreAction, reasoning: str, raw_response: str):
        self.action = action
        self.reasoning = reasoning
        self.raw_response = raw_response


class DojoObservation(Observation):
    def __init__(self, task_response: TaskResponse, screenshot_image: PIL.Image.Image):
        self.task_response = task_response
        self.screenshot_image = screenshot_image
