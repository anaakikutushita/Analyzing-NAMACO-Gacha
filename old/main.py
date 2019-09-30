# coding: utf-8
"""
NAMACOポイントガチャの排出率を計算する。
ガチャ結果のスクショは./input_imagesに配置する
"""

from pathlib import Path
import uuid
import cv2
import GachaResultDetecter
import GachaResults
import ResultSaver

def main():
    """entry point"""
    input_dir = Path('./input_images/')
    input_paths = set(input_dir.glob('*.jpg'))
    gacha_results = GachaResults.AllResultContainer()
    detecter = GachaResultDetecter.Detecter()
    for input_path in input_paths:
        mat = cv2.imread(str(input_path))
        id = uuid.uuid4()
        result = detecter.detect(id, mat)
        gacha_results.add(result)
    csv_result = gacha_results.get_csv()
    ResultSaver.save(csv_result)

if __name__ == '__main__':
    main()