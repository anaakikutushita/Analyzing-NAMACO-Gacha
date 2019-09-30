# coding: utf-8
"""
Screenshotクラスを受け取って、そのガチャ結果が何なのかを判定する
"""

import uuid
import numpy as np
from pathlib import Path
import cv2
import GachaResults

class Detecter():
    def __init__(self):
        self._target_rois_first_category = set(
            Comparer(Roi(287, 369, 597, 677), Path('model_images/cash_center.png')),
            Comparer(Roi(302, 366, 581, 655), Path('model_images/food_exp15.png')),
            Comparer(Roi(302, 366, 581, 655), Path('model_images/food_exp20.png')),
            Comparer(Roi(302, 366, 581, 655), Path('model_images/food_exp25.png')),
            Comparer(Roi(302, 366, 581, 655), Path('model_images/food_cash15.png')),
            Comparer(Roi(302, 366, 581, 655), Path('model_images/food_cash20.png')),
            Comparer(Roi(302, 366, 581, 655), Path('model_images/food_cash25.png'))
        )
        self._target_rois_cash_amount = set(
            Comparer(Roi(194, 225, 520, 614), Path('model_images/cash_4000.png')),
            Comparer(Roi(194, 225, 520, 614), Path('model_images/cash_8000.png')),
            Comparer(Roi(194, 225, 507, 626), Path('model_images/cash_20000.png')),
            Comparer(Roi(194, 225, 507, 626), Path('model_images/cash_40000.png'))
        )

    def detect(self, id, screenshot: np.ndarray):
        """ガチャ結果のスクショ画像を受け取って、ガチャ結果を辞書形式にして返す"""
        if not isinstance(screenshot, np.ndarray):
            raise TypeError('ガチャ結果の判定にはcv2.imreadで読み込んだMatオブジェクトを渡してください')

        result = GachaResults.SingleResult(id)
        if there_is_cash(screenshot):
            amount = detect_cash_amount(screenshot)
            result.gain_cash(amount)
            return result
        elif there_is_chunk(screenshot):
            chunk_type = detect_chunk_type(screenshot)
            amount = detect_chunk_num(screenshot)
            result.gain_chunk(chunk_type, amount)

        #中央におカネアイコンがあるか
        model_path = Path('model_images/cash_center.png')
        model_img = cv2.imread(str(model_path))
        model_hist = get_image_hist_vector(model_img)
        roi = Roi(287, 369, 597, 677)
        target_img = roi.crop(screenshot)
        target_hist = get_image_hist_vector(target_img)
        similarity = cv2.compareHist(target_hist, model_hist, 0)

        #中央にかけらアイコンがあるか
        model_path = Path('model_images/chunk_mpu.png')
        roi = Roi(287, 369, 597, 677)
        comparer = Comparer(roi, model_path)
        similar = comparer.is_similar(screenshot)
        roi = Roi(284, 377, 590, 684)
        target_img = roi.crop(screenshot)
        target_hist = get_image_hist_vector(target_img)
        similarity = cv2.compareHist(target_hist, model_hist, 0)

        #中央にフードチケットアイコンがあるか

        #中央にドリンクアイコンがあるか

        #ドリンク14種か

        #どれでもない場合

        return similarity

class Comparer():
    """入力画像の特定領域がモデル画像と似ているかどうかを判定する"""
    def __init__(self, target_roi, model_path: Path):
        if not isinstance(target_roi, Roi):
            raise TypeError('ComparerにはRoi型を渡してください')

        if not isinstance(model_path, Path):
            raise TypeError('ComparerにはPathを渡してください')
        elif not model_path.exists():
            raise FileNotFoundError('モデル画像のパスが存在しません')
        elif not model_path.is_file():
            raise TypeError('モデル画像に指定されたパスがファイルではありません')

        self._target_roi = target_roi
        model = cv2.imread(str(model_path))
        self._model_hist = self._get_image_hist_vector(model)

    def is_similar(self, screenshot: np.ndarray):
        if not isinstance(screenshot, np.ndarray):
            raise TypeError('Comparerにはnp.ndarrayを渡してください')

        target_img = self._target_roi.crop(screenshot)
        target_hist = self._get_image_hist_vector(target_img)

        compare_method = 0
        similarity = cv2.compareHist(target_hist, self._model_hist, compare_method)
        return similarity > 0.9

    def _get_image_hist_vector(self, target_image):
        """
        BGR三色を考慮したヒストグラムのベクトルを取得する。
        ベクトルどうしでcv2.compareHistが可能。
        """
        #binsはヒストグラム解析の解像度を示す指標。最も詳細に解析する場合は256でよい
        all_bins = [256]
        #rangeはヒストグラム解析の対象となる画素領域。最も詳細に解析する場合は[0,256]でよい
        all_ranges = [0, 256]

        mask = None

        hist_bgr = []
        #channelは0,1,2がそれぞれB,G,Rに相当。グレースケールの場合は0
        for channel in range(3):
            hist = cv2.calcHist([target_image], [channel], mask, all_bins, all_ranges)
            hist_bgr.append(hist)

        hist_array = np.array(hist_bgr)

        # hist_vecの計算方法はよくわからない。参考記事を写しただけ https://ensekitt.hatenablog.com/entry/2018/07/09/200000
        hist_vec = hist_array.reshape(hist_array.shape[0]*hist_array.shape[1], 1)
        return hist_vec

def get_image_hist_vector(target_image):
    """
    BGR三色を考慮したヒストグラムのベクトルを取得する。
    ベクトルどうしでcv2.compareHistが可能。
    """
    #binsはヒストグラム解析の解像度を示す指標。最も詳細に解析する場合は256でよい
    all_bins = [256]
    #rangeはヒストグラム解析の対象となる画素領域。最も詳細に解析する場合は[0,256]でよい
    all_ranges = [0, 256]

    mask = None

    hist_bgr = []
    #channelは0,1,2がそれぞれB,G,Rに相当。グレースケールの場合は0
    for channel in range(3):
        hist = cv2.calcHist([target_image], [channel], mask, all_bins, all_ranges)
        hist_bgr.append(hist)

    hist_array = np.array(hist_bgr)

    # hist_vecの計算方法はよくわからない。参考記事を写しただけ https://ensekitt.hatenablog.com/entry/2018/07/09/200000
    hist_vec = hist_array.reshape(hist_array.shape[0]*hist_array.shape[1], 1)
    return hist_vec

class Roi():
    def __init__(self, top, bottom, left, right):
        for elem in (top, bottom, left, right):
            if not isinstance(elem, int):
                raise TypeError('Roiにはintのtupleを渡してください')

        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def crop(self, img: np.ndarray):
        return img[self.top:self.bottom, self.left:self.right]

if __name__ == '__main__':
    target_path = Path('unit_tests/test_images/chunk_mpu.jpg')
    screenshot = cv2.imread(str(target_path))
    Detecter().detect(screenshot)
