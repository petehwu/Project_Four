from sys import argv
from helper import *

tfidf_vec = joblib.load('/home/jovyan/pkl/tfidf_vec2.pkl')
prediction_model = joblib.load('/home/jovyan/pkl/prediction_model2.pkl')

def generate_page_query(url):
    '''
    Format an api call for requests
    '''
    clean_url = re.sub('\s','_',url.split('/')[-1])
    query = """http://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&explaintext=True&titles={}""".format(clean_url)
    return query


def make_page_prediction(url):
    response_url = requests.get(generate_page_query(url))
    page_id = list(response_url.json()['query']['pages'].keys())[0]
    if int(page_id) == -1:
        print('Invalid URL given or wikipedia page not found')
        return 0,0
    else:
        page_text = response_url.json()['query']['pages'][page_id]['extract']
        X = tfidf_vec.transform([cleaner(page_text)])
        predicted_category = prediction_model.predict(X)[0]
        proba_dict = {}
        for key, val in enumerate(prediction_model.classes_):
            proba_dict[val] = prediction_model.predict_proba(X)[0][key]
        #print(proba_dict)
        return predicted_category, proba_dict[predicted_category].round(3)

if __name__ == '__main__':
    numVar = len(argv)

    if (numVar == 1):
        print ('Please enter a URL enclosed in quotes to classify ')
    elif(numVar == 2):
        cat, proba = make_page_prediction(argv[1])
        print('\n')
        print('Page: {} \nPredicted Category: {} \nProbability: {}'.format(argv[1], cat, proba))
        print('\n')

    else:
        print('Too many arguments.  Please re-try with only one url enclosed in quotes')

