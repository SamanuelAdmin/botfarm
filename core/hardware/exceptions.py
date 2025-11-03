from typing import Any


class IncorrectStatusCodeException(Exception):
    def __init__(self, statusCode, url: str=None):
        self.statusCode = statusCode
        self.url = url

    def __str__(self):
        return f'Incorrect status code: {self.statusCode}. ' \
               + f' URL: {self.url}' if self.url else ''

class ResultNotFoundException(Exception):
    def __init__(self, json: dict[Any, Any]=None):
        self.json = json

    def __str__(self):
        return f'Result not found in {self.json}'


class IncorrectStatusException(Exception):
    def __init__(self, json):
        self.json = json

    def __str__(self):
        return f'Got incorrect status: {self.json.get("status")}. \nJSON: \n{self.json}'


class FileDownloadException(Exception):
    def __init__(self, filePath: str):
        self.filePath = filePath

    def __str__(self):
        return f'Error downloading file: {self.filePath}'

