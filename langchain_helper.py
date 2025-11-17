import os
import re

from dotenv import load_dotenv
from langchain.chains.sql_database.prompt import PROMPT_SUFFIX, _mysql_prompt
from langchain_community.utilities import SQLDatabase
from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import FewShotPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_experimental.sql import SQLDatabaseChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from few_shots import few_shots

load_dotenv()  # loads OPENAI_API_KEY, DB creds, etc.

def _extract_sql(text: str) -> str:
    if not isinstance(text, str):
        return text
    # strip markdown fences
    text = re.sub(r"^\s*```(?:sql)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```\s*$", "", text)
    # strip leading 'SQLQuery:' label if present
    text = re.sub(r"^\s*SQLQuery\s*:\s*", "", text, flags=re.I)
    # stop at the next section label if the model added one
    text = re.split(r"\b(SQLResult|Answer)\b\s*:", text, maxsplit=1)[0]
    # grab from first SQL keyword onward
    m = re.search(r"\b(SELECT|WITH|INSERT|UPDATE|DELETE)\b.*", text, flags=re.I | re.S)
    text = m.group(0) if m else text
    return text.strip()

def get_few_shot_db_chain():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")

    # Validate required environment variables
    if not all([db_user, db_password, db_host, db_name]):
        raise ValueError(
            "Missing required environment variables. Please set DB_USER, DB_PASSWORD, DB_HOST, and DB_NAME in .env file"
        )

    # Requires `pymysql`
    db = SQLDatabase.from_uri(
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",
        sample_rows_in_table_info=3,
        # engine_args={"echo": True},  # uncomment to see SQLAlchemy statements
    )


    # Instantiate the LLM (reads OPENAI_API_KEY from env)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Add "input" key to each example for semantic similarity matching
    few_shots_with_input = [{**ex, "input": ex["Question"]} for ex in few_shots]

    # Create semantic similarity example selector using vector store
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples=few_shots_with_input,
        embeddings=embeddings,
        vectorstore_cls=Chroma,
        k=2,  # how many examples to retrieve
        input_keys=["input"]
    )

    mysql_prompt = _mysql_prompt


    example_prompt = PromptTemplate(
        input_variables=["Question", "SQLQuery", "SQLResult","Answer",],
        template="\nQuestion: {Question}\nSQLQuery: {SQLQuery}\nSQLResult: {SQLResult}\nAnswer: {Answer}",
    )

    few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix=mysql_prompt,
        suffix=PROMPT_SUFFIX,
        input_variables=["input", "table_info", "top_k"]
    )

    new_chain = SQLDatabaseChain.from_llm(
        llm=llm,
        db=db,
        prompt=few_shot_prompt,
        verbose=True,
        use_query_checker=True,  # catches common SQL issues
        top_k=10,  # default LIMIT size passed into the prompt
        return_sql=True,
        input_key="input",
    )

    def run(question: str):
        out = new_chain.invoke({"input": question})
        raw_sql = out["result"]
        sql = _extract_sql(raw_sql)
        return db.run(sql)

    return new_chain, run




