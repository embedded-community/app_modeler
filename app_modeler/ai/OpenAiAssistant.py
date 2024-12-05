import abc

import openai
import logging
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class AiModel(BaseModel, abc.ABC):
    pass


class OpenAIAssistant:
    def __init__(self, api_key: str, base_url: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the OpenAIAssistant with an API token.
        :param api_key: OpenAI API mey.
        """
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self._default_model = model or "gpt-4o-mini"
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        self.used_tokens = 0

    def ask(self,
            prompt: str,
            response_format: AiModel,
            model: Optional[str] = None) -> AiModel:
        """
        Ask the assistant a question, and store the prompt and response in memory.
        :param prompt: The prompt/question to ask the assistant.
        :param response_format: pydantic model to ensure the response format.
        :return: The response from the assistant in JSON format.
        """
        full_prompt = self._create_full_prompt(response_format, prompt)

        logger.debug(f"prompt: {full_prompt}, full_prompt: {full_prompt}")

        completion = self.client.beta.chat.completions.parse(
            model=model or self._default_model,
            messages=[{"role": "user", "content": full_prompt}],
            response_format=response_format
        )
        response = completion.choices[0].message.parsed
        self.used_tokens += completion.usage.total_tokens


        logger.debug(f'AI response (tokens: {self.used_tokens}): {response}')
        response = response

        if response_format.__name__ not in self.conversation_history:
            self.conversation_history[response_format.__name__] = []
        history = self.conversation_history[response_format.__name__]
        history.append({"role": "assistant", "content": str(response)})

        return response

    def upload_image_and_prompt(self,
                                prompt: str,
                                base64_image: str,
                                response_format: any,
                                model: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a base64 encoded PNG image along with a prompt to the assistant.
        :param prompt: The prompt/question to ask the assistant.
        :param base64_image: The base64 encoded PNG image.
        :param response_format: Response class to ensure the response format.
        :return: The response from the assistant in JSON format.
        """

        full_prompt = self._create_full_prompt(prompt)

        logger.debug(f"prompt: {prompt}, full_prompt: {full_prompt}")

        completion = self.client.beta.chat.completions.parse(
            model=model or self._default_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                          "type": "text",
                           "text": full_prompt
                        },
                        {"type": "text",
                         "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
            response_format=response_format
        )
        response = completion.choices[0].message.parsed
        self.used_tokens += completion.usage.total_tokens

        logger.debug(f'AI response (tokens: {self.used_tokens}): {response}')

        if response_format.__name__ not in self.conversation_history:
            self.conversation_history[response_format.__name__] = []

        history = self.conversation_history[response_format.__name__]
        history.append({"role": "assistant", "content": response})
        history.append({"role": "assistant", "content": full_prompt})

        return response

    def _create_full_prompt(self, response_format, prompt: str) -> str:
        """
        Create a full prompt including the history perspective.
        :param prompt: The current prompt/question.
        :return: The full prompt including conversation history.
        """
        return prompt
        #history_perspective = "\n\nPrevious conversation history:\n"
        #if response_format.__name__ not in self.conversation_history:
        #    self.conversation_history[response_format.__name__] = []
        ##for message in self.conversation_history[response_format.__name__]:
        ##    history_perspective += f"{message['role']}: {message['content']}\n"
        #return history_perspective + "\nCurrent question:\n" + prompt

    def get_conversation_history(self, response_format) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        :return: The conversation history as a list of prompts and responses.
        """
        if response_format.__name__ not in self.conversation_history:
            self.conversation_history[response_format.__name__] = []
        return self.conversation_history[response_format.__name__]
