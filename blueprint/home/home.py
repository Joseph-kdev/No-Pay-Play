from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime

home = Blueprint("home", __name__, template_folder="templates", static_folder="static")

db = SQLAlchemy()

class GameBase(db.Model):
    __abstract__ = True #ensure it is not created as a table
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    thumbnail = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    platform = db.Column(db.String(255), nullable=False)
    short_description = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.DateTime, nullable=False)
    
class NewReleases(GameBase):
    __tablename__ = "new_releases"

class Popular(GameBase):
    __tablename__ = "popular"
    
def populateFunction(table, query, limit=6):
    if table.query.count() == 0:
        games_returned = requests.get(f"https://www.freetogame.com/api/games?sort-by={query}")
        games_returned.raise_for_status()
        if games_returned.status_code == 200:
            for release in games_returned.json():
                try:
                    # Try to parse the release date
                    release_date = datetime.strptime(release["release_date"], "%Y-%m-%d")
                except ValueError:
                    # If parsing fails, skip this entry and continue with the next
                    print(f"Skipping invalid date format: {release['release_date']}")
                    continue
                new_games = table(
                    id = release["id"],
                    title = release["title"].lower(),
                    thumbnail = release["thumbnail"],
                    genre = release["genre"],
                    platform = release["platform"],
                    short_description = release["short_description"],
                    release_date = datetime.strptime(release["release_date"], "%Y-%m-%d")
                )
                db.session.add(new_games)
                
            db.session.commit()
        else:
            return "Error: " + str(games_returned.status_code)
    
    games = table.query.order_by(desc(table.release_date)).limit(limit).all()
    return games
        

def assignBackground(genre):
    if genre == "mmorpg":
        return "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExam8yN2o3ZWF3NWZjNjY1YmVhMG5obWlxbmQ0cHk0Z2RndTRydjhpciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/fdcGUMRHrt3CNt3lwQ/giphy-downsized-large.gif"
    elif genre == "shooter":
        return "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjJ3cTVpNjFoYnF6bnlyZGEwZmZ0bWtxam1qbWpvdjg1NnB6b25obyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/fv0DXhENnsBHOYHMZI/giphy.gif"
    elif genre == "moba":
        return "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExZm5nNjB6dGdqc3hzcm00c2hnaGZwNjc2cndnNG91bnBka3Qwc2ZnNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/PjVWEB5LvNn9K/giphy.gif"
    elif genre == "battle-royale":
        return "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExbjh3em1lejFwNngwa2RrYTc0bHFqMnB2aHgwaWx4bDI4NGl5M2hkbCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xd2c44rUajkHnxpywZ/giphy.gif"
    elif genre == "racing":
        return "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHowbm02d3N2dWkydW0yd2QzbWx1bHBtbG5kZjRrYndqNm5saTY0eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ylBNHicNjRfqmr8btd/giphy.gif"
    elif genre == "strategy":
        return "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmUwaDRqbHplbjZmMHVxODdiNDhkbHRobjEyZXQ5NjhtemJubnA2aSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/IXnnnVD5kyKqXRhaCR/giphy-downsized-large.gif"
    elif genre == "sports":
        return "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGdkYnQxcnlkdnZueXNjamc4anZqbmJsYW1vc3Job2ttcmZreXRoYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cDUgG78hHn7TOt1aLO/giphy-downsized.gif"
    else:
        return "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3Y1bjdkNzE0aWVpNnRoN3d1cHJ4NTltbXpmNnZka2JobzltaW9hMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/AWYdAubkFK8yr0cpdE/giphy.gif"


    
@home.route("/")
@home.route("/home")
def home_page():
    new_releases = populateFunction(NewReleases, "release-date")
    
    response = requests.get("https://www.freetogame.com/api/games?sort-by=popularity")
    response.raise_for_status()
    
    popular_games = []
    
    if response.status_code == 200:
        for game in response.json():
            if len(popular_games) < 5:
                popular_games.append(game)
            else:
                break
    
    return render_template("index.html", new_releases=new_releases, popular_games = popular_games)


platforms = ["All", "pc", "browser"]
categories = ["mmorpg", "shooter", "strategy", "moba", "racing", "sports", "social", "sandbox", "open-world", "survival", "pvp", "pve", "pixel", "voxel", "zombie", "turn-based", "first-person", "third-person", "top-down", "tank", "space", "sailing", "side-scroller", "superhero", "permadeath", "card", "battle-royale", "mmo", "mmofps", "mmotps", "3d", "2d", "anime", "fantasy", "sci-fi", "fighting", "action-rpg", "action", "military", "martial-arts", "flight", "low-spec", "tower-defense", "horror", "mmorts"]
sorts = ["popularity", "alphabetical", "relevance", "release-date"]

@home.route("/genre/<genre>")
def genre_page(genre):
    

    hero_background = assignBackground(genre)
    response = requests.get(f"https://www.freetogame.com/api/games?category={genre}")
    response.raise_for_status()
    games = response.json() if response.status_code == 200 else []
    
    if len(games) == 0:
        flash("There was an error loading the games. Please try again later.")
    
    return render_template("genre.html", genre=genre, hero_background=hero_background, games=games, platforms=platforms, categories=categories, sorts=sorts, current_platform="all", current_category=genre, current_sort="popularity")

@home.route("/api/filter")
def advanced_filter():
    platform = request.args.get('platform', 'all').lower()
    category = request.args.get('category', '').lower()
    sort = request.args.get('sort', 'relevance').lower()
    
    url = "https://www.freetogame.com/api/games"
    params = {}
    if platform != "all":
        params["platform"] = "browser" if platform == "browser" else "pc"
    if category:
        params["category"] = category
    if sort != "relevance":  # API default is relevance
        params["sort-by"] = sort
    
    try:
        response = requests.get(
            "https://www.freetogame.com/api/games",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to fetch games"
        }), 500
        
@home.route('/home/<collection>')
def front_collection(collection):
    hero_background = assignBackground(collection)
    
    url = f"https://www.freetogame.com/api/games?sort-by={collection}"
    response = requests.get(url)
    response.raise_for_status()
    games = response.json() if response.status_code == 200 else []
    
    if len(games) == 0:
        flash("There was an error loading the games. Please try again later.")
    
    return render_template("collection.html", collection=collection, games=games, hero_background=hero_background, platforms=platforms, categories=categories, sorts=sorts, current_platform="all", current_category=collection, current_sort=collection)
    
    
@home.route("/home/game/<int:game_id>")
def game_page(game_id):
    
    try:
        # Make API call to get specific game details
        response = requests.get(
            f"https://www.freetogame.com/api/game",
            params={"id": game_id},
            timeout=10
        )
        response.raise_for_status()
        game = response.json()
        
        if game.get("status") == 404:
            flash("Game not found", "error")
            return redirect(url_for("home.index"))
            
        date_obj = datetime.strptime(game['release_date'], "%Y-%m-%d")
        formatted_date = date_obj.strftime("%B %d, %Y")
        
        game["release_date"] = formatted_date
        
        return render_template("game_page.html", game=game)
    except requests.RequestException as e:
        flash(f"Error loading game: {str(e)}", "error")
        return redirect(url_for("home.index"))
    
@home.route('/search', methods=['GET', 'POST'])
def search_page():
    game = []
    if request.method == 'POST':
        search_query = request.form.get('search_query').lower()
        game = NewReleases.query.filter_by(title=search_query).first()
        
        if game:
            return(render_template('search.html', game=game))
        else:
            game = 0
            return(render_template('search.html', game=game))
    
    return render_template('search.html')