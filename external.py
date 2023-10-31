import streamlit as st
import random
from DButils import save_results, get_survey, get_choice_id
import pandas as pd

st.set_page_config(page_title="External Page")

# Récupération des questions
questions = get_survey()
responses = []

# Répondre aux questions
for index, row in questions.iterrows():
    question_text = row['question']
    choices = row['choices'].split(', ')
    response = st.radio(question_text, choices)
    responses.append((question_text, response))  # Sauvegarder la question et la réponse

# ------------ Captcha ------------
if 'num1' not in st.session_state:
    st.session_state['num1'] = random.randint(1, 10)
if 'num2' not in st.session_state:
    st.session_state['num2'] = random.randint(1, 10)

st.write(f"What is {st.session_state['num1']} + {st.session_state['num2']}?")
captcha = st.text_input("Please enter the right number.")

if st.button("Submit"):
    if captcha == str(st.session_state['num1'] + st.session_state['num2']):
        # Sauvegarder les réponses
        save_results(responses)

        st.success("Answers submitted successfully!")
        st.session_state['num1'] = random.randint(1, 10)
        st.session_state['num2'] = random.randint(1, 10)

        # Afficher le tableau des réponses à la fin
        st.write("Voici vos réponses :")
        response_table = pd.DataFrame(responses, columns=["Question", "Réponse"])
        st.table(response_table)
    else:
        st.error("Incorrect captcha. Please try again.")
