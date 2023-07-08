import sys
import requests
import json
import os
import re
import shutil
import urllib.request
from pathlib import Path
from tempfile import NamedTemporaryFile
import fitz
import numpy as np
import openai
import tensorflow_hub as hub
from fastapi import UploadFile
from sklearn.neighbors import NearestNeighbors
from flask import Flask, request, jsonify

app = Flask(__name__)
           
recommender = None
os.environ["OPENAI_API_KEY"] = "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"


def download_pdf(url, output_path):
    urllib.request.urlretrieve(url, output_path)


def preprocess(text):
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    return text


def pdf_to_text(path, start_page=1, end_page=None):
    doc = fitz.open(path)
    total_pages = doc.page_count

    if end_page is None:
        end_page = total_pages

    text_list = []

    for i in range(start_page - 1, end_page):
        text = doc.load_page(i).get_text("text")
        text = preprocess(text)
        text_list.append(text)

    doc.close()
    return text_list


def text_to_chunks(texts, word_length=150, start_page=1):
    text_toks = [t.split(' ') for t in texts]
    page_nums = []
    chunks = []

    for idx, words in enumerate(text_toks):
        for i in range(0, len(words), word_length):
            chunk = words[i: i + word_length]
            if (
                (i + word_length) > len(words)
                and (len(chunk) < word_length)
                and (len(text_toks) != (idx + 1))
            ):
                text_toks[idx + 1] = chunk + text_toks[idx + 1]
                continue
            chunk = ' '.join(chunk).strip()
            chunk = f'[Page no. {idx+start_page}]' + ' ' + '"' + chunk + '"'
            chunks.append(chunk)
    return chunks


class SemanticSearch:
    def __init__(self):
        self.use = hub.load(
            'https://tfhub.dev/google/universal-sentence-encoder/4')
        self.fitted = False

    def fit(self, data, batch=1000, n_neighbors=5):
        self.data = data
        self.embeddings = self.get_text_embedding(data, batch=batch)
        n_neighbors = min(n_neighbors, len(self.embeddings))
        self.nn = NearestNeighbors(n_neighbors=n_neighbors)
        self.nn.fit(self.embeddings)
        self.fitted = True

    def __call__(self, text, return_data=True):
        inp_emb = self.use([text])
        neighbors = self.nn.kneighbors(inp_emb, return_distance=False)[0]

        if return_data:
            return [self.data[i] for i in neighbors]
        else:
            return neighbors

    def get_text_embedding(self, texts, batch=1000):
        embeddings = []
        for i in range(0, len(texts), batch):
            text_batch = texts[i: (i + batch)]
            emb_batch = self.use(text_batch)
            embeddings.append(emb_batch)
        embeddings = np.vstack(embeddings)
        return embeddings


def load_recommender(path, start_page=1):
    global recommender
    if recommender is None:
        recommender = SemanticSearch()

    texts = pdf_to_text(path, start_page=start_page)
    chunks = text_to_chunks(texts, start_page=start_page)
    recommender.fit(chunks)
    return 'Corpus Loaded.'


def generate_text(openAI_key, prompt, query, model="gpt-3.5-turbo"):
    messages = []
    messages.append({"role": "system", "content": prompt})

    question = {}
    question['role'] = 'user'
    question['content'] = query
    messages.append(question)
    openai.api_key = openAI_key
    response = openai.ChatCompletion.create(model=model, 
                                            messages=messages,
                                            max_tokens=512,
                                            top_p=1,
                                            stop=None,
                                            temperature=0.7,)

    try:
        answer = response['choices'][0]['message']['content'].replace(
            '\n', '<br>')
    except:
        answer = 'Oops you beat the AI, try a different question, if the problem persists, come bacl later.'

    return answer


def generate_answer(query, openAI_key):
    topn_chunks = recommender(query)
    print(topn_chunks)
    prompt = ""
    prompt += 'search results:\n\n'
    for c in topn_chunks:
        prompt += c + '\n\n'

    prompt += (
        "Instructions: Compose a comprehensive reply to the query using the search results given. "
        "Cite each reference using [ Page Number] notation (every result has this number at the beginning). "
        "Citation should be done at the end of each sentence. If the search results mention multiple subjects "
        "with the same name, create separate answers for each. Only include information found in the results and "
        "don't add any additional information. Make sure the answer is correct and don't output false content. "
        "If the text does not relate to the query, simply state 'Text Not Found in PDF'. Ignore outlier "
        "search results which has nothing to do with the question. Only answer what is asked. The "
        "answer should be short and concise. Answer step-by-step.\n\n"
    )
    answer = generate_text(openAI_key, prompt, query)
    return answer


def load_openai_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if key is None:
        raise ValueError(
            "[ERROR]: Please pass your OPENAI_API_KEY. Get your key here : https://platform.openai.com/account/api-keys"
        )
    return key

@app.route('/autofill_answer', methods=['POST'])
def autofill_answer():
    question = request.json['question']
    resume_link = request.json['resume_link']

    load_recommender(resume_link)
    openAI_key = load_openai_key()
    answer = generate_answer(question, openAI_key)

    response = {
        'question': question,
        'answer': answer
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run()
    #curl -X POST -H "Content-Type: application/json" -d '{"question": "my last internship?", "resume_link":"/Users/leon/workdir/generate-answer-extension/resume.pdf"}' http://localhost:5000/autofill_answer