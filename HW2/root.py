import os
import cherrypy


class Root(object):
    #visit counter
    num_visits = 0

    @cherrypy.expose
    def index(self):
        #get code from HTML file and increment visit counter
        with open("./index.html", "r") as file:
            index_html = file.read()
            self.num_visits += 1
            if self.num_visits >= 1:
                 sentence = "This page has been visited "+str(self.num_visits)+" times."
            else:
                 sentence = "This page has been visited 1 time."
            #insert visit count into HTML
            return index_html.format(num_visits=sentence)

    @cherrypy.expose
    def more(self):
        with open("more.html", "r") as file:
            cherrypy.log("Visitor Log Entry")
        return "Your visit has been logged."
        return file.read()

if __name__ == '__main__':    
     cherrypy.quickstart(Root(), config={
        #static
         "/static": {
             "tools.staticdir.on": True,
             "tools.staticdir.dir": os.path.abspath("./static")
 },
        # logging
        "/": {
        "log.access_file" : "access.log",
        "log.error_file": "error.log"
        }

         })
