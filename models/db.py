# -*- coding: utf-8 -*-
isMigrate = True
# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.15.5":
    raise HTTP(500, "Requires web2py 2.15.5 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(configuration.get('db.uri'),
             pool_size=configuration.get('db.pool_size'),
             migrate_enabled=configuration.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = [] 
if request.is_local and not configuration.get('app.production'):
    response.generic_patterns.append('*')

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = 'bootstrap4_inline'
response.form_label_separator = ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=configuration.get('host.names'))

# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------
auth.settings.extra_fields['auth_user'] = []
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else configuration.get('smtp.server')
mail.settings.sender = configuration.get('smtp.sender')
mail.settings.login = configuration.get('smtp.login')
mail.settings.tls = configuration.get('smtp.tls') or False
mail.settings.ssl = configuration.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------  
# read more at http://dev.w3.org/html5/markup/meta.name.html               
# -------------------------------------------------------------------------
response.meta.author = configuration.get('app.author')
response.meta.description = configuration.get('app.description')
response.meta.keywords = configuration.get('app.keywords')
response.meta.generator = configuration.get('app.generator')
response.show_toolbar = configuration.get('app.toolbar')

# -------------------------------------------------------------------------
# your http://google.com/analytics id                                      
# -------------------------------------------------------------------------
response.google_analytics_id = configuration.get('google.analytics_id')

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
if configuration.get('scheduler.enabled'):
    from gluon.scheduler import Scheduler
    scheduler = Scheduler(db, heartbeat=configuration.get('scheduler.heartbeat'))

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
## ============================================================= ##
## ====== ====== ## ## ====== inddpdf ====== ## ## ====== ====== ##
## ============================================================= ##
def my_string_widget(field, value):
    return INPUT(_name=field.name,
                 _id="%s_%s" % (field._tablename, field.name),
                 _class=field.type,
                 _value=value,
                 # _style='color:blue',
                 requires=field.requires)

db.define_table('exportlist',
    Field('filepath', requires=IS_NOT_EMPTY(), widget=my_string_widget),
    Field('pdfpreset', requires=IS_IN_SET(['pdf_150ppi','pdf_150ppi_single','Toppan_pdf_31Dec2012']), widget=my_string_widget),
    Field('pagerange', requires=IS_NOT_EMPTY(), widget=my_string_widget),
    Field('createdate', 'datetime', default=request.now, writable=False, readable=False),
    Field('status',default='Idle', requires=IS_IN_SET(['Idle','Processing','Finish','Error']), widget=SQLFORM.widgets.radio.widget),
    Field('errormessage', widget=my_string_widget),
    Field('folderpath', requires=IS_NOT_EMPTY(), widget=my_string_widget),
    Field('filename', requires=IS_NOT_EMPTY(), widget=my_string_widget),
    Field('filepath_copy', requires=IS_NOT_EMPTY(), widget=my_string_widget),
    Field('exectime', 'integer', writable=False, readable=True ),
    Field('mdate', 'datetime', writable=False, readable=False),
    Field('inddname',writable=False, readable=False),
    migrate=isMigrate
    )

db.define_table('onidle',
    Field('name', requires=IS_NOT_EMPTY()),
    Field('status', requires=IS_NOT_EMPTY()),
    Field('createdate', 'datetime', default=request.now, writable=False, readable=False),
    migrate=isMigrate
    )


## ============================================================= ##
## ====== ====== ## ## ====== inddjpg ====== ## ## ====== ====== ##
## ============================================================= ##
db.define_table('exportjpg',
    Field('filepath', requires=IS_NOT_EMPTY(), widget=my_string_widget),
    Field('exportRangeOrAllPages', default='EXPORT_RANGE', requires=IS_IN_SET(['EXPORT_RANGE','EXPORT_ALL']), widget=SQLFORM.widgets.radio.widget),
    Field('exportingSpread','boolean', default=False),
    Field('jpegQuality', default='MEDIUM', requires=IS_IN_SET(['LOW','MEDIUM','HIGH','MAXIMUM'])),
    Field('exportResolution', 'integer', default=150, requires=IS_IN_SET([72,150,300])),
    Field('pageString'),
    Field('cdate', 'datetime', default=request.now, writable=False, readable=False),
    Field('status', default='Idle', requires=IS_IN_SET(['Idle','Processing','Finish','Error']), widget=SQLFORM.widgets.radio.widget),
    Field('errormessage', widget=my_string_widget),
    Field('folderpath', requires=IS_NOT_EMPTY(), widget=my_string_widget),
    Field('filename', requires=IS_NOT_EMPTY(), widget=my_string_widget),
    Field('filepath_copy', requires=IS_NOT_EMPTY(), widget=my_string_widget),
    Field('exectime', 'integer', writable=False, readable=True ),
    Field('mdate', 'datetime', writable=False, readable=False),
    Field('inddname',writable=False, readable=False),
    migrate=isMigrate
    )
