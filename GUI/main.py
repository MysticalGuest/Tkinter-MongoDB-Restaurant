"""***************************************************************************

                                 main.py


***************************************************************************"""

# To run this program, start cmd，
# You need to download and import the pymongo library, bson library,
# math library, json library and time library first.
# and then type:
# python ..path\main.py
# Or run directly through pycharm.


from myfunction import *

"""---------------------------------------------------------------------------

这个.py文件是用Tkinter编写的程序主界面。
主界面的上一部分是可以显示餐厅详细信息的表格；
主界面的写一部分包括了左边的搜索框和右边的执行各功能的按钮。
进入主界面首先需要点击“Import”按钮，将一个.json文件导入数据库。
然后才能进行其他操作。
This .py file is the main interface of the program written in Tkinter.
The previous part of the main interface
is a table that can display restaurant details;
The main part of the main interface includes the search box on the left
and the buttons on the right to perform various functions.
To enter the main interface, you first need to click the "Import" button
to import a .json file into the database.
Then you can do other operations."""


root = tk.Tk()

root.title("My Meituan")

width = 1200
height = 650
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
size = '%dx%d+%d+%d' % (width,
                        height,
                        (screenwidth - width)/2,
                        (screenheight - height)/2)
root.geometry(size)

root.resizable(width=False, height=False)

tk.Label(root,
         text='Welcome to Meituan!',
         font=('times', 24, 'italic'),
         width=100,
         height=1,
         fg="white",
         bg='#0096E6').pack()

frm_top = tk.Frame(root)
frm_top.pack(side=tk.TOP)

frm_mid = tk.Frame(root)
fields_name = ('Name', 'Borough', 'Street', 'Zipcode')
fields = ('name', 'borough', 'address.street', 'address.zipcode')

create_heading(frm_mid)

'''---------------------------------------------------------------------------

表格'''
S = tk.Scrollbar(frm_mid)  # 加滚条
S.pack(side=tk.RIGHT, fill=tk.Y)

# 创建表格对象
tree = ttk.Treeview(frm_mid, yscrollcommand=S.set, height=15, show="headings")
S.config(command=tree.yview)
# 定义列
tree["columns"] = ("restaurant_id", "name", "grades", "building", "coord",
                   "street", "zipcode", "borough", "cuisine", "distance")
# 设置列
tree.column("restaurant_id",
            minwidth=87,
            width=87,
            anchor='center',
            stretch=False)
tree.column("name",
            minwidth=180,
            anchor='center',
            stretch=False)
tree.column("grades",
            minwidth=80,
            width=80,
            anchor='center',
            stretch=False)
tree.column("building",
            minwidth=70,
            width=70,
            anchor='center',
            stretch=False)
tree.column("coord",
            minwidth=180,
            anchor='center',
            stretch=False)
tree.column("street",
            minwidth=180,
            anchor='center',
            stretch=False)
tree.column("zipcode",
            minwidth=70,
            width=70,
            anchor='center',
            stretch=False)
tree.column("borough",
            minwidth=70,
            width=70,
            anchor='center',
            stretch=False)
tree.column("cuisine",
            minwidth=100,
            width=100,
            anchor='center',
            stretch=False)
tree.column("distance",
            minwidth=100,
            width=100,
            anchor='center',
            stretch=False)

# 设置显示的表头名
tree.heading("restaurant_id", text="Restaurant ID")
tree.heading("name", text="Name")
tree.heading("grades", text="Grades")
tree.heading("building", text="Building")
tree.heading("coord", text="Coord")
tree.heading("street", text="Street")
tree.heading("zipcode", text="Zipcode")
tree.heading("borough", text="Borough")
tree.heading("cuisine", text="Cuisine")
tree.heading("distance",
             text="Distance",
             command=lambda: tree_sort_column(tree, "distance", False))

tree.pack()

'''---------------------------------------------------------------------------

双击左键进入编辑'''


def show_grade(event):
    for item in tree.selection():
        item_text = tree.item(item, "values")
    try:
        for item in get_collection().find({"restaurant_id": item_text[0]}):
            msg = item["grades"]
            # item_text[-1]是objectId,用于后面修改grade
            my_table_dialog(msg, item_text[-1])
    except Exception as e:
        print(e)


tree.bind('<Double-1>', show_grade)

frm_mid.pack(side=tk.TOP)


frm_bot = tk.Frame(root)
frm_bot_left = tk.Frame(frm_bot, bg="#BDBDBD")

ents = make_form(frm_bot_left, fields_name, fields)

frm_bot_right = tk.Frame(frm_bot, bg="#007EDC")
frm_bot_right_left = tk.Frame(frm_bot_right, bg="#007EDC")
frm_bot_right_left_left = tk.Frame(frm_bot_right_left, bg="#007EDC")
frm_bot_right_left_right = tk.Frame(frm_bot_right_left, bg="#007EDC")
frm_bot_right_right = tk.Frame(frm_bot_right, bg="#007EDC")

bt = tk.Button(frm_bot_right_left_left,
               text='Search',
               font="Helvetica 16 bold italic",
               activebackground="white",
               command=(lambda: fetch(tree, ents)))
bt.pack(padx=20, pady=15)

bt_import = tk.Button(frm_bot_right_left_left,
                      text='Import',
                      font="Helvetica 16 bold italic",
                      activebackground="white",
                      command=import_json)
bt_import.pack(padx=20, pady=15)

sort_message = "Click on the header of the \"Distance\"" \
               "column to sort each restaurant by distance."
tk_sort_msg = tk.Message(frm_bot_right_left_right, text=sort_message)
tk_sort_msg.config(fg="red", bg='#BECCED', font=('times', 15, 'italic'), width=800)
tk_sort_msg.pack(side=tk.TOP, pady=15)

message = "Click the \"Set Up\" button to start your own restaurant.\n" \
          "Click the \"Update\" button to" \
          "update the information of restaurant.\n" \
          "Click the \"Delete\" button to delete the restaurant.\n" \
          "Click the \"Quit\" button to Exit the software!"
tk_msg = tk.Message(frm_bot_right_left_right, text=message)
tk_msg.config(bg='#BECCED', font=('times', 15, 'italic'), width=800)
tk_msg.pack(side=tk.BOTTOM, pady=15)

bt_new = tk.Button(frm_bot_right_right,
                   text='Set Up',
                   font="Helvetica 16 bold italic",
                   activebackground="white",
                   command=(lambda: set_up(tree, dist_for_refresh)))
bt_new.pack(padx=10, pady=5, ipadx=4)

bt_update = tk.Button(frm_bot_right_right,
                      text='Update',
                      font="Helvetica 16 bold italic",
                      activebackground="white",
                      command=(lambda: update(tree)))
bt_update.pack(padx=10, pady=5)

bt_delete = tk.Button(frm_bot_right_right,
                      text='Delete',
                      font="Helvetica 16 bold italic",
                      activebackground="white",
                      command=(lambda: delete(tree)))
bt_delete.pack(padx=10, pady=5, ipadx=5)

bt_quit = tk.Button(frm_bot_right_right,
                    text='Quit',
                    font="Helvetica 16 bold italic",
                    activebackground="white",
                    command=root.quit)
bt_quit.pack(padx=10, pady=5, ipadx=15)

frm_bot_left.pack(side=tk.LEFT)

frm_bot_right_left_left.pack(side=tk.LEFT)
frm_bot_right_left_right.pack(side=tk.LEFT)
frm_bot_right_left.pack(side=tk.LEFT, padx=10)
frm_bot_right_right.pack(side=tk.RIGHT, padx=10)
frm_bot_right.pack(side=tk.RIGHT)
frm_bot.pack(side=tk.TOP)

root.mainloop()

