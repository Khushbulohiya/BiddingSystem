#!/usr/bin/python

class Sale:
    def __init__(self, seller_id, startdate, enddate, address_line_one, address_line_two, city, state, country, pincode, start_price):
        self.seller_id = seller_id
        self.address_line_one = address_line_one
        self.address_line_two = address_line_two
        self.city = city
        self.state = state
        self.country = country
        self.pincode = pincode
        self.start_price = start_price
        self.startdate = startdate
        self.enddate = enddate