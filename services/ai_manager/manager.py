import os

from groq import Groq
import json



class Manager:
    def __init__(self, apiKey=None, model='openai/gpt-oss-20b'):
        self._apiKey = apiKey
        self._client = Groq(
            api_key=self._apiKey,
        )
        self._model = model

    def loadTools(self, filename='meta/tools.json'):
        with open( 'tools.json', 'r' ) as file:
            return json.loads(file.read())

    def request(self, prompt):
        # noinspection PyTypeChecker
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            tools=self.loadTools(), # the result format for responses
            temperature=1,
            max_completion_tokens=8192,
            top_p=1,
            # reasoning_effort="default",
            stream=False,
            stop=None
        )

        response = completion.choices[0].message
        return response