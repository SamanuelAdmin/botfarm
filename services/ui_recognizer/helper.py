import copy
import math
import cv2
import numpy as np


class Helper:
    @classmethod
    def draw_rect_by_contour(cls, frame, cnt: tuple[int]):
        x, y, w, h = cv2.boundingRect(cnt)
        frame_out = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 200), 2)
        return frame_out, (x, y, x + w, y + h, w, h)


    @classmethod
    def show_image(cls, image, name='Image'):
        cv2.imshow(name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @classmethod
    def get_distance_between_rect(cls, cnt1, cnt2, xk=1, yk=0.5):
        rect1 = cv2.boundingRect(cnt1) # x, y, w, h
        rect2 = cv2.boundingRect(cnt2)

        center1 = (rect1[0] + rect1[2]/2, rect1[1] + rect1[3]/2)
        center2 = (rect2[0] + rect2[2]/2, rect2[1] + rect2[3]/2)
        distance = math.sqrt( ( abs(center1[0] - center2[0])*xk )**2 + ( abs(center1[1] - center2[1])*yk )**2)

        return  distance


    @classmethod
    def merge_contours(cls, cnt1, cnt2):
        return np.vstack((cnt1, cnt2)).reshape(-1, 1, 2)


    @classmethod
    def merge_close_contours(cls, contours):
        contours = list(contours)
        newContours = []

        while len(contours) > 0:
            currentContour = contours.pop(0)
            lastContour = copy.deepcopy(currentContour)

            i = 0
            while i < len(contours):
                if cls.get_distance_between_rect(currentContour, contours[i]) < 15:
                    currentContour = cls.merge_contours(currentContour, contours[i])
                    contours.pop(i)
                    i = 0
                else:
                    i += 1

            newContours.append(currentContour)

        return newContours