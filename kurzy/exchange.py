import httpx
import pandas as pd
import io
from prettytable import PrettyTable
import shutil
import sys

# --- HELPER FUNCTIONS ---
def print_header(text, char="-"):
    columns = shutil.get_terminal_size().columns
    print((' ' + text + ' ').center(columns, char))

def load_data(date=None):
    """Fetches data from CNB. Returns (info_string, dataframe) or None on error."""
    url = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt"
    params = {}
    if date:
        params = {'date': date}
    
    try:
        r = httpx.get(url, params=params)
        r.raise_for_status() # Check for 404/500 errors
        
        data = r.text.splitlines()
        info = data.pop(0) # Extract date info
        csv_data = "\n".join(data)
        
        # Parse CSV
        df = pd.read_csv(io.StringIO(csv_data), sep="|", decimal=",", header="infer")
        
        # OPTIMIZATION: Set 'kód' as index for instant lookups
        df['kód'] = df['kód'].str.strip() # clean whitespace just in case
        df.set_index('kód', inplace=True) 
        
        return info, df
        
    except Exception as e:
        print(f"Chyba při stahování dat: {e}")
        return None, None

def print_table(df, codes=None):
    x = PrettyTable()
    x.field_names = ['Kód', 'Země', 'Měna', 'Množství', 'Kurz']
    
    # If specific codes are requested, filter using .loc (faster)
    if codes:
        # Filter only codes that actually exist in the index
        valid_codes = [c for c in codes if c in df.index]
        subset = df.loc[valid_codes]
    else:
        subset = df

    # Iterate over the dataframe to add rows
    for code, row in subset.iterrows():
        x.add_row([code, row['země'], row['měna'], row['množství'], row['kurz']])

    x.align["Země"] = "l"
    x.align["Kurz"] = "r"
    print(x)

# --- CONVERSION LOGIC ---
def get_rate(df, code):
    """Safely gets rate components. Returns (quantity, rate) or None."""
    try:
        row = df.loc[code.upper()]
        return row['množství'], row['kurz']
    except KeyError:
        print(f"Měna {code} nenalezena.")
        return None

def convert(amount, from_code, to_code, df):
    # 1. Get Source Data
    source = get_rate(df, from_code)
    if not source: return None
    src_qty, src_rate = source

    # 2. Get Target Data
    target = get_rate(df, to_code)
    if not target: return None
    target_qty, target_rate = target

    # 3. Math: (Amount * Rate / Qty) = CZK Value
    val_in_czk = amount * (src_rate / src_qty)
    
    # 4. Math: (CZK / Rate * Qty) = Target Value
    final_val = val_in_czk / target_rate * target_qty
    
    return final_val

# --- MAIN APP ---
def main():
    print_header("Načítání dat...")
    info, df = load_data()
    
    if df is None:
        return # Exit if internet is down

    # Main application loop
    while True:
        print_header('Převodník měn CNB', "=")
        print(f'Kurzy platné pro: {info}')
        
        print('''
    1. Rychlý přehled (EUR, USD)
    2. Převodník (Cokoliv -> Cokoliv)
    3. Zobrazit kompletní tabulku
    4. Změnit datum (Historie)
    5. Ukončit
        ''')

        choice = input('Vaše volba: ')

        if choice == '1':
            print_table(df, codes=['EUR', 'USD', 'GBP'])
            input("\nStiskněte Enter pro pokračování...")

        elif choice == '2':
            print_header("Převodník")
            try:
                amt = float(input("Částka: ").replace(",", "."))
                curr_from = input("Z měny (kód, např. CZK, EUR): ").upper()
                curr_to = input("Na měnu (kód, např. USD): ").upper()

                # Handle CZK logic manually since it's not in the table
                if curr_from == 'CZK' and curr_to == 'CZK':
                    res = amt
                elif curr_from == 'CZK':
                    tgt = get_rate(df, curr_to)
                    if tgt: res = amt / tgt[1] * tgt[0]
                elif curr_to == 'CZK':
                    src = get_rate(df, curr_from)
                    if src: res = amt * src[1] / src[0]
                else:
                    res = convert(amt, curr_from, curr_to, df)

                if res is not None:
                    print_header(f"{amt} {curr_from} = {res:.2f} {curr_to}")

            except ValueError:
                print("Chyba: Zadána neplatná částka.")
            
            input("\nStiskněte Enter pro pokračování...")

        elif choice == '3':
            print_table(df)
            input("\nStiskněte Enter pro pokračování...")

        elif choice == '4':
            date_input = input("Zadejte datum (DD.MM.RRRR): ")
            new_info, new_df = load_data(date_input)
            if new_df is not None:
                info = new_info
                df = new_df
                print("Historická data načtena.")
            else:
                print("Návrat k aktuálním datům.")

        elif choice == '5':
            print("Nashledanou!")
            break

if __name__ == "__main__":
    main()