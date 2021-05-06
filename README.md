# Project 1

## Web Programming with Python(Flask) and JavaScript

A webpage demonstrating concepts discussed in week 1 of CS50 Web

## Files

* templates/book.html - html page for when a book is selected from books.html. Details about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book. Displays user's personal review of the book, or allows him/her to leave a review and rating if not yet reviewed.
* templates/books.html - Display a list of possible matching results from search query on search.html. Displays partial matches from title, ISBN number and author
* templates/index.html - Landing page
* templates/layout.html - Template with navbar, footer, alerts and allocated space for rest of the pages
* templates/login.html - Login page. Allows users to log in to site when a valid username and matching password is entered. Shows alert message if username or password is invalid
* templates/register - Allows user to register with a username and password. Stores credentials in database
* templates/search - Allows user to search for ISBN number, title or author. Handles partial matches

* static/cover_not_found.jpg default image for when a book cover image couldn't be found

* static/styles.css - stylesheet

* import.py - creates, if non-existing, the users, reviews and books tables on a Heroku postgres database. Reads the entries from books.csv and inserts them into the books table.
* application.py - Various endpoints for the different webpage functions. Handles database queries to and from the Heroku database. Does an API request to Goodreads for ratings data. Provides API access to a book's information by using it's ISBN number as a request.

Online link: https://crooks-books.herokuapp.com
