from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ============ TEXT GENERATION (Pollinations) ============
def generate_text(prompt, model=None):
    try:
        # Pollinations text API (free, no key, model param ignored)
        url = f"https://text.pollinations.ai/{requests.utils.quote(prompt)}"
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            return response.text.strip(), None
        else:
            return None, f"Pollinations API returned status {response.status_code}"
    except Exception as e:
        return None, str(e)

# ============ IMAGE GENERATION (Pollinations) ============
def generate_image(prompt):
    try:
        # Pollinations image URL (no key needed)
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=512&height=512&nologo=true"
        return url, None
    except Exception as e:
        return None, str(e)

# ============ UI / MAP CODE GENERATION ============
def generate_lua_code(prompt, task="ui"):
    full_prompt = f"Create Roblox Lua code for {task} based on this description: {prompt}. Only output the code, no explanations."
    code, err = generate_text(full_prompt)
    if code:
        # Clean the code: remove markdown code fences if present
        code = code.strip()
        if code.startswith("```lua"):
            code = code[7:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip(), None
    else:
        return None, err

# ============ FLASK ENDPOINTS ============
@app.route('/models', methods=['GET'])
def get_models():
    return jsonify({
        "text": ["pollinations"],
        "image": ["pollinations"]
    })

@app.route('/generate-text', methods=['POST'])
def generate_text_endpoint():
    data = request.get_json()
    prompt = data.get('prompt', '')
    # model is ignored for Pollinations
    result, error = generate_text(prompt)
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"result": result})

@app.route('/generate-image', methods=['POST'])
def generate_image_endpoint():
    data = request.get_json()
    prompt = data.get('prompt', '')
    image_url, error = generate_image(prompt)
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"imageUrl": image_url})

@app.route('/generate-ui', methods=['POST'])
def generate_ui_endpoint():
    data = request.get_json()
    prompt = data.get('prompt', '')
    code, error = generate_lua_code(prompt, task="UI layout")
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"code": code})

@app.route('/generate-map', methods=['POST'])
def generate_map_endpoint():
    data = request.get_json()
    prompt = data.get('prompt', '')
    code, error = generate_lua_code(prompt, task="map/terrain")
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"code": code})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)