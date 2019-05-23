# Docker Set Up
To run the application, run these commands:

`docker compose build`

`docker compose up`

Go to localhost:5000

For Windows:

`docker-compose build`

`docker-compose up`

# Populate the data in the DATABASE
Go to the mysql/sql-scripts/CreateTable.sql and read the sql command to see what data is
added.  


# View the data in the DATABASE
to look at DB:
`docker exec -it corkboardit_db_1 mysql -p -e 'SELECT * from users;' cs6400_fa18_team074`
