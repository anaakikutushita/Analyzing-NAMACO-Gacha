# coding: utf-8

from pathlib import Path
import datetime
import ValueObject

def main():
    """entry point"""
    input_dir = Path('input_screenshots')
    input_paths = ValueObject.PathCollector(input_dir)
    gacha_results = input_paths.analyze_each()

    now = datetime.datetime.today().strftime('%Y-%m-%d_%H%M')
    file_name = 'result_' + now + '.csv'
    gacha_results.output_csv(output_dst=file_name)

if __name__ == '__main__':
    main()
