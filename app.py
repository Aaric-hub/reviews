import functions 
import pandas as pd
import pickle
import os
from flask_cors import cross_origin, CORS
import flask_monitoringdashboard as dashboard
from flask import Flask, request, render_template, redirect, make_response,jsonify
from gensim.test.utils import common_texts
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.sentiment.vader import SentimentIntensityAnalyzer

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
dashboard.bind(app)
CORS(app)


@app.route('/', methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')

@app.route("/file",methods=["GET","POST"])
@cross_origin()
def file():
    try:
        if request.method == 'POST' and request.files:
                #self.log.log(self.file_object,f"File recived...")
            file = request.files['File']
            file.save(f"Upload/{file.filename}")
               #self.log.log(self.file_object,f"Files saved..")
            return render_template('index.html', output = f"{file.filename} \t File uploaded successfuly...")
    except Exception as e:
            #self.log.log(self.file_object,f"Error while reciving file..:: {e}")
        raise Exception

@app.route("/review",methods=["GET","POST"])
@cross_origin()
def review():
    try:
        if request.method == 'POST' or request.method == 'GET':
            file = os.listdir('Upload')
            print(file)
            reviews = pd.read_csv(f"Upload/{file[0]}")
            reviews["is_bad_review"] = reviews["Star"].apply(lambda x: 1 if x < 5 else 0)

            reviews_df = reviews[["Text", "is_bad_review"]]
            #fun = functions()
            reviews_df["review_clean"] = reviews_df["Text"].apply(lambda x: functions.clean_text(x))
        
        # add sentiment anaylsis columns
        
            sid = SentimentIntensityAnalyzer()
            reviews_df["sentiments"] = reviews_df["Text"].apply(lambda x: sid.polarity_scores(str(x)))
            reviews_df = pd.concat([reviews_df.drop(['sentiments'], axis=1), reviews_df['sentiments'].apply(pd.Series)], axis=1)

        # add number of characters column
            reviews_df["nb_chars"] = reviews_df["Text"].apply(lambda x: len(str(x)))

        # add number of words column
            reviews_df["nb_words"] = reviews_df["Text"].apply(lambda x: len(str(x).split(" ")))

            documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(reviews_df["review_clean"].apply(lambda x: x.split(" ")))]

        # train a Doc2Vec model with our text data
            model = Doc2Vec(documents, vector_size=5, window=2, min_count=1, workers=4)

        # transform each document into a vector data
            doc2vec_df = reviews_df["review_clean"].apply(lambda x: model.infer_vector(x.split(" "))).apply(pd.Series)
            doc2vec_df.columns = ["doc2vec_vector_" + str(x) for x in doc2vec_df.columns]
            reviews_df = pd.concat([reviews_df, doc2vec_df], axis=1)

            tfidf = TfidfVectorizer(min_df = 10)
            tfidf_result = tfidf.fit_transform(reviews_df["review_clean"]).toarray()
            tfidf_df = pd.DataFrame(tfidf_result, columns = tfidf.get_feature_names())
            tfidf_df.columns = ["word_" + str(x) for x in tfidf_df.columns]
            tfidf_df.index = reviews_df.index
            reviews_df = pd.concat([reviews_df, tfidf_df], axis=1)

            label = "is_bad_review"
            ignore_cols = [label, "Text", "review_clean"]
            features = [c for c in reviews_df.columns if c not in ignore_cols]
            r =reviews_df[features]

            model = pickle.load(open("rf_model_best.pkl","rb"))

            y_pred_mod = model.predict(r)

            for i in range(len(y_pred_mod)):
                if y_pred_mod[i] == 1:
                    reviews["Developer Reply"][i] = "Doesn't Match"
                else:
                    reviews["Developer Reply"][i] = "Matches"

            reviews.to_csv("chrome_reviews_output.csv")
            return render_template('index.html', prediction_output = "Prediction file created at :: chrome_reviews_output.csv")

    except Exception as e:
            #self.log.log(self.file_object,f"Error while reciving file..:: {e}")
        raise Exception


if __name__ == '__main__':
    app.run(debug=True)