import cherrypy
import sqlite3
import os
import html


def init_table(thread_index):
    # Connect to the database and save it in cherrypy.thread_data
    # so we can access it later:
    cherrypy.thread_data.conn = sqlite3.connect("data.db")
    # Get the cursor:
    cur = cherrypy.thread_data.conn.cursor()
    # Create the books table:
    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id integer primary key,
        title text,
        author_first_name text,
        author_last_name text
    )
    """)
    # Create the user table:
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id integer primary key,
        username text unique,
        nickname text
    )
    """)
    # Create the relation:
    cur.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        book_id integer references books on delete cascade,
        user_id integer references users on delete cascade,
        unique(book_id, user_id)
    )
    """)
    # Make sure that referential integrity is kept:
    cur.execute("pragma foreign_keys = 1")
    # Save changes:
    cherrypy.thread_data.conn.commit()
    # Close cursor:
    cur.close()


# Tell CherryPy to connect to the database for each thread:
cherrypy.engine.subscribe("start_thread", init_table)


class Root(object):
    # Just use index.html as the home page:
    @cherrypy.expose
    def index(self):
        with open("index.html", "r") as file: return file.read()

    @cherrypy.expose
    def get_books(self):
        # Get the cursor:
        cur = cherrypy.thread_data.conn.cursor()
        # Get the database entries:
        cur.execute("""
        SELECT * FROM books
        """)
        book_records = cur.fetchall()

        # This is where we will store the HTML code:
        books_html = ""
        # If there are no books, tell the user:
        if len(book_records) == 0:
            books_html = "There are no books yet. Please add a book!"
        # Otherwise, loop through the book records:
        for record in book_records:
            # From the order of the books table,
            # the id comes first:
            book_id = record[0]
            # Then the title:
            title = html.escape(record[1])
            # Then the author's first name:
            first_name = html.escape(record[2])
            # Then the author's last name:
            last_name = html.escape(record[3])
            # Make a p element containing the above information:
            books_html += "<p>" + title + " by " + first_name + " " + last_name + "</p>"

            # Now, get the likes:
            cur.execute("""
            SELECT * FROM likes WHERE book_id=?
            """, (book_id,))
            like_records = cur.fetchall()
            # If there are no like records, tell the user:
            if len(like_records) == 0:
                books_html += "<p>No one has liked the above book!</p>"
            # Otherwise, loop through the likes:
            else:
                # This is the list of users who have liked the book:
                users_lst = []
                for like in like_records:
                    # From the order in the likes table, user_id is second:
                    user_id = like[1]
                    # Get the user:
                    cur.execute("""
                    SELECT * FROM users WHERE user_id=?
                    """, (user_id,))
                    user = cur.fetchone()
                    # From the order in the users table, nickname is third.
                    nickname = html.escape(user[2])
                    # Add the nickname to the list of users:
                    users_lst.append(nickname)
                # Add a p element using users_lst:
                books_html += "<p>Users who have liked the above book: " + ", ".join(users_lst) + "</p>"

        # Finally, close the cursor and return books_html:
        cur.close()
        return books_html

    @cherrypy.expose
    def add_book(self, title, first_name, last_name):
        # Get the cursor:
        cur = cherrypy.thread_data.conn.cursor()
        # Insert the database entries:
        cur.execute("""
        INSERT INTO books (title, author_first_name, author_last_name)
        VALUES (?,?,?)
        """, (title, first_name, last_name))
        # Save changes:
        cherrypy.thread_data.conn.commit()
        # Close the cursor:
        cur.close()
        # Return an empty page:
        return ""

    @cherrypy.expose
    def add_user(self, username, nickname):
        # This is the message we will return to the user:
        message = ""

        # Get the cursor:
        cur = cherrypy.thread_data.conn.cursor()
        try:
            # Insert the database entries:
            cur.execute("""
            INSERT INTO users (username, nickname)
            VALUES (?,?)
            """, (username, nickname))
            # If we get to this point, then there was no error.
            # Therefore, save the changes:
            cherrypy.thread_data.conn.commit()
            # Tell the user changes were successfully saved:
            message = html.escape(username) + " was successfully saved!"
        except sqlite3.IntegrityError:
            # If there was an error, rollback the changes:
            cherrypy.thread_data.conn.rollback()
            # Tell the user of the error:
            message = "It looks like there is already a user with the username " + html.escape(username) + "."

        # Close the cursor:
        cur.close()
        # Return the message:
        return message

    @cherrypy.expose
    def like_book_form(self):
        # Get the HTML page:
        with open("like-book-form.html", "r") as file:
            like_book_html = file.read()
        # Get the cursor:
        cur = cherrypy.thread_data.conn.cursor()

        # This is where all of the book options will go:
        book_select_elem = """<select name="book_id">"""
        # First, add the default option:
        book_select_elem += """<option value="default">Choose Book</option>"""
        # Get all of the books:
        cur.execute("SELECT * FROM books")
        book_records = cur.fetchall()
        # For every book:
        for record in book_records:
            # According to the table, the id comes first:
            id = str(record[0])
            # Then the title:
            title = html.escape(record[1])
            # Then the author first name (record[2]) and last name (record[3]):
            author = html.escape(record[2] + " " + record[3])
            '''
            Now, add the option.
            Here, the value is the book ID, but what the user sees is the title and author.
            We set the value to the book ID so that when the user submits the form,
            we can get the book from the book ID.
            This is important just in case there are books with multiple titles,
            so we can tell the apart.
            '''
            book_select_elem += "<option value=\"" + id + "\">" + title + " by " + author + "</option>"
        # Finally, end the select element:
        book_select_elem += "</select>"

        # Now, we go through a similar for creating the user select element:
        # This is where all of the book options will go:
        user_select_elem = """<select name="user_id">"""
        # First, add the default option:
        user_select_elem += """<option value="default">Choose User</option>"""
        # Get all of the users:
        cur.execute("SELECT * FROM users")
        user_records = cur.fetchall()
        # For every user:
        for record in user_records:
            # According to the table, the id comes first:
            id = str(record[0])
            # Then the username:
            username = html.escape(record[1])
            # Now, add the option:
            user_select_elem += "<option value=\"" + id + "\">" + username + "</option>"
        # Finally, end the select element:
        user_select_elem += "</select>"

        # Finally, insert the select elements into the HTML code:
        return like_book_html.format(
            select_book=book_select_elem,
            select_user=user_select_elem
        )

    @cherrypy.expose
    def like_book(self, user_id, book_id):
        # This is the message we will return to the user:
        message = ""

        # If the user or book ID is default, tell the user:
        if user_id == "default":
            message = "It looks like you did not actually choose a user. Please select a user from the dropdown bar or, if there isn't one, add one on."
        elif book_id == "default":
            message = "It looks like you did not actually choose a book. Please select a book from the dropdown bar or, if there isn't one, add one on."
        # Otherwise, try to add the like to the database:
        else:
            # Get the cursor:
            cur = cherrypy.thread_data.conn.cursor()
            try:
                '''
                Insert the database entry.
                Remember to convert the ids to integers because
                we defined them as integers in the SQL tables.
                '''
                cur.execute("""
                INSERT INTO likes VALUES (?, ?)
                """, (int(book_id), int(user_id)))
                # If we get to this point, then there was no error.
                # Therefore, save the changes:
                cherrypy.thread_data.conn.commit()
                # Tell the user the like was successfully saved:
                message = "You successfully liked a book!"
            except sqlite3.IntegrityError:
                # If there was an error, rollback the changes:
                cherrypy.thread_data.conn.rollback()
                # Tell the user of the error:
                message = "It looks like you already liked this pair of books."
            # Close the cursor:
            cur.close()

        # Finally, return the message:
        return message


if __name__ == "__main__":
    cherrypy.quickstart(Root(), config={
        "/static": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": os.path.abspath("./static")
        }
    })