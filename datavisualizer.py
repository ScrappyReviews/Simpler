from flask import Flask, render_template, request
from webscraper import getRestaurants
app = Flask(__name__,static_url_path='/static')

@app.route('/',methods=['GET', 'POST'])
def hello():
    if request.method == "POST":
        citystate = request.form["text"].replace(",","+")
        graphNames = ["/static/"+name for name in getRestaurants(citystate)]
        return render_template("output.html",graphNames=graphNames)
    return render_template("input.html")

if __name__ == "__main__":
    app.run()