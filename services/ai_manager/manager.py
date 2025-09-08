import os

from groq import Groq
import json

from .history import *



class Manager:
    def __init__(self, apiKey=None, model='openai/gpt-oss-20b', systemPrompt=''):
        self._apiKey = apiKey
        self._client = Groq(
            api_key=self._apiKey,
        )
        self._model = model
        # and also adding system prompt (system description)
        self.historyQueue = HistoryQueue(
            systemMessage=systemPrompt,
            messagesLimit=10
        )


    def loadTools(self, filename='tools.json') -> dict:
        if __file__ != "__main__":
            filedir = os.path.dirname(__file__)
            filename = os.path.join(filedir, filename)

        with open( filename, 'r' ) as file:
            return json.loads(file.read())

    def addToolResponse(self, callId: str, data: ToolDataScheme) -> None:
        self.historyQueue.updateHistory(
            ToolRecord(
                callId, data
            )
        )

    def request(self, prompt: str):
        # create user prompt and add it to history
        currentUserPrompt = UserRecord(content=prompt)
        self.historyQueue.updateHistory(currentUserPrompt)

        history = self.historyQueue.convertHistoryToOpenAI()

        # noinspection PyTypeChecker
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=history,
            tools=self.loadTools(), # the result format for responses
            temperature=1,
            max_completion_tokens=8192,
            top_p=1,
            # reasoning_effort="default",
            stream=False,
            stop=None
        )

        # getting response and adding response to history
        response = completion.choices[0].message

        responseRecord = AssistantRecord(
                content=completion.choices[0].message.content
            ) if hasattr(completion.choices[0].message, 'content') else AssistantRecord(
                call_id = response.tool_calls[0].id,
                function_name = response.tool_calls[0].function.name,
                args=response.tool_calls[0].function.arguments
            )

        self.historyQueue.updateHistory(responseRecord)

        return response