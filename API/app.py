import re

import pandas as pd

from flask import Flask, jsonify

app = Flask(__name__)

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'Binar Gold Challange'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'Binar Gold Challange - Muhammad Irsyad Ramadhan')
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    'headers': [],
    'specs': [
        {
            'endpoint': 'docs',
            'route': '/docs.json'
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/docs/'
}

Swagger = Swagger(app, template=swagger_template, config=swagger_config)

#endpoint pertama - proses input dari user
@swag_from('docs/text_processing.yml', methods=['POST'])
@app.route('/text_processing.yml', methods=['POST'])
def text_processing():

    text = request.form.get('text')

    text = re.sub('\n', ' ', text) #remove newline
    text = re.sub('  +', ' ', text) # remove extra spaces
    text = re.sub('[^0-9a-zA-Z]+', ' ', text) #remove nonalphanumeric

    json_response = {
        'status_code': 200,
        'description': 'Teks yang sudah diproses',
        'data': text
    }

    response_data = jsonify(json_response)
    return response_data

#endpoint kedua - cleansing re_dataset.csv
@swag_from('docs/data_cleansing.yml', methods=['GET'])
@app.route('/data_cleansing.yml', methods=['GET'])
def data_cleansing():

    #read csv file
    df = pd.read_csv('re_dataset.csv', encoding='latin-1')

    indo_slang_dict = pd.read_csv('indo_slang.csv', encoding='latin-1', header=None)
    indo_slang_dict = indo_slang_dict.rename(columns={0: 'original', 1: 'replacement'})

    #cleansing
    def lowercase(text):
        return text.lower()

    def rmv_unnecessary_char(text):
        text = re.sub('\n', ' ', text) #remove newline
        text = re.sub('rt', ' ', text) #remove retweet symbol
        text = re.sub('user', ' ', text) #remove username
        text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) #remove URL
        text = re.sub('  +', ' ', text) # remove extra spaces
        return text

    def rmv_nonalphanumeric(text):
        text = re.sub('[^0-9a-zA-Z]+', ' ', text) #remove nonalphanumeric
        return text

    #cleansing - normalize indonesian slang
    indo_slang_dict_map = dict(zip(indo_slang_dict['original'], indo_slang_dict['replacement']))
    def normalize_indo_slang(text):
        return ' '.join([indo_slang_dict_map[word] if word in indo_slang_dict_map else word for word in text.split(' ')])

    #cleansing - apply all function
    def cleansing(text):
        text = lowercase(text)
        text = rmv_nonalphanumeric(text)
        text = rmv_unnecessary_char(text)
        text = normalize_indo_slang(text)
        return text

    df_clean = df['Tweet'].apply(cleansing)
    
    json_response = str(df_clean.head())

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run()