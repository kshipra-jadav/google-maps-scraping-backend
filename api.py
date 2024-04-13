from flask import Flask, render_template, request, send_file, make_response
from webscraper import scrape_maps

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "Hello there"


@app.route("/getResults", methods=["POST"])
def getResults():
    search_term = request.json["Search Term"]
    city = request.json["City"]
    state = request.json["State"]
    items = request.json["items"]

    excel_bytes = scrape_maps(search_term, city, state, items)

    response = make_response(excel_bytes)

    response.headers.set(
        "Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers.set(
        'Content-Disposition', 'attachment', filename=f"{city} Consultancies.xlsx")

    return response


if __name__ == "__main__":
    app.run(debug=True)
