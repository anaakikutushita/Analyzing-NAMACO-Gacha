# coding: utf-8

from pathlib import Path
import ValueObject

def main():
    """entry point"""
    input_dir = Path('./input_images/')
    input_paths = ValueObject.PathCollecter(input_dir)
    input_screenshots = input_paths.get_screenshots()
    gacha_results = input_screenshots.get_result_collection()
    gacha_results.output_csv()

if __name__ == '__main__':
    main()
