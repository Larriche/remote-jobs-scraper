import sqlite3

def create_table(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)

# Create the database for storing the jobs
conn = sqlite3.connect('jobs.db')

job_table_sql = """
                CREATE TABLE IF NOT EXISTS jobs(
                    id INT AUTO INCREMENT PRIMARY KEY,
                    job_id VARCHAR(255) UNIQUE,
                    title VARCHAR(255),
                    company VARCHAR(255),
                    emails TEXT,
                    url VARCHAR(255),
                    applied TINYINT,
                    match DECIMAL
                )
                """

if conn is not None:
    # create jobs table
    create_table(conn, job_table_sql)
else:
    print("Error! cannot create the database connection.")

