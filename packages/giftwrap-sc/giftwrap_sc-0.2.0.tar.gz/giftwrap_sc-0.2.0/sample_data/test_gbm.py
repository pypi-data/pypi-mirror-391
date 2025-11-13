import sys
import os
import gzip

import pandas as pd
from tqdm import tqdm
from Bio.SeqIO.QualityIO import FastqGeneralIterator
from line_profiler import LineProfiler
from giftwrap.utils import VisiumHDFormatInfo


def main():
    data = "20250815_GBM_5b_GapFill_S6_L001_R1_001.fastq.gz"

    tech_info = VisiumHDFormatInfo(
        space_ranger_path="/Users/austinv11/PycharmProjects/giftwrap/spaceranger-4.0.1/bin/"
    )

    total = 0
    corrected = 0
    missing = 0
    try:
        for title, seq, qual in tqdm(FastqGeneralIterator(gzip.open(data, "rt")), desc="Processing reads"):
            # Correct the barcode
            bc, corrections = tech_info.correct_barcode(
                seq,
                max_mismatches=4,
                start_idx=0,
                end_idx=len(seq),
            )
            total += 1
            if bc is None:
                # print("Correction failed, no valid barcode found.")
                missing += 1
                continue

            if corrections > 0:
                corrected += 1

            # Convert the barcode to coordinates
            # coordinate_x, coordinate_y = tech_info.barcode2coordinates(bc)

            # Create the converted barcode string
            # converted = tech_info.make_barcode_string(bc, x_coord=coordinate_x, y_coord=coordinate_y, is_multiplexed=False)

            # print(f"Original: {seq}, Corrected: {bc}, Converted: {converted}, Was Corrected: {was_corrected}")
            # tqdm.write(f"Original: {seq}, Corrected: {bc}, Converted: {converted}, Was Corrected: {was_corrected}")
    except KeyboardInterrupt:
        print("Processing interrupted by user.")

    print(f"Exact: {(total - corrected - missing)/total * 100:.2f}%, Corrected: {corrected/total * 100:.2f}%, Missing: {missing/total * 100:.2f}% of {total} reads processed.")


if __name__ == '__main__':
    # PATH="~/PycharmProjects/giftwrap/spaceranger-4.0.1/bin/:$PATH" py-spy record -o profile.svg -- python test_gbm.py
    main()