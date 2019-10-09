# coding: utf-8

from uuid import uuid4
from uuid import UUID
from enum import Enum
from pathlib import Path
import csv
import cv2
import numpy as np

########################################################
##### Screenshot Definition
########################################################
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

    def __ge__(self, other):
        return self._value >= other._value

    def __sub__(self, other):
        return self._value - other._value

class VerticalAxisCoordinate():
    def __init__(self, value):
        max_val = ScreenshotScale().height
        minimum_val = 0
        if not is_within_range(value, minimum_val, max_val):
            raise ValueError("{value}が範囲外")
        self._value = value

    def __ge__(self, other):
        return self._value >= other._value

    def __sub__(self, other):
        return self._value - other._value

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

        self._height = image.shape[0]
        self._width = image.shape[1]
        if self._height > ScreenshotScale().height:
            raise ValueError("画像の縦：{height}が規定より大きい")
        if self._width > ScreenshotScale().width:
            raise ValueError("画像の横：{width}が規定より大きい")

        self._image = image

    def crop(self, region):
        if not isinstance(region, ImageRegion):
            raise TypeError("クロップ指定領域がImageRegion型でない")

        crop_width = region.right - region.left
        if crop_width > self._width:
            raise ValueError("画像横幅：{self._width}よりも大きな横幅：{crop_width}でクロップしようとしている")

        crop_height = region.bottom - region.top
        if crop_height > self._height:
            raise ValueError("画像縦幅：{self._height}よりも大きな縦幅：{crop_height}でクロップしようとしている")

        # 本当はCoodinateクラスの._valueに触るべきではないが、うまいやり方が分からなかったのでこうした
        cropped_image = self._image[
            region.top._value:region.bottom._value,
            region.left._value:region.right._value]
        return Screenshot(cropped_image)

class ScreenshotCollecter():
    def __init__(self):
        self._screenshots = set()

    def add(self, screenshot):
        if not isinstance(screenshot, Screenshot):
            raise TypeError('スクリーンショットの型が不正')

        self._screenshots.add(screenshot)

    def count(self):
        return len(self._screenshots)

    def get_result_collection(self):
        collector = ResultCollector()

        while self._screenshots:
            target = self._screenshots.pop()
            gacha_result = GachaAnalyzer(target).get_result()
            collector.add(gacha_result)

        return collector

########################################################
##### File Definition
########################################################
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

        if extension not in Extension:
            raise TypeError('extension{Extension}の型がExtensionでない')

        if not target_directory.exists():
            raise ValueError('ディレクトリ{target_directory}が存在しない')

        if not target_directory.is_dir():
            raise ValueError('ディレクトリ{target_directory}がファイルを指している')

        self._path_collection = set(target_directory.glob(extension.value))

    def get_screenshots(self):
        """ScreenshotCollecterを返す"""
        collecter = ScreenshotCollecter()
        for image_path in self._path_collection:
            image = cv2.imread(str(image_path))
            screenshot = Screenshot(image)
            collecter.add(screenshot)

        return collecter

########################################################
##### Game System Definition
########################################################
class CashAmount(Enum):
    four_thousand   = 4000
    eight_thousand  = 8000
    twenty_thousand = 20000
    fourty_thousand = 40000
    zero            = 0 # 初期化用

class Cash():
    def __init__(self, amount=CashAmount.zero):
        if amount not in CashAmount:
            raise ValueError("おカネ{amount}の値が不正")

        self._amount = amount

    # 一度のガチャ結果でCashは1種類しか出てこないのが、ゼロで初期化したあとにaddが必要
    def get_added(self, cash):
        if not isinstance(cash, Cash):
            raise TypeError("cashの型が不正")

        if self._amount != CashAmount.zero:
            raise ValueError('Cashはzeroのときにだけgainできる')

        # ゼロのときだけaddできるので、self._amount + cash._amountのような足し算をする必要はない
        new_cash = Cash(cash._amount)
        return new_cash

    def count(self):
        return self._amount.value

class FoodTicketPiece():
    def __init__(self, pieces: int):
        if not self._available_pieces(pieces):
            raise ValueError('フードチケット枚数{pieces}が不正')

        self._pieces = pieces

    def _available_pieces(self, pieces):
        return pieces in (0, 1)

    # フードチケットは一度に1枚しか出ないが、ゼロで初期化したあとにaddメソッドが必要
    def get_added(self, ticket_piece):
        if not isinstance(ticket_piece, FoodTicketPiece):
            raise TypeError('ticket_pieceの型がFoodTicketPieceでない')

        new_piece = FoodTicketPiece(self._pieces + ticket_piece._pieces)
        return new_piece

    def count(self):
        return self._pieces

class FoodType(Enum):
    EXP      = 'exp'
    CASH     = 'cash'
    NO_TYPES = 'no_types' # FoodTicketsの初期化用

class FoodMultiplier(Enum):
    """見本になる画像ファイルの名前に小数点を使えないっぽいので妥協"""
    multi15 = 15
    multi20 = 20
    multi25 = 25
    zero    = 0 # FoodSuperの初期化用

class FoodSuper():
    """CashなのかExpなのかは本クラスでは判別しない"""
    def __init__(self, amount):
        if amount not in FoodMultiplier:
            raise TypeError("入手倍率：{amount}の値が不正")

        self._amount = amount / 10 # 実際の1.5倍などの数字に合わせるために10で割る

    #Foodをaddすることはないので、get_addedメソッドは実装しない

class FoodExp(FoodSuper):
    def __init__(self, amount):
        super().__init__(amount)

class FoodCash(FoodSuper):
    def __init__(self, amount):
        super().__init__(amount)

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
    NO_ABILITIES       = 'no_abilities' # DrinkTicketPieceの初期化用

class DrinkTicketPiece():
    """ドリンクチケットの枚数を表現する型。一回のガチャで手に入る枚数のみ表現可能"""
    def __init__(self, pieces: int):
        if not self._available_pieces(pieces):
            raise ValueError('ドリンクチケット枚数{pieces}が不正')

        self._pieces = pieces

    def _available_pieces(self, pieces):
        # 一度の結果で1種3枚が同時に手に入ることは恐らくないが、低確率なだけかもしれないので許容しておく
        return pieces in (0, 1, 2, 3)

    def get_added(self, ticket_piece):
        if not isinstance(ticket_piece, DrinkTicketPiece):
            raise TypeError('ficket_piecesの型がDrinkTicketPieceでない')

        new_piece = DrinkTicketPiece(self._pieces + ticket_piece._pieces)
        return new_piece

    def count(self):
        return self._pieces

class ChunkPiece(Enum):
    zero  = 0
    one   = 1
    three = 3
    five  = 5
    ten   = 10

class Chunk():
    def __init__(self, pieces: ChunkPiece):
        if pieces not in ChunkPiece:
            raise ValueError('ドリンクチケット枚数{pieces}が不正')

        self._pieces = pieces

    # 一度のガチャ結果ではchunkは一種しか出ないが、ゼロで初期化したあとにgainするので必要
    def get_added(self, chunk):
        if not isinstance(chunk, Chunk):
            raise TypeError('chunkの型がChunkでない')

        if not self._pieces == ChunkPiece.zero:
            raise ValueError('Chunkはzeroの場合のみgain可能')

        # zeroのときに限ってaddが可能なので、実際に足し算self._piece + chunk._pieceをする必要はない
        new_piece = Chunk(chunk._pieces)
        return new_piece

    def count(self):
        return int(self._pieces.value)

########################################################
##### Result Holder
########################################################
class FoodTickets():
    """おカネフードと経験値フードの両方を保持する"""
    def __init__(self,
                 food_type=FoodType.NO_TYPES,
                 multiplier=FoodMultiplier.multi15,
                 pieces=FoodTicketPiece(0)):
        if food_type not in FoodType:
            raise TypeError('food_typeの値が不正')

        if multiplier not in FoodMultiplier:
            raise TypeError('multiplierの値が不正')

        if not isinstance(pieces, FoodTicketPiece):
            raise TypeError('cash_foodの型が不正')

        self._tickets = dict()
        # (おカネ・経験値で2種)×(倍率3種)=6項目をkeyとする辞書で保持する
        for ftype in FoodType:
            if ftype == FoodType.NO_TYPES:
                # NO_TYPESは必要ないので飛ばす
                continue

            for multi in FoodMultiplier:
                self._tickets[str(ftype.value) + str(multi.value / 10)] = FoodTicketPiece(0)

        if ftype != FoodType.NO_TYPES:
            target_key = str(food_type.value) + str(multiplier.value / 10)
            self._tickets[target_key] = self._tickets[target_key].get_added(pieces)

    # ガチャ一回の結果でフードチケットは1種1枚しか出ないが、ゼロで初期化したあとにgainするので必要
    def gain(self, add_target):
        if isinstance(add_target, FoodTickets):
            raise TypeError('add_targetの型が不正')

        # gainできるのはゼロのときだけという縛りを入れようと思ったけど力尽きた

        for ticket_type in add_target._tickets.keys():
            added_tickets = self._tickets[ticket_type].get_added(add_target._tickets[ticket_type])
            self._tickets[ticket_type] = added_tickets

class DrinkTickets():
    """どの種類のドリンクチケットが何枚獲得できたかを表現するクラス"""
    # ドリンクチケットの各種を扱うコレクションクラスを作ったほうが懸命か
    # いや、コレクションクラスとはそもそも同じ型のオブジェクトを不特定多数扱うためのものなので不適
    def __init__(self, ability=Abilities.NO_ABILITIES, pieces=DrinkTicketPiece(0)):
        if ability not in Abilities:
            raise ValueError('abilityの値が不正')

        if not isinstance(pieces, DrinkTicketPiece):
            raise TypeError('quantityの型が不正')

        # self._tickets = dict(
        #     ism     = DrinkTicketPiece(0)
        #     ,iss    = DrinkTicketPiece(0)
        #     ,iru    = DrinkTicketPiece(0)
        #     ,rsu    = DrinkTicketPiece(0)
        #     ,ssu    = DrinkTicketPiece(0)
        #     ,scu    = DrinkTicketPiece(0)
        #     ,ss     = DrinkTicketPiece(0)
        #     ,spu    = DrinkTicketPiece(0)
        #     ,qr     = DrinkTicketPiece(0)
        #     ,qsj    = DrinkTicketPiece(0)
        #     ,bpu    = DrinkTicketPiece(0)
        #     ,inkres = DrinkTicketPiece(0)
        #     ,bdx    = DrinkTicketPiece(0)
        #     ,mpu    = DrinkTicketPiece(0))
        self._tickets = dict()
        for abl in Abilities:
            # 最初に全種類ゼロで定義してから、指定された種類だけ数を入れる
            self._tickets[abl] = DrinkTicketPiece(0)

        self._tickets[ability] = self._tickets[ability].get_added(pieces)

        # NO_ABILITIESは削除しておく
        del self._tickets[Abilities.NO_ABILITIES]

    def gain(self, add_target):
        if not isinstance(add_target, DrinkTickets):
            raise TypeError('add_target:{add_target}の型が不正')

        for power in add_target._tickets.keys():
            self._tickets[power] = self._tickets[power].get_added(add_target._tickets[power])

    def gain_all(self):
        # 1度に全種類のチケットを入手するときは必ず1枚ずつ入手するので、数量指定はしない
        for ability in Abilities:
            if ability in self._tickets:
                self._tickets[ability] = self._tickets[ability].get_added(DrinkTicketPiece(1))

class Chunks():
    """どの種類のギアパワーのかけらをいくつ取得できたかを表現するクラス"""
    def __init__(self,
                 ability=Abilities.NO_ABILITIES,
                 pieces=Chunk(ChunkPiece.zero)):
        if ability not in Abilities:
            raise ValueError('abilityの値が不正')

        if not isinstance(pieces, Chunk):
            raise TypeError('piecesの型が不正')

        self._chunks = dict()
        for abl in Abilities:
            self._chunks[abl] = Chunk(ChunkPiece.zero)

        self._chunks[ability] = self._chunks[ability].get_added(pieces)

        # NO_ABILITIESは削除しておく
        del self._chunks[Abilities.NO_ABILITIES]

    # 一度のガチャ結果ではかけらは1種しか手に入らないが、ゼロで初期化したあとにgainするので必要
    def gain(self, add_target):
        if not isinstance(add_target, Chunks):
            raise TypeError('add_target：{add_target}の型が不正')

        for power in add_target._chunks.keys():
            self._chunks[power] = self._chunks[power].get_added(add_target._chunks[power])

class SingleResult():
    """単発のガチャ結果を保持する"""
    def __init__(self, result_id):
        if not isinstance(result_id, UUID):
            raise TypeError('result_idの型がUUIDでない')

        self._result_id = result_id
        self._cash   = Cash()
        self._foods  = FoodTickets()
        self._drinks = DrinkTickets()
        self._chunks = Chunks()

    def gain_cash(self, cash: Cash):
        self._cash = self._cash.get_added(cash)

    def gain_food(self, food_tickets: FoodTickets):
        self._foods.gain(food_tickets)

    def gain_drink(self, drink_tickets: DrinkTickets):
        self._drinks.gain(drink_tickets)

    def gain_chunk(self, chunks: Chunks):
        self._chunks.gain(chunks)

class ResultCollector():
    def __init__(self):
        self._results = set()

    def add(self, result: SingleResult):
        if not isinstance(result, SingleResult):
            TypeError('resultの型がSingleResultでない')

        self._results.add(result)

    def output_csv(self):
        """csv形式にしてファイルに出力する"""
        writer = CsvWriter(self._results)
        writer.write('output.csv')

########################################################
##### Result Writer
########################################################
class CsvWriter():
    def __init__(self, results_set):
        if not isinstance(results_set, set):
            raise TypeError('results_setがset型ではない')

        for result in results_set:
            if not isinstance(result, SingleResult):
                raise TypeError('results_setの中にSingleResult型ではないオブジェクトを含んでいる')

        self._results_set = results_set

    def write(self, file_name):
        # チュートリアルのコピペ
        # with open('names.csv', 'w', newline='') as csvfile:
        #     fieldnames = ['first_name', 'last_name']
        #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        #     writer.writeheader()
        #     writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
        #     writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
        #     writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})
        with open(file_name, 'w', newline='') as csvfile:
            fieldnames = self._get_csv_head()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

            for single_result in self._results_set:
                csv_row = self._get_csv_row(single_result)
                writer.writerow(csv_row)

    def _get_csv_head(self):
        """SingleResult型のメンバー名などを使ってCSVファイルのヘッダを作る"""
        # メンバー名が必要なだけなので、インスタンスそのものは必要ない
        dummy_result = SingleResult(uuid4())
        header = list()
        for member, value in dummy_result.__dict__.items():
            if member == dummy_result.__dict__.keys()[0]: # uuidの場合
                # 最初のmember(uuid)だけはvalue_memberを持っていないので、memberだけを追加する
                header.append(member[1:])
            else:
                for value_member, value_value in value.__dict__.items():
                    # value_memberの値をdict型で持っているFoodTicketsなどは、そのdictのkeyを取り出す
                    if isinstance(value_value, dict):
                        for dict_key in value_value.keys():
                            header.append(member[1:] + '_' + dict_key)
                    else: # Cashの場合
                        # memberの0文字目はアンダースコアなので取り除く。
                        # value_memberの0文字目もアンダースコアだが、こちらは入れると読みやすくなるので取り除かない。
                        header.append(member[1:] + value_member)

        return header

    def _get_csv_row(self, single_result):
        # DrinkTickets._tickets[Abilities.ISM]などの各フィールド名と、それが保持している数量を対応させた辞書を作る
        row = dict()
        for member, value in single_result.__dict__.items():
            if member == single_result.__dict__.keys()[0]: # uuidの場合
                row[member[1:]] = value
            else:
                for value_member, value_value in value.__dict__.items():
                    if isinstance(value_value, dict): # FoodTicketsなどの場合
                        for dict_key in value_value.keys():
                            row[member[1:] + '_' + dict_key] = value_member[dict_key].count()
                    else: # Cashの場合
                        row[member[1:] + value_member] = value.count()

        return row

########################################################
##### Gacha Analyzer
########################################################
class AnalyzerSuper():
    """ちゃんとScreenshot型の変数が渡されてるかどうかチェックするだけ"""
    def __init__(self, screenshot):
        if not isinstance(screenshot, Screenshot):
            raise TypeError("Screenshot型ではない")
        self._screenshot = screenshot

class GachaAnalyzer(AnalyzerSuper):
    def __init__(self, screenshot):
        super().__init__(screenshot)

    def get_result(self):
        """画像に何が写っているかに関係なく、おカネ・フード・ドリンク・かけらの解析を順番に行う。"""
        gacha_result = SingleResult(uuid4())

        cash_result = DetecterCash(self._screenshot).get_cash()
        gacha_result.gain_cash(cash_result)

        food_result = DetecterFood(self._screenshot).get_foods()
        gacha_result.gain_food(food_result)

        drink_result = DetecterDrink(self._screenshot).get_drinks()
        gacha_result.gain_drink(drink_result)

        chunk_result = DetecterChunk(self._screenshot)
        gacha_result.gain_chunk(chunk_result)

        return gacha_result

class DetecterCash(AnalyzerSuper):
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

    def get_cash(self):
        """おカネを入手していたらその金額を、入手していないスクショであれば0Gを返す"""
        if self._has_any_cash():
            for target_amount in CashAmount:
                if self._is(target_amount):
                    return Cash(int(target_amount))
                else:
                    return Cash(0)
        else:
            return Cash(0)

    def _has_any_cash(self):
        """ガチャ結果のスクショがおカネを入手したものかどうか判定する"""
        center_icon_path = 'model_images/cash_center.png'

        cash_icon_region = ImageRegion(HorizontalAxisCoordinate(597),
                                       HorizontalAxisCoordinate(677),
                                       VerticalAxisCoordinate(287),
                                       VerticalAxisCoordinate(369))
        center_crop = self._screenshot.crop(cash_icon_region)

        # スクショの中央部分の切り抜きと、予め取得しているおカネアイコンの画像が似ていれば、
        # そのガチャ結果のスクショはおカネを手に入れているといえる
        return is_similar(center_icon_path, center_crop)

    def _is(self, target_amount):
        """画像に写っているおカネの金額がtarget_amountに等しいかどうか判定する"""
        if not isinstance(target_amount, CashAmount):
            raise TypeError('target_amountの型が不正')

        model_path = 'model_images/cash_{cash_amount}.png'
        return is_similar(model_path, self._digits4_crop)

class DetecterFood(AnalyzerSuper):
    def __init__(self, screenshot):
        super().__init__(screenshot)

        food_region = ImageRegion(HorizontalAxisCoordinate(581),
                                  HorizontalAxisCoordinate(655),
                                  VerticalAxisCoordinate(302),
                                  VerticalAxisCoordinate(366))
        self._food_crop = self._screenshot.crop(food_region)

    def get_foods(self):
        food_tickets = FoodTickets()
        food_tickets.gain(self._get_exp())
        food_tickets.gain(self._get_cash())
        return food_tickets

    def _get_exp(self):
        for multiplier in FoodMultiplier:
            if self._has(FoodType.EXP, multiplier):
                return FoodTickets(FoodType.EXP, multiplier, FoodTicketPiece(1))

        # ガチャ結果に写っているのが経験値チケットじゃなかったら、ゼロ枚で返す
        return FoodTickets()

    def _get_cash(self):
        for multiplier in FoodMultiplier:
            if self._has(FoodType.CASH, multiplier):
                return FoodTickets(FoodType.CASH, multiplier, FoodTicketPiece(1))

        return FoodTickets()

    def _has(self, food_type, multiplier):
        if not isinstance(food_type, FoodType):
            raise TypeError("フードの種類{food_type}が不正")

        if not isinstance(multiplier, FoodMultiplier):
            raise TypeError("フードの入手倍率{multiplier}が不正")

        model_path = 'model_images/food_{food_type}{multiplier}.png'
        return is_similar(model_path, self._food_crop)

class DetecterDrink(AnalyzerSuper):
    def __init__(self, screenshot):
        super().__init__(screenshot)

        # ドリンクチケットは「1枚だけ出る」「3つ横並びに出る」「14枚一気に出る」という３パターンがあるので、調べるregionも多数定義する
        center_region = ImageRegion(HorizontalAxisCoordinate(581),
                                    HorizontalAxisCoordinate(655),
                                    VerticalAxisCoordinate(302),
                                    VerticalAxisCoordinate(366))
        self._center_crop = self._screenshot.crop(center_region)

        left_region = ImageRegion(HorizontalAxisCoordinate(460),
                                  HorizontalAxisCoordinate(534),
                                  VerticalAxisCoordinate(288),
                                  VerticalAxisCoordinate(352))
        self._left_crop = self._screenshot.crop(left_region)

        right_region = ImageRegion(HorizontalAxisCoordinate(702),
                                   HorizontalAxisCoordinate(776),
                                   VerticalAxisCoordinate(315),
                                   VerticalAxisCoordinate(379))
        self._right_crop = self._screenshot.crop(right_region)

        fourteen_region = ImageRegion(HorizontalAxisCoordinate(389),
                                      HorizontalAxisCoordinate(887),
                                      VerticalAxisCoordinate(270),
                                      VerticalAxisCoordinate(388))
        self._fourteen_crop = self._screenshot.crop(fourteen_region)

        # self._model_paths = dict(
        #     ism     = 'model_images/drink_ism.png'
        #     ,iss    = 'model_images/drink_iss.png'
        #     ,iru    = 'model_images/drink_iru.png'
        #     ,rsu    = 'model_images/drink_rsu.png'
        #     ,ssu    = 'model_images/drink_ssu.png'
        #     ,scu    = 'model_images/drink_scu.png'
        #     ,ss     = 'model_images/drink_ss.png'
        #     ,spu    = 'model_images/drink_spu.png'
        #     ,qr     = 'model_images/drink_qr.png'
        #     ,qsj    = 'model_images/drink_qsj.png'
        #     ,bpu    = 'model_images/drink_bpu.png'
        #     ,InkRes = 'model_images/drink_InkRes.png'
        #     ,bdx    = 'model_images/drink_bdx.png'
        #     ,mpu    = 'model_images/drink_mpu.png')
        self._model_paths = dict()
        for ability in Abilities:
            self._model_paths[ability] = 'model_images/drink_' + ability + '.png'

        # NO_ABILITIESは削除しておく
        del self._model_paths[Abilities.NO_ABILITIES]

    def get_drinks(self):
        drinks = DrinkTickets()

        if self._has_fourteen():
            # 14枚のチケットには被りがないと決めつけて、結果を返す
            drinks.gain_all()
            return drinks

        center_ticket = self._get(self._center_crop)
        if center_ticket:
            drinks.gain(center_ticket)

            # 中央にチケットがある場合、左右にもある可能性を考慮する
            left_ticket = self._get(self._left_crop)
            right_ticket = self._get(self._right_crop)

            if left_ticket and right_ticket:
                drinks.gain(left_ticket)
                drinks.gain(right_ticket)

            return drinks

        # 14枚でもないし、中央にもない場合はドリンクはゼロ
        return DrinkTickets(Abilities.NO_ABILITIES, DrinkTicketPiece(0))

    def _has_fourteen(self):
        model_path = 'model_images/drink_14.png'
        return is_similar(model_path, self._fourteen_crop)

    def _get(self, target):
        for power, path in self._model_paths:
            if is_similar(path, target):
                return DrinkTickets(power, DrinkTicketPiece(0))

        return None

class DetecterChunk(AnalyzerSuper):
    def __init__(self, screenshot):
        super().__init__(screenshot)

        # 中央のかけらアイコンのクロップと、かけらの個数部分のクロップを保持する
        icon_region = ImageRegion(HorizontalAxisCoordinate(590),
                                  HorizontalAxisCoordinate(684),
                                  VerticalAxisCoordinate(284),
                                  VerticalAxisCoordinate(377))
        self._icon_crop = self._screenshot.crop(icon_region)

        pieces_region = ImageRegion(HorizontalAxisCoordinate(725),
                                    HorizontalAxisCoordinate(770),
                                    VerticalAxisCoordinate(340),
                                    VerticalAxisCoordinate(367))
        self._pieces_crop = self._screenshot.crop(pieces_region)

        self._chunk_model_paths = dict()
        for ability in Abilities:
            self._chunk_model_paths[ability] = 'model_images/chunk_' + ability + '.png'
        # NO_ABILITIESは削除しておく
        del self._chunk_model_paths[Abilities.NO_ABILITIES]

        self._chunk_piece_paths = dict()
        for piece in ChunkPiece:
            self._chunk_piece_paths[piece] = 'model_images/chunk_' + piece + '.png'
        # zeroは削除しておく
        del self._chunk_piece_paths[ChunkPiece.zero]

    def get_chunk(self):
        # かけらの種類を確定させてから、個数を調べる
        ability = Abilities.NO_ABILITIES
        for target_ability in Abilities:
            if not target_ability == Abilities.NO_ABILITIES:
                target_path = self._chunk_model_paths[target_ability]
                if is_similar(target_path, self._icon_crop):
                    ability = target_ability

        # 個数を調べる
        piece = ChunkPiece.zero
        for target_piece in ChunkPiece:
            if not target_piece == ChunkPiece.zero:
                target_path = self._chunk_piece_paths[target_piece]
                if is_similar(target_path, self._pieces_crop):
                    piece = target_piece

        return Chunks(ability, piece)

########################################################
##### Image Amalysis Core
########################################################
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

def is_similar(path_str, ndarray):
    model = cv2.imread(str(Path(path_str)))
    similarity = get_similarity(ndarray, model)
    return similarity > 0.9
