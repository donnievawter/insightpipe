from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

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


@app.route("/")
def index():
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

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5050, debug=True)

