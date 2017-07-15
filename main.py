#!/usr/bin/python

'''
Khushbu Lohiya - klohiya47@gmail.com

'''

import re
import sys
import argparse
import getpass
from datetime import datetime
from dao import Dao
from user import User
from sale import Sale
from bid import Bid
from config import admin_password, commision_percentage

parser = argparse.ArgumentParser()
parser.add_argument("-admin")
parser.add_argument("-password")

def pretty_print(sale):
    user_info = Dao.get_user_info_from_id(sale.seller_id)
    if not user_info:
        user_info = {"fname": "Unknown", "lname": "Unknown"}
    print "------------------------------"
    print "Seller Name: %s %s" % (user_info['fname'], user_info['lname'])
    print "Address: %s, %s, %s, %s, %s - %s" % (
        sale.address_line_one, sale.address_line_two, sale.city, sale.state, sale.country, sale.pincode)
    print "Start Date: %s" % sale.startdate.date()
    print "End Date: %s" % sale.enddate
    print "Start Price: $%s" % sale.start_price
    print "------------------------------\n"


'''
 Create user account by taking input from user, 
 and validating it before creating the account
'''
def create_account():
    
    fname = raw_input("Enter first name:")
    lname = raw_input("Enter last name:")
    email = raw_input("Enter email address in the form kk@email.com:")
    
    # reg ex match to validate mail address
    match = re.match('^[a-zA-Z0-9_\-]+[a-zA-Z0-9_\-]+@[a-zA-Z]+.[a-zA-Z]{2,4}$', email)
    
    # if the reg ex match fails the email address entererd is incorrect,
    # return w/o creating the account as email address is not valid
    if not match:
        print "\nInvalid email address %s" %email
        return
    
    # get password from user, with the help of getpass,
    # we are getting the password from user w/o having the password appear on the
    # terminal (wink)
    password = getpass.getpass(stream=sys.stderr)
    print "your entered password is: ", password

    mobile = raw_input("Enter mobile number. it should be in the format +1 (1-9)xxxxxxxxx or +91 (1-9)xxxxxxxxx:")

    # regex to validate the mobile number entered by the user
    match = re.match('^((\+\d{1,2}|1)[\s.-]?)?\(?[1-9](?!11)\d{2}\)?[\s.-]?\d{3}[\s.-]?\d{4}$|^$', mobile)

    #first part for area code can be 1, +1, +91, 91
    #second part area code start between 1-9 and 2 and 3rd digit cannot have digit 11
    #third part have 3 digits = exchange number
    #Fourt part have 4 digits = subscriber number

    # if the mobile number does not match our regex, we are not happy with user's input
    # so return w/o creating the account
    if not match:
        print "\nInvalid phone  number %s" % mobile
        return

    gender = raw_input("Enter gender:")
    dob_input = raw_input("Enter date of birth in mm/dd/yyyy:")

    # validate the birthday by creating the datetime object,
    # if exception is thrown print error and return w/o creating the account
    try:
        dob = datetime.strptime(dob_input, "%m/%d/%Y").date()
    except ValueError:
        print "Please enter date in the format mm/dd/yyyy"
        return

    # All went well, lets create the account now
    user = User(fname, lname, email, password, mobile, gender, dob)
    Dao.create_user(user)


def add_sale():
    email = raw_input("Enter your email address:")
    password = getpass.getpass(stream=sys.stderr)

    seller_id = Dao.get_user_id(email, password)
    if seller_id == None:
        return

    startdate = datetime.now().date()
    enddate_input = raw_input("Please enter end date time in correct format mm/dd/yyyy: ")
    try:
        enddate = datetime.strptime(enddate_input, "%m/%d/%Y").date()
    except ValueError:
        print "Please enter date in the format mm/dd/yyyy"
        return

    address_line_one = raw_input("Enter address line one:")
    address_line_two = raw_input("Enter address line two:")
    city = raw_input("Enter city:")
    state = raw_input("Enter state:")
    country = raw_input("Enter country:")
    pincode = raw_input("Enter pincode:")
    match = re.match('^\\d{5}(-\\d{4})?$', pincode)

    if not match:
        print "\nInvalid pincode %s. It should be in the format xxxxxx-xxxx" % pincode
        return
    start_price = raw_input("Enter start price:")

    sale = Sale(seller_id, startdate, enddate, address_line_one, address_line_two, city, state, country, pincode,
                start_price)
    Dao.sale_by_user(sale)


def put_bid():
    # start with index 1 means page 1; each page will print 5 results
    index = 1
    sales = {}
    while True:

        # get sales for page number index from database
        sales_from_db_for_index = Dao.get_all_valid_sales(index)

        # increase index to goto next page if user selects 'y' below
        index += 1

        # only if there are any sales from database we do things
        # inside this if
        if sales_from_db_for_index:

            # add sales read from database to sales dictionary
            sales.update(sales_from_db_for_index)

            # print the sales read from database call above

            for key in sales_from_db_for_index:
                print "Sale Id: ", key, "\n",
                pretty_print(sales_from_db_for_index[key])

            # ask user if he should would like to get more sale options
            input = raw_input("More sale options: y/n: ")

            # if the user does not enter 'y', break from the loop
            if input != "y":
                break

        else:
            break

    # if there are no sales at all, we return
    # there is nothing the user can bid on. :)
    if not sales:
        print "No sales found\n"
        return

    email = raw_input("Enter your email address:")
    password = getpass.getpass(stream=sys.stderr)

    bidder_id = Dao.get_user_id(email, password)

    try:
        sale_id = int(raw_input("Enter sale id to bid on: "))
    except ValueError as e:
        print "Invalid input for sale id"
        return

    if sale_id not in sales:
        print "Invalid sale id entered"
        return

    max_bid_price = Dao.get_max_bid_price(sale_id)

    if max_bid_price == None:
        max_bid_price = sales[sale_id].start_price

    bid_price = raw_input("Enter bid price greater than %s:" % (max_bid_price))
    if float(bid_price) < max_bid_price:
        print "Error, invalid price; amount should be greter than %s" % (max_bid_price)
        return

    bid_date = datetime.now()

    bid = Bid(bidder_id, sale_id, bid_price, bid_date)
    Dao.bid_by_user(bid)


def view_my_bids():
    email = raw_input("Enter your email address:")
    password = getpass.getpass(stream=sys.stderr)

    mybid_id = Dao.get_user_id(email, password)
    if not mybid_id:
        return

    '''
      [
        { "sale" : Saleobjcect1, "recent_bid_price" :500 },
        { "sale" : Saleobjcect2, "recent_bid_price" :120000 },
        { "sale" : Saleobjcect3, "recent_bid_price" :2300 },
      ]
    '''
    bid_sale_info_list = Dao.my_bid_details(mybid_id)

    for bid_sale_info_dict in bid_sale_info_list:
        print "--------------------------------"
        print "Your Recent bid: $", bid_sale_info_dict["recent_bid_price"]
        print "SALE INFO"
        pretty_print(bid_sale_info_dict['sale'])


def view_my_sales():
    email = raw_input("Enter your email address:")
    password = getpass.getpass(stream=sys.stderr)

    seller_id = Dao.get_user_id(email, password)
    if seller_id == None:
        return

    '''
       {
           1 : salesObj1,
           2 : salesObj2,
           4 : saledObj3
       }
    '''
    sales_dict = Dao.get_sale_details(seller_id)

    if not sales_dict:
        print "No sales found"
        return

    for sale_id in sales_dict:
        print "Sale id: %s" % sale_id
        pretty_print(sales_dict[sale_id])

    return sales_dict


def withdraw_my_sales():
    email = raw_input("Enter your email address:")
    password = getpass.getpass(stream=sys.stderr)

    seller_id = Dao.get_user_id(email, password)
    if seller_id == None:
        return

    sales_dict = Dao.my_active_sale_details(seller_id)

    if not sales_dict:
        print "No sales found"
        return

    for sale_id in sales_dict:
        print "Sale id: %s" % sale_id
        pretty_print(sales_dict[sale_id])

    with_draw_sale_id = raw_input("Please enter sale id to withdraw: ")
    if int(with_draw_sale_id) not in sales_dict:
        print "Invalid sale id entered to withdraw"
        return

    Dao.withdraw_sale(with_draw_sale_id)
    print "Sale withdrawn successfully"
    pretty_print(sales_dict[int(with_draw_sale_id)])

    return sales_dict


def print_menu():
    print "\n********* MENU *********"
    print "1. Create Account"
    print "2. Add Sale"
    print "3. Bid"
    print "4. View my Bids"
    print "5. View my Auctions"
    print "6. Withdraw my Auction"
    print "7. Exit"


def get_commission():
    sales_with_final_bid_list = Dao.get_bids_for_completed_sales()

    total_sales = 0
    total_amount = float(0.0)
    if sales_with_final_bid_list:
        for sales_with_final_bid_dict in sales_with_final_bid_list:
            total_amount = total_amount + float(sales_with_final_bid_dict["earning"])
            total_sales += 1

    commission = (commision_percentage) * total_amount / 100.00
    print "Rita's commission for %d sales is $%.3f" %(total_sales, commission)

'''
Program starts here
'''
if __name__ == "__main__":
    args = parser.parse_args()

    if args.admin:
        if args.admin == "rita":
            if args.password == admin_password:
                get_commission()
            else:
                print "Invalid admin password"
        else:
            print "Invalid admin user %s" %args.u
    else:
        while True:
            print_menu()
            input = raw_input("\nPlease Enter input: ")
            if input == "1":
                create_account()
            elif input == "2":
                add_sale()
            elif input == "3":
                put_bid()
            elif input == "4":
                view_my_bids()
            elif input == "5":
                view_my_sales()
            elif input == "6":
                withdraw_my_sales()
            elif input == "7":
                break
            else:
                print "Invalid input, please enter valid input"
                break

    print "\nThank you for using our sale and bidding system!!\nSee you soon!!\n\n"
