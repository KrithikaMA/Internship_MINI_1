from flask import Flask, render_template, request, send_file
from scraper import get_naukri_jobs
import os

app = Flask(__name__)

OUTPUT_FOLDER = "output"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form.get("query")
        location = request.form.get("location")
        jobs = get_naukri_jobs(query, location, page=1)
        return render_template("results.html", jobs=jobs, query=query, location=location)
    return render_template("index.html")


@app.route("/download/<filetype>")
def download(filetype):
    path_map = {
        "csv": os.path.join(OUTPUT_FOLDER, "jobs.csv"),
        "json": os.path.join(OUTPUT_FOLDER, "jobs.json"),
        "excel": os.path.join(OUTPUT_FOLDER, "jobs.xlsx"),
    }

    path = path_map.get(filetype)

    if path and os.path.exists(path):
        return send_file(path, as_attachment=True)

    return "File not found", 404


if __name__ == "__main__":
    app.run(debug=True)
