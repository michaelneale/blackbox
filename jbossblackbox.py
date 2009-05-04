import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db



class Report(db.Model):
  project = db.StringProperty(multiline=False)
  application = db.StringProperty(multiline=False)
  version = db.StringProperty(multiline=False)
  date = db.DateTimeProperty(auto_now_add=True)
  content = db.StringProperty(multiline=True)


class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>')

    reports = db.GqlQuery("SELECT * FROM Report ORDER BY date DESC LIMIT 10")

    for report in reports:
        self.response.out.write('Project : <b>%s</b><br/>' % report.project)
        self.response.out.write('Date : <b>%s</b><br/>' % report.date)
        self.response.out.write('Report : <blockquote>%s</blockquote><br/>' %
                              cgi.escape(report.content))
        self.response.out.write("Path : <i>%s</i><br/>" % self.request.path)

    # Write the submission form and the footer of the page
    self.response.out.write("""
          <form action="/manual" method="post">
            <div><input type="text" name="project" /></div>
            <div><textarea name="content" rows="3" cols="60"></textarea></div>
            <div><input type="submit" value="Create report"></div>
          </form>
        </body>
      </html>""")

class ManualCreate(webapp.RequestHandler):
  def post(self):
    report = Report()

    report.content = self.request.get('content')
    report.project = self.request.get('project')
    report.put()
    self.redirect('/')

class AgentCreate(webapp.RequestHandler): 
  def post(self):



application = webapp.WSGIApplication(
                                     [('/list', MainPage),
                                      ('/manual', ManualCreate)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
