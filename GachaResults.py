# coding: utf-8
"""
そもそもガチャ結果で出てくるはずのものを定義する
"""

from enum import Enum

valid_amounts_of_cash = set(4000, 8000, 20000, 40000)

valid_amounts_of_food = set(150, 200, 250)

class AllResult():
    def __init__(self, result_set: set):
        if not isinstance()

class SingleResult():
    def __init__(self, one_result: dict):
        if not isinstance(one_result, dict):
            raise TypeError('ガチャ結果画像から得たリザルトの型がdictではありません。')

        self._screenshot_id = one_result["id"]
        self._

class FoodTypes(Enum):
    Cash = 'Cash'
    Exp = 'Exp'

class Abilities(Enum):
    ISM = 'ink saver main'
    ISS = 'ink saver sub'
    IRU = 'ink recovery up'
    RSU = 'run speed up'
    SSU = 'swim speed up'
    SCU = 'special charge up'
    SS = 'special saver'
    SPU = 'special power up'
    QR = 'quick respawn'
    QSJ = 'quick super jump'
    BPU = 'sub power up'
    InkRes = 'ink resistance up'
    BDX = 'bomb defence up dx'
    MPU = 'main power up'