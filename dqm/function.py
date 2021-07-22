from dqm.models import MetaData
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def get_data_sources_name():
    sources = MetaData.query.all()
    sources_name = []
    for value in sources:
        sources_name.append((value, value))

    return sources_name

# general func - get separator of csv file
def get_separator(file_name: str):
    with open('datas/' + file_name, "r", encoding="utf-8") as file:
        line = file.readline()
        if ',' in line:
            delimiter = ','
        elif ';' in line:
            delimiter = ';'
        else:
            pass

    return delimiter


def fuzzy_merge(df_1, df_2, key1, key2, threshold=90, limit=2):
    """
    :param df_1: the left table to join
    :param df_2: the right table to join
    :param key1: key column of the left table
    :param key2: key column of the right table
    :param threshold: how close the matches should be to return a match, based on Levenshtein distance
    :param limit: the amount of matches that will get returned, these are sorted high to low
    :return: dataframe with boths keys and matches
    """

    # TODO: convert int/float cols into string

    s = df_2[key2].tolist()
    m = df_1[key1].apply(lambda x: process.extract(x, s, limit=limit))
    df_1['matches'] = m

    m2 = df_1['matches'].apply(lambda x: ', '.join([i[0] for i in x if i[1] >= threshold]))
    df_1['matches'] = m2

    df = pd.merge(left=df_1, right=df_2, left_on='matches', right_on=key2, suffixes=('_left', '_right'))
    df.drop(columns=['matches'], axis=1, inplace=True)
    print(df.head())
    return df

def get_datetime_cols(df:pd.DataFrame):
    df_time_cols = []
    for i in range(0, len(df.columns)):
        # print("--------------")
        # print(str(i + 1) + "/" + str(len(df.columns)) + " " + df.columns[i])

        try:
            tmp_val = df[df.columns[i]].first_valid_index()

            try:
                if (type(int(df[df.columns[i]][tmp_val])) in [int, float]):
                    pass
                    # print("Szám formátum")

            except:
                tmp_val_len = len(str(df[df.columns[i]][tmp_val]))
                # print("Nem szám formátum")
                if (tmp_val_len > 5):
                    df[df.columns[i]] = pd.to_datetime(df[df.columns[i]])
                    df_time_cols.append(df.columns[i])
                    # print("Datetimera konvertálva")
                else:
                    pass
                    # print("Nem konvertálható Datetimera")

                if (tmp_val_len < 12):
                    df[df.columns[i]] = df[df.columns[i]].dt.date
                    # print("Dátummá alakítva")
                # print("Konvertálva: " + str(df[df.columns[i]][tmp_val]))

        except:
            if df.columns[i] in df_time_cols:
                pass
            else:
                pass
                # print("Szöveges mező")

    return df, df_time_cols

def get_numeric_cols(df:pd.DataFrame, df_time_cols):
    num_types = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    df_num_cols = df.select_dtypes(include=num_types).columns
    df_num_cols = list(set(df_num_cols) - set(df_time_cols))
    return df_num_cols

def get_character_cols(df: pd.DataFrame):
    df_char_cols = df.select_dtypes(include=['object']).columns
    return df_char_cols

def get_summary(df: pd.DataFrame):
    """
    Count column types using previously defined function then create statistics from the input dataframe
    """

    # get datetime columns and convert them
    df, df_time_cols = get_datetime_cols(df)

    # get numeric columns
    df_num_cols = get_numeric_cols(df, df_time_cols)

    # get character columns
    df_char_cols = get_character_cols(df)

    # Null value stats
    comp = df.shape[1] - df.apply(lambda x: x.count(), axis=1)  # NA values in the row
    uni_row = df.drop_duplicates().shape[0]  # unique rows

    if ((comp).unique()[-1] == 0):  # if 0 is the first, then the dataset has rows without NA
        comp_cnt = comp.value_counts()[0]
        comp_pct = comp.value_counts(1)[0]
    else:
        comp_cnt = 0
        comp_pct = 0

    # Create EDA statistics table
    df_tmp = [str(round(df.shape[1], 0)),
              str(df.shape[0]),
              str(round(uni_row, 0)),
              str(round(uni_row / df.shape[0]*100, 3))+'%',
              str(round(comp_cnt, 0)),
              str(round(comp_pct*100, 3))+'%',
              str(round(df.shape[0] - comp_cnt, 0)),
              str(round((1 - comp_pct)*100, 3))+'%']

    df_data = {'Tulajdonság': ['Oszlopok száma',
                           'Sorok száma',
                           'Egyedi sorok száma',
                           'Egyedi sorok aránya',
                           'Kitöltött sorok száma',
                           'Kitöltött sorok aránya',
                           'Hiányzó sorok száma',
                           'Hiányzó sorok aránya'],
               'Érték': df_tmp}
    df_data = pd.DataFrame(df_data)
    return df_data





