# coding: utf-8

from uuid import uuid4
import unittest
from pathlib import Path
import cv2
import ValueObject

class TestScreenshotScale(unittest.TestCase):
    def test_scales(self):
        scale = ValueObject.ScreenshotScale()
        self.assertEqual(scale.width, 1280)
        self.assertEqual(scale.height, 720)

class TestHorizontalAxisCoordinate(unittest.TestCase):
    def test_outrange(self):
        try:
            ValueObject.HorizontalAxisCoordinate(2000)
        except:
            self.assertRaises(ValueError)

class TestVerticalAxisCoordinate(unittest.TestCase):
    def test_outrange(self):
        try:
            ValueObject.VerticalAxisCoordinate(2000)
        except:
            self.assertRaises(ValueError)

class TestImageRegion(unittest.TestCase):
    def test_invalid_type(self):
        try:
            ValueObject.ImageRegion(0, 100, 0, 100)
        except:
            self.assertRaises(TypeError)

    def test_value_relation(self):
        try:
            ValueObject.ImageRegion(100, 0, 0, 100)
        except:
            self.assertRaises(ValueError)

class TestScreenshot(unittest.TestCase):
    def test_invalid_type(self):
        try:
            ValueObject.Screenshot('dummy')
        except:
            self.assertRaises(TypeError)

    def test_invalid_scale(self):
        input_array = cv2.imread('./unit_tests/test_images/too_large_image.jpg')
        try:
            ValueObject.Screenshot(input_array)
        except:
            self.assertRaises(ValueError)

    def test_invalid_crop_type(self):
        input_array = cv2.imread('./unit_tests/test_images/sample_image.jpg')
        screenshot = ValueObject.Screenshot(input_array)
        try:
            screenshot.crop(100)
        except:
            self.assertRaises(TypeError)

    def test_large_crop_width(self):
        # 画像を読み込んで小さなクロップを作ってから、その小さなクロップよりも大きなRegionでクロップしようとする
        input_array = cv2.imread('./unit_tests/test_images/sample_image.jpg')
        screenshot = ValueObject.Screenshot(input_array)
        region = ValueObject.ImageRegion(
            ValueObject.HorizontalAxisCoordinate(0),
            ValueObject.HorizontalAxisCoordinate(100),
            ValueObject.VerticalAxisCoordinate(0),
            ValueObject.VerticalAxisCoordinate(200))
        small_screenshot = screenshot.crop(region)
        new_region = ValueObject.ImageRegion(
            ValueObject.HorizontalAxisCoordinate(0),
            ValueObject.HorizontalAxisCoordinate(200),
            ValueObject.VerticalAxisCoordinate(0),
            ValueObject.VerticalAxisCoordinate(300))
        try:
            small_screenshot.crop(new_region)
        except:
            self.assertRaises(ValueError)

    def test_crop(self):
        input_array = cv2.imread('./unit_tests/test_images/sample_image.jpg')
        screenshot = ValueObject.Screenshot(input_array)
        width = 200
        height = 300
        region = ValueObject.ImageRegion(
            ValueObject.HorizontalAxisCoordinate(0),
            ValueObject.HorizontalAxisCoordinate(width),
            ValueObject.VerticalAxisCoordinate(0),
            ValueObject.VerticalAxisCoordinate(height))
        cropped = screenshot.crop(region)
        self.assertEqual(cropped._width, width)
        self.assertEqual(cropped._height, height)

class TestScreenshotCollecter(unittest.TestCase):
    def test_invalid_add(self):
        collocter = ValueObject.ScreenshotCollecter()
        try:
            collocter.add('dummy')
        except:
            self.assertRaises(TypeError)

    def test_add(self):
        input_array = cv2.imread('./unit_tests/test_images/sample_image.jpg')

        screenshot = ValueObject.Screenshot(input_array)
        screenshot2 = ValueObject.Screenshot(input_array)

        collecter = ValueObject.ScreenshotCollecter()
        collecter.add(screenshot)
        collecter.add(screenshot2)

        self.assertEqual(collecter.count(), 2)

    # def test_get_result_collection(self): あとでテストを書く

class TestPathCollecter(unittest.TestCase):
    def test_invalid_extention(self):
        invalid_ext = 'jpg'
        try:
            ValueObject.PathCollecter(Path('./input_screenshots/'), invalid_ext)
        except:
            self.assertRaises(TypeError)

    def test_get_screenshots(self):
        input_directory = Path('./unit_tests/test_images/three_images_test/')
        path_collecter = ValueObject.PathCollecter(input_directory)
        screenshot_collecter = path_collecter.get_screenshots()

        self.assertEqual(screenshot_collecter.count(), 3)

class TestCash(unittest.TestCase):
    def test_invalid_amount(self):
        try:
            ValueObject.Cash(0)
        except:
            self.assertRaises(ValueError)

class TestFoodTicketPiece(unittest.TestCase):
    def test_invalid_pieces(self):
        try:
            ValueObject.FoodTicketPiece(3)
        except:
            self.assertRaises(ValueError)

    def test_invalid_add(self):
        piece = ValueObject.FoodTicketPiece(1)
        try:
            piece.get_added(1)
        except:
            self.assertRaises(TypeError)

class TestFoodSuper(unittest.TestCase):
    def test_invalid_multiplier(self):
        try:
            ValueObject.FoodSuper(15)
        except:
            self.assertRaises(TypeError)

class TestDrinkTicketPiece(unittest.TestCase):
    def test_invalid_piece(self):
        try:
            ValueObject.DrinkTicketPiece(5)
        except:
            self.assertRaises(ValueError)

    def test_get_added(self):
        piece = ValueObject.DrinkTicketPiece(1)
        add_target = ValueObject.DrinkTicketPiece(1)
        added = piece.get_added(add_target)

        self.assertEqual(added.count(), 2)

    def test_invalid_add(self):
        piece = ValueObject.DrinkTicketPiece(1)
        try:
            piece.get_added(1)
        except:
            self.assertRaises(TypeError)

class TestChunk(unittest.TestCase):
    def test_invalid_piece(self):
        try:
            ValueObject.Chunk(2)
        except:
            self.assertRaises(ValueError)

class TestFoodTickets(unittest.TestCase):
    def test_invalid_type(self):
        try:
            ValueObject.FoodTickets('dummy',
                                    ValueObject.FoodMultiplier.multi15,
                                    ValueObject.FoodTicketPiece(0))
        except:
            self.assertRaises(TypeError)

    # def test_invalid_gain(self):
    #     tickets = ValueObject.FoodTickets(
    #         ValueObject.FoodType.CASH,
    #         ValueObject.FoodMultiplier.multi15,
    #         ValueObject.FoodTicketPiece(1)
    #     )

    #     try:
    #         tickets.gain(1)
    #     except:
    #         self.assertRaises(TypeError)

    # def test_gain(self):
    #     tickets = ValueObject.FoodTickets(
    #         ValueObject.FoodType.CASH,
    #         ValueObject.FoodMultiplier.multi15,
    #         ValueObject.FoodTicketPiece(1)
    #     )

    #     add_target = ValueObject.FoodTickets(
    #         ValueObject.FoodType.EXP,
    #         ValueObject.FoodMultiplier.multi20,
    #         ValueObject.FoodTicketPiece(1)
    #     )

    #     tickets.gain(add_target)

    #     gained_key = ValueObject.FoodType.EXP.value + ValueObject.FoodMultiplier.multi20.value
    #     gained_num = tickets._tickets[gained_key].count()
    #     self.assertEqual(gained_num, 1)

class TestDrinkTickets(unittest.TestCase):
    def test_invalid_ability(self):
        try:
            ValueObject.DrinkTickets(
                'dummy',
                ValueObject.DrinkTicketPiece(0))
        except:
            self.assertRaises(ValueError)

    def test_invalid_piece(self):
        try:
            ValueObject.DrinkTickets(
                ValueObject.Abilities.ink_saver_main,
                1)
        except:
            self.assertRaises(TypeError)

    def test_invalid_gain(self):
        tickets = ValueObject.DrinkTickets(
            ValueObject.Abilities.ink_saver_main,
            ValueObject.DrinkTicketPiece(1)
        )

        try:
            tickets.gain(1)
        except:
            self.assertRaises(TypeError)

    def test_gain_same(self):
        tickets = ValueObject.DrinkTickets(
            ValueObject.Abilities.ink_saver_main,
            ValueObject.DrinkTicketPiece(1)
        )

        add_target = ValueObject.DrinkTickets(
            ValueObject.Abilities.ink_saver_main,
            ValueObject.DrinkTicketPiece(1)
        )

        tickets.gain(add_target)

        gained_num = tickets._tickets[ValueObject.Abilities.ink_saver_main].count()
        self.assertEqual(gained_num, 2)

    def test_gain_deff(self):
        tickets = ValueObject.DrinkTickets(
            ValueObject.Abilities.ink_saver_main,
            ValueObject.DrinkTicketPiece(1)
        )

        add_target = ValueObject.DrinkTickets(
            ValueObject.Abilities.ink_saver_sub,
            ValueObject.DrinkTicketPiece(1)
        )

        tickets.gain(add_target)

        gained_num = tickets._tickets[ValueObject.Abilities.ink_saver_sub].count()
        self.assertEqual(gained_num, 1)

    def test_gain_all(self):
        tickets = ValueObject.DrinkTickets()
        tickets.gain_all()

        for ability in ValueObject.Abilities:
            if ability == ValueObject.Abilities.NO_ABILITIES:
                continue # NO_ABILITIESはgainの対象外

            gained_num = tickets._tickets[ability].count()
            self.assertEqual(gained_num, 1)

class TestChunks(unittest.TestCase):
    def test_invalid_ability(self):
        try:
            ValueObject.Chunks(
                'dummy',
                ValueObject.Chunk(ValueObject.ChunkPiece.zero))
        except:
            self.assertRaises(ValueError)

    def test_invalid_piece(self):
        try:
            ValueObject.Chunks(
                ValueObject.Abilities.ink_saver_main,
                1)
        except:
            self.assertRaises(TypeError)

    def test_invalid_gain(self):
        chunks = ValueObject.Chunks(
            ValueObject.Abilities.ink_saver_main,
            ValueObject.Chunk(ValueObject.ChunkPiece.one)
        )

        try:
            chunks.gain(1)
        except:
            self.assertRaises(TypeError)

    def test_gain(self):
        ability = ValueObject.Abilities.ink_saver_main
        chunks = ValueObject.Chunks(
            ability,
            ValueObject.Chunk(ValueObject.ChunkPiece.zero)
        )

        add_target = ValueObject.Chunks(
            ability,
            ValueObject.Chunk(ValueObject.ChunkPiece.three)
        )

        chunks.gain(add_target)

        gained_num = chunks._chunks[ability].count()
        self.assertEqual(gained_num, 3)

class TestSingleResult(unittest.TestCase):
    def test_invalid_id(self):
        try:
            ValueObject.SingleResult('dummy')
        except:
            self.assertRaises(TypeError)

    def test_gain_cash(self):
        result_id = uuid4()
        single_result = ValueObject.SingleResult(result_id)
        cash = ValueObject.Cash(ValueObject.CashAmount.four_thousand)

        single_result.gain_cash(cash)
        self.assertEqual(single_result._cash.count(), 4000)
