import pandas as pd
from io import StringIO
import gzip
def read_vcf_pandas(vcf_file):
    lines = []
    with gzip.open(vcf_file, 'rt') as f:
      for line in f:
        if not line.startswith("##"):
          if line.startswith("#"):
            lines.append(line)
            continue
          if line.startswith("2"): ## To filter chromsome wise, as file can be huge
            lines.append(line)
        #lines = [l for l in f if not l.startswith('##')]

    from io import StringIO
    return pd.read_csv(
        StringIO(''.join(lines)),
        sep='\t'
    )
""" below code you can use to load data in interective mode"""

#df = read_vcf_pandas("SnpEff.vcf.gz")

#print(df.head())
#print(df.columns)
