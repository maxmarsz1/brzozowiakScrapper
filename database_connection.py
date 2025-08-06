import mysql.connector


def connection(host, login, password):
    mydb = mysql.connector.connect(
        host = host,
        user = login,
        password = password
    )
    return mydb


def init(cursor):
    try:
        cursor.execute("use brzozowiak")
        print("Database is present.")
        
    except Exception as e:
        print(e)

        print("Creating database: brzozowiak")
        cursor.execute("create database brzozowiak")
        cursor.execute("use brzozowiak")

    
    cursor.execute("use brzozowiak")
    cursor.execute('show tables')
        
    cursor.fetchall()
    if not cursor.rowcount:
        print("Creating table: offers")
        cursor.execute("""create table offers (
            id int PRIMARY KEY,
            url VARCHAR(255),
            title VARCHAR(255),
            price INT,
            image VARCHAR(255),
            description TEXT,
            date DATE,
            equipment VARCHAR(255),
            brand VARCHAR(255),
            model VARCHAR(255),
            year INT,
            fuel VARCHAR(64),
            km VARCHAR(10),
            color VARCHAR(64),
            body VARCHAR(64),
            transmission VARCHAR(64),
            mileage INT,
            capacity VARCHAR(10),
            location VARCHAR(255))""")
    else:
        print("Table is present.")
        


def add_offer(mysql, all_details: list):
    cursor = mysql.cursor()
    command = "insert into offers values"
    for details in all_details:
        print(f"Adding offer: {details['id']}")
        command += f"""(
            "{details['id']}",
            "{details['url']}",
            "{details['title']}",
            "{details['price']}",
            "{details['img']}",
            "{details['description']}",
            "{details['date']}",
            "{details['equipment']}",
            "{details['brand']}",
            "{details['model']}",
            "{details['year']}",
            "{details['fuel']}",
            "{details['km']}",
            "{details['color']}",
            "{details['body']}",
            "{details['transmission']}",
            "{details['mileage']}",
            "{details['capacity']}",
            "{details['location']}"),"""
            
    cursor.execute(command[:-1])
    mysql.commit()


def update_offer(mysql, details: dict):
    cursor = mysql.cursor()
    cursor.execute(f"select * from offers where id = {details['id']}")
    cursor.fetchall()
    if not cursor.rowcount:
        print(f"Offer with id: {details['id']} doesn't exists")
    else:
        print(f"Updating offer: {details['id']}")
        command = f"""update offers set
            url="{details['url']}",
            title="{details['title']}",
            price="{details['price']}",
            image="{details['img']}",
            description="{details['description']}",
            date="{details['date']}",
            equipment="{details['equipment']}",
            brand="{details['brand']}",
            model="{details['model']}",
            year="{details['year']}",
            fuel="{details['fuel']}",
            km="{details['km']}",
            color="{details['color']}",
            body="{details['body']}",
            transmission="{details['transmission']}",
            mileage="{details['mileage']}",
            capacity="{details['capacity']}",
            location="{details['location']}"
            where id="{details['id']}"
            """
        cursor.execute(command)
        mysql.commit()


def main():
    host = "localhost"
    login = "root"
    password = ""
    sql = connection(host, login, password)

    init(sql.cursor())


if __name__ == "__main__":
    main()