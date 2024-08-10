from streamlitUtils import *
from util import *

st.set_page_config(page_title = "Image Helper", layout = "wide")
st.title("AI Helper")

if 'context' not in st.session_state:
    st.session_state.context = ""

context: str = ""

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
        (get_magic_options()),
        index = None,
        placeholder = "Select contact method...",
    )

    print_spaces(1)
    predefinedQuery = st.selectbox(
        "Select a predefined query",
        get_predefined_query(),
        index = None,
        placeholder = "Choose a predefined prompt"
    )

    print_spaces(3)
    useContext = st.checkbox("Use Context")
    submit_button = st.button("Get Answer")

if uploaded_file is not None:
    st.text("Image Preview")
    st.image(uploaded_file, caption = uploaded_file.name)

if submit_button:
    print_spaces(2)
    if uploaded_file is not None:
        generate_answer_for_image_question(uploaded_file, st, query, useContext, magic_options, predefinedQuery)
    else:
        generate_answer_for_text_question(st, query, useContext, magic_options)
