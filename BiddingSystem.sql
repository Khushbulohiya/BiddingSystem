DROP DATABASE IF EXISTS `BiddingSystem`;

CREATE DATABASE `BiddingSystem`;
USE `BiddingSystem`;

CREATE TABLE `user`
(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    fname VARCHAR(30) NOT NULL,
    lname VARCHAR(30) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE KEY,
    password VARCHAR(50) NOT NULL,
    mobile VARCHAR(15) NOT NULL,
    gender VARCHAR(8),
    dob DATETIME NOT NULL
);

CREATE TABLE sale
(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    seller_id INT REFERENCES user(id) ON DELETE CASCADE,
    startdate DATETIME NOT NULL,
    enddate DATETIME NOT NULL,
    address_line_one VARCHAR(50),
    address_line_two VARCHAR(50),
    city VARCHAR(30) NOT NULL,
    state VARCHAR(30) NOT NULL,
    country VARCHAR(30) NOT NULL,
    pincode VARCHAR(12) NOT NULL,
    start_price DOUBLE NOT NULL
);

CREATE TABLE bid
(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    bidder_id INT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    sale_id INT NOT NULL REFERENCES sale(id) ON DELETE CASCADE,
    bid_price DOUBLE NOT NULL,
    bid_date DATETIME NOT NULL
);

