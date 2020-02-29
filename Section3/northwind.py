#!/usr/bin/python3

import boto3
import csv
import matplotlib.pyplot as plt
import pandas as pd
import pymysql
import sys

from botocore.exceptions import NoCredentialsError

class DataGrokr:
	def __init__(self):
		#db = pymysql.connect("DBADDR", "DBUNAME", "DBPASS", "DBNAME")
		self.cursor = db.cursor()

	def list_products(self):
		self.cursor.execute("SELECT ProductName, COUNT(Products.ProductID) AS NumOfProducts FROM `Products`, OrderDetails WHERE OrderDetails.ProductID=Products.ProductID GROUP BY Products.ProductID ORDER BY NumOfProducts DESC;")
		rows = self.cursor.fetchall()

		if rows:
			res = list() #Empty list. Will be written to CSV later.

			col_names = list() #Empty list. Used to fetch the column names as first entry of CSV file.
			for i in self.cursor.description:
				col_names.append(i[0])

			res.append(col_names)
			for row in rows:
				res.append(row)

			openfile = open("query1.csv", "w") #Writing to CSV begins from here.
			myfile = csv.writer(openfile)
			myfile.writerows(res)
			openfile.close()

	def group_products(self):
		query = """SELECT Orders.OrderID,
				  CASE
				      WHEN ROUND(DATEDIFF("2000-01-01", BirthDate)/365,0) < 30 THEN 'Under 30'
				      WHEN ROUND(DATEDIFF("2000-01-01", BirthDate)/365,0) BETWEEN 31 AND 40 THEN '31-40'
				      WHEN ROUND(DATEDIFF("2000-01-01", BirthDate)/365,0) BETWEEN 41 AND 50 THEN '41-50'
				      WHEN ROUND(DATEDIFF("2000-01-01", BirthDate)/365,0) > 50 THEN 'Above 50'
				  END AS AgeRange
				  FROM Employees
				  LEFT JOIN Orders ON Orders.EmployeeID = Employees.EmployeeID
				  GROUP BY AgeRange, Orders.OrderID; """
		self.cursor.execute(query)
		rows = self.cursor.fetchall()

		if rows:
			res = list() #Empty list. Will be written to CSV later.

			col_names = list() #Empty list. Used to fetch the column names as first entry of CSV file.
			for i in self.cursor.description:
				col_names.append(i[0])

			res.append(col_names)
			for row in rows:
				res.append(row)

			openfile = open("query2.csv", "w") #Writing to CSV begins from here.
			myfile = csv.writer(openfile)
			myfile.writerows(res)
			openfile.close()

			df = pd.DataFrame(res)

			df.columns = ['AgeRange', 'OrderID']
			bins = [1,2,3,4] #ranges of data
			plt.xlabel('Age Range')
			plt.ylabel('Max number of orders')
			plt.hist(list(df['OrderID']),bins,histtype='bar',rwidth=0.8)
			plt.savefig("query2.png")

	def increase_tax(self):
		query = """ 
				SELECT Orders.OrderID, Customers.ContactName, Customers.Country, Orders.Freight, (CASE
				WHEN Customers.Country='USA' OR Customers.Country='Canada' THEN TRUNCATE(Orders.Freight+Orders.Freight*15/100,4)
				WHEN Customers.Country='France' OR Customers.Country='Germany' OR Customers.Country='Belgium' THEN TRUNCATE(Orders.Freight+Orders.Freight*10/100,4)
				ELSE TRUNCATE(Orders.Freight+Orders.Freight*5/100,4) END) AS NewFreight
				FROM `Customers`
				INNER JOIN Orders ON Orders.CustomerID = Customers.CustomerID;
				"""
		self.cursor.execute(query)
		rows = self.cursor.fetchall()

		if rows:
			res = list() #Empty list. Will be written to CSV later.

			col_names = list() #Empty list. Used to fetch the column names as first entry of CSV file.
			for i in self.cursor.description:
				col_names.append(i[0])

			res.append(col_names)
			for row in rows:
				res.append(row)

			openfile = open("query3.csv", "w") #Writing to CSV begins from here.
			myfile = csv.writer(openfile)
			myfile.writerows(res)
			openfile.close()
		db.close()

	def upload_bucket(self, local_file, bucket, s3_file):
		#ACCESS_KEY = ''
		#SECRET_KEY = ''

		s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
						aws_secret_access_key=SECRET_KEY)

		try:
			s3.upload_file(local_file, bucket, s3_file)
			print("Upload Successful")
			return True
		except FileNotFoundError:
			print("The file was not found")
			return False
		except NoCredentialsError:
			print("Credentials not available")
			return False

dg = DataGrokr()
dg.list_products()
dg.group_products()
dg.increase_tax()
files = ["query1.csv", "query2.csv", "query2.png", "query3.csv"]
for i in files:
	dg.upload_bucket(i, 'dg-assessment', '\shreyas_s\%s'%i)
