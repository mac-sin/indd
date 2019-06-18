# -*- coding: utf-8 -*-
import gluon.contrib.simplejson as sj
import time
import datetime
from gluon.tools import Auth, Service, PluginManager

def index():
    return locals()

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


def getOnIdles():
    """
    s = '"{
            "draw": "1",
            "start": "0",
            "length": "10",
            "order[0][column]": "0",
            "order[0][dir]": "desc",
            "search[value]": "",
            "search[regex]": "false",

            "columns[0][name]": "",
            "columns[0][data]": "id",
            "columns[0][orderable]": "true",
            "columns[0][searchable]": "true",
            "columns[0][search][value]": "",
            "columns[0][search][regex]": "false",

            "columns[1][name]": "",
            "columns[1][data]": "name",
            "columns[1][orderable]": "true",
            "columns[1][searchable]": "true",
            "columns[1][search][value]": "",
            "columns[1][search][regex]": "false",

            "columns[2][name]": "",
            "columns[2][data]": "status",
            "columns[2][orderable]": "true",
            "columns[2][searchable]": "true",
            "columns[2][search][value]": "",
            "columns[2][search][regex]": "false",

            "columns[3][name]": "",
            "columns[3][data]": "createdate",
            "columns[3][orderable]": "true",
            "columns[3][searchable]": "true",
            "columns[3][search][value]": "",
            "columns[3][search][regex]": "false",
            }"'
    """
    draw = int(request.vars.draw)
    start = int(request.vars.start)
    length = start + int(request.vars.length)
    searchValue = request.vars["search[value]"]
    orderColumn = request.vars["order[0][column]"]
    orderBy = request.vars["columns["+ orderColumn +"][data]"]
    orderType = request.vars["order[0][dir]"]
    orderQuery = "onidle."+orderBy+" "+orderType
    recordsTotal = db(db.onidle).count()
    if searchValue:
        recordsFiltered = db((db.onidle.name.contains(searchValue))|(db.onidle.status.contains(searchValue))).count()
        datas = db((db.onidle.name.contains(searchValue))|(db.onidle.status.contains(searchValue))).select(orderby=orderQuery,limitby=(start,length)).as_list()
    else:
        datas = db(db.onidle).select(orderby=orderQuery,limitby=(start,length)).as_list()
        recordsFiltered = recordsTotal
    data = {"draw":draw, "recordsTotal":recordsTotal, "recordsFiltered":recordsFiltered, "data":datas }
    data["q"] = sj.dumps( request.vars )
    data["method"] = request.env.request_method
    data["ajax"] = request.ajax
    data["start"] = start
    data["length"] = length
    data["orderColumn"] = orderColumn
    data["orderBy"] = orderBy
    data["orderType"] = orderType
    data["searchValue"] = searchValue
    return response.json(data)


