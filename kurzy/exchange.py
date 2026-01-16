import httpx
import pandas as pd

r = httpx.get("https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt")

data = r.text
df = pd.read_csv(pd.compat.StringIO(data), sep="|", header=None)

print(df.head())

# python -m venv .venv
# source .venv/bin/activate
# pip install httpx
