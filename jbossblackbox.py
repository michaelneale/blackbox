import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db



class ErrorReport(db.Model):
  project = db.StringProperty(multiline=False)
  module = db.StringProperty(multiline=False)
  version = db.StringProperty(multiline=False)
  date = db.DateTimeProperty(auto_now_add=True)
  contact_name = db.StringProperty(multiline=False)
  contact_email = db.StringProperty(multiline=False)
  content = db.StringProperty(multiline=True)
    

class UsageReport(db.Model):
  project = db.StringProperty(multiline=False)
  module = db.StringProperty(multiline=False)
  version = db.StringProperty(multiline=False)
  ip = db.StringProperty(multiline=False)
  date = db.DateTimeProperty(auto_now_add=True)
  content = db.StringProperty(multiline=True)



class MainPage(webapp.RequestHandler): 
  def get(self):
    self.response.out.write('<html><body>BLACKBOX</body></html>')

class CreateErrorReport(webapp.RequestHandler):
  def post(self):
    report = ErrorReport()
    report.content = self.request.get('content')
    report.project = self.request.get('project')
    report.module = self.request.get('module')
    report.version = self.request.get('version')
    report.contact_name = self.request.get('contact_name')
    report.contact_email = self.request.get('contact_email')
    report.put()
    self.redirect('/')


class CreateUsageReport(webapp.RequestHandler):
  def post(self):
    report = UsageReport()
    report.content = self.request.get('content')
    report.project = self.request.get('project')
    report.module = self.request.get('module')
    report.version = self.request.get('version')
    report.ip = self.request.remote_addr
    report.put()
    self.redirect('/')

      

class ReportViewerCsv(webapp.RequestHandler): 
  def get(self): 
    checkAuth(self)
    reports = db.GqlQuery("SELECT * FROM ErrorReport ORDER BY date DESC LIMIT 10")
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write("Project,Module,Version,Date,Contact Name,Contact Email,Report\n")
    for report in reports:
        self.response.out.write('%s,' % report.project)
        self.response.out.write('%s,' % report.module)
        self.response.out.write('%s,' % report.version)
        self.response.out.write('"%s",' % report.date)
        self.response.out.write('%s,' % report.contact_name)
        self.response.out.write('%s,' % report.contact_email)
        self.response.out.write('"%s"\n' % report.content)


class ReportViewerXML(webapp.RequestHandler): 
  def get(self): 
    checkAuth(self)
    reports = makeQuery(self.request.get('project'), self.request.get('module'), self.request.get('version'), self.request.get('from'), self.request.get('to'))
              
    self.response.headers['Content-Type'] = 'text/xml'
    self.response.out.write("<error-reports>")
    for report in reports:
        self.response.out.write('<report>')
        self.response.out.write('<project>%s</project>' % report.project)
        self.response.out.write('<module>%s</module>' % report.module)
        self.response.out.write('<version>%s</version>' % report.version)
        self.response.out.write('<date>%s</date>' % report.date)
        self.response.out.write('<name>%s</name>' % report.contact_name)
        self.response.out.write('<email>%s</email>' % report.contact_email)
        self.response.out.write('<report><![CDATA[%s]]></report>' % report.content)
        self.response.out.write('</report>')
    self.response.out.write('</error-reports>')


def makeQuery(project, module, version, from_date, to_date):
  q = 'where project = :project'
  if (from_date):
    q = q + " and date <= DATETIME(:to_date)"
  if (to_date):
    q = q + " and date >= DATETIME(:from_date)"
  if (module):
    q = q + " and module = :module"
  if (version):
    q = q + " and version = :version"
  return  ErrorReport.gql(q, project=project, version=version, module=module, from_date=from_date, to_date=to_date)


#this is for debugging really...
class ErrorMessagesAdmin(webapp.RequestHandler):
  def get(self):
    checkAuth(self)
    self.response.out.write('<html><body>')

    reports = db.GqlQuery("SELECT * FROM ErrorReport ORDER BY date DESC LIMIT 10")

    for report in reports:
        self.response.out.write('Project : <b>%s</b><br/>' % report.project)
        self.response.out.write('Module : <b>%s</b><br/>' % report.module)
        self.response.out.write('Version : <b>%s</b><br/>' % report.version)
        self.response.out.write('Date : <b>%s</b><br/>' % report.date)
        self.response.out.write('Contact Name : <b>%s</b><br/>' % report.contact_name)
        self.response.out.write('Contact Email : <b>%s</b><br/>' % report.contact_email)
        self.response.out.write('Report : <blockquote>%s</blockquote><br/>' % cgi.escape(report.content))

    # Write the submission form and the footer of the page
    self.response.out.write("""
          <form action="/create_error" method="post">
            <div>Project: <input type="text" name="project" /></div>
            <div>Module: <input type="text" name="module" /></div>
            <div>Version: <input type="text" name="version" /></div>
            <div>Contact name: <input type="text" name="contact_name" /></div>
            <div>Contact email: <input type="text" name="contact_email" /></div>
            <div>Report: <textarea name="content" rows="3" cols="60"></textarea></div>
            <div><input type="submit" value="Create report"></div>
          </form>
        </body>
      </html>""")

  
  


def checkAuth(self): 
  user = users.get_current_user()
  if not user:
    self.redirect(users.create_login_url(self.request.uri))
    

  


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/errors/csv', ReportViewerCsv), 
                                      ('/errors/xml', ReportViewerXML), 
                                      ('/create_error', CreateErrorReport),
                                      ('/error_admin', ErrorMessagesAdmin),
                                      ('/create_usage', CreateUsageReport) 
                                      ],
                                      debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()





