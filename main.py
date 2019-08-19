# coding: utf-8
"""
NAMACOポイントガチャの排出率を計算する。
ガチャ結果のスクショは./input_imagesに配置する
"""

from pathlib import Path
import cv2
import GachaResultDetecter
import GachaResults

def main():
    """entry point"""
    input_dir = Path('./input_images/')
    input_paths = set(input_dir.glob('*.jpg'))
    gacha_result = GachaResults.SingleResult()
    for input_path in input_paths:
        mat = cv2.imread(str(input_path))
        result = GachaResultDetecter.detect(mat)
        gacha_result.add(result)
    final_result = gacha_result.show()
    print(final_result)

if __name__ == '__main__':
    main()