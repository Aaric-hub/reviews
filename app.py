import pandas as pd
import os
import time
from flask_cors import cross_origin, CORS
import flask_monitoringdashboard as dashboard
from flask import Flask, request, render_template, redirect, make_response,jsonify

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
            l = ['Good','Nice','Excellent','Awesome','Helpfull','Hrust','Houthful','yay','wonderful',
                'workable','worked','whooa','whoooa','valuable','useful','usable','trusty',
                'trustworthy','trendy','thumbs-up','thankful','supurb','secure','pros','prefer',
                'positive','neat','love','lovely','joy','helpful','examplary','clean','best','like',
                'fast','fastest','Thanks','cool','learning','ok','recommend','Easy','easily','simple',
                'Fantastic','luv','okay','Wow','Thankyou','thank','effective','efficient',
                'Excelente','Better','Super','Great','Quick','Favourite','Right'
                ]

            count = 0
            num = []

            start_time = time.time()

            for scent in range(len(reviews.Text)):
                for i in l:
                    if i in str(reviews.Text[scent]) or i.lower() in str(reviews.Text[scent]):
                        if reviews.Star[scent] < 4:
                            num.append(reviews.index[scent])
                            #print(count)
                            count+=1
            #print("--- %s seconds ---" % (time.time() - start_time))
            for i in num:
                reviews['Developer Reply'][i] = 'Unmatched'
            
            reviews.to_csv("chrome_reviews_output.csv")
            return render_template('index.html', prediction_output = f"Output file created at :: chrome_reviews_output.csv :: Processing Time took = {(time.time() - start_time)} :: Number of unmatched = {count}" )

    except Exception as e:
            #self.log.log(self.file_object,f"Error while reciving file..:: {e}")
        raise Exception


if __name__ == '__main__':
    app.run(debug=True)