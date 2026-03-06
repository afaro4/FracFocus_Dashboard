# import libraries
import sqlite3
import pandas as pd

# Load raw data

# fix datatypes when reading files
disclosure_dtype_mapping = {
    'DisclosureId': 'string',
    'JobStartDate': 'string',
    'JobEndDate': 'string',
    'APINumber': 'string',
    'StateName': 'category',
    'CountyName': 'category',
    'OperatorName': 'category',
    'WellName': 'category',
    'Projection': 'category'
}
watersource_dtype_mapping = {
    'WaterSourceId': 'string',
    'DisclosureId': 'string',
    'APINumber': 'string',
    'StateName': 'category',
    'CountyName': 'category',
    'OperatorName': 'category',
    'WellName': 'category',
    'Description': 'category'
}
registry_dtype_mapping = {
    'DisclosureId': 'string',
    'JobStartDate': 'string',
    'JobEndDate': 'string',
    'APINumber': 'string',
    'StateName': 'category',
    'CountyName': 'category',
    'OperatorName': 'category',
    'WellName': 'category',
    'Projection': 'category',
    'PurposeId': 'string',
    'TradeName': 'category',
    'Supplier': 'category',
    'Purpose': 'category',
    'IngredientsId': 'string',
    'CASNumber': 'string',
    'IngredientName': 'category',
    'IngredientMSDS': 'bool',
    'ClaimantCompany': 'category'
}

# Load raw data
# 244k data
disclosure_data_path = "/Users/alishbahfarooq/Desktop/Chirality Research/fracfocus_case_study/data/FracFocusCSV_Oil_Gas/DisclosureList_1.csv"
disclosure_df_raw = pd.read_csv(disclosure_data_path, dtype = disclosure_dtype_mapping)

#20k data
watersource_data_path = "/Users/alishbahfarooq/Desktop/Chirality Research/fracfocus_case_study/data/FracFocusCSV_Oil_Gas/WaterSource_1.csv"
watersource_df_raw = pd.read_csv(watersource_data_path, dtype = watersource_dtype_mapping)

#500k data each (~7.5 mill total)
# getting all registry files
#path = r'/Users/alishbahfarooq/Desktop/Chirality Research/fracfocus_case_study/data/FracFocusCSV_Oil_Gas/'
#files = glob.glob(os.path.join(path,"FracFocusRegistry_*.csv"))
# reading files and concatenating to one df
#df_list = [pd.read_csv(file, index_col=None, header=0) for file in files]
#registry_df_raw = pd.concat(df_list, axis=0, ignore_index=True)
registry_df_path = "/Users/alishbahfarooq/Desktop/Chirality Research/fracfocus_case_study/data/FracFocusCSV_Oil_Gas/FracFocusRegistry_1.csv"
registry_df_raw = pd.read_csv(registry_df_path)

# Clean Data

disclosure_df_clean = disclosure_df_raw.copy()
# Given df with col_name of datatype str, the function returns col[col_name] with any occurances of 3XXX changed to 2XXX and 23XX to 20XX
def replace_3xxx_23xx(col):
    # Replacing 3xxx with 2xxx
    col= col.str.replace(
        r"\b3(\d{3})", 
        r"2\1", 
        regex=True 
    )
    # Replacing 23xx with 20xx
    col = col.str.replace(
        r"\b23(\d{2})", 
        r"20\1", 
        regex=True 
    )
    return col

disclosure_df_clean['JobStartDate'] = replace_3xxx_23xx(disclosure_df_clean['JobStartDate'])
disclosure_df_clean['JobEndDate'] = replace_3xxx_23xx(disclosure_df_clean['JobEndDate'])

# Converting datatype to datatime
disclosure_df_clean['JobStartDate'] = pd.to_datetime(disclosure_df_clean['JobStartDate'], format='%m/%d/%Y %I:%M:%S %p')
disclosure_df_clean['JobEndDate'] = pd.to_datetime(disclosure_df_clean['JobEndDate'], format='%m/%d/%Y %I:%M:%S %p')

# Removing rows where 'TotalBaseNonWaterVolume' is less than 0 (only 6 rows removed)
disclosure_df_clean = disclosure_df_clean.loc[~(disclosure_df_clean['TotalBaseNonWaterVolume'] < 0)]

# 15 NaN for JobStartDate
# 4 NaN for CountyName
# 34 NaN for Latitude, Longitude
# 30139 NaN for TVD -> does missingness have a meaning?
# 30168 NaN for TotalBaseWaterVolume -> does it mean 0?
# 50325 NaN for TotalBaseNonWaterVolume -> does it mean 0?

# fill NaN values for County in Disclosure df
disclosure_df_clean['CountyName'] = disclosure_df_clean['CountyName'] = disclosure_df_clean['CountyName'].cat.add_categories('Unknown')
disclosure_df_clean["CountyName"] = disclosure_df_clean["CountyName"].fillna("Unknown")

# Watersource df cleaning
watersource_df_clean = watersource_df_raw.copy()
watersource_columns_to_drop = ['APINumber',
                               'StateName',
                               'CountyName',
                               'OperatorName']
watersource_df_clean = watersource_df_clean.drop(columns=watersource_columns_to_drop)

# Registry Datasets 1 cleaning
registry_df_clean = registry_df_raw.copy()

# NaN values in each column for Registry dataset


registry_df_clean = registry_df_clean.astype(registry_dtype_mapping)
# not needed 
registry_columns_to_drop = ['IngredientCommonName',
                            'IngredientComment',
                            'JobStartDate',
                            'JobEndDate',
                            'APINumber',
                            'StateName',
                            'CountyName',
                            'OperatorName',
                            'WellName',
                            'Latitude',
                            'Longitude',
                            'Projection',
                            'TVD',
                            'TotalBaseWaterVolume',
                            'TotalBaseNonWaterVolume',
                            'FFVersion',
                            'FederalWell',
                            'IndianWell']
registry_df_clean = registry_df_clean.drop(columns=registry_columns_to_drop)

# Setup database

connection = sqlite3.connect('fracfocus.db')
cursor = connection.cursor()

# enabling foreign key enforcement
cursor.execute("PRAGMA foreign_keys = ON;")

connection.commit()

# making Disclosure Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS disclosures (
               DisclosureId TEXT PRIMARY KEY,
               JobStartDate TEXT,
               JobEndDate TEXT,
               APINumber TEXT,
               StateName TEXT,
               CountyName TEXT,
               OperatorName TEXT,
               WellName TEXT,
               Latitude REAL,
               Longitude REAL,
               Projection TEXT,
               TVD REAL,
               TotalBaseWaterVolume REAL,
               TotalBaseNonWaterVolume REAL,
               FFVersion TEXT,
               FederalWell BOOLEAN,
               IndianWell BOOLEAN
);
""")
# making Water Source Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS watersource (
               WaterSourceId TEXT PRIMARY KEY,
               DisclosureId TEXT,
               WellName TEXT,
               Description TEXT,
               Percent REAL,
               FOREIGN KEY (DisclosureId) REFERENCES disclosures(DisclosureId)
);
""")
# making Registry Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS registry (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               DisclosureId TEXT,
               PurposeId TEXT,
               TradeName TEXT, 
               Supplier TEXT,
               Purpose TEXT,
               IngredientsId TEXT,
               CASNumber TEXT,
               IngredientName TEXT,
               PercentHighAdditive REAL,
               PercentHFJob REAL,
               IngredientMSDS BOOLEAN,
               MassIngredient REAL,
               ClaimantCompany TEXT,
               FOREIGN KEY (DisclosureId) REFERENCES disclosures(DisclosureId)
);
""")
connection.commit()

cursor.execute("DROP TABLE IF EXISTS registry")
cursor.execute("DROP TABLE IF EXISTS watersource")
cursor.execute("DROP TABLE IF EXISTS disclosures")
# load Disclosure table
disclosure_df_clean.to_sql("disclosures", connection, if_exists="append", index=False)
connection.commit()

# load water source table
watersource_df_clean.to_sql('watersource', connection, if_exists="append", index=False)
connection.commit()

# load registry table
registry_df_clean.to_sql('registry', connection, if_exists="append", index=False)
connection.commit()

connection.close()