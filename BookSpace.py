import requests
import streamlit as st
import mysql.connector
from streamlit_option_menu import option_menu


QUERIES = {
    "Ebook vs Non-Ebook": "SELECT isEbook, COUNT(book_title) AS book_count FROM Books GROUP BY isEbook;",
    "Publisher with Most books": 'SELECT Publishers, COUNT(book_title) AS total_books FROM Books WHERE Publishers != "N/A" GROUP BY Publishers ORDER BY total_books DESC LIMIT 1;',
    "Publisher with Highest Avarage Rating": "SELECT Publishers, MAX(averageRating) AS Average_Rating FROM Books WHERE Publishers != 'N/A' GROUP BY Publishers ORDER BY Average_Rating DESC LIMIT 10;",
    "Top 5 books with highest Retail Price":"SELECT book_title, amount_retailPrice FROM Books ORDER BY amount_retailPrice DESC LIMIT 5;",
    "Books published in 2010 with more than 500 pages":"SELECT book_title, year AS PublishedYear, pageCount AS PageCount FROM Books WHERE pageCount>500 AND year LIKE '2010%';",
    "List Books with Discounts Greater than 20%":"SELECT book_title, amount_listPrice AS Original_Price, amount_retailPrice as Discounted_Price FROM Books WHERE ((amount_listPrice - amount_retailPrice)/ amount_listPrice * 100) > 20;",
    "Average Page Count for eBooks vs Physical Books":"SELECT isEbook, AVG(pageCount) AS book_count FROM Books GROUP BY isEbook;",
    "Top 3 Authors with the Most Books":"SELECT book_authors, COUNT(book_title) as Total_Books FROM Books WHERE book_authors != 'N/A' GROUP BY book_authors ORDER BY Total_Books desc Limit 3;",
    "Publishers with More than 10 Books":"SELECT Publishers AS Publisher, COUNT(book_title) AS Total_Books FROM Books WHERE Publishers != 'N/A' GROUP BY Publishers HAVING COUNT(book_title) >10 ORDER BY Total_Books desc;",
    "Average Page Count for Each Category":"SELECT categories, AVG(pageCount) AS Avg_Page_Count FROM Books  WHERE categories != 'N/A' GROUP BY categories ORDER BY Avg_Page_Count desc;",
    "Retrieve Books with More than 3 Authors":"SELECT book_title AS Book_Name, COUNT(DISTINCT book_authors) AS Author_Count FROM Books GROUP BY book_title HAVING COUNT(DISTINCT book_authors) > 3;",
    "Books with Ratings Count Greater Than the Average":"SELECT book_title AS Book_Name, ratingsCount AS Rating_Count, averageRating AS Average_Rating FROM Books WHERE ratingsCount > averageRating;",
    "Books with the Same Author Published in the Same Year":"SELECT book_authors AS Author_Count, (year) as Published_Year, COUNT(book_title) AS Total_Books FROM Books bd1 WHERE book_authors!= 'N/A'  or  (year) != NULL GROUP BY book_authors, year HAVING COUNT(book_title) > 1;",
    "Books with a Specific Keyword in the Title":"SELECT book_title AS Title, book_authors AS Author, year AS Published_Year FROM Books WHERE book_title LIKE '%Museum%';",
    "Year with the Highest Average Book Price":"SELECT YEAR(year) as Published_Year, AVG(amount_listPrice) as Average_Books_Price FROM Books GROUP BY year HAVING AVG(amount_listPrice) ORDER BY Published_Year desc;",
    "Count Authors Who Published 3 Consecutive Years":"SELECT COUNT(DISTINCT book_authors) AS Author_Count FROM Books bd1 WHERE EXISTS (SELECT 1 FROM Books AS bd2 WHERE bd2.book_authors = bd1.book_authors AND bd2.year = bd1.year + 1) AND EXISTS (SELECT 1 FROM Books AS bd3 WHERE bd3.book_authors = bd1.book_authors AND bd3.year = bd1.year + 2);",
    "Same Author with Different Publishers in Same Year":"SELECT book_authors AS Book_Authors, year AS Published_Year, COUNT(DISTINCT Publishers) AS Publisher_Count, COUNT(book_title) AS Total_Books FROM Books WHERE book_authors != 'N/A' GROUP BY book_authors, year HAVING  COUNT(DISTINCT Publishers) > 1;",
    "Average amount_retailPrice of eBooks and physical books":"SELECT (AVG(CASE WHEN isEbook = 1 THEN amount_retailPrice END)) AS Avg_Ebook_Price, (AVG(CASE WHEN isEbook = 0 THEN amount_retailPrice END)) AS Avg_Physical_Price FROM Books;",
    "Books with ratings 2 deviations from average":"SELECT book_title AS Title, averageRating AS Average_Rating, ratingsCount as Rating_Count FROM Books WHERE ABS(averageRating - (SELECT AVG(averageRating) FROM Books)) > 2 * (SELECT STDDEV(averageRating) FROM Books);",
    "Publisher with highest average rating, over 10 books":"SELECT Publishers AS Publisher, AVG(averageRating) AS Average_Rating, COUNT(book_title) as Total_Books FROM Books GROUP BY Publishers HAVING COUNT(book_title) > 10 ORDER BY Average_Rating DESC LIMIT 1;"
}


def create_mysql_connection():
  connection = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    port=4000,
    user="3tN77YkdrSS9WKK.root",
    password="Eufk68BdWytW0E6w",
    database = "Books",
    ssl_ca = "C:/isrgrootx1.pem",
    ssl_verify_cert=True
  )
  return connection

def view_data(conn, q):
    cursor = conn.cursor()
    search_query = "SELECT * FROM books WHERE title LIKE %s"
    cursor.execute(search_query, ('%' + q + '%',))
    results = cursor.fetchall()
    return results

def insert_into_mysql(conn, books):
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO books (
                book_id,search_key,book_title,book_subtitle,book_authors,book_description,Publishers,industryIdentifiers,
                text_readingModes,image_readingModes,pageCount,categories,language,imageLinks,ratingsCount,averageRating,
                country,saleability,isEbook,amount_listPrice,currencyCode_listPrice,amount_retailPrice, currencyCode_retailPrice,
                buyLink, year
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
   
    inserted_count = 0
    try:
        for book in books:
            cursor.execute("SELECT book_id FROM books WHERE book_id = %s", (book[0],))
            existing = cursor.fetchone()
            
            if existing:
                pass
            else:
                cursor.execute(insert_query, book)
                conn.commit()
                inserted_count += 1
                st.write(f"Inserted book with ID: {book[0]}")
               
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    
    return inserted_count
def fetch_books_and_format_data(params):
    response = requests.get(base_url, params)
    if response.status_code == 200:
        data = response.json()
        books = []
        for item in data.get("items", []):
            book = (
                item.get("id"),
                item.get("searchInfo", {}).get("textSnippet", ""),
                item.get("volumeInfo", {}).get("title", ""),
                item.get("volumeInfo", {}).get("subtitle", None),
                ", ".join(item.get("volumeInfo", {}).get("authors", [])),
                item.get("volumeInfo", {}).get("description", ""),
                item.get("volumeInfo", {}).get("Publishers", ""),
                ", ".join([f"{id['type']}: {id['identifier']}" for id in item.get("volumeInfo", {}).get("industryIdentifiers", [])]),
                None if item.get("volumeInfo", {}).get("readingModes", {}).get("text") == "N/A" else int(item.get("volumeInfo", {}).get("readingModes", {}).get("text", 0)),
                None if item.get("volumeInfo", {}).get("readingModes", {}).get("image") == "N/A" else int(item.get("volumeInfo", {}).get("readingModes", {}).get("image", 0)),
                item.get("volumeInfo", {}).get("pageCount"),
                ", ".join(item.get("volumeInfo", {}).get("categories", [])),
                item.get("volumeInfo", {}).get("language", ""),
                item.get("volumeInfo", {}).get("imageLinks", {}).get("thumbnail", ""),
                item.get("volumeInfo", {}).get("ratingsCount"),
                item.get("volumeInfo", {}).get("averageRating"),
                item.get("saleInfo", {}).get("country", ""),
                item.get("saleInfo", {}).get("saleability", ""),
                None if item.get("saleInfo", {}).get("isEbook") == "N/A" else int(item.get("saleInfo", {}).get("isEbook")),
                item.get("saleInfo", {}).get("listPrice", {}).get("amount"),
                item.get("saleInfo", {}).get("listPrice", {}).get("currencyCode", ""),
                item.get("saleInfo", {}).get("retailPrice", {}).get("amount"),
                item.get("saleInfo", {}).get("retailPrice", {}).get("currencyCode", ""),
                item.get("saleInfo", {}).get("buyLink", ""),
                item.get("volumeInfo", {}).get("publishedDate", "")
            )
            books.append(book)
        return books
    else:
        st.error("Failed to fetch data from Google Books API")
        return []

def data_analytics(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    if query.strip().lower().startswith("select"):
        results = cursor.fetchall()
        return results, cursor.column_names
    else:
        conn.commit()
        return "Query executed successfully!", None

def get_books(conn,search_title=None, search_author=None, search_category=None):
    cursor = conn.cursor()
    query = "SELECT book_id, book_title, book_authors, categories, year FROM Books WHERE 1=1"
    if search_title:
        query += f" AND book_title LIKE '%{search_title}%'"
    if search_author:
        query += f" AND book_authors LIKE '%{search_author}%'"
    if search_category:
        query += f" AND categories LIKE '%{search_category}%'"
    cursor.execute(query)
    results = cursor.fetchall()
    return results

def main():
    with st.sidebar:
        selected = option_menu(
            menu_title = "Main Menu",
            options = ["Insert and View Data", "Data Analytics", "Search a Book"]
            )
    if selected == "Insert and View Data":    
        st.title("Google Books Explorer")

        conn = create_mysql_connection()
        book_to_insert =st.text_input("Search for books")
        books_per_batch = 40
        maximum_records = st.number_input("Search for Number of Books", min_value=0, max_value=1000)
        left, middle, right = st.columns(3)
        if left.button("Insert into Database"):
            params = {
                "key": api_key,
                "q": book_to_insert,
                "startIndex": 0,
                "maxResults": books_per_batch
            }
            while params["startIndex"] < maximum_records:
                remaining_records = maximum_records - params["startIndex"]
                params["maxResults"] = min(books_per_batch, remaining_records)
                books = fetch_books_and_format_data(params)
                if books:
                    insert_into_mysql(conn, books)
                params["startIndex"] += params["maxResults"]
                
        
        if right.button("Show Books in Database"):
            cursor = conn.cursor()
            cursor.execute("SELECT book_title, book_authors, Publishers, year FROM books")
            rows = cursor.fetchall()
            for row in rows:
                st.write(f"**Title:** {row[0]}")
                st.write(f"**Authors:** {row[1]}")
                st.write(f"**Publisher:** {row[2]}")
                st.write(f"**Published Date:** {row[3]}")
                st.markdown("---")

    if selected == "Data Analytics":
        st.title("Data Analytics")
        conn = create_mysql_connection()
        query_name = st.selectbox("Select a Query", list(QUERIES.keys()))
        query = QUERIES[query_name]
        result, columns = data_analytics(conn, query)
        if isinstance(result, str): 
            st.sidebar.success(result)
        else:
            st.write(f"Results for: **{query_name}**")
            if result:
                table_data = [dict(zip(columns, row)) for row in result]
                st.table(table_data)  
            else:
                st.write("No results found.")

    if selected == "Search a Book":
        st.title("Search a Book")
        conn = create_mysql_connection()
        search_title = st.text_input("Search by Book Title")
        search_author = st.text_input("Search by Author")
        search_category = st.selectbox("Search by Genre", ["","Fiction", "Historical fiction", "Business & Economics", "Creation (Literary, artistic, etc.)",
                                                "Biography & Autobiography", "Literary Collections", "Sports & Recreation", "Imaginary histories", "English poetry", "World War",
                                                "Language Arts & Disciplines", "Political Science", "Dystopias", "Dyslexia", "Literary Criticism", "N/A"])
        books_data = get_books(conn, search_title, search_author, search_category)
        if books_data:
            st.write("### List of Books:")
            st.write("This list displays all the books matching your search criteria.")

            book_columns={
                0 : "ID",
                1 : "Title",
                2 : "Author",
                3 : "Category",
                4 : "Year Published"
            }
        
            st.table(books_data)
        else:
            st.write("No books found based on your search criteria.")

        conn.close()
if __name__ == "__main__":
    api_key = "AIzaSyCOkkQNIO5W68THYDnjhSqeNQ3zkxEOeqI"
    base_url = "https://www.googleapis.com/books/v1/volumes"
    main()
    