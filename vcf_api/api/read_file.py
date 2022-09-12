from cmath import nan
from importlib.resources import path
import io
import os
import pandas as pd
from pathlib import Path
import re
import sys

#get dynamic file path at the root of the project named file.vcf
file_path = os.path.join(Path(__file__).resolve().parent.parent.parent, 'file.vcf')


#function to parse the file into a pandas DataFrame while ignoring the lines starting with ## and then returning only the 5 columns that we want.
def read_vcf(path):
    pattern = re.compile(r"rs[0-9]+;rs[0-9]+", re.IGNORECASE)
    try:
        with open(path, 'r') as f:
            lines = [l for l in f if not l.startswith('##')]
            df = pd.read_csv(
            io.StringIO(''.join(lines)),
            dtype={'#CHROM': str, 'POS': str, 'ID': str, 'REF': str, 'ALT': str,}, sep='\t').rename(columns={'#CHROM': 'CHROM'})
    #Error handling
    except OSError as e:
        print(f"Unable to open {path}: {e}", file=sys.stderr)
        return
    except UnicodeDecodeError as e:
        print(f"Unable to open {path}, invalid file encoding: {e}", file=sys.stderr)
    except pd.errors.EmptyDataError as e:
        print(f"Unable to parse data, file at {path} is empty: {e}",file=sys.stderr)
        return pd.DataFrame()
    except pd.errors.ParserError as e:
        print(f"Unable to parse data, file at {path} is empty: {e}",file=sys.stderr)
        return pd.DataFrame()
    else:
        df = df[['CHROM', 'POS', 'ID', 'REF', 'ALT']].copy()
        df = df.reset_index()
        return df


#Function to keep only the header part of the vcf file, so that when saving we can keep this part stable and append the "body" that we are manipulating
def get_vcf_header(path):
    try:
        with open(path, 'r') as f:
            lines = [l for l in f if l.startswith('##')]
            df = pd.read_csv(
            io.StringIO(''.join(lines)),
            sep='\t', header=None)
    except OSError as e:
        print(f"Unable to open {path}: {e}", file=sys.stderr)
        return
    except UnicodeDecodeError as e:
        print(f"Unable to open {path}, invalid file encoding: {e}", file=sys.stderr)
    except pd.errors.EmptyDataError as e:
        print(f"Unable to parse data, file at {path} is empty: {e}",file=sys.stderr)
        return pd.DataFrame()
    else:
        return df



#for cases where we need all the columns (such as the PUT and DELETE methods) we use this function to pass all the columns of the file into a DataFrame. This way we can manipulate the 5 columns that we desire and keep the rest of the data intact
def read_original_vcf(path):
    try:
        with open(path, 'r') as f:
            lines = [l for l in f if not l.startswith('##')]
            df = pd.read_csv(
            io.StringIO(''.join(lines)), sep='\t', low_memory=False).rename(columns={'#CHROM': 'CHROM'})
    except OSError as e:
        print(f"Unable to open {path}: {e}", file=sys.stderr)
        return
    except UnicodeDecodeError as e:
        print(f"Unable to open {path}, invalid file encoding: {e}", file=sys.stderr)
    except pd.errors.EmptyDataError as e:
        print(f"Unable to parse data, file at {path} is empty: {e}",file=sys.stderr)
        return pd.DataFrame()
    else:
        df = df.fillna('')
        return df