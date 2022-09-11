from importlib.resources import path
import io
import os
import pandas as pd
from pathlib import Path
import re
import sys

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
            dtype={'#CHROM': str, 'POS': str, 'ID': str, 'REF': str, 'ALT': str,}, sep='\t').rename(columns={'#CHROM': 'CHROM'})
    except OSError as e:
        print(f"Unable to open {path}: {e}", file=sys.stderr)
        return
    except UnicodeDecodeError as e:
        print(f"Unable to open {path}, invalid file encoding: {e}", file=sys.stderr)
    except pd.errors.EmptyDataError as e:
        print(f"Unable to parse data, file at {path} is empty: {e}",file=sys.stderr)
        return pd.DataFrame()
    else:
        df = df[['CHROM', 'POS', 'ID', 'REF', 'ALT']].copy()
        df = df.replace('.', float('NaN')).copy()
        df = df.replace(pattern, float('NaN'), regex = True)
        df.dropna(subset = ['ID'], inplace = True)
        df = df.reset_index(drop=True)
        return df

