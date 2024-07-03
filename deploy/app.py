from flask import Flask,render_template,request
import numpy as np
import pickle

#loading stuff for popular books
popularity_df = pickle.load(open('popular.pkl','rb'))

#initiating app
app = Flask(__name__)

print("len is: ")
print(len(list(popularity_df['Book-Title']))) # shows that top 487 books  are listed hence 50 hv to be filtered

book = list(popularity_df['Book-Title'].values)[:50]
authors = list(popularity_df['Book-Author'].values)[:50]
images = list(popularity_df['Image-URL-M'].values)[:50]
vote = list(popularity_df['num_ratings'].values)[:50]
ratings = list(popularity_df['avg_ratings'].values)[:50]
https_imgs = []

for img in images:
    if img.startswith("http://"):
        img = img.replace("http://", "https://")
    https_imgs.append(img)

images = https_imgs

#now working on data for recommending
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
sim_matrix = pickle.load(open('sim_matrix.pkl','rb'))


@app.route('/')
def index():
    return render_template('index.html',
                            book_name= book,
                            author= authors,
                            image= images,
                            votes= vote,
                            rating= ratings)

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['post'])
def recommend(num_books=8):
    user_input = request.form.get('user_input')
    #index fetching for particular book
    index = np.where(pt.index==user_input)[0][0]

    # finding the similarity scores of the given book with all others
    distances = sim_matrix[index]
    num_books = num_books+1
    sim_items = sorted(list(enumerate(distances)), key= lambda x:x[1],reverse=True)[1:num_books]


    data = []
    
    for i in sim_items:
        item=[]
        temp_df = books[books['Book-Title']==pt.index[i[0]]]
        # print(temp_df.drop_duplicates('Book-Title')['Book-Author']) #as an example
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        
        # replacing http with https for urls  to work with heroku
        imgs = list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values)
        https_imgs = [url.replace('http://','https://') if url.startswith('http://') else url for url in imgs]
        item.extend(https_imgs)


        data.append(item)

    print(data)

    return render_template('recommend.html',data=data)


if __name__ == '__main__':
    app.run(debug=True)

  