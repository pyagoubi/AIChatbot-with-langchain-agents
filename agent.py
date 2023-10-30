import pandas as pd
from langchain.agents import create_sql_agent
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.agents.agent_types import AgentType
from sqlalchemy import create_engine
from config import Config
from langchain.callbacks.streaming_stdout_final_only import (
    FinalStreamingStdOutCallbackHandler,
)



def create_agent(API_KEY, dbconnection=Config.dbconnection, pandas_agent=False):
    """
    Create an agent that can access and use a large language model (LLM).

    Args:
        filename: The path to the CSV file that contains the data.

    Returns:
        An agent that can access and use the LLM.
    """

    # Create an OpenAI object.

    llm = OpenAI(
        streaming=True, callbacks=[FinalStreamingStdOutCallbackHandler()], temperature=0, openai_api_key=API_KEY
    )

    db = SQLDatabase.from_uri(dbconnection)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    if pandas_agent == True:
        # Create a SQLAlchemy engine
        engine = create_engine(dbconnection)

        # Read the table into a pandas DataFrame
        df = pd.read_sql_table('UserExperiences', engine)

        agent_executor = create_pandas_dataframe_agent(llm, df, verbose=False)
    else:
        agent_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=False,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        )

    return agent_executor


def query_agent(agent, query):
    """
    Query an agent and return the response as a string.

    Args:
        agent: The agent to query.
        query: The query to ask the agent.

    Returns:
        The response from the agent as a string.
    """

    prompt = (
            """               
                For the following query, if it requires drawing a table, reply as follows:
                {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}
    
                If the query requires creating a bar chart, reply as follows:
                {"bar": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}
    
                If the query requires creating a line chart, reply as follows:
                {"line": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}
    
                There can only be two types of chart, "bar" and "line".
                If it requires drawing a table, bar or chart, also summarize the results in a few words in following form:
                {"answer": "summary"}
    
                If it is just asking a question that requires neither, reply as follows:
                {"answer": "answer"}
                Example:
                {"answer": "The title with the highest rating is 'Gilead'"}
    
                If you do not know the answer, reply as follows:
                {"answer": "I do not know."}
    
                Return all output as a string.
    
                All strings in "columns" list and data list, should be in double quotes,
    
                For example: {"columns": ["title", "ratings_count"], "data": [["Gilead", 361], ["Spider's Web", 5164]]}
    
                Lets think step by step.         
                           
                Below is the query.
                Query: 
                """
            + query
    )

    # Run the prompt through the agent.
    response = agent.run(prompt)

    # Convert the response to a string.
    return response.__str__()



