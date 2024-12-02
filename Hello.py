# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger
import http.client
import google.generativeai as genai
import re
import json
from urllib.parse import quote

LOGGER = get_logger(__name__)

genai.configure(api_key=st.secrets["GPT_API_KEY"])
model = genai.GenerativeModel('gemini-pro')
ms = st.session_state

COEF_THAIBHAT_TO_SINGAPORE = 27.14
PLACEHOLDER_PRICE = 1000

APIKeys = {"APIKey1": st.secrets["RAPID_API_KEY1"], 
           "APIKey2": st.secrets["RAPID_API_KEY2"], 
           "APIKey3": st.secrets["RAPID_API_KEY3"], 
           "APIKey4": st.secrets["RAPID_API_KEY4"], 
           "APIKey5": st.secrets["RAPID_API_KEY5"]}

products_with_reasons = []
greeting_message = "Let Eco Mart know what you're looking for, and we'll guide you to eco-friendly options that align with your values, making conscious shopping choices easier than ever."

if 'replyText' not in ms:
    ms['replyText'] = greeting_message

if 'loadingMessage' not in ms:
    ms['loadingMessage'] = ""

if 'products_with_reasons' not in ms:
    ms['products_with_reasons'] = []

if "themes" not in ms: 
    ms.themes = {"current_theme": "light", "refreshed": True}

def run():
        
    global my_bar 

    st.set_page_config(
        page_title="Eco Mart",
        page_icon="🍃",
        layout="wide"
    )

    st.image('image.png', width = 75)
    st.markdown("# Find Your Products Here!")
    st.subheader("Your Eco-Friendly Shopping Advisor.")
    
    st.sidebar.header("Find Your Products Here!")
    
    APIKey = APIKeys[st.sidebar.selectbox(
    'API Key for RapidAPI',
    ("APIKey1", "APIKey2", "APIKey3", "APIKey4", "APIKey5"))]

    searchItem = st.sidebar.text_input('Search Item', 'Lamp')
    
    price = st.sidebar.number_input('Maximum Price in Bhat', min_value = 0, value = 0, step = 200)

    #store = st.sidebar.selectbox(
    #'Online Shops',
    #("All", "Amazon", "Lazada", "Shopee"))

    store = "Amazon"

    additionalInfo = st.sidebar.text_input('Additional Product Info', 'Students')

    if st.sidebar.button('Suggest Products'):
        progress_text = "Fetching Products. Please wait."
        my_bar = st.progress(0, text=progress_text)
        amazon_data = fetch_amazon_data(APIKey, searchItem, price, additionalInfo)
           
        ms['products_with_reasons'] = esg_module(amazon_data, additionalInfo, searchItem)

    for product in ms['products_with_reasons']:
        st.write(str(ms['products_with_reasons'].index(product)+1)+". "+product["product_title"])
        st.image(product["product_photo"], width = 200)
        st.write("Price: "+str(product["product_price"])+" Bhat")
        st.write("Rating: "+str(product["product_star_rating"])+" Stars")
        st.markdown("Reason: "+product["reasons"])
        st.markdown("Link: "+product["product_url"])

    st.write(st.session_state['replyText'])

def data_pharser(data):
    my_bar.progress(25, text='Parsing Data...')
    amazon_data = json.loads(data)
    all_data = amazon_data['data']['products']
    products_data = []
    for i in all_data:
        temp = {}
        temp['asin'] = i['asin']
        temp['product_title'] = i['product_title']
        if i['product_price']:
            # Calculate the price and round it
            temp['product_price'] = round(eval(i['product_price'].replace("S$", "")) * COEF_THAIBHAT_TO_SINGAPORE)
        else:
            # Assign the placeholder price
            temp['product_price'] = PLACEHOLDER_PRICE
        temp['product_star_rating'] = i['product_star_rating']
        temp['product_url'] = i['product_url']
        temp['product_photo'] = i['product_photo']
        temp['climate_pledge_friendly'] = i['climate_pledge_friendly']
        products_data.append(temp)
    return products_data

def esg_module(data, additionalInfo, searchItem):
    amazon_data = data_pharser(data)
    chat = model.start_chat(history=[])
    products_with_reasons = []
    my_bar.progress(30, text='Evaluating ESG Compliance... 1/2')
    if len(amazon_data) >= 5:
        chat.send_message("""You are an AI Model that suggests users eco-friendly,sustainable or esg compliant products from a given dictionary of products. 
                        You will guesstimates a product based on the keyword used in the title as well as if they are cilmate pledge friendly or not. You are allowed to look up information for the manufacturers info or anything that would be helpful to you.
                        At least return 5 products as well as a detailed explaination on you've chosen them. Even if you can't find them, at least choose the best 5 options and why the user should buy them.""")

        prompt = "Given dictionary: "+str(amazon_data)
        chat.send_message(prompt)
        my_bar.progress(55, text='Evaluating ESG Compliance... 2/2')
        response = chat.send_message("""Follow these instructions very carefully if you mess this step up the whole project will fail. 
                                    Return the asin of the product of the products that you chose in the last step into a structured string format where each tuple provides information about a specific product, including its asin and a long detailed eco-friendly or esg reason for choosing it, or a reason to buy it. Example: "[('asin1', 'reason_for_choosing1'), ('asin2', 'reason_for_choosing2')]". Do not put any bolds. The resulting string will be passed into the python eval() function so keeping the format is very imporatnt.""")
        
        pattern = r"\('([A-Z0-9]+)', '([^']+)'\)"

        # Use findall to extract matches
        matches = re.findall(pattern, response.text)

        # List to store tuples of product IDs and descriptions
        results = [(product_id, description) for product_id, description in matches]

        # Print the list of tuples
        my_bar.progress(75, text='Generating Response...')
        reply(chat, 'You can speak normally now. Explain how the products you chose is eco-friendly or environmentally safe or esg compliant. Additionally tell a list of things to keep an eye out upon buying '+ data)

        # Iterate through both lists simultaneously
        for result in results:
            for item in amazon_data:
                if str(result[0]) in item.values():
                    temp = {}
                    temp['asin'] = item['asin']
                    temp['product_title'] = item['product_title']
                    temp['product_price'] = item['product_price']
                    temp['product_star_rating'] = item['product_star_rating']
                    temp['product_url'] = item['product_url']
                    temp['product_photo'] = item['product_photo']
                    temp['climate_pledge_friendly'] = item['climate_pledge_friendly']
                    temp["reasons"] = result[1]
                    products_with_reasons.append(temp)
                    break

        # Print the resulting list of dictionaries
        my_bar.empty()
    else:
        reply(chat, 'Reply with something along the lines of not having enough data that fits the requirements.'+ data)

    return products_with_reasons

def reply(chat, prompt):
    st.session_state['replyText'] = chat.send_message(prompt).text
    return

def fetch_amazon_data(api_key, search_item, price, additionalInfo):

    conn = http.client.HTTPSConnection("real-time-amazon-data.p.rapidapi.com")
    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': "real-time-amazon-data.p.rapidapi.com"
    }
    price_text = "" if price == 0 else f"&max_price={round(price / COEF_THAIBHAT_TO_SINGAPORE)}"
    search_item_encoded = quote(search_item)
    additional_info_encoded = quote(additionalInfo)
    query_string = f"/search?query={search_item_encoded}%20eco%20friendly%20{additional_info_encoded}&page=1&country=SG&category_id=aps{price_text}&sort_by=RELEVANCE&"
    
    conn.request("GET", query_string, headers=headers)
    res = conn.getresponse()
    
    return res.read().decode("utf-8")

if __name__ == "__main__":
    run()


