# deploy_front/app.py
#

import os.path
from flask import Flask, request #
import os
import json
import run_backend
import get_data #
import ml_utils #

import sqlite3 as sql  # 

import time
import youtube_dl


app = Flask(__name__)



def get_predictions():

    videos = []

    with sql.connect(run_backend.db_name) as conn: # 
        c = conn.cursor() #
        for line in c.execute("SELECT * FROM videos"): #
            #(title, video_id, score, update_time)
            line_json = {"title": line[0], "video_id": line[1], "score": line[2], "update_time": line[3]} #
            videos.append(line_json)
			

    predictions = []
    for video in videos:
        predictions.append((video['video_id'], video['title'], float(video['score'])))

    predictions = sorted(predictions, key=lambda x: x[2], reverse=True)[:30]


    predictions_formatted = []
    for e in predictions:
        #print(e)
        predictions_formatted.append("<tr><th><a href=\"{link}\">{title}</a></th><th>{score}</th></tr>".format(title=e[1], link=e[0], score=e[2]))
  
    return '\n'.join(predictions_formatted) #

@app.route('/')
def main_page():
    preds = get_predictions() #
    return """<head><h1>Recomendador de Vídeos do Youtube</h1></head>
    <body>
    <table>
             {}
    </table>
    </body>""".format(preds) #

@app.route('/predict')
def predict_api():
    yt_video_id = request.args.get("yt_video_id", default='')
    
    ydl = youtube_dl.YoutubeDL({"ignoreerrors": True})
    video_json_data = ydl.extract_info("https://www.youtube.com/watch?v={}".format(yt_video_id), download=False)

    if video_json_data is None:
        return "not found"

    p = ml_utils.compute_prediction(video_json_data)
    output = {"title": video_json_data['title'], "score": p}

    return json.dumps(output)

    #https://sheltered-reef-65520.herokuapp.com/predict?yt_video_id=KL8qBKAHn_A
    #{"title": "As 5 Etapas Que Garantem o Sucesso de um Projeto de Data Science | Mario Filho", "score": 0.015146822893148866}
    
    #https://sheltered-reef-65520.herokuapp.com/predict?yt_video_id=kU1NeSuZ-rg
    #{"title": "Common Obstacles in Kaggle Competitions | Mikhail Trofimov | Kaggle Days", "score": 0.06971212606254984}

    
#def update_db




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')