from services.adb_manager import AdbManager, AdbClient, Dot
from services.parsers import ScreenDumpParser
from services.ai_manager import AiManager
from views import MainApp
import uvicorn
import json

from services.accounts_manager import AccountsManager
from services.insta_api.api_account_manager import ApiAccountManager


def actionScript(adb: AdbClient, ai: AiManager, action):
    currentScreenDump = adb.getScreenDump()
    dumpParser = ScreenDumpParser()
    parsedCurrentScreenDump = ''.join(
        [str(line) for line in dumpParser.parse(currentScreenDump)]
    )

    res = ai.request(
        f"Task: {action.upper()}.\n"
        "You are controlling an Android device. You MUST use ONLY the following tools:\n"
        "1) tap(x, y) — Tap a specific point on the screen. Use ONLY to press buttons, icons, or interact with visible UI elements.\n"
        "2) swipe(x1, y1, x2, y2) — Swipe from start to end coordinates. Use ONLY for scrolling or dragging.\n"
        "3) write(text) — Type text into the currently focused input field. Use ONLY after tapping a text field.\n"
        "4) done() — Indicate the task is fully completed or impossible. Use ONLY when there is nothing more to do.\n\n"
        "RULES:\n"
        "- Do NOT output raw JSON commands.\n"
        "- Do NOT write explanations or extra text.\n"
        "- Each step MUST call EXACTLY ONE tool from the list above with proper arguments.\n\n"
        + parsedCurrentScreenDump
    )

    if hasattr(res, 'tool_calls'):
        for toolCall in res.tool_calls:
            try: toolArgs = json.loads(toolCall.function.arguments)
            except: toolArgs = {}

            if toolCall.function.name == 'tap':
                actionDot = Dot(toolArgs.get('x'), toolArgs.get('y')).make_random()
                print( f'Tap ', actionDot, adb.tap( actionDot ) )

            elif toolCall.function.name == 'swipe':
                startDot = Dot(toolArgs.get('x1'), toolArgs.get('y1')).make_random()
                finishDot = Dot(toolArgs.get('x2'), toolArgs.get('y2')).make_random()
                print(f'Swipe from {startDot} to {finishDot}', adb.swipe(startDot, finishDot) )
            elif toolCall.function.name == 'write':
                adb.fastText(toolArgs.get('text'))
            elif toolCall.function.name == 'done':
                print('DONE')
            else:
                print(f'Got unexpected tool call {toolCall.function.name} with args {toolArgs}')
    else:
        print(f'AI response (text format): {res}')



def main():
    m = AdbManager('https://aa618b646034.ngrok-free.app')
    ai = AiManager(apiKey='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')
    adb = m.loadSerial('98896a374256375548')
    actionScript(
        adb, ai, 'open instagram site in browser'
    )
    # adb.tap(Dot(300, 600))


if __name__ == "__main__": main()
