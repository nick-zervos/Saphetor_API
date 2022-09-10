from importlib.resources import path
import io
import os
import pandas as pd
from pathlib import Path
import re

#get dynamic file path at the root of the project named file.vcf
file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')


#function to parse the file into a pandas DataFrame while ignoring the lines starting with ## and then returning only the 5 columns that we want. Also checks for empty ID fields and discards those rows.
def read_vcf(path):
    pattern = re.compile(r"rs[0-9]+;rs[0-9]+", re.IGNORECASE)
    try:
        with open(path, 'r') as f:
            lines = [l for l in f if not l.startswith('##')]
            df = pd.read_csv(
            io.StringIO(''.join(lines)),
            dtype={'#CHROM': str, 'POS': int, 'ID': str, 'REF': str, 'ALT': str,}, sep='\t').rename(columns={'#CHROM': 'CHROM'})
    except FileNotFoundError:
        raise FileNotFoundError('File does not exist or has wrong name. Make sure it is "file.vcf" ')
    else:
        df = df[['CHROM', 'POS', 'ID', 'REF', 'ALT']].copy()
        df = df.replace('.', float('NaN')).copy()
        df = df.replace(pattern, float('NaN'), regex = True)
        df.dropna(subset = ['ID'], inplace = True)
        df = df.reset_index(drop=True)
        return df

# def get_header(path):
#     with open(path, 'r') as f:
#         header = [l for l in f if l.startswith('##')]
#         print(header)
#         return header


# header = get_header(file_path)

# my_file = read_vcf(file_path)
# print(my_file)


