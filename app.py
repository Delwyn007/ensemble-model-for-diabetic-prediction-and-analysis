import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template,send_from_directory,redirect
import pickle
import time
import os.path
from os import path
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)

# --------------------------------------------------------
#Enable Download Report 50% *
#Enable Feedback mail composite ***
#About Us send photos  ***
# -------------------------------------------------------- 
# imporing model and scalar object 

KNN= 'KNN.pkl'
model_KNN = pickle.load(open(f'./{KNN}','rb'))
LGBM = "LGBM.pkl"
model_LGBM = pickle.load(open(f'./{LGBM}','rb'))
FINAL = "Final.pkl"
SCALAR= 'transformer.pkl'
model_FINAL = pickle.load(open(f'./{FINAL}','rb'))
sc = pickle.load(open(f'./{SCALAR}','rb'))


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/')
def homepredict():
    return render_template('index.html#book')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')
    

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    float_features = [x for x in request.form.values()]
    name = float_features[0]
    print(name)
    final_features = [[ int(float_features[x]) for x in range(2,len(float_features))]]
    pregnacies = final_features[0][0]

    glucose = final_features[0][1]
    bp = final_features[0][2]
    skin = final_features[0][3]
    insulin = final_features[0][4]
    bmi = final_features[0][5]
    dpf = final_features[0][6]
    age = final_features[0][7]
    print("----------------------------------------------------")
    print(final_features)
    print("----------------------------------------------------")
    prediction_KNN = model_KNN.predict( final_features)
    prediction_LGBM = model_LGBM.predict( final_features)
    prediction_FINAL = model_FINAL.predict(final_features)

    if prediction_KNN == 1:
        pred_KNN = "KNN Model Claims: You have Diabetes, please consult a Doctor."
    elif prediction_KNN == 0:
        pred_KNN = "KNN Model Claims: You don't have Diabetes."
    if prediction_LGBM == 1:
        pred_LGBM = "LGBM Model Claims: You have Diabetes, please consult a Doctor."
    elif prediction_LGBM == 0:
        pred_LGBM = "LGBM Model Claims: You don't have Diabetes."
    if prediction_FINAL == 1:
        pred_FINAL = "KNN+LGBM Model Claims: You have Diabetes, please consult a Doctor."
        pred_FINAL_1 ="On Considering the above inputs, We are Really Sorry to say that you Have diabetes. Please do Consult a Doctor. "
    elif prediction_FINAL == 0:
        pred_FINAL = "KNN+LGBM Model Claims: You don't have Diabetes."
        pred_FINAL_1 =  "You Are Healthy so Stay Home,Stay Safe, Excercise Well and Stay Fit."
    output_KNN = pred_KNN
    ouput_LGBM = pred_LGBM
    ouput_FINAL = pred_FINAL
    ouput_FINAL_1 = pred_FINAL_1

    return render_template('report.html',Name='{}'.format(name) ,KNN='{}'.format(output_KNN),LGBM='{}'.format(ouput_LGBM),FINAL='{}'.format(ouput_FINAL),Pregnacies='{}'.format(pregnacies),Glucose='{}'.format(glucose),BP='{}'.format(bp),Skin='{}'.format(skin),Insulin='{}'.format(insulin),BMI='{}'.format(bmi),DPF='{}'.format(dpf),Age='{}'.format(age),res = '{}'.format(ouput_FINAL_1),scroll='something')



if __name__ == "__main__":
    app.run(debug=False)
