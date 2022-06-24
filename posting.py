from datetime import datetime
from http import HTTPStatus
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector
import boto3
from config import Config

class PostingResource(Resource) :
    @jwt_required()
    def post(self) :

        # 1. 클라이언트로부터 데이터를 받아온다.
        # photo(file), content(text)

        user_id = get_jwt_identity()

        if "photo" not in request.files :
            return {"error" : "파일을 업로드 하세요."}, 400

        file = request.files["photo"]
        content = request.form["content"]

        # 2. S3에 파일을 업로드한다.
        # 파일명을 변경해준다.
        # 파일명은 유니크하게 만들어야한다.
        current_time = datetime.now()
        new_file_name = current_time.isoformat().replace(":", "_") + ".jpg"

        # 유저가 올린 파일의 이름을 내가 만든 파일명으로 변경한다.
        file.filename = new_file_name

        # S3에 업로드를 한다.
        # AWS의 라이브러리를 사용해야한다.
        # 이 python 라이브러리를 boto3 라이브러리이다.
        # boto3 설치 : pip install boto3
        s3 = boto3.client("s3", aws_access_key_id = Config.ACCESS_KEY, 
                    aws_secret_access_key = Config.SECRET_ACCESS)

        try :
            s3.upload_fileobj(file, Config.S3_BUCKET, file.filename, 
                            ExtraArgs = {"ACL" : "public-read", "ContentType" : file.content_type})

        except Exception as e:
            return {"error" : str(e)}, 500
        
        # 3. DB에 저장한다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''insert into posting
                    (content, imgUrl, userId)
                    values
                    (%s, %s, %s);'''

            # %s에 맞게 튜플로 작성한다.
            record = (content, new_file_name, user_id)
            
            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야 한다. -> DB에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        # 예외처리
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 503

        return {"result" : "업로드에 성공했습니다.",
                "imgUrl" : Config.S3_LOCATION + file.filename}