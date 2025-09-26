from typing import Tuple
import json

from services.adb_manager import AdbClient, Dot
from services.parsers import ScreenDumpParser
from services.ai_manager import AiManager, ToolDataScheme



SYSTEM_PROMPT = '''You are an AI agent controlling an Android device. Follow these instructions STRICTLY:
TOOLS:
1) tap(x, y) — Tap a specific point on the screen. Use ONLY on visible buttons, icons, or interactable UI elements.
2) swipe(x1, y1, x2, y2) — Swipe from start to end coordinates. Use ONLY for scrolling or dragging.
3) write(text) — Type text into the currently focused input field. Use ONLY after tapping a text field.
4) done() — Indicate the task is fully completed or impossible. Use ONLY when no further actions are possible.
RULES:
- ALWAYS output EXACTLY ONE tool call per step.
- NEVER write raw JSON commands outside the tool call structure.
- NEVER add explanations, comments, or extra text.
- Each tool call MUST include all required arguments correctly.
- Act only based on visible UI elements and previous tool_call results.
- After executing a tool_call, you will receive a screen dump as a tool response. Use this new screen state to decide the next step.
- Continue performing steps until the task is completed or impossible. Only use done() when truly finished.
'''


def analyzeResponse(adb, response, fake=False) -> Tuple[bool, str, dict]:
    if not hasattr(response, 'tool_calls'):
        print(f'AI response (text format): {response}')
        return False, "", {}

    toolCall = response.tool_calls[0]

    try: toolArgs = json.loads(toolCall.function.arguments)
    except json.JSONDecodeError:
        toolArgs = {}
        print("Warning: Failed to parse tool arguments")

    def makeAction() -> bool:
        if toolCall.function.name == 'tap':
            actionDot = Dot(toolArgs.get('x'), toolArgs.get('y')).make_random()
            return adb.tap(actionDot)

        elif toolCall.function.name == 'swipe':
            startDot = Dot(toolArgs.get('x1'), toolArgs.get('y1')).make_random()
            finishDot = Dot(toolArgs.get('x2'), toolArgs.get('y2')).make_random()
            return adb.swipe(startDot, finishDot)

        elif toolCall.function.name == 'write':
            return adb.fastText(toolArgs.get('text'))

        elif toolCall.function.name == 'done':
            return True
        else: return False

    result = (True, toolCall.function.name, toolArgs) if fake \
        else (makeAction(), toolCall.function.name, toolArgs)
    print(f'[{result[1]} -> {result[0]}] {result[2]}')
    return result


def getOptScreenDump(adb: AdbClient) -> str:
    currentScreenDump = adb.getScreenDump()
    dumpParser = ScreenDumpParser()
    return ''.join(
        [str(line) for line in dumpParser.parse(currentScreenDump)]
    )

def action(adb: AdbClient, ai: AiManager, action):
    optimizeScreenDump = getOptScreenDump(adb)

    startPrompt = f'TASK: {action}\nSCREEN DUMP: {optimizeScreenDump}'
    workingPrompt = f'TASK: {action}'

    res = ai.request(startPrompt)

    # do an action
    last_action_status, last_function_name, last_function_args = analyzeResponse(adb, res, fake=True)

    # getting current screen dump (after actions)
    optimizeScreenDump = getOptScreenDump(adb)

    # and adding current state as tool response
    ai.addToolResponse(
        res.tool_calls[0].id,
        ToolDataScheme(
            last_action_status=last_action_status,
            last_function_name=last_function_name,
            last_function_args=last_function_args,
            screen_dump=optimizeScreenDump
        ).toJson()
    )

    while True:
        input('Wait for confirmation')
        res = ai.request(workingPrompt)
        last_action_status, last_function_name, last_function_args = analyzeResponse(adb, res, fake=True)
        # getting current screen dump (after actions)
        optimizeScreenDump = getOptScreenDump(adb)

        # and adding current state as tool response
        ai.addToolResponse(
            res.tool_calls[0].id,
            ToolDataScheme(
                last_action_status=last_action_status,
                last_function_name=last_function_name,
                last_function_args=last_function_args,
                screen_dump=optimizeScreenDump
            ).toJson()
        )

        if last_function_name == 'done': break