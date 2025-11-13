import sys
import os

import pandas as pd
from tqdm import tqdm

from giftwrap.utils import VisiumHDFormatInfo


def main():
    """
    Compare our barcode parsing to spaceranger-parsed barcodes.
    To run:
        1) First run extract_visiumHD_barcodes.sh to extract the barcodes from the spaceranger BAM file.
        2) The run this script with the output from the previous step as input.

    Usage: python test_visiumhd_barcode_parsing.py <input_file> [<output_file>] [<N_random_samples>]
    """
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "parsed_visiumHD_barcodes.csv"
    N_samples = int(sys.argv[3]) if len(sys.argv) > 3 else 1e10
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} does not exist.")

    tech_info = VisiumHDFormatInfo()
    df = pd.read_csv(input_file)
    # Randomize the order of the rows
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    # Limit the number of samples if specified
    if N_samples < len(df):
        df = df.head(N_samples)

    # Parse the coordinates
    df['x'] = df.Barcode.str.split('_').str[2].astype(int)
    df['y'] = df.Barcode.str.split('_').str[3].str.split('-').str[0].astype(int)

    max_error = 4  # Default maximum error for Visium HD barcodes

    # Parse the barcodes using the technology format info
    parsed = dict(
        parsed_bc=[],
        corrections=[],
        converted_bc=[],
    )
    for i, row in tqdm(df.iterrows(), total=len(df), desc="Parsing barcodes"):
        barcode, corrections = tech_info.correct_barcode(
            row['R1'],
            max_error,
            start_idx=0,
            end_idx=len(row['R1']),
        )
        if barcode is None:
            # If correction failed, use the original padded barcode
            parsed['parsed_bc'].append('')
            parsed['corrections'].append(-1)
            parsed['converted_bc'].append('')
        else:
            coordinate_x, coordinate_y = tech_info.barcode2coordinates(barcode)
            converted = tech_info.make_barcode_string(barcode, x_coord=coordinate_x, y_coord=coordinate_y, is_multiplexed=False)
            parsed['parsed_bc'].append(barcode)
            parsed['corrections'].append(corrections)
            parsed['converted_bc'].append(converted)

    df = df.assign(**parsed)

    # Compute accuracy
    df['correct_final'] = df['converted_bc'] == df['Barcode']
    df['correct_parsed'] = df['parsed_bc'] == df['ID']

    print("Accuracy of final converted barcodes:", df['correct_final'].mean())
    print("Accuracy of parsed barcodes:", df['correct_parsed'].mean())

    # Save the results to a new CSV file
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")


if __name__ == '__main__':
    main()