import cgi
import logging

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db



class StartupReport(db.Model):
  project = db.StringProperty(multiline=False)
  module = db.StringProperty(multiline=False)
  version = db.StringProperty(multiline=False)
  date = db.DateTimeProperty(auto_now_add=True)
  ip = db.StringProperty(multiline=False)

class ErrorReport(db.Model):
  project = db.StringProperty(multiline=False)
  module = db.StringProperty(multiline=False)
  version = db.StringProperty(multiline=False)
  date = db.DateTimeProperty(auto_now_add=True)
  contact_name = db.StringProperty(multiline=False)
  contact_email = db.StringProperty(multiline=False)
  content = db.TextProperty()

class UsageReport(db.Model):
  project = db.StringProperty(multiline=False)
  module = db.StringProperty(multiline=False)
  version = db.StringProperty(multiline=False)
  date = db.DateTimeProperty(auto_now_add=True)
  content = db.TextProperty()


class MainPage(webapp.RequestHandler): 
  def get(self):
    self.response.out.write('<html><body>BLACKBOX</body></html>')

class CreateErrorReport(webapp.RequestHandler):
  def post(self):
    report = ErrorReport()
    report.project = self.request.get('project')
    report.module = self.request.get('module')
    report.version = self.request.get('version')
    report.contact_name = self.request.get('contact_name')
    report.contact_email = self.request.get('contact_email')
    report.content = self.request.body
    report.put()
    self.redirect('/')


class CreateUsageReport(webapp.RequestHandler):
  def post(self):
    report = UsageReport()
    report.content = self.request.body
    report.project = self.request.get('project')
    report.module = self.request.get('module')
    report.version = self.request.get('version')
    report.put()
    self.redirect('/')


class CreateStartupReport(webapp.RequestHandler):
  def post(self):
    report = StartupReport()
    report.project = self.request.get('project')
    report.module = self.request.get('module')
    report.version = self.request.get('version')
    report.ip = self.request.remote_addr
    report.put()
    self.redirect('/')


      

class ReportViewerCsv(webapp.RequestHandler): 
  def get(self): 
    checkAuth(self)
    reports = makeQuery("ErrorReport", self.request.get('project'), self.request.get('module'), self.request.get('version'), self.request.get('from'), self.request.get('to'))              
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
    reports = makeQuery("ErrorReport", self.request.get('project'), self.request.get('module'), self.request.get('version'), self.request.get('from'), self.request.get('to'))              
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

class UsageViewerXML(webapp.RequestHandler): 
  def get(self): 
    checkAuth(self)
    reports = makeQuery("UsageReport", self.request.get('project'), self.request.get('module'), self.request.get('version'), self.request.get('from'), self.request.get('to'))              
    self.response.headers['Content-Type'] = 'text/xml'
    self.response.out.write("<usage-reports>")
    for report in reports:
        self.response.out.write('<report>')
        self.response.out.write('<project>%s</project>' % report.project)
        self.response.out.write('<module>%s</module>' % report.module)
        self.response.out.write('<version>%s</version>' % report.version)
        self.response.out.write('<date>%s</date>' % report.date)
        self.response.out.write('<ip>%s</ip>' % report.ip)
        self.response.out.write('<report><![CDATA[%s]]></report>' % report.content)
        self.response.out.write('</report>')
    self.response.out.write('</usage-reports>')


def makeQuery(entity, project, module, version, from_date, to_date):
  if not project:
    return db.GqlQuery("select * from " + entity + " order by date DESC LIMIT 100")
  q = 'select * from ' + entity + ' where project = :project'
  if (from_date):
    q = q + " and date <= DATETIME(:to_date)"
  if (to_date):
    q = q + " and date >= DATETIME(:from_date)"
  if (module):
    q = q + " and module = :module"
  if (version):
    q = q + " and version = :version"
  return  db.GqlQuery(q, project=project, version=version, module=module, from_date=from_date, to_date=to_date)

  
  


def checkAuth(self): 
  user = users.get_current_user()
  if not user:
    self.redirect(users.create_login_url(self.request.uri))
    

  


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/errors/csv', ReportViewerCsv), 
                                      ('/errors/xml', ReportViewerXML), 
                                      ('/usage/xml', UsageViewerXML), 
                                      ('/create_error', CreateErrorReport),
                                      ('/create_usage', CreateUsageReport)
                                      ],
                                      debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()





