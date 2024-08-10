import base64
from util import send_request, print_spaces, stream_data, send_text_request
from typing import List


def generate_answer_for_image_question(uploaded_file, st, query: str, useContext: bool, magic_options: List[str],
                                       predefinedQuery):
    base64_encoded_data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    with st.spinner('Wait for it...'):
        if query:
            res, ans = send_request(query = query, img64 = base64_encoded_data, agree = useContext,
                                    context = st.session_state.context,
                                    magic_options = magic_options)
            st.session_state.context = f"Last Question: {query}\n"
        else:
            res, ans = send_request(query = predefinedQuery, img64 = base64_encoded_data, agree = useContext,
                                    context = st.session_state.context,
                                    magic_options = magic_options)
            st.session_state.context = f"Last Question: {query}\n"
    # st.write(f"Query: \n {ans}")
    print_spaces(2)
    st.write_stream(stream_data(res))
    st.session_state.context += f"Answer to last question: {res}\n"
    st.success('Done!')


def generate_answer_for_text_question(st, query: str, useContext: bool, magic_options: List[str]):
    with st.spinner('Wait for it...'):
        res, ans = send_text_request(query = query, context = st.session_state.context, agree = useContext,
                                     magic_options = magic_options)
        # st.write(f"Query: \n {ans}")
        st.session_state.context = f"Last Question: {query}\n"
        st.session_state.context += f"Answer to last question: {res}\n"
        st.write_stream(stream_data(res))
        st.success('Done!')
