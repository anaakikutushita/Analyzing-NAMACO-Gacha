# coding: utf-8
"""
スクリーンショットを読み込んで各種の必要な領域を保持する
"""

from abc import ABC
from pathlib import Path
import cv2

class AbstractScreenshot(ABC):
    def __init__(self):
        """ガチャ結果の判定に必要な各種領域を定義"""
        pass
