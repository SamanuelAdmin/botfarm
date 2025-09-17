import os
from typing import Optional

import cv2
import json

if __name__ == '__main__':
    from helper import Helper
    from services.ui_recognizer.text import TextRecognizer
    from services.ui_recognizer.visual import VisualRecognizer
else:
    from .helper import Helper
    from services.ui_recognizer.text import TextRecognizer
    from services.ui_recognizer.visual import VisualRecognizer



class Main:
    def __init__(self, dataPath: Optional[str]=None) -> None:
        self.textRecognizer = TextRecognizer()
        self.visualRecognizer = VisualRecognizer()
        self.helper = Helper()

        if dataPath: self.dataPath = dataPath
        else:
            if __name__ == "__main__" and not dataPath:
                self.dataPath = os.getcwd()
            else:
                self.dataPath = os.path.dirname(
                    os.path.dirname(__file__)
                )

        self.dataPath = os.path.join(
            self.dataPath, "data"
        )
        self.visualSetPath = os.path.join(self.dataPath, "visual")



    def findTextOnImage(self, image, elements: list[str], lower=True) -> dict[str, list[int]]:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        result = {}

        # format elements and data
        data = {
            k.strip(): v for k, v in \
                self.textRecognizer.recognize(image).items()
        }
        elements = [
            el.strip() for el in elements
        ]

        if lower:
            data = { k.lower(): v for k, v in data.items() }
            elements = [e.lower() for e in elements]

        for element in elements:
            if data.get(element):
                result.update(
                    { element: data.get(element) }
                )

        return result


    def findTemplateOnImage(self, baseImage, templateName, baseSectorLen=5) -> list[int]|None:
        with open(os.path.join(self.dataPath, 'visual.json')) as file:
            templateJson = json.loads( file.read() )

        assert templateName in list(templateJson.keys())

        pathToTemplate = os.path.join(
            self.visualSetPath,
            templateJson[templateName]
        )

        baseTemplate = cv2.imread(pathToTemplate)
        template = self.visualRecognizer.loadImage( baseTemplate )
        image = self.visualRecognizer.loadImage( baseImage )

        match = self.visualRecognizer.compareImagesByKp(
            image, template
        )

        if match: return [match[0], match[1], baseSectorLen, baseSectorLen]

        return self.visualRecognizer.matchViaTemplate(baseImage, baseTemplate)


if __name__ == "__main__":
    main = Main()
    img = cv2.imread('test.jpg')

    foundedWords = main.findTextOnImage(img, ['edit', 'profile'])
    baseImg = main.textRecognizer.show_recognized(img, foundedWords)
    optionsButton = main.findTemplateOnImage(img, 'optionsButton')
    cv2.rectangle(baseImg, (optionsButton[0], optionsButton[1]), (optionsButton[0] + optionsButton[2], optionsButton[1] + optionsButton[3]), (0, 0, 255), 2)
    main.helper.show_image(baseImg)