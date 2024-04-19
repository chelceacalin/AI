import streamlit as st
from langchain.chains.llm import LLMChain
from langchain.chains.sequential import SequentialChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

openai_key = os.environ.get("OPENAI_KEY")
llm = OpenAI(api_key = openai_key)


st.title('Chain Chaining')
first_input_prompt = PromptTemplate(template = "Tell me about {name}, short 30 words", input_variables = ['name'])
second_input_prompt = PromptTemplate(template = "When was {person} born, short, 5 words max",
                                     input_variables = ['person'])
third_input_prompt = PromptTemplate(
    template = "Tell me 2 events that happened at {dob} date, short, bullet points, 10 words",
    input_variables = ['dob'])

with st.form("my_form"):
    input_text = st.text_input("Search the topic you want")
    submitted = st.form_submit_button("Submit")
    if submitted:
        first_chain = LLMChain(llm = llm, prompt = first_input_prompt, output_key = 'person')
        second_chain = LLMChain(llm = llm, prompt = second_input_prompt, output_key = 'dob', verbose = True)
        third_chain = LLMChain(llm = llm, prompt = third_input_prompt, output_key = 'event_names', verbose = True)
        parent_chain = SequentialChain(
            chains = [first_chain, second_chain, third_chain],
            input_variables = ['name'],
            output_variables = ['person', 'dob', 'event_names'],
            verbose = True
        )
        response = parent_chain(inputs = {'name': input_text}, return_only_outputs = True)
        st.write(response)
