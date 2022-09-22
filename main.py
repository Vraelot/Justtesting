import itertools
from logging import log
import os
import json
import numpy as np

# import snowballstemmer
# import requests

# response = requests.get(url)
# response.raise_for_status()  # raises exception when not a 2xx response


from streamlit_lottie import st_lottie
from io import StringIO

import spacy
from spacy_streamlit import visualize_parser

import pandas as pd
import streamlit as st

import utils
import time

author_textrazor_token = os.getenv("TEXTRAZOR_TOKEN")
author_google_key = os.getenv("GOOGLE_KEY")
# print(author_google_key)

st.set_page_config(
    page_title="The Entities Swissknife",
    page_icon="https://cdn.shortpixel.ai/spai/q_lossy+ret_img+to_auto/https://studiomakoto.it/wp-content/uploads/2021/08/cropped-favicon-16x16-1-192x192.png",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": None
    }
)

hide_st_style = """
            <style>
            footer {visibility: hidden;}
            [title^='streamlit_lottie.streamlit_lottie'] {
                margin-bottom: -35px;
                margin-top: -90px;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

if "en_nlp" not in st.session_state:
    st.session_state.en_nlp = spacy.load("en_core_web_sm")

if "it_nlp" not in st.session_state:
    st.session_state.it_nlp = spacy.load("it_core_news_sm")

# @st.cache(suppress_st_warning=True)
# def logo():
# @st.cache(allow_output_mutation=True)
# def logo():


# # x= "anim"
# if  'anim'  not in st.session_state:
#     with open("data.json") as f:
#         st.session_state.anim = json.loads(f.read())

#     with st.sidebar:
#         st_lottie(st.session_state.anim, width=280, height=230, loop=False, key="anim_makoto")
# # # logo()




@st.cache(allow_output_mutation=True)
def load_lottifile(filepath: str):
    with open(filepath, 'r') as f:
        return json.load(f)


loti_path = load_lottifile('data.json')
# st.title('Lotti')
with st.sidebar:
    # time.sleep(3)
    st_lottie(loti_path, width=280, height=180, loop=False)

df = None
texts = None  # initialize for
language_option = None
# response2 = None
with st.form("my_form"):
    api_selectbox = st.sidebar.selectbox(
        "Choose the API you wish to use",
        ("TextRazor", "Google NLP")
    )
    input_type_selectbox = st.sidebar.selectbox(
        "Choose what you want to analyze",
        ("Text", "URL", "URL vs URL")
    )

    st.sidebar.info(
        '##### Read this article to [learn more about how to use The Entities Swissknife](https://studiomakoto.it/digital-marketing/entity-seo-semantic-publishing/).')
    st.sidebar.info(
        '##### Register on the [TextRazor website](https://www.textrazor.com/) to obtain a free API keyword (🙌 500 calls/day 🙌) or activate the [NLP API](https://cloud.google.com/natural-language) inside your Google Cloud Console, and export the JSON authentication file.')
    st.sidebar.info('##### Knowledge Graph Entity ID is extracted only using the Google NLP API.')
    st.sidebar.info(
        '##### Categories and Topics - by [IPTC Media Topics](https://iptc.org/standards/media-topics/) - are avalaible only using the TextRazor API.')

    # loti_path = load_lottifile('lotti/seo.json')
    # with st.sidebar:
    #     st_lottie(loti_path, width=280, height=130)

    # st.title('Lotti')

    if api_selectbox == "TextRazor":
        google_api = None
        st.session_state.google_api = False
        if not author_textrazor_token:
            text_razor_key = st.text_input('Please enter a valid TextRazor API Key (Required)', value="3c816b4452eb1be8f95fad3776f8fe556109e96ac04f576f2b28e00a")
        else:
            text_razor_key = author_textrazor_token
    elif api_selectbox == "Google NLP":
        text_razor_key = None
        st.session_state.text_razor = False
        if not author_google_key:
            google_api = st.file_uploader("Please upload a valid Google NLP API Key (Required)", type=["json"])
            if google_api:
                google_api = json.loads(google_api.getvalue().decode("utf-8"))
        else:
            google_api = json.loads(author_google_key)
            # print(google_api)

    if input_type_selectbox == "URL":
        text_input = st.text_input('Please enter a URL', value="https://gofishdigital.com/what-is-semantic-seo/")
        # print('text_input 171 the first lien\n',text_input)

        meta_tags_only = st.checkbox('Extract Entities only from meta tags (tag_title, meta_description & H1-4)')
        # print('172 meta tag', meta_tags_only)
        if "last_field_type" in st.session_state and st.session_state.last_field_type != input_type_selectbox:
            st.session_state.text_razor = False
            st.session_state.google_api = False
        st.session_state.last_field_type = input_type_selectbox
    elif input_type_selectbox == "Text":
        if "last_field_type" not in st.session_state:
            st.session_state.last_field_type = input_type_selectbox
            st.session_state.text_razor = False
            st.session_state.google_api = False
        if st.session_state.last_field_type != input_type_selectbox:
            st.session_state.text_razor = False
            st.session_state.google_api = False
        st.session_state.last_field_type = input_type_selectbox
        meta_tags_only = False
        text_input = st.text_area('Please enter a text',
                                  placeholder='Posts involving Semantic SEO at Google include structured data, schema, and knowledge graphs, with SERPs that answer questions and rank entities - Bill Slawsky.')
    elif input_type_selectbox == "URL vs URL":
        if "last_field_type" in st.session_state and st.session_state.last_field_type != input_type_selectbox:
            st.session_state.text_razor = False
            st.session_state.google_api = False
        meta_tags_only = False
        st.session_state.last_field_type = input_type_selectbox

        url1 = st.text_input(label='Enter first URL')
        url2 = st.text_input(label='Enter second URL')

        # Every form must have a submit button.
        # submitted = st.form_submit_button("Submit")
        are_urls = utils.is_url(url1) and utils.is_url(url2)
        urls = [url1, url2]
        text_input = "None"
        # if submitted:
        #     st.write("First Url", url1, "Second Url", url2)

    is_url = utils.is_url(text_input)
    if input_type_selectbox != "URL vs URL":
        # print('is_uri from 192 line\n', is_url)
        spacy_pos = st.checkbox('Process Part-of-Speech analysis with SpaCy')
        # spacy_pos = False
        # rint('Scrape all', scrape_all)
        if api_selectbox == "TextRazor":
            extract_categories_topics = st.checkbox('Extract Categories and Topics')
    scrape_all = st.checkbox(
        "Scrape ALL the Entities descriptions from Wikipedia. This is a time-consuming task, so grab a coffee if you need all the descriptions in your CSV file. The descriptions of the Entities you select for your 'about' and 'mentions' schema properties will be scraped and present in the corresponding JSON-LD files", value=True)
    submitted = st.form_submit_button("Submit")
    if submitted:
        if not text_razor_key and not google_api:
            st.warning("Please fill out all the required fields")
        elif not text_input:
            st.warning("Please Enter a URL/Text in the required field")
        else:
            st.session_state.submit = True
            if api_selectbox == "TextRazor":
                if input_type_selectbox == "URL vs URL":
                    output1, output2, entities1, entities2, language = utils.get_df_url2url_razor(text_razor_key, urls,
                                                                                                  are_urls)
                    st.session_state.text_razor = True
                    st.session_state.google_api = False
                    st.session_state.df_url1 = pd.DataFrame(output1)
                    st.session_state.df_url2 = pd.DataFrame(output2)
                    lang = language
                else:
                    output, response, topics_output, categories_output = utils.get_df_text_razor(text_razor_key,
                                                                                                 text_input,
                                                                                                 extract_categories_topics,
                                                                                                 is_url, scrape_all)
                    st.session_state.text = response.cleaned_text
                    texts = st.session_state.text
                    st.session_state.text_razor = True
                    st.session_state.google_api = False
                    st.session_state.df_razor = pd.DataFrame(output)
                    if topics_output:
                        st.session_state.df_razor_topics = pd.DataFrame(topics_output)
                    if categories_output:
                        st.session_state.df_razor_categories = pd.DataFrame(categories_output)
                    lang = response.language
            elif api_selectbox == "Google NLP":
                if input_type_selectbox == "URL vs URL":
                    output1, output2, response1, response2 = utils.get_df_url2url_google(google_api, urls,
                                                                                         are_urls, scrape_all)
                    st.session_state.text_razor = False
                    st.session_state.google_api = True
                    st.session_state.df_url1 = pd.DataFrame(output1)
                    st.session_state.df_url2 = pd.DataFrame(output2)
                    lang = response1.language
                else:
                    output, response = utils.get_df_google_nlp(google_api, text_input, is_url, scrape_all)
                    st.session_state.text = text_input  # just gives the url for google api text_intput from url
                    st.session_state.google_api = True
                    st.session_state.text_razor = False
                    st.session_state.df_google = pd.DataFrame(output)
                    lang = response.language
            st.session_state.lang = lang
            language_option = lang

if 'submit' in st.session_state and ("text_razor" in st.session_state and st.session_state.text_razor == True):
    if st.session_state.last_field_type == "URL vs URL":
        df1 = st.session_state["df_url1"].drop(columns=["DBpedia Category", "Wikidata Id", "Wikipedia Link"])
        df2 = st.session_state["df_url2"].drop(columns=["DBpedia Category", "Wikidata Id", "Wikipedia Link"])
        ab = pd.merge(df1, df2, how='inner', on=["name"])
        ab.dropna(inplace=True)
        names = pd.DataFrame({"Entities": ab["name"].values.tolist()})
        amb = df1[~df1.name.isin(ab.name)]
        bma = df2[~df2.name.isin(ab.name)]
        st.write("### Entities")
        col1, col2, col3 = st.columns([1.25, .75, 3])

        # st.write('### Entities in both urls', names)
        col1.markdown("Entities in both URLs")
        col1.write(names)
        with col2:
            selection = st.radio(label='Select Entities', options=['Url1 only', 'Url2 only'])

        if "Url1 only" == selection:
            # st.write('### Entities in Url1 only', amb)
            col3.markdown("Entities in Url1")
            col3.write(amb)
        elif "Url2 only" == selection:
            # st.write('### Entities in Url2 only', bma)
            col3.markdown("Entities in Url2")
            col3.write(bma)

        download_buttons = ""
        download_buttons += utils.download_button(names, 'url_common.csv',
                                                  'Download common Entities CSV ✨', pickle_it=False)
        if not amb.empty:
            # st.write('### Entities in first url', amb)
            download_buttons += utils.download_button(amb, 'url1-url2.csv',
                                                      'Download url1 Entities CSV ✨', pickle_it=False)
        else:
            st.write("0 entities in url1 which are not present in url2")
        if not bma.empty:
            # st.write('### Entities in second url', bma)
            download_buttons += utils.download_button(bma, 'url2-url1.csv',
                                                      'Download url2 Entities CSV ✨', pickle_it=False)
        else:
            st.write("0 entities in url2 which are not present url1")
        st.markdown(download_buttons, unsafe_allow_html=True)

    else:
        text_input, is_url = utils.write_meta(text_input, meta_tags_only, is_url)
        if 'df_razor' in st.session_state:
            df = st.session_state["df_razor"]

        if len(df) > 0:
            df['temp'] = df['Relevance Score'].str.strip('%').astype(float)
            df = df.sort_values('temp', ascending=False)
            del df['temp']
            selected_about_names = st.multiselect('Select About Entities:', df.name)
            selected_mention_names = st.multiselect('Select Mentions Entities:', df.name)
            # --------------Frequency count--------------
            # if not url:
            utils.word_frequency(df, text_input, language_option,
                                 st.session_state.text)  # -----------------------Function call for textrazor-------------
            st.write('### Entities', df)
            theLength = (len(df["English Wikipedia Link"]))
            num = 0
            
            while num < theLength:
                linker = df["English Wikipedia Link"][num]
                linker2 = df["English Wikipedia Link"][num].replace('https://en.wikipedia.org',"https://wikipedia.org")
                with st.expander(f"""{df['name'][num]}"""):
                    st.write(f"""{{"@context": "http://schema.org",\n"@type": "Thing","name": "{df['name'][num]}",\n"description":"{df['description'][num]}",\n"SameAs": ["{linker}","{linker2}", "https://www.wikidata.org/wiki/{df['Wikidata Id'][num]}"]}},""")
                num = num + 1
            df = df.sort_values('Frequency', ascending=False)
            st.write('### Top 10 Entities by Frequency', df[['name', 'Frequency']].head(10))
        # print(is_url)
        # print(text_input)
        utils.conf(df, "Confidence Score")
        # st.write('### Entities', df)
        # st.write('#### Entity table Dimension', df.shape)
        # df1 = df.sort_values('Frequency', ascending=False)
        # st.write('### Top 10 Entities by Frequency', df1[['name', 'Frequency']].head(10))
        # st.write(response1)

        c, t = st.columns(2)
        if 'df_razor_categories' in st.session_state and extract_categories_topics:
            with c:
                df_categories = st.session_state["df_razor_categories"]
                st.write('### Categories', df_categories)
        if 'df_razor_topics' in st.session_state and extract_categories_topics:
            with t:
                df_topics = st.session_state["df_razor_topics"]
                st.write('### Topics', df_topics)

        if len(df) > 0:
            about_download_button = utils.download_button(
                utils.convert_schema("about", df.loc[df['name'].isin(selected_about_names)].to_json(orient='records'),
                                     scrape_all, st.session_state.lang), 'about-entities.json',
                'Download About Entities JSON-LD ( Yes ) ✨', pickle_it=False)


            if len(df.loc[df['name'].isin(selected_about_names)]) > 0:
                st.markdown(about_download_button, unsafe_allow_html=True)
            mention_download_button = utils.download_button(utils.convert_schema("mentions", df.loc[
                df['name'].isin(selected_mention_names)].to_json(orient='records'), scrape_all, st.session_state.lang),
                                                            'mentions-entities.json',
                                                            'Download Mentions Entities JSON-LD ( Yes ) ✨', pickle_it=False)
            if len(df.loc[df['name'].isin(selected_mention_names)]) > 0:
                st.markdown(mention_download_button, unsafe_allow_html=True)
        if "df_razor_topics" in st.session_state and extract_categories_topics:
            df_topics = st.session_state["df_razor_topics"]
            download_buttons = ""
            download_buttons += utils.download_button(df_topics, 'topics.csv', 'Download all Topics CSV ✨',
                                                      pickle_it=False)
            st.markdown(download_buttons, unsafe_allow_html=True)
        if "df_razor_categories" in st.session_state and extract_categories_topics:
            df_categories = st.session_state["df_razor_categories"]
            download_buttons = ""
            download_buttons += utils.download_button(df_categories, 'categories.csv', 'Download all Categories CSV ✨',
                                                      pickle_it=False)
            st.markdown(download_buttons, unsafe_allow_html=True)
        if len(df) > 0:
            download_buttons = ""
            download_buttons += utils.download_button(df, 'entities.csv', 'Download all Entities CSV ✨',
                                                      pickle_it=False)
            st.markdown(download_buttons, unsafe_allow_html=True)
        if spacy_pos:
            if st.session_state.lang in "eng":
                # print('textrazor-eng lang\n', st.session_state.lang)
                doc = st.session_state.en_nlp(st.session_state.text)
            elif st.session_state.lang in "ita":
                # print('textrazor-ita lang\n', st.session_state.lang)
                doc = st.session_state.it_nlp(st.session_state.text)
            visualize_parser(doc)

if 'submit' in st.session_state and ("google_api" in st.session_state and st.session_state.google_api == True):
    if st.session_state.last_field_type == "URL vs URL":
        df1 = st.session_state["df_url1"].drop(columns=["type", "Knowledge Graph ID"])
        df2 = st.session_state["df_url2"].drop(columns=["type", "Knowledge Graph ID"])

        ab = pd.merge(df1, df2, how='inner', on=["name"])
        names = pd.DataFrame({"Entities": ab["name"].values.tolist()})
        ab.dropna(inplace=True)
        amb = df1[~df1.name.isin(ab.name)]
        bma = df2[~df2.name.isin(ab.name)]
        st.write("### Entities")
        col1, col2, col3 = st.columns([1.25, .75, 3])

        # st.write('### Entities in both urls', names)
        col1.markdown("Entities in both URLs")
        col1.write(names)
        with col2:
            selection = st.radio(label='Select Entities', options=['Url1 only', 'Url2 only'])

        if "Url1 only" == selection:
            # st.write('### Entities in Url1 only', amb)
            col3.markdown("Entities in Url1")
            col3.write(amb)
        elif "Url2 only" == selection:
            # st.write('### Entities in Url2 only', bma)
            col3.markdown("Entities in Url2")
            col3.write(bma)

        download_buttons = ""
        download_buttons += utils.download_button(names, 'url_common.csv',
                                                  'Download common Entities CSV ✨', pickle_it=False)
        if not amb.empty:
            # st.write('### Entities in first url', amb)
            download_buttons += utils.download_button(amb, 'url1-url2.csv',
                                                      'Download url1 Entities CSV ✨', pickle_it=False)
        else:
            st.write("0 entities in url1 which are not present in url2")
        if not bma.empty:
            # st.write('### Entities in second url', bma)
            download_buttons += utils.download_button(bma, 'url2-url1.csv',
                                                      'Download url2 Entities CSV ✨', pickle_it=False)
        else:
            st.write("0 entities in url2 which are not present url1")
        st.markdown(download_buttons, unsafe_allow_html=True)
    else:
        text_input, is_url = utils.write_meta(text_input, meta_tags_only, is_url)

        if 'df_google' in st.session_state:
            df = st.session_state["df_google"]
        if len(df) > 0:
            df['temp'] = df['Salience'].str.strip('%').astype(float)
            df = df.sort_values('temp', ascending=False)
            del df['temp']
            selected_about_names = st.multiselect('Select About Entities:', df.name)
            selected_mention_names = st.multiselect('Select Mentions Entities:', df.name)
            if not is_url:
                utils.word_frequency_google(df, st.session_state.text)
            # ---------------------frequency counter
        utils.conf(df, "Confidence Score")
        st.write('### Entities', df)

        # st.write('#### Entity table Dimension', df.shape)
        # if not is_url:
        #     df1 = df.sort_values('Frequency', ascending=False)
        #     st.write('### Top 10 Entities', df1[['name', 'Frequency']].head(10))

        if len(df) > 0:
            about_download_button = utils.download_button(
                utils.convert_schema("about", df.loc[df['name'].isin(selected_about_names)].to_json(orient='records'),
                                     scrape_all, st.session_state.lang), 'about-entities.json',
                'Download About Entities JSON-LD ( Hi ) ✨', pickle_it=False)

            if len(df.loc[df['name'].isin(selected_about_names)]) > 0:
                st.markdown(about_download_button, unsafe_allow_html=True)

            mention_download_button = utils.download_button(utils.convert_schema("mentions", df.loc[
                df['name'].isin(selected_mention_names)].to_json(orient='records'), scrape_all, st.session_state.lang),
                                                            'mentions-entities.json',
                                                            'Download Mentions Entities JSON-LD ( Hi ) ✨', pickle_it=False)

            if len(df.loc[df['name'].isin(selected_mention_names)]) > 0:
                st.markdown(mention_download_button, unsafe_allow_html=True)
            download_buttons = ""
            download_buttons += utils.download_button(df, 'entities.csv', 'Download all Entities CSV ✨',
                                                      pickle_it=False)
            st.markdown(download_buttons, unsafe_allow_html=True)
        if spacy_pos:
            if st.session_state.lang in "eng":
                doc = st.session_state.en_nlp(st.session_state.text)
                # print('English', doc)
            elif st.session_state.lang in "ita":
                doc = st.session_state.it_nlp(st.session_state.text)
                # print('Itelian')
            visualize_parser(doc)
