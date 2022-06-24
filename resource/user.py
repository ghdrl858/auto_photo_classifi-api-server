from http import HTTPStatus
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector
from email_validator import validate_email, EmailNotValidError
from utils import check_password, hash_password

# 회원가입 코드
class UserRegisterResource(Resource) :
    def post(self) :
        
        # {
        #     "email": "abc@naver.com",
        #     "password": "1234"
        # }

        # 1. 클라이언트가 body에 보내준 json을 받아온다.
        data = request.get_json()

        # 2. 이메일 주소형식이 제대로 된 주소형식인지 확인하는 코드 작성한다.
        # 이메일 형식의 오류 형식은 1번으로 정한다.
        try :
            validate_email(data['email'])

        except EmailNotValidError as e :
            print(str(e))
            return {"error" : str(e), "error_no" : 1}, 400

        # 3. 비밀번호의 길이가 유효한지 체크한다.
        # 비밀번호의 길이는 4자리 이상, 12자리 이하로만 받겠다.
        # 비밀번호 오류는 2번으로 정한다.
        if len(data["password"]) < 4 or len(data["password"]) > 12 :
            return {"error" : "비밀번호 길이를 확인하세요.", "error_no" : 2}, 400

        # 4. 비밀번호를 암호화한다.
        # data["password"]

        hashed_password = hash_password(data["password"])

        print(hashed_password)

        # 5. DB에 회원정보를 저장한다.
        try :
            # 데이터 insert
            # 1) DB에 연결
            connection = get_connection()

            # 2) 쿼리문 만들기
            query = '''insert into user
                    (email, password)
                    values
                    (%s, %s);'''

            # %s에 맞게 튜플로 작성한다.
            record = (data['email'], hashed_password)
            
            # 3) 커서를 가져온다.
            cursor = connection.cursor()

            # 4) 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record)

            # 5) 커넥션을 커밋해줘야 한다. -> DB에 영구적으로 반영하라는 뜻
            connection.commit()

            # 5-1) DB에 저장된 아이디 값을 가져온다.
            user_id = cursor.lastrowid

            # 6) 자원 해제
            cursor.close()
            connection.close()

        # 예외처리
        # 데이터베이스 에러 : 3번
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e), "error_no" : 3}, 503

        # 6. 억세스 토큰을 생성, 클라이언트에 응답해준다.
        # user_id를 바로 보내면 안되고 JWT로 암호화해서 보내준다.
        # 암호화 하는 방법
        access_token = create_access_token(user_id)

        return {"result" : "success", "access_token" : access_token}, 200

# 로그인 코드
class UserLoginResource(Resource) :
    def post(self) :
        # {
        #     "email" : "abc@naver.com",
        #     "password": "1234"
        # }

        # 1. 클라이언트로부터 데이터를 받아온다.
        data = request.get_json()

        # 2. 이메일로 DB에 해당 이메일과 일치하는 데이터를 가져온다.
        try :
            connection = get_connection()

            query = '''select * 
                        from user
                        where email = %s;'''
            # 튜플로 설정할 것.
            record = (data["email"], )

            # select 문은, dictionary = True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            # select 문은, 아래 함수를 이용해서, 데이터를 가져온다.
            # fetchall() : 모든 데이터를 한번에 클라이언트로 가져올 때 사용한다.
            result_list = cursor.fetchall()

            print(result_list)

            # 중요! 디비에서 가져온 timestamp 는 
            # 파이썬의 datetime 으로 자동 변경된다.
            # 문제는! 이데이터를 json 으로 바로 보낼수 없으므로,
            # 문자열로 바꿔서 다시 저장해서 보낸다.
            i = 0
            for record in result_list :
                result_list[i]['created_at'] = record['created_at'].isoformat()
                i = i + 1                

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 503

        # 3. result_list의 행의 갯수가 1개이면
        # 유저 데이터를 정상적으로 받아온 것이고
        # 행의 갯수가 0이면, 요청한 이메일은 회원가입이 되어 있지 않은 이메일이다.
        if len(result_list) != 1 :
            return {"error" : "회원가입이 안된 이메일입니다."}, 400
        
        # 4. 비밀번호가 맞는지 확인한다.
        user_info = result_list[0]

        # 4-1 data["password"] 와 user_info["password"]를 비교하기.
        check = check_password(data["password"], user_info["password"])

        if check == False :
            return {"error" : "비밀번호가 일치하지 않습니다."}, 400

        access_token = create_access_token(user_info['id'])
        return { "result" : "success",
                 "access_token" : access_token}, 200

# 로그아웃을 위한
jwt_blocklist = set()

# 로그아웃 코드
class UserLogoutResource(Resource) :
    @jwt_required()
    def post(self) :
        
        jti = get_jwt()['jti']
        print(jti)

        jwt_blocklist.add(jti)

        return {"result" : "로그아웃이 정상적으로 처리되었습니다."}, 200