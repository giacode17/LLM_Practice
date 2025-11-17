# Go T-Shirts Stock Checker

A natural language SQL query system for t-shirt inventory management. This application uses LangChain with OpenAI's GPT-4o-mini to convert natural language questions into SQL queries, providing an intuitive interface for querying inventory and revenue data.

## Features

- **Natural Language Queries**: Ask questions in plain English about inventory and revenue
- **Few-Shot Learning**: Uses semantic similarity to select relevant examples for improved accuracy
- **Real-time Database Access**: Connects directly to MySQL database for up-to-date information
- **User-Friendly Interface**: Clean Streamlit web interface with formatted responses
- **SQL Query Validation**: Built-in query checker to catch common SQL errors

## Tech Stack

- **Frontend**: Streamlit
- **LLM Framework**: LangChain with OpenAI GPT-4o-mini
- **Database**: MySQL
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Store**: Chroma (for semantic example selection)

## Database Schema

### Tables

**t_shirts**
- `t_shirt_id`: Primary key
- `brand`: ENUM ('Van Huesen', 'Levi', 'Nike', 'Adidas')
- `color`: ENUM ('Red', 'Blue', 'Black', 'White')
- `size`: ENUM ('XS', 'S', 'M', 'L', 'XL')
- `price`: INT (between 10 and 50)
- `stock_quantity`: INT

**discounts**
- `discount_id`: Primary key
- `t_shirt_id`: Foreign key to t_shirts
- `pct_discount`: DECIMAL (0-100)

## Prerequisites

- Python 3.8+
- MySQL Server
- OpenAI API key

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd LLM_go_tshirts
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up MySQL database

```bash
mysql -u root -p < database/db_shop.sql
```

This will:
- Create the `go_tshirts` database
- Create the `t_shirts` and `discounts` tables
- Populate sample data

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_NAME=go_tshirts
```

**Important**: Never commit the `.env` file to version control. It's already included in `.gitignore`.

## Usage

### Running the Application

```bash
streamlit run main.py
```

The application will open in your default browser at `http://localhost:8501`

### Example Questions

- "How many white color Levi's shirts do I have?"
- "How much is the total price of the inventory for all S-size t-shirts?"
- "If we have to sell all the Levi's T-shirts today. How much revenue will our store generate without discount?"
- "How many Nike t-shirts do we have in XS size?"
- "What is the total revenue if we sell all large size Nike t-shirts after discounts?"

### Testing the Connection

Run the test script to verify your setup:

```bash
python test.py
```

This will:
1. Test the OpenAI API connection
2. Test the database connection
3. Display sample table information

## Project Structure

```
LLM_go_tshirts/
├── main.py                 # Streamlit web application
├── langchain_helper.py     # LangChain setup and SQL chain configuration
├── few_shots.py           # Few-shot examples for training
├── test.py                # Connection testing script
├── database/
│   └── db_shop.sql        # Database schema and sample data
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore rules
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## How It Works

1. **User Input**: User enters a natural language question in the Streamlit interface
2. **Example Selection**: Semantic similarity selector finds the most relevant few-shot examples
3. **Query Generation**: GPT-4o-mini generates SQL query based on the question and examples
4. **Query Validation**: Built-in checker validates the SQL syntax
5. **Execution**: Query is executed against the MySQL database
6. **Response Formatting**: Results are formatted and displayed to the user

## Security Notes

- Never commit credentials to version control
- Use environment variables for all sensitive data
- The `.env` file is excluded from git via `.gitignore`
- Consider using a read-only database user for production deployments
- Rotate any exposed credentials immediately

## Development

### Adding New Few-Shot Examples

Edit `few_shots.py` to add new examples:

```python
{
    'Question': "Your question here",
    'SQLQuery': "SELECT ... your SQL query",
    'SQLResult': "Result of the SQL query",
    'Answer': "Expected answer"
}
```

### Customizing the LLM

Modify parameters in `langchain_helper.py`:

```python
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)  # Adjust temperature
k=2,  # Number of examples to retrieve
```

## Troubleshooting

### Database Connection Issues

- Verify MySQL is running
- Check credentials in `.env`
- Ensure database `go_tshirts` exists
- Test connection with `python test.py`

### OpenAI API Errors

- Verify `OPENAI_API_KEY` in `.env`
- Check API quota and billing
- Ensure you have access to GPT-4o-mini model

### Missing Dependencies

```bash
pip install -r requirements.txt --upgrade
```

