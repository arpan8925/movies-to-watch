from flask import Flask, render_template, redirect, url_for
import requests
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean

MOVIE_END = "https://www.91mobiles.com/entertainment/best-hindi-bollywood-movies"
SERIES_END = "https://www.91mobiles.com/entertainment/new-hindi-web-series"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///media-watchlist.db"

db = SQLAlchemy(app)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(250), unique=True, nullable=False)
    poster = db.Column(String(250), nullable=False)
    deleted = db.Column(Boolean, default=False)

class Series(db.Model):
    __tablename__ = 'series'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(250), unique=True, nullable=False)
    poster = db.Column(String(250), unique=True, nullable=False)
    deleted = db.Column(Boolean, default=False)

with app.app_context():
    db.create_all()

def scrape_movies():
    soup_response = requests.get(MOVIE_END).text
    soup = BeautifulSoup(soup_response, "html.parser")

    movie_containers = soup.find_all("div", class_="target_link ga_tracking")

    for container in movie_containers:
        # Extract the movie title
        title_span = container.find("h3", class_="f-s-l txt-cap m-0 font-med")
        movie_title = title_span.get_text(strip=True) if title_span else None

        # Extract the movie poster URL
        poster_img = container.find("img")
        poster_url = None
        if poster_img:
            poster_url = poster_img.get('src')

            # Check if it's a placeholder image
            if "no-image.png" in poster_url:
                # Try to get the 'data-src' if available
                poster_url = poster_img.get('data-src', 'Poster Not Available')

        # Skip if the title or poster URL is missing
        if not movie_title or not poster_url:
            continue

        # Check for an existing movie with the same name or poster URL
        existing_movie = Movie.query.filter(
            (Movie.name == movie_title) | (Movie.poster == poster_url)
        ).first()

        # Skip adding if the movie exists and is marked as deleted
        if existing_movie:
            if existing_movie.deleted:
                continue  # Skip re-adding deleted movies
            continue

        # Create and add the new movie
        new_movie = Movie(name=movie_title, poster=poster_url)
        db.session.add(new_movie)
        db.session.commit()

def scrape_series():
    soup_response = requests.get(SERIES_END).text
    soup = BeautifulSoup(soup_response, "html.parser")

    series_containers = soup.find_all("div", class_="target_link ga_tracking")

    for container in series_containers:
        # Extract the series title
        title_span = container.find("h3", class_="f-s-l txt-cap m-0 font-med")
        series_title = title_span.get_text(strip=True) if title_span else None

        # Extract the series poster URL
        poster_img = container.find("img")
        poster_url = None
        if poster_img:
            poster_url = poster_img.get('src')

            # Check if it's a placeholder image
            if "no-image.png" in poster_url:
                # Try to get the 'data-src' if available
                poster_url = poster_img.get('data-src', 'Poster Not Available')

        # Skip if the title or poster URL is missing
        if not series_title or not poster_url:
            continue

        # Check for an existing series with the same name or poster URL
        existing_series = Series.query.filter(
            (Series.name == series_title) | (Series.poster == poster_url)
        ).first()

        # Skip adding if the series exists and is marked as deleted
        if existing_series:
            if existing_series.deleted:
                continue  # Skip re-adding deleted series
            continue

        # Create and add the new series
        new_series = Series(name=series_title, poster=poster_url)
        db.session.add(new_series)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movie')
def movie_page():
    scrape_movies()
    movies = Movie.query.all()
    return render_template("movies.html", movies=movies)

@app.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    movie = Movie.query.get(movie_id)
    if movie:
        movie.deleted = True  # Set the deleted attribute to True (or 1)
        db.session.commit()
    return redirect(url_for('movie_page'))

@app.route('/series')
def series_page():
    scrape_series()
    series = Series.query.all()
    return render_template("series.html", all_series=series)

@app.route('/delete_series/<int:series_id>', methods=['POST'])
def delete_series(series_id):
    series = Series.query.get(series_id)
    if series:
        series.deleted = True
        db.session.commit()
    return redirect(url_for('series_page'))

if __name__ == '__main__':
    app.run(debug=True)
