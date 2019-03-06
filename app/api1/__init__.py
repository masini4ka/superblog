from flask import Blueprint

bp = Blueprint('api1', __name__)

from app.api1 import posts, errors, tokens