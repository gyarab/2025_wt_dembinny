import httpx
import pandas as pd
import io
from prettytable import PrettyTable
import shutil

def print_header(text):
    columns = shutil.get_terminal_size().columns
    
    print((' ' + text + ' ').center(columns, "-"))
def print_section(text):
    columns = shutil.get_terminal_size().columns
    
    print((' ' + text + ' ').center(columns, "."))


codes = ['EUR', 'USD']

r = httpx.get("https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt")

data = r.text
data = data.splitlines()
info = data.pop(0)
data = "\n".join(data)
df = pd.read_csv(io.StringIO(data), sep="|", decimal=",", header="infer")

print(info)
print(df.head())

print(df[df['kód'] == 'EUR'])

print_header('Převodník')
print('Měny platné od: ', info)

x = PrettyTable()

x.title = 'Důležité měny'

x.field_names = ['Měna', 'Kód', 'Množství', 'Kurz']
x.add_rows(df[df['kód'].isin(codes)][['měna', 'kód', 'množství', 'kurz']].values.tolist())

x.align["Země"] = "l"
x.align["Kurz"] = "r"

print(x)


def main_menu(df):
    def input_currency():
        inp = input('Zadejte měnu: ')
        kurz = None
        if df['kód'].isin([inp.upper()]).any():
            kurz = df[df['kód'] == inp.upper()]
            print(df[df['kód'] == inp.upper()])
        elif df['měna'].isin([inp]).any():
            kurz = df[df['měna'] == inp]
            print(df[df['měna'] == inp])
        else:
            print('Měna nenalezena.')

        return kurz

    def input_amount():
        val = input('Zadejte částku: ')
        if not val.replace('.', '', 1).isdigit():
            print('Neplatná částka.')
            return None
        return float(val.replace(',', '.'))

    def input_amount_currency(currency):
        val = input(f'Zadejte částku v { currency }: ')
        if not val.replace('.', '', 1).isdigit():
            print('Neplatná částka.')
            return None
        return float(val.replace(',', '.'))

    def convert_to_czk(amount, currency):
        kurz = df[df['kód'] == currency]
        if kurz.empty:
            print('Měna nenalezena.')
            return None
        return amount * kurz['kurz'].values[0] / kurz['množství'].values[0]

    def convert_from_czk(amount, currency):
        kurz = df[df['kód'] == currency]
        if kurz.empty:
            print('Měna nenalezena.')
            return None
        return amount * kurz['množství'].values[0] / kurz['kurz'].values[0]

    def convert_from_to(from_currency, to_currency, amount):
        czk_amount = convert_to_czk(amount, from_currency)
        if czk_amount is None:
            return None
        return convert_from_czk(czk_amount, to_currency)

    print('''
    Vyberte možnost:
    1. Zobrazit kurz
    2. Převést měnu z CZK
    3. Převést měnu na CZK
    4. Převést měnu na jinou měnu
    5. Zobrazit všechny měny
    6. Použít historické kurzy (Not yet supported)
    7. Ukončit
    ''')

    input_option = input('Zadejte číslo možnosti: ')

    match input_option:
        case '1':
            print_header('Zobrazit kurz')
            input_currency()
        case '2':
            print_header('Převést měnu z CZK')
            currency = input_currency()
            if currency is not None:
                amount = input_amount_currency('CZK')
                if amount is not None:
                    result = convert_from_czk(amount, currency['kód'].values[0])
                    print(f'{amount} CZK = {result:.2f} {currency["kód"].values[0]}')
        case '3':
            print_header('Převést měnu na CZK')
            currency = input_currency()
            if currency is not None:
                amount = input_amount_currency(currency['kód'].values[0])
                if amount is not None:
                    result = convert_to_czk(amount, currency['kód'].values[0])
                    print(f'{amount} {currency["kód"].values[0]} = {result:.2f} CZK')
        case '4':
            print_header('Převést měnu na jinou měnu')
            print_section('Zadejte měnu, ze které chcete převádět:')
            from_currency = input_currency()
            if from_currency is not None:
                amount = input_amount_currency(from_currency['kód'].values[0])
                if amount is not None:
                    print_section('Zadejte měnu, na kterou chcete převádět:')
                    to_currency = input_currency()
                    if to_currency is not None:
                        result = convert_from_to(from_currency['kód'].values[0], to_currency['kód'].values[0], amount)
                        if result is not None:
                            print(f'{amount} {from_currency["kód"].values[0]} = {result:.2f} {to_currency["kód"].values[0]}')
        case '5':
            print_header('Zobrazit všechny měny')
            print(df)
        case '6':
            def historical_exchange():
                print_header('Použít historické kurzy')
                date = input('Zadejte datum ve formátu DD.MM.RRRR: ')
                r = httpx.get("https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date=" + date)
                data = r.text

                date_info = data.splitlines().pop(0)
                date_df = pd.read_csv(io.StringIO(data), sep="|", decimal=",", header="infer", skiprows=1)
                print(date_df)
                print('Měny platné od: ', date_info)

                print(
                '''
                Vyberte možnost:
                1. Zobrazit jiný historický kurz
                2. Použít tento kurz
                3. Zpět
                ''')
                input_option_historical = input('Zadejte číslo možnosti: ')
                match input_option_historical:
                    case '1':
                        historical_exchange()
                    case '2':
                        print('Použit aktuální historický kurz...')
                        main_menu(date_df)
                    case '3':
                        pass
            historical_exchange()

        case '7':
            print_header('Ukončit')
            exit()

# python -m venv .venv
# source .venv/bin/activate
# pip install httpx

main_menu(df)

'''
22.01.2026 #15
země|měna|množství|kód|kurz
Austrálie|dolar|1|AUD|14,133
Brazílie|real|1|BRL|3,905
Čína|žen-min-pi|1|CNY|2,976
Dánsko|koruna|1|DKK|3,254
'''