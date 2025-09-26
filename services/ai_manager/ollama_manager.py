from typing import Optional
from datetime import datetime

from ollama import Client
from ollama import ResponseError as OllamaResponseError



class OllamaManager:
    def __init__(self, host: str='http://localhost', port: int = 11434):
        self._client = Client(
            host=f'{host}:{port}',
        )


    def _systemLog(self, *logs):
        currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{currentTime}', *logs)


    def createModel(self, newModelName: str, fromModelName: str, instructions: str) -> bool:
        for log in self._client.create(
            model=newModelName,
            # quantize='q4_K_M',
            system=instructions,
            from_=fromModelName
        ):
            self._systemLog(
                'Creating ', newModelName, '...  ', log
            )

        return True


    def request(self, modelName: str, text: str, instruction: Optional[str]=None) -> tuple[bool, str]:
        try:
            genResponse = self._client.generate(modelName, prompt=text, system=instruction, think=False)
            return True, genResponse.response
        except OllamaResponseError as error:
            return False, str(error)



if __name__ == '__main__':
    om = OllamaManager(host='http://109.87.156.203', port=28901)
    status, response = om.request(
            'deepseek-r1:8b',
                'Generate 30 lines only.',
                '''You are an Instagram profile generator. Generate exactly 100 unique user profiles, each on a single line in the exact format USERNAME - FULLNAME - BIO. The FULLNAME must always be a real Italian first name and surname such as Chiara Ferri, Marco Bianchi, or Luca Romano with no emojis, special symbols, or extra characters. The USERNAME must never be just the fullname or only the name and surname; it must always include at least one extra element such as a hobby, profession, passion, random word, numbers, underscore _ or dot .. Usernames must look like realistic Instagram handles, be lowercase, unique, contain no spaces or emojis, and must not exceed 24 characters. Examples include chiara.art92, marco_travel21, bianchi.music_88. The BIO must be written only in Italian, be informal, playful, and non-formal, between 10 and 25 words, and may include casual phrases like “sempre in giro”, “caffè addict”, “amo viaggiare”, or “musica a palla”. The BIO may include zero, one, or two emojis, but never more, and never in the fullname or username. The output must contain exactly 100 different profiles with no explanations, no numbering, no extra text, no headings, and nothing outside the specified format.'''
            )
    if status:
        for line in response.split('\n'):
            try:
                username, name, *_ = line.split(' - ')
                bio = ' - '.join(line.split(' - ')[2:])
                print(f'{username} : {name}  ->  {bio}')
            except ValueError: pass