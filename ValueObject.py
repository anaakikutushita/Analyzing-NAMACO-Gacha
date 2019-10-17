# coding: utf-8

from uuid import uuid4
from uuid import UUID
from enum import Enum
from pathlib import Path
import csv
import math
import operator
from functools import reduce
from PIL import ImageChops
from PIL import Image
from PIL import ImageFilter

########################################################
##### Screenshot Definition
########################################################
class ScreenshotScale():
    def __init__(self):
        self.width = 1280
        self.height = 720

class CoodinateOperator():
    def __init__(self, value):
        self._value = value

    def __ge__(self, other):
        return self._value >= other._value

    def __sub__(self, other):
        return self._value - other._value

    def is_within_range(self, value, minimum_val, max_val):
        return minimum_val <= value <= max_val

class HorizontalAxisCoordinate(CoodinateOperator):
    def __init__(self, value):
        max_val = ScreenshotScale().width
        minimum_val = 0
        if not self.is_within_range(value, minimum_val, max_val):
            raise ValueError(f"{value}が範囲外")
        super().__init__(value)

class VerticalAxisCoordinate(CoodinateOperator):
    def __init__(self, value):
        max_val = ScreenshotScale().height
        minimum_val = 0
        if not self.is_within_range(value, minimum_val, max_val):
            raise ValueError(f"{value}が範囲外")
        super().__init__(value)

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
    def __init__(self, image: Image):
        # 型チェックしたかったけど、Imageオブジェクトの型を指定する方法がわからず断念
        # if not isinstance(image, Image):
        #     raise TypeError("Screenshot型に渡したものがImageでない")

        self._set_attribute(image)

        if self._height > ScreenshotScale().height:
            raise ValueError(f"画像の縦：{self._image.size[0]}が規定より大きい")
        if self._width > ScreenshotScale().width:
            raise ValueError(f"画像の横：{self._image.size[1]}が規定より大きい")

        self._image = image

    def crop(self, region):
        if not isinstance(region, ImageRegion):
            raise TypeError("クロップ指定領域がImageRegion型でない")

        crop_width = region.right - region.left
        if crop_width > self._width:
            raise ValueError(f"画像横幅：{self._width}よりも大きな横幅：{crop_width}でクロップしようとしている")

        crop_height = region.bottom - region.top
        if crop_height > self._height:
            raise ValueError(f"画像縦幅：{self._height}よりも大きな縦幅：{crop_height}でクロップしようとしている")

        # 本当はCoodinateクラスの._valueに触るべきではないが、うまいやり方が分からなかったのでこうした
        cropped_image = self._image.crop((
            region.left._value, region.top._value,
            region.right._value, region.bottom._value))

        # 新しいオブジェクトを作って返す
        new_screenshot = Screenshot(cropped_image)
        return new_screenshot

    def _set_attribute(self, image):
        self._image = image

        self._width = image.size[0]
        self._height = image.size[1]

########################################################
##### File Definition
########################################################
class Extension(Enum):
    # BMP = 'bmp'
    JPG = '*.jpg'
    # PNG = 'png'
    # ALL = None #ALLは使わないほうが懸命かも（画像以外の拡張子を持つPathが混入するとめんどい）

class PathCollector():
    """単一のディレクトリ内に存在するPathのコレクションを扱う"""
    def __init__(self, target_directory: Path, extension=Extension.JPG):
        if not isinstance(target_directory, Path):
            raise TypeError(f'ディレクトリ{target_directory}がPathでない')

        if extension not in Extension:
            raise TypeError(f'extension{Extension}の型がExtensionでない')

        if not target_directory.exists():
            raise ValueError(f'ディレクトリ{target_directory}が存在しない')

        if not target_directory.is_dir():
            raise ValueError(f'ディレクトリ{target_directory}がファイルを指している')

        self._path_collection = set(target_directory.glob(extension.value))

    def analyze_each(self):
        """
        取得した画像のパスからリザルトを取得してまとめて返す
        """
        collector = ResultCollector()
        all_screenshots = len(self._path_collection)
        print(f'全部で{all_screenshots}枚の画像の解析を始めます。')
        percent = 0
        while self._path_collection:
            # 一枚ずつopen → closeしないとファイルの開きすぎでエラーになる
            path = self._path_collection.pop()
            with Image.open(path) as image:
                screenshot = Screenshot(image)
                single_result = GachaAnalyzer(screenshot).get_result()
                collector.add(single_result)

            done_screenshots = all_screenshots - len(self._path_collection)
            progress = int(done_screenshots / all_screenshots * 100)
            if progress > percent:
                percent = progress
                print(f'{percent}%...')

        return collector

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
            raise ValueError(f"おカネ{amount}の値が不正")

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
            raise ValueError(f'フードチケット枚数{pieces}が不正')

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
            raise TypeError(f"入手倍率：{amount}の値が不正")

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
            raise ValueError(f'ドリンクチケット枚数{pieces}が不正')

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
            raise ValueError(f'ドリンクチケット枚数{pieces}が不正')

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
                # NO_TYPESとzeroは必要ないので飛ばす
                continue

            for multi in FoodMultiplier:
                if multi == FoodMultiplier.zero:
                    continue

                self._tickets[str(ftype.value) + str(multi.value / 10)] = FoodTicketPiece(0)

        if food_type != FoodType.NO_TYPES:
            target_key = str(food_type.value) + str(multiplier.value / 10)
            self._tickets[target_key] = self._tickets[target_key].get_added(pieces)

    # ガチャ一回の結果でフードチケットは1種1枚しか出ないが、ゼロで初期化したあとにgainするので必要
    def gain(self, add_target):
        if not isinstance(add_target, FoodTickets):
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
            raise TypeError(f'add_target:{add_target}の型が不正')

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
            raise TypeError(f'add_target：{add_target}の型が不正')

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

    def output_csv(self, output_dst='output.csv'):
        """csv形式にしてファイルに出力する"""
        writer = CsvWriter(self._results)
        writer.write(output_dst)

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

            writer.writeheader()
            for single_result in self._results_set:
                csv_row = self._get_csv_row(single_result)
                writer.writerow(csv_row)

    def _get_csv_head(self):
        """SingleResult型のメンバー名などを使ってCSVファイルのヘッダを作る。ソートして返す"""
        # メンバー名が必要なだけなので、インスタンスそのものは必要ない
        dummy_result = SingleResult(uuid4())
        header = list()
        for member, value in dummy_result.__dict__.items():
            if isinstance(value, UUID):
                # uuidだけはvalue_memberを持っていないので、memberだけを追加する
                header.append(member[1:])
            else:
                for value_member, value_value in value.__dict__.items():
                    # value_memberの値をdict型で持っているFoodTicketsなどは、そのdictのkeyを取り出す
                    if isinstance(value_value, dict):
                        for dict_key in value_value.keys():
                            key = ''
                            if isinstance(dict_key, Enum):
                                # dict_keyがEnumで定義されているときは、処理しやすいように.nameのstr型で取得する
                                key = dict_key.name
                            else:
                                key = dict_key

                            header.append(member[1:] + '_' + key)
                    else: # Cashの場合
                        # memberの0文字目はアンダースコアなので取り除く。
                        # value_memberの0文字目もアンダースコアだが、こちらは入れると読みやすくなるので取り除かない。
                        header.append(member[1:] + value_member)

        header.sort()
        return header

    def _get_csv_row(self, single_result):
        # DrinkTickets._tickets[Abilities.ISM]などの各フィールド名と、それが保持している数量を対応させた辞書を作る
        row = dict()
        for member, value in single_result.__dict__.items():
            if isinstance(value, UUID): # uuidの場合
                row[member[1:]] = value
            else:
                for value_member, value_value in value.__dict__.items():
                    if isinstance(value_value, dict): # FoodTicketsなどの場合
                        for dict_key in value_value.keys():
                            key = ''
                            if isinstance(dict_key, Enum):
                                # dict_keyがEnumで定義されているときは、処理しやすいように.nameのstr型で取得する
                                key = dict_key.name
                            else:
                                key = dict_key

                            row[member[1:] + '_' + key] = value_value[dict_key].count()
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

        chunk_result = DetecterChunk(self._screenshot).get_chunk()
        gacha_result.gain_chunk(chunk_result)

        return gacha_result

class DetecterCash():
    def __init__(self, screenshot):
        # super().__init__(screenshot)
        if not isinstance(screenshot, Screenshot):
            raise TypeError("Screenshot型ではない")
        self._screenshot = screenshot

        # ↓金額特定に使う変数
        digits4_region = ImageRegion(HorizontalAxisCoordinate(520),
                                     HorizontalAxisCoordinate(615),
                                     VerticalAxisCoordinate(194),
                                     VerticalAxisCoordinate(226))
        self._digits4_crop = self._screenshot.crop(digits4_region)

        digits5_region = ImageRegion(HorizontalAxisCoordinate(507),
                                     HorizontalAxisCoordinate(627),
                                     VerticalAxisCoordinate(194),
                                     VerticalAxisCoordinate(226))
        self._digits5_crop = self._screenshot.crop(digits5_region)

    def get_cash(self):
        """おカネを入手していたらその金額を、入手していないスクショであれば0Gを返す"""
        if self._has_any_cash(self._screenshot):
            for target_amount in CashAmount:
                if target_amount == CashAmount.zero:
                    continue

                if self._is(target_amount):
                    return Cash(target_amount)

        else:
            return Cash(CashAmount.zero)

    def _has_any_cash(self, screenshot):
        """ガチャ結果のスクショがおカネを入手したものかどうか判定する"""
        cash_icon_region = ImageRegion(HorizontalAxisCoordinate(597),
                                       HorizontalAxisCoordinate(678),
                                       VerticalAxisCoordinate(287),
                                       VerticalAxisCoordinate(370))
        center_crop = screenshot.crop(cash_icon_region)

        # スクショの中央部分の切り抜きと、予め取得しているおカネアイコンの画像が似ていれば、
        # そのガチャ結果のスクショはおカネを手に入れているといえる
        center_icon_path = 'model_images/cash_center.png'
        return is_similar(center_icon_path, center_crop)

    def _is(self, target_amount):
        """画像に写っているおカネの金額がtarget_amountに等しいかどうか判定する"""
        if not isinstance(target_amount, CashAmount):
            raise TypeError('target_amountの型が不正')

        # 4桁か5桁かで分岐
        if target_amount.value >= CashAmount.twenty_thousand.value:
            crop = self._digits5_crop
        else:
            crop = self._digits4_crop

        model_path = f'model_images/cash_{str(target_amount.value)}.png'
        return is_similar(model_path, crop, 10)

class DetecterFood(AnalyzerSuper):
    def __init__(self, screenshot):
        super().__init__(screenshot)

        food_region = ImageRegion(HorizontalAxisCoordinate(581),
                                  HorizontalAxisCoordinate(656),
                                  VerticalAxisCoordinate(302),
                                  VerticalAxisCoordinate(367))
        self._food_crop = self._screenshot.crop(food_region)

    def get_foods(self):
        food_tickets = FoodTickets()
        food_tickets.gain(self._get_exp())
        food_tickets.gain(self._get_cash())
        return food_tickets

    def _get_exp(self):
        for multiplier in FoodMultiplier:
            if multiplier == FoodMultiplier.zero:
                continue

            if self._has(FoodType.EXP, multiplier):
                return FoodTickets(FoodType.EXP, multiplier, FoodTicketPiece(1))

        # ガチャ結果に写っているのが経験値チケットじゃなかったら、ゼロ枚で返す
        return FoodTickets()

    def _get_cash(self):
        for multiplier in FoodMultiplier:
            if multiplier == FoodMultiplier.zero:
                continue

            if self._has(FoodType.CASH, multiplier):
                return FoodTickets(FoodType.CASH, multiplier, FoodTicketPiece(1))

        return FoodTickets()

    def _has(self, food_type, multiplier):
        if not isinstance(food_type, FoodType):
            raise TypeError(f"フードの種類{food_type}が不正")

        if not isinstance(multiplier, FoodMultiplier):
            raise TypeError(f"フードの入手倍率{multiplier}が不正")

        model_path = f'model_images/food_{food_type.value}{str(multiplier.value)}.png'
        return is_similar(model_path, self._food_crop)

class DetecterDrink(AnalyzerSuper):
    def __init__(self, screenshot):
        super().__init__(screenshot)

        # ドリンクチケットは「1枚だけ出る」「3つ横並びに出る」「14枚一気に出る」という３パターンがあるので、調べるregionも多数定義する
        center_region = ImageRegion(HorizontalAxisCoordinate(581),
                                    HorizontalAxisCoordinate(656),
                                    VerticalAxisCoordinate(302),
                                    VerticalAxisCoordinate(367))
        self._center_crop = self._screenshot.crop(center_region)

        left_region = ImageRegion(HorizontalAxisCoordinate(460),
                                  HorizontalAxisCoordinate(535),
                                  VerticalAxisCoordinate(288),
                                  VerticalAxisCoordinate(353))
        self._left_crop = self._screenshot.crop(left_region)

        right_region = ImageRegion(HorizontalAxisCoordinate(702),
                                   HorizontalAxisCoordinate(777),
                                   VerticalAxisCoordinate(315),
                                   VerticalAxisCoordinate(380))
        self._right_crop = self._screenshot.crop(right_region)

        fourteen_region = ImageRegion(HorizontalAxisCoordinate(389),
                                      HorizontalAxisCoordinate(888),
                                      VerticalAxisCoordinate(270),
                                      VerticalAxisCoordinate(389))
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
            self._model_paths[ability] = f'model_images/drink_{ability.value}.png'

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
        for power, path in self._model_paths.items():
            if is_similar(path, target):
                return DrinkTickets(power, DrinkTicketPiece(1))

        return None

class DetecterChunk(AnalyzerSuper):
    def __init__(self, screenshot):
        super().__init__(screenshot)

        # 中央のかけらアイコンのクロップと、かけらの個数部分のクロップを保持する
        icon_region = ImageRegion(HorizontalAxisCoordinate(590),
                                  HorizontalAxisCoordinate(685),
                                  VerticalAxisCoordinate(284),
                                  VerticalAxisCoordinate(378))
        self._icon_crop = self._screenshot.crop(icon_region)

        pieces_region = ImageRegion(HorizontalAxisCoordinate(725),
                                    HorizontalAxisCoordinate(771),
                                    VerticalAxisCoordinate(340),
                                    VerticalAxisCoordinate(368))
        self._pieces_crop = self._screenshot.crop(pieces_region)

        self._chunk_model_paths = dict()
        for ability in Abilities:
            self._chunk_model_paths[ability] = f'model_images/chunk_{ability.value}.png'
        # NO_ABILITIESは削除しておく
        del self._chunk_model_paths[Abilities.NO_ABILITIES]

        self._chunk_piece_paths = dict()
        for piece in ChunkPiece:
            self._chunk_piece_paths[piece] = f'model_images/chunk_{str(piece.value)}.png'
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

        return Chunks(ability, Chunk(piece))

########################################################
##### Image Amalysis Core
########################################################
def get_similarity(cropped_image, model, threshold_difference):
    # グレースケール化してから画像をガウスぼかしして、ピクセルごとの二乗平均平方根を使う
    grayed_cropped = cropped_image.convert('L')
    grayed_model = model.convert('L')

    rad = 2
    gaussed_cropped = grayed_cropped.filter(filter=ImageFilter.GaussianBlur(radius=rad))
    gaussed_model = grayed_model.filter(filter=ImageFilter.GaussianBlur(radius=rad))

    # テストで画像を確認したいときに実行するshowメソッド
    # gaussed_cropped.show()
    # gaussed_model.show()

    hist = ImageChops.difference(gaussed_cropped, gaussed_model).histogram()
    difference = math.sqrt(reduce(operator.add,
                                  map(lambda hist,
                                      i: hist*(i**2),
                                      hist,
                                      range(256))) / (float(gaussed_model.size[0]) * gaussed_cropped.size[1]))

    is_same_image = difference < threshold_difference
    return is_same_image

def is_similar(path_str, screenshot, threshold_difference=8):
    """
    存在しなくてもいいメソッドなんだけど、リファクタリングが面倒なので作った
    """
    # threshold_differenceの値は実際の画像でテストしつつ調整したもの。計算で出したい……
    model = Image.open(path_str)
    whole_image = screenshot._image
    is_similar = get_similarity(whole_image, model, threshold_difference)
    return is_similar
