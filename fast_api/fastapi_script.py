from fastapi import FastAPI,Request,Form
from fastapi.responses import RedirectResponse, HTMLResponse
import pandas as pd
import os 
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydantic import BaseModel
import joblib

from nltk.tokenize import word_tokenize
import nltk
from nltk.tokenize.regexp import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import PorterStemmer
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import GradientBoostingClassifier
import joblib
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from prometheus_client import start_http_server
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Summary
from prometheus_client import Histogram
import random
import time
start_http_server(8010)       

INPROGRESS = Gauge('fastapiinprogress', 'Nombre de requête en chargement' )
LAST = Gauge('fastapi_last_time_seconds','La dernière fois que l app est appelée')
LATENCY_SUM = Summary('fastapi_latency_summary_seconds','temps nécessaire pour le chargement')
LATENCY_HIS = Histogram('fastapi_latency_histogram_seconds','temps nécessaire pour un chargement pour chacune de ces plages', buckets=[0.0001, 0.1, 1, 120])
app = FastAPI()

df = pd.read_csv(f"{os.path.dirname(os.getcwd())}/app/ML/data_final.csv")
df = df.fillna("null")
data_dict = df.to_dict(orient='records') 

@app.get("/data", response_class=HTMLResponse)
async def getDataFinal():
    LAST.set(time.time())
    INPROGRESS.inc() 
    debut = time.time()  
    try:
        html_content = df.to_html()
        latency = time.time() - debut
        LATENCY_SUM.observe(latency) 
        LATENCY_HIS.observe(latency) 
        
        return html_content
            #'data': data_dict
    finally:
        INPROGRESS.dec() 

@app.get("/postgre")
async def getPostgre():
    LAST.set(time.time())
    INPROGRESS.inc()
    debut = time.time()  
    try:
        url = RedirectResponse(url="http://34.249.92.128:5050/")
        latency = time.time() - debut
        print(latency)
        LATENCY_SUM.observe(latency) 
        LATENCY_HIS.observe(latency) 
        return url
    finally:
        INPROGRESS.dec() 

@app.get("/kibana")
async def getKibana():
    LAST.set(time.time())
    INPROGRESS.inc()
    debut = time.time()  
    try:
        url = RedirectResponse(url="http://34.249.92.128:5601/app/dashboards#/view/e0fd7660-7b42-11ef-b6a3-c1efa0ec564e?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-2y,to:now))")
        latency = time.time() - debut
        LATENCY_SUM.observe(latency) 
        LATENCY_HIS.observe(latency)
        return url
    finally:
        INPROGRESS.dec() 

@app.get("/grafana")
async def getGrafana():
    LAST.set(time.time())
    INPROGRESS.inc()
    debut = time.time()  
    try:
        url = RedirectResponse(url="http://34.249.92.128:3000/d/fdza718lrp43kc/satisfaction-client?orgId=1&refresh=5s")
        latency = time.time() - debut
        LATENCY_SUM.observe(latency) 
        LATENCY_HIS.observe(latency)
        return url
    finally:
        INPROGRESS.dec() 

@app.get("/elasticsearch")
async def getElasticsearch():
    LAST.set(time.time())
    INPROGRESS.inc()
    debut = time.time()  
    try:
        url = RedirectResponse(url="http://34.249.92.128:5601/app/dev_tools#/console")
        latency = time.time() - debut
        LATENCY_SUM.observe(latency) 
        LATENCY_HIS.observe(latency)
        return url
    finally:
        INPROGRESS.dec() 


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))
#templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    LAST.set(time.time())
    INPROGRESS.inc()
    debut = time.time()
    try:
        url = templates.TemplateResponse("indexs.html", {"request": request})
        latency = time.time() - debut
        LATENCY_SUM.observe(latency) 
        LATENCY_HIS.observe(latency)
        return url
    finally:
        INPROGRESS.dec()

@app.get("/mlnotebook", response_class=HTMLResponse)
async def getNotebook(request: Request):
    LAST.set(time.time())
    INPROGRESS.inc()
    debut = time.time()
    try:
        url = templates.TemplateResponse("SentimentAnalysis.html", {"request": request})
        latency = time.time() - debut
        LATENCY_SUM.observe(latency) 
        LATENCY_HIS.observe(latency)
        return url
    finally:
        INPROGRESS.dec()

@app.get("/mlmetrics")
async def getMetrics():
    LAST.set(time.time())
    INPROGRESS.inc()
    debut = time.time()  
    try:
        url = RedirectResponse(url="http://34.249.92.128:5601/app/dashboards#/view/58b0c1d0-8115-11ef-b4a8-55e50525ccc9?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-2d,to:now))")
        latency = time.time() - debut
        LATENCY_SUM.observe(latency) 
        LATENCY_HIS.observe(latency)
        return url
    finally:
        INPROGRESS.dec() 




if nltk.download('punkt') == True:
    pass
else:
    nltk.download('punkt')

if nltk.download('stopwords') == True:
    pass
else:
    nltk.download('stopwords')

if nltk.download('wordnet') == True:
    pass
else:
    nltk.download('wordnet')

tokenizer = RegexpTokenizer(r"[a-zA-Z0-9]{4,}")
stop_words = set(stopwords.words('english'))
stop_words.update([".",",","?","@"])

def stop_words_filtering(l):
    for element in l:
        if element in stop_words:
            l.remove(element)
    return l

def lemmatisation(mots):
    wordnet_lemmatizer = WordNetLemmatizer()
    result = []
    for element in mots:
        radical = wordnet_lemmatizer.lemmatize(element, pos='v')
        if (radical not in result):
            result.append(radical)
    return result

def extract_sentiment_cv(reviews,model_CV):
    tokenizer = RegexpTokenizer(r"[a-zA-Z0-9]{4,}")
    result = []
    reviews = reviews.str.lower().apply(tokenizer.tokenize)
    reviews = reviews.apply(stop_words_filtering)
    reviews = reviews.apply(lemmatisation)
    reviews = reviews.apply(str)
    for text in reviews:
        new_text_vectorized = vectorizer.transform([text])

        prediction = model_CV.predict(new_text_vectorized)
        result.append(prediction[0])
    return result

def extract_sentiment_tfidf(reviews,model_tfidf):
    tokenizer = RegexpTokenizer(r"[a-zA-Z0-9]{4,}")
    result = []
    reviews = reviews.str.lower().apply(tokenizer.tokenize)
    reviews = reviews.apply(stop_words_filtering)
    reviews = reviews.apply(lemmatisation)
    reviews = reviews.apply(str)
    for text in reviews:

        new_text_vectorized = vec_tfidf.transform([text])

        prediction = model_tfidf.predict(new_text_vectorized)
        result.append(prediction[0])
    return result

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ML/model/'))



@app.post("/predict")
async def predict(request: Request, model: str = Form(...), text: str = Form(...)):
    LAST.set(time.time())
    INPROGRESS.inc()
    debut = time.time()
    try:
        input_text = pd.Series([text])
        
        
        if model == "cv_trustpilot":
            vectorizer, model_clf_CV_trustpilot = joblib.load(os.path.join(data_dir, 'modelCV_trustpilot.pkl'))
            selected_model = model_clf_CV_trustpilot
        elif model == "cv_twitter":
            vectorizer, model_clf_CV_twitter = joblib.load(os.path.join(data_dir, 'modelCV_twitter.pkl'))
            selected_model = model_clf_CV_twitter
        elif model == "tfidf_twitter":
            vec_tfidf, model_clf_tfidf_twitter = joblib.load(os.path.join(data_dir, 'modeltfidf_twitter.pkl'))
            selected_model = model_clf_tfidf_twitter
        else:
            url = templates.TemplateResponse("indexs.html", {"request": request, "error": "Modèle non valide"})
            return url
        
        if model == "tfidf_twitter":
            vectorized_text = vec_tfidf.transform(input_text)
        else:
            vectorized_text = vectorizer.transform(input_text)
        
        
        result = selected_model.predict(vectorized_text)
        url = templates.TemplateResponse("indexs.html", {"request": request, "prediction": result[0], "input_text": input_text[0], "model": model }) 
        latency = time.time() - debut
        LATENCY_SUM.observe(latency) 
        LATENCY_HIS.observe(latency)
        return url
    finally:
        INPROGRESS.dec()


    



