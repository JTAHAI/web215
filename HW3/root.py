import cherrypy
import json
import html

class Root (object):
    @cherrypy.expose
    def index(self):
        with open ("index.html" , "r") as file:
            index_html = file.read()
        with open ("data.json" , "r") as file:
            data = json.loads (file.read())
        user_name = data["name"]
        user_age = data["age"]
        user_bio = data["bio"]
        user_food = data["food"]
        user_local = data["local"]
        user_name = html.escape(user_name)
        user_bio = html.escape(user_bio)
        user_food = html.escape(user_food)
        user_local = html.escape(user_local)
        return index_html.format(
            username=user_name,
            age=str(user_age),
            bio=user_bio,
            food=user_food,
            local=user_local
        )


    @cherrypy.expose
    def form_action(self , name, age, bio, food, local):
        user_info = {
             "name": name,
             "age": int(age),
             "bio": bio,
             "food": food,
             "local": local
        }
        with open("data.json", "w") as file:
            file.write(json.dumps(user_info))
        with open ("form-action.html" , "r") as file:
            return file.read()

if __name__ == "__main__":
 cherrypy.quickstart( Root ())