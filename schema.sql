-- CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
CREATE USER IF NOT EXISTS joe@localhost IDENTIFIED BY '123';


DROP DATABASE IF EXISTS `cs6400_fa18_team074`;
SET default_storage_engine=InnoDB;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;


CREATE DATABASE IF NOT EXISTS cs6400_fa18_team074
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;
USE cs6400_fa18_team074;


GRANT SELECT, INSERT, UPDATE, DELETE, FILE ON *.* TO
'joe'@'localhost';
GRANT ALL PRIVILEGES ON `joe`.* TO 'joe'@'localhost';
GRANT ALL PRIVILEGES ON `cs6400_fa18_team074`.* TO 'joe'@'localhost';
FLUSH PRIVILEGES;


-- Tables
CREATE TABLE User (
        email varchar(100) NOT NULL,
        pin varchar(4) NOT NULL,
        first varchar(50) NOT NULL,
        last varchar(50) NOT NULL,
        PRIMARY KEY (email));


CREATE TABLE Follow (
        followerEmail varchar(100) NOT NULL,
        followeeEmail varchar(100) NOT NULL,
        PRIMARY KEY (followerEmail, followeeEmail),
        FOREIGN KEY (followerEmail) REFERENCES User (email),
        FOREIGN KEY (foloweeEmail) REFERENCES User (email));


CREATE TABLE Watch (
        email varchar(100) NOT NULL,
        boardOwnerEmail varchar(100) NOT NULL,
        boardID int NOT NULL,
        PRIMARY KEY (email, boardID, boardOwnerEmail),
        FOREIGN KEY (email) REFERENCES User (email),
        FOREIGN KEY (boardOwnerEmail) REFERENCES User (email),
        FOREIGN KEY (boardID) REFERENCES CorkBoard (boardID));




CREATE TABLE CorkBoard (
        email varchar(100) NOT NULL,
        boardID int NOT NULL AUTO_INCREMENT,
        title varchar(50) NOT NULL,
        categoryName varchar(50) NOT NULL,
        lastUpdateTime datetime NOT NULL,
        boardType varchar(7) NOT NULL,
        PRIMARY KEY (email, boardID),
        FOREIGN KEY (email) REFERENCES User (email),
        FOREIGN KEY (categoryName) REFERENCES Category (name));


CREATE TABLE BoardPassword (
        email varchar(100) NOT NULL,
        boardID int NOT NULL,
        password varchar(50) NOT NULL,
        PRIMARY KEY (email, boardID, password),
        FOREIGN KEY (email) REFERENCES User (email),
        FOREIGN KEY (boardID) REFERENCES CorkBoard (boardID));


CREATE TABLE Category (
        name varchar(50) NOT NULL,
        PRIMARY KEY (name));


CREATE TABLE PushPin (
        email varchar(100) NOT NULL,
        boardID int NOT NULL,
        pinID int NOT NULL AUTO_INCREMENT,
        url varchar(250) NOT NULL,
        description varchar(200) NOT NULL,
        createdDateTime datetime NOT NULL,
        PRIMARY KEY (email, boardID, pinID),
        FOREIGN KEY (boardID) REFERENCES CorkBoard (boardID),
        FOREIGN KEY (email) REFERENCES User (email));


CREATE TABLE PushPinTag (
        email varchar(100) NOT NULL,
        boardID int NOT NULL,
        pinID int NOT NULL,
        tag varchar(20) NOT NULL,
        PRIMARY KEY (email, boardID, pinID, tag),
        FOREIGN KEY (pinID) REFERENCES PushPin (pinID),
        FOREIGN KEY (boardID) REFERENCES CorkBoard (boardID),
        FOREIGN KEY (email) REFERENCES User (email));


CREATE TABLE Comment (
        email varchar(100) NOT NULL,
        boardOwnerEmail varchar(100) NOT NULL,
        boardID int NOT NULL,
        pinID int NOT NULL,
        commentID int NOT NULL AUTO_INCREMENT,
        text varchar(500) NOT NULL,
        createdDateTime datetime NOT NULL,
        PRIMARY KEY (email, pinID, commentID, boardOwnerEmail, boardID),
        FOREIGN KEY (email) REFERENCES User (email),
        FOREIGN KEY (pinID) REFERENCES PushPin (pinID),
        FOREIGN KEY (boardID) REFERENCES CorkBoard (boardID),
        FOREIGN KEY (boardOwnerEmail) REFERENCES User (email));


CREATE TABLE Like (
        email varchar(100) NOT NULL,
        pinOwnerEmail varchar(100) NOT NULL,
        boardID int NOT NULL,
        pinID int NOT NULL,
        PRIMARY KEY (pinOwnerEmail, pinID, boardID, email),
        FOREIGN KEY (pinID) REFERENCES PushPin (pinID),
        FOREIGN KEY (email) REFERENCES User (email),
        FOREIGN KEY (boardID) REFERENCES CorkBoard (boardID),
        FOREIGN KEY (pinOwnerEmail) REFERENCES User (email));
