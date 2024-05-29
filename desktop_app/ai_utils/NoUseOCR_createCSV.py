import pandas as pd
import os
import shutil
import glob
import cv2
from ultralytics import YOLO
import PIL.ExifTags as ExifTags
from PIL import Image
import datetime
import requests
import random
import string
from dotenv import load_dotenv

load_dotenv()

numDF = pd.DataFrame(columns=['ImageName', 'num'])

model = YOLO(task="detect",model="./cucum_label.pt")

if not os.path.isdir("output"):
    os.makedirs("output")
if not os.path.isdir("renamedImages"):
    os.makedirs("renamedImages")


class CreateNumCsv:
    def __init__(self, img_path):
        self.img_path = ""
        self.detectNumList = []
        self.detectStringList = []
        self.datetimeList = []
        self.img_file_list = []
        self.img_path = img_path
        self.img_file_list = glob.glob(os.path.join(img_path,"*.jpg"))
        self.numDF = pd.DataFrame()
        self.source_directory = "./output"
        self.download_directory = "/Users/aai/Downloads"
        self.croped_label_dir = "./Runs_croped_label"

    def clean_up(self):
        if os.path.isdir(self.croped_label_dir):
            shutil.rmtree(self.croped_label_dir)
    def create_csv(self):
        self.clean_up()
        dt_now = datetime.datetime.now()

        for i, img_path in enumerate(self.img_file_list):
            print("img_path",img_path)
            img = cv2.imread(img_path)
            img_PIL = Image.open(img_path)

            # ******* YOLO v8 ********
            ObjectDetection_results = model.predict(img,project="Runs_cucumber",name="predict",exist_ok=False,conf=0.5,save=True,classes=0)
            LabelDetection_result = model.predict(img,project="Runs_croped_label",name="predict",exist_ok=False,conf=0.5,save_crop=True,classes=1)
            # print("ObjectDetection_results.names",ObjectDetection_results)

            # ******* YOLO v8 ********
            print(f"image{i}",type(LabelDetection_result[0]))
            print(f"image{i}",len(LabelDetection_result[0]))
            print(f"image{i}",LabelDetection_result[0].names)
            #ラベルがないときLabelDetection_result[0]のlenが０になる
            #きゅうりの本数をリストに格納
            for result in ObjectDetection_results:
                self.detectNumList.append(len(result))
                
            exif_data = img_PIL._getexif()
            if exif_data is not None:
                exif_dict = {ExifTags.TAGS[k]: v for k, v in exif_data.items() if k in ExifTags.TAGS}
                if "DateTimeOriginal" in exif_dict:
                    #撮影日時に基づく新規ファイル名を準備
                    file_dateTime = datetime.datetime.strptime(exif_dict["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
                    file_dateTime = file_dateTime.strftime("%Y-%m-%d_%H-%M-%S")
                    self.datetimeList.append(file_dateTime)
                else:
                    #DateTimeOriginalが存在しなかった場合
                    self.datetimeList.append("2024-0-0")
            else:
                self.datetimeList.append("2024-0-0")
            img_PIL.close()

        for _ in range(5):
            random_string = ''.join(random.choices(string.ascii_lowercase, k=5))  # ランダムな５文字の文字列を生成
            self.detectStringList.append(random_string)
        print()
        print("OCRで検出された文字列の数",len(self.detectStringList))
        print("元画像のメタデータ（datetime）の数",len(self.datetimeList))

        # 新しいファイル名を生成してリストに追加
        ChangeFileNameList = [f"{detect}_{date}.jpg" for detect, date in zip(self.detectStringList, self.datetimeList)]
        # 元画像を残したまま新しいディレクトリに名前変更済みの画像を格納
        for index, img in enumerate(self.img_file_list):
            # 新しいファイル名を作成
            new_filename = ChangeFileNameList[index]
            # 元のファイルパス
            source_item = img
            # 新しいファイルパス
            destination_item = os.path.join("./renamedImages", new_filename)
            # ファイルをコピー
            shutil.copy2(source_item, destination_item)
            
        #結果をCSVに出力
        result_list = [[item1, item2] for item1, item2 in zip(ChangeFileNameList, self.detectNumList)]
        self.numDF = pd.DataFrame(result_list, columns=numDF.columns)
        self.numDF.to_csv(f'output/cucumber_num_{dt_now}.csv', index=False)
        source_file_path = os.path.join(self.source_directory, f"cucumber_num_{dt_now}.csv")
        shutil.copy(source_file_path, self.download_directory)

        return True