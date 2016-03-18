from tkinter import *
import quit
import session

class AutoTransactionPage(object):
	"""docstring for ClassName
	
		vehicle( serial_no, maker, model, year, color, type_id )
		owner(owner_id, vehicle_id, is_primary_owner)
		auto_sale( transaction_id,seller_id, buyer_id, vehicle_id, s_date, price )	
	
	"""
	def __init__(self, master):
		frame = Frame(master, width = 500, height = 500)
		frame.grid()
		self.frame = frame		
		self.successor = -1
		
		#This is where the user entered data gets stored
		self.formData = {}
		self.personalFormData = {}
		self.sin = {}
		self.primarySin = ""
		self.newOwnerIndex = 4
		self.addOwnerFormText = []
		self.addOwnerEntries = []
		self.personalEntries = []

		self.numForms = 0
		self.nextButton = None
		
		self.formText = ["transaction_id", "seller_id","buyer_id", "vehicle_id","s_date","price"]
        
		#Create the Entry Forms and display them
		self.forms = self.makeForm(frame)

		self.entries[4].insert(20, "(DD-MMM-YY)")

		self.pageTitle = self.makeTitle(frame, "New Auto Transaction", 0, 1)

		self.submitButton = Button(frame, text="Submit", command=self.submitCallBack)
		self.submitButton.grid(row=8, column=1)

		self.homeButton = Button(frame, text="Home", command=self.homeCB)
		self.homeButton.grid(row=8, column=2)

		self.quitButton = Button(frame, text="Quit", command=lambda:quit.quit_callback(self.frame))
		self.quitButton.grid(row=8, column=0)

		self.addOwnerButton = Button(self.frame, text="Add Buyer", command=self.AddNewOwner)
		self.addOwnerButton.grid(row=4, column=2)


	def homeCB(self):
		print("Home")
		self.successor = 0

	def submitCallBack(self):
		
		n=0
		for entry in self.entries:
				self.formData[self.formText[n]] = entry.get()
				n += 1

		self.sin[self.formData["buyer_id"]] = []
		self.primarySin = self.formData["buyer_id"]
		# Grab id from additional owners
		for entry in self.addOwnerEntries:
			self.sin[entry.get()] = []


		self.validateOwner()

		for value in self.sin.values():
			if not value[0]:
				self.numForms += 1

		#check transaction_id is unique:
		query = "SELECT transaction_id FROM auto_sale where transaction_id = '" + str(self.formData["transaction_id"] )+ "'"
		buyerValid = self.validateForm("SELECT sin FROM people where sin = '" + str(self.formData["buyer_id"] )+ "'")
		sellerValid = self.validateForm("SELECT sin FROM people where sin = '" + str(self.formData["seller_id"] )+ "'")
		vehicleValid = self.validateForm("SELECT serial_no FROM vehicle where serial_no = '" + str(self.formData["vehicle_id"] )+ "'")

		if( not self.validateForm(query)):
			print("transaction_id already exists")
		elif( sellerValid ):
			print("Seller does not exist")
		elif(vehicleValid):
			print("Vehicle not registered")	
		elif(not self.checkOwnership()):
			print("Seller does not own the vehicle")
		elif self.numForms > 0:
			print("Buyer not in database")
			#buyer doesnt exist and needs to be added
			# delete previous owner entry in database
			# update new owner entry in database
			print("Number of forms: " + str( self.numForms))
			# make form
			self.makePersonalForm(self.frame)
			self.addOwnerButton.config(state=DISABLED)
			self.submitButton.config(state=DISABLED)

			for entry in self.entries:
				entry.config(state=DISABLED)

			found = False
			for key in self.sin.keys():
				
				if (( not self.sin[key][0] ) and ( not found ) ):
					self.sin[key] = []
					self.personalEntries[0].insert(0, key)
					self.personalEntries[0].config(state=DISABLED)

					found = True
		else:
			print("all owners exist")

			# Insert into auto_sale
			self.submitSale()
         
	def validateForm(self, statement):                  
		rs = session.db.execute_sql(statement)
		print("rs: "+ str(rs))              
		if not rs:      
			print("NONE")           
			return True
		else: return False

	
	def checkOwnership(self):
		query = "SELECT * FROM owner where owner_id = " + self.formData["seller_id"] +  " and vehicle_id = " + self.formData["vehicle_id"]  	
		rs = session.db.execute_sql(query)	
		if rs: #seller does own vehicle
			return True
		else:
			return False
	
	def updateOwner(self):
		#delete old owner
		query = "DELETE FROM owner WHERE owner_id = " + self.formData["seller_id"] + " and vehicle_id = " + self.formData["vehicle_id"]
		session.db.passive_update(query)		
		# update new owner
		#owner(owner_id, vehicle_id, is_primary_owner)
		for key in self.sin.keys():
			if (self.primarySin == key):
				data = [(key, self.formData["vehicle_id"], "y")]
			else:
				data = [(key, self.formData["vehicle_id"], "n")]

			session.db.curs.executemany("INSERT INTO owner( owner_id, vehicle_id, is_primary_owner) " 
						"VALUES(:1, :2, :3)", data )
		
	def makeButton(self, parent, caption, width, row, column):
		button = Button(parent, text=caption)
		button.grid(row=row, column=column)
		return button

	def makeentry(self, parent, caption, width, row, column):
		Label(parent, text=caption, width=20, justify=RIGHT).grid(row=row,column=column[0])
		entry = Entry(parent)
		if width:
			entry.config(width=width)
			
		entry.grid(row=row, column=column[1], sticky=E)
		return entry

	def makeTitle(self, parent, text, row, column):
		title = Label(parent, text=text)
		title.grid(row=row, column=column)
		return title

	def makeForm(self, parent):
		baseRow = 2

		self.entries = []
		for text in self.formText:
				self.entries.append(self.makeentry(parent, text, 40, baseRow, [0,1]))
				baseRow += 1


	def quit(self):
		self.frame.destroy()


	def makePersonalForm(self, parent):
		self.personalFormText = ["sin", "name", "height", "weight", "eyecolor", "haircolor", "addr", "gender", "birthday"]
		
		baseRow = 30
		for text in self.personalFormText:
			self.personalEntries.append(self.makeentry(parent, text, 40, baseRow, [0,1]),)
			baseRow += 1  

		self.nextButton = self.makeButton(self.frame, "Finalize", 10, 50, 1)
		if self.numForms > 0:
			self.nextButton.config(command=self.saveAndClear, text="Next")
		else:
			self.nextButton.config(command=self.submitPersonal)

	def submitSale(self):
		data = [(self.formData["transaction_id"], self.formData["seller_id"], self.formData["buyer_id"], self.formData["vehicle_id"], self.formData["s_date"],self.formData["price"])]		 	
		session.db.curs.executemany("INSERT INTO auto_sale(transaction_id,seller_id, buyer_id, vehicle_id, s_date, price) " 
				"VALUES(:1, :2, :3, :4, :5, :6)", data)
		self.updateOwner()			
		
		print("Transaction complete")
		
		session.db.curs.connection.commit()
		self.successor = 0;
		self.quit()

	def submitPersonal(self):
		print("Last Step")

		for key, value in self.sin.items():
			print(key, value)

		self.updatePeople()
		self.submitSale()

	def displayResults(self, text, row, column):
		resultText = text
		self.searchResults = Label(self.frame, text=resultText)
		self.searchResults.grid(row=row, column=column)	

	def AddNewOwner(self):
		print("Owner Added")
		text = "Additional Buyer " + str(self.newOwnerIndex-3)
		self.addOwnerFormText.append(text)
		self.addOwnerEntries.append(self.makeentry(self.frame, text, 15, self.newOwnerIndex, [3,4])) 
		self.newOwnerIndex += 1	

	def validateOwner(self):
		for key in self.sin.keys():
			query = "SELECT sin from people where sin = " + str(key)
			if (self.validateForm(query)):
				self.sin[key].append(False) # not in database
			else:
				self.sin[key].append(True) # in database	

	def saveAndClear(self):
		"""
			sin: {1:[False], 2: [False]}
					{1:["", "" ...], 2: [False]}
		"""
		#print(self.personalEntries[1].get())
		currentKey = self.personalEntries[0].get()
		print(currentKey)
		for entry in self.personalEntries:
			self.sin[currentKey].append(entry.get())
		print(currentKey, self.sin[currentKey])
		self.personalEntries[0].config(state=NORMAL)

		found = False
		for key in self.sin.keys():
			if (( not self.sin[key][0] ) and ( not found ) ):
				self.sin[key] = []
				self.personalEntries[0].delete(0, END)
				self.personalEntries[0].insert(0, key)
				self.personalEntries[0].config(state=DISABLED)

				found = True
	

		if self.numForms == 1:
			self.nextButton.config(command=self.submitPersonal, text="Finalize")

			for entry in self.personalEntries:
				entry.config(state=DISABLED)		
		else:
			#clear forms
			self.numForms -= 1
		
		for entry in self.personalEntries:
			entry.delete(0,END)

	def updatePeople(self):
		"""
			build 
		"""

		for key in self.sin.keys():
			#print("key: " + str(key) + "val: " +  str(self.sin[key]))
			if len(self.sin[key]) > 2:
				data = [(self.sin[key][0], self.sin[key][1], self.sin[key][2], self.sin[key][3], self.sin[key][4], self.sin[key][5], self.sin[key][6], self.sin[key][7], self.sin[key][8])]		
				session.db.curs.executemany("INSERT INTO people( sin, name, height, weight, eyecolor, haircolor, addr, gender, birthday) " 
							"VALUES(:1, :2, :3, :4, :5, :6, :7, :8, :9)", data )