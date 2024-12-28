# Google Books Explorer
Google Books Explorer is a Streamlit web application that integrates with the Google Books API and a MySQL database to allow users to search for, insert, view, and analyze book data. This application also provides insights into book analytics and enables users to search for books based on various criteria.

## Features
1. Insert and View Data
  Search for books using the Google Books API and insert them into the MySQL database.
  View the books stored in the database, including details such as title, author, publisher, and published date.
  
2. Data Analytics
  Run predefined SQL queries on the database to extract insights and perform analytics, such as:
    Count of eBooks vs non-eBooks.
    Publishers with the most books.
    Books with the highest retail price.
    Books with discounts greater than 20%
    Top authors by number of books  and more

3. Search a Book
  Search books stored in the database based on:
    Book title.
    Author.
    Genre or category.

## Usage
Launch the application using Streamlit.
Navigate between the sections using the sidebar:
Insert and View Data: Fetch data from the Google Books API and manage it in the database.
Data Analytics: Perform predefined SQL-based analytics.
Search a Book: Search books in the database by title, author, or category.

## SQL Queries
The app includes a variety of predefined SQL queries to analyze the book data, such as:
Finding publishers with the highest average ratings.
Listing books with more than 3 authors.
Calculating the average retail price for eBooks and physical books.
Identifying books with ratings significantly above average and more

## Database Schema
The database contains a single table Books with the following columns:
book_id: Unique identifier for the book.
search_key: Search snippet.
book_title: Title of the book.
book_subtitle: Subtitle of the book.
book_authors: Authors of the book.
book_description: Description of the book.
Publishers: Publisher of the book.
industryIdentifiers: Identifiers like ISBN.
text_readingModes: Reading modes available as text.
image_readingModes: Reading modes available as images.
pageCount: Number of pages in the book.
categories: Book categories.
language: Language of the book.
imageLinks: Thumbnail image link.
ratingsCount: Number of ratings.
averageRating: Average rating.
country: Sale country.
saleability: Sale status.
isEbook: Boolean indicating if the book is an eBook.
amount_listPrice: List price of the book.
currencyCode_listPrice: Currency code for the list price.
amount_retailPrice: Retail price of the book.
currencyCode_retailPrice: Currency code for the retail price.
buyLink: Link to buy the book.
year: Published year.


## Acknowledgments
Streamlit for the web framework.
Google Books API for book data.
MySQL for database management.
