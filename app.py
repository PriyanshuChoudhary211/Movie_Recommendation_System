from flask import Flask, request, render_template
import pickle
import requests
# from patsy import dmatrices

movies=pickle.load(open("Models/movies_list.pkl","rb"))
similarity=pickle.load(open("Models/similarity.pkl","rb"))

app = Flask(__name__)

import sqlite3

# cur.execute('Create table Details(name varchar(20),email varchar(40),message varchar(300))')
# db.commit()

def fetch_poster(movie_id):
     url="https://api.themoviedb.org/3/movie/{}?api_key=903a7054acd4dc9b70403514b148c055&language=en-US".format(movie_id)
     data=requests.get(url)
     data=data.json()
     poster_path=data['poster_path']
     full_path="https://image.tmdb.org/t/p/w500/"+poster_path
     return full_path 

def recommend(movie):
    index=movies[movies["title2"] == movie].index[0]
    x=list(enumerate(similarity[index]))
    distance=sorted(x,reverse=True,key=lambda x:x[1])
    recommended_movies_name = []
    recommended_movies_poster = []
    recommended_movies_genre=[]
    for i in distance[1:7]:
        movie_id=movies.iloc[i[0]].id
        recommended_movies_poster.append(fetch_poster(movie_id))
        recommended_movies_name.append(movies.iloc[i[0]].title)
        recommended_movies_genre.append(movies.iloc[i[0]].genres)
    return recommended_movies_name, recommended_movies_poster,recommended_movies_genre
     

         

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact",methods=['GET','POST'])
def contact():
    status=0
    db=sqlite3.connect("moviedb.sqlite")
    cur=db.cursor()
    # cur.execute('create table details(name varchar(50),email varchar(50),msg varchar(200) )')
    # if cur.execute('create table details(name varchar(50),email varchar(50),msg varchar(200) )') == False
    if request.method == 'POST':
        fname=request.form.get("name")
        email=request.form.get("email")
        message=request.form.get("message")
        # print(fname," ",email," ",message)
        cur.execute('insert into Details values(?,?,?)',(fname,email,message))
        # cur.execute('delete from details')
        db.commit()
        if request.form:
            status=1
            return render_template("contact.html",status=status)
    return render_template("contact.html",status=status)

@app.route("/prediction", methods=['GET','POST'])
def prediction():
    
    movies_list=movies["title"].values
    movies_list2=movies["title2"].values
    status = False
    if request.method=='POST':
        try:
            if request.form:
                movies_name=request.form["movies"]
                index=movies[movies["title2"] == movies_name].index[0]
                name = movies.iloc[index].title
                print(movies_name)
                recommend_movies_name, recommend_movies_poster,recommend_movies_genre=recommend(movies_name)
                status=True

                return render_template('prediction.html',movies_name=recommend_movies_name,genres_list=recommend_movies_genre, poster=recommend_movies_poster,movie_list=movies_list,status=status,movie_list2=movies_list2,movie=name) 

        except Exception as e:
            error={'error':e}
            return render_template('prediction.html',error=error,movie_list=movies_list,status=status,movie_list2=movies_list2)



    # movies_list=movies['title'].values
    else:
        return render_template("prediction.html",movie_list=movies_list,status=status,movie_list2=movies_list2)

if __name__ == "__main__":
    app.debug=True
    app.run()