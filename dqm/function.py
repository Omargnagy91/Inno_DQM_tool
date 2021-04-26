import pandas as pd
import numpy as np

def get_datetime_cols(df:pd.DataFrame):
    df_time_cols = []
    for i in range(0, len(df.columns)):
        print("--------------")
        print(str(i + 1) + "/" + str(len(df.columns)) + " " + df.columns[i])

        try:
            tmp_val = df[df.columns[i]].first_valid_index()

            try:
                if (type(int(df[df.columns[i]][tmp_val])) in [int, float]):
                    print("Szám formátum")

            except:
                tmp_val_len = len(str(df[df.columns[i]][tmp_val]))
                print("Nem szám formátum")
                if (tmp_val_len > 5):
                    df[df.columns[i]] = pd.to_datetime(df[df.columns[i]])
                    df_time_cols.append(df.columns[i])
                    print("Datetimera konvertálva")
                else:
                    print("Nem konvertálható Datetimera")

                if (tmp_val_len < 12):
                    df[df.columns[i]] = df[df.columns[i]].dt.date
                    print("Dátummá alakítva")
                print("Konvertálva: " + str(df[df.columns[i]][tmp_val]))

        except:
            if df.columns[i] in df_time_cols:
                pass
            else:
                print("Szöveges mező")

    return df, df_time_cols

def get_numeric_cols(df:pd.DataFrame, df_time_cols):
    num_types = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    df_num_cols = df.select_dtypes(include=num_types).columns
    print(df_num_cols)
    df_num_cols = list(set(df_num_cols) - set(df_time_cols))
    # df_num = df[df_num_cols]
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





