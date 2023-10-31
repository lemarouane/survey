import streamlit as st
import pandas as pd 
from DButils import create_tables, get_survey, save_question, save_results, get_results, get_choice_id, remove_question
import plotly.express as px
import random
import sqlite3

st.set_page_config(layout="wide")

create_tables()  
df_survey = get_survey()

if 'survey' not in st.session_state:
    st.session_state['survey'] = get_survey()

st.title("Allomonpsy - Configuration and Data Analysis")
st.write("""Bienvenue sur Allomonpsy, votre plateforme de réservation de rendez-vous avec des professionnels de la santé mentale. Ici, vous pouvez configurer votre sondage et analyser les données collectées pour une meilleure prestation de services. """)


st.header("Configurer Votre Sondage")
q_text = st.text_input("Question du sondage")

possible_responses = [
    "Immédiatement, Dans la semaine, Dans le mois, Dans quelques mois, Pas sûr",
    "Oui, Non, Je ne sais pas encore",
    "Extrêmement satisfait, Satisfait, Neutre, Insatisfait, Très insatisfait",
    "Oui, Non",
    "Par téléphone, En personne, En ligne, Pas sûr",
    "Tous les jours, Quelques fois par semaine, Quelques fois par mois, Rarement, Jamais",
    "Oui, Non, Peut-être"
]

q_choices = st.selectbox('Choisissez parmi les réponses possibles :', possible_responses)

new_choices = st.text_input('Spécifiez vos propres choix en les séparant par des virgules.')

if new_choices:
    q_choices = new_choices

st.write(f'Vous avez sélectionné : {q_choices}')

submitted = st.button("Ajouter la question au sondage")  

if submitted:
    save_question(q_text, q_choices)
    st.session_state['survey'] = get_survey()

# ---------- Supprimer une question -------------------- 
st.header("Supprimer une Question")
questions = get_survey()['question'].tolist()

# Laissez l'utilisateur choisir une question à supprimer
selected_question = st.selectbox("Sélectionnez une question à supprimer", questions)

if st.button("Supprimer la question"):
    connection = sqlite3.connect('survey.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM question WHERE question_text = ?', (selected_question,))
    row = cursor.fetchone()
    if row:
        selected_question_id = row[0]

        remove_question(selected_question_id)

        st.session_state['survey'] = get_survey()

        st.success(f"Question '{selected_question}' supprimée avec succès!")



# Afficher les Résultats du Sondage
st.header("Résultats du Sondage")
st.write("Les résultats du sondage sont présentés sous forme de tableau.")

df = get_results()
st.dataframe(df, use_container_width=True)

# Télécharger les Résultats du Sondage
st.download_button(
    label="Télécharger les résultats du sondage au format CSV",
    data=df.to_csv().encode("utf-8"),
    file_name="survey_results.csv",
    mime="text/csv",
)

# Visualiser les Résultats du Sondage
st.header("Analyse des Données - Résultats du Sondage")
fig = px.bar(df, x='id', y='count', color='choice_text', title='Résultats du Sondage',
             labels={'id':'ID de la question', 'count':'Nombre de Réponses', 'choice_text':'Choix'},
             template='plotly_dark')

st.plotly_chart(fig)

# Visualiser les Questions du Sondage
df = get_survey()
results = get_results()

# Créer une liste de figures, une pour chaque question
figures = []
for q in df['question'].unique():
    # Filtrer les données pour la question en cours
    data = results[results['question_text'] == q]
    
    # Obtenir tous les choix pour la question en cours
    choices = df[df['question'] == q]['choices'].iloc[0].split(', ')
    
    # Créer un graphique en barres pour la question en cours
    fig = px.bar(data, x='choice_text', y='count', title=q)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text="Réponse", categoryorder='array', categoryarray=choices)
    fig.update_yaxes(title_text="Nombre")
    
    # Ajouter la figure à la liste de figures
    figures.append(fig)

# Choisissez le graphique à afficher avec des boutons radio
if not df.empty:
    st.info("### Graphique en Barres pour Chaque Question")
    f = st.radio("Choisissez une question", options=df['question'].unique())
    column_index = list(df['question'].unique()).index(f)
    st.plotly_chart(figures[column_index])
else:
    st.warning("Aucune donnée disponible pour l'affichage.")
