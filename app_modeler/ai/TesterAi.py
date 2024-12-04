import json
import logging

import openai

from app_modeler.ai.OpenAiAssistant import OpenAIAssistant
from app_modeler.models.FunctionCall import NextFunctionList, FunctionCall

logger = logging.getLogger(__name__)


class TesterAi:
    def __init__(self, ai_assistant: OpenAIAssistant, prompt_template: str = None):
        self.ai = ai_assistant
        self.prompt_template = prompt_template

    def ask_next_step(self, class_docstring: [dict], previous_steps: [str]) -> [FunctionCall]:
        prompt =self.prompt_template.format(previous_steps=json.dumps(previous_steps),
                                            class_docstring=json.dumps(class_docstring))
        try:
            response: NextFunctionList = self.ai.ask(prompt=prompt, response_format=NextFunctionList)
        except openai.BadRequestError as error:
            logger.error(error.message)
            raise StopIteration("openAI fails to provide the next step")
        dump = response.model_dump()
        return [FunctionCall(**step) for step in dump['candidates']]
