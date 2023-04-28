import pandas
import numpy
from student import *
from company import *

PREFERENCES = 4


def import_companies(input_name, rounds):
    df = pandas.read_excel(f'inputs\{input_name}', sheet_name='Company', header=0)

    # df.replace(value=numpy.nan, to_replace=[None], inplace=True)

    for index, row in df.iterrows():

        representatives = [row[f'Representative{i}'] for i in range(1, 5) if row[f'Representative{i}'] is not numpy.nan]
        
        Company(row['Company'], representatives, rounds)



def import_students(input_name, early_bird_scalar):
    
    df = pandas.read_excel(f'inputs\{input_name}', sheet_name='Student', header=0)

    for index, row in df.iterrows():
        preferences = [row[f'Preference {i}'] for i in range(1, (PREFERENCES + 1)) if row[f'Preference {i}'] is not numpy.nan]
        Student(row['Student Name'], preferences, early_bird_scalar)
