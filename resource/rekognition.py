from http import HTTPStatus
import resource
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from datetime import datetime
import boto3
from config import Config

class ObjectDetectionResource(Resource) :
    # 사진 업로드하기
    def get(self) :
        # 1. 클라이언트로부터 데이터를 받아온다.
        filename = request.args["filename"]

        # 2. 위의 파일은, S3에 저장되어 있어야한다.
        # rekognition을 이용해서 object detection한다.
        client = boto3.client("rekognition", "ap-northeast-2",
                                aws_access_key_id = Config.ACCESS_KEY,
                                aws_secret_access_key = Config.SECRET_ACCESS)
        
        response = client.detect_labels(Image = {"S3Object" : { "Bucket" : Config.S3_BUCKET,
                                                                "Name" : filename}},
                                                                MaxLabels = 10)

        return {"result" : "success",
                "Label" : response["Labels"]}, 200
        
  