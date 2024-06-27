import re
import spacy
import random
from flask import Flask, request, jsonify, render_template
from stories import story_list;
from transformers import pipeline



nlp = spacy.load('en_core_web_sm')
sentiment_analyzer = pipeline('sentiment-analysis')

def tell_story():
    story = random.choice(story_list)
    return story
current_problem, current_answer = None, None
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

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/chat', methods = ['GET'])
def chat_view():
    return render_template('chat.html')
@app.route('/chat', methods = ['POST'])
def chat():
    global current_problem, current_answer
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
    
    elif 'math' in user_input:
        problem= math_problem()
        return jsonify({'response': problem})
    else:
        print(sentiment_analyzer(user_input)[0]['label'])  

        user_answer = re.findall(r'\d+', user_input)
        if user_answer:
            user_answer = int(user_answer[0])
            if current_problem and user_answer == current_answer:
                response = "Correct! Great job!"
            elif current_problem:
                response = f"Incorrect. The correct answer was {current_answer}."
            else:
                response = "I don't understand. you can ask me either to tell you stories or ask you math."
            current_problem, current_answer = None, None
            return jsonify({'response': response})
        elif sentiment_analyzer(user_input)[0]['label'] == 'NEGATIVE':
            if current_problem:
                response = f"It is totally fine. The answer was {current_answer}."
            else:
                response = "Okay"
            return jsonify({'response': response})
        else:
            return jsonify({'response': 'I am sorry I can only tell stories or ask math questions. Please try again.'})
if __name__ == '__main__':
    app.run(debug = True)
