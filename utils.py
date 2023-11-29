from flask import jsonify
import json

# Format Response with status, msg, data
def FormatResponse(code=1, data=[], msg=None):
    if msg:
        return jsonify({'code': code, 'msg': msg, 'data': data})
    if code==0:
        msg = '请求失败'
    elif code==1:
        msg = '请求成功'
    elif code==2:
        msg = '请求失败'
    elif code==3:
        msg = '没有更多信息'
    return jsonify({'code': code, 'msg': msg, 'data': data})
