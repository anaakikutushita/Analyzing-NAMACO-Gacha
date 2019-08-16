# coding: utf-8
"""
Screenshotクラスを受け取って、そのガチャ結果が何なのかを判定する
"""

import abc
import uuid
import numpy as np
import GachaResults

class ResultDetecter():
    def __init__(self, mat):
        if not isinstance(mat, np.ndarray):
            raise TypeError('detecter got not mat object')

        self._target_mat = mat

class GachaResult(abc.ABC):
    @abc.abstractmethod
    def get_result(self):
        pass

class Cash(GachaResult):
    def __init__(self, screenshot_id: uuid.UUID, amount: int):
        if not amount in GachaResults.valid_amounts_of_cash:
            raise CashAmountError(amount, 'Amount is invalid.')

        self._uuid = str(screenshot_id)
        self._amount = amount

    def get_result(self):
        return (self._uuid, 'Cash', None, self._amount)

class FoodTicket(GachaResult):
    def __init__(self, screenshot_id: uuid.UUID, food_type: str, amount_percent: int):
        if not food_type in GachaResults.FoodTypes:
            raise FoodTypeError(food_type, 'Food type should be Cash or Exp.')

        if not amount_percent in GachaResults.valid_amounts_of_food:
            raise FoodAmountError(amount_percent, 'Amount is invalid. Specify as 150 or 200, 250.')

        self._uuid = str(screenshot_id)
        self._food_type = food_type
        self._amount_percent = amount_percent

    def get_result(self):
        return (self._uuid, 'Food', self._food_type, self._amount_percent)

class DrinkTcket(GachaResult):
    def __init__(self, screenshot_id: uuid.UUID, ability_type: str):
        if not ability_type in GachaResults.Abilities:
            raise AbilityTypeError(ability_type, 'Ability type is invalid.')

        self._uuid = str(screenshot_id)
        self._ability_type = ability_type

    def get_result(self):
        return (self._uuid, 'Drink', self._ability_type, 1)

class AbilityChunk(GachaResult):
    def __init__(self, screenshot_id: uuid.UUID, ability_type: str, chunk_num: int):
        self._valid_nums = set(1, 3, 5, 10)

        if ability_type not in GachaResults.Abilities:
            raise AbilityTypeError(ability_type, 'Ability type is invalid.')

        if chunk_num not in self._valid_nums:
            raise ChunkNumError(chunk_num, 'Chunk num is invalid.')

        self._uuid = str(screenshot_id)
        self._ability_type = ability_type
        self._chunk_num = chunk_num

    def get_result(self):
        return (self._uuid, 'Chunk', self._ability_type, self._chunk_num)

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class CashAmountError(Error):
    """
    NAMACOガチャで出てくるおカネの金額は決まっているので、それ以外を入力していたらエラーにする
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class FoodTypeError(Error):
    """
    フードチケットの種類にチェックをかける
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class FoodAmountError(Error):
    """
    フードチケットの倍率にチェックをかける
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class AbilityTypeError(Error):
    """
    ギアパワーの種類にチェックをかける
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class ChunkNumError(Error):
    """
    NAMACOガチャで出てくるギアパワーのかけらの個数は決まっているので、それ以外を入力していたらエラーにする
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
