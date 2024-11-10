from flask import Flask, request, jsonify
from ..database.models import get_vuz_info, get_train_info

app = Flask(__name__)

@app.route('/get_train_info', methods=['POST'])
def execute_get_vuz_info():
    data = request.json
    vuz = data.get('vuz', False)
    
    result = get_vuz_info(vuz)
    print(jsonify(result))
    return jsonify(result)

@app.route('/get_train_info', methods=['POST'])
def execute_get_train_info():
    data = request.json
    vuz = data.get('vuz', False)
    prog = data.get('prog', False)
    formname = data.get('formname', False)
    
    result = get_train_info(vuz, prog, formname)
    print(jsonify(result))
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)