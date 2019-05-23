from app import app
from app.forms import LoginForm, AddPushpinForm, AddCorkBoardForm, LikePushpinForm, UnlikePushpinForm, CommentForm

from flask import render_template, redirect, request, url_for, flash, session, request
from app.models import User
from flask_login import login_user, logout_user, current_user, login_required
import pymysql
import pymysql.cursors
from datetime import datetime as dt
from urllib.parse import urlparse



################################################################################
@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('login'))

################################################################################
@app.route('/login', methods=['GET'])
def login_view():
    logout_user()
    error = False
    return render_template('login.html', error=error)

@app.route('/login', methods=["POST"])
def login():
    email = request.form['emailid']
    pin = request.form['pinid']

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    try:
        with connection.cursor() as cursor:
            # Read user record by email
            sql = "SELECT `email`,`pin` FROM `users` WHERE `email`=%s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
    finally:
        connection.close()

    if (result is not None) and (email == result[0]) and (pin == result[1]):
        user = User()
        user.id = email
        login_user(user)
        return redirect('/user/'+ email)
    error = True
    return render_template('login.html',error=error)#redirect(url_for('login'))

################################################################################
@app.route('/add-corkboard', methods=['GET', 'POST'])
@login_required
def addCorkboard():
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    title = request.form.get('titleid')
    user = current_user.id
    category = []
    try:
        with connection.cursor() as cursor:
            sql = "SELECT name FROM category";
            cursor.execute(sql)
            result = cursor.fetchall()
            for res in result:
                category+= res
    finally:
        connection.close
    form = AddCorkBoardForm()
    if request.method == 'GET':
        return render_template('add-corkboard.html', category = category)
    elif request.method == 'POST':
        board_id = insert_corkboard(form)
    viewCorkboard(board_id, False)
    return redirect('/board/' + board_id)


def insert_corkboard(form):
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    title = request.form.get('titleid')
    category = request.form.get('categoryid')
    visibility = request.form.get('visibilityid')
    password = request.form.get('inputpassword')
    user = current_user.id
    board_id = None

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('" +str(user) + "', '" +str(title) + "', '" +str(category) + "',NOW(),'" +str(visibility) + "')";
            cursor.execute(sql)
            board_id = str(cursor.lastrowid)
            if str(visibility) == "Private":
                sql = "INSERT INTO boardpassword (email, boardID, password) VALUES ('" +str(user) + "', '" +str(cursor.lastrowid) + "','" +str(password) + "')";
                cursor.execute(sql)
            connection.commit()
    finally:
        connection.close
    return board_id


################################################################################
@app.route('/pushpin/<pin_id>', methods=['GET', 'POST'])
@login_required
def view_pushpin(pin_id):
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    like_form = LikePushpinForm()
    unlike_form = UnlikePushpinForm()
    comment_form = CommentForm()
    session["pin_id"] = pin_id

    if request.method == 'POST':
        if request.form.get('submit') == 'like':
            insert_like(connection=connection, pin_id = pin_id)
        if request.form.get('submit') == 'unlike':
            remove_like(connection=connection, pin_id = pin_id)
        if request.form.get('submit') == 'comment':
            content = request.form['content']
            insert_comment(connection=connection, pin_id = pin_id, content=content)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT `first`, `last`, url, description, createdDateTime, pushpin.email " \
                  "FROM pushpin JOIN users ON users.email=pushpin.email " \
                  "WHERE pinID=%s"
            cursor.execute(sql, (pin_id,))
            result = cursor.fetchone()
            first = result[0]
            last = result[1]
            url = result[2]
            description = result[3]
            createdDateTime = result[4]
            email = result[5]
            user = [first, last]

            parsed_uri = urlparse(url)
            pushpin_base_url = '{uri.netloc}'.format(uri=parsed_uri)

            pin_info = [url, description, createdDateTime]

            board_sql = "SELECT title, pushpin.boardID " \
                        "FROM corkboard JOIN pushpin ON pushpin.boardID=corkboard.boardID " \
                        "WHERE pushpin.pinID=%s"
            cursor.execute(board_sql, (pin_id,))
            result = cursor.fetchone()
            board_name = result[0]
            board_id = result[1]
            session["board_id"] = board_id

            tags_sql = "SELECT tag " \
                       "FROM pushpin_tag JOIN pushpin ON pushpin.pinID=pushpin_tag.pinID " \
                       "WHERE pushpin.pinID=%s " \
                       "ORDER BY pushpin_tag.tag"
            cursor.execute(tags_sql, (pin_id,))
            result = cursor.fetchall()
            tags = [x[0] for x in result]

            like_sql = "SELECT * " \
                       "FROM `like` " \
                       "WHERE pinOwnerEmail=%s AND email=%s AND pinID=%s"
            cursor.execute(like_sql, (email, current_user.id, pin_id))
            result = cursor.fetchall()
            user_likes_pushpin = len(result) > 0

            show_like_button = (current_user.id != email and not user_likes_pushpin)
            show_unlike_button = (current_user.id != email and user_likes_pushpin)

            pushpin_likes_sql = "SELECT first,last " \
                                "FROM `like` NATURAL JOIN users " \
                                "WHERE pinID=%s"
            cursor.execute(pushpin_likes_sql, (pin_id,))
            pushpin_likes = cursor.fetchall()

            comment_sql = "SELECT `first`,`last`,content " \
                          "FROM comment NATURAL JOIN users WHERE  pinID=%s " \
                          "ORDER BY createdDateTime DESC"

            cursor.execute(comment_sql, (pin_id,))
            comments = cursor.fetchall()

            can_follow = is_viewer_following_board_owner(email)

            home_url = url_for('login').split('/')[0] + '/user/' + str(current_user.id)
            self_follow = (current_user.id == email)

            board_url = url_for('login').split('/')[0] + '/board/' + str(board_id)

    finally:
        connection.close()

    return render_template('view-pushpin.html', like_form=like_form, unlike_form=unlike_form, comment_form=comment_form, pin_id=pin_id, user=user, pin_info=pin_info,
                           board_name=board_name, pushpin_base_url=pushpin_base_url, tags=tags, home_url=home_url, board_url=board_url,
                           show_like_button=show_like_button, show_unlike_button=show_unlike_button, comments=comments, can_follow=can_follow, pushpin_likes=pushpin_likes, self_follow = self_follow)


def insert_comment(connection, pin_id, content):
    try:
        with connection.cursor() as cursor:
            insert_comment_sql = "INSERT INTO comment (email, pinID, content, createdDateTime) VALUES ('" + str(current_user.id) + "', '" + str(pin_id) + "', '" + str(content) + "', NOW());"
            cursor.execute(insert_comment_sql)
            connection.commit()
    finally:
        pass


def insert_like(connection, pin_id):
    email_sql = "SELECT email, boardID FROM pushpin WHERE pinID=%s"

    try:
        with connection.cursor() as cursor:
            cursor.execute(email_sql,(pin_id,))
            result = cursor.fetchone()
            email = result[0]
            board_id = result[1]

            like_sql = "INSERT INTO `like` (email, pinOwnerEmail, boardID, pinID) VALUES ('" + str(current_user.id) + "', '" + str(email) + "','" + str(board_id) + "','" + str(pin_id) + "')"

            cursor.execute(like_sql)
            connection.commit()
    finally:
        pass


def remove_like(connection, pin_id):
    email_sql = "SELECT email, boardID FROM pushpin WHERE pinID=%s"
    unlike_sql = "DELETE FROM `like` WHERE email=%s and pinOwnerEmail=%s and boardID=%s and pinID=%s;"
    try:
        with connection.cursor() as cursor:
            cursor.execute(email_sql,(pin_id,))
            result = cursor.fetchone()
            email = result[0]
            board_id = result[1]

            cursor.execute(unlike_sql, (current_user.id, email, board_id, pin_id,))
            connection.commit()
    finally:
        pass


def is_viewer_following_board_owner(board_owner_id):
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')

    try:
        with connection.cursor() as cursor:
            viewer_id = current_user.id
            sql = "SELECT followeeEmail " \
                  "FROM follow " \
                  "WHERE  followeeEmail = '" + str(board_owner_id) + "'AND followerEmail = '" + str(viewer_id) + "' "
            cursor.execute(sql)
            result = cursor.fetchone()
            # Not sure bout this logic, but it seemed to fix my problems of being in sync with ViewCorkboard
            if result is not None:
                return False
            else:
                return True
    finally:
        connection.close()


################################################################################
@app.route('/add-pushpin', methods=['GET', 'POST'])
@login_required
def add_pushpin():
    if request.method == 'POST':
        app.logger.info("got through")
        flash('Your changes have been saved.')
        insert_pushpin()
        board_id = session['board_id']
        #url = url_for('viewCorkboard', board_id=board_id, check_if_board_private=False)

        return viewCorkboard(board_id, False)
        #return redirect(url)
    else:
        connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
        try:
            with connection.cursor() as cursor:
                board_id = session['board_id']
                sql = "SELECT `title` FROM `corkboard` WHERE `boardID`=%s"
                cursor.execute(sql, (board_id,))
                result = cursor.fetchone()
                corkboard_name = result[0]
                # Get the user emailid
                viewer_id = current_user.id
                home_url = url_for('login').split('/')[0] + '/user/' + str(viewer_id)
                return render_template('add-pushpin.html', corkboard_name=corkboard_name, home_url=home_url)
        finally:
            connection.close()

def insert_pushpin():
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    try:
        with connection.cursor() as cursor:
            url = request.form['urlid']
            description = request.form['descid']
            tags = request.form['tagid'].split(",")
            tags = [x.lower().strip() for x in tags]
            tags = list(set(tags))
            user = current_user.id
            board_id = session['board_id']
            pushpin_sql = "INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES  ('" +str(user) + "', '" +str(board_id) + "', '" +str(url) + "','" +str(description) + "',NOW())"
            cursor.execute(pushpin_sql)

            update_corkboardTime = "UPDATE corkboard set lastUpdateTime = "' NOW()'" WHERE boardID = '" +str(board_id) + "'"
            cursor.execute(update_corkboardTime)

            get_pin_sql = "SELECT MAX(pinID) FROM pushpin"
            cursor.execute(get_pin_sql)
            last_inserted_pushpin_id = cursor.fetchone()[0]
            for tag in tags:
                pushpin_tag_sql = "INSERT INTO pushpin_tag (email, boardID, pinID, tag ) VALUES  ('" +str(user) + "', '" +str(board_id) + "','" +str(last_inserted_pushpin_id) + "' ,'" +str(tag) + "')"
                cursor.execute(pushpin_tag_sql)

            connection.commit()
    finally:
        connection.close()


################################################################################
@app.route('/user/<user_email>')
@login_required
def user(user_email):
    email = user_email
    # make database connectionto get the data
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    try:
        with connection.cursor() as cursor:
            # Get user first and last name by email
            sql = "SELECT `first`,`last` FROM `users` WHERE `email`=%s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            first_name = result[0]
            last_name = result[1]

            # Get user CorkBoards and PushPin number
            sql = "SELECT title,boardType, COUNT(title), corkboard.boardID FROM corkboard LEFT JOIN pushpin ON corkboard.boardID=pushpin.boardID  WHERE corkboard.email= %s GROUP BY title, boardType,boardID ORDER BY title"
            cursor.execute(sql, (email,))
            boards_pin_num_ = cursor.fetchall()
            #convert tuple of tuples to list
            boards_pin_num= [list(item) for item in boards_pin_num_]
            for i in range(len(boards_pin_num)):
                record = boards_pin_num[i]
                board_url = url_for('login').split("/")[0]+'/board/'+str(record[3])
                boards_pin_num[i].append(board_url)
            for board in boards_pin_num:
                if board[2] == 1:
                    sql = "SELECT pinID FROM pushpin  WHERE boardID = %s"
                    cursor.execute(sql, (board[3],))
                    result = cursor.fetchone()
                    if result is None:
                        board[2] = 0;


            # Get recently updated CorkBoards
            sql = """ (SELECT  DISTINCT first,last, title, boardType, lastUpdateTime, corkboard.boardID from users INNER JOIN corkboard on users.email=corkboard.email INNER JOIN pushpin on corkboard.boardID =pushpin.boardID  WHERE corkboard.email=%s)
                    UNION(
                    SELECT DISTINCT first, last, title, boardType, lastUpdateTime, corkboard.boardID from users INNER JOIN corkboard on users.email=corkboard.email INNER JOIN pushpin on corkboard.boardID =pushpin.boardID WHERE corkboard.email IN (SELECT followeeEmail FROM follow WHERE followerEmail=%s)
                    )
                    UNION(
                    SELECT DISTINCT first, last, title, boardType, lastUpdateTime, corkboard.boardID from users INNER JOIN corkboard on users.email=corkboard.email INNER JOIN pushpin on corkboard.boardID =pushpin.boardID WHERE corkboard.boardID IN (SELECT watch.boardID FROM watch WHERE watch.email=%s)
                    )
                    ORDER BY lastUpdateTime DESC
                    LIMIT 4"""
            cursor.execute(sql, (email,email, email))

            recent_board_ = cursor.fetchall()
            #convert tuple of tuples to list of lists
            recent_board = [list(item) for item in recent_board_]
            for i in range (len(recent_board)):
                record = recent_board[i]
                date_obj = record[4]
                #date_obj = dt.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                date_ = dt.strftime(date_obj, '%B %d, %Y')
                time_ = dt.strftime(date_obj, '%H:%M %p')
                recent_board[i].append(date_)
                recent_board[i].append(time_)
                #build the url for corkboard
                board_url = url_for('login').split("/")[0]+'/board/'+str(record[5])
                recent_board[i].append(board_url)
    finally:
        connection.close()

    return render_template('home.html', first_name=first_name, last_name=last_name, boards_pin_num=boards_pin_num, recent_board=recent_board)
################################################################################
@app.route('/board/<board_id>')
@login_required
def viewCorkboard(board_id, check_if_board_private = True):

    board_id = int(board_id)
    session["board_id"] = board_id
    session["pin_id"] = None
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')

    try:
        with connection.cursor() as cursor:
            #if it's a private corkboard, re-direct to private page
            if check_if_board_private == True:
                sql = "SELECT  boardType FROM corkboard WHERE boardID=%s"
                cursor.execute(sql, (board_id,))
                result = cursor.fetchone()
                privacy = result[0]
                if str(privacy) == "Private":
                    return redirect('/privateBoard/' + str(board_id) )

            # Get watch number
            sql = "SELECT COUNT(email) FROM watch WHERE boardID=%s"
            cursor.execute(sql, (board_id,))
            result = cursor.fetchone()
            watch_num = result[0]

            # Get user and board info
            sql = "SELECT first, last, title, categoryName, lastUpdateTime FROM corkboard LEFT JOIN users ON users.email=corkboard.email WHERE boardID=%s"
            cursor.execute(sql, (board_id,))
            result = cursor.fetchone()
            board_info = list(result)
            date_obj = board_info[4]
            date_ = dt.strftime(date_obj, '%B %d, %Y')
            time_ = dt.strftime(date_obj, '%H:%M %p')
            board_info.append(date_)
            board_info.append(time_)

            # Get the PushPin
            sql = "SELECT url, pinID FROM pushpin WHERE boardID=%s"
            cursor.execute(sql, (board_id,))
            result = cursor.fetchall()
            pin_info = []
            for info in result:
                pin_info.append([info[0], info[1]])

            #Decide the button status  can follow vs. can't follow
            viewer_id = current_user.id
            sql = "SELECT email, boardType FROM corkboard WHERE boardID=%s"
            cursor.execute(sql, (board_id,))
            result = cursor.fetchone()
            board_onwer_id = result[0]
            if (board_onwer_id == viewer_id):
                isSelf = True
            else:
                isSelf = False
            if (board_onwer_id != viewer_id) and (result[1]=='Public'):
                canWatch = True
            else:
                canWatch = False
            # Get the user emailid
            home_url = url_for('login').split('/')[0] + '/user/' + str(viewer_id)

            #Decide the button status follow vs. unfollow;
            sql = "SELECT followeeEmail FROM follow WHERE  followeeEmail = '" +str(board_onwer_id) + "'AND followerEmail = '" +str(viewer_id) + "' "
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is not None):
                isFollowed = True
            else:
                isFollowed = False;

            sql = "SELECT boardID FROM watch WHERE boardID = %s AND email = %s"
            cursor.execute(sql, (board_id, viewer_id))
            result = cursor.fetchone()
            if (result is not None):
                isWatched = True
            else:
                isWatched = False
    finally:
        connection.close()

    return render_template('view-corkboard.html', watch_num=watch_num,board_info=board_info, pin_info=pin_info, home_url=home_url, isSelf = isSelf, isFollowed = isFollowed, isWatched = isWatched, canWatch = canWatch)
################################################################################
@app.route('/privateBoard/<board_id>' , methods=['GET', 'POST'])
def privateBoard(board_id):
    board_id = int(board_id)
    if request.method == 'POST' and request.form['button'] == 'cancelbutton':
        #user hits cancel, go back to home page
        user = current_user.id
        return redirect('/user/'+ user)

    elif request.method == 'POST' and request.form['button'] == 'okbutton':
        #user hits ok, verify the correct password now
        password = request.form.get('passwordid')
        connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
        try:
            with connection.cursor() as cursor:
                board_id = session['board_id']
                sql = "SELECT `password` FROM `boardpassword` WHERE `boardID`=%s"
                cursor.execute(sql, (board_id,))
                result = cursor.fetchone()
                corkboard_password = result[0]

        finally:
            connection.close()
        if corkboard_password == password:
            return viewCorkboard(board_id, False)

    return render_template('view-private-corkboard.html', id = board_id)
################################################################################
@app.route('/pushpin-search', methods=['GET', 'POST'])
def search():
    searchTerm = request.form.get('pinsearchinput')
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    pushPinDescription = []
    url = []
    corkboardTitle = []
    corkboardOwner = []

    try:
        with connection.cursor() as cursor:
            pushpin_sql = "SELECT DISTINCT P.description, C.title, U.first, U.last, C.boardType, P.pinID " \
                          "FROM pushpin P JOIN corkboard C on P.boardID = C.boardID " \
                            "JOIN users U on P.email = U.email " \
                            "LEFT JOIN pushpin_tag T on T.pinID = P.pinID " \
                          "WHERE P.description LIKE '%" + str(searchTerm) + "%' " \
                          "OR C.categoryName LIKE '%" + str(searchTerm) + "%'" \
                          "OR T.tag LIKE '%" + str(searchTerm) + "%'" \
                          " ORDER by description"
            cursor.execute(pushpin_sql)
            result = cursor.fetchall()
            for col in result:
                #only display description, title, and owner if the board is public
                if str(col[4]) == "Public":
                    pushPinDescription.append(col[0])
                    corkboardTitle.append(col[1])
                    corkboardOwner.append(col[2] + " " + col[3])
                    url.append("/pushpin/" + str(col[5]))

            connection.commit()
    finally:
        connection.close
    return render_template('pushpin-search.html', pushPinDescription=pushPinDescription, corkboardTitle = corkboardTitle, corkboardOwner = corkboardOwner, url = url, zip=zip)
################################################################################
@app.route('/follow', methods=["POST"])
def follow():
    follower = current_user.id
    board_id = session['board_id']
    if ('pin_id' in session.keys()):
        pin_id = session['pin_id']
    else:
        pin_id = None

    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    try:
        with connection.cursor() as cursor:
            #Get the boardowner email using boardID #
            sql = "SELECT `email` FROM `corkboard` WHERE `boardID`=%s"
            cursor.execute(sql, (board_id,))
            result = cursor.fetchone()
            followee = result[0]
            # Insert followee record into table follow
            sql = "INSERT INTO follow (followerEmail, followeeEmail) VALUES ('" +str(follower) + "', '" +str(followee) + "')";
            cursor.execute(sql)
            connection.commit()
    finally:
        connection.close()
    if pin_id is not None:
        return redirect('/pushpin/'+ str(pin_id))
    else:
        return viewCorkboard(str(board_id), False)

################################################################################
@app.route('/watch', methods=["POST"])
def watch():
    watcher = current_user.id
    board_id = session['board_id']


    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    try:
        with connection.cursor() as cursor:
            #Get the boardowner email using boardID #
            sql = "SELECT `email` FROM `corkboard` WHERE `boardID`=%s"
            cursor.execute(sql, (board_id,))
            result = cursor.fetchone()
            boardOwner = result[0]
            # Insert followee record into table follow
            sql = "INSERT INTO watch (email, boardOwnerEmail, boardID) VALUES ('" +str(watcher) + "', '" +str(boardOwner) + "', '" +str(board_id) + "')";
            cursor.execute(sql)
            connection.commit()
    finally:
        connection.close()
    return redirect('/board/'+ str(board_id))

################################################################################
@app.route('/unfollow', methods=["POST"])
def unfollow():
    follower = current_user.id
    board_id = session['board_id']
    if ('pin_id' in session.keys()):
        pin_id = session['pin_id']
    else:
        pin_id = None

    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    try:
        with connection.cursor() as cursor:
            #Get the boardowner email using boardID #
            sql = "SELECT `email`, `boardType` FROM `corkboard` WHERE `boardID`=%s"
            cursor.execute(sql, (board_id,))
            result = cursor.fetchone()
            followee = result[0]
            boardType = result[1]
            # Insert followee record into table follow
            sql = "DELETE FROM `follow`  WHERE followerEmail = %s And  followeeEmail=%s";
            cursor.execute(sql,(follower, followee))
            connection.commit()
    finally:
        connection.close()
    if pin_id is not None:
        return redirect('/pushpin/'+ str(pin_id))
    else:
        return viewCorkboard(str(board_id), False)

################################################################################
@app.route('/unwatch', methods=["POST"])
def unwatch():
    followee = current_user.id
    board_id = session['board_id']
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    try:
        with connection.cursor() as cursor:
            # Insert followee record into table follow
            sql = "DELETE FROM `watch`  WHERE email = %s And  boardID = %s";
            cursor.execute(sql,(followee, board_id))
            connection.commit()
    finally:
        connection.close()
    return redirect('/board/'+ str(board_id))
###############################################################################
@app.route('/popular-tags', methods=["GET"])
def popularTags():
    # Get and show top 5 most popular tags
    # Allow user to click tags and redirect to Search Results Page w/ tag's name as search criteria
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    tags = []
    pushPinCount = []
    uniqueCorkBoardCount = []

    try:
        with connection.cursor() as cursor:
            tag_sql = "SELECT `tag`, COUNT(*) as count " \
                  "FROM `pushpin_tag` " \
                  "GROUP BY `tag` " \
                  "ORDER BY count DESC"
            numRows = cursor.execute(tag_sql)
            countRow = 0
            while True:
                row = cursor.fetchone()
                if row == None:
                    break
                else:
                    tags.append(row[0])
                    pushPinCount.append(row[1])
                countRow += 1
                if countRow >= 5:
                    break

            for tag in tags:
                unique_sql = "SELECT COUNT(DISTINCT boardID) " \
                             "FROM `pushpin_tag` " \
                             "WHERE tag = %s"
                cursor.execute(unique_sql,(tag))
                result = cursor.fetchone()
                uniqueCorkBoardCount.append(result[0])

            # Get the user emailid
            viewer_id = current_user.id
            home_url = url_for('login').split('/')[0] + '/user/' + str(viewer_id)
    finally:
        connection.close()

    # if clickedOnTag:
    #     return redirect(url_for('search'))

    return render_template('popular-tags.html', tags=tags, pushPinCount=pushPinCount, uniqueCorkBoardCount=uniqueCorkBoardCount, home_url=home_url)
###############################################################################
@app.route('/popular-sites', methods=["GET"])
def popularSites():
    # Get and show most popular sites
    # Order from high to low based on pushpin count
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    url = []
    pushPinCount = []

    try:
        with connection.cursor() as cursor:
            url_sql = "SELECT SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(target_url, '/', 3), '://', -1), '/', 1), '?', 1) AS domain, COUNT(*) as count " \
                      "FROM ( " \
                      "SELECT url as target_url " \
                      "FROM `pushpin`) AS custom " \
                      "GROUP BY domain " \
                      "ORDER BY count DESC"
            numRows = cursor.execute(url_sql)
            while True:
                row = cursor.fetchone()
                if row == None:
                    break
                else:
                    url.append(row[0])
                    pushPinCount.append(row[1])
            # Get the user emailid
            viewer_id = current_user.id
            home_url = url_for('login').split('/')[0] + '/user/' + str(viewer_id)
    finally:
        connection.close()

    return render_template('popular-sites.html', url=url, pushPinCount=pushPinCount, home_url=home_url)
###############################################################################
@app.route('/corkboard-statistics', methods=["GET"])
@login_required
def corkboardStatistics():
    # Get and show users, public CBs, public pps, private cbs, private pps
    # Order by # of public cbs then # of private cbs
    # highlight currnet user in red
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    currUser = current_user.id

    users = []
    usersEmail = []
    numPublicCorkBoards = []
    numPublicPushPins = []
    numPrivateCorkBoards = []
    numPrivatePushPins = []

    try:
        with connection.cursor() as cursor:
            board_sql = "SELECT sq1.email, sq1.publicCount, sq2.privateCount " \
            "FROM( " \
            "(SELECT u1.email, ifnull(COUNT(publicCork.email), 0) as publicCount " \
            "FROM users u1 left join " \
            "(SELECT `email` FROM corkboard c1 WHERE c1.boardType = 'Public') as publicCork " \
            "on u1.email = publicCork.email " \
            "GROUP BY u1.email) as sq1 " \
            "LEFT JOIN " \
            "(SELECT u2.email, ifnull(COUNT(privateCork.email), 0) as privateCount " \
            "FROM users u2 left join " \
            "(SELECT `email` FROM corkboard c2 WHERE c2.boardType = 'Private') as privateCork " \
            "on u2.email = privateCork.email " \
            "GROUP BY u2.email) as sq2 " \
            "on sq1.email = sq2.email " \
            ") " \
            "GROUP BY sq1.email " \
            "ORDER BY sq1.publicCount DESC, sq2.privateCount DESC"
            numRows = cursor.execute(board_sql)
            while True:
                row = cursor.fetchone()
                if row == None:
                    break
                else:
                    usersEmail.append(row[0])
                    numPublicCorkBoards.append(row[1])
                    numPrivateCorkBoards.append(row[2])

            for email in usersEmail:
                name_sql = "SELECT first, last " \
                           "FROM users " \
                           "WHERE email=%s"
                cursor.execute(name_sql,(email))
                row = cursor.fetchone()
                users.append("%s %s" %(row[0], row[1]))
                pub_pin_sql = "SELECT publicEmail, publicCount " \
                              "FROM ( " \
                              "SELECT pushpin.email as publicEmail, COUNT(pushpin.pinID) as publicCount " \
                              "FROM pushpin INNER JOIN corkboard on pushpin.email = corkboard.email and pushpin.boardID = corkboard.boardID " \
                              "WHERE `boardType` = 'Public' " \
                              "GROUP BY pushpin.email ) as public " \
                              "WHERE publicEmail=%s"
                cursor.execute(pub_pin_sql,(email))
                row = cursor.fetchone()
                if row == None:
                    numPublicPushPins.append(0)
                else:
                    numPublicPushPins.append(row[1])
                priv_pin_sql = "SELECT privateEmail, privateCount " \
                              "FROM ( " \
                              "SELECT pushpin.email as privateEmail, COUNT(pushpin.pinID) as privateCount " \
                              "FROM pushpin INNER JOIN corkboard on pushpin.email = corkboard.email and pushpin.boardID = corkboard.boardID " \
                              "WHERE `boardType` = 'Private' " \
                              "GROUP BY pushpin.email ) as private " \
                              "WHERE privateEmail=%s"
                cursor.execute(priv_pin_sql,(email))
                row = cursor.fetchone()
                if row == None:
                    numPrivatePushPins.append(0)
                else:
                    numPrivatePushPins.append(row[1])
            # Get the user emailid
            viewer_id = current_user.id
            home_url = url_for('login').split('/')[0] + '/user/' + str(viewer_id)
    finally:
        connection.close()

    return render_template('corkboard-statistics.html', users=users, usersEmail=usersEmail, numPublicCorkBoards=numPublicCorkBoards, numPublicPushPins=numPublicPushPins, numPrivateCorkBoards=numPrivateCorkBoards, numPrivatePushPins=numPrivatePushPins, currUser=currUser, home_url=home_url, zip=zip)
###########################################################################################
@app.route('/pushpin-search/<tag>', methods=['GET', 'POST'])
def searchFromPushPin(tag):
    #searchTerm = request.form.get('pinsearchinput')
    searchTerm = tag
    connection = pymysql.connect(user='root', passwd='securepass', host='db', port=3306, db='cs6400_fa18_team074')
    pushPinDescription = []
    url = []
    corkboardTitle = []
    corkboardOwner = []

    try:
        with connection.cursor() as cursor:
            pushpin_sql = "SELECT DISTINCT P.description, C.title, U.first, U.last, C.boardType, P.pinID " \
                          "FROM pushpin P JOIN corkboard C on P.boardID = C.boardID " \
                            "JOIN users U on P.email = U.email " \
                            "LEFT JOIN pushpin_tag T on T.pinID = P.pinID " \
                          "WHERE P.description LIKE '%" + str(searchTerm) + "%' " \
                          "OR C.categoryName LIKE '%" + str(searchTerm) + "%'" \
                          "OR T.tag LIKE '%" + str(searchTerm) + "%'" \
                          " ORDER by description"
            cursor.execute(pushpin_sql)
            result = cursor.fetchall()
            for col in result:
                #only display description, title, and owner if the board is public
                if str(col[4]) == "Public":
                    pushPinDescription.append(col[0])
                    corkboardTitle.append(col[1])
                    corkboardOwner.append(col[2] + " " + col[3])
                    url.append("/pushpin/" + str(col[5]))

            connection.commit()
    finally:
        connection.close
    return render_template('pushpin-search.html', pushPinDescription=pushPinDescription, corkboardTitle = corkboardTitle, corkboardOwner = corkboardOwner, url = url, zip=zip)
