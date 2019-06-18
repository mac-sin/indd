# -*- coding: utf-8 -*-
import gluon.contrib.simplejson as sj
import time
import datetime
from gluon.tools import Auth, Service, PluginManager

def index():
    today = datetime.datetime.today()
    oldday = datetime.datetime(2009, 7, 22)
    # response.flash = today
    if request.args(0):
        row = db.exportlist(request.args(0,cast=int))
        form = SQLFORM(db.exportlist, row, deletable=True, showid=False, formstyle='bootstrap3_stacked', fields=['pdfpreset','pagerange','status','errormessage'])
        my_extra_element = DIV(
                                LABEL('Filepath',_class='conrol-label'),
                                PRE(row['filepath'], _class='text-light text'),
                                _class='form-group',
                                )
        form[0].insert(0,my_extra_element)
    else:
        form = SQLFORM(db.exportlist, formstyle='bootstrap3_stacked')
    # form['_style']='background-color:#343a40'
    if form.process().accepted:
        response.flash = 'record inserted'
        redirect(URL(r=request,c='pdf',f='index'))
    return locals()

def connect():
    conn = {'connect':True, 'host':request.env.http_host}
    # return dict(conn=conn)
    return sj.dumps( conn )

def onIdle():
    if request.args(0)=="new":
        id = db.onidle.insert( name=request.vars.name, status=request.vars.status )
        redirect(URL('onIdle'))
    elif request.args(0)=="last":
        data = db(db.onidle).select().last().as_dict()
    elif request.args(0):
        data = db(db.onidle.id==request.args(0)).select().as_dict()
    else:
        data = db(db.onidle).select(orderby="onidle.id DESC",limitby=(0,20))
    return dict(data=data)


def getExportList():
    draw = int(request.vars.draw)
    start = int(request.vars.start)
    length = start + int(request.vars.length)
    searchValue = request.vars["search[value]"]
    # orderColumn = request.vars["order[0][column]"]
    # orderBy = request.vars["columns["+ orderColumn +"][data]"]
    # orderType = request.vars["order[0][dir]"]
    # orderQuery = "exportlist."+orderBy+" "+orderType
    orderQuery = "exportlist.id desc"
    recordsTotal = db(db.exportlist).count()
    if searchValue:
        recordsFiltered = db((db.exportlist.filepath.contains(searchValue))|(db.exportlist.status.contains(searchValue))).count()
        datas = db((db.exportlist.filepath.contains(searchValue))|(db.exportlist.status.contains(searchValue))).select(orderby=orderQuery,limitby=(start,length)).as_list()
    else:
        datas = db(db.exportlist).select(orderby=orderQuery,limitby=(start,length)).as_list()
        recordsFiltered = recordsTotal
    data = {"draw":draw, "recordsTotal":recordsTotal, "recordsFiltered":recordsFiltered, "data":datas }
    data["q"] = sj.dumps( request.vars )
    data["method"] = request.env.request_method
    data["ajax"] = request.ajax
    data["start"] = start
    data["length"] = length
    # data["orderColumn"] = orderColumn
    # data["orderBy"] = orderBy
    # data["orderType"] = orderType
    data["searchValue"] = searchValue
    return response.json(data)

def launchApp():
    import subprocess
    command = 'open -a "Adobe InDesign CC 2018"'
    success = False
    warning = False
    message = ""
    if subprocess.call( command, shell=True )==0:
        success = True
        warning = False
        message = request.function + " success."
    else:
        success = False
        warning = True
        message = request.function + " error."
    return sj.dumps( dict(success=success, warning=warning, message=message, id=request.vars.id) )

def openFile():
    import subprocess
    if (request.env.http_host=="localhost:8000") or (request.env.http_host=="127.0.0.1:8000") :
        logsInddPath = '/Users/kwongsin/Desktop/logs.indd'
    elif request.env.http_host =="inhouse1.skyyer.com:98":
        logsInddPath = '/Users/skyyer_edit01/Desktop/logs.indd'
    applescript ='''osascript<<END
tell application id "com.adobe.InDesign"
    try
        set myDocument to open "'''+ logsInddPath +'''"
    on error
        set myDocument to open "'''+ logsInddPath +'''"
    end try
end tell
'''
    success = False
    warning = False
    message = ""
    if subprocess.call( applescript, shell=True )==0:
        success = True
        warning = False
        message = request.function + " success."
    else:
        success = False
        warning = True
        message = request.function + " error."
    return sj.dumps( dict(success=success, warning=warning, message=message, id=request.vars.id) )

def alertCount():
    import subprocess
    scriptName = 'x_alertCount.jsx'
    if (request.env.http_host=="localhost:8000") or (request.env.http_host=="127.0.0.1:8000") :
        scriptPath = 'Users:kwongsin:Google Drive:Adobe_Scripts:beta:'
    elif request.env.http_host =="inhouse1.skyyer.com:98":
        scriptPath = 'Users:skyyer_edit01:Desktop:adobe_script:'
    args = [111, 3]
    p = subprocess.Popen( ['/usr/bin/osascript', '-'] + [str(arg) for arg in args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    scptA = '''
tell application id "com.adobe.InDesign"
	try
        --activate
		set aScriptPath to "'''+ scriptPath + scriptName +'''"
		set myAlertCount to do script aScriptPath language javascript
        --return "myAlertCount= " & myAlertCount & "."
	on error errStr
		--activate
		--display alert errStr
        set myAlertCount to "undefined"
	end try
end tell
'''
    stdout, stderr = p.communicate(scptA)
    myarg = [str(arg) for arg in args]
    if stdout:
        success = True
        warning = False
        stdout = stdout.replace('\n', '')
        message = request.function + " result: "+ stdout
    else:
        success = False
        warning = True
        message = request.function + " error."
    result = dict( stdout=stdout, stderr=stderr, args=args, host=request.env.http_host, success=success, warning=warning, message=message, id=request.vars.id )
    return sj.dumps( result )

def checkAppStatus():
    import subprocess
    scriptName = 'x_checkStatus.jsx'
    if (request.env.http_host=="localhost:8000") or (request.env.http_host=="127.0.0.1:8000") :
        scriptPath = 'Users:kwongsin:Google Drive:Adobe_Scripts:beta:'
    elif request.env.http_host =="inhouse1.skyyer.com:98":
        scriptPath = 'Users:skyyer_edit01:Desktop:adobe_script:'
    scptA ='''
tell application id "com.adobe.InDesign"
	try
		set aScriptPath to "'''+ scriptPath + scriptName +'''"
		do script aScriptPath language javascript
	on error errStr
		activate
		display alert errStr
	end try
end tell
'''
    args = [111, 3]
    p = subprocess.Popen( ['/usr/bin/osascript', '-'] + [str(arg) for arg in args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = p.communicate(scptA)
    myarg = [str(arg) for arg in args]
    if stdout:
        success = True
        warning = False
        message = request.function + " result: "+ stdout
    else:
        success = False
        warning = True
        message = request.function + " error."
    result = dict( stdout=stdout, stderr=stderr, args=args, host=request.env.http_host, success=success, warning=warning, message=message, id=request.vars.id )
    return sj.dumps( result )

def backgroundTasks():
    import subprocess
    scriptName = 'x_getBackgroundTasks.jsx'
    if (request.env.http_host=="localhost:8000") or (request.env.http_host=="127.0.0.1:8000") :
        scriptPath = 'Users:kwongsin:Google Drive:Adobe_Scripts:beta:'
    elif request.env.http_host=="inhouse1.skyyer.com:98":
        scriptPath = 'Users:skyyer_edit01:Desktop:adobe_script:'
    scptA ='''
tell application id "com.adobe.InDesign"
	try
		set aScriptPath to "'''+ scriptPath + scriptName +'''"
		do script aScriptPath language javascript
	on error errStr
		activate
		display alert errStr
	end try
end tell
'''
    args = [111, 3]
    p = subprocess.Popen( ['/usr/bin/osascript', '-'] + [str(arg) for arg in args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = p.communicate(scptA)
    myarg = [str(arg) for arg in args]
    if stdout:
        success = True
        warning = False
        message = request.function + " result: "+ stdout
    else:
        success = False
        warning = True
        message = request.function + " error."
    result = dict( stdout=stdout, stderr=stderr, args=args, host=request.env.http_host, success=success, warning=warning, message=message, id=request.vars.id )
    return sj.dumps( result )


def addIdleTask():
    import subprocess
    scriptName = 'x_idle_onIdle.jsx'
    if (request.env.http_host=="localhost:8000") or (request.env.http_host=="127.0.0.1:8000") :
        scriptPath = 'Users:kwongsin:Google Drive:Adobe_Scripts:beta:'
    elif request.env.http_host =="inhouse1.skyyer.com:98":
        scriptPath = 'Users:skyyer_edit01:Desktop:adobe_script:'
    applescript ='''osascript<<END
tell application id "com.adobe.InDesign"
	try
		set aScriptPath to "'''+ scriptPath + scriptName +'''"
		do script aScriptPath language javascript
	on error errStr
		activate
		display alert errStr
	end try
end tell
'''
    success = False
    warning = False
    message = ""
    if subprocess.call( applescript, shell=True )==0:
        success = True
        warning = False
        message = request.function + " success."
    else:
        success = False
        warning = True
        message = request.function + " error."
    return sj.dumps( dict(success=success, warning=warning, message=message, id=request.vars.id) )


def removeIdleTasks():
    import subprocess
    scriptName = 'x_removeIdleTasks.jsx'
    if (request.env.http_host=="localhost:8000") or (request.env.http_host=="127.0.0.1:8000") :
        scriptPath = 'Users:kwongsin:Google Drive:Adobe_Scripts:beta:'
    elif request.env.http_host =="inhouse1.skyyer.com:98":
        scriptPath = 'Users:skyyer_edit01:Desktop:adobe_script:'
    applescript ='''osascript<<END
tell application id "com.adobe.InDesign"
	try
		set aScriptPath to "'''+ scriptPath + scriptName +'''"
		do script aScriptPath language javascript
	on error errStr
		activate
		display alert errStr
	end try
end tell
'''
    success = False
    warning = False
    message = ""
    if subprocess.call( applescript, shell=True )==0:
        success = True
        warning = False
        message = request.function + " success."
    else:
        success = False
        warning = True
        message = request.function + " error."
    return sj.dumps( dict(success=success, warning=warning, message=message, id=request.vars.id) )


def getFolders():
    start_time = time.time()
    currentpath = request.vars.selectfolder
    if not currentpath:
        return sj.dumps( dict(currentpath="null") )
    import os
    inddfiles = []
    child = []
    # if currentpath == "/Volumes":
    #     return sj.dumps( dict(currentpath="null") )
    # if currentpath != "/Volumes/Public1":
    #     child.append(dict(name="..", path=".."))
    try:
        oslistdir = os.listdir(currentpath)
    except Exception, e:
        return sj.dumps( dict(error=e) )

    oslistdir.sort()
    for filename in oslistdir:
        filepath = os.path.join(currentpath,filename)
        isFolder = os.path.isdir(filepath)
        isFile = os.path.isfile(filepath)
        isIndd = filename.endswith(".indd")

        if filename.startswith(".") or filename==".DS_Store":
            continue
        elif isFolder:
            child.append(dict(name=filename, path=filepath))
        elif isFile:
            if isIndd:
                inddfiles.append(dict(name=filename, path=filepath))

    currentname = currentpath.split("/")
    currentname = currentname[-1]
    elapsed_time = time.time() - start_time
    result = dict(currentname=currentname, currentpath=currentpath, child=child, inddfiles=inddfiles, childlength=len(child)-1, inddfileslength=len(inddfiles) )
    return sj.dumps(result)

def newExportRequest():
    filepath = request.vars.filepath
    pdfpreset = request.vars.pdfpreset
    pagerange = request.vars.pagerange
    fp = filepath.split("/")
    filename = fp.pop()
    folderpath = ("/").join(fp)
    # filepath_copy = folderpath +"/copy_"+ filename
    fn = "/"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+"_"
    filepath_copy = folderpath + fn + filename
    result = db.exportlist.insert(filepath=filepath, pdfpreset=pdfpreset, pagerange=pagerange, filename=filename, folderpath=folderpath, filepath_copy=filepath_copy)
    return sj.dumps( result )

def job():
    count = db(db.exportlist.status=="Idle").count()
    if count==0:
        return "no_data"
    try:
        data = db(db.exportlist.status=="Idle").select().first().as_dict()
        data["createdate"] = str( data["createdate"] )
        data["mdate"] = str( data["mdate"] )
        fp = data["filepath"]
        fpc = data["filepath_copy"]
        command = 'cp "'+ fp +'" "'+ fpc +'"'
        import subprocess
        if subprocess.call( command, shell=True )==0:
            return sj.dumps( data )
        else:
            db(db.exportlist.id==data["id"]).update(status="Error",errormessage="indd_file_not_find")
            return "indd_file_not_find"
    except Exception, e:
        return e
    #     return sj.dumps( dict(error=e) )

def updatejob():
    id = int(request.vars.jobid)
    status = request.vars.status
    inddname = request.vars.inddname
    execTime = 0.00001
    if request.vars.exectime:
        execTime = int(request.vars.exectime)
    errormessage = request.vars.errormessage
    if status=="P":
        db(db.exportlist.id==id).update(status="Processing", errormessage="", inddname=inddname)
    elif status=="E":
        db(db.exportlist.id==id).update(status="Error", errormessage=errormessage, inddname=inddname )
        data = db(db.exportlist.id==id).select().first().as_dict()
        fp = data["filepath"].split("/")
        data["fileName"] = fp.pop()
        data["folderPath"] = ("/").join(fp)
        data["filepath_dup"] = data["folderPath"] +"/copy_"+ data["fileName"]
        # import subprocess
        # command = 'rm "'+ data["filepath_dup"] +'"'
        # if subprocess.call( command, shell=True )==0:
        return dict()
    elif status=="F":
        db(db.exportlist.id==id).update(status="Finish", errormessage="", exectime=execTime, mdate=request.now, inddname=inddname)
        data = db(db.exportlist.id==id).select().first().as_dict()
        fp = data["filepath"].split("/")
        data["fileName"] = fp.pop()
        data["folderPath"] = ("/").join(fp)
        data["filepath_dup"] = data["folderPath"] +"/copy_"+ data["fileName"]
        # import subprocess
        # command = 'rm "'+ data["filepath_dup"] +'"'
        # if subprocess.call( command, shell=True )==0:
        # return dict()
    return dict()

