from sys import argv
from helper import *

connection, cursor = connect_to_db()

def generate_category(category):
    '''
    format a category for insertion in to a wikipedia api call
    '''
    category = re.sub('\s', '_', category)
    category = category.lower()
    return category

def generate_query(category):
    '''
    Format an api call for requests
    '''
    query = """
            http://en.wikipedia.org/w/api.php?
            action=query&
            format=json&
            list=categorymembers&
            cmtitle=Category:{}& 
            cmlimit=max
            """.format(generate_category(category))
    query = re.sub('\s', '', query)
    return query


def get_page_ids(category, level=0):
    # insert record into the Category Table and get the categoryID
    print('Getting PageIDs from Wikipedia for category: {}.  Please wait'.format(category))
    category = generate_category(category)
    cursor.execute("SELECT CATEGORYID FROM CATEGORY_INFO where category_name = '{}';".format(category))
    cat_id = cursor.fetchall()
    if not cat_id:
        insert_category = """
                BEGIN;
                INSERT INTO CATEGORY_INFO (CATEGORY_NAME) VALUES ('{}');
                COMMIT;
                    """.format(category.lower())
        cursor.execute(insert_category)
    cursor.execute("SELECT CATEGORYID FROM CATEGORY_INFO where category_name = '{}';".format(category))
    cat_id = cursor.fetchall()
    cat_id = cat_id[0]['categoryid']
    get_wikipedia_page_ids(category, cat_id, level)
    print('Finished getting PageID list')
    get_wikipedia_page_text()

def get_wikipedia_page_ids(category, cat_id, level=0):
    response_url = requests.get(generate_query(category))
    response_url.json()
    id_list = response_url.json()['query']['categorymembers']
    for x in id_list:
        pageid = x['pageid']
        title = x['title']
        title = title.replace("'", '"')
        if ('Category:' not in title):
            #check to see if page already exists.  If it does do not insert again
            cursor.execute("""SELECT PAGEID FROM PAGE_INFO WHERE PAGEID = {};""".format(pageid))
            page_exist = cursor.fetchall()
            if not page_exist:
                insert_stmt = """
                       BEGIN;
                       INSERT INTO PAGE_INFO VALUES ({},'{}');
                       COMMIT;
                   """.format(pageid, title)
                cursor.execute(insert_stmt)
                #from here, insert category_id and page_id into category_data table
            cursor.execute("""SELECT MAINCATEGORYID FROM CATEGORY_DATA WHERE MAINCATEGORYID = {} AND PAGEID = {};""".format(cat_id, pageid))
            rec_exist = cursor.fetchall()
            if not rec_exist:
                insert_stmt = """
                        BEGIN;
                        INSERT INTO CATEGORY_DATA (MAINCATEGORYID, PAGEID, LEVEL, CATEGORY) VALUES ({}, {}, {}, '{}');
                        COMMIT;
                    """.format(cat_id, pageid,level,category)
                cursor.execute(insert_stmt)
        else:
            # if level > 0 decrease level by 1 and then make recursive call using sub-category as category 
            if level:
                sub_cat = title.replace('Category:', '')
                cursor.execute("""SELECT MAINCATEGORYID, CATEGORY, SUBCATEGORY FROM CATEGORY_DATA
                WHERE MAINCATEGORYID = {} AND CATEGORY = '{}' AND SUBCATEGORY = '{}'""".format(cat_id, category, sub_cat))
                rec_exist = cursor.fetchall()
                if not rec_exist:
                    insert_subcat = """
                        BEGIN;
                        INSERT INTO CATEGORY_DATA (MAINCATEGORYID, CATEGORY, SUBCATEGORY, LEVEL ) VALUES ({}, '{}', '{}',{});
                        COMMIT;
                        """.format(cat_id,  category, sub_cat, level)
                    cursor.execute(insert_subcat)
                    level -=1
                    get_wikipedia_page_ids(sub_cat, cat_id, level)
                    level +=1 
                    


def get_wikipedia_page_text():
    print('Start getting wikipedia page text from PageID list.  Please wait')
    select_stmt = """
            SELECT A.PAGEID,A.TITLE FROM PAGE_INFO A LEFT OUTER JOIN PAGE_DATA B ON A.PAGEID = B.PAGEID WHERE B.PAGEID IS NULL;
        """
    cursor.execute(select_stmt)
    result = cursor.fetchall()
    for item in result:
        pageid = item['pageid']
        title = item['title']
        rich_url = 'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&explaintext=True&pageids=' + str(
            pageid)
        response_url = requests.get(rich_url)
        r_text = response_url.json()['query']['pages'][str(pageid)]['extract']
        r_text = r_text.replace("'", '"')
        r_text = cleaner(r_text)
        insert_stmt = """
                    BEGIN;
                    INSERT INTO PAGE_DATA VALUES ({},'{}', '{}');
                    COMMIT;
        """.format(pageid, title, r_text)
        cursor.execute(insert_stmt)
    print('\nFinished getting page text from wikipedia.  Process is complete\n')


if __name__ == '__main__':
    numVar = len(argv)

    if (numVar == 1):
        print ('Please enter a Category you would like to extract from wikipedia')
    elif(numVar == 2):
        print('Please Specify a Category Level to extract to')
    else:
        category = argv[1]
        level = int(argv[2])

    get_page_ids(category, level)