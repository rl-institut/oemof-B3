import sys
import pandas as pd

in_path = sys.argv[1]
out_path = sys.argv[2]

if __name__ == '__main__':
    opsd = pd.read_csv(in_path)
    b3 = opsd[opsd.state.isin(['Brandenburg', 'Berlin'])]
    b3.to_csv(out_path, index=False)