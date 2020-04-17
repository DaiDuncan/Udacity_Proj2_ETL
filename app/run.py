import json
import plotly
import pandas as pd

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar
#from sklearn.externals
import joblib
from sqlalchemy import create_engine


app = Flask(__name__)

def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens

# load data
engine = create_engine('sqlite:///../data/DisasterResponse.db')
df = pd.read_sql_table('ETL_pipeline_cleaned', engine)

# load model
model = joblib.load("../models/classifier.pkl")


# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():

    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)

    #Bar: class information of the messages
    df_class = df[df.columns[4:]]
    df_count = (df_class==1).sum().sort_values(ascending=False)

    class_rate = df_count / df.shape[0]
    class_rate_names = list(class_rate.index)

    # create visuals
    # TODO: Below is an example - modify to create your own visuals

    '''
    annotations=[]
    for i, count in enumerate(genre_counts):
        annotations.append(dict(text=str(count),
                                font=dict(family='Arial', size=14,
                                        color='rgb(248, 248, 255)'),
                                showarrow=False))
    '''

    graphs = [
        {
            'data': [
                Bar(
                    x=genre_names,
                    y=genre_counts,
                    text = genre_counts,
                    textposition = 'outside'
                )
            ],

            'layout': {
                'title': 'Distribution of Message Genres',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Genre"
                }
            }
        },

        {
            'data': [
                Bar(
                    x=class_rate_names,
                    y=class_rate,
                    text=df_count,
                    textposition = 'outside'
                )
            ],

            'layout': {
                'title': 'Distribution of Class Rate',
                'yaxis': {
                    'title': "Rate"
                },
                'xaxis': {
                    'title': "Class"
                }
            }
        }
    ]

    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


# web page that handles user query and displays model results
@app.route('/go')
def go():
    # save user input in query
    #get the query: one is 'message', another is 'genre'
    message = request.args.get('query_message', '')
    genre = request.args.get('select_genre', '')
    #make sure this is the right information of 'genre'
    genre_list = list(df['genre'].unique())
    assert (genre in genre_list), "Please enter just one of the three genres"

    #convert the data form to be adjusted as INPUT of the model
    query_dict = {'message': message, 'genre': genre}
    query_df = pd.DataFrame.from_dict(query_dict, orient='index')
    query_df = query_df.T

    # use model to predict classification for query
    classification_labels = model.predict(query_df)[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))

    # This will render the go.html Please see that file.
    return render_template(
        'go.html',
        query_message=message,
        query_genre=genre,
        classification_result=classification_results
    )


def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()
