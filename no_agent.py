import openai
import pandas as pd
from sqlalchemy import create_engine
from config import Config

def easy_mode(input_text, openaikey):

    openai.api_key = openaikey

    engine = create_engine(Config.dbconnection)

    # Read the table into a pandas DataFrame
    df = pd.read_sql_table('UserExperiences', engine)

    prompt = """Please regard the following data:\n {}. This data is complete. Answer the following 
                question and please return only value: {}""".format(df, input_text)

    request = openai.ChatCompletion.create(
        model="gpt-4-32k",
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    result = request['choices'][0]['message']['content']

    return result