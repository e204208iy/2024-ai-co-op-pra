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
from dotenv import load_dotenv

load_dotenv()

model = YOLO(task="detect",model="./cucum_label.pt")
# reader = easyocr.Reader(['en'])
endpoint = os.environ['COMPUTER_VISION_ENDPOINT']
subscription_key = os.environ['COMPUTER_VISION_KEY']
text_recognition_url = endpoint + "computervision/imageanalysis:analyze?features=caption,read&model-version=latest&language=en&api-version=2023-02-01-preview"

headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-Type': 'application/octet-stream'
}

if not os.path.isdir("output"):
    os.makedirs("output")
if not os.path.isdir("renamedImages"):
    os.makedirs("renamedImages")

class CreateCSVClass:
    def __init__(self, img_path):
        self.img_path = ""
        self.detectNumList = []
        self.detectStringList = []
        self.datetimeList = []
        self.img_file_list = []
        self.img_path = img_path
        self.img_file_list = glob.glob(os.path.join(img_path,"*.jpg"))
        self.numDF = pd.DataFrame(columns=['ImageName', 'num'])
        self.source_directory = "./output"
        self.download_directory = "/Users/aai/Downloads"
        self.croped_label_dir = "./Runs_croped_label"

    def clean_up(self):
        if os.path.isdir(self.croped_label_dir):
            shutil.rmtree(self.croped_label_dir)
    
    def create_csv(self):
        self.clean_up()
        dt_now = datetime.datetime.now()

        for i,img_path in enumerate(self.img_file_list):
            print("now index is",i)
            img = cv2.imread(img_path)
            img_PIL = Image.open(img_path)

            # ******* YOLO v8 ********
            ObjectDetection_results = model.predict(img,project="Runs_cucumber",name="predict",exist_ok=False,conf=0.5,save=True)
            DetectLabel = model.predict(img,project="Runs_croped_label",name="predict",exist_ok=False,conf=0.5,save_crop=True,classes=1)
            #きゅうりの本数をリストに格納
            for result in ObjectDetection_results:
                self.detectNumList.append(len(result))
            # ******* YOLO v8 ********
            
            # ******* azure_readAPI　********
            if i == 0:
                with open(self.croped_label_dir + f"/predict/crops/label/image0.jpg", 'rb') as image_file:
                    image_data = image_file.read()
            else:
                with open(self.croped_label_dir + f"/predict{i+1}/crops/label/image0.jpg", 'rb') as image_file:
                    image_data = image_file.read()

            response = requests.post(
            url=text_recognition_url,
            headers=headers,
            data=image_data
            )
            response.raise_for_status()
            response = response.json()
            OCR_results = response["readResult"]["content"]
            OCR_results = OCR_results.replace('\n', '')
            detectString = ""
            
            for result in OCR_results:
                n = result
                detectString += n
            # detectString = "000000"
            self.detectStringList.append(detectString)
            print("detectString",detectString)
            # ******* azure_readAPI　********

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
        self.numDF = pd.DataFrame(result_list, columns=self.numDF.columns)
        self.numDF.to_csv(f'output/cucumber_num_{dt_now}.csv', index=False)
        source_file_path = os.path.join(self.source_directory, f"cucumber_num_{dt_now}.csv")
        shutil.copy(source_file_path, self.download_directory)

        return True