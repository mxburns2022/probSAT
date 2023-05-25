from argparse import ArgumentParser
from pathlib import Path
import pandas as pd
import glob
import os


def identity(x):
    return x


stat_map = {
    'name':            ('Problem', lambda x: Path(x).stem),
    'variables':      ('N', lambda x: int(x)),
    'clauses':        ('M', lambda x: int(x)),
    'using:':         ('Function', identity),
    'maxTries':      ('maxTries', lambda x: int(x)),
    'maxFlips':      ('maxFlips', lambda x: int(x)),
    'cm':      ('cm', lambda x: float(x)),
    'cb':      ('cb', lambda x: float(x)),
    'seed':      ('seed', lambda x: int(x)),
    'numFlips':      ('Flips', lambda x: int(x)),
    'Time':      ('Time', lambda x: float(x)),
    'UNKNOWN':      ('SAT', lambda x: False)}


def get_file_df(fpath: str) -> pd.DataFrame:
    """Parse a single file and store as a dataframe

    Args:
        fpath (str): Path to probSAT output
    """
    assert os.path.exists(fpath)
    result_dict = {
        'Problem': [],
        'N': [],
        'M': [],
        'Function': [],
        'maxTries': [],
        'maxFlips': [],
        'cm': [],
        'cb': [],
        'seed': [],
        'Flips': [],
        'Time': [],
        'SAT': []
    }
    with open(fpath) as resultfile:
        for line in resultfile.readlines():
            linewords = line.strip().split()
            if len(linewords) < 1:
                continue
            if linewords[0] == 'c':
                for i, word in enumerate(linewords[1:]):
                    if word in stat_map:
                        if (word == 'using:' and
                            (len(linewords) < i+4 or
                             linewords[i+4] != 'function')):
                            continue
                        col, func = stat_map[word]
                        result_dict[col].append(func(linewords[i+3]))
                        break
            if linewords[0] == 's' and linewords[1] == 'SATISFIABLE':
                result_dict['SAT'].append(True)
    return pd.DataFrame.from_dict(result_dict)


def loop_file_df(result_path: str, simname: str, outpath: str = None):
    file_list = glob.glob(os.path.join(
                          result_path,
                          'probSAT',
                          simname,
                          "*",  # all configurations for SIM
                          "*",  # work directories
                          "*",  # problem classes (e.g. cust-u1000-4250)
                          "*",  # problem instances (e.g. cust-u1000-01.cnf)
                          "*",  # individual runs (e.g. '000')
                          "*.run.*"))
    dflist = []
    for f in file_list:
        dflist.append(get_file_df(f))
    result_df = pd.concat(dflist)
    if outpath is not None:
        result_df.to_csv(outpath, index=False)
        print('Wrote output to {}'.format(
            os.path.abspath(outpath)))
    return result_df


parser = ArgumentParser()
parser.add_argument('-d', '--dir',
                    dest='result_dir',
                    required=True,
                    help='Path to result directory' +
                    ' (e.g. /scratch/mhuang_lab/mburns13/SAT_RESULTS)')
parser.add_argument('-s', '--sim',
                    dest='sim',
                    required=True,
                    help='Name of simulation' +
                    ' (e.g. sim000_example_test_name)')
parser.add_argument('-o', '--out',
                    dest='out',
                    required=True,
                    help='Output path for CSV' +
                         ' (e.g. /scratch/mhuang_lab/' +
                         'mburns13/data/probsat_results.csv)')
if __name__ == '__main__':
    args = parser.parse_args()
    loop_file_df(args.dir, args.sim, args.out)
