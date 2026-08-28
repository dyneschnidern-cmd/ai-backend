from flask import Flask, request, jsonify
import g4f
import requests
import json

app = Flask(__name__)

# Optional: set up CORS if needed (for web use)
# from flask_cors import CORS
# CORS(app)

# ============ TEXT GENERATION ============
def generate_text(prompt, model="gpt-3.5-turbo"):
    try:
        # Use g4f to get a response from a free GPT-like model
        response = g4f.ChatCompletion.create(
            model=model,  # can be "gpt-3.5-turbo", "gpt-4", etc. (g4f supports many)
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        if isinstance(response, str):
            return response
        else:
            # g4f may return a response object
            return str(response)
    except Exception as e:
        return None, str(e)

# ============ IMAGE GENERATION ============
def generate_image(prompt):
    try:
        # Pollinations.ai free image generation (no key)
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&nologo=true"
        return url
    except Exception as e:
        return None, str(e)

# ============ UI / MAP CODE GENERATION ============
# These can reuse the text generation but with a specific prompt asking for Lua code.
def generate_lua_code(prompt, task="ui"):
    full_prompt = f"Create Roblox Lua code for {task} based on this description: {prompt}. Only output the code, no explanations."
    code, err = generate_text(full_prompt)
    if code:
        # Clean the code: remove markdown code fences if present
        code = code.strip()
        if code.startswith("```lua"):
            code = code[7:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()
    else:
        return None, err

# ============ FLASK ENDPOINTS ============
@app.route('/models', methods=['GET'])
def get_models():
    # Return available models (hardcoded for simplicity)
    return jsonify({
        "text": ["gpt-3.5-turbo", "gpt-4", "claude-v2", "llama-2-70b"],
        "image": ["pollinations", "stable-diffusion"]
    })

@app.route('/generate-text', methods=['POST'])
def generate_text_endpoint():
    data = request.get_json()
    prompt = data.get('prompt', '')
    model = data.get('model', 'gpt-3.5-turbo')
    result, error = generate_text(prompt, model)
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