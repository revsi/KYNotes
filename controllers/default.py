import datetime
import os
import re
# -*- coding: utf-8 -*-
import time
import gluon.contrib.simplejson
to=['rajat.singh@students.iiit.ac.in']

@auth.requires_login()
def index():
    response.flash ="Welcome to KEEP YOUR NOTES!"
    return locals()

@auth.requires_login()
def wall():
    a=db(db.auth_user.id==auth.user.id).select()
    b=a[0]['notes']
    a=b.split('@')
    d=[]
    for i in range(len(a)):
   	 c=db((db.note.authoris==auth.user.email)&(db.note.title==a[i])).select()
   	 if len(c):
		    d.append(c[0])

    d=sorted(d,key=lambda x: x['title'] )
    e=d
    p=0
    q=0
    r=0
    q1=[]
    r1=[]
    c=db(db.task.authoris==auth.user.email).select()
    for i in range(0,len(c)):
	    if c[i]['done']:
	    	p=1
	    else:
	    	if(c[i]['pending'].date()>=datetime.date.today()):
	    		q=1
			q1.append(c[i])
	    	else:
	    		r=1
			r1.append(c[i])
    q1=sorted(q1,key=lambda x: x['tit'] )
    r1=sorted(r1,key=lambda x: x['tit'] )
    response.flash ="Welcome to Your Wall!"
    return dict(b=b,a=e,c=c,p=p,q=q,r=r,q1=q1,r1=r1)


def user():
    return dict(form=auth())

def download():
    return response.download(request,db)

def call():
    session.forget()
    return service()


@auth.requires_login()
def home():
    return locals()
# our wall, will show our profile 
@auth.requires_login()
def search():
    form = SQLFORM.factory(Field('name',requires=IS_NOT_EMPTY()))
    if form.accepts(request):
        tokens = form.vars.name.split()
        query = reduce(lambda a,b:a&b,
                       [User.first_name.contains(k)|User.last_name.contains(k) \
                            for k in tokens])
        people = db(query).select(orderby=alphabetical)
    else:
        people = []
    response.flash ="Wanna Search something!"
    return locals()

@auth.requires_login()
def contact_us():
    form=SQLFORM(db1.message,fields=['your_name','your_email','your_message'])
    if form.accepts(request,session):
       subject='cfgroup message from '+form.vars.your_name
       email_user(sender=form.vars.your_email,to=to,message=form.vars.your_message,subject=subject)
       response.flash='your message has been submitted'
    elif form.errors:
       response.flash='please check the form and try again'
    return dict(form=form)

def about_us():
    return locals()

@auth.requires_login()
def create_note():
    response.flash='Create Your Notes Here !'
    if session.msg=='NO':
        response.flash='Invalid Title!'
        session.msg='Yes'
    if session.msg=='E':
        response.flash='Please Choose a priority'
        session.msg='Yes'
    form=SQLFORM.factory(
        Field('title','string',label='Title'),
        Field('description','string',label="Short description",requires=IS_NOT_EMPTY()),
        Field('val','text',label='Note',requires=IS_NOT_EMPTY()),
        Field('tags','string',label="Tags"),
        Field('priority',requires=IS_IN_SET(['Private','Public'])))
    if form.process().accepted:
        a=db(db.auth_user.id==auth.user.id).select()
        if form.vars.title in a[0]['notes'].split('@'):
            session.msg='NO'
            redirect(URL('create_note'))
        if form.vars.priority !='Private' and form.vars.priority !='Public':
            session.msg='E'
            redirect(URL('create_note'))
        b=a[0]['notes']+'@'+form.vars.title
        c=form.vars.tags.split(',')
        db(db.auth_user.id==auth.user.id).update(notes=b)
        session.title=form.vars.title
        db.note.insert(priority=form.vars.priority,title=form.vars.title,cd=request.now,md=request.now,description=form.vars.description,val=form.vars.val,tags=form.vars.tags,authoris=auth.user.email)
        for i in range(len(c)): 
            db.tags.insert(word=c[i],title=form.vars.title,authoris=auth.user.email)    
        redirect(URL('attachment'))
    return dict(form=form)

@auth.requires_login()
def attachment():
    message='Want to add Attachments ?'
    return dict(message=message)

@auth.requires_login()
def attachment_upload():
    if session.msg=='A':
        response.flash='Change File Name'
        session.msg='Y'
    title=session.title
    message='Hi'
    a=db((db.att.title==title)&(db.att.usr==auth.user.email)).select()
    form=SQLFORM(db.att,deletable=True,upload=os.path.join(request.folder,'/pic'))
    if request.vars.fil!=None:
        form.vars.nm=request.vars.fil.filename
    if form.process().accepted:
        a=db((db.att.nm==form.vars.nm)&(db.att.usr==auth.user.email)&(db.att.title==session.title)).select()
        if len(a)>0:
            session.msg='A'
            redirect(URL('attachment_upload'))
        db(db.att.fil==form.vars.fil).update(usr=auth.user.email,title=title,nm=form.vars.nm)
        redirect(URL('attachment_upload'))
    return dict(a=a,form=form)

@auth.requires_login()
def show():
    title=request.args(0,cast=str).strip()
    title=title.replace('_',' ')
    session.title=title
    a=db((db.note.title==title)& (auth.user.email==db.note.authoris)).select()
    tit=a[0]['title']
    val=a[0]['val']
    des=a[0]['description']
    tags=a[0]['tags']
    ct=a[0]['cd']
    mt=a[0]['md']
    pr=a[0]['priority']
    em=a[0]['authoris']
    l=db((db.att.title==title)&(db.att.usr==auth.user.email)).select()
    return dict(title=tit,val=val,des=des,tags=tags,ct=ct,mt=mt,a=a,l=l,pr=pr,em=em)

@auth.requires_login()
def edit():
    if session.message=='NOT':
        response.flash='Invalid Username'
        session.message='Yes'
    title=request.args(0,cast=str).replace('_',' ')
    title=title.replace('_',' ')
    c=db((db.note.title==title)&(db.note.authoris==auth.user.email)).select()
    form=SQLFORM.factory(
        Field('title','string',label='Title',default=c[0]['title']),
        Field('description','string',label='Description',default=c[0]['description']),
        Field('val','text',label='Note',default=c[0]['val'],requires=IS_NOT_EMPTY()),
        Field('tags','string',label='Tags',default=c[0]['tags']),
        Field('priority',requires=IS_IN_SET(['Public','Private'])))
    if form.process().accepted:
        c=form.vars.tags.split(',')
        a=db(db.note.title==form.vars.title).select()
        if len(a)==1 and a[0]['title']!=title:
            session.message='NOT'
            redirect(URL('edit',args=title))
        db((db.tags.title==title)&(db.tags.authoris==auth.user.email)).delete()
        for i in range(len(c)): 
            db.tags.insert(word=c[i],title=form.vars.title,authoris=auth.user.email)    
        
        db((db.note.title==title)&(auth.user.email==db.note.authoris)).update(title=form.vars.title,md=request.now,description=form.vars.description,val=form.vars.val,tags=form.vars.tags,priority=form.vars.priority)
        a=db(db.auth_user.id==auth.user.id).select()
        a=a[0]['notes']
        b=a.split('@')
        a=''
        for i in range(1,len(b)):
            if b[i].strip()==title.strip():
                b[i]=form.vars.title
            a+='@'+b[i]
        db(db.auth_user.id==auth.user.id).update(notes=a)
        redirect(URL('show',args=form.vars.title))
    return dict(form=form)

@auth.requires_login()
def edit_note():
    a=db(db.auth_user.id==auth.user.id).select()
    b=a[0]['notes']
    response.flash = "You can edit notes here!"
    return dict(b=b,a=[])
@auth.requires_login()

def delete_note():
    a=db(db.auth_user.id==auth.user.id).select()
    b=a[0]['notes']
    response.flash = "Are you sure ?"
    return dict(b=b,a=[])

@auth.requires_login()
def view_note():
    tagname=[]
    notest=[]
    a=db(auth.user.email==db.tags.authoris).select(db.tags.ALL)
    for i in range(len(a)):#if len(a) is zero then tell that there is no tags attached
        if a[i]['word'] not in tagname:
            tagname.append(a[i]['word'])
            tmp=[];
            for j in range(len(a)):
                if a[i]['word']==a[j]['word']:
                    tmp.append(a[j]['title'])
            notest.append(tmp)
    return dict(tagname=tagname,notest=notest)

@auth.requires_login()
def create_task():
    a={}
    response.flash='Create Tasks Here'
    if session.msg=='N':
        response.flash='Invalid Title'
        session.msg='Y'
    elif session.msg=='T':
        response.flash='Invalid Date'
        session.msg='Y'
    form=SQLFORM.factory(
            Field('title','string',label='Title',requires=IS_NOT_EMPTY()),
            Field('des','text',label='Description'),
            Field('pen','date',label='Date'))
    if form.process().accepted:
        a=db((db.task.tit==form.vars.title)&(auth.user.email==db.task.authoris)).select()
        if len(a)>0:
            session.msg='N'
            redirect(URL('create_task'))
        if form.vars.pen<datetime.date.today():
            session.msg='T'
            redirect(URL('create_task'))
        db.task.insert(tit=form.vars.title,description=form.vars.des,pending=form.vars.pen,done=False,authoris=auth.user.email)
#       Inserting For scheduler
        a={}
        a=[auth.user.email,form.vars.title]
        db.scheduler_task.insert(
        application_name='asd/appadmin',
        task_name=form.vars.title+'+'+auth.user.email,
        group_name='main',
        start_time=form.vars.pen+datetime.timedelta(-1),
        stop_time=form.vars.pen,
        status='QUEUED',
        function_name='f',
        enabled=True,
        period=60,
        args=gluon.contrib.simplejson.dumps(a))
        redirect(URL('wall'))
    return dict(form=form,a=a)

@auth.requires_login()
def edit_task():
    a=db(db.task.authoris==auth.user.email).select()
    response.flash = "You can edit tasks here!"
    return dict(a=a)

@auth.requires_login()
def delete_task():
    a=db(db.task.authoris==auth.user.email).select()
    return dict(a=a)

@auth.requires_login()
def search_task():
    form=SQLFORM.factory(Field('stime','date',requires=IS_NOT_EMPTY(),label="Start Time"),
            Field('endtime','date',label="End Time"))
    if form.process().accepted:
        st=form.vars.stime
        et=form.vars.endtime
        if et!=None:
            redirect(URL('taskdate2',args=(form.vars.stime,form.vars.endtime)))
        else:
            redirect(URL('taskdate',args=(form.vars.stime)))
    return dict(form=form)

@auth.requires_login()
def taskdate2():
    a=request.args(0,cast=str)
    b=request.args(1,cast=str)
    nam=[]
    name=db(db.task.authoris==auth.user.email).select()
    l=len(name)
    for i in range(l):
        if str(name[i]['pending'].date())>=a and str(name[i]['pending'].date())<=b:
            nam.append(name[i])
    return dict(nam=nam,a=a,b=b)

@auth.requires_login()
def taskdate():
    a=request.args(0,cast=str)
    nam=[]
    name=db(db.task.authoris==auth.user.email).select()
    l=len(name)
    for i in range(l):
        if str(name[i]['pending'].date())==a:
            nam.append(name[i])
    return dict(nam=nam,a=a)


@auth.requires_login()
def search_title():
    form=SQLFORM.factory(Field('Name','string',requires=IS_NOT_EMPTY()))
    if form.process().accepted:
        redirect(URL('searchtitle',args=form.vars.Name))
    return dict(form=form)

@auth.requires_login()
def search_tag():
    form=SQLFORM.factory(Field('Name','string',requires=IS_NOT_EMPTY()))
    if form.process().accepted:
        redirect(URL('searchtag',args=form.vars.Name))
    return dict(form=form)

@auth.requires_login()
def note_show():
    f=request.args(0,cast=int)
    c=[]
    d=[]
    a=db(db.auth_user.id==auth.user.id).select()
    b=a[0]['notes']
    a=b.split('@')
    for i in range(len(a)):
   	 c=db((db.note.authoris==auth.user.email)&(db.note.title==a[i])).select()
   	 if len(c):
		    d.append(c[0])
    if(f==1):
    	d=sorted(d,key=lambda x: x['title'] )
    elif(f==2):
    	d=sorted(d,key=lambda x: x['cd'] ,reverse=True)
    elif(f==3):
    	d=sorted(d,key=lambda x: x['md'] ,reverse=True)
    response.flash ="Notes Listing !"
    return dict(d=d,b=b,a=[])

@auth.requires_login()
def tshow():
    f=request.args(0,cast=int)
    a=[]
    b=[]
    status='Expired'
    d=db(db.task.authoris==auth.user.email).select()
    for i in range(len(d)):
	    b=[]
	    if d[i]['done']==True:
	    	status='Done'
	    else:
		if d[i]['pending'].date()<datetime.date.today():
		    status='Expired'
		else :
		    status='Pending'
	    b.append(d[i]['tit'])
	    b.append(status)
	    a.append(b)
    if(f==1):
    	d=sorted(d,key=lambda x: x['tit'] )
	a=sorted(a,key=lambda x: x[0])
    elif(f==2):
    	d=sorted(d,key=lambda x: x['pending'] ,reverse=True)
	a=sorted(a,key=lambda x: x[0])
    elif(f==3):
	a=sorted(a,key=lambda x: x[1])
	[x for (y,x) in sorted(zip(d[1],a))]
    response.flash ="Tasks Listing !"
    return dict(d=d,a=a,x='')

@auth.requires_login()
def search_inp():
    form1=SQLFORM.factory(Field('stime','date',requires=IS_NOT_EMPTY(),label="Start Time"),
            Field('endtime','date',label="End Time"),table_name="1000")
    form2=SQLFORM.factory(Field('Name','string',requires=IS_NOT_EMPTY()),table_name="2")
    form3=SQLFORM.factory(Field('Name','string',requires=IS_NOT_EMPTY()),table_name="3")
    d=['Search By Title','Search By Tags','Search By Date']
    a=[form2,form3,form1]  
    if form1.accepts(request.vars,session):
        st=form1.vars.stime
        et=form1.vars.endtime
        if et!=None:
            redirect(URL('sdate2',args=(form1.vars.stime,form1.vars.endtime)))
        else:
            redirect(URL('sdate',args=(form1.vars.stime)))
    if form2.accepts(request.vars,session):
        redirect(URL('searchtitle',args=form2.vars.Name))
    if form3.accepts(request.vars,session):
        redirect(URL('searchtag',args=form3.vars.Name))
    response.flash ="Search for anything !"
    return dict(a=a,d=d,form2=form2)

@auth.requires_login()
def search_date():
    form=SQLFORM.factory(Field('stime','date',requires=IS_NOT_EMPTY(),label="Start Time"),
            Field('endtime','date',label="End Time"))
    if form.process().accepted:
        st=form.vars.stime
        et=form.vars.endtime
        if et!=None:
            redirect(URL('sdate2',args=(form.vars.stime,form.vars.endtime)))
        else:
            redirect(URL('sdate',args=(form.vars.stime)))
    return dict(form=form)

@auth.requires_login()
def searchtitle():
    a=request.args(0,cast=str).replace('_',' ')
    a=a.replace('_',' ')
    nam=[]
    name=db(db.note.title>0).select(db.note.ALL)
    l=len(name)
    for i in range(0,l):
        mat=re.search(a,name[i]['title'])
        if mat and name[i]['authoris']==auth.user.email:
            nam.append(name[i])
    return dict(nam=nam)

@auth.requires_login()
def searchtag():
    a=request.args(0,cast=str).replace('_',' ')
    a=a.replace('_',' ')
    nam=[]
    tit=[]
    name=db(db.tags.id>0).select(db.tags.ALL)
    l=len(name)
    for i in range(len(name)):
        mat=re.search(a,name[i]['word'])
        if mat and name[i]['authoris']==auth.user.email:
            nam.append(name[i])
    return dict(nam=nam)

@auth.requires_login()
def sdate2():
    a=request.args(0,cast=str)
    b=request.args(1,cast=str)
    nam=[]
    nam2=[]
    d=[]
    name=db(db.note.authoris==auth.user.email).select()
    l=len(name)
    for i in range(l):
        if str(name[i]['cd'].date())>=a and str(name[i]['cd'].date())<=b:
            nam.append(name[i])
        if str(name[i]['md'].date())>=a and str(name[i]['md'].date())<=b:
            nam2.append(name[i])
    return dict(nam=nam,nam2=nam2,a=a,b=b)

@auth.requires_login()
def sdate():
    a=request.args(0,cast=str)
    nam=[]
    nam2=[]
    d=[]
    name=db(db.note.authoris==auth.user.email).select()
    l=len(name)
    for i in range(l):
        if str(name[i]['cd'].date())==a:
            nam.append(name[i])
        if str(name[i]['md'].date())==a:
            nam2.append(name[i])
    return dict(nam=nam,nam2=nam2,a=a)

@auth.requires_login()
def shtask():
    title=request.args(0,cast=str).strip()
    title=title.replace('_',' ')
    a=db((db.task.tit==title)& (auth.user.email==db.task.authoris)).select()
    tit=a[0]['tit']
    des=a[0]['description']
    return dict(title=tit,description=des,a=a,pending=a[0]['pending'])

@auth.requires_login()
def didtask():
    a=request.args(0,cast=str).replace('_',' ')
    d=db((db.task.authoris==auth.user.email)&(db.task.tit==a)).update(done=True)
    redirect(URL('task_show',args=1))
    return()

@auth.requires_login()
def ndidtask():
    a=request.args(0,cast=str).replace('_',' ')
    d=db((db.task.authoris==auth.user.email)&(db.task.tit==a)).update(done=False)
    redirect(URL('task_show',args=1))
    return()

@auth.requires_login()
def delet():
    title=request.args(0,cast=str).replace('_',' ')
    title=title.replace('_',' ')
    db((db.note.title==title)&(db.note.authoris==auth.user.email)).delete()
    db((db.tags.title==title)&(db.tags.authoris==auth.user.email)).delete()
    db((db.att.usr==auth.user.email)&(db.att.title==title)).delete()
    a=db(db.auth_user.id==auth.user.id).select()
    a=a[0]['notes']
    b=a.split('@')
    a=''
    for i in range(1,len(b)):
        if b[i].strip()==title.strip():
            continue
        a+='@'+b[i]
    db(db.auth_user.id==auth.user.id).update(notes=a)
    redirect(URL('wall'))
    return dict(form=form)

@auth.requires_login()
def eddel():
    a=db(db.auth_user.id==auth.user.id).select()
    b=a[0]['notes']
    response.flash = "Are you sure ?"
    return dict(b=b,a=[])

@auth.requires_login()
def attdel():
    title=request.args(0,cast=str).strip()
    title=title.replace('_',' ')
    db(db.att.fil==title).delete()
    redirect(URL('attachment_upload'))
    return()

@auth.requires_login()
def taskdel():
    title=request.args(0,cast=str).strip()
    title=title.replace('_',' ')
    db((db.task.tit==title)&(db.task.authoris==auth.user.email)).delete()
    db(db.scheduler_task.task_name==title+'+'+auth.user.email).delete()
    message='Done'
    redirect(URL('wall'))
    return (message)

@auth.requires_login()
def taskdel1():
    title=request.args(0,cast=str).strip()
    title=title.replace('_',' ')
    db((db.task.tit==title)&(db.task.authoris==auth.user.email)).delete()
    db(db.scheduler_task.task_name==title+'+'+auth.user.email).delete()
    message='Done'
    redirect(URL('delete_task'))
    return (message)

@auth.requires_login()
def taskedit():
    if session.message=='NOT':
        response.flash='Invalid Username'
        session.message='Yes'
    title=request.args(0,cast=str).strip()
    title=title.replace('_',' ')
    c=db(db.task.tit==title).select()
    form=SQLFORM.factory(
        Field('title','string',label='Title',default=c[0]['tit']),
        Field('description','text',label='Description',default=c[0]['description'],length=255),
        Field('time','date',default=c[0]['pending']),
        Field('done','boolean',default=c[0]['done']))
    if form.process().accepted:
        a=db(db.task.tit==form.vars.title).select()
        if len(a)==1 and a[0]['tit']!=title:
            session.message='NOT'
            redirect(URL('taskedit',args=title))
        db((db.task.tit==title)&(auth.user.email==db.task.authoris)).update(tit=form.vars.title,description=form.vars.description,pending=form.vars.time,done=form.vars.done)    
        db(db.scheduler_task.task_name==title+'+'+auth.user.email).delete()
        if(form.vars.done==False):
            a={}
            a=[auth.user.email,form.vars.title]
            db.scheduler_task.insert(
            application_name='asd/appadmin',
            task_name=form.vars.title+'+'+auth.user.email,
            group_name='main',
            start_time=form.vars.time+datetime.timedelta(-1),
            stop_time=form.vars.pen,
            status='QUEUED',
            function_name='f',
            enabled=True,
            period=60,
            args=gluon.contrib.simplejson.dumps(a))
        redirect(URL('shtask',args=form.vars.title))
    return dict(form=form,title=title)

def task_show():
    f=request.args(0,cast=int)
    a=[]
    b=[]
    status='Expired'
    d=db(db.task.authoris==auth.user.email).select()
    for i in range(len(d)):
	    b=[]
	    if d[i]['done']==True:
	    	status='Done'
	    else:
		if d[i]['pending'].date()<datetime.date.today():
		    status='Expired'
		else :
		    status='Pending'
	    b.append(d[i]['tit'])
	    b.append(status)
	    a.append(b)
    if(f==1):
    	d=sorted(d,key=lambda x: x['tit'] )
	a=sorted(a,key=lambda x: x[0])
    elif(f==2):
    	d=sorted(d,key=lambda x: x['pending'] ,reverse=True)
	a=sorted(a,key=lambda x: x[0])
    elif(f==3):
	a=sorted(a,key=lambda x: x[1])
	[x for (y,x) in sorted(zip(d[1],a))]
    response.flash ="Tasks Listing !"
    return dict(d=d,a=a,x='')

@auth.requires_login()
def taskedit1():
    if session.message=='NOT':
        response.flash='Invalid Username'
        session.message='Yes'
    title=request.args(0,cast=str).strip()
    title=title.replace('_',' ')
    c=db(db.task.tit==title).select()
    form=SQLFORM.factory(
        Field('title','string',label='Title',default=c[0]['tit']),
        Field('description','string',label='Description',default=c[0]['description']),
        Field('time','date',default=c[0]['pending']),
        Field('done','boolean',default=c[0]['done']))
    if form.process().accepted:
        a=db(db.task.tit==form.vars.title).select()
        if len(a)==1 and a[0]['tit']!=title:
            session.message='NOT'
            redirect(URL('taskedit',args=title))
        db((db.task.tit==title)&(auth.user.email==db.task.authoris)).update(tit=form.vars.title,description=form.vars.description,pending=form.vars.time,done=form.vars.done)    
        db(db.scheduler_task.task_name==title+'+'+auth.user.email).delete()
        if(form.vars.done==False):
            a={}
            a=[auth.user.email,form.vars.title]
            db.scheduler_task.insert(
            application_name='asd/appadmin',
            task_name=form.vars.title+'+'+auth.user.email,
            group_name='main',
            start_time=form.vars.time+datetime.timedelta(-1),
            stop_time=form.vars.pen,
            status='QUEUED',
            function_name='f',
            enabled=True,
            period=60,
            args=gluon.contrib.simplejson.dumps(a))
        redirect(URL('edit_task',args=form.vars.title))
    return dict(form=form,title=title)


@auth.requires_login()
def edit1():
    if session.message=='NOT':
        response.flash='Invalid Username'
        session.message='Yes'
    title=request.args(0,cast=str).replace('_',' ')
    title=title.replace('_',' ')
    c=db((db.note.title==title)&(db.note.authoris==auth.user.email)).select()
    form=SQLFORM.factory(
        Field('title','string',label='Title',default=c[0]['title']),
        Field('description','string',label='Description',default=c[0]['description']),
        Field('val','text',label='Note',default=c[0]['val'],requires=IS_NOT_EMPTY()),
        Field('tags','string',label='Tags',default=c[0]['tags']))
    if form.process().accepted:
        c=form.vars.tags.split(',')
        a=db(db.note.title==form.vars.title).select()
        if len(a)==1 and a[0]['title']!=title:
            session.message='NOT'
            redirect(URL('edit',args=title))
        db((db.tags.title==title)&(db.tags.authoris==auth.user.email)).delete()
        for i in range(len(c)): 
            db.tags.insert(word=c[i],title=form.vars.title,authoris=auth.user.email)        
        db((db.note.title==title)&(auth.user.email==db.note.authoris)).update(title=form.vars.title,md=request.now,description=form.vars.description,val=form.vars.val,tags=form.vars.tags)
        a=db(db.auth_user.id==auth.user.id).select()
        a=a[0]['notes']
        b=a.split('@')
        a=''
        for i in range(1,len(b)):
            if b[i].strip()==title.strip():
                b[i]=form.vars.title
            a+='@'+b[i]
        db(db.auth_user.id==auth.user.id).update(notes=a)
        redirect(URL('edit_note',args=form.vars.title))
    return dict(form=form)
