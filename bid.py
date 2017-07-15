#!/usr/bin/python

class Bid:
	def __init__(self, bidder_id, sale_id, bid_price, bid_date):
		self.bidder_id = bidder_id
		self.sale_id = sale_id
		self.bid_price = bid_price
		self.bid_date = bid_date.date()