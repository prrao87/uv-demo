"""
Create a graph in Kùzu using the given structured data.
"""

import os
import shutil

import kuzu
import polars as pl
from dotenv import load_dotenv
from openai import OpenAI


def init_database(db_name: str = "test_kuzudb") -> kuzu.Connection:
    """Initialize the database and connection"""
    shutil.rmtree(db_name, ignore_errors=True)
    db = kuzu.Database(db_name)
    return kuzu.Connection(db)


def init_openai() -> OpenAI:
    """Initialize OpenAI client"""
    load_dotenv()
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def embed(query: str, client: OpenAI) -> list:
    """Get embeddings for a text query"""
    response = client.embeddings.create(model="text-embedding-3-small", input=query)
    return response.data[0].embedding


def create_tables(conn: kuzu.Connection) -> None:
    """Create the node and relationship tables using the graph schema"""
    conn.execute("""
        CREATE NODE TABLE IF NOT EXISTS Actor(name STRING, age INT64, PRIMARY KEY(name));
        CREATE NODE TABLE IF NOT EXISTS Movie(title STRING, year INT64, summary STRING, PRIMARY KEY(title));
        CREATE NODE TABLE IF NOT EXISTS Director(name STRING, age INT64, PRIMARY KEY(name));
        CREATE NODE TABLE IF NOT EXISTS Character(name STRING, description STRING, PRIMARY KEY(name));
        CREATE NODE TABLE IF NOT EXISTS Writer(name STRING, age INT64, PRIMARY KEY(name));
        CREATE REL TABLE IF NOT EXISTS ACTED_IN(FROM Actor TO Movie);
        CREATE REL TABLE IF NOT EXISTS PLAYED(FROM Actor TO Character);
        CREATE REL TABLE IF NOT EXISTS DIRECTED(FROM Director TO Movie);
        CREATE REL TABLE IF NOT EXISTS PLAYED_ROLE_IN(FROM Character TO Movie);
        CREATE REL TABLE IF NOT EXISTS RELATED_TO(FROM Character TO Character, relationship STRING);
        CREATE REL TABLE IF NOT EXISTS WROTE(FROM Writer TO Movie);
    """)
    print("Finished creating node and relationship tables")


def ingest_data(conn: kuzu.Connection, base_path: str) -> None:
    """Ingest CSV data into the graph"""
    files = {
        "Actor": "actor.csv",
        "Movie": "movie.csv",
        "Director": "director.csv",
        "Character": "character.csv",
        "Writer": "writer.csv",
        "ACTED_IN": "acted_in.csv",
        "DIRECTED": "directed.csv",
        "PLAYED": "played.csv",
        "PLAYED_ROLE_IN": "played_role_in.csv",
        "RELATED_TO": "related_to.csv",
        "WROTE": "wrote.csv",
    }
    ddl_statements = [f"COPY {table} FROM '{base_path}/{file}';" for table, file in files.items()]

    for statement in ddl_statements:
        print(f"Running: {statement}")
        conn.execute(statement)
    print("---\nFinished ingesting data")


def add_movie_embeddings(conn: kuzu.Connection, base_path: str, openai_client: OpenAI) -> None:
    """Add embedding vectors to movie nodes"""
    df = pl.read_csv(f"{base_path}/movie.csv", has_header=False).rename(
        {"column_1": "title", "column_2": "year", "column_3": "summary"}
    )
    # Generate embeddings for the movie summaries and store them in the DataFrame
    final_df = df.with_columns(  # noqa: F841
        pl.col("summary")
        .map_elements(lambda x: embed(x, openai_client), return_dtype=pl.List(pl.Float32))
        .alias("vector")
    )
    # Alter the Movie table to add the vector column
    conn.execute("ALTER TABLE Movie ADD vector DOUBLE[1536];")
    print("Added a new column `vector` to the Movie table")
    # Load the data into the graph
    conn.execute(
        """
        LOAD FROM final_df
        MERGE (m:Movie {title: title})
        ON MATCH SET m.vector = vector
        """
    )
    print("Inserted the embedding data into the graph!")


def query_movie_cast(conn: kuzu.Connection) -> None:
    """Query and print actor-character relationships"""
    print("---\nHere are the actors and the characters they played in Interstellar:")
    res = conn.execute(
        """
        MATCH (a:Actor)-[:ACTED_IN]->(m:Movie {title: "Interstellar"}),
              (a)-[:PLAYED]->(c:Character)
        RETURN DISTINCT a.name, c.name
        """
    )
    while res.has_next():
        data = res.get_next()
        print(f"{data[0]} -> {data[1]}")


def similarity_search(conn: kuzu.Connection, query: str, openai_client: OpenAI) -> pl.DataFrame:
    """Search for movies similar to query"""
    query_vector = embed(query, openai_client)
    res = conn.execute(
        """
        MATCH (m:Movie)<-[:WROTE]-(w:Writer)
        WITH m, w, array_cosine_similarity(m.vector, $query_vector) AS similarity
        RETURN m.title AS title, similarity, m.summary AS summary, COLLECT(w.name) AS writers
        ORDER BY similarity DESC
        LIMIT 3;
        """,
        parameters={"query_vector": query_vector},
    )
    return res.get_as_pl()


if __name__ == "__main__":
    # Initialize the database and OpenAI client
    conn = init_database()
    openai_client = init_openai()
    base_path = "./data"

    # Create the graph schema
    create_tables(conn)

    # Ingest the data
    ingest_data(conn, base_path)

    # Add embeddings to the movies
    add_movie_embeddings(conn, base_path, openai_client)

    # Query the movie cast
    query_movie_cast(conn)

    # Query for movies similar to a given query
    query_item = "space opera"
    result = similarity_search(conn, query_item, openai_client)
    print(f"---\nMovies that are closest to the query '{query_item}':\n{result}")
