import base64
from typing import List

from util import *

st.set_page_config(page_title = "Image Helper", layout = "wide")
st.title("AI Helper")

if 'context' not in st.session_state:
    st.session_state.context = ""

context: str = ""

options: List[str] = ["Help me solve the following problem received as an image with a concise answer",
                      "Give me just the right answer to the following grid question ",
                      "Answer the following question correctly and concisely"]

with st.sidebar:
    st.title('Upload Image')
    print_spaces(2)
    uploaded_file = st.file_uploader("Choose a file")
    print_spaces(2)

    query = st.text_area(
        label = 'Enter Query',
        placeholder = 'Enter Query to help LLM',
        help = "What should LLM do with the image"
    )
    print_spaces(1)

    magic_options: st.selectbox = st.selectbox(
        "Give context for LLM",
        (["The language is C# ASP.NET"]),
        index = None,
        placeholder = "Select contact method...",
    )

    print_spaces(1)
    option = st.selectbox(
        "Select a predefined query",
        options,
        index = None,
        placeholder = "Choose a predefined prompt"
    )

    print_spaces(3)
    agree = st.checkbox("Use Context")
    submit_button = st.button("Get Answer")

if uploaded_file is not None:
    st.text("Image Preview")
    st.image(uploaded_file, caption = uploaded_file.name)

if submit_button:
    st.text("")
    st.text("")
    if uploaded_file is not None:
        base64_encoded_data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        res = ""
        ans = ""
        with st.spinner('Wait for it...'):
            if query:
                res, ans = send_request(query = query, img64 = base64_encoded_data, agree = agree,
                                        context = st.session_state.context,
                                        magic_options = magic_options)
                st.session_state.context = f"Last Question: {query}\n"
            else:
                res, ans = send_request(query = option, img64 = base64_encoded_data, agree = agree,
                                        context = st.session_state.context,
                                        magic_options = magic_options)
                st.session_state.context = f"Last Question: {query}\n"
        #st.write(f"Query: \n {ans}")
        print_spaces(2)
        st.write_stream(stream_data(res))
        st.session_state.context += f"Answer to last question: {res}\n"
        st.success('Done!')
    else:
        with st.spinner('Wait for it...'):
            res, ans = send_text_request(query = query, context = st.session_state.context, agree = agree,
                                         magic_options = magic_options)
            #st.write(f"Query: \n {ans}")
            st.session_state.context = f"Last Question: {query}\n"
            st.session_state.context += f"Answer to last question: {res}\n"
            st.write_stream(stream_data(res))
            st.success('Done!')
