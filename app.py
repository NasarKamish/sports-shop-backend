import hmac
import sqlite3
import datetime
from itertools import product

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS, cross_origin
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

db = "e_commerce.db"


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[4], data[5]))
    return new_data


def init_user_table():
    conn = sqlite3.connect(db)
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "Email TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL"
                 ")")
    print("users table created successfully")
    conn.close()


def init_product_table():
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS Product (product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "name TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "date TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "category TEXT NOT NULL"
                     ")")
    print("Product table created successfully.")


def init_comments_table():
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS Comment (comment_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "user_id TEXT NOT NULL,"
                     "comment TEXT NOT NULL,"
                     "stars TEXT NOT NULL,"
                     "date_created TEXT NOT NULL,"
                     "product_id INTEGER NOT NULL,"
                     "FOREIGN KEY (user_id) REFERENCES users (user_id),"
                     "FOREIGN KEY (product_id) REFERENCES Product (product_id))")
    print("Comments table created successfully.")


def init_cart_table():
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS Cart (cart_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "date_created TEXT NOT NULL,"
                     "total_price TEXT NOT NULL,"
                     "user_id TEXT NOT NULL,"
                     "progress TEXT NOT NULL,"
                     "FOREIGN KEY (user_id) REFERENCES users (user_id))"
                     )
    print("Cart table created successfully.")


def init_items_table():
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS Items (items_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "quantity TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "cart_id INTEGER NOT NULL,"
                     "product_id INTEGER NOT NULL,"
                     "FOREIGN KEY (cart_id) REFERENCES Cart (cart_id),"
                     "FOREIGN KEY (product_id) REFERENCES Product (product_id))"
                     )
    print("Item table created successfully.")


init_user_table()
init_product_table()
init_comments_table()
init_cart_table()
init_items_table()
users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
CORS(app)

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
# @jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        begin_name = str(request.data).find('"', 15)
        end_name = str(request.data).find('"', begin_name + 1)
        begin_surname = str(request.data).find('"', end_name + 13)
        end_surname = str(request.data).find('"', begin_surname + 1)
        begin_email = str(request.data).find('"', end_surname + 9)
        end_email = str(request.data).find('"', begin_email + 1)
        begin_username = str(request.data).find('"', end_email + 12)
        end_username = str(request.data).find('"', begin_username + 1)
        begin_password = str(request.data).find('"', end_username + 12)
        end_password = str(request.data).find('"', begin_password + 1)

        first_name = str(request.data)[begin_name + 1:end_name]
        last_name = str(request.data)[begin_surname + 1:end_surname]
        email = str(request.data)[begin_email + 1:end_email]
        username = str(request.data)[begin_username + 1:end_username]
        password = str(request.data)[begin_password + 1:end_password]

        # entered info is correct
        info_val = False
        if first_name != '' and last_name != '' and username != '' and password != '':
            info_val = True
        else:
            info_val = False

        # email validation
        email_val = False

        if email != "":
            try:
                sender_email_id = 'jimmy.local.shop.project@gmail.com'
                receiver_email_id = email
                password_e = "smsSHOP31314"
                subject = "Local Shop Register"
                msg = MIMEMultipart()
                msg['From'] = sender_email_id
                msg['To'] = receiver_email_id
                msg['Subject'] = subject
                body = "You're account has been verified"
                msg.attach(MIMEText(body, 'plain'))
                text = msg.as_string()
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(sender_email_id, password_e)
                s.sendmail(sender_email_id, receiver_email_id, text)
                s.quit()
                email_val = True
            except:
                email_val = False
        else:
            # response["message"] = "Invalid email"
            # response["status_code"] = 201
            return response

        if email_val and info_val:
            with sqlite3.connect(db) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users("
                               "first_name,"
                               "last_name,"
                               "email,"
                               "username,"
                               "password) VALUES(?, ?, ?, ?, ?)", (first_name, last_name, email, username, password))
                conn.commit()
                response["message"] = "success"
                response["status_code"] = 201
    return response


@app.route('/create-product/', methods=["POST"])
# @jwt_required()
def create_product():
    response = {}

    if request.method == "POST":

        begin_name = str(request.data).find('"', 18)
        end_name = str(request.data).find('"', begin_name + 1)
        begin_price = str(request.data).find('"', end_name + 17)
        end_price = str(request.data).find('"', begin_price + 1)
        begin_description = str(request.data).find('"', end_price + 16)
        end_description = str(request.data).find('"', begin_description + 1)
        begin_category = str(request.data).find('"', end_description + 13)
        end_category = str(request.data).find('"', begin_category + 1)

        product_name = str(request.data)[begin_name + 1:end_name]
        product_price = str(request.data)[begin_price + 1:end_price]
        description = str(request.data)[begin_description + 1:end_description]
        category = str(request.data)[begin_category + 1:end_category]

        date_created = datetime.datetime.now()

        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Product ("
                           "name,"
                           "price,"
                           "date,"
                           "description,"
                           "category"
                           ") VALUES(?, ?, ?, ?, ?)", (product_name, product_price, date_created, description, category))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Product added successfully"
        return response


@app.route('/create-cart/', methods=["POST"])
# @jwt_required()
def create_cart():
    response = {}

    if request.method == "POST":
        print(request.data)

        begin_price = str(request.data).find('"', 17)
        end_price = str(request.data).find('"', begin_price + 1)
        begin_progress = str(request.data).find('"', end_price + 13)
        end_progress = str(request.data).find('"', begin_progress + 1)
        begin_user = str(request.data).find('"', end_progress + 12)
        end_user = str(request.data).find('"', begin_user + 1)

        total_price = str(request.data)[begin_price + 1:end_price]
        progress = str(request.data)[begin_progress + 1:end_progress]
        user_id = str(request.data)[begin_user + 1:end_user]

        date_created = datetime.datetime.now()

        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Cart ("
                           "date_created,"
                           "total_price,"
                           "progress,"
                           "user_id"
                           ") VALUES(?, ?, ?, ?)", (date_created, total_price, progress, user_id))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Cart added successfully"
        return response


@app.route('/create-item/', methods=["POST"])
# @jwt_required()
def create_item():
    response = {}

    if request.method == "POST":

        begin_quantity = str(request.data).find('"', 14)
        end_quantity = str(request.data).find('"', begin_quantity + 1)
        begin_price = str(request.data).find('"', end_quantity + 9)
        end_price = str(request.data).find('"', begin_price + 1)
        begin_cart = str(request.data).find('"', end_price + 11)
        end_cart = str(request.data).find('"', begin_cart + 1)
        begin_product = str(request.data).find('"', end_cart + 15)
        end_product = str(request.data).find('"', begin_product + 1)

        quantity = str(request.data)[begin_quantity + 1:end_quantity]
        price = str(request.data)[begin_price + 1:end_price]
        cart_id = str(request.data)[begin_cart + 1:end_cart]
        product_id = str(request.data)[begin_product + 1:end_product]

        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Items ("
                           "quantity,"
                           "price,"
                           "cart_id,"
                           "product_id"
                           ") VALUES(?, ?, ?, ?)", (quantity, price, cart_id, product_id))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Item added successfully"
        return response


@app.route('/get-comments/', methods=["GET"])
def get_comments():
    response = {}
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Comment")

        comments = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = comments
    return response


@app.route('/get-cart/', methods=["GET"])
def get_cart():
    response = {}
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Cart")

        carts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = carts
    return response


@app.route('/get-items/', methods=["GET"])
def get_items():
    response = {}
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Items")

        items = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = items
    return response


@app.route("/delete-comment/<int:comment_id>/")
# @jwt_required()
def delete_comment(comment_id):
    response = {}
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Comment WHERE comment_id=" + str(comment_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Comment deleted successfully."
    return response
    

@app.route('/create-comment/', methods=["POST"])
# @jwt_required()
def create_comment():
    response = {}

    if request.method == "POST":

        begin_user = str(request.data).find('"', 13)
        end_user = str(request.data).find('"', begin_user + 1)
        begin_comment = str(request.data).find('"', end_user + 11)
        end_comment = str(request.data).find('"', begin_comment + 1)
        begin_stars = str(request.data).find('"', end_comment + 9)
        end_stars = str(request.data).find('"', begin_stars + 1)
        begin_product = str(request.data).find('"', end_stars + 14)
        end_product = str(request.data).find('"', begin_product + 1)

        user_id = str(request.data)[begin_user + 1:end_user]
        comment = str(request.data)[begin_comment + 1:end_comment]
        stars = str(request.data)[begin_stars + 1:end_stars]
        product_id = str(request.data)[begin_product + 1:end_product]
        date_created = datetime.datetime.now()

        arr = [user_id, comment, stars, product_id, date_created]

        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Comment ("
                           "user_id,"
                           "comment,"
                           "stars,"
                           "product_id,"
                           "date_created"
                           ") VALUES(?, ?, ?, ?, ?)", (arr[0], arr[1], arr[2], arr[3], arr[4]))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Comment added successfully"
        return response


@app.route('/get-products/', methods=["GET"])
def get_products():
    response = {}
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Product")

        products = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = products
    return response


@app.route('/get-users/', methods=["GET"])
def get_users():
    response = {}
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")

        products = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = products
    return response


@app.route('/get-user/<int:user_id>/', methods=["GET"])
def get_user(user_id):
    response = {}
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id=" + str(user_id))

        products = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = products
    return response


@app.route("/delete-product/<int:product_id>/")
# @jwt_required()
def delete_product(product_id):
    response = {}
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Product WHERE product_id=" + str(product_id))
        conn.commit()

        cursor = conn.cursor()
        cursor.execute("DELETE FROM Comment WHERE product_id=" + str(product_id))
        conn.commit()

        response['status_code'] = 200
        response['message'] = "Product deleted successfully."
    return response


@app.route('/edit-product/<int:product_id>/', methods=["PUT"])
# @cross_origin
# @jwt_required()
def edit_product(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect(db) as conn:
            begin = str(request.data).find('"', 18)
            end = str(request.data).find('"', begin+1)
            begin_second = str(request.data).find('"', end+17)
            end_second = str(request.data).find('"', begin_second+1)

            begin_description = str(request.data).find('"', end_second + 16)
            end_description = str(request.data).find('"', begin_description + 1)
            begin_category = str(request.data).find('"', end_description + 13)
            end_category = str(request.data).find('"', begin_category + 1)

            product_name = str(request.data)[begin+1:end]
            product_price = str(request.data)[begin_second+1:end_second]
            description = str(request.data)[begin_description + 1:end_description]
            category = str(request.data)[begin_category + 1:end_category]

            input_value = dict(product_name=product_name, product_price=product_price, description=description, category=category)
            incoming_data = input_value
            put_data = {}

            if incoming_data["product_name"] is not None:
                put_data["name"] = incoming_data["product_name"]
                with sqlite3.connect(db) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Product SET name =? WHERE product_id=?", (put_data["name"], str(product_id)))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200
            if incoming_data["product_price"] is not None:
                put_data['price'] = incoming_data['product_price']

                with sqlite3.connect(db) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Product SET price =? WHERE product_id=?",
                                   (put_data["price"], str(product_id)))
                    conn.commit()

                    response["content"] = "Content updated successfully"
                    response["status_code"] = 200
            if incoming_data["description"] is not None:
                put_data['description'] = incoming_data['description']

                with sqlite3.connect(db) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Product SET description =? WHERE product_id=?", (put_data["description"], str(product_id)))
                    conn.commit()

                    response["content"] = "Content updated successfully"
                    response["status_code"] = 200
            if incoming_data["category"] is not None:
                put_data['category'] = incoming_data['category']

                with sqlite3.connect(db) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Product SET category =? WHERE product_id=?", (put_data["category"], str(product_id)))
                    conn.commit()

                    response["content"] = "Content updated successfully"
                    response["status_code"] = 200
    return response


@app.route('/edit-cart-progress/<int:cart_id>/', methods=["PUT"])
# @cross_origin
# @jwt_required()
def edit_cart_progress(cart_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect(db) as conn:
            print(request.data)

            begin_progress = str(request.data).find('"', 14)
            end_progress = str(request.data).find('"', begin_progress+1)

            progress = str(request.data)[begin_progress + 1:end_progress]
            print(progress)

            input_value = dict(progress=progress)

            incoming_data = input_value
            put_data = {}

            if incoming_data["progress"] is not None:
                put_data["progress"] = incoming_data["progress"]
                with sqlite3.connect(db) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Cart SET progress =? WHERE cart_id=?", (put_data["progress"], str(cart_id)))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200
    return response


@app.route('/get-product/<int:product_id>/', methods=["GET"])
def get_product(product_id):
    response = {}

    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Product WHERE product_id=" + str(product_id))

        response["status_code"] = 200
        response["description"] = "Product retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


if __name__ == "__main__":
    app.run()
