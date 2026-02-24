from flask import Flask, request, jsonify
import fugashi
import os

app = Flask(__name__)
tagger = fugashi.Tagger()

@app.route('/romaji', methods=['GET'])
def romaji():
    text = request.args.get('text', '')
    if not text:
        return jsonify({'result': ''})
    
    parts = []
    for word in tagger(text):
        reading = word.feature.kana
        if reading:
            # convert katakana reading to romaji
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
