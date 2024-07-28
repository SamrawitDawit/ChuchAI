
import re
import spacy
import random
import requests
from flask import Flask, request, jsonify, render_template
from stories import story_list;
from transformers import pipeline

nlp = spacy.load('en_core_web_sm')
sentiment_analyzer = pipeline('sentiment-analysis')
current_problem, current_answer, current_quiz_question= None, None, None

def tell_story():
    story = random.choice(story_list)
    return story


def math_problem():
    global current_problem, current_answer
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    op = random.choice(['+', '-', '*', '/'])
    current_problem = f"what is {num1} {op} {num2}?"
    current_answer = eval(str(num1) + op + str(num2))
    return current_problem

def askName():
    return "Hello! I am a ChchAI. What is your name?"
def greeting():
    return "Hello! I can tell stories or ask you math questions. What would you like to do?"
def fetch_quiz_question():
    global current_quiz_question
    url = "https://opentdb.com/api.php?amount=1&category=17&difficulty=easy&type=multiple"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        question = data['results'][0]['question']
        correct_answer = data['results'][0]['correct_answer']
        incorrect_answers = data['results'][0]['incorrect_answers']
        return {
            "question": question,
            "correct_answer": correct_answer,
            "incorrect_answers": incorrect_answers
        }
    return None

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/chat', methods = ['GET'])
def chat_view():
    return render_template('chat.html')
@app.route('/chat', methods = ['POST'])
def chat():
    global current_problem, current_answer, current_quiz_question
    user_input = request.json.get('message', '').lower()
    user_input = nlp(user_input).text
    if "my name is" in user_input:
        name = re.search(r"my name is (\w+)", user_input)
        if name:
            response = f"Hello {name.group(1)}! I can tell stories or ask you math questions. What would you like to do?"
        return jsonify({'response': response})
    if 'hello' in user_input or 'hi' in user_input or 'hey' in user_input or 'greetings' in user_input:
        response = askName()
        return jsonify({'response': response})
    if 'story' in user_input:
        response = tell_story()
        return jsonify({'response': response})
    if any(word in user_input for word in ['quiz', 'trivia', 'test']):
        quiz_data = fetch_quiz_question()
        if quiz_data:
            current_quiz_question = quiz_data
            response = current_quiz_question['question']
        else: response = "I just forgot what to ask you. Please try again later."
        return jsonify({'response': response})
    elif 'math' in user_input:
        problem= math_problem()
        return jsonify({'response': problem})
    else:
        print(sentiment_analyzer(user_input)[0]['label'])  
        if sentiment_analyzer(user_input)[0]['label'] == 'NEGATIVE':
            if current_problem:
                response = f"It is totally fine. The answer was {current_answer}."
                current_problem, current_answer = None, None
            elif current_quiz_question:
                response = f"It is fine. The correct answer was {current_quiz_question['correct_answer']}."
                current_quiz_question = None
            else:
                response = "I am sorry to hear that. Is there anything else I can help you with?"
            return jsonify({'response': response})  
        elif current_problem:
            user_answer = re.findall(r'\d+', user_input)
            user_answer = int(user_answer[0])
            if current_problem and user_answer == current_answer:
                response = "Correct! Great job!"
            elif current_problem:
                response = f"Incorrect. The correct answer was {current_answer}."
            else:
                response = "I don't understand. you can ask me either to tell you stories or ask you math."
            current_problem, current_answer = None, None
            return jsonify({'response': response})
        elif current_quiz_question:
            user_answer = user_input.strip().lower()
            if user_answer == current_quiz_question['correct_answer'].lower():
                response = "Correct! Great job!"
            else:
                response = f"Incorrect! The correct answer was {current_quiz_question['correct_answer']}."
            current_quiz_question = None
            return jsonify({'response': response})
        else:
            return jsonify({'response': 'I am sorry I can only tell stories or ask math questions. Please try again.'})
if __name__ == '__main__':
    app.run(debug = True)