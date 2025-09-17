import json
import os
import sys
import uuid
from typing import Any, Optional
from dataclasses import dataclass, field



@dataclass
class HistoryRecord:
    role: str = field(default="", init=False)
    content: str

    @property
    def to_OpenAi(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
        }

    def __str__(self):
        return '\n'.join([f'{k}: {v}' for k, v in self.__dict__.items()])


class SystemRecord(HistoryRecord):
    role: str = "system"
    content: str

class UserRecord(HistoryRecord):
    role: str = "user"
    content: str


class AssistantRecord(HistoryRecord):
    role: str = "assistant"
    content: Optional[str] = None
    call_id: str = ""
    function_name: str = ""
    args: dict[str, Any] | str = {}

    def __init__(self,
        call_id: str="", function_name: str="",
        args: dict[str, Any] | str = {},
        content: Optional[str] = None
    ):
        self.call_id = call_id
        self.function_name = function_name
        self.args = args
        self.content = content or ""


    @property
    def to_OpenAi(self):
        result: dict[str, Any] = {
            "role": "assistant",
        }

        if self.content:
            result["content"] = self.content
        else:
            result["tool_calls"] = [
                {
                    "id": self.call_id,
                    "type": "function",
                    "function": {
                        "name": self.function_name,
                        "arguments": json.dumps(self.args) if type(self.args) != str else self.args
                    }
                }
            ]

        return result


@dataclass
class ToolDataScheme:
    last_action_status: str
    last_function_name: str
    last_function_args: dict[str, Any]
    screen_dump: str

    def toJson(self):
        return json.loads(
            json.dumps(self.__dict__)
        )


class ToolRecord(HistoryRecord):
    role: str = "tool"
    content: ToolDataScheme
    tool_call_id: str

    # the solution for TypeError: HistoryRecord.__init__() got an unexpected keyword argument 'tool_call_id'
    def __init__(self, tool_call_id: str, data: ToolDataScheme):
        self.content = data
        self.tool_call_id = tool_call_id

    @property
    def to_OpenAi(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "content": json.dumps(self.content),
            "tool_call_id": self.tool_call_id
        }





class HistoryQueue:
    def __init__(self,
                 systemMessage: str='You are control manager for phones farm',
                 messagesLimit: int=30, logFile=None
            ):
        self._history: list[HistoryRecord] = []
        self._systemMessage: str = systemMessage
        self._messagesLimit: int = abs(messagesLimit)

        self.logsFullpath: str = None
        if __name__ != "__main__":
            self.logFile = logFile if logFile else uuid.uuid1().hex + '.json'
            filedir = os.path.join(os.getcwd(), 'history')
            if not os.path.exists(filedir): os.mkdir(filedir)

            self.logsFullpath = os.path.join(filedir, self.logFile)
            print(f'Path lo logs file: {self.logsFullpath}')

        self.updateHistory(
            SystemRecord( content=self._systemMessage )
        )


    def updateHistory(self, data: HistoryRecord):
        if len(self._history) >= self._messagesLimit:
            # SYSTEM RECORD PROTECTION! DO NOT TOUCH!
            self._history.pop(1)
        self._history.append(data)

        if self.logsFullpath: self.saveHistory()

    def saveHistory(self):
        if not self.logsFullpath: return

        with open(self.logsFullpath, 'w') as logfile:
            logfile.write(json.dumps(self.convertHistoryToOpenAI()))

    @property
    def history(self): return self._history

    def convertHistoryToOpenAI(self) -> list[dict[str, Any]]:
        return [record.to_OpenAi for record in self._history]
