from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import redis
import markdown
import html
import datetime
import sqlite3
import os
import requests
import hashlib
from flask import jsonify
from flask import session
from insightpipe import init_from_file, get_ollama_url, getVisionModels,describe_file,keyword_file
from dotenv import load_dotenv
from datetime import timedelta

import yaml
app = Flask(__name__)

# Redis connection
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(
    host=os.getenv("REDIS_URL"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PWD")
    
)


# Optional: session timeout
app.config['PERMANENT_SESSION_LIFETIME'] = int(os.getenv("SESSION_LIFETIME", "3600"))


# Initialize session manager
Session(app)

@app.before_request
def make_session_permanent():
    session.permanent = True
@app.template_filter("markdown")
def markdown_filter(text):
    # Unescape HTML entities
    unescaped = html.unescape(text)

    # Normalize triple backticks to start on a new line
    if "```" in unescaped:
        unescaped = unescaped.replace("<p>```", "```").replace("```</p>", "```")

    return markdown.markdown(unescaped, extensions=["fenced_code", "codehilite"])


load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET_KEY")
init_from_file()  # Load config.yaml and set global state
ollama_url = get_ollama_url("chat")

def clean_markdown(text):
    # Remove stray <p> tags around fenced blocks
    text = text.replace("<p>```", "```").replace("```</p>", "```")
    return text




DB_PATH = "db/results.db"
def get_filter_options():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT model FROM results ORDER BY model")
    models = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT prompt FROM results ORDER BY prompt")
    prompts = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT filename FROM results ORDER BY filename")
    filenames = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT test_run_timestamp FROM results ORDER BY test_run_timestamp DESC")
    timestamps = [row[0] for row in cur.fetchall()]

    conn.close()
    return models, prompts, filenames, timestamps

def fetch_all_results():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM results ORDER BY test_run_timestamp DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_result_by_id(result_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM results WHERE id = ?", (result_id,))
    row = cur.fetchone()
    conn.close()
    return row

def build_chat_payload(model, prompt, prior_messages=None, system_prompt="Respond to queries in English", temperature=0.7):
    messages = prior_messages[:] if prior_messages else []

    # Insert system message if not present
    if not any(m["role"] == "system" for m in messages):
        messages.insert(0, {"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": temperature
    }

    return payload, messages


def prompt_model(model, prompt, history=None, ollama_url=None, system_prompt="Respond to queries in English"):
    payload, updated_history = build_chat_payload(
        model, prompt,
        prior_messages=history,
        system_prompt=system_prompt,
        temperature=0.7
    )
   
    try:
        response = requests.post(f"{ollama_url}", json=payload, timeout=120)
        response.raise_for_status()
        content = response.json().get("message", {}).get("content", "").strip()
    except Exception as e:
        content = f"Error: {str(e)}"

    return {
        "model": model,
        "timestamp": datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S"),
        "prompt": prompt,
        "history": history if history else [],
        "response": content
    }, updated_history





@app.route("/")
def index():
    return redirect("/chat")

@app.route("/results")
def results():
    model = request.args.get("model")
    prompt = request.args.get("prompt")
    filename = request.args.get("filename")
    sort_by = request.args.get("sort", "test_run_timestamp")
    test_run_timestamp = request.args.get("test_run_timestamp")

    order = request.args.get("order", "desc")

    query = "SELECT * FROM results WHERE 1=1"
    params = []

    if model:
        query += " AND model LIKE ?"
        params.append(f"%{model}%")

    if prompt:
        query += " AND prompt LIKE ?"
        params.append(f"%{prompt}%")

    if filename:
        query += " AND filename LIKE ?"
        params.append(f"%{filename}%")

    if test_run_timestamp:
        query += " AND test_run_timestamp = ?"
        params.append(test_run_timestamp)


    query += f" ORDER BY {sort_by} {order.upper()}"

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, params)
    results = cur.fetchall()
    conn.close()

    models, prompts, filenames, timestamps = get_filter_options()
    return render_template("index.html", results=results, models=models, prompts=prompts, filenames=filenames, timestamps=timestamps)


@app.route("/view/<int:result_id>")
def detail(result_id):
    result = fetch_result_by_id(result_id)
    return render_template("detail.html", result=result)



@app.route("/keywords", methods=["POST"])
def keywords_endpoint():
    image = request.files.get("file")
    model = request.form.get("model")
    max_keywords = request.form.get("max_keywords", type=int)

    if not image:
        return jsonify({"error": "Missing image"}), 400
    temp_path = os.path.join("/tmp", image.filename)
    image.save(temp_path)
    result = keyword_file(temp_path, model=model, max_keywords=max_keywords)
    return jsonify(result)

@app.route("/describe", methods=["POST"])
def describe_endpoint():
    image = request.files.get("file")
    prompt = request.form.get("prompt")
    model = request.form.get("model")

    if not image or not prompt:
        return jsonify({"error": "Missing image or prompt"}), 400
    temp_path = os.path.join("/tmp", image.filename)
    image.save(temp_path)

    result = describe_file(temp_path, prompt=prompt, model=model)

    os.remove(temp_path)  # optional cleanup
  
    return jsonify(result)
@app.route("/chat", methods=["GET", "POST"])
def chat():
    print("Starting chat endpoint")
    if request.method == "GET":
        session.clear()  # 🔄 New session starts fresh
        session["system_prompt"] = request.args.get("context", "Respond to queries in English")
    models = getVisionModels()
    prompt_history = session.get("prompt_history", [])
    message_history = session.get("message_history", [])
    result = None
    keywords_response = None
    describe_response = None
    if request.method == "POST":
        print("Processing POST request in chat endpoint")
        model = request.form.get("model")
        prompt = request.form.get("prompt")
        prompt = (prompt or "").strip()
        # ✅ Store model only on the first turn
        if "model" not in session and model:
            session["model"] = model

        # ✅ Use locked model for all subsequent turns
        active_model = session.get("model")
        print(f"Using model: {active_model}")
        if prompt and prompt not in prompt_history:
            prompt_history.append(prompt)
            session["prompt_history"] = prompt_history

        system_prompt = request.args.get("context", "Respond to queries in English")
      
        run_keywords = request.form.get("run_keywords")
       
        image = request.files.get("file")
        if image:
 

            filename_hash = hashlib.md5(image.read()).hexdigest() + "_" + image.filename
            image_path = os.path.join("static", "uploads", filename_hash)
            image.seek(0)  # rewind after hashing
            image.save(image_path)
            session["image_path"] = filename_hash  # Persist across messages
            print(f"Image uploaded: {image_path}")
        if run_keywords and image:
            max_keywords = 10
            resultk = keyword_file(image_path, model=active_model, max_keywords=max_keywords)
            print(f"Keyword result: {resultk}")
            jsonify(resultk)
            keywords_response = resultk["keywords"]
            message_history.append({
                "role": "assistant",
                "content": keywords_response
            })
            session["message_history"] = message_history
            print(f"Keywords: {resultk['keywords']}")
        if image:
            
            resultd = describe_file(image_path,prompt=prompt or "Describe the image in detail", model=active_model)
            jsonify(resultd)
            print(f"Describe result: {resultd}")
            describe_response = clean_markdown(resultd["description"])
            result = resultd
            result["response"] = describe_response
            message_history.append({
                "role": "assistant",
                "content": describe_response
            })
            session["message_history"] = message_history
       
            print(f"Description: {describe_response}")
        if  not image:
            response_data, updated_history = prompt_model(
                model=model,
                prompt=prompt,
                history=message_history,
                ollama_url=ollama_url,
                system_prompt=system_prompt
            )
            response_text = clean_markdown(response_data["response"])
            updated_history.append({
                "role": "assistant",
                "content": response_text
            })
            result = response_data
            result["response"] = clean_markdown(result["response"])
            print(f"Raw response:\n{repr(result['response'])}")
            #print(markdown.markdown(result["response"], extensions=["fenced_code", "codehilite"])) 
            session["message_history"] = updated_history
       
   
    return render_template(
        "chat.html",
        models=models,
        prompt_history=prompt_history,
        result=result,
        locked_model=session.get("model"),
        keywords_response= keywords_response,      
        image_path=session.get("image_path") # 🧷 Pass model to template
    )



@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return redirect("/chat")

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5050, debug=True)

