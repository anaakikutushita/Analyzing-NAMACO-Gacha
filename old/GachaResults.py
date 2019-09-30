# coding: utf-8
"""
そもそもガチャ結果で出てくるはずのものを定義する
"""

from enum import Enum

# valid_amounts_of_cash = set(4000, 8000, 20000, 40000)

# valid_amounts_of_food = set(150, 200, 250)

class AllResultContainer():
    """複数のガチャ結果オブジェクトを保持しておく"""
    def __init__(self):
        self._result_set = set()

    def add(self, result):
        """ガチャ結果オブジェクトを追加する"""
        if not isinstance(result, SingleResult):
            raise TypeError('リザルトをコンテナに格納するには、SingleResult型のオブジェクトを使用してください')

        self._result_set.add(result)

    def get_csv(self):
        """保持しているガチャ結果オブジェクトの全結果をCSV形式にして返す"""
        return None

class SingleResult():
    """単発のガチャ結果を保持する"""
    def __init__(self, id):
        self._id = id
        self._cash = 0
        self._food_cash = 0
        self._food_exp = 0
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

    def gain_food(self, food_type, amount):
        if food_type == FoodTypes.cash:
            self._food_cash = amount
        elif food_type == FoodTypes.exp:
            self._food_exp = amount
        else:
            pass

    def gain_chunk(self, chunk_type, amount):
        if chunk_type == Abilities.ink_saver_main:
            self._chunk_ism = amount

class ResultTypes(Enum):
    cash  = 'cash'
    food  = 'food'
    drink = 'drink'
    chunk = 'chunk'

class FoodTypes(Enum):
    cash = 'cash'
    exp  = 'exp'

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
    ink_resistance_up  = 'InkRes'
    bomb_defence_up_dx = 'bdx'
    main_power_up      = 'mpu'
