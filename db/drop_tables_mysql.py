import mysql.connector

conn = mysql.connector.connect(
    user="rj", password="Rodolfjohn25!", host="localhost", database="kafka"
)

c = conn.cursor()
c.execute(
    """
    DROP TABLE buying_products;
    DROP TABLE search_products;
    """
)


conn.close()
