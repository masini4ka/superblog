# {
#     "id": 123,
#     "title": "susan",
#     "body": "my-password",
#     "author": "susan@example.com",
#     "_links": {
#         "self": "/api/posts/123",
#
#     }
# }
#
# GET	/api/posts/<id>	Return post.
# GET	/api/posts	Return the collection of all posts.
# POST	/api/posts	Create a new post.
# PUT	/api/posts/<id>	Modify post.
from sqlalchemy import null

from app.api1 import bp
from flask import jsonify
from app.models import Post, User
from flask import request
from app import db
from app.api1.auth import token_auth
from app.api1.errors import bad_request

@bp.route('/posts/<int:id>', methods=['GET'])
@token_auth.login_required
def get_post(id):
    return jsonify(Post.query.get_or_404(id).to_dict())

@bp.route('/posts/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    auth_header = request.headers["Authorization"]
    auth_header = auth_header.split()
    user = User.check_token(auth_header[1])
    if user.id != post.user_id:
        response = jsonify('you dont have the right to delete this post')
        response.status_code = 403
        return response
    else:
        db.session.query(Post).filter(Post.id == id).delete()
        db.session.commit()
        return jsonify({'result': True})

@bp.route('/posts', methods=['GET'])
@token_auth.login_required
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Post.to_collection_dict(Post.query, page, per_page, 'api1.get_posts')
    return jsonify(data)

@bp.route('/posts', methods=['POST'])
@token_auth.login_required
def create_post():
    data = request.get_json() or {}
    if 'title' not in data or 'body' not in data:
        return bad_request('must include title and body fields')
    post = Post()
    post.from_dict(data)
    auth_header = request.headers["Authorization"]
    auth_header = auth_header.split()
    # print(auth_header[1])
    user = User.check_token(auth_header[1])
    post.user_id=user.id
    db.session.add(post)
    db.session.commit()
    response = jsonify(post.to_dict())
    response.status_code = 201
    return response

@bp.route('/posts/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_post(id):
    auth_header = request.headers["Authorization"]
    auth_header = auth_header.split()
    user = User.check_token(auth_header[1])
    post = db.session.query(Post).filter(Post.id == id).first_or_404()
    if user.id != post.user_id:
        response=jsonify('you dont have the right to edit this post')
        response.status_code=403
        return response
    data = request.get_json() or {}
    if 'title' in data and 'body' in data:
        post.from_dict(data)
    db.session.commit()
    return jsonify(post.to_dict())

