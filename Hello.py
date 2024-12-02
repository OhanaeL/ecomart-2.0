import streamlit as st
from streamlit.logger import get_logger
import http.client
import google.generativeai as genai
import re
import json
from urllib.parse import quote
import os

# Constants for configuration
COEF_THAIBHAT_TO_SINGAPORE = 27.14
PLACEHOLDER_PRICE = 1000
DEFAULT_SEARCH_ITEM = "Lamp"
DEFAULT_ADDITIONAL_INFO = "Students"
DEFAULT_PRICE = 0
GREETING_MESSAGE = "Let Eco Mart know what you're looking for, and we'll guide you to eco-friendly options that align with your values, making conscious shopping choices easier than ever."

# Load API keys securely from environment variables
API_KEYS = {"APIKey1": "1d02052b51msh6dee74f2642bb67p1ab876jsn345ba5f417d8", 
           "APIKey2": "1d02052b51msh6dee74f2642bb67p1ab876jsn345ba5f417d8", 
           "APIKey3": "4a10d4e4d5mshfbd8cd7450cc2c7p1e7032jsndbfb762af901", 
           "APIKey4": "8117d35566mshb8c846b8b54eb78p1add92jsn71abb44d24df", 
           "APIKey5": "ac3b1d622bmsh1de025fe61bdef8p1d88edjsn7d433b07cd39"}

# Initialize session state variables if they don't exist
if 'replyText' not in st.session_state:
    st.session_state['replyText'] = GREETING_MESSAGE

if 'loadingMessage' not in st.session_state:
    st.session_state['loadingMessage'] = ""

if 'products_with_reasons' not in st.session_state:
    st.session_state['products_with_reasons'] = []

if "themes" not in st.session_state: 
    st.session_state.themes = {"current_theme": "light", "refreshed": True}

# Initialize Google Generative AI
genai.configure(api_key="AIzaSyAgxoQ-YcW77-rz_4imbxWdy-JHg52r-CI")
model = genai.GenerativeModel('gemini-pro')

LOGGER = get_logger(__name__)

def run():
    """Main function to run the Streamlit app."""
    # Set up Streamlit page configuration
    st.set_page_config(
        page_title="Eco Mart",
        page_icon="🍃",
        layout="wide"
    )

    # Display image and title
    st.image('image.png', width=75)
    st.markdown("# Find Your Products Here!")
    st.subheader("Your Eco-Friendly Shopping Advisor.")

    st.sidebar.header("Find Your Products Here!")

    # Sidebar options
    api_key = API_KEYS[st.sidebar.selectbox(
        'API Key for RapidAPI',
        list(API_KEYS.keys())
    )]

    search_item = st.sidebar.text_input('Search Item', DEFAULT_SEARCH_ITEM)
    price = st.sidebar.number_input('Maximum Price in Baht', min_value=0, value=DEFAULT_PRICE, step=200)
    additional_info = st.sidebar.text_input('Additional Product Info', DEFAULT_ADDITIONAL_INFO)

    if st.sidebar.button('Suggest Products'):
        progress_text = "Fetching Products. Please wait."
        progress_bar = st.progress(0, text=progress_text)
        amazon_data = fetch_amazon_data(api_key, search_item, price, additional_info)
        st.session_state['products_with_reasons'] = esg_module(amazon_data, additional_info, search_item, progress_bar)

    # Display products with reasons
    for product in st.session_state['products_with_reasons']:
        display_product(product)

    # Display additional reply text
    st.markdown(st.session_state['replyText'])

def fetch_amazon_data(api_key, search_item, price, additional_info):
    """Fetches product data from Amazon via RapidAPI."""
    conn = http.client.HTTPSConnection("real-time-amazon-data.p.rapidapi.com")
    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': "real-time-amazon-data.p.rapidapi.com"
    }

    price_text = "" if price == 0 else f"&max_price={round(price / COEF_THAIBHAT_TO_SINGAPORE)}"
    search_item_encoded = quote(search_item)
    additional_info_encoded = quote(additional_info)
    query_string = f"/search?query={search_item_encoded}%20eco%20friendly%20{additional_info_encoded}&page=1&country=SG&category_id=aps{price_text}&sort_by=RELEVANCE&"

    try:
        conn.request("GET", query_string, headers=headers)
        res = conn.getresponse()
        return res.read().decode("utf-8")
    except Exception as e:
        LOGGER.error(f"Error fetching Amazon data: {e}")
        return "[]"

def data_parser(data):
    """Parses the Amazon product data."""
    amazon_data = json.loads(data)
    all_data = amazon_data.get('data', {}).get('products', [])
    
    products_data = []
    for i in all_data:
        product = {
            'asin': i.get('asin'),
            'product_title': i.get('product_title'),
            'product_price': round(eval(i.get('product_price', "0").replace("S$", "")) * COEF_THAIBHAT_TO_SINGAPORE) if i.get('product_price') else PLACEHOLDER_PRICE,
            'product_star_rating': i.get('product_star_rating'),
            'product_url': i.get('product_url'),
            'product_photo': i.get('product_photo'),
            'climate_pledge_friendly': i.get('climate_pledge_friendly')
        }
        products_data.append(product)
    
    return products_data

def esg_module(data, additional_info, search_item, progress_bar):
    """Evaluates the ESG compliance of products."""
    amazon_data = data_parser(data)
    chat = model.start_chat(history=[])
    products_with_reasons = []

    if len(amazon_data) >= 5:
        chat.send_message("""You are an AI Model that suggests users eco-friendly, sustainable or ESG compliant products.""")

        prompt = f"Given dictionary: {amazon_data}"
        chat.send_message(prompt)
        progress_bar.progress(50, text='Evaluating ESG Compliance...')

        response = chat.send_message("""Return a structured string with product IDs and detailed reasons for choosing them.""")
        
        matches = re.findall(r"\('([A-Z0-9]+)', '([^']+)'\)", response.text)
        results = [(product_id, description) for product_id, description in matches]

        progress_bar.progress(75, text='Generating Response...')

        for result in results:
            for item in amazon_data:
                if str(result[0]) in item.values():
                    product = item.copy()
                    product["reasons"] = result[1]
                    products_with_reasons.append(product)

        progress_bar.empty()
    else:
        chat.send_message('Not enough data that fits the requirements.')

    return products_with_reasons

def display_product(product):
    """Displays product information in Streamlit."""
    st.write(f"{st.session_state['products_with_reasons'].index(product)+1}. {product['product_title']}")
    st.image(product["product_photo"], width=200)
    st.write(f"Price: {product['product_price']} Baht")
    st.write(f"Rating: {product['product_star_rating']} Stars")
    st.markdown(f"Reason: {product['reasons']}")
    st.markdown(f"Link: {product['product_url']}")

if __name__ == "__main__":
    run()
