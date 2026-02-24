from flask import Flask, request, jsonify
import pykakasi
import os

app = Flask(__name__)
kks = pykakasi.kakasi()

@app.route('/romaji', methods=['GET'])
def romaji():
    text = request.args.get('text', '')
    if not text:
        return jsonify({'result': ''})
    result = kks.convert(text)
    romaji_text = ''.join([
        item['hepburn'] if item['hepburn'] else item['orig'] 
        for item in result
    ])
    return jsonify({'result': romaji_text})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
