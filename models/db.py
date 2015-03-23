# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables

## configure email
from gluon.tools import Mail
mail=Mail()
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'samfisher2394@gmail.com'
mail.settings.login = 'samfisher2394:ani231994'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
##from gluon.contrib.login_methods.rpx_account import use_janrain
##use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
##auth = Auth(db)

import datetime

db1=DAL("sqlite://db.db")
db1.define_table('message',
   Field('your_name',requires=IS_NOT_EMPTY()),
   Field('your_email',requires=IS_EMAIL()),
   Field('your_message','text'),
   Field('timestamp',default=str(datetime.datetime.now())))


db.define_table(auth.settings.table_user_name,
	Field('first_name', length=128, default=''),
	Field('last_name', length=128, default=''),
	Field('email', length=128, default='', unique=True), # required
	Field('password', 'password', length=512,readable=False, label='Password'),
	Field('pic','upload',autodelete='True'),
    Field('contact','string',length=15,default='+91', unique=True),
	Field('notes','string',writable=False,readable=False,default=''),
	Field('registration_key', length=512,writable=False, readable=False, default=''),
	Field('reset_password_key', length=512,writable=False, readable=False, default=''),
	Field('registration_id', length=512,writable=False, readable=False, default=''))
## do not forget validators
db.define_table('task',
		Field('tit','string',length=128,label='Title',unique=False),
		Field('description','string',length=255,label='Description'),
		Field('pending','datetime'),
		Field('done','boolean'),
		Field('authoris','string',readable=False,writable=False))
db.define_table('note',
		Field('cd','datetime',default=request.now),
		Field('md','datetime',default=request.now),
		Field('title','string',length=128,label='Title',unique=True),
		Field('description','string',length=255,label="Short Description"),
		Field('val','text',label='Note'),
		Field('tags','string',default=''),
		Field('authoris',writable=False,default='',readable=False),
		Field('priority',requires=IS_IN_SET(['Private','Public'])))
db.define_table('tags',
		Field('word','string'),
		Field('title','string',default=''),
		Field('authoris','string',default=''))
db.define_table('att',
		Field('usr','string',readable=False,writable=False),
		Field('title','string',readable=False,writable=False),
		Field('nm','string',readable=False,writable=False),
		Field('fil','upload',label='Attachments',autodelete=True))
custom_auth_table = db[auth.settings.table_user_name] # get the custom_auth_table
#custom_auth_table.Country.requires=IS_IN_SET(['India','Usa','Canada'])
custom_auth_table.pic.multiple=True
custom_auth_table.first_name.requires =   IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.last_name.requires =   IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.password.requires = [CRYPT()]
custom_auth_table.notes.requires=IS_IN_DB(db,db.note.title)
custom_auth_table.email.requires = [ IS_EMAIL(error_message=auth.messages.invalid_email),IS_NOT_IN_DB(db, custom_auth_table.email)]
auth.settings.table_user = custom_auth_table # tell auth to use custom_auth_table
auth.define_tables(username=False, signature=False)
db.note.val.requires=IS_NOT_EMPTY()
if auth.is_logged_in():
	db.auth_user.email.writable=False

def ma(*a):
    import datetime
    mail.send(a[0],subject='Your Task '+a[1]+' is pending!!',message='You Have Tasks Pending')
    return
from gluon.scheduler import Scheduler
scheduler=Scheduler(db,dict(f=ma))


def email_user(sender,to,message,subject="group notice"):
    import smtplib
    fromaddr=sender
    if type(to)==type([]): toaddrs=to
    else: toaddrs=[to]
    msg="From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"%(fromaddr,", ".join(toaddrs),subject,message)
    server = smtplib.SMTP('localhost:25')
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
