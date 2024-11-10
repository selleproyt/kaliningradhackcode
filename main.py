from flask import Flask
from flask import request
from flask import render_template, redirect

from flask import session
import os
import shutil
from zipfile import ZipFile
from ultralytics import YOLO
from os import listdir

app = Flask(__name__,static_folder="static")
app.config['SECRET_KEY']="5b38897f6f7b7bb3fcb2c8a55027235710df24b1"
UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'zip'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route("/")
def index():
    return render_template('main2.html')


@app.route("/submitone", methods=['POST'])
def submitone():
    file = request.files['image']
    filename=""
    if file:
        #os.mkdir("img/uploads/"+str(file.filename))
        filename = "static/img/uploads/"+(file.filename)
        file.save(filename)
    filename2 = "static/img/results/" + (file.filename)

    def f(path_to_file, path_to_model,filename2):
        model = YOLO(path_to_model)
        result = model.predict([path_to_file])[0]
        cls = result.boxes.cls
        result.save(filename2)
        return cls
    restext=str(f(filename, "without_delete_augmentation.pt",filename2))
    cnt0 = 0
    cnt1 = 0
    res = restext
    for sym in restext:
        if sym == "0":
            cnt0 += 1
        if sym == "1":
            cnt1 += 1
    if cnt1 > 0:
        res="Good_photo"
    elif cnt0 > 0:
        res="Bad_photo"
    else:
        res="Животных не обнаружено"
    pth=f"<img src='{filename2}'>"

    return render_template("resultone.html",pth=filename2,res=res)

@app.route("/submittwo", methods=['POST'])
def submittwo():
    def f(path_to_file, path_to_model,filename2):
        model = YOLO(path_to_model)
        result = model.predict([path_to_file])[0]
        cls = result.boxes.cls
        result.save(filename2)
        return cls
    file = request.files['zip']
    filename = ""
    if file:
        # os.mkdir("img/uploads/"+str(file.filename))
        filename = "static/img/uploads/" + (file.filename)
        file.save(filename)
    filename2 = filename[:-4]
    filename3="static/img/results/"+str(file.filename)
    myzip2=ZipFile(filename3,"w")
    stat0=0
    stat1=0
    statmn=0
    with ZipFile(filename, "r") as myzip:
        myzip.extractall(path=filename2)
        for item in myzip.namelist():
            filepth=filename2+"/"+str(item)
            filepth2 = "static/img/results/" + str(item)
            restext=str(f(filepth,"without_delete_augmentation.pt",filepth2))
            cnt0=0
            cnt1=0
            for sym in restext:
                if sym=="0":
                    cnt0+=1
                if sym=="1":
                    cnt1+=1
            fl=1
            if cnt1>0:
                stat1+=1
            elif cnt0>0:
                stat0+=1
            else:
                statmn+=1
                fl=0

            if fl==1:
                myzip2.write(filepth2)
    return render_template("resulttwo.html", pth=filename3, res=restext,stat1=stat1,stat0=stat0,statmn=statmn)

#print()
app.run()