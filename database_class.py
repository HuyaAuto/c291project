import sys
import cx_Oracle # the package used for accessing Oracle in Python
import getpass # the package for getting password from user without displaying it


class Database():
	"""docstring for DataBase"""
	def __init__(self):

		# get username
		#user = input("Username [%s]: " % getpass.getuser())
		#if not user:
				#user=getpass.getuser()
		
		# get password
		#pw = getpass.getpass()

		# The URL we are connnecting to
		conString=''+"" +'/' + "" +'@gwynne.cs.ualberta.ca:1521/CRS'
		
		self.connection = cx_Oracle.connect(conString)

		# create a cursor 
		self.curs = self.connection.cursor()

	def close_connection(self):
		print("Closing Database")
		self.curs.close()
		self.connection.close()

	def passive_update(self, statement):

		try:        
			#curs = self.connection.cursor()
			# Execute the desired statement 
			self.curs.execute(statement)
			self.connection.commit()
			return True

		except cx_Oracle.DatabaseError as exc:
			error, = exc.args
			print( sys.stderr, "Oracle code:", error.code)
			print( sys.stderr, "Oracle message:", error.message)
			return False


	def execute_sql(self, statement):

		try:
			# Establish a connection in Python
  
			# create a cursor 
			curs = self.connection.cursor()

			# Execute the desired statement 
			curs.execute(statement)
			self.connection.commit()

			# get all data and print it
			resultRows = curs.fetchall()

			# getting metadata
			resultRowsDescription = curs.description

			return resultRows


		except cx_Oracle.DatabaseError as exc:
			error, = exc.args
			print( sys.stderr, "Oracle code:", error.code)
			print( sys.stderr, "Oracle message:", error.message)
			return [None, None]


