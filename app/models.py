from datetime import datetime
import flask_login
from app import login
import pymysql
import pymysql.cursors

class User(flask_login.UserMixin):
    pass


@login.user_loader
def user_loader(email):
    users = []
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    try:
        with connection.cursor() as cursor:
            # Read user record by email
            sql = "SELECT `email` FROM `users`"
            cursor.execute(sql)
            result = cursor.fetchall()
            for i in result:
                users.append(i[0])
    finally:
        connection.close()


    if email not in users:
        return

    user = User()
    user.id = email
    return user

#@login.request_loader
#def request_loader(request):
#    email = request.form['emailid']
#    if email not in users:
#        return

#    user = User()
#    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
#    user.is_authenticated = request.form['pinid] == users[email]['pin']

#    return user
