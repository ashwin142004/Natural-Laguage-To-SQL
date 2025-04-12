from dotenv import load_dotenv
import os
import sqlite3
import streamlit as st
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Combine prompt and question into a single string
def get_gemini_response(prompt, question):
    try:
        full_prompt = f"{prompt}\nQuestion: {question}"
        response = model.generate_content(full_prompt)
        parts = response.candidates[0].content.parts
        text = ' '.join([part.text for part in parts])
        return text.strip().strip('`').strip()
    except Exception as e:
        st.error(f"Error generating text: {e}")
        return None

def read_sql_query(sql, db):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
    except sqlite3.Error as e:
        st.error(f"SQL error: {e}")
        return None
    finally:
        connection.close()

prompt = """
You are an expert in converting English questions to SQL queries.
The SQL database has the table 'employee' with the following columns:
EMP_NAME varchar(50), EMP_ID varchar(50), DESIGNATION varchar(50), EMP_AGE int

Examples:

1. How many entries of records are present?
SQL: SELECT COUNT(*) FROM employee;

2. What is the name of the employee with ID E123?
SQL: SELECT EMP_NAME FROM employee WHERE EMP_ID = 'E123';

3. Tell me all the employees with designation as Software Engineer?
SQL: SELECT * FROM employee WHERE DESIGNATION = 'Software Engineer';

Important rules:
- Do not use DML commands like INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE etc.
- Only output the SQL query.
- Do not include triple backticks (```).
"""

# Streamlit UI
st.set_page_config(page_title="AskSQL")
st.header("Gemini Application to Retrieve SQL Data Using English")
question = st.text_input("Enter your question: ", key="input")
submit = st.button("Submit")

if submit:
    sql_query = get_gemini_response(prompt, question)

    if sql_query is None or sql_query.strip() == "":
        st.error("Failed to generate SQL query.")
    else:
        st.subheader("Generated SQL Query")
        st.code(sql_query, language='sql')

        result = read_sql_query(sql_query, "employee.db")

        if result:
            st.subheader("SQL Output")
            for row in result:
                st.write(row)
        else:
            st.error("No results or query failed.")

