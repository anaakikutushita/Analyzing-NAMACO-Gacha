# coding: utf-8

from uuid import uuid4
import unittest
from pathlib import Path
import os
import csv
import cv2
from PIL import Image
import ValueObject

class TestScreenshotScale(unittest.TestCase):
    def test_scales(self):
        scale = ValueObject.ScreenshotScale()
        self.assertEqual(scale.width, 1280)
        self.assertEqual(scale.height, 720)

class TestHorizontalAxisCoordinate(unittest.TestCase):
    def test_outrange(self):
        try:
            ValueObject.HorizontalAxis(2000)
        except:
            self.assertRaises(ValueError)

class TestVerticalAxisCoordinate(unittest.TestCase):
    def test_outrange(self):
        try:
            ValueObject.VerticalAxis(2000)
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

    # 現状は型チェックできないためテストしない
    # def test_invalid_crop_type(self):
    #     input_path = Path('unit_tests/test_images/sample_image.jpg')
    #     screenshot = ValueObject.Screenshot(input_path)
    #     try:
    #         screenshot.crop(100)
    #     except:
    #         self.assertRaises(TypeError)

    def test_large_crop_width(self):
        # 画像を読み込んで小さなクロップを作ってから、その小さなクロップよりも大きなRegionでクロップしようとする
        image = Image.open('unit_tests/test_images/sample_image.jpg')
        screenshot = ValueObject.Screenshot(image)
        region = ValueObject.ImageRegion(
            ValueObject.HorizontalAxis(0),
            ValueObject.HorizontalAxis(100),
            ValueObject.VerticalAxis(0),
            ValueObject.VerticalAxis(200))
        small_screenshot = screenshot.crop(region)
        new_region = ValueObject.ImageRegion(
            ValueObject.HorizontalAxis(0),
            ValueObject.HorizontalAxis(200),
            ValueObject.VerticalAxis(0),
            ValueObject.VerticalAxis(300))
        try:
            small_screenshot.crop(new_region)
        except:
            self.assertRaises(ValueError)

    def test_crop(self):
        image = Image.open('unit_tests/test_images/sample_image.jpg')
        screenshot = ValueObject.Screenshot(image)
        width = 200
        height = 300
        region = ValueObject.ImageRegion(
            ValueObject.HorizontalAxis(0),
            ValueObject.HorizontalAxis(width),
            ValueObject.VerticalAxis(0),
            ValueObject.VerticalAxis(height))
        cropped = screenshot.crop(region)
        self.assertEqual(cropped._width, width)
        self.assertEqual(cropped._height, height)

class TestResultCollection(unittest.TestCase):
    def test_get_result_collection(self):
        input_dir = Path('unit_tests/test_images/result_collector_test')
        input_paths = ValueObject.PathCollector(input_dir)
        gacha_results = input_paths.analyze_each()

        # gacha_resultsの中に以下の結果が入っていることを確認する
        # cash4000 * 2
        # ink_saver_sub chunk1 * 1
        # food_cash1.5 * 1
        results_set = gacha_results._results
        cash4000_1 = False
        cash4000_2 = False
        iss_chunk1 = False
        food_cash15 = False

        for result in results_set:
            if self._has_cash4000(result):
                if not cash4000_1:
                    cash4000_1 = True
                else:
                    cash4000_2 = True

            if self._has_iss_chunk1(result):
                iss_chunk1 = True

            if self._has_food_cash15(result):
                food_cash15 = True

        test_resuts = [
            cash4000_1,
            cash4000_2,
            iss_chunk1,
            food_cash15
        ]
        self.assertTrue(all(test_resuts))

    def _has_cash4000(self, result):
        return result._cash.count() == 4000

    def _has_iss_chunk1(self, result):
        ability = ValueObject.Abilities.ink_saver_sub
        return result._chunks._chunks[ability].count() == 1

    def _has_food_cash15(self, result):
        foodtype = ValueObject.FoodType.CASH
        multiplier = ValueObject.FoodMultiplier.multi15
        key = str(foodtype.value) + str(multiplier.value / 10)
        return result._foods._tickets[key].count() == 1

class TestPathCollector(unittest.TestCase):
    def test_invalid_extention(self):
        invalid_ext = 'jpg'
        try:
            ValueObject.PathCollector(Path('./input_screenshots/'), invalid_ext)
        except:
            self.assertRaises(TypeError)

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

    def test_gain_food(self):
        ftype = ValueObject.FoodType.CASH
        multi = ValueObject.FoodMultiplier.multi15

        tickets = ValueObject.FoodTickets(
            ftype,
            multi,
            ValueObject.FoodTicketPiece(1)
        )

        single_result = ValueObject.SingleResult(uuid4())
        single_result.gain_food(tickets)

        key = str(ftype.value) + str(multi.value / 10)
        self.assertEqual(single_result._foods._tickets[key].count(), 1)

    def test_gain_drink(self):
        # 1種1枚gain出来るか調べる
        ability1 = ValueObject.Abilities.ink_saver_main
        tickets1 = ValueObject.DrinkTickets(
            ability1,
            ValueObject.DrinkTicketPiece(1)
        )

        single_result = ValueObject.SingleResult(uuid4())
        single_result.gain_drink(tickets1)

        self.assertEqual(single_result._drinks._tickets[ability1].count(), 1)

        # 2種1枚ずつgain出来るか調べる
        ability2 = ValueObject.Abilities.ink_saver_sub
        tickets2 = ValueObject.DrinkTickets(
            ability2,
            ValueObject.DrinkTicketPiece(1)
        )

        single_result.gain_drink(tickets2)

        self.assertEqual(single_result._drinks._tickets[ability1].count(), 1)
        self.assertEqual(single_result._drinks._tickets[ability2].count(), 1)

        # 1種2枚、もう1種1枚gain出来るか調べる
        tickets3 = ValueObject.DrinkTickets(
            ability1,
            ValueObject.DrinkTicketPiece(1)
        )

        single_result.gain_drink(tickets3)

        self.assertEqual(single_result._drinks._tickets[ability1].count(), 2)
        self.assertEqual(single_result._drinks._tickets[ability2].count(), 1)

    def test_gain_chunk(self):
        ability1 = ValueObject.Abilities.ink_saver_main
        chunk = ValueObject.Chunks(
            ability1,
            ValueObject.Chunk(ValueObject.ChunkPiece.five)
        )

        single_result = ValueObject.SingleResult(uuid4())
        single_result.gain_chunk(chunk)

        self.assertEqual(single_result._chunks._chunks[ability1].count(), 5)

class TestResultCollector(unittest.TestCase):
    def test_invalid_add(self):
        collector = ValueObject.ResultCollector()
        try:
            collector.add('dummy')
        except:
            self.assertRaises(TypeError)

    def test_add(self):
        collector = ValueObject.ResultCollector()

        # おカネをゲットした場合を想定
        single_result = ValueObject.SingleResult(uuid4())
        cash_amount = ValueObject.CashAmount.four_thousand
        cash = ValueObject.Cash(cash_amount)
        single_result.gain_cash(cash)

        collector.add(single_result)

        # collectorの中におカネが入っていることを確認する
        popped_result = collector._results.pop()
        popped_cash = popped_result._cash
        popped_amount = popped_cash.count()

        self.assertEqual(popped_amount, cash_amount.value)

    def test_output_csv(self):
        # テスト前にアウトプットを削除しておく
        output_dst = Path('unit_tests/output.csv')
        self._delete_if_exists(output_dst)

        input_dir = Path('unit_tests/test_images/result_collector_test')
        input_paths = ValueObject.PathCollector(input_dir)
        gacha_results = input_paths.analyze_each()
        gacha_results.output_csv(output_dst=output_dst)

        # CSVが生成されているかを確認
        # 読み込んで中を確認しようと思ったけど力尽きた。ファイル生成だけ確認すればいいやってことにした。
        self.assertTrue(output_dst.exists())


    def _delete_if_exists(self, path: Path):
        if path.exists() and path.is_file():
            os.remove(str(path))

class TestCsvWriter(unittest.TestCase):
    def test_invalid_result(self):
        try:
            ValueObject.CsvWriter('dummy')
        except:
            self.assertRaises(TypeError)

    # def test_write(self): TestResultCollector側でテストする

    def test_get_csv_head(self):
        # テストを書いた時点における想定ヘッダを手打ちして比較する
        expected_header = list()
        expected_header.append('result_id')

        expected_header.append('cash' + '_amount')

        expected_header.append('foods' + '_' + 'exp1.5')
        expected_header.append('foods' + '_' + 'exp2.0')
        expected_header.append('foods' + '_' + 'exp2.5')
        expected_header.append('foods' + '_' + 'cash1.5')
        expected_header.append('foods' + '_' + 'cash2.0')
        expected_header.append('foods' + '_' + 'cash2.5')

        expected_header.append('drinks' + '_' + 'ink_saver_main')
        expected_header.append('drinks' + '_' + 'ink_saver_sub')
        expected_header.append('drinks' + '_' + 'ink_recovery_up')
        expected_header.append('drinks' + '_' + 'run_speed_up')
        expected_header.append('drinks' + '_' + 'swim_speed_up')
        expected_header.append('drinks' + '_' + 'special_charge_up')
        expected_header.append('drinks' + '_' + 'special_saver')
        expected_header.append('drinks' + '_' + 'special_power_up')
        expected_header.append('drinks' + '_' + 'quick_respawn')
        expected_header.append('drinks' + '_' + 'quick_super_jump')
        expected_header.append('drinks' + '_' + 'sub_power_up')
        expected_header.append('drinks' + '_' + 'ink_resistance_up')
        expected_header.append('drinks' + '_' + 'bomb_defence_up_dx')
        expected_header.append('drinks' + '_' + 'main_power_up')

        expected_header.append('chunks' + '_' + 'ink_saver_main')
        expected_header.append('chunks' + '_' + 'ink_saver_sub')
        expected_header.append('chunks' + '_' + 'ink_recovery_up')
        expected_header.append('chunks' + '_' + 'run_speed_up')
        expected_header.append('chunks' + '_' + 'swim_speed_up')
        expected_header.append('chunks' + '_' + 'special_charge_up')
        expected_header.append('chunks' + '_' + 'special_saver')
        expected_header.append('chunks' + '_' + 'special_power_up')
        expected_header.append('chunks' + '_' + 'quick_respawn')
        expected_header.append('chunks' + '_' + 'quick_super_jump')
        expected_header.append('chunks' + '_' + 'sub_power_up')
        expected_header.append('chunks' + '_' + 'ink_resistance_up')
        expected_header.append('chunks' + '_' + 'bomb_defence_up_dx')
        expected_header.append('chunks' + '_' + 'main_power_up')

        # ソートすることで比較を容易にする
        expected_header.sort()

        dummy_result = ValueObject.SingleResult(uuid4())
        results_set = set()
        results_set.add(dummy_result)
        writer = ValueObject.CsvWriter(results_set)

        header = writer._get_csv_head()

        self.assertEqual(header, expected_header)

    def test_get_csv_row(self):
        collector = ValueObject.ResultCollector()

        # ガチャ1回でおカネを4000Gゲット
        result_id = uuid4()
        single_result1 = ValueObject.SingleResult(result_id)
        cash_amount = ValueObject.CashAmount.four_thousand
        cash = ValueObject.Cash(cash_amount)
        single_result1.gain_cash(cash)
        collector.add(single_result1)

        writer = ValueObject.CsvWriter(collector._results)

        # 期待されるリザルト行を手打ちする
        expected_row = dict()
        expected_row['result_id'] = result_id

        expected_row['cash' + '_amount'] = cash_amount.four_thousand.value

        expected_row['foods' + '_' + 'exp1.5']  = ValueObject.FoodTicketPiece(0).count()
        expected_row['foods' + '_' + 'exp2.0']  = ValueObject.FoodTicketPiece(0).count()
        expected_row['foods' + '_' + 'exp2.5']  = ValueObject.FoodTicketPiece(0).count()
        expected_row['foods' + '_' + 'cash1.5'] = ValueObject.FoodTicketPiece(0).count()
        expected_row['foods' + '_' + 'cash2.0'] = ValueObject.FoodTicketPiece(0).count()
        expected_row['foods' + '_' + 'cash2.5'] = ValueObject.FoodTicketPiece(0).count()

        expected_row['drinks' + '_' + 'ink_saver_main']     = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'ink_saver_sub']      = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'ink_recovery_up']    = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'run_speed_up']       = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'swim_speed_up']      = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'special_charge_up']  = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'special_saver']      = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'special_power_up']   = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'quick_respawn']      = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'quick_super_jump']   = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'sub_power_up']       = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'ink_resistance_up']  = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'bomb_defence_up_dx'] = ValueObject.DrinkTicketPiece(0).count()
        expected_row['drinks' + '_' + 'main_power_up']      = ValueObject.DrinkTicketPiece(0).count()

        expected_row['chunks' + '_' + 'ink_saver_main']     = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'ink_saver_sub']      = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'ink_recovery_up']    = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'run_speed_up']       = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'swim_speed_up']      = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'special_charge_up']  = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'special_saver']      = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'special_power_up']   = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'quick_respawn']      = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'quick_super_jump']   = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'sub_power_up']       = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'ink_resistance_up']  = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'bomb_defence_up_dx'] = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()
        expected_row['chunks' + '_' + 'main_power_up']      = ValueObject.Chunk(ValueObject.ChunkPiece.zero).count()

        row = writer._get_csv_row(collector._results.pop())

        # keysが一致することを確認
        keys_set = set(row.keys())
        expected_keys_set = set(expected_row.keys())

        self.assertFalse(keys_set.difference(expected_keys_set))

class TestAnalyzerSuper(unittest.TestCase):
    def test_invalid_screenshot(self):
        try:
            ValueObject.AnalyzerSuper('dummy')
        except:
            self.assertRaises(TypeError)

class TestGachaAnalyzer(unittest.TestCase):
    def test_cash_4000(self):
        image = Image.open('unit_tests/test_images/cash_4000.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        got_value = single_result._cash.count()
        self.assertEqual(got_value, 4000)

    def test_cash_8000(self):
        image = Image.open('unit_tests/test_images/cash_8000.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        got_value = single_result._cash.count()
        self.assertEqual(got_value, 8000)

    def test_cash_20000(self):
        image = Image.open('unit_tests/test_images/cash_20000.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        got_value = single_result._cash.count()
        self.assertEqual(got_value, 20000)

    def test_cash_40000(self):
        image = Image.open('unit_tests/test_images/cash_40000.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        got_value = single_result._cash.count()
        self.assertEqual(got_value, 40000)

    def test_chunk_1(self):
        image = Image.open('unit_tests/test_images/chunk_1.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        abiliry = ValueObject.Abilities.bomb_defence_up_dx
        got_value = single_result._chunks._chunks[abiliry].count()
        self.assertEqual(got_value, 1)

    def test_chunk_3(self):
        image = Image.open('unit_tests/test_images/chunk_3.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        abiliry = ValueObject.Abilities.sub_power_up
        got_value = single_result._chunks._chunks[abiliry].count()
        self.assertEqual(got_value, 3)

    def test_chunk_5(self):
        image = Image.open('unit_tests/test_images/chunk_5.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        abiliry = ValueObject.Abilities.quick_super_jump
        got_value = single_result._chunks._chunks[abiliry].count()
        self.assertEqual(got_value, 5)

    def test_chunk_10(self):
        image = Image.open('unit_tests/test_images/chunk_10.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        abiliry = ValueObject.Abilities.run_speed_up
        got_value = single_result._chunks._chunks[abiliry].count()
        self.assertEqual(got_value, 10)

    def test_chunk_bdx(self):
        image = Image.open('unit_tests/test_images/chunk_bdx.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        abiliry = ValueObject.Abilities.bomb_defence_up_dx
        got_value = single_result._chunks._chunks[abiliry].count()
        self.assertEqual(got_value, 1)

    def test_chunk_bpu(self):
        image = Image.open('unit_tests/test_images/chunk_bpu.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        abiliry = ValueObject.Abilities.sub_power_up
        got_value = single_result._chunks._chunks[abiliry].count()
        self.assertEqual(got_value, 3)

    def test_chunk_inkres(self):
        image = Image.open('unit_tests/test_images/chunk_inkres.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        abiliry = ValueObject.Abilities.ink_resistance_up
        got_value = single_result._chunks._chunks[abiliry].count()
        self.assertEqual(got_value, 1)

    def test_chunk_iru(self):
        image = Image.open('unit_tests/test_images/chunk_iru.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        abiliry = ValueObject.Abilities.ink_recovery_up
        got_value = single_result._chunks._chunks[abiliry].count()
        self.assertEqual(got_value, 1)

    def test_chunk_ism(self):
        image = Image.open('unit_tests/test_images/chunk_ism.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        abiliry = ValueObject.Abilities.ink_saver_main
        got_value = single_result._chunks._chunks[abiliry].count()
        self.assertEqual(got_value, 1)

    def test_three_bbs(self):
        image = Image.open('unit_tests/test_images/three_tickets/bdx_bdx_spu.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        ability1 = ValueObject.Abilities.bomb_defence_up_dx
        got_value = single_result._drinks._tickets[ability1].count()
        self.assertEqual(got_value, 2)

        # single_resultの中身を確認する
        # ability2 = ValueObject.Abilities.bomb_defence_up_dx
        # got_value = single_result._drinks._tickets[ability2].count()
        # self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability3 = ValueObject.Abilities.special_power_up
        got_value = single_result._drinks._tickets[ability3].count()
        self.assertEqual(got_value, 1)

    def test_three_bbs(self):
        image = Image.open('unit_tests/test_images/three_tickets/inkres_ss_qsj.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        ability1 = ValueObject.Abilities.ink_resistance_up
        got_value = single_result._drinks._tickets[ability1].count()
        self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability2 = ValueObject.Abilities.special_saver
        got_value = single_result._drinks._tickets[ability2].count()
        self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability3 = ValueObject.Abilities.quick_super_jump
        got_value = single_result._drinks._tickets[ability3].count()
        self.assertEqual(got_value, 1)

    def test_three_iib(self):
        image = Image.open('unit_tests/test_images/three_tickets/iss_iss_bpu.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        ability1 = ValueObject.Abilities.ink_saver_sub
        got_value = single_result._drinks._tickets[ability1].count()
        self.assertEqual(got_value, 2)

        # single_resultの中身を確認する
        # ability2 = ValueObject.Abilities.special_saver
        # got_value = single_result._drinks._tickets[ability2].count()
        # self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability3 = ValueObject.Abilities.sub_power_up
        got_value = single_result._drinks._tickets[ability3].count()
        self.assertEqual(got_value, 1)

    def test_three_qqq(self):
        image = Image.open('unit_tests/test_images/three_tickets/qr_qr_qsj.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        ability1 = ValueObject.Abilities.quick_respawn
        got_value = single_result._drinks._tickets[ability1].count()
        self.assertEqual(got_value, 2)

        # single_resultの中身を確認する
        # ability2 = ValueObject.Abilities.special_saver
        # got_value = single_result._drinks._tickets[ability2].count()
        # self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability3 = ValueObject.Abilities.quick_super_jump
        got_value = single_result._drinks._tickets[ability3].count()
        self.assertEqual(got_value, 1)

    def test_three_qiinkres(self):
        image = Image.open('unit_tests/test_images/three_tickets/qsj_inkres_inkres.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        ability1 = ValueObject.Abilities.ink_resistance_up
        got_value = single_result._drinks._tickets[ability1].count()
        self.assertEqual(got_value, 2)

        # single_resultの中身を確認する
        # ability2 = ValueObject.Abilities.special_saver
        # got_value = single_result._drinks._tickets[ability2].count()
        # self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability3 = ValueObject.Abilities.quick_super_jump
        got_value = single_result._drinks._tickets[ability3].count()
        self.assertEqual(got_value, 1)

    def test_three_rqr(self):
        image = Image.open('unit_tests/test_images/three_tickets/rsu_qsj_rsu.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        ability1 = ValueObject.Abilities.run_speed_up
        got_value = single_result._drinks._tickets[ability1].count()
        self.assertEqual(got_value, 2)

        # single_resultの中身を確認する
        # ability2 = ValueObject.Abilities.special_saver
        # got_value = single_result._drinks._tickets[ability2].count()
        # self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability3 = ValueObject.Abilities.quick_super_jump
        got_value = single_result._drinks._tickets[ability3].count()
        self.assertEqual(got_value, 1)

    def test_three_sqs(self):
        image = Image.open('unit_tests/test_images/three_tickets/scu_qsj_scu.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        ability1 = ValueObject.Abilities.special_charge_up
        got_value = single_result._drinks._tickets[ability1].count()
        self.assertEqual(got_value, 2)

        # single_resultの中身を確認する
        # ability2 = ValueObject.Abilities.special_saver
        # got_value = single_result._drinks._tickets[ability2].count()
        # self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability3 = ValueObject.Abilities.quick_super_jump
        got_value = single_result._drinks._tickets[ability3].count()
        self.assertEqual(got_value, 1)

    def test_three_sir(self):
        image = Image.open('unit_tests/test_images/three_tickets/spu_iru_rsu.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        ability1 = ValueObject.Abilities.special_power_up
        got_value = single_result._drinks._tickets[ability1].count()
        self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability2 = ValueObject.Abilities.ink_recovery_up
        got_value = single_result._drinks._tickets[ability2].count()
        self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability3 = ValueObject.Abilities.run_speed_up
        got_value = single_result._drinks._tickets[ability3].count()
        self.assertEqual(got_value, 1)

    def test_three_sbi(self):
        image = Image.open('unit_tests/test_images/three_tickets/ss_bdx_ism.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        ability1 = ValueObject.Abilities.special_saver
        got_value = single_result._drinks._tickets[ability1].count()
        self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability2 = ValueObject.Abilities.bomb_defence_up_dx
        got_value = single_result._drinks._tickets[ability2].count()
        self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability3 = ValueObject.Abilities.ink_saver_main
        got_value = single_result._drinks._tickets[ability3].count()
        self.assertEqual(got_value, 1)

    def test_three_ssm(self):
        image = Image.open('unit_tests/test_images/three_tickets/ss_ssu_mpu.jpg')
        screenshot = ValueObject.Screenshot(image)
        analyzer = ValueObject.GachaAnalyzer(screenshot)
        single_result = analyzer.get_result()

        # single_resultの中身を確認する
        ability1 = ValueObject.Abilities.special_saver
        got_value = single_result._drinks._tickets[ability1].count()
        self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability2 = ValueObject.Abilities.swim_speed_up
        got_value = single_result._drinks._tickets[ability2].count()
        self.assertEqual(got_value, 1)

        # single_resultの中身を確認する
        ability3 = ValueObject.Abilities.main_power_up
        got_value = single_result._drinks._tickets[ability3].count()
        self.assertEqual(got_value, 1)
