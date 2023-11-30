from flask import Flask
from apis.feed.controller import api_feed
from apis.search.controller import api_search
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化app
app = Flask(__name__)

# 允许跨域
CORS(app)


# 注册feed蓝图
app.register_blueprint(api_feed)
# 注册search蓝图
app.register_blueprint(api_search)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
