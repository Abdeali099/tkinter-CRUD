from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Treeview
import sqlite3

# variables
input_data = []
selected_router_id = 0
selected_tree_row_index = ""


class Database:
    # Queries
    fetch_all_data_query = "SELECT * FROM routers;"
    insert_query = "INSERT INTO routers VALUES (?,?,?,?,?);"
    update_query = "UPDATE routers SET hostname=? , brand=? , ram=? , flash=? WHERE id = ?;"
    delete_query = "DELETE FROM routers WHERE id = ?;"
    hostname_search_query = "SELECT * FROM routers WHERE hostname LIKE ? ;"

    # run only for once
    def __init__(self, database_name):
        self.database_name = database_name
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS 
            routers (id INTEGER PRIMARY KEY, 
                     hostname TEXT, 
                     brand TEXT, 
                     ram Text, 
                     flash Text)
            """)

        self.connection.commit()

    # Populate data at window loading / Opening
    def fetch_all_data(self):

        initial_data = self.cursor.execute(Database.fetch_all_data_query)
        routers_data = initial_data.fetchall()

        if len(routers_data) != 0:
            for data in routers_data:
                router_tree_view.insert('', 'end', values=data)

    # ---- CRUD Operation Methods (Database)  ---- #

    # 1 : Insert Data
    def insert(self, valid_input_data):

        try:
            # save to database
            self.cursor.execute(Database.insert_query, valid_input_data)
            self.connection.commit()

            # save to tree
            router_tree_view.insert('', 'end', values=valid_input_data)

        except Exception as e:
            print('Error in saving data : ', e)
            messagebox.showerror('Error', 'Error in saving data,try again...')

    # 2 : Update Data
    def update(self, valid_input_data):
        try:
            # update to database
            update_values = valid_input_data[1::]
            update_values.append(valid_input_data[0])

            self.cursor.execute(Database.update_query, update_values)
            self.connection.commit()

            # update tree
            router_tree_view.item(selected_tree_row_index, values=valid_input_data)

        except Exception as e:
            print('Error in updating data : ', e)
            messagebox.showerror('Error', 'Error in updating data,try again...')

    # 3 : Delete Data
    def delete(self, delete_id):

        try:
            # delete from database
            self.cursor.execute(Database.delete_query, [delete_id])
            self.connection.commit()

            # delete temporary
            router_tree_view.delete(selected_tree_row_index)

        except Exception as e:
            print('Error in deleting data : ', e)
            messagebox.showerror('Error', 'Error in deleting data,try again...')

    # 4 : search hostname
    def search_by_hostname(self, search_hostname):
        initial_data = self.cursor.execute(Database.hostname_search_query, ('%' + search_hostname + '%',))
        routers_data = initial_data.fetchall()

        if len(routers_data) != 0:
            for data in routers_data:
                router_tree_view.insert('', 'end', values=data)

    def search_by_query(self, search_query):
        initial_data = self.cursor.execute(search_query)
        routers_data = initial_data.fetchall()

        if len(routers_data) != 0:
            for data in routers_data:
                router_tree_view.insert('', 'end', values=data)


# ---- CRUD Operation Functions ---- #

def add_router():
    isValid = is_inputs_valid()

    if isValid:
        database.insert(input_data)
        clear_input_fields()


def update_router():
    isValid = is_inputs_valid()

    if isValid:
        input_data[0] = selected_router_id
        database.update(input_data)


def remove_router():
    isValid = is_inputs_valid()

    if isValid:
        database.delete(selected_router_id)
        clear_input_fields()


# ---- Search queries Functions ---- #

def search_by_hostname():
    search_hostname = entry_search_by_hostname.get()

    if search_hostname == '':
        messagebox.showerror('Error', 'Please provide proper hostname')
        return

    clear_table_row()

    database.search_by_hostname(search_hostname)


def execute_query():

    clear_table_row()

    database.search_by_query(entry_search_by_query.get())


def search_by_queries():
    search_query = entry_search_by_query.get()

    if search_query == '':
        messagebox.showerror('Error', 'Please provide proper Query')
        return

    clear_table_row()

    database.search_by_query(search_query)


# ---- Helper Functions | Functionality ---- #

def is_inputs_valid() -> bool:
    global input_data

    try:
        new_id = int(entry_id.get())

        input_data = [new_id, entry_hostname.get(), entry_brand.get(), entry_ram.get(),
                      entry_flash.get()]

        if '' in input_data:
            messagebox.showerror('Error', 'Please provide proper inputs')
            return False

    except Exception as e:
        print("Value error in selection : ", e)
        messagebox.showerror('Error', 'Please provide proper inputs')
        return False

    return True


def clear_input_fields():
    entry_id.delete(0, END)
    entry_hostname.delete(0, END)
    entry_brand.delete(0, END)
    entry_ram.delete(0, END)
    entry_flash.delete(0, END)


def select_row_of_router(event):
    global selected_router_id
    global selected_tree_row_index

    try:

        selected_tree_row_index = router_tree_view.selection()[0]

        selected_item = router_tree_view.item(selected_tree_row_index)['values']

        selected_router_id, selected_hostname, selected_brand, selected_ram, selected_flash = selected_item

        entry_id.delete(0, END)
        entry_id.insert(0, selected_router_id)

        entry_hostname.delete(0, END)
        entry_hostname.insert(0, selected_hostname)

        entry_brand.delete(0, END)
        entry_brand.insert(0, selected_brand)

        entry_ram.delete(0, END)
        entry_ram.insert(0, selected_ram)

        entry_flash.delete(0, END)
        entry_flash.insert(0, selected_flash)

        return

    except Exception as e:
        print("Error in selection row  : ", e)


def clear_queries():
    entry_search_by_query.delete(0, END)
    entry_search_by_query.insert(0, "SELECT * FROM routers WHERE ")

    entry_search_by_hostname.delete(0, END)

    clear_table_row()

    database.fetch_all_data()


def clear_table_row():
    for item in router_tree_view.get_children():
        router_tree_view.delete(item)


# -------------------- Initialize DataBase ------------------- #
database = Database('routers.db')

# -------------------- GUI Application ------------------- #
main_window = Tk()
main_window.title('Router Manager')

# ----- Frame 1 :  Search Frame ----- #

frame_search = Frame(main_window)
frame_search.grid(row=0, column=0)

# --> Search by Host Name

lbl_search_by_hostname = Label(frame_search, text='Search by Host-Name', font=('Fira Code', 12, 'bold'), pady=20)
lbl_search_by_hostname.grid(row=0, column=0, sticky=W, padx=10)

entry_search_by_hostname = Entry(frame_search, width=40)
entry_search_by_hostname.grid(row=0, column=1, padx=10)

btn_search_by_hostname = Button(frame_search, text='Search', width=12, command=search_by_hostname)
btn_search_by_hostname.grid(row=0, column=2)

clear_search_query = Button(frame_search, text='Clear', width=12, command=clear_queries)
clear_search_query.grid(row=0, column=3, padx=15)

# --> Search by Query

lbl_search_by_query = Label(frame_search, text='Search by Query', font=('Fira Code', 12, 'bold'), pady=20)
lbl_search_by_query.grid(row=1, column=0, sticky=W, padx=10)

entry_search_by_query = Entry(frame_search, width=40)
entry_search_by_query.insert(0, "SELECT * FROM routers WHERE ")
entry_search_by_query.grid(row=1, column=1, padx=10)

btn_search_by_query = Button(frame_search, text='Fire Query', width=12, command=execute_query)
btn_search_by_query.grid(row=1, column=2)

clear_search_query = Button(frame_search, text='Clear', width=12, command=clear_queries)
clear_search_query.grid(row=1, column=3, padx=15)

# ----- Frame 2 :  Field's Frame ----- #

frame_fields = Frame(main_window)
frame_fields.grid(row=1, column=0)

# -> Id
label_id = Label(frame_fields, text='Id', font=('Fira Code', 12, 'bold'))
label_id.grid(row=0, column=0, sticky=E)

entry_id = Entry(frame_fields, width=50)
entry_id.grid(row=0, column=1, sticky=W, padx=15, pady=15, columnspan=5)

# -> Host  - Name
label_hostname = Label(frame_fields, text='Host-Name', font=('Fira Code', 12, 'bold'))
label_hostname.grid(row=1, column=0, sticky=E)

entry_hostname = Entry(frame_fields)
entry_hostname.grid(row=1, column=1, sticky=W, padx=15)

# -> BRAND
label_brand = Label(frame_fields, text='Brand', font=('Fira Code', 12, 'bold'))
label_brand.grid(row=1, column=2, sticky=E)

entry_brand = Entry(frame_fields)
entry_brand.grid(row=1, column=3, sticky=W, padx=15)

# -> RAM
label_ram = Label(frame_fields, text='RAM', font=('Fira Code', 12, 'bold'))
label_ram.grid(row=2, column=0, sticky=E)

entry_ram = Entry(frame_fields)
entry_ram.grid(row=2, column=1, sticky=W, padx=15)

# -> FLASH
label_flash = Label(frame_fields, text='Flash', font=('Fira Code', 12, 'bold'), pady=20)
label_flash.grid(row=2, column=2, sticky=E)

entry_flash = Entry(frame_fields)
entry_flash.grid(row=2, column=3, sticky=W, padx=15)

# ----- Frame 3 :  CRUD Operation Buttons  ----- #

frame_crud_btns = Frame(main_window)
frame_crud_btns.grid(row=3, column=0)

add_btn = Button(frame_crud_btns, text='Add Router', width=12, command=add_router)
add_btn.grid(row=0, column=0, padx=15)

remove_btn = Button(frame_crud_btns, text='Remove Router', width=12, command=remove_router)
remove_btn.grid(row=0, column=1, padx=15)

update_btn = Button(frame_crud_btns, text='Update Router', width=12, command=update_router)
update_btn.grid(row=0, column=2, padx=15)

clear_btn = Button(frame_crud_btns, text='Clear Input', width=12, command=clear_input_fields)
clear_btn.grid(row=0, column=3, padx=15)

# ----- Frame 4 :  Available router frame  ----- #

frame_available_router = Frame(main_window)
frame_available_router.grid(row=4, column=0, columnspan=4, rowspan=6, pady=20, padx=20)

# -> Creating tree view (Table)

columns = ['id', 'Hostname', 'Brand', 'Ram', 'Flash']
router_tree_view = Treeview(frame_available_router, columns=columns, show="headings")

for col in columns:
    router_tree_view.column(col, width=120, anchor=CENTER)
    router_tree_view.heading(col, text=col)

router_tree_view.bind('<<TreeviewSelect>>', select_row_of_router)
router_tree_view.pack(side="left", fill="y")

scrollbar = Scrollbar(frame_available_router, orient='vertical')
scrollbar.configure(command=router_tree_view.yview)
scrollbar.pack(side="right", fill="y")

router_tree_view.config(yscrollcommand=scrollbar.set)

# load already saved data in table
database.fetch_all_data()

# Start program
main_window.mainloop()
