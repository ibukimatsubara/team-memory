"""Detect circle symbols in drawing images."""
import cv2
import numpy as np


def binarize(gray: np.ndarray) -> np.ndarray:
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 5
    )


def detect_circles(path: str) -> list[tuple[int, int, int]]:
    gray = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    binary = binarize(gray)
    circles = cv2.HoughCircles(
        binary, cv2.HOUGH_GRADIENT, dp=1.2, minDist=12, param1=80, param2=18,
        minRadius=4, maxRadius=20,
    )
    if circles is None:
        return []
    return [tuple(int(v) for v in c) for c in circles[0]]
