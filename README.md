# EcoMart🍃: Eco-Friendly Product Search

EcoMart is a simple web application built with **Streamlit** that helps users find eco-friendly alternatives for products they want to buy. The app utilizes the **Amazon Product API** from **RapidAPI** to fetch data and recommend sustainable, eco-friendly products based on user preferences. The inventory of products can be easily modified using RapidAPI keys, and the application supports customizable search features.

## Features

- **Search for eco-friendly alternatives**: Users can search for items and discover sustainable alternatives based on product names, features, and sustainability ratings.
- **Integration with Amazon API**: Retrieves product data, including names, ratings, images, and eco-friendly information.
- **Customizable price filter**: Set a maximum price for the products to find alternatives within your budget.
- **Dynamic inventory**: Easily change the inventory by using different API keys from RapidAPI.

## Technologies Used

- **Streamlit**: For building the interactive web application.
- **Pandas**: For handling and analyzing data.
- **Pydeck**: For displaying geographical data, if necessary.
- **Google Generative AI**: For AI-generated suggestions and eco-friendly insights.
- **RapidAPI**: For accessing the Amazon Product API to fetch product data.

## Installation

Follow these steps to set up the project on your local machine:

### Prerequisites
1. Python 3.7 or higher.
2. **Streamlit** installed on your machine.
3. A **RapidAPI account** to obtain API keys for the Amazon Product API.

4. ## Installation Steps

1. Clone this repository:

   ```bash
   git clone https://github.com/OhanaeL/ecomart-2.0.git
   cd ecomart-2.0
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Obtain your **RapidAPI API keys**:
   - Sign up at [RapidAPI](https://rapidapi.com/).
   - Go to the **Amazon Product API** and get your API keys.

4. Update the API keys in the `APIKeys` dictionary in the code:

   ```python
   APIKeys = {
       "APIKey1": "your-api-key-here",
       "APIKey2": "your-api-key-here",
       "APIKey3": "your-api-key-here"
   }
   ```

5. Run the application:

   ```bash
   streamlit run app.py
   ```

6. Open the app in your browser (usually at `http://localhost:8501`).

## How to Use

1. **Search Item**: Enter the name of the product you want to find eco-friendly alternatives for (e.g., "Lamp").
2. **Maximum Price**: Set a maximum price for the search results in Thai Baht.
3. **Store Selection**: Choose between "Amazon" or "All" for product sources.
4. **Additional Product Info**: Specify any additional requirements or context for the product (e.g., "Suggest for Students").
5. **Get Eco-Friendly Suggestions**: Click the "Suggest Eco Friendly Products" button to retrieve eco-friendly alternatives.

## Example Usage

- **Search for Eco-Friendly Lamp**:
   - Type "Lamp" in the search field, set the maximum price, and click the "Suggest Eco Friendly Products" button.
   - The app will provide a list of sustainable alternatives from Amazon.

## API Keys

In order to fetch product data, you will need API keys from **RapidAPI**. Replace the API keys in the `APIKeys` dictionary:

```python
APIKeys = {
    "APIKey1": "your-api-key-here",
    "APIKey2": "your-api-key-here",
    "APIKey3": "your-api-key-here"
}
```

## Contributions

If you’d like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch`.
3. Make changes and commit them: `git commit -am 'Add feature'`.
4. Push the branch to your fork: `git push origin feature-branch`.
5. Create a pull request to merge your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
