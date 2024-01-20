import cv2
import numpy as np
from transformers import pipeline

pipe = pipeline("image-to-text", model="microsoft/trocr-large-printed")

class CaptchaSolver:
    def __init__(self, image_path):
        self.image = cv2.imread(image_path)
        self.kernel = np.ones((2, 2), np.uint8)

    def enhance_legibility(self, cropped_image):
        gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return cv2.erode(cv2.blur(mask, (2, 2)), self.kernel, iterations=1)

    def math_operation(self, left_number, right_number, operation='+'):
        if left_number.isdigit() and right_number.isdigit():
            return eval(f"{left_number} {operation} {right_number}")
        else:
            return None
    def math_operation_for_both_signs(self, left_number, right_number):
        if left_number.isdigit() and right_number.isdigit():
            left_number = int(left_number)
            right_number = int(right_number)
            return [left_number - right_number, left_number + right_number]
        else:
            return None
    def resolve(self, left_image, right_image, sign_image, negative_sign_right_image):
        sign = pipe(sign_image)[0]['generated_text']
        left_number = pipe(left_image)[0]['generated_text']
        
        if sign in {'+', '@', '4','*'}:
            right_number = pipe(right_image)[0]['generated_text']
            return self.math_operation(left_number, right_number)
        elif sign in {'-', '='}:
            right_number = pipe(negative_sign_right_image)[0]['generated_text']
            return self.math_operation(left_number, right_number, '-')
        else:
            unfixed_right_number = ''.join(char for char in pipe(right_image)[0]['generated_text'] if char.isdigit())
            return self.math_operation_for_both_signs(left_number, unfixed_right_number)

    def solve_captcha(self):
        positions = {'left': 5, 'right': 60, 'sign': 39, 'negative_sign_right': 56}
        dimensions = {'width': 25, 'height': 20, 'width_sign': 15, 'height_sign': 15, 'width_negative_sign': 18}
        
        left_image = self.image[7:27, positions['left']:positions['left']+dimensions['width']]
        right_image = self.image[7:27, positions['right']:positions['right']+dimensions['width']]
        sign_image = self.image[10:25, positions['sign']:positions['sign']+dimensions['width_sign']]
        negative_sign_right_image = self.image[7:27, positions['negative_sign_right']:positions['negative_sign_right']+dimensions['width_negative_sign']]
        
        left_enhanced = self.enhance_legibility(left_image)
        right_enhanced = self.enhance_legibility(right_image)
        negative_sign_right_enhanced = self.enhance_legibility(negative_sign_right_image)

        cv2.imwrite('left_number.jpg', left_enhanced)
        cv2.imwrite('right_number.jpg', right_enhanced)
        cv2.imwrite('sign.jpg', sign_image)
        cv2.imwrite('negative_sign_right_number.jpg', negative_sign_right_enhanced)

        return self.resolve('left_number.jpg', 'right_number.jpg', 'sign.jpg', 'negative_sign_right_number.jpg')