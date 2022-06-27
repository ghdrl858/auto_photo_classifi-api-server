from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from config import Config
from resource.follow import FollowResource
from resource.like import LikeResource
from resource.posting import PostingFollowResource, PostingInfoResource, PostingResource
from resource.tag import TagSearchResource
from resource.user import UserLoginResource, UserLogoutResource, UserRegisterResource, jwt_blocklist

app = Flask(__name__)

# 환경변수 셋팅
app.config.from_object(Config)

# JWT 토큰 라이브러리 만들기
# JWT를 관리해주는 라이브러리
jwt = JWTManager(app)

# 로그아웃 된 토큰이 들어있는 set을 jwt에 알려준다.
@jwt.token_in_blocklist_loader
def check_list_token_is_revoked(jwt_header, jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

api = Api(app)

# 경로와 리소스(API코드) 연결
# api.add_resource(MemoListResource, '/memo')
# api.add_resource(MemoResource, '/memo/<int:memo_id>')
api.add_resource(UserRegisterResource, '/users/register')
api.add_resource(UserLoginResource, '/users/login')
api.add_resource(UserLogoutResource, '/users/logout')

api.add_resource(FollowResource, '/follow/<int:follow_id>')
# api.add_resource(FollowListResource, '/follow')

api.add_resource(PostingResource, "/posting")
api.add_resource(PostingInfoResource, "/posting/<int:posting_id>")

api.add_resource(TagSearchResource, "/posting/search/tag")

api.add_resource(LikeResource, "/like/<int:posting_id>")
# api.add_resource(LikeResource, "body : posting_id")

api.add_resource(PostingFollowResource, "/posting/follow")

if __name__ == '__main__' :
    app.run()