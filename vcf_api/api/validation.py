import re

#try for value error
def chrom_test(data : str):
    chars = ('X', 'Y', 'M')
    first = data[:3]
    second = data[3:]
    try:
        if first == "chr":
            if second in chars:
                return True
            elif int(second) <= 22:
                return True
            else:
                return False
        else:
            return False
    except ValueError:
        return False


def id_test(data : str):
    pattern = re.compile(r"rs[0-9]+", re.IGNORECASE)
    return pattern.match(data)
    

def alt_ref_test(data : str):
    allowed_chars = ('A', 'C', 'G', 'T' , '.')
    return data in allowed_chars


def pos_test(data):
    return type(data) is int


def validate_post_request(data:dict):
    keys = ('CHROM', 'POS', 'ALT', 'REF', 'ID')
    flag = False
    if type(data) is dict and all(key in data for key in keys):
        flag = all([
                chrom_test(data['CHROM']),
                pos_test(data['POS']),
                id_test(data['ID']),
                alt_ref_test(data['ALT']),
                alt_ref_test(data['REF'])
                ]) 
    return flag
        




