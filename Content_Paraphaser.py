import streamlit as st
from streamlit_quill import st_quill 
from streamlit_extras.stylable_container import stylable_container 
import pandas as pd
import anthropic
from dotenv import load_dotenv
import os
import re

#### CSS Customization ####

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
local_css("style.css")

#### Session State ####

if 'user_input' not in st.session_state:
    st.session_state.user_input = None
    
#### Claude API setup ####
load_dotenv()
client = anthropic.Anthropic(
    api_key = os.getenv('claude_api_key')
)

tone_prompts = {
    
    'Business': "As a Thai content paraphrasing, your main task is to carefully translate Thai text to improve its lucidity and nuance in a business setting make sure that you are using business wording or rewriting in business style. Make sure the primary concepts, context, and pertinent facts are effectively communicated while boosting relevance and applicability. but, do not expand the character further than the original only to creating paraphrased versions. (IMPORTANT: YOU MUST RESPONSE IN THAI)",
    
    'Neutral': "As a Thai Content Paraphraser, your main task is to carefully reword Thai content to improve its depth and clarity. You ensure that the essence, context, and key points are retained and effectively communicated. Your skill lies in creating paraphrased versions that not only maintain the core message of the original content but also expand its significance and applicability but, do not expand the character further than the original content only to creating paraphrased versions , (IMPORTANT: YOU MUST RESPONSE IN THAI)",

    'Academic': "As a Thai content paraphrasing, your main task is to carefully translate Thai text to improve its lucidity and nuance in an academic context make sure the word that you are using is academic professional rewrite style. Ensure effective communication of the main ideas, context, and important details while enhancing relevance and applicability but, do not expand the character further than the original content only to creating paraphrased versions. (IMPORTANT: YOU MUST RESPONSE IN THAI)"
    
}

##### Title of the app #####
st.title ('Thai Content Paraphraser')

##### UI #####
user_input = st_quill(placeholder="Enter your content here...", html=True, readonly=False, key='quill_input')
st.session_state.user_input = user_input

#### Paraphrase_button ####
with stylable_container( 
    "paraphrase_button",
    css_styles= """
    [data-testid="baseButton-secondary"] {
        background-color: #EEEEEE;
        color: #000000; /* Sets the text color to black */
    }

    [data-testid="baseButton-secondary"] p {
        color: inherit; /* Inherits color from parent (button) */
    }
    """,
):
    tone_select = st.selectbox('Select Tones', tone_prompts.keys(), key='tone_select')
    paraphase_button = st.button("Paraphrase", key="paraphrase_button")

if paraphase_button:
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        temperature=0,
        system= tone_prompts[tone_select],
        messages=[
        {"role": "user", "content": user_input}
        ]
    )
    
    raw_text = message.content
    text_cleaned = raw_text[0].text
    
    #Remove markdown and html tags from the text using regex
    text_cleaned = re.sub(r'<[^>]*>', '', text_cleaned)
    text_cleaned = re.sub(r'\*\*', '', text_cleaned)
    
    #Display the paraphrased content in the text area
    st.subheader('Paraphrased Content')
    with stylable_container(
        key = 'paraphrased_content',
        css_styles= """
        {   border: 1px solid #EEEEEE;
            border-radius: 10px;
            padding: 15px;
            width: auto;
            overflow: auto;
            text-color: #EEEEEE;
            }
        """,
    ):
        st.markdown(text_cleaned)

    # Columns for displaying the metrics
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        character_count = len(text_cleaned.replace(" ", ""))
        st.metric(label='No. Characters', value=character_count)
        
    with c2:
        word_count = len(text_cleaned.split())
        st.metric(label='No. Words', value=word_count)
        
    with c3:
        original_word_count = len(user_input.split())
        st.metric(label='Original No. Words', value=original_word_count)
    
    with c4:
        original_character_count = len(user_input.replace(" ", ""))
        st.metric(label='Original No. Characters', value=original_character_count)