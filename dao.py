#!/usr/bin/python

import sha
import mysql.connector
from mysql.connector.errors import DatabaseError
from datetime import datetime
from sale import Sale
from config import *

SALE_COUNT = 3


def get_hashed_password(clear_password):
    return sha.new(clear_password).hexdigest()


class Dao:

    @staticmethod
    def get_connection():

        cnx = mysql.connector.connect(user=user,
                                      password=password,
                                      host=host,
                                      database=database)
        return cnx

    @staticmethod
    def create_user(user):
        connector = Dao.get_connection()
        cursor = connector.cursor()

        insert_user_query = ("INSERT INTO user "
                             "(fname, lname, email, password, mobile, gender, dob) "
                             "VALUES (%s, %s, %s, %s, %s, %s, %s)")

        hashed_password = get_hashed_password(user.password)
        user_info = (user.fname, user.lname, user.email, hashed_password, user.mobile, user.gender, user.dob)
        cursor.execute(insert_user_query, user_info)

        # Make sure data is committed to the database
        connector.commit()

        cursor.close()
        connector.close()

    @staticmethod
    def sale_by_user(sale):
        try:
            connector = Dao.get_connection()
            cursor = connector.cursor()

            insert_sale_info = ("INSERT INTO sale"
                                "(seller_id, startdate, enddate, address_line_one, address_line_two, city, state, country, pincode, start_price)"
                                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            user_info = (sale.seller_id,
                         sale.startdate,
                         sale.enddate,
                         sale.address_line_one,
                         sale.address_line_two,
                         sale.city,
                         sale.state,
                         sale.country,
                         sale.pincode,
                         sale.start_price)

            cursor.execute(insert_sale_info, user_info)

            # Make sure data is committed to the database
            connector.commit()

        except DatabaseError as e:
            print "\nError occurred while creating sale for the user", e

        try:
            cursor.close()
            connector.close()
        except:
            print "Error closing connection to database after creating sale record"

    @staticmethod
    def bid_by_user(bid):
        connector = Dao.get_connection()
        cursor = connector.cursor()

        insert_bid_info = ("INSERT INTO bid"
                           "(bidder_id, sale_id, bid_price, bid_date)"
                           "VALUES (%s, %s, %s, %s)")

        bid_info = (bid.bidder_id, bid.sale_id, bid.bid_price, bid.bid_date)
        cursor.execute(insert_bid_info, bid_info)

        # Make sure data is committed to the database
        connector.commit()

        cursor.close()
        connector.close()

    @staticmethod
    def get_all_valid_sales(index):
        connector = Dao.get_connection()
        cursor = connector.cursor(dictionary=True)
        now = datetime.now()

        offset = (index - 1) * SALE_COUNT
        query = "SELECT id, seller_id, startdate, enddate, address_line_one, address_line_two, city, state, country, pincode, start_price FROM sale WHERE enddate > %s AND startdate < %s ORDER BY startdate LIMIT %s, %s"

        cursor.execute(query, (now, now, offset, SALE_COUNT))
        #print "query executed is: ", cursor.statement, "\n\n"

        sales = {}
        rows = cursor.fetchall()
        for row in rows:
            sale = Sale(row["seller_id"],
                        row["startdate"],
                        row["enddate"].strftime('%m/%d/%Y'),
                        row["address_line_one"],
                        row["address_line_two"],
                        row["city"],
                        row["state"],
                        row["country"],
                        row["pincode"],
                        row["start_price"])

            sales[row["id"]] = sale

        return sales

    @staticmethod
    def get_user_id(email, password):
        connector = Dao.get_connection()
        cursor = connector.cursor()

        print email
        query = ("SELECT id FROM user "
                 " WHERE email = %s AND password = %s")

        hashed_password = get_hashed_password(password)
        cursor.execute(query, (email, hashed_password))
        # print "query executed is: ", cursor.statement

        user_id = None
        row = cursor.fetchone()
        if row:
            user_id = row[0]
            print "Found user and password with id=", user_id
        else:
            print "Found no user and password match"

        cursor.close()
        connector.close()

        return user_id

    @staticmethod
    def get_user_info_from_id(user_id):
        connector = Dao.get_connection()
        cursor = connector.cursor(dictionary=True)

        query = "SELECT fname, lname FROM user WHERE id = %s"

        cursor.execute(query, (user_id,))
        user_id_info = cursor.fetchone()

        '''if user_id_info:
            print "Found user and password with id=", user_id_info
        else:
            print "Found no user and password match"
        '''

        cursor.close()
        connector.close()

        return user_id_info

    @staticmethod
    def get_max_bid_price(sale_id):
        # select max(bid_price) as max_price from bid where sale_id=3;
        connector = Dao.get_connection()
        cursor = connector.cursor()

        print sale_id
        query = "select max(bid_price) as max_price from bid where sale_id = %s"

        cursor.execute(query, (sale_id,))
        # print "query executed is: ", cursor.statement

        max_price = None
        row = cursor.fetchone()
        if row:
            max_price = row[0]
            print "Max price for sale id %s is %s" % (sale_id, max_price)
        else:
            print "No max price for the sale"

        cursor.close()
        connector.close()

        return max_price

    @staticmethod
    def my_bid_details(bidder_id):

        connector = Dao.get_connection()
        cursor = connector.cursor(dictionary=True)

        query = ("SELECT bidder_id, MAX(bid_price) AS recent_bid_price, seller_id, start_price, startdate, "
                 "enddate, address_line_one, address_line_two, city, state, country, pincode FROM bid INNER JOIN sale "
                 "ON sale_id = sale.id "
                 "WHERE bidder_id=%s GROUP BY sale_id")

        cursor.execute(query, (bidder_id,))
        #print cursor.statement

        bids = cursor.fetchall()
        sales_list_of_dict = []
        for bid in bids:
            sale = Sale(bid["seller_id"],
                        bid["startdate"],
                        bid["enddate"].strftime('%m/%d/%Y'),
                        bid["address_line_one"],
                        bid["address_line_two"],
                        bid["city"],
                        bid["state"],
                        bid["country"],
                        bid["pincode"],
                        bid["start_price"])

            bid_sale_info_dict = {"sale": sale, "recent_bid_price": bid["recent_bid_price"]}
            sales_list_of_dict.append(bid_sale_info_dict)

        cursor.close()
        connector.close()
        '''
          [
            { "sale" : Saleobjcect1, "recent_bid_price" :500 },
            { "sale" : Saleobjcect2, "recent_bid_price" :120000 },
            { "sale" : Saleobjcect3, "recent_bid_price" :2300 },
          ]
        '''
        return sales_list_of_dict

    @staticmethod
    def get_sale_details(seller_id):
        # select max(bid_price) as max_price from bid where sale_id=3;
        connector = Dao.get_connection()
        cursor = connector.cursor(dictionary=True)

        query = ("SELECT id, seller_id, startdate, enddate, address_line_one, address_line_two, city, state, country, pincode, start_price" \
                " FROM sale where seller_id = %s")

        cursor.execute(query, (seller_id,))

        sales_from_database = cursor.fetchall()

        sales = {}
        for row in sales_from_database:
            sale = Sale(row["seller_id"],
                        row["startdate"],
                        row["enddate"].strftime('%m/%d/%Y'),
                        row["address_line_one"],
                        row["address_line_two"],
                        row["city"],
                        row["state"],
                        row["country"],
                        row["pincode"],
                        row["start_price"])
            sales[row['id']] = sale

        cursor.close()
        connector.close()

        '''
        {
            1 : salesObj1,
            2 : salesObj2,
            4 : saledObj3
        }
        '''
        return sales

    @staticmethod
    def my_active_sale_details(seller_id):

        connector = Dao.get_connection()
        cursor = connector.cursor(dictionary=True)
        now = datetime.now()
        query = "SELECT id, seller_id, startdate, enddate, address_line_one, address_line_two, city, state, country, pincode, start_price FROM sale " \
                "WHERE endstart > %s AND seller_id = %s"

        cursor.execute(query, (now, seller_id))

        sales_from_database = cursor.fetchall()

        sales = {}
        for row in sales_from_database:
            sale = Sale(row["seller_id"],
                        row["startdate"],
                        row["enddate"].strftime('%m/%d/%Y'),
                        row["address_line_one"],
                        row["address_line_two"],
                        row["city"],
                        row["state"],
                        row["country"],
                        row["pincode"],
                        row["start_price"])
            sales[row['id']] = sale

        cursor.close()
        connector.close()

        '''
        {
            1 : salesObj1,
            2 : salesObj2,
            4 : saledObj3
        }
        '''
        return sales

    @staticmethod
    def withdraw_sale(sale_id):
        connector = Dao.get_connection()
        cursor = connector.cursor()

        query = ("DELETE FROM sale WHERE id = %s")
        cursor.execute(query, (sale_id,))

        connector.commit()

        cursor.close()
        connector.close()

    @staticmethod
    def get_bids_for_completed_sales():
        connector = Dao.get_connection()
        cursor = connector.cursor(dictionary=True)

        query = ("SELECT MAX(bid.bid_price) AS final_bid_price, "
                 "ANY_VALUE(sale.start_price) AS start_price "
                 "FROM bid INNER JOIN sale ON bid.sale_id = sale.id "
                 "WHERE enddate <= %s GROUP BY bid.sale_id")

        now = datetime.now()
        cursor.execute(query, (now, ))

        rows = cursor.fetchall()

        sales_with_final_bid_list = []
        for row in rows:
            sale_with_final_bid_dict = {
                "earning": row["final_bid_price"] - row["start_price"]
            }
            sales_with_final_bid_list.append(sale_with_final_bid_dict)

        cursor.close()
        connector.close()

        return sales_with_final_bid_list