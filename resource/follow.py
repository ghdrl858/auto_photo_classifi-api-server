from http import HTTPStatus
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector

class FollowResource(Resource) :
    # 친구 맺기
    @jwt_required()
    def post(self, follow_id) :
        
        # 1. 클라이언트로부터 데이터를 받아온다.
        user_id = get_jwt_identity()

        # 2. DB에 친구정보를 insert한다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''insert into follow
                    (followerId, followeeId)
                    values
                    (%s, %s);'''

            # %s에 맞게 튜플로 작성한다.
            record = (user_id, follow_id)
            
            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야 한다.->DB에 영구적으로 반영하라는 뜻
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

        return {'result' : '정상적으로 친구 맺기 처리되었습니다.'}, 200

    # 친구 끊기
    @jwt_required()
    def delete(self, follow_id) :

        # 1. 클라이언트로부 데이터를 받아온다.
        user_id = get_jwt_identity()

        # 2. DB를 삭제해준다.
        try :
            # 데이터 delete
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''delete from follow
                    where followerId = %s and followeeId = %s;'''

            # %s에 맞게 튜플로 작성한다.
            record = (user_id, follow_id)
            
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

        return {'result' : '정상적으로 친구 끊기 처리되었습니다.'}, 200