from sys import argv
from psycopg2.extras import RealDictCursor
from helper import *


svd_pipe = joblib.load('/home/jovyan/pkl/svd_pipe.pkl')
svd_matrix = joblib.load('/home/jovyan/pkl/svd_matrix.pkl')


def get_data():
    get_some_docs = """
    with tb1 as( SELECT DISTINCT A.PAGEID, A.TITLE, A.PAGE_TEXT, C.CATEGORY_NAME FROM PAGE_DATA A, CATEGORY_DATA B, CATEGORY_INFO C
    WHERE A.PAGEID = B.PAGEID AND B.MAINCATEGORYID = C.CATEGORYID AND C.CATEGORY_NAME = 'machine_learning' limit 1100),
    tb2 as 
    (SELECT DISTINCT A.PAGEID, A.TITLE, A.PAGE_TEXT,  C.CATEGORY_NAME FROM PAGE_DATA A, CATEGORY_DATA B, CATEGORY_INFO C
    WHERE A.PAGEID = B.PAGEID AND B.MAINCATEGORYID = C.CATEGORYID AND C.CATEGORY_NAME = 'business_software' limit 1100),
    tb3 as
    (SELECT DISTINCT A.PAGEID, A.TITLE, A.PAGE_TEXT,C.CATEGORY_NAME FROM PAGE_DATA A, CATEGORY_DATA B, CATEGORY_INFO C
    WHERE A.PAGEID = B.PAGEID AND B.MAINCATEGORYID = C.CATEGORYID AND C.CATEGORY_NAME = 'maps' limit 1100)
    select * from tb1 union all select * from tb2 union all select * from tb3;
    """
    df = query_to_dataframe(get_some_docs)
    return(df)

if __name__ == '__main__':
    numVar = len(argv)
    if (numVar == 1):
        print ('Please enter a search term enclosed in quotes')
    elif(numVar == 2):
        search_term = [argv[1]]
        #print(search_term)
        df = get_data()
        query_vector = svd_pipe.transform(search_term)
        tmp = pd.DataFrame(np.dot(svd_matrix, query_vector.T))
        df['cosine_distance'] = tmp[0]
        df.sort_values(['cosine_distance'], ascending=False).head(5)
        return_df = pd.DataFrame(df.sort_values(['cosine_distance'], ascending=False).head(5))
        return_df.drop(['category_name', 'page_text', 'cosine_distance'], axis=1, inplace=True)
        wikipedia_url = 'https://en.wikipedia.org/wiki/'
        return_df['title'] = [wikipedia_url + re.sub('\s', '_', i) for i in return_df['title']]
        print('Five most relevant wikipedia pages to the search string: {}\n'.format(search_term[0]))
        for item in return_df['title']:
            print(item )
        print('\n\n')
    else:
        print ('Too many arguments.  Please check your input')
