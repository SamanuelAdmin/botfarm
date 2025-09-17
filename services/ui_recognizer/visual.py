import cv2


class VisualRecognizer:
    def __init__(self):
        self._akaze = cv2.AKAZE_create()
        self._bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    def getCountours(self, image, approxK=0.015):
        _, thresholded = cv2.threshold(
            image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        thresholded = cv2.bitwise_not(thresholded)
        contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        apprtoxContours = self.approxContours(contours, k=approxK)

        return apprtoxContours


    def approxContours(self, contours, k=0.015):
        approxContours = []

        for contour in contours:
            approxContours.append(
                cv2.approxPolyDP(contour, k * cv2.arcLength(contour, True), True)
            )

        return approxContours


    def loadImage(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    def getThresholdedImage(self, grayImage):
        _, thresholded = cv2.threshold(
            grayImage, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return cv2.bitwise_not(thresholded)  # white -> black, black -> white


    def compareImagesByKp(self, image, template) -> None|tuple[int]:
        kp1, des1 = self._akaze.detectAndCompute(image, None)
        kp2, des2 = self._akaze.detectAndCompute(template, None)

        if not all([len(kp1), len(kp2)]): return None

        matches = sorted(
            self._bf.match(des1, des2),
            key=lambda x: x.distance
        )

        # getting first matches
        match = matches[0]
        return kp1[match.queryIdx].pt



    def matchViaTemplate(self, image, template) -> None|list[int]:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        imageWidth, imageHeight = image.shape[::-1]

        scale = 0
        maxValue = 0
        dataToReturn: list[int] | list = []  # x, y, width, height

        for _ in range(0, 100):
            scale += 0.1

            resized = cv2.resize(
                template, (0, 0), fx=scale, fy=scale
            )
            if resized.shape[0] > imageHeight or resized.shape[1] > imageWidth:
                break

            res = cv2.matchTemplate(image, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val > maxValue:
                maxValue = max_val
                dataToReturn = [max_loc[0], max_loc[1], resized.shape[1], resized.shape[0]]

        return dataToReturn if dataToReturn else None


    def showDot(self, image, dot, thicknessAndRadius=2):
        cv2.circle(image, dot, thicknessAndRadius, thicknessAndRadius)
        return image