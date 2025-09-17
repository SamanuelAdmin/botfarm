import os

import cv2
import pytesseract



class TextRecognizer:
    def __init__(self, dataPath=None):
        if __name__ == "__main__": baseTesseractDataFolder = os.getcwd()
        else: baseTesseractDataFolder = os.path.dirname(__file__)
        baseTesseractDataFolder = os.path.join(baseTesseractDataFolder, 'data')

        self.tesseractDataFolder = dataPath if dataPath else baseTesseractDataFolder

        self._configs = r'--tessdata-dir "{}"'.format(baseTesseractDataFolder)

    def _reformat_pytesseract_data(self, data: dict[str, list]) -> dict[str, list[int]]:
        result: dict[str, list[int]] = {}

        for ind, box in enumerate(data['level']):
            if data['text'][ind] != '':
                result.update(
                    {
                        data['text'][ind]: (data['left'][ind], data['top'][ind], data['width'][ind],
                                            data['height'][ind])
                    }
                )

        return result

    def recognize(self, image) -> dict[str, list[int]]:
        return self._reformat_pytesseract_data(
            pytesseract.image_to_data(
                image, output_type='dict',
                config=self._configs
            )
        )

    def show_recognized(self, image, data: dict[str, list[int]]):
        for word, cords in data.items():
            cv2.rectangle(image, (cords[0], cords[1]), (cords[0] + cords[2], cords[1] + cords[3]), (0, 0, 200), 1)
            image = cv2.putText(image, word, (cords[0], cords[1]), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 0, 255), 1, cv2.LINE_AA)

        return image