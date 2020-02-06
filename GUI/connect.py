"""***************************************************************************

                                 connect.py


***************************************************************************"""

# 使用pymongo模块连接mongoDB数据库
# Connect to mongoDB database using pymongo module
# coding=utf-8
from pymongo import MongoClient

from tkinter import dialog

"""---------------------------------------------------------------------------

这个.py文件是用来连接mongoDB数据库的。
This .py file is used to connect to the mongoDB database."""

# 建立MongoDB数据库连接
# Establish a MongoDB database connection
client = MongoClient('localhost', 27017)

gl_collection = ''

"""---------------------------------------------------------------------------

judge_database(database, root)函数会判断用户将要创建的数据库是否已存在。
如果存在，弹出对话框询问用户是否要删除已存在数据库或则对自己的数据库重命名。
如果不存在，直接创建。
The judge_database (database, root) function will
determine whether the database that the user will create already exists.
If it exists, a pop-up dialog asks the user if they want to
delete the existing database or rename their own database.
If it does not exist, create it directly."""


def judge_database(database, root):
    # 返回系统中的数据库列表
    # Returns a list of databases in the system
    db_list = client.list_database_names()
    if database in db_list:
        # 使用dialog.Dialog创建对话框
        d = dialog.Dialog(root,  # 设置该对话框所属的窗口
                          {'title': 'Tip',  # 标题
                           'text': "The database is already existed! \n"
                                   "Delete existed database? \n"
                                   "OR\n"
                                   "Rename your database?",  # 内容
                           'bitmap': 'warning',  # 图标
                           'default': '',  # 设置默认选中项
                           'strings': ('Delete', 'Rename')})
        if d.num == 0:
            client.drop_database(database)
            return False
        else:
            return True
    else:
        return False


"""---------------------------------------------------------------------------

create_collection(database, collection)函数连接集合。
该函数返回数据库的集合。
The create_collection (database, collection) function connects collections.
This function returns a collection of databases."""


def create_collection(database, collection):
    db = client[database]
    return db[collection]


"""---------------------------------------------------------------------------

set_collection(collection)函数将数据库集合赋值给全局变量gl_collection。
The set_collection (collection) function
assigns the database collection to the global variable gl_collection."""


def set_collection(collection):
    global gl_collection
    gl_collection = collection


"""---------------------------------------------------------------------------

get_collection()函数会获得这个全局变量，供其他文件使用。
The get_collection () function will
get this global variable for use by other files."""


def get_collection():
    return gl_collection

