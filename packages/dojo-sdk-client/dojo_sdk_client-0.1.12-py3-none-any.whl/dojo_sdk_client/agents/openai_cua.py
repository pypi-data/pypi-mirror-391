from dojo_sdk_core.types import Action
import openai
from PIL import Image
from .computer_use_tool import computer_tool


class OpenAICUA:
    def __init__(self, model: str, image_context_length: int = 10, verbose: bool = False):
        self.model = model
        self.image_context_length = image_context_length
        self.verbose = verbose

    def get_next_action(self, prompt: str, image: Image.Image, history: list) -> tuple[Action, str, str]:
        return Action(type="text", text=prompt), "Thinking", "Thinking"
