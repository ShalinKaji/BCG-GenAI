from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Load the company data from saved files
Apple_df = pd.read_csv('Apple (AAPL)_financials.csv')
Microsoft_df = pd.read_csv('Microsoft (MSFT)_financials.csv')
Tesla_df = pd.read_csv('Tesla (TSLA)_financials.csv')

company_data = {
    'Apple': Apple_df,
    'Microsoft': Microsoft_df,
    'Tesla': Tesla_df
}

def simple_chatbot(user_query):
    user_query = user_query.lower()
    if "total revenue" in user_query:
        company = get_company_from_query(user_query)
        if company:
            total_revenue = company_data[company]['Total Revenue'].values[-1]
            return f"The latest total revenue for {company} is ${total_revenue} million."
    elif "net income" in user_query:
        company = get_company_from_query(user_query)
        if company:
            net_income = company_data[company]['Net Income'].values[-1]
            return f"The latest net income for {company} is ${net_income} million."
    elif "total assets" in user_query:
        company = get_company_from_query(user_query)
        if company:
            total_assets = company_data[company]['Total Assets'].values[-1]
            return f"The latest total assets for {company} are ${total_assets} million."
    elif "liabilities" in user_query:
        company = get_company_from_query(user_query)
        if company:
            liabilities = company_data[company]['Total Liabilities'].values[-1]
            return f"The latest total liabilities for {company} are ${liabilities} million."
    else:
        return "Sorry, I can only provide information on total revenue, net income, total assets, and liabilities for Apple, Microsoft, and Tesla."

def get_company_from_query(query):
    for company in company_data.keys():
        if company.lower() in query:
            return company
    return None

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def chat():
    user_query = request.json.get("query")
    response = simple_chatbot(user_query)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
