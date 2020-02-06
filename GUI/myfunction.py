"""***************************************************************************

                                 myfunction.py


***************************************************************************"""

import tkinter as tk

from mydialog import *

from bson.objectid import ObjectId

from connect import *

"""---------------------------------------------------------------------------

这个.py文件里包含了许多方法。
将会在a2017115146.py文件中被调用。
This .py file contains many methods.
Will be called in a2017115146.py file."""

# 设置这3个值的目的是为了后面插入后，执行刷新表格
dist_for_refresh = {}


def fetch(tree, entries):
    i = 0
    dist = {}
    for entry in entries:
        field = entry[0]
        text = entry[1].get()
        if text != '':
            # regular用于模糊查询
            regular = dict()
            regular["$regex"] = text
            regular["$options"] = "i"
            dist[field] = regular
    del_treeview(tree)
    if get_collection():
        print("Searching")
        # 给第i行添加数据，索引值可重复
        for item in get_collection().find(dist):
            if '' in item["address"]["coord"] or\
                    len(item["address"]["coord"]) == 0 or\
                    '' in get_coord():  # 判断餐厅有无坐标信息
                str_dit = "unknown"
            else:
                dit = geodistance(get_coord()[0],
                                  get_coord()[1],
                                  item["address"]["coord"][0],
                                  item["address"]["coord"][1])
                str_dit = str(dit) + " km"
            # 将唯一字段"_id"作为后面删除特定信息的依据
            tree.insert("", i,
                        values=(item["restaurant_id"],
                                item["name"],
                                str(len(item["grades"])) + " records",
                                item["address"]["building"],
                                item["address"]["coord"],
                                item["address"]["street"],
                                item["address"]["zipcode"],
                                item["borough"],
                                item["cuisine"],
                                str_dit,
                                item["_id"]))
            i += 1
        for key in dist:
            dist_for_refresh.clear()
            # ["$regex"]用于还原数据
            dist_for_refresh[key] = dist[key]["$regex"]
    else:
        showwarning(title="Warning",
                    message="You haven't imported any database"
                            "or the database is empty!")


"""---------------------------------------------------------------------------

make_form(fields_name, fields)函数会将许多文本框布局在主界面左边的搜索框中。
该函数返回的（key名，entry对象）的列表。
The make_form (fields_name, fields) function will
lay out many text boxes in the search box
on the left side of the main interface.
This function returns a list of (key names, entry objects)."""


def make_form(frm_bot_left, fields_name, fields):
    entries = []
    for field_name, field in zip(fields_name, fields):
        row = tk.Frame(frm_bot_left, pady=9, bg="#007EDC")
        lab = tk.Label(row,
                       width=8,
                       font="Helvetica 16 bold italic",
                       text=field_name+" :",
                       anchor='center',
                       fg="white",
                       bg="#007EDC")
        ent = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X, ipady=6)
        entries.append((field, ent))
    return entries


"""---------------------------------------------------------------------------

create_heading(self, )函数对主界面中的treeview表格上添加一个表头，
以保证滚动滚动条时，表头依然存在！
The create_heading (self,) function
adds a table header to the treeview table in the main interface.
To ensure that when the scroll bar is scrolled, the header still exists!"""


def create_heading(self, ):
    # 重新做一个treeview的头，不然滚动滚动条，看不到原先的头！！
    heading_frame = tk.Frame(self)
    heading_frame.pack(fill=tk.X)

    self.columns = ['Restaurant ID', 'Name', 'Grades', 'Address',
                    'Borough', 'Cuisine', 'Distance']
    self.widths = [12, 28, 10, 76, 10, 13, 17]

    # 重建tree的头
    for i in range(len(self.columns)):
        tk.Label(heading_frame,
                 text=self.columns[i],
                 width=self.widths[i],
                 anchor='center',
                 relief=tk.GROOVE).pack(side=tk.LEFT)


"""---------------------------------------------------------------------------

del_treeview(last_tree)
函数会在每次进行搜索后删除上次搜索留在treeview表格中的数据及记录，
因为上次的数据可能不满足这次的搜索条件，
所以上次的数据没必要显示出来，导致数据冗余。
所以会清空上次搜索留下来的信息。
del_treeview (last_tree)
The function deletes the data and records left
in the treeview table from the last search after each search.
Because the previous data may not meet this search criteria,
Therefore, the last data is not necessarily displayed,
resulting in data redundancy.
So the information left over from the last search will be cleared."""


def del_treeview(last_tree):
    x = last_tree.get_children()
    for item in x:
        last_tree.delete(item)


"""---------------------------------------------------------------------------

新建操作：
set_up(tree, dist_for_refresh)函数会判断用户是否已经导入数据库，
如果没有就弹出对话框提示用户，如果已经导入，
就会调用set_up_form_dialog(tree, dist_for_refresh)，
弹出创建餐厅的对话框，开始创建餐厅的操作。
New operation:
The set_up (tree, dist_for_refresh) function
will determine whether the user has imported the database,
If not, a dialog box will pop up to prompt the user.
If it has been imported,
Will call set_up_form_dialog (tree, dist_for_refresh),
The dialog box for creating a restaurant pops up
to start the operation of creating a restaurant."""


def set_up(tree, dist_for_refresh):
    if get_collection():
        set_up_form_dialog(tree, dist_for_refresh)
    else:
        showwarning(title="Warning",
                    message="You haven't imported any database!")


"""---------------------------------------------------------------------------

更新操作：
update(tree)函数会判断用户是否选中了表中的一条数据，如果未选中，
给出提示，如果选中一条数据，就会弹出填写修改信息的窗口。
Update operation:
The update (tree) function will determine whether the user
has selected a piece of data in the table. If it is not selected,
Give a prompt, if you select a piece of data,
a window for filling in the modification information will pop up."""


def update(tree):
    if not tree.selection():  # 元组判空
        showwarning(title="Warning",
                    message="You haven't picked a restaurant yet?!")
    else:
        print("Updating")
        for item in tree.selection():
            item_text = tree.item(item, "values")
        item = get_collection().find({"_id": ObjectId(item_text[-1])})
        value = list(item)[0]
        update_form_dialog(value, tree)  # 将tree传给refresh_tree刷新表格


"""---------------------------------------------------------------------------

删除操作：
delete(tree)函数会判断用户是否选中了表中的一条数据，如果未选中，
给出提示，如果选中一条数据，点击“delete”按钮就会立即删除。
Delete operation:
The delete (tree) function will determine
whether the user has selected a piece of data in the table.
If it is not selected,
Given a prompt, if a piece of data is selected,
clicking the "delete" button will delete it immediately."""


def delete(tree):
    if not tree.selection():  # 元组判空
        showwarning(title="Warning",
                    message="You haven't picked a restaurant yet?!")
    else:
        print("Deleting")
        for item in tree.selection():
            item_text = tree.item(item, "values")
        item = get_collection().remove({"_id": ObjectId(item_text[-1])})
        tree.delete(tree.selection())
        if item:
            showinfo(title="Tip",
                     message="Delete successfully!")
            print("Deleted successfully!")
        else:
            print("Delete error!")


"""---------------------------------------------------------------------------

导入操作：
import_json()函数会在点击“import”按钮后，
弹出填写数据库信息及选择导入文件的窗口。
Import operation:
After import_json () function is clicked,
A window pops up to fill
in the database information and select the import file."""


def import_json():
    open_import_dialog()


"""---------------------------------------------------------------------------

tree_sort_column(tv, col, reverse)函数当点击主界面“Distance”表头时，
会被调用。对每个餐厅的距离进行排序。
tree_sort_column (tv, col, reverse) function
when clicking the "Distance" header on the main interface,
it will be called.
Sort the distance of each restaurant."""


def tree_sort_column(tv, col, reverse):  # Treeview、列名、排列方式
    li = []
    for k in tv.get_children(''):
        if tv.set(k, col)[:-3] != 'unkn':
            li.append((float(tv.set(k, col)[:-3]), k))
    li.sort(reverse=reverse)  # 排序方式
    # rearrange items in sorted positions
    for index, (val, k) in enumerate(li):  # 根据排序后索引移动
        tv.move(k, '', index)
    # 重写标题，使之成为再点倒序的标题
    tv.heading(col, command=lambda: tree_sort_column(tv, col, not reverse))

