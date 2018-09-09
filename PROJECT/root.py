import cherrypy
import sqlite3
import os
import html

def init_table(thread_index):
    cherrypy.thread_data.conn = sqlite3.connect("data.db")
    cur = cherrypy.thread_data.conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        comment_id integer PRIMARY KEY, 
        name text,
        comment text
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id integer primary key,
        username text unique,
        nickname text
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        comment_id integer references comments on delete cascade,
        user_id integer references users on delete cascade,
        unique(comment_id, user_id)
    )
    """)
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
        SELECT * FROM comments
        """)
        comments_records = cur.fetchall()

        comments_html = ""
        if len(comments_records) == 0:
            comments_html = "There are no comments yet."
        for record in comments_records:
            comment_id = record[0]
            name = html.escape(record[1])
            comment = html.escape(record[2])
            comments_html += "<p>"+name+"'s comment: "+comment+"</p>"

        cur.execute("""
        SELECT * FROM likes WHERE comment_id=?
        """, (comment_id,))
        like_records = cur.fetchall()
        if len(like_records) == 0:
            comments_html += "<p>No one has liked the above comment!</p>"
        else:
            users_lst = []
            for like in like_records:
                user_id = like[1]
                cur.execute("""
                SELECT * FROM users WHERE user_id=?
                """, (user_id,))
                user = cur.fetchone()
                nickname = html.escape(user[2])
                users_lst.append(nickname)
            comments_html += "<p>Users who have liked the above comment: " + ", ".join(users_lst) + "</p>"
        comments_html += """You can edit or delete the above comment <a href="/edit-comment-form?comment_id="""+str(comment_id) + """">here</a>."""

        cur.close()
        return comments_html


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
        INSERT INTO comments (name, comment)
        VALUES (?,?)
        """, (name, comment))
        cherrypy.thread_data.conn.commit()
        cur.close()
        return ""


    @cherrypy.expose
    def add_user(self, username, nickname):
        message = ""

        cur = cherrypy.thread_data.conn.cursor()
        try:
            cur.execute("""
            INSERT INTO users (username, nickname)
            VALUES (?,?)
            """, (username, nickname))
            cherrypy.thread_data.conn.commit()
            message = html.escape(username) + " was successfully saved!"
        except sqlite3.IntegrityError:
            cherrypy.thread_data.conn.rollback()
            message = "It looks like there is already a user with the username " + html.escape(username) + "."

        cur.close()
        return message


    @cherrypy.expose
    def like_comment_form(self):
        with open("like-comment-form.html", "r") as file:
            like_comment_html = file.read()
            
        cur = cherrypy.thread_data.conn.cursor()

        comment_select_elem = """<select name="comment_id">"""
        comment_select_elem += """<option value="default">Choose Comment</option>"""
        cur.execute("SELECT * FROM comments")
        comments_records = cur.fetchall()
        for record in comments_records:
            id = str(record[0])
            name = html.escape(record[1])
            comment = html.escape(record[1] + " " + record[2])

            comment_select_elem += "<option value=\""+id+"\">"+name+" by "+comment+"</option>"
        comment_select_elem += "</select>"


        user_select_elem = """<select name="user_id">"""
        user_select_elem += """<option value="default">Choose User</option>"""
        cur.execute("SELECT * FROM users")
        user_records = cur.fetchall()
        for record in user_records:
            user_id = str(record[0])
            username = html.escape(record[1])
        user_select_elem += "<option value=\""+user_id+"\">"+username+"</option>"
        user_select_elem += "</select>"

        return like_comment_html.format(
            select_comment=comment_select_elem,
            select_user=user_select_elem
        )


    @cherrypy.expose
    def like_comment(self, user_id, comment_id):
        message = ""

        if user_id == "default":
            message = "It looks like you did not actually choose a user. Please select a user from the dropdown bar or, if there isn't one, add one on."
        elif comment_id == "default":
            message = "It looks like you did not actually choose a comment. Please select a comment from the dropdown bar or, if there isn't one, add one on."
        else:
            cur = cherrypy.thread_data.conn.cursor()
            try:
                cur.execute("""
                INSERT INTO likes VALUES (?, ?)
                """, (int(comment_id), int(user_id)))
                cherrypy.thread_data.conn.commit()
                message = "You successfully liked a comment!"
            except sqlite3.IntegrityError:
                cherrypy.thread_data.conn.rollback()
                message = "It looks like you already liked comment."
            cur.close()

        return message


    @cherrypy.expose
    def edit_comment_form(self, comment_id):
        with open("edit-comment-form.html", "r") as file:
            edit_comment_form_html = file.read()

        cur = cherrypy.thread_data.conn.cursor()
        cur.execute("""
        SELECT * FROM comments
        WHERE comment_id=?
        """, (int(comment_id),))
        comments_record = cur.fetchone()
        name = html.escape(comments_record[1])
        comment = html.escape(comments_record[2])
        cur.close()

        return edit_comment_form_html.format(
            comment_id=comment_id,
            name=name,
            comment=comment
        )


    @cherrypy.expose
    def edit_comment(self, comment_id, name, comment):
        if len(name) == 0:
            return "There is no new name."
        if len(name) > 50:
            return "The new name is over 50 characters."
        if len(comment) == 0:
            return "There is no new comment."
        if len(comment) > 1000:
            return "The new comment is over 1000 characters."


        cur = cherrypy.thread_data.conn.cursor()
        cur.execute("""
        UPDATE comments
        SET name=?, comment=?
        WHERE comment_id=?
        """, (name, comment, int(comment_id)))
        cherrypy.thread_data.conn.commit()
        cur.close()
        return "The comment has been updated successfully!"


    @cherrypy.expose
    def delete_comment(self, comment_id):
        cur = cherrypy.thread_data.conn.cursor()
        cur.execute("""
        DELETE FROM comments
        WHERE comment_id=?
        """, (int(comment_id),))
        cherrypy.thread_data.conn.commit()
        cur.close()

        raise cherrypy.HTTPRedirect("/")

if __name__ == "__main__":
    cherrypy.quickstart(root(), config={
        "/static": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": os.path.abspath("./static")
        },

        "/": {
            "log.access_file" : "access.log",
            "log.error_file": "error.log"
        }
    })
