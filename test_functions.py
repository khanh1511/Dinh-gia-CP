import sys
import io
import warnings

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
warnings.simplefilter(action='ignore', category=FutureWarning)

from data_loader import fetch_financial_ratio

ratios_df = fetch_financial_ratio("FPT")
print("Type of Columns:", type(ratios_df.columns))
print("Columns:", ratios_df.columns.tolist()[:10])
print("Type of Index:", type(ratios_df.index))
print("Index:", ratios_df.index.tolist()[:10])
print("Head:")
print(ratios_df.head(3))
