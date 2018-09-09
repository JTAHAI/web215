import cherrypy
import sqlite3
import os
import html

def init_table(thread_index):
    cherrypy.thread_data.conn = sqlite3.connect("data.db")
    cur = cherrypy.thread_data.conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS data (
        name text,
        comment text
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
    cherrypy.thread_data.conn.commit()
    cur.close()
cherrypy.engine.subscribe("start_thread", init_table)

class root(object):
    @cherrypy.expose
    def index(self):
        with open("index.html", "r") as file: return file.read()

    @cherrypy.expose
    def get_comments(self):
        cur = cherrypy.thread_data.conn.cursor()
        cur.execute("""
        SELECT * FROM data
        """)
        data_comments = cur.fetchall()
        cur.close()

        data_html = ""
        if len(data_comments) == 0:
            data_html = "There are no comments yet."
        for record in data_comments:
            name = html.escape(record[0])
            comment = html.escape(record[1])
            data_html += "<p>"+name+"'s comment: "+comment+"</p>"

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
        # Add a link to /edit-books-form:
        books_html += """You can edit or delete the above book <a href="/edit-book-form?book_id=""" + str(
            book_id) + """">here</a>."""

        # Finally, close the cursor and return books_html:

    cur.close()
    return data_html


@cherrypy.expose
    def add_comment(self, name, comment):
        if len(name) == 0:
            return "You did not enter a name."
        if len(name) > 50:
            return "Your name is more than 50 characters.  Please enter a shorter name."
        if len(comment) == 0:
            return "You did not enter a comment."
        if len(comment) > 1000:
            return "Your comment is more than 1000 characters.  Please enter a shorter comment."
        cur = cherrypy.thread_data.conn.cursor()
        cur.execute("""
        INSERT INTO data VALUES (?,?)
        """, (name, comment))
        data_comments = cur.fetchall()
        cherrypy.thread_data.conn.commit()
        cur.close()
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


@cherrypy.expose
def edit_book_form(self, book_id):
    # Get the HTML page
    with open("edit-book-form.html", "r") as file:
        edit_book_form_html = file.read()

    # Get the cursor:
    cur = cherrypy.thread_data.conn.cursor()
    # Get the record for this book_id:
    cur.execute("""
        SELECT * FROM books
        WHERE book_id=?
        """, (int(book_id),))
    book_record = cur.fetchone()
    # From this record, get the title, first_name, and last_name:
    title = html.escape(book_record[1])
    first_name = html.escape(book_record[2])
    last_name = html.escape(book_record[3])
    # Close the cursor:
    cur.close()

    # Finally, replace {book_id}, {book_title},
    # {author_first_name}, and {author_last_name}
    # with the appropriate information:
    return edit_book_form_html.format(
        book_id=book_id,
        book_title=title,
        author_first_name=first_name,
        author_last_name=last_name
    )


@cherrypy.expose
def edit_book(self, book_id, title, first_name, last_name):
    # If the title is empty or too long, tell the user:
    if len(title) == 0:
        return "There is no new title."
    if len(title) > 50:
        return "The new title is over 50 characters."
    # Do the same for first name and last name:
    if len(first_name) == 0:
        return "There is no new author's first name."
    if len(first_name) > 50:
        return "The new author's first name is over 50 characters."
    if len(last_name) == 0:
        return "There is no new author's last name."
    if len(last_name) > 50:
        return "The new author's last name is over 50 characters."

    # Get the cursor:
    cur = cherrypy.thread_data.conn.cursor()
    # Execute the UPDATE:
    cur.execute("""
        UPDATE books
        SET title=?, author_first_name=?, author_last_name=?
        WHERE book_id=?
        """, (title, first_name, last_name, int(book_id)))
    # Commit changes:
    cherrypy.thread_data.conn.commit()
    # Close the cursor:
    cur.close()
    # Tell the user the book has been updated successfully:
    return "The book has been updated successfully!"


@cherrypy.expose
def delete_book(self, book_id):
    # Get the cursor:
    cur = cherrypy.thread_data.conn.cursor()
    # Execute the DELETE:
    cur.execute("""
        DELETE FROM books
        WHERE book_id=?
        """, (int(book_id),))
    # Commit changes:
    cherrypy.thread_data.conn.commit()
    # Close the cursor:
    cur.close()

    '''
    Whenever you want to redirect to a different page,
    raise an error using cherrypy.HTTPRedirect().
    Here, we are going to use it to redirect back to the home page:
    '''
    raise cherrypy.HTTPRedirect("/")
if __name__ == "__main__":
    cherrypy.quickstart(root(), config={
                        "/static": {
                        "tools.staticdir.on": True,
                        "tools.staticdir.dir": os.path.abspath("./static")
                        }
    })
