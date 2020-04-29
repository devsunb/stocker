import cv2
from PIL import Image


class CoupangKeypad:
    def __init__(self, keypad_ref_path_format):
        self.keypad_ref = []
        for i in range(10):
            self.keypad_ref.append(cv2.imread(keypad_ref_path_format.format(i), cv2.IMREAD_GRAYSCALE))

    def get_positions(self, screenshot_path, keypad_start=(509, 300), keypad_size=(250, 400),
                      keypad_positions=(
                              (0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2), (3, 1))):
        positions = []
        cropped = CoupangKeypad.crop_keys(screenshot_path, keypad_start, keypad_size, keypad_positions)
        for img in cropped:
            positions.append(self.check_keypad(img))
        return positions

    @staticmethod
    def save_keys(screenshot_path, keypad_start=(509, 300), keypad_size=(250, 400),
                  keypad_positions=((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2), (3, 1))):
        cropped = CoupangKeypad.crop_keys(screenshot_path, keypad_start, keypad_size, keypad_positions)
        for i, img in enumerate(cropped):
            Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).save('{}.png'.format(i))

    @staticmethod
    def crop_keys(screenshot_path, keypad_start=(509, 300), keypad_size=(250, 400),
                  keypad_positions=((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2), (3, 1))):
        cropped = []
        keypad_num = (max([y for y, x in keypad_positions]) + 1, max([x for y, x in keypad_positions]) + 1)
        img = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
        keypad = img[keypad_start[0]:keypad_start[0] + keypad_size[0], keypad_start[1]:keypad_start[1] + keypad_size[1]]
        for y, x in keypad_positions:
            y_area = slice(round((keypad_size[0] / keypad_num[0]) * y),
                           round((keypad_size[0] / keypad_num[0]) * (y + 1)))
            x_area = slice(round((keypad_size[1] / keypad_num[1]) * x),
                           round((keypad_size[1] / keypad_num[1]) * (x + 1)))
            cropped.append(keypad[y_area, x_area])
        return cropped

    def check_keypad(self, img):
        match_result = []
        for i, ref in enumerate(self.keypad_ref):
            res = cv2.matchTemplate(img, ref, cv2.TM_SQDIFF)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            match_result.append(min_val)
        return match_result.index(min(match_result))
