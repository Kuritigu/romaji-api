from flask import Flask, request, jsonify
import fugashi
import unidic_lite
import pykakasi
import os

app = Flask(__name__)
tagger = fugashi.Tagger('-d ' + unidic_lite.DICDIR)
kks = pykakasi.kakasi()

# ── Language detection ──────────────────────────────────────────────────────

def detect_language(text):
    for ch in text:
        cp = ord(ch)
        if 0xAC00 <= cp <= 0xD7A3 or 0x1100 <= cp <= 0x11FF or 0x3130 <= cp <= 0x318F:
            return 'korean'
    for ch in text:
        cp = ord(ch)
        if 0x3040 <= cp <= 0x309F or 0x30A0 <= cp <= 0x30FF:
            return 'japanese'
        if 0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF:
            return 'chinese'
    return 'unknown'

# ── Japanese ────────────────────────────────────────────────────────────────

def kata_to_romaji(text):
    result = kks.convert(text)
    return ''.join([item['hepburn'] if item['hepburn'] else item['orig'] for item in result])

def romanize_japanese(text):
    parts = []
    for word in tagger(text):
        reading = word.feature.kana
        if reading:
            parts.append(kata_to_romaji(reading))
        else:
            parts.append(word.surface)
    return ' '.join(parts)

# ── Korean ──────────────────────────────────────────────────────────────────

def romanize_korean(text):
    try:
        from korean_romanizer.romanizer import Romanizer
        return Romanizer(text).romanize()
    except ImportError:
        pass
    try:
        import hangul_romanize
        from hangul_romanize.rule import academic
        h = hangul_romanize.Transliter(academic)
        return h.translit(text)
    except ImportError:
        pass
    raise RuntimeError("No Korean romanization library found.")

# ── Chinese ─────────────────────────────────────────────────────────────────

def romanize_chinese(text):
    try:
        from pypinyin import lazy_pinyin, Style
        return ' '.join(lazy_pinyin(text, style=Style.TONE))
    except ImportError:
        pass
    raise RuntimeError("No Chinese romanization library found.")

# ── Shared romanize ─────────────────────────────────────────────────────────

def romanize(text, lang=None):
    if not lang:
        lang = detect_language(text)
    if lang == 'japanese':
        return romanize_japanese(text)
    elif lang == 'korean':
        return romanize_korean(text)
    elif lang == 'chinese':
        return romanize_chinese(text)
    return text

# ── Routes ───────────────────────────────────────────────────────────────────

@app.route('/romaji', methods=['GET'])
def romaji():
    text = request.args.get('text', '')
    lang = request.args.get('lang', '').lower()
    if not text:
        return jsonify({'result': '', 'language': 'none'})
    try:
        lang = lang or detect_language(text)
        result = romanize(text, lang)
        return jsonify({'result': result, 'language': lang})
    except Exception as e:
        return jsonify({'error': str(e), 'language': lang}), 500

@app.route('/romaji_batch', methods=['POST'])
def romaji_batch():
    data = request.get_json()
    if not data or 'lines' not in data:
        return jsonify({'error': 'Missing lines'}), 400

    results = []
    for line in data['lines']:
        if not line or line.startswith('♪'):
            results.append(line)
            continue
        try:
            results.append(romanize(line))
        except Exception:
            results.append(line)

    return jsonify({'results': results})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
