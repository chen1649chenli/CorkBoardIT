-- CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
CREATE USER IF NOT EXISTS 'joe'@'localhost' IDENTIFIED BY '123';


DROP DATABASE IF EXISTS cs6400_fa18_team074;
SET default_storage_engine=InnoDB;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS cs6400_fa18_team074
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;
USE cs6400_fa18_team074;

GRANT ALL PRIVILEGES ON `cs6400_fa18_team074`.* TO 'joe'@'localhost';
FLUSH PRIVILEGES;





-- User
CREATE TABLE users (
        email varchar(100) NOT NULL,
        pin varchar(4) NOT NULL,
        first varchar(50) NOT NULL,
        last varchar(50) NOT NULL,
        PRIMARY KEY (email));

INSERT INTO users (email, pin, first, last) VALUES ('lchen427@gatech.edu', '1234', 'Li', 'Chen');
INSERT INTO users (email, pin, first, last) VALUES ('zbb7@gatech.edu', '1234', 'Zachary', 'Buchanan');
INSERT INTO users (email, pin, first, last) VALUES ('mprior6@gatech.edu', '1234', 'Matt', 'Prior');
INSERT INTO users (email, pin, first, last) VALUES ('awang383@gatech.edu', '1234', 'Alan', 'Wang');
INSERT INTO users (email, pin, first, last) VALUES ('taylor@gatech.edu', '1234', 'Taylor', 'Swift');
INSERT INTO users (email, pin, first, last) VALUES ('selena@gatech.edu', '1234', 'Selena', 'Gomez');
INSERT INTO users (email, pin, first, last) VALUES ('dwayne@gatech.edu', '1234', 'Dwayne', 'Johnson');
INSERT INTO users (email, pin, first, last) VALUES ('tim@gatech.edu', '1234', 'Tim', 'Cook');
INSERT INTO users (email, pin, first, last) VALUES ('warren@gatech.edu', '1234', 'Warren', 'Buffett');
INSERT INTO users (email, pin, first, last) VALUES ('bill@gatech.edu', '1234', 'Bill', 'Gates');
INSERT INTO users (email, pin, first, last) VALUES ('elon@gatech.edu', '1234', 'Elon', 'Musk');

-- Category
CREATE TABLE category (
        name varchar(50) NOT NULL,
        PRIMARY KEY (name));

INSERT INTO category (name) VALUES ('Education');
INSERT INTO category (name) VALUES ('People');
INSERT INTO category (name) VALUES ('Sports');
INSERT INTO category (name) VALUES ('Other');
INSERT INTO category (name) VALUES ('Architecture');
INSERT INTO category (name) VALUES ('Travel');
INSERT INTO category (name) VALUES ('Pets');
INSERT INTO category (name) VALUES ('Food & Drink');
INSERT INTO category (name) VALUES ('Home & Garden');
INSERT INTO category (name) VALUES ('Photography');
INSERT INTO category (name) VALUES ('Technology');
INSERT INTO category (name) VALUES ('Art');


-- CorkBoard
CREATE TABLE corkboard (
        email varchar(100) NOT NULL,
        boardID int NOT NULL AUTO_INCREMENT,
        title varchar(50) NOT NULL,
        categoryName varchar(50) NOT NULL,
        lastUpdateTime datetime NULL,
        boardType varchar(7) NOT NULL,
        PRIMARY KEY (email, boardID),
        FOREIGN KEY (email) REFERENCES users (email),
        FOREIGN KEY (categoryName) REFERENCES category (name),
        UNIQUE(boardID));

INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('lchen427@gatech.edu', 'Dogs', 'Pets','2018-10-21 00:00:00.000000','Public');
INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('lchen427@gatech.edu','Cats', 'Pets','2018-10-21 01:00:00.000000','Private');
INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('lchen427@gatech.edu', 'Turtles', 'Pets','2018-10-21 00:01:00.000000','Public');
INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('lchen427@gatech.edu', 'Fish', 'Pets','2018-10-21 00:00:03.000000','Public');
INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('zbb7@gatech.edu', 'Boston Celtics', 'Sports','2018-10-21 02:00:00.000000','Public');
INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('zbb7@gatech.edu', 'Chicago Bulls', 'Sports','2018-10-21 00:01:01.000000','Public');
INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('zbb7@gatech.edu', 'Houston Rockets', 'Sports','2018-10-21 03:00:00.000000','Private');
INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('awang383@gatech.edu', 'Titanic', 'Art','2018-10-21 04:00:00.000000','Public');
INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('awang383@gatech.edu', 'Forrest Gump', 'Art','2018-10-21 10:00:00.000000','Public');
INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('awang383@gatech.edu', 'Jaws', 'Art','2018-10-21 02:00:00.000000','Public');
INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('mprior6@gatech.edu', 'Omega', 'Other','2018-10-21 00:02:00.000000','Public');
INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('mprior6@gatech.edu', 'Tissot', 'Other','2018-10-21 00:00:00.200000','Public');
INSERT INTO corkboard (email, title, categoryName, lastUpdateTime, boardType ) VALUES ('mprior6@gatech.edu', 'Patek Philippe', 'Other','2018-10-22 00:03:00.000000','Private');

-- PushPin
CREATE TABLE pushpin (
        email varchar(100) NOT NULL,
        boardID int NOT NULL,
        pinID int NOT NULL AUTO_INCREMENT,
        url varchar(250) NOT NULL,
        description varchar(200) NOT NULL,
        createdDateTime datetime NOT NULL,
        PRIMARY KEY (email, boardID, pinID),
        FOREIGN KEY (boardID) REFERENCES corkboard (boardID),
        FOREIGN KEY (email) REFERENCES users (email),
        UNIQUE(pinID));

-- PushPin Tag
Create TABLE pushpin_tag (
        email varchar(100) NOT NULL,
        boardID int NOT NULL,
        pinID int NOT NULL AUTO_INCREMENT,
        tag varchar(20) NOT NULL,
        PRIMARY KEY (email, boardID, pinID, tag),
        FOREIGN KEY (boardID) REFERENCES corkboard (boardID),
        FOREIGN KEY (email) REFERENCES users (email),
        FOREIGN KEY (pinID) REFERENCES pushpin (pinID));


INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('lchen427@gatech.edu', 1, 'http://jiangzhenling.com/img/CS6400/dog/dog1.png', 'this is a cute dog','2018-10-21 09:00:00.000000');
INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('lchen427@gatech.edu', 1, 'http://jiangzhenling.com/img/CS6400/dog/dog2.png', 'this is a ugly dog','2018-10-21 09:00:00.000000');
INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('lchen427@gatech.edu', 2, 'http://123.cats.com/1', 'this is a cute cat','2018-10-21 09:00:00.000000');
INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('lchen427@gatech.edu', 3, 'http://123.turtles.com/2', 'this is a Japanese turtle','2018-10-21 09:00:00.000000');
INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('lchen427@gatech.edu', 3, 'http://123.turtles.com/1', 'this is a Chinese turtle','2018-10-21 09:00:00.000000');
INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('lchen427@gatech.edu', 3, 'http://123.turtles.com/2', 'this is a Box turtle','2018-10-21 09:00:00.000000');
INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('lchen427@gatech.edu', 4, 'http://123.fish.com/2', 'this is a golden fish','2018-10-21 09:00:00.000000');
INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('mprior6@gatech.edu', 13,  'http://jiangzhenling.com/img/CS6400/watch/watch1.png', 'this is a beautiful watch','2018-10-22 09:00:00.000000');
INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('mprior6@gatech.edu', 13, 'http://jiangzhenling.com/img/CS6400/watch/watch2.png', 'this is an expensive watch','2018-10-22 09:00:00.000000');
INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('mprior6@gatech.edu', 13, 'http://jiangzhenling.com/img/CS6400/watch/watch3.png', 'this is a cute watch','2018-10-22 09:00:00.000000');
INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('mprior6@gatech.edu', 13, 'http://jiangzhenling.com/img/CS6400/watch/watch4.png', 'this is a dream watch','2018-10-22 09:00:00.000000');
INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('mprior6@gatech.edu', 13, 'http://jiangzhenling.com/img/CS6400/watch/watch5.png', 'I want this watch','2018-10-22 09:00:00.000000');
INSERT INTO pushpin (email, boardID, url, description, createdDateTime ) VALUES ('mprior6@gatech.edu', 13, 'http://jiangzhenling.com/img/CS6400/watch/watch6.png', 'Most expensive watch in the world','2018-10-21 02:00:00.000000');

INSERT INTO pushpin_tag (email, boardID, pinID, tag) VALUE ('lchen427@gatech.edu', 1, 1, 'cats');

-- Follow
CREATE TABLE follow (
        followerEmail varchar(100) NOT NULL,
        followeeEmail varchar(100) NOT NULL,
        PRIMARY KEY (followerEmail, followeeEmail),
        FOREIGN KEY (followerEmail) REFERENCES users (email),
        FOREIGN KEY (followeeEmail) REFERENCES users (email));

INSERT INTO follow (followerEmail, followeeEmail) VALUES ('lchen427@gatech.edu', 'zbb7@gatech.edu');
INSERT INTO follow (followerEmail, followeeEmail) VALUES ('lchen427@gatech.edu', 'awang383@gatech.edu');

delimiter //
CREATE TRIGGER follow_trigger BEFORE INSERT ON follow
FOR EACH ROW
BEGIN
    IF (new.followerEmail = new.followeeEmail) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'self-follow error. Insertion canceled';
    END IF;
END
//
delimiter ;
-- Watch
CREATE TABLE watch (
        email varchar(100) NOT NULL,
        boardOwnerEmail varchar(100) NOT NULL,
        boardID int NOT NULL,
        PRIMARY KEY (email, boardID, boardOwnerEmail),
        FOREIGN KEY (email) REFERENCES users (email),
        FOREIGN KEY (boardOwnerEmail) REFERENCES users (email),
        FOREIGN KEY (boardID) REFERENCES corkboard (boardID));

INSERT INTO watch (email, boardOwnerEmail, boardID) VALUES ('lchen427@gatech.edu', 'mprior6@gatech.edu', 11);

delimiter //
CREATE TRIGGER watch_trigger BEFORE INSERT ON watch
FOR EACH ROW
BEGIN
    IF (new.email = new.boardOwnerEmail) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'watch own board error. Insertion canceled';
    END IF;
END
//
delimiter ;

-- Like
CREATE TABLE `like` (
        email varchar(100) NOT NULL,
        pinOwnerEmail varchar(100) NOT NULL,
        boardID int NOT NULL,
        pinID int NOT NULL,
        PRIMARY KEY (email, boardID, pinOwnerEmail, pinID),
        FOREIGN KEY (email) REFERENCES users (email),
        FOREIGN KEY (pinOwnerEmail) REFERENCES users (email),
        FOREIGN KEY (boardID) REFERENCES corkboard (boardID),
        FOREIGN KEY (pinID) REFERENCES pushpin (pinID));

INSERT INTO `like` (email, pinOwnerEmail, boardID, pinID) VALUES ('mprior6@gatech.edu','lchen427@gatech.edu','1','1');

-- Comment
CREATE TABLE comment (
        email varchar(100) NOT NULL,
        pinID int NOT NULL,
        commentID int NOT NULL AUTO_INCREMENT,
        content VARCHAR(1000) NOT NULL,
        createdDateTime DATETIME NOT NULL,
        PRIMARY KEY (email, pinID, commentID),
        FOREIGN KEY (email) REFERENCES users (email),
        FOREIGN KEY (pinID) REFERENCES pushpin (pinID),
        UNIQUE (commentID));

INSERT INTO comment (email, pinID, content, createdDateTime) VALUES ('zbb7@gatech.edu', 1, 'GREAT', '2018-10-22 09:00:00.000000');
INSERT INTO comment (email, pinID, content, createdDateTime) VALUES ('zbb7@gatech.edu', 1, 'DAY', '2018-10-22 09:00:00.000000');


-- BoardPassword
CREATE TABLE boardpassword (
        email varchar(100) NOT NULL,
        boardID int NOT NULL,
        password varchar(50) NOT NULL,
        PRIMARY KEY (email, boardID, password),
        FOREIGN KEY (email) REFERENCES users (email),
        FOREIGN KEY (boardID) REFERENCES corkboard (boardID));

INSERT INTO boardpassword (email, boardID, password) VALUES ('lchen427@gatech.edu', 2, '1234');
INSERT INTO boardpassword (email, boardID, password) VALUES ('zbb7@gatech.edu', 7, '1234');
INSERT INTO boardpassword (email, boardID, password) VALUES ('mprior6@gatech.edu', 13, '1234');
