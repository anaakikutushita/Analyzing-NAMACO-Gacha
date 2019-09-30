# coding: utf-8

from uuid import uuid4
from enum import Enum
from pathlib import Path
import cv2
import numpy as np

class ScreenshotScale():
    def __init__(self):
        self.width = 1280
        self.height = 720

class HorizontalAxisCoordinate():
    def __init__(self, value):
        max_val = ScreenshotScale().width
        minimum_val = 0
        if not is_within_range(value, minimum_val, max_val):
            raise ValueError("{value}が範囲外")
        self._value = value

class VerticalAxisCoordinate():
    def __init__(self, value):
        max_val = ScreenshotScale().height
        minimum_val = 0
        if not is_within_range(value, minimum_val, max_val):
            raise ValueError("{value}が範囲外")
        self._value = value

def is_within_range(value, minimum_val, max_val):
    return minimum_val <= value <= max_val

class ImageRegion():
    def __init__(self, left, right, top, bottom):
        if not (isinstance(left, HorizontalAxisCoordinate) and
                isinstance(right, HorizontalAxisCoordinate) and
                isinstance(top, VerticalAxisCoordinate) and
                isinstance(bottom, VerticalAxisCoordinate)):
            raise TypeError("AxixCoordinateを使っていない")

        if left >= right or top >= bottom:
            raise ValueError("画像範囲の左右もしくは上下が逆かも。または同じ値になっている")

        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

class Screenshot():
    def __init__(self, image: np.ndarray):
        if not isinstance(image, np.ndarray):
            raise TypeError("ndarrayでない")

        self._height, self._width = image.shape
        if self._height > ScreenshotScale().height:
            raise ValueError("画像の縦：{height}が規定より大きい")
        if self._width > ScreenshotScale().width:
            raise ValueError("画像の横：{width}が規定より大きい")

        self._image = image

    def crop(self, region):
        if not isinstance(region, ImageRegion):
            raise TypeError("クロップ指定領域がImageRegion型でない")

        crop_width = region.right - region.left
        if self._width < crop_width:
            raise ValueError("画像横幅：{self._width}よりも大きな横幅：{crop_width}でクロップしようとしている")

        crop_height = region.bottom - region.top
        if self._height < crop_height:
            raise ValueError("画像縦幅：{self._height}よりも大きな縦幅：{crop_height}でクロップしようとしている")

        cropped_image = self._image[region.top:region.bottom, region.left:region.right]
        return Screenshot(cropped_image)

class ScreenshotCollecter():
    def __init__(self):
        self._screenshots = set()

    def add(self, screenshot):
        if not isinstance(screenshot, Screenshot):
            raise TypeError('スクリーンショットの型が不正')

        self._screenshots.add(screenshot)

    def get_result_collection(self):
        collector = ResultCollector()
        for screenshot in self._screenshots:
            pass
        return ResultCollector()

class Extension(Enum):
    # BMP = 'bmp'
    JPG = '*.jpg'
    # PNG = 'png'
    # ALL = None #ALLは使わないほうが懸命かも（画像以外の拡張子を持つPathが混入するとめんどい）

class PathCollecter():
    """単一のディレクトリ内に存在するPathのコレクションを扱う"""
    def __init__(self, target_directory: Path, extension=Extension.JPG):
        if not isinstance(target_directory, Path):
            raise TypeError('ディレクトリ{target_directory}がPathでない')

        if not isinstance(extension, Extension):
            raise TypeError('extension{Extension}の型がExtensionでない')

        if not target_directory.exists():
            raise ValueError('ディレクトリ{target_directory}が存在しない')

        if not target_directory.is_dir():
            raise ValueError('ディレクトリ{target_directory}がファイルを指している')

        self._path_collection = set(target_directory.glob(extension))

    def get_screenshots(self):
        """ScreenshotCollecterを返す"""
        collecter = ScreenshotCollecter()
        while self._path_collection:
            image = cv2.imread(self._path_collection.pop())
            screenshot = Screenshot(image)
            collecter.add(screenshot)

        return collecter

class DrinkTicketQuantity():
    def __init__(self, pieces):
        if not self._available_pieces(pieces):
            raise ValueError('ドリンクチケット枚数{pieces}が不正')

        self._pieces = pieces

    def add(self, pieces):
        if not self._available_pieces(pieces):
            raise ValueError('ドリンクチケット枚数{pieces}が不正')

        new_quantity = DrinkTicketQuantity(self._pieces + pieces)
        return new_quantity

    def _available_pieces(self, pieces):
        return pieces in (0, 1, 3)

class DrinkTickets():
    # ドリンクチケットの各種を扱うコレクションクラスを作ったほうが懸命か
    # いや、コレクションクラスとは同じ型のオブジェクトを不特定多数扱うためなので不適
    def __init__(self):
        self._ism = DrinkTicketQuantity(0)
        self._iss = DrinkTicketQuantity(0)
        self._iru = DrinkTicketQuantity(0)
        self._rsu = DrinkTicketQuantity(0)
        self._ssu = DrinkTicketQuantity(0)
        self._scu = DrinkTicketQuantity(0)
        self._ss = DrinkTicketQuantity(0)
        self._spu = DrinkTicketQuantity(0)
        self._qr = DrinkTicketQuantity(0)
        self._qsj = DrinkTicketQuantity(0)
        self._bpu = DrinkTicketQuantity(0)
        self._inkres = DrinkTicketQuantity(0)
        self._bdx = DrinkTicketQuantity(0)
        self._mpu = DrinkTicketQuantity(0)

    def gain(self, drink_ticket_type, quantity):
        if not isinstance(drink_ticket_type, Abilities):
            raise TypeError('drink_ticket_type：{drink_ticket_type}の型が不正')

        if not isinstance(quantity, DrinkTicketQuantity):
            raise TypeError('quantity：{quantity}の型が不正')

        if drink_ticket_type == Abilities.ink_saver_main:
            pass

class DetecterSuper():
    def __init__(self, screenshot):
        if not isinstance(screenshot, Screenshot):
            raise TypeError("Screenshot型ではない")
        self._screenshot = screenshot

class Detecter14Pieces(DetecterSuper):
    def __init__(self, screenshot):
        super().__init__(screenshot)

        # 14枚チケットかどうかの特定に使う変数
        ticket14_region = ImageRegion(HorizontalAxisCoordinate(389),
                                      HorizontalAxisCoordinate(887),
                                      VerticalAxisCoordinate(270),
                                      VerticalAxisCoordinate(388))
        ticket14_region = self._screenshot.crop(ticket14_region)

class SingleResult():
    """単発のガチャ結果を保持する"""
    def __init__(self, result_id):
        if not isinstance(result_id, uuid4):
            raise TypeError('型がuuid4でない')

        self._result_id = result_id
        self._cash = Cash(0)
        self._food_cash = FoodCash(0)
        self._food_exp = FoodExp(0)
        self._drink_ism = 0
        self._drink_iss = 0
        self._drink_iru = 0
        self._drink_rsu = 0
        self._drink_ssu = 0
        self._drink_scu = 0
        self._drink_ss = 0
        self._drink_spu = 0
        self._drink_qr = 0
        self._drink_qsj = 0
        self._drink_bpu = 0
        self._drink_InkRes = 0
        self._drink_bdx = 0
        self._drink_mpu = 0
        self._chunk_ism = 0
        self._chunk_iss = 0
        self._chunk_iru = 0
        self._chunk_rsu = 0
        self._chunk_ssu = 0
        self._chunk_scu = 0
        self._chunk_ss = 0
        self._chunk_spu = 0
        self._chunk_qr = 0
        self._chunk_qsj = 0
        self._chunk_bpu = 0
        self._chunk_InkRes = 0
        self._chunk_bdx = 0
        self._chunk_mpu = 0

    def gain_cash(self, amount=0):
        self._cash = amount

    # def gain_food(self, food_type, amount):
    #     if food_type == FoodTypes.cash:
    #         self._food_cash = amount
    #     elif food_type == FoodTypes.exp:
    #         self._food_exp = amount
    #     else:
    #         pass

    def gain_chunk(self, chunk_type, amount):
        if chunk_type == Abilities.ink_saver_main:
            self._chunk_ism = amount

class ResultCollector():
    def __init__(self):
        self._results = set()

    def add(self, result: SingleResult):
        pass

    def output_csv(self):
        """csv形式にしてファイルに出力する"""
        pass

class CashAmount(Enum):
    four_thousand = '4000'
    eight_thousand = '8000'
    twenty_thousand = '20000'
    fourty_thousand = '40000'

class Cash():
    def __init__(self, amount):
        if amount not in (0, 4000, 8000, 20000, 40000):
            raise ValueError("おカネ{amount}の値が不正")

        self._amount = amount

class DetecterCash(DetecterSuper):
    def __init__(self, screenshot):
        super().__init__(screenshot)

        # ↓金額特定に使う変数
        digits4_region = ImageRegion(HorizontalAxisCoordinate(520),
                                     HorizontalAxisCoordinate(614),
                                     VerticalAxisCoordinate(194),
                                     VerticalAxisCoordinate(225))
        self._digits4_crop = self._screenshot.crop(digits4_region)
        digits5_region = ImageRegion(HorizontalAxisCoordinate(507),
                                     HorizontalAxisCoordinate(626),
                                     VerticalAxisCoordinate(194),
                                     VerticalAxisCoordinate(225))
        self._digits5_crop = self._screenshot.crop(digits5_region)

    def is_given(self):
        """ガチャ結果のスクショがおカネを入手したものかどうか判定する"""
        cash_model = cv2.imread(str(Path('model_images/cash_center.png')))

        cash_icon_region = ImageRegion(HorizontalAxisCoordinate(597),
                                       HorizontalAxisCoordinate(677),
                                       VerticalAxisCoordinate(287),
                                       VerticalAxisCoordinate(369))
        center_crop = self._screenshot.crop(cash_icon_region)

        # スクショの中央部分の切り抜きと、予め取得しているおカネアイコンの画像が似ていれば、
        # そのガチャ結果のスクショはおカネを手に入れているといえる
        similarity = get_similarity(center_crop, cash_model)
        return similarity > 0.9

    def get_amount(self):
        """おカネを入手していたらその金額を、入手していないスクショであれば0Gを返す"""
        if self.is_given():
            for cash_amouont in CashAmount:
                if self._is(cash_amouont):
                    return Cash(int(cash_amouont))
                else:
                    return Cash(0)
        else:
            return Cash(0)

    def _is(self, cash_amount):
        if not isinstance(cash_amount, CashAmount):
            raise TypeError('cash_amountの型が不正')

        model_path = 'model_images/cash_{cash_amount}.png'
        cash_model = cv2.imread(str(Path(model_path)))
        similarity = get_similarity(self._digits4_crop, cash_model)
        return similarity > 0.9

class FoodSuper():
    def __init__(self, amount):
        if amount not in (0, 15, 20, 25):
            raise ValueError("入手倍率：{amount}の値が不正")

        self._amount = amount / 10 # 実際の1.5倍などの数字に合わせるために10で割る

class FoodExp(FoodSuper):
    def __init__(self, amount):
        super().__init__(amount)

class FoodCash(FoodSuper):
    def __init__(self, amount):
        super().__init__(amount)

class FoodType(Enum):
    EXP = 'exp'
    CASH = 'cash'

class FoodMultiplier(Enum):
    multi15 = '15'
    multi20 = '20'
    multi25 = '25'

class DetecterFood(DetecterSuper):
    def __init__(self, screenshot):
        super().__init__(screenshot)

        food_region = ImageRegion(HorizontalAxisCoordinate(581),
                                  HorizontalAxisCoordinate(655),
                                  VerticalAxisCoordinate(302),
                                  VerticalAxisCoordinate(366))
        self._food_crop = self._screenshot.crop(food_region)

    def get_exp(self):
        return self._get(FoodType.EXP)

    def get_cash(self):
        return self._get(FoodType.CASH)

    def _get(self, food_type):
        for multiplier in FoodMultiplier:
            if self._is(food_type, multiplier):
                return FoodExp(multiplier)

        return FoodExp(0)

    def _is(self, food_type, multiplier):
        if not isinstance(food_type, FoodType):
            raise TypeError("フードの種類{food_type}が不正")

        if not isinstance(multiplier, FoodMultiplier):
            raise TypeError("フードの入手倍率{multiplier}が不正")

        model_path = 'model_images/food_{food_type}{multiplier}.png'
        food_model = cv2.imread(str(Path(model_path)))
        similarity = get_similarity(self._food_crop, food_model)
        return similarity > 0.9

class Abilities(Enum):
    ink_saver_main     = 'ism'
    ink_saver_sub      = 'iss'
    ink_recovery_up    = 'iru'
    run_speed_up       = 'rsu'
    swim_speed_up      = 'ssu'
    special_charge_up  = 'scu'
    special_saver      = 'ss'
    special_power_up   = 'spu'
    quick_respawn      = 'qr'
    quick_super_jump   = 'qsj'
    sub_power_up       = 'bpu'
    ink_resistance_up  = 'inkres'
    bomb_defence_up_dx = 'bdx'
    main_power_up      = 'mpu'

class GachaResultDetecter(DetecterSuper):
    def __init__(self, screenshot):
        super().__init__(screenshot)

    def get(self):
        pass

def get_hist(image):
    """
    cv2.compareHistに渡すと画像の類似度を計算できるヒストグラムオブジェクトを取得する。
    """
    #BGR三色を考慮したヒストグラムのベクトルを取得する。
    if not isinstance(image, np.ndarray):
        raise TypeError("ヒストグラム計算時に使うオブジェクトがndarrayでない")

    #binsはヒストグラム解析の解像度を示す指標。最も詳細に解析する場合は256でよい
    all_bins = [256]
    #rangeはヒストグラム解析の対象となる画素領域。最も詳細に解析する場合は[0,256]でよい
    all_ranges = [0, 256]

    mask = None

    hist_bgr = []
    #channelは0,1,2がそれぞれB,G,Rに相当。グレースケールの場合は0
    for channel in range(3):
        hist = cv2.calcHist([image], [channel], mask, all_bins, all_ranges)
        hist_bgr.append(hist)

    hist_array = np.array(hist_bgr)

    # hist_vecの計算方法はよくわからない。参考記事を写しただけ https://ensekitt.hatenablog.com/entry/2018/07/09/200000
    hist_vec = hist_array.reshape(hist_array.shape[0]*hist_array.shape[1], 1)
    return hist_vec

def get_similarity(image1, image2):
    if not (isinstance(image1, np.ndarray) and
            isinstance(image2, np.ndarray)):
        raise TypeError("画像比較時に渡すオブジェクトがndarrayではない")

    hist1 = get_hist(image1)
    hist2 = get_hist(image2)
    compare_method = 0 #ようわからんけど0にしとくといいみたい
    return cv2.compareHist(hist1, hist2, compare_method)
