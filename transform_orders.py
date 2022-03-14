import os
import sys
from typing import TextIO
import numpy as np
import pandas as pd

# name csv file
FILENAME_ORDERS_CSV = "orders.csv"
# name of output folder
FOLDER_OUTPUT = "output"
# filename output
FILENAME_OUTPUT = "orders_transformiert.csv"
# renaming of cols
RENAMING = {'createdOn': 'erstellt_datum', 'modifiedBy': 'bearbeitet_von', 'modifiedOn': 'bearbeitet_datum',
            'remarks': 'bemerkungen', 'state': 'status', 'shipper': 'ladeadresse', 'receiver': 'lieferadresse',
            'principal': 'auftraggeber', 'deliveryDate': 'liefer_datum', 'pickUpDate': 'lade_datum',
            'owner': 'besitzer', 'rasterLagerplatzPickUp': 'rasterLagerplatz_laden', 'anlagePickUp': 'anlage_laden',
            'rasterLagerplatz': 'rasterLagerplatz_liefern', 'anlage': 'anlage_liefern',
            'deliveryOnly': 'nur_anlieferung', 'construction': 'spez_leistung_mit_fhrz', 'goods': 'warentransport',
            'people': 'personentransport', 'costTrpExternal': 'trp_konsten_extern', 'cbm': 'm^3',
            'totalweight': 'gewicht_total', 'deliveryTime': 'liefer_zeit', 'pickUpTime': 'lade_zeit',
            'principal_name': 'auftraggeber_name', 'principal_street': 'auftraggeber_strasse',
            'principal_zipcode': 'auftraggeber_plz', 'principal_place': 'auftraggeber_ort',
            'principal_email': 'auftraggeber_email', 'principal_phone': 'auftraggeber_tel',
            'principal_ressort': 'auftraggeber_ressort', 'principal_bereich': 'auftraggeber_bereich',
            'receiver_name': 'lieferadresse_name', 'receiver_street': 'lieferadresse_strasse',
            'receiver_zipcode': 'lieferadresse_plz', 'receiver_place': 'lieferadresse_ort',
            'receiver_email': 'lieferadresse_email', 'receiver_phone': 'lieferadresse_tel',
            'shipper_name': 'ladeadresse_name', 'shipper_street': 'ladeadresse_strasse',
            'shipper_zipcode': 'ladeadresse_plz', 'shipper_place': 'ladeadresse_ort',
            'shipper_email': 'ladeadresse_email', 'shipper_phone': 'ladeadresse_tel',
            'pos_1_goods_dangerousGoods': 'pos_1_warentransport_gefahrgut',
            'pos_1_goodsDescription': 'pos_1_warentransport_beschreibung',
            'pos_1_goods_grossWeight': 'pos_1_warentransport_brutto_gewicht',
            'pos_1_goods_netWeight': 'pos_1_warentransport_netto_gewicht',
            'pos_1_goods_length': 'pos_1_warentransport_laenge', 'pos_1_goods_width': 'pos_1_warentransport_breite',
            'pos_1_goods_height': 'pos_1_warentransport_hoehe',
            'pos_1_goods_packingUnit': 'pos_1_warentransport_verpackungseinheit',
            'pos_1_goods_marking': 'pos_1_warentransport_markierung',
            'pos_1_goods_quantity': 'pos_1_warentransport_quantiaet',
            'pos_1_goods_valueChf': 'pos_1_warentransport_warenwert_chf',
            'pos_1_goods_kommissionieren': 'pos_1_warentransport_kommissioniern',
            'pos_1_goods_stapelbar': 'pos_1_warentransport_stapelbar',
            'pos_1_const_description': 'pos_1_spez_leistung_mit_fhrz_beschreibung',
            'pos_1_const_quantity': 'pos_1_spez_leistung_mit_fhrz_quantitaet',
            'pos_1_const_weight': 'pos_1_spez_leitung_mit_fhrz_gewicht'}


def main() -> int:
    root_directory = create_file_paths()
    check_if_file_exists(root_directory)
    df_orders = pd.read_csv(root_directory + os.sep + FILENAME_ORDERS_CSV, dtype=str)
    # rename cols
    df_orders.rename(
        columns=RENAMING, inplace=True)
    tageszeit_liefer(df_orders)
    tageszeit_laden(df_orders)
    # shorten plz to 3 decimal points
    df_orders['auftraggeber_plz_kurz'] = df_orders.auftraggeber_plz.str.slice(start=0, stop=3)
    df_orders['ladeadresse_plz_kurz'] = df_orders.ladeadresse_plz.str.slice(start=0, stop=3)
    df_orders['lieferadresse_plz_kurz'] = df_orders.lieferadresse_plz.str.slice(start=0, stop=3)
    df_orders_with_titles = df_orders.copy()
    # put titles of cols into the rows of df
    for col in df_orders.columns:
        df_orders_with_titles[col] = col + ": " + df_orders_with_titles[col]
    # add suffix for rows with title in it
    df_orders_with_titles = df_orders_with_titles.add_suffix("_mit_titel")
    # concat both df
    df_orders_final = pd.concat([df_orders, df_orders_with_titles], axis=1)
    check_if_output_folder_exists(root_directory)
    # save transformed data
    # existing files will be overridden
    df_orders_final.to_csv(root_directory + os.sep + FOLDER_OUTPUT + os.sep + FILENAME_OUTPUT)
    # only works if xlsxwirter is installed
    # df_orders_final.to_excel(FOLDER_OUTPUT + "//orders_transformiert.xlsx", engine="xlsxwriter")
    return 0


def create_file_paths() -> str:
    pathname = os.path.dirname(sys.argv[0])
    return os.path.abspath(pathname)


def check_if_file_exists(root_dir):
    try:
        f: TextIO = open(root_dir + os.sep + FILENAME_ORDERS_CSV)
    except IOError:
        print("Kann orders.csv nicht finden... Stelle sicher, dass sich orders.csv im gleichen Verzeichnis befindet.")
    finally:
        f.close()
    return 0


def check_if_output_folder_exists(root_dir):
    # check if output folder exists
    is_exist = os.path.exists(root_dir + os.sep + FOLDER_OUTPUT)
    # if it not exists creat it
    if not is_exist:
        os.makedirs(root_dir + os.sep + FOLDER_OUTPUT)
        print("Created output directory")


def tageszeit_liefer(df_orders):
    # condition for tageszeit morgen 7-11:59, abend 12-19:59, nacht 20:00-6:59, egal 00:00
    conditions_liefern = [(pd.to_numeric(df_orders['liefer_zeit'].str.slice(start=0, stop=2)) >= 7) & (
            pd.to_numeric(df_orders['liefer_zeit'].str.slice(start=0, stop=2)) < 12),
                          (pd.to_numeric(df_orders['liefer_zeit'].str.slice(start=0, stop=2)) >= 12) & (
                                  pd.to_numeric(df_orders['liefer_zeit'].str.slice(start=0, stop=2)) < 20),
                          (pd.to_numeric(df_orders['liefer_zeit'].str.slice(start=0, stop=2)) >= 20) & (
                                  pd.to_numeric(df_orders['liefer_zeit'].str.slice(start=0, stop=2)) <= 23),
                          (pd.to_numeric(df_orders['liefer_zeit'].str.slice(start=0, stop=2)) > 00) & (
                                  pd.to_numeric(df_orders['liefer_zeit'].str.slice(start=0, stop=2)) < 7),
                          (pd.to_numeric(df_orders['liefer_zeit'].str.slice(start=0, stop=2)) == 00) & (
                                  pd.to_numeric(df_orders['liefer_zeit'].str.slice(start=3, stop=5)) == 00)]
    # values to set for condition
    values = ['morgen', 'abend', 'nacht', 'nacht', 'egal']

    # add tageszeit col for liefer_zeit
    df_orders['liefer_tagesszeit'] = np.select(conditions_liefern, values)


def tageszeit_laden(df_orders):
    # condition for tageszeit morgen 7-11:59, abend 12-19:59, nacht 20:00-6:59, egal 00:00
    conditions_laden = [(pd.to_numeric(df_orders['lade_zeit'].str.slice(start=0, stop=2)) >= 7) & (
            pd.to_numeric(df_orders['lade_zeit'].str.slice(start=0, stop=2)) < 12),
                        (pd.to_numeric(df_orders['lade_zeit'].str.slice(start=0, stop=2)) >= 12) & (
                                pd.to_numeric(df_orders['lade_zeit'].str.slice(start=0, stop=2)) < 20),
                        (pd.to_numeric(df_orders['lade_zeit'].str.slice(start=0, stop=2)) >= 20) & (
                                pd.to_numeric(df_orders['lade_zeit'].str.slice(start=0, stop=2)) <= 23),
                        (pd.to_numeric(df_orders['lade_zeit'].str.slice(start=0, stop=2)) > 00) & (
                                pd.to_numeric(df_orders['lade_zeit'].str.slice(start=0, stop=2)) < 7),
                        (pd.to_numeric(df_orders['lade_zeit'].str.slice(start=0, stop=2)) == 00) & (
                                pd.to_numeric(df_orders['lade_zeit'].str.slice(start=3, stop=5)) == 00)]
    # values to set for condition
    values = ['morgen', 'abend', 'nacht', 'nacht', 'egal']

    # add tageszeit col for lade_zeit
    df_orders['lade_tagesszeit'] = np.select(conditions_laden, values)


if __name__ == '__main__':
    sys.exit(main())
