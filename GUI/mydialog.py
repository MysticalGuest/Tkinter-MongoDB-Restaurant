"""***************************************************************************

                                 mydialog.py


***************************************************************************"""

from tkinter import *
from tkinter import ttk

import json
import time

from bson import ObjectId

from connect import *

from tkinter.filedialog import askopenfile

from tkinter.messagebox import showinfo, showwarning, showerror

from math import radians, cos, sin, asin, sqrt

"""---------------------------------------------------------------------------

这个.py文件里包含了许多方法。
将会在myfunction.py文件中被调用。
This .py file contains many methods.
Will be called in myfunction.py file."""

my_coord = ['', '']


"""---------------------------------------------------------------------------

my_table_dialog(message, object_id)函数与主界面的treeview表格绑定，
当用户双击某一条数据后，就会弹出这个对话框，显示详细的餐厅评分信息。
The my_table_dialog (message, object_id) function
is bound to the treeview table in the main interface.
When the user double-clicks a piece of data, this dialog box will pop up,
displaying detailed restaurant rating information."""


def my_table_dialog(message, object_id):
    top = Toplevel()
    top.title('Grades Information')
    # 设置为模式对话框
    top.grab_set()
    # 让对话框获取焦点
    top.focus_set()

    width = 600
    height = 200
    screenwidth = top.winfo_screenwidth()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, 100)
    top.geometry(size)
    top.resizable(width=False, height=False)

    tree_grade = ttk.Treeview(top, show="headings")
    # 定义列
    tree_grade["columns"] = ("date", "grade", "score")
    # 设置列
    tree_grade.column("date", anchor='center')
    tree_grade.column("grade", anchor='center')
    tree_grade.column("score", anchor='center')
    # 设置显示的表头名
    tree_grade.heading("date", text="Date")
    tree_grade.heading("grade", text="Grade")
    tree_grade.heading("score", text="Score")
    if len(message) != 0:
        for i in range(len(message)):
            tree_grade.insert("",
                              i,
                              values=(message[i]["date"],
                                      message[i]["grade"],
                                      message[i]["score"]))
    newb = ttk.Button(top, text='New', width=20)
    newb.configure(command=(lambda: new_grade(tree_grade, message)))
    newb.pack(side=BOTTOM)

    """-----------------------------------------------------------------------

    set_cell_value(event)函数与对话框绑定，双击对话框中的得分信息进入编辑状态，
    点击文本框后面的“OK”按钮，即可立即保存。
    The set_cell_value (event) function is bound to the dialog box.
    Double-click the score information in the dialog box to
    enter the editing state.
    Click the "OK" button behind the text box to save immediately."""

    def set_cell_value(event):
        for item in tree_grade.selection():
            item_text = tree_grade.item(item, "values")
        # 列
        column = tree_grade.identify_column(event.x)
        # 行
        row = tree_grade.identify_row(event.y)
        try:
            cn = int(str(column).replace('#', ''))
            rn = int(str(row).replace('I', ''))
        except Exception as e:
            print(e)
        if cn == 1:
            wid = 20  # "date"列输入框长度长一些
        else:
            wid = 10
        entry_edit = Text(top, width=wid, height=1)
        # 设置entry输入框的位置
        if cn == 1:
            entry_x = 20
        elif cn == 2:
            entry_x = 250
        # elif cn == 3:
        else:
            entry_x = 460
        try:
            entry_edit.place(x=entry_x, y=6 + rn * 20)
        except Exception as e:
            print(e)

        """-------------------------------------------------------------------

        save_edit()函数时点击“OK”按钮触发事件，会将修改信息保存到数据库。
        When the save_edit () function is clicked on the "OK" button to
        trigger an event,
        the modification information will be saved to the database."""

        def save_edit():
            value = entry_edit.get(0.0, "end")
            tree_grade.set(item, column=column, value=value)
            # 记录下来改变的是第几条数据
            order = int(item.replace("I", '')) - 1
            # 判断修改的是第几列的数据
            if column == '#1':  # 第一列"date"
                # 从输入框读取的数据总是带有'\n'，用value[0]取得合适数据
                val = value[0]
                message[order]["date"] = val
            elif column == '#2':  # 第二列"grade"
                # 从输入框读取的数据总是带有'\n'，用value[0]取得合适数据
                val = value[0]
                message[order]["grade"] = val
            elif column == '#3':  # 第三列"score"
                int_value = int(value)
                message[order]["score"] = int_value
            my_query = {"_id": ObjectId(object_id)}
            new_values = {"$set": {"grades": message}}
            # 在mongoDB数据库中进行修改
            get_collection().update_one(my_query, new_values)

            entry_edit.destroy()
            okb.destroy()

        okb = ttk.Button(top, text='OK', width=4, command=save_edit)
        okb_x = 332  # 设置okb按钮的位置
        if cn == 1:
            okb_x = 150
        elif cn == 3:
            okb_x = 550
        try:
            okb.place(x=okb_x, y=2 + rn * 20)
        except Exception as e:
            print(e)

    tree_grade.bind('<Double-1>', set_cell_value)
    tree_grade.pack()


"""---------------------------------------------------------------------------

new_grade(tree_grade, msg)是点击评分对话框中的“New”按钮触发的方法，
会在对话框表格中添加一条评分数据，
事件自动设置评分时间为当前时间，当然也可以修改。
new_grade (tree_grade, msg) is a method triggered
by clicking the "New" button in the grading dialog box,
A scoring data is added to the dialog table,
The event automatically sets the scoring time to the current time,
of course, it can also be modified."""


def new_grade(tree_grade, msg):
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    value = {'date': now_time, 'grade': '', 'score': ''}
    tree_grade.insert('', "end", values=(now_time,
                                         "Double click to edit",
                                         "Double click to edit"))
    tree_grade.update()
    # 加入到message列表变量里面，为后来修改准备
    msg.append(value)


"""---------------------------------------------------------------------------

fetch(entries)函数将用户输入的信息转化为字典，
并记录用户有几个输入框没有没有填写。
该函数返回含有填入餐厅信息的字典和记录空文本框的数量。
The fetch (entries) function
converts the information entered by the user into a dictionary,
And record that the user has several input boxes that are not filled out.
This function returns the number of empty text boxes
containing a dictionary filled with restaurant information."""


def fetch(entries):
    empty_flag = 0
    dist = {}
    for entry in entries:
        field = entry[0]
        if field == "coord":
            # 坐标获得的是之前存储的两个entry对象列表，所以这里要取两个
            # The coordinates obtained are
            # the list of the two entry objects stored before,
            # so we need to take two
            text = [entry[1][0].get(), entry[1][1].get()]
            if text == ['', '']:  # 判断用户输入信息是否为空
                empty_flag += 1
        else:
            text = entry[1].get()
            if text == '':  # 判断用户输入信息是否为空
                empty_flag += 1
        dist[field] = text
    return dist, empty_flag


"""---------------------------------------------------------------------------

makeform(root, fields_name, fields, init_value)函数
会将许多文本框布局在对话框中，
更新操作和新建操作弹出的对话框都会调用这个函数。
更新操作时，将用户选中的一条信息保存，通过init_value参数传给makeform()函数。
这个函数会根据init_value参数，初始化文本框中的信息。
新建操作时，将文本框布局。
该函数返回的（key名，entry对象）的列表。
makeform (root, fields_name, fields, init_value) functions
Many text boxes are laid out in dialog boxes,
This function will be called in the dialog box
popped up by the update operation and the new operation.
During the update operation,
a piece of information selected by the user is saved
and passed to the makeform () function through the init_value parameter.
This function initializes the information
in the text box based on the init_value parameter.
Layout the text box when creating a new operation.
This function returns a list of (key names, entry objects)."""


def makeform(root, fields_name, fields, init_value):
    entries = []
    for field_name, field in zip(fields_name, fields):
        row = Frame(root)
        lab = Label(row, width=15, relief=RIDGE,
                    text=field_name, anchor='center',
                    bg="#0096E6", fg="white")

        if field_name == "Coord":
            lab.pack(side=LEFT, ipady=5)
            lab_coord_longitude = Label(row, text="Longitude:",
                                        relief=RIDGE, anchor='center')
            lab_coord_longitude.pack(side=LEFT, ipady=5)
            if init_value == '':  # 在新建餐厅时，不需给输入框附初值，则为空
                temp_longitude = ''
            else:
                temp_longitude = StringVar()
                if init_value[field]:
                    temp_longitude.set(init_value[field][0])
                else:
                    temp_longitude.set('')
            ent_longitude = Entry(row, textvariable=temp_longitude, width=5)
            ent_longitude.pack(side=LEFT, expand=YES, fill=X, ipady=5)

            lab_coord_latitude = Label(row, text="Latitude:",
                                       relief=RIDGE, anchor='center')
            lab_coord_latitude.pack(side=LEFT, ipady=5)
            if init_value == '':  # 在新建餐厅时，不需给输入框附初值，则为空
                temp_latitude = ''
            else:
                temp_latitude = StringVar()
                if init_value[field]:
                    temp_latitude.set(init_value[field][1])
                else:
                    temp_longitude.set('')
            ent_latitude = Entry(row, textvariable=temp_latitude, width=5, )
            ent_latitude.pack(side=RIGHT, expand=YES, fill=X, ipady=5)
            # 把经度和纬度这两个entry对象放在一个列表中，在后面取出来
            ent = [ent_longitude, ent_latitude]
        else:
            temp = StringVar()
            if init_value == '':  # 在新建餐厅时，不需给输入框附初值，则为空
                temp = ''
            else:
                temp.set(init_value[field])
            ent = Entry(row, textvariable=temp)
            ent.pack(side=RIGHT, expand=YES, fill=X, ipady=5)
            lab.pack(side=LEFT, ipady=5)
        row.pack(side=TOP, fill=X, padx=5, pady=5)
        entries.append((field, ent))
    return entries


"""---------------------------------------------------------------------------

数据规范化处理：
format_data(restaurant_info)函数会在open_set_up_dialog()方法中调用，
这个函数处理用户填入的信息，将其数据格式与数据库中的数据格式统一。
该函数返回统一格式的数据。
Data normalization:
The format_data (restaurant_info) function
is called in the open_set_up_dialog () method,
This function processes the information entered by the user
and unifies its data format with the data format in the database.
This function returns data in a uniform format."""


def format_data(restaurant_info):
    format_info = {"address": {"building": "",
                               "coord": [],
                               "street": "",
                               "zipcode": ""},
                   "borough": "",
                   "cuisine": "",
                   "grades": [],
                   "name": "",
                   "restaurant_id": ""}
    for info in restaurant_info:
        if info == "building" or \
                info == "coord" or \
                info == "street" or \
                info == "zipcode":
            format_info["address"][info] = restaurant_info[info]
        else:
            format_info[info] = restaurant_info[info]
    return format_info


'''---------------------------------------------------------------------------

set_up_form_dialog(tree, dist_for_refresh)函数是用户点击主界面的“Set up”时，
会弹出填写信息的对话框的方法。
The set_up_form_dialog (tree, dist_for_refresh) function
is when the user clicks "Set up" on the main interface,
the dialog box method will pop up to fill in the information.'''


def set_up_form_dialog(tree, dist_for_refresh):
    top = Toplevel()
    top.title('Information OF My Restaurant')
    # 设置为模式对话框
    top.grab_set()
    # 让对话框获取焦点
    top.focus_set()

    width = 500
    height = 400
    screenwidth = top.winfo_screenwidth()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, 100)
    top.geometry(size)
    top.resizable(width=False, height=False)

    fields_name = ('Restaurant ID', 'Name',
                   'Building', 'Coord', 'Street', 'Zipcode',
                   'Borough', 'Cuisine')
    fields = ('restaurant_id', 'name',
              'building', 'coord', 'street', 'zipcode',
              'borough', 'cuisine')
    ents = makeform(top, fields_name, fields, '')
    b1 = Button(top, text='Save',
                command=(lambda:
                         open_set_up_dialog(top, ents, tree, dist_for_refresh)))
    b1.pack(side=LEFT, padx=100, pady=5)
    b2 = Button(top, text='Cancel', command=top.destroy)
    b2.pack(side=RIGHT, padx=100, pady=5)


"""---------------------------------------------------------------------------

在新建新餐厅时，填写信息后会弹出的对话框。
如果用户没有填写“Restaurant ID”项，会弹出提示框提示用户此为必填项。
因为“Restaurant ID”的唯一性，如果用户填写的“Restaurant ID”已在后台存在，
则会弹出提示框提示用户填写的“Restaurant ID”已存在。
当用户填写信息满足要求，会进行保存，插入到后台数据库。
When creating a new restaurant,
a dialog box will pop up after filling in the information.
If the user does not fill in the "Restaurant ID" item,
a prompt box will pop up to remind the user that this is a required item.
Because the "Restaurant ID" is unique,
if the "Restaurant ID" filled in by the user already exists in the background,
a prompt box will pop up to
remind the user that the "Restaurant ID" filled in already exists.
When the user fills in the information to meet the requirements,
it will be saved and inserted into the background database."""


def open_set_up_dialog(root, entries, tree, dist_for_refresh):
    restaurant_info = fetch(entries)[0]
    empty_flag = fetch(entries)[1]
    # 如果用户没有填restaurant_id，给出提示
    if restaurant_info["restaurant_id"] == '':
        showwarning(title="Warning",
                    message="\"Restaurant ID\" is required!")
    # 判断用户有没有输入餐厅的信息
    elif empty_flag == 8:  # 如果为空，弹出“提示用户填入信息”
        # 使用dialog.Dialog创建对话框
        d = dialog.Dialog(root,  # 设置该对话框所属的窗口
                          {'title': 'Warning',  # 标题
                           'text': "You have not filled in"
                                   "any information yet! \n"
                                   "Can't save!?",  # 内容
                           'bitmap': 'warning',  # 图标
                           'default': 0,  # 设置默认选中项
                           # strings选项用于设置按钮
                           'strings': ('Return', 'Exit')})
        if d.num == 1:  # 点击退出按钮
            root.destroy()
    else:
        # 查出数据库里的所有restaurant_id，判断是否与用户将要创建的重复
        restaurant_id_list = []
        for item in get_collection().find():
            restaurant_id_list.append(item["restaurant_id"])
        if restaurant_info["restaurant_id"] in restaurant_id_list:
            showinfo(title="Tip",
                     message="\"Restaurant ID\" already exists!")
        else:
            # 处理数据
            # 插入到mongoDB数据库
            fd = format_data(restaurant_info)
            x = get_collection().insert_one(fd)
            # 获得该对象包含的 inserted_id 属性，它是插入文档的 id 值
            fd["_id"] = x.inserted_id
            refresh_tree_after_set(tree, fd, dist_for_refresh)
            if x:
                print("Inserted successfully!")
            else:
                print("Insert error!")
            root.destroy()


'''---------------------------------------------------------------------------

update_form_dialog(values, tree)函数是用户点击主界面的“Update”时，
会弹出修改信息的对话框的方法。
The update_form_dialog (values, tree) function is
when the user clicks "Update" on the main interface,
a dialog box method will pop up to modify the information.'''


def update_form_dialog(values, tree):
    top = Toplevel()
    top.title('Information OF This Restaurant')
    # 设置为模式对话框
    top.grab_set()
    # 让对话框获取焦点
    top.focus_set()

    width = 500
    height = 350
    screenwidth = top.winfo_screenwidth()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, 100)
    top.geometry(size)
    top.resizable(width=False, height=False)

    fields_name = ('Name',
                   'Building', 'Coord', 'Street', 'Zipcode',
                   'Borough', 'Cuisine')
    fields = ('name',
              'building', 'coord', 'street', 'zipcode',
              'borough', 'cuisine')
    # 获取选中的餐厅的数据信息
    init_value = {}
    for key in values:
        one_init = StringVar()
        one_init.set(values[key])
        if key == "address":
            init_value["building"] = values[key]["building"]
            init_value["coord"] = values[key]["coord"]
            init_value["street"] = values[key]["street"]
            init_value["zipcode"] = values[key]["zipcode"]
        else:
            init_value[key] = values[key]
    id = init_value["_id"]
    ents = makeform(top, fields_name, fields, init_value)
    b1 = Button(top, text='Save',
                command=(lambda: open_update_dialog(top, ents, id, tree)))
    b1.pack(side=LEFT, padx=100, pady=5)
    b2 = Button(top, text='Cancel', command=top.destroy)
    b2.pack(side=RIGHT, padx=100, pady=5)


"""---------------------------------------------------------------------------

open_update_dialog(root, entries, id, tree)函数会在
update_form_dialog(values, tree)函数中被调用。
当用户点击对话框中的“Save”按钮后，
该函数判断用户填写的信息是否满足要求，
如果不满足，弹出提示框提示；
如果满足，进行保存。
open_update_dialog (root, entries, id, tree)
update_form_dialog (values, tree) is called.
When the user clicks the "Save" button in the dialog,
This function determines
whether the information filled in by the user meets the requirements,
If not, a prompt box will pop up;
If so, save it."""


def open_update_dialog(root, entries, id, tree):
    restaurant_info = fetch(entries)[0]
    # 获得用户填了多少信息
    empty_flag = fetch(entries)[1]
    # 判断用户有没有输入餐厅的信息
    if empty_flag == 7:  # 如果为空，弹出“提示用户填入信息”
        # 使用dialog.Dialog创建对话框
        d = dialog.Dialog(root,  # 设置该对话框所属的窗口
                          {'title': 'Warning',  # 标题
                           'text': "You change all the"
                                   "information to empty! \n"
                                   "Can't save!?",  # 内容
                           'bitmap': 'warning',  # 图标
                           'default': 0,  # 设置默认选中项
                           'strings': ('Return', 'Exit')})  # strings选项用于设置按钮
        if d.num == 1:  # 点击退出按钮
            root.destroy()
    else:
        my_query = {"_id": ObjectId(id)}
        # 处理数据
        fd = format_data(restaurant_info)
        # 因为没有对"restaurant_id"字段进行修改，则在修改信息里将其删除
        del fd["restaurant_id"]
        refresh_tree_after_update(tree, fd)
        new_values = {"$set": fd}
        # 在mongoDB数据库中进行修改
        x = get_collection().update_one(my_query, new_values)
        if x:
            print("Updated successfully!")
        else:
            print("Update error!")
        root.destroy()


'''---------------------------------------------------------------------------

refresh_tree_after_update(tree, updated_value)函数会在修改restaurant信息后，
及时更新主界面的treeview表格数据。
The refresh_tree_after_update (tree, updated_value) function
will modify the restaurant information,
Update the treeview table data of the main interface in time.'''


def refresh_tree_after_update(tree, updated_value):
    # 判断餐厅有无坐标信息
    if '' in updated_value["address"]["coord"] or '' in get_coord():
        str_dit = "unknown"
    else:
        dit = geodistance(get_coord()[0],
                          get_coord()[1],
                          updated_value["address"]["coord"][0],
                          updated_value["address"]["coord"][1])
        str_dit = str(dit) + " km"
    tree.set(tree.selection(),
             column="name",
             value=updated_value["name"])
    tree.set(tree.selection(),
             column="building",
             value=updated_value["address"]["building"])
    tree.set(tree.selection(),
             column="coord",
             value=updated_value["address"]["coord"])
    tree.set(tree.selection(),
             column="street",
             value=updated_value["address"]["street"])
    tree.set(tree.selection(),
             column="zipcode",
             value=updated_value["address"]["zipcode"])
    tree.set(tree.selection(),
             column="borough",
             value=updated_value["borough"])
    tree.set(tree.selection(),
             column="cuisine",
             value=updated_value["cuisine"])
    tree.set(tree.selection(),
             column="distance",
             value=str_dit)


"""---------------------------------------------------------------------------

refresh_tree_after_set(tree, set_value, dist_for_refresh)函数会在新建餐厅之后，
判断插入的数据是否满足搜索框的条件，
如果满足，就会立即显示在主界面的treeview表格中。
如果不满足，就不显示在当前搜索条件下的表格中。
The refresh_tree_after_set (tree, set_value, dist_for_refresh) function will
Determine whether the inserted data meets the conditions of the search box,
If it is satisfied,
it will be immediately displayed in the treeview table of the main interface.
If not,
it is not displayed in the table under the current search conditions."""


def refresh_tree_after_set(tree, set_value, dist_for_refresh):
    flag = 0
    judge_dist = {"name": set_value["name"],
                  "address.street": set_value["address"]["street"],
                  "address.zipcode": set_value["address"]["zipcode"]
                  }
    if dist_for_refresh:  # 查询条件非空
        for key in dist_for_refresh:
            if dist_for_refresh[key] == judge_dist[key]:
                flag += 1
        if flag == len(dist_for_refresh):  # 表示都满足搜索条件
            print("refreshed successfully")
            if '' in set_value["address"]["coord"]:  # 判断餐厅有无坐标信息
                str_dit = "unknown"
            else:
                dit = geodistance(get_coord()[0],
                                  get_coord()[1],
                                  set_value["address"]["coord"][0],
                                  set_value["address"]["coord"][1])
                str_dit = str(dit) + " km"
            tree.insert('', 0, values=(set_value["restaurant_id"],
                                           set_value["name"],
                                           str(len(set_value["grades"]))
                                           + " records",
                                           set_value["address"]["building"],
                                           set_value["address"]["coord"],
                                           set_value["address"]["street"],
                                           set_value["address"]["zipcode"],
                                           set_value["borough"],
                                           set_value["cuisine"],
                                           str_dit,
                                           set_value["_id"]))


"""---------------------------------------------------------------------------

open_import_dialog()函数会在用户点击主界面的“Import”按钮后被调用。
弹出对话框，将文本框和按钮布局。
The open_import_dialog () function will be called
after the user clicks the "Import" button on the main interface.
A dialog box pops up to lay out text boxes and buttons."""


def open_import_dialog():
    top = Toplevel()
    top.title('Create Database')
    # 设置为模式对话框
    top.grab_set()
    # 让对话框获取焦点
    top.focus_set()

    width = 400
    height = 300
    screenwidth = top.winfo_screenwidth()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, 100)
    top.geometry(size)
    top.resizable(width=False, height=False)

    fields = ('Database Name', 'Collection', 'JSON File', 'Coord')
    ents = make_import_form(top, fields)
    b1 = Button(top, text='Create Database',
                command=(lambda: create_database(top, ents)))
    b1.pack(side=LEFT, padx=50)
    b3 = Button(top, text='Cancel', command=top.destroy)
    b3.pack(side=RIGHT, padx=50, pady=5)


"""---------------------------------------------------------------------------

make_import_form(root, fields)函数会在open_import_dialog()中被调用。
对文本框和按钮进行布局。
该函数返回的（key名，entry对象）的列表。
The make_import_form (root, fields) function
is called in open_import_dialog ().
Layout text boxes and buttons.
This function returns a list of (key names, entry objects)."""


def make_import_form(root, fields):
    entries = []
    for field in fields:
        row = Frame(root)
        lab = Label(row,
                    width=13,
                    relief=RIDGE,
                    font="Helvetica 14 bold italic",
                    text=field + " :",
                    anchor='center',
                    fg="white",
                    bg="#0096E6")
        if field == "JSON File":
            ent = Entry(row)
            b2 = Button(row,
                        text='Select A File',
                        command=(lambda e=ent: import_json_file(e)))
            b2.pack(side=RIGHT, ipady=2)
            ent.pack(side=RIGHT, expand=YES, fill=X, ipady=6)
        elif field == "Coord":
            lab.pack(side=LEFT)
            # 经度
            lab_coord_longitude = Label(row,
                                        text="Longitude:",
                                        relief=RIDGE,
                                        anchor='center')
            lab_coord_longitude.pack(side=LEFT, ipady=5)
            ent_longitude = Entry(row, width=5)
            ent_longitude.pack(side=LEFT, expand=YES, fill=X, ipady=5)
            # 纬度
            lab_coord_latitude = Label(row,
                                       text="Latitude:",
                                       relief=RIDGE,
                                       anchor='center')
            lab_coord_latitude.pack(side=LEFT, ipady=5)
            ent_latitude = Entry(row, width=5)
            ent_latitude.pack(side=RIGHT, expand=YES, fill=X, ipady=5)
            # 把经度和纬度这两个entry对象放在一个列表中，在后面取出来
            ent = [ent_longitude, ent_latitude]
        else:
            ent = Entry(row)
            ent.pack(side=RIGHT, expand=YES, fill=X, ipady=6)
        lab.pack(side=LEFT)
        row.pack(side=TOP, fill=X, padx=5, pady=10)
        entries.append((field, ent))
    return entries


"""---------------------------------------------------------------------------

fetch_import_form(entries)函数会在create_database(root, entries)函数中被调用。
该函数返回含有填入的数据库信息的字典。
The fetch_import_form (entries) function
is called in the create_database (root, entries) function.
This function
returns a dictionary containing the filled database information."""


def fetch_import_form(entries):
    dist = {}
    for entry in entries:
        field = entry[0]
        if field == 'Coord':
            # 坐标获得的是之前存储的两个entry对象列表，所以这里要取两个
            text = [entry[1][0].get(), entry[1][1].get()]
        else:
            text = entry[1].get()
        if text != '':
            dist[field] = text
    return dist


"""---------------------------------------------------------------------------

import_json(entry)函数会在make_import_form(root, fields)函数中被调用。
当点击“Import”对话框中的“Select A File”按钮后调用该函数。
弹出“选择文件”的对话框，将文件路径赋值给全局变量imported_json中。
The import_json (entry) function
is called in the make_import_form (root, fields) function.
This function is called
when the "Select A File" button in the "Import" dialog box is clicked.
The "Select File" dialog box is displayed,
and the file path is assigned to the global variable imported_json."""
imported_json = ''


def import_json_file(entry):
    print("Importing")
    global imported_json
    open_file = askopenfile(title="Please select a JSON file to import",
                            filetypes=[("JSON文件", "*.json")])
    if open_file:
        temp = StringVar()
        temp.set(open_file.name.split('/')[-1])
        entry.configure(textvariable=temp)
        imported_json = open_file


"""---------------------------------------------------------------------------

create_database(root, entries)函数会在open_import_dialog()函数中被调用。
当点击“Import”对话框中的“Create database”按钮后调用该函数。
判断用户输入信息是否满足要求，
如果满足，则导入文件到相应数据库；
否则，弹出提示框提示用户。
The create_database (root, entries) function
is called in the open_import_dialog () function.
This function is called
when the "Create database" button in the "Import" dialog box is clicked.
Determine whether the user input information meets the requirements,
If so, import the file to the corresponding database;
Otherwise, a prompt box will pop up to prompt the user."""


def create_database(root, entries):
    ents = fetch_import_form(entries)
    # 判断创建数据库必要的信息有没有填
    if "Database Name" in ents.keys() and\
            "Collection" in ents.keys() and\
            "JSON File" in ents.keys():
        # 判断用户填不填坐标
        if judge_coord(root, ents['Coord']):
            return
        # 将坐标信息存入全局变量
        set_coord(ents['Coord'])
        # 连接数据库
        if judge_database(ents["Database Name"], root):
            return

        col = create_collection(ents["Database Name"], ents["Collection"])
        set_collection(col)
        # 根据文件插入数据到数据库
        for item in imported_json.readlines():
            try:
                json_data = json.loads(item)
                for date in json_data["grades"]:
                    time_stamp = date["date"]["$date"] / 1000
                    time_array = time.localtime(time_stamp)
                    other_style_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                                     time_array)
                    date["date"] = other_style_time
                get_collection().insert_one(json_data)
            except Exception as e:
                return showerror(title="Error",
                                 message="The file format is not correct!"
                                         + str(e))
        imported_json.close()
        print("Import successfully")
        showinfo(title="Tip",
                 message="Import successfully")
        root.destroy()
    else:
        showwarning(title="Warning",
                    message="Please fill"
                            "all the information about the database!")


"""---------------------------------------------------------------------------

judge_coord(root, coord)函数会在create_database(root, entries)函数中被调用。
判断用户是否输入了坐标。
The judge_coord (root, coord) function
is called in the create_database (root, entries) function.
Determine whether the user has entered coordinates."""


def judge_coord(root, coord):
    # entries[-1]的值是'Coord': ['', '']，以此判断用户有没有填坐标
    if '' in coord:
        d = dialog.Dialog(root,  # 设置该对话框所属的窗口
                          {'title': 'Tip',  # 标题
                           'text': "If you do not fill in the coordinates,\n"
                                   "you will not"
                                   "be able to get your location\n"
                                   "information from other restaurants.\n"
                                   "Do you want to continue?",  # 内容
                           'bitmap': 'question',  # 图标
                           'default': 0,  # 设置默认选中项
                           # strings选项用于设置按钮
                           'strings': ('Continue', 'Return')})
        if d.num == 0:
            return False
        else:
            return True
    else:
        return False


"""---------------------------------------------------------------------------

set_coord(coord)函数会在create_database(root, entries)函数中被调用。
给全局变量my_coord赋用户填入的坐标值。
The set_coord (coord) function
is called in the create_database (root, entries) function.
The global variable my_coord
is assigned the coordinate value entered by the user."""


def set_coord(coord):
    global my_coord
    my_coord = coord


"""---------------------------------------------------------------------------

其他文件调用get_coord()函数得到用户填入的坐标值。
Other files call the get_coord () function
to get the coordinate values entered by the user."""


def get_coord():
    return my_coord


"""---------------------------------------------------------------------------

geodistance(lng1, lat1, lng2, lat2)函数计算两点间距离（km）。
geodistance (lng1, lat1, lng2, lat2) function
calculates the distance (km) between two points."""


def geodistance(lng1, lat1, lng2, lat2):  # (经度， 纬度)
    # 经纬度转换成弧度
    lng1, lat1, lng2, lat2 = map(radians,
                                 [float(lng1),
                                  float(lat1),
                                  float(lng2),
                                  float(lat2)])
    dlon = lng2-lng1
    dlat = lat2-lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    distance = 2 * asin(sqrt(a)) * 6371 * 1000   # 地球平均半径，6371km
    distance = round(distance/1000, 3)
    return distance

