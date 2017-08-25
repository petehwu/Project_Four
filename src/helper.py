import psycopg2 as pg2
from pandas import DataFrame
from psycopg2.extras import RealDictCursor
import re
import requests
import psycopg2 as pg2
import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
from psycopg2.extras import RealDictCursor

def connect_to_db():
    con = pg2.connect(host='postgres',
                      dbname='postgres',
                      user='postgres')
    cur = con.cursor(cursor_factory=RealDictCursor)
    return con, cur

def query_to_dictionary(query, fetch_res=True):
    con, cur = connect_to_db()
    cur.execute(query)
    if fetch_res:
        results = cur.fetchall()
    else:
        results = None
    con.close()
    return results

def query_to_dataframe(query):
    return DataFrame(query_to_dictionary(query))

def cleaner(text):
    text = re.sub('[A-Z]\\n', ' ', text)
    text = re.sub('{.*}', '', text)
    text = re.sub('\s\s', ' ', text)
    text = re.sub('[^a-zA-Z ]', ' ', text)
    text = re.sub('\\t', ' ', text)
    text = re.sub('\s\s', ' ', text)
    return text