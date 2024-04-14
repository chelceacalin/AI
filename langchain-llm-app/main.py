import streamlit as st

import langchain_helper as lch

question_max_chars = 100

st.title("Youtube video RAG and Translator")
st.image("https://www.esolutions.ro/icons/esol.svg", width=150)
form = st.form(key='my_form')
form.write("Enter the required information")
youtube_url = form.text_input(label='Enter youtube video url', placeholder='url ( min 10 characters )',
                              help="The video must be shorter than 20 minutes long in order to not become costly")

question_input = form.text_area("Ask me about the video", max_chars=question_max_chars)

language_selected = form.selectbox('Select answer output language ', ['Romanian', 'Spanish', 'English'])

submit_button = form.form_submit_button(label='Submit')

if submit_button:
    if len(youtube_url) < 10:
        form.error("Youtube url is too short, actual:" + str(len(youtube_url)) + ", required: 10")
    elif len(question_input) < 5 or len(question_input) > question_max_chars:
        form.error("Question input doesnt match the requirents, actual:" + str(
            len(question_input)) + f", required:  5 < question < {question_max_chars}")
    else:
        # st.subheader("Answer")
        db = lch.create_vector_db_from_url(youtube_url)
        response: str = lch.get_response_from_query(db=db, query=question_input, output_language=language_selected, k=5)
        st.write(response)
        st.download_button(label='Download output', data=response, file_name='output.txt')
