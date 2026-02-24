from flask import Flask, request, jsonify
import fugashi
import unidic_lite
import pykakasi
import os

app = Flask(__name__)
tagger = fugashi.Tagger('-d ' + unidic_lite.DICDIR)
kks = pykakasi.kakasi()

def kata_to_romaji(text):
    result = kks.convert(text)
    return ''.join([item['hepburn'] if item['hepburn'] else item['orig'] for item in result])

@app.route('/romaji', methods=['GET'])
def romaji():
    text = request.args.get('text', '')
    if not text:
        return jsonify({'result': ''})
    
    parts = []
    for word in tagger(text):
        reading = word.feature.kana
        if reading:
            parts.append(kata_to_romaji(reading))
        else:
            parts.append(word.surface)
    
    return jsonify({'result': ' '.join(parts)})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
