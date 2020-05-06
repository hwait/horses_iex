import pandas as pd
df = pd.read_csv('data/races/races_{}.csv'.format('2020-01-30'))
import sys


def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

print(is_venv())