from tkinter import *
import quit
import session

class VehicleRegPage(object):
	"""docstring for ClassName
		Page process flow: 
			1. Check serial_no is not already in database
			2. Check owner is in database
				2.1. TRUE: --> Finalize
				2.2. FALSE: --> Add person in database
					2.2.1. Add in people table
					2.2.2. Add in owner table.
					2.2.3. --> Finalize
			3. Finalze
	"""
	def __init__(self, master):
		frame = Frame(master, width = 500, height = 500)
		frame.grid()
		self.frame = frame
		self.successor = -1
		self.newOwnerIndex = 20
		self.addOwnerFormText = []
		self.addOwnerEntries = []
		self.personalEntries = []
		self.sin = {}
		self.primarySin = ""

		self.formData = {}
		self.ownerFormData = {}
		self.personalFormData = {}
		self.additionalOwnerFormData = {}
		self.numForms = 0
		self.nextButton = None

		self.formText = ["serial_no", "maker", "model", "year", "color", "type_id"]
		self.makeForm(frame)
		self.pageTitle = self.makeTitle(frame, "Register a New Vehicle", 0, 1)

		self.submitButton = Button(frame, text="Submit", command=self.submitVehicleCallback)
		self.submitButton.grid(row=10, column=1)

		self.homeButton = Button(frame, text="Home", command=self.homeCallback)
		self.homeButton.grid(row=10, column=2)

		self.quitButton = Button(frame, text="Quit", command=lambda:quit.quit_callback(self.frame))
		self.quitButton.grid(row=10, column=0)
	
	def homeCallback(self):

		self.successor = 0

	def submitVehicleCallback(self):
		n=0
		for entry in self.entries:
			self.formData[self.formText[n]] = entry.get()
			n+=1

		querry = "SELECT serial_no FROM vehicle where serial_no = '" + str(self.formData["serial_no"] )+ "'"     
		validation = False
		notNull = True
		if self.formData["serial_no"] and notNull:      
			validation = self.validateForm(querry)

		for entry in self.entries:
			if not entry.get():
				entry.insert(0,"null")

		print(self.entries[0].get())
		if self.entries[0].get() == "null":
			print("Serial_no cannot be null")
			notNull = False 
		
		if validation and notNull:

			for entry in self.entries:
				entry.config(state=DISABLED)
				
			self.submitButton.config(state=DISABLED)

			self.makeOwnerForm(self.frame)
			self.displayText("Please Enter Owner Information", 23, 1)

			self.ownerEntries[1].insert(0, self.formData["serial_no"])

			self.addOwnerButton = Button(self.frame, text="Add Owner", command=self.AddNewOwner)
			self.addOwnerButton.grid(row=20, column=2)
		
			self.submitOwnerButton = Button(self.frame, text="Submit Owner Data", command=self.submitOwnerCallback)
			self.submitOwnerButton.grid(row=24, column=1)
		elif notNull:
			print("Vehicle already registered")
		
	
	def validateForm(self, statement):                  
		rs = session.db.execute_sql(statement)
		print("rs: "+ str(rs))              
		if not rs:      
			print("NONE")           
			return True
		else: return False

	def submitOwnerCallback(self):
		self.addOwnerButton.config(state=DISABLED)
		self.submitOwnerButton.config(state=DISABLED)
		self.fetchOwnerFormData()
		self.fetchAdditionalOwnerFormData()
		self.sin[self.ownerFormData["owner_id"]] = []
		self.primarySin = self.ownerFormData["owner_id"]

		#print(self.personalEntries[0])
		
		# Grab id from additional owners
		for entry in self.addOwnerEntries:
			self.sin[entry.get()] = []

		self.validateOwner()

		for value in self.sin.values():
			if not value[0]:
				self.numForms += 1

		print("Number of forms: " + str( self.numForms))
		if self.numForms > 0:
			# make form
			self.makePersonalForm(self.frame, 30)

			found = False
			for key in self.sin.keys():
				
				if (( not self.sin[key][0] ) and ( not found ) ):
					self.sin[key] = []
					self.personalEntries[0].insert(0, key)
					self.personalEntries[0].config(state=DISABLED)

					found = True
		else:
			print("all owners exist")

			# Insert into vehicle table
			self.updateVehicle()

			# Insert into Owner table
			self.updateOwner()

			session.db.curs.connection.commit()
			self.successor = 0; # Go back home after
			self.quit()


	def submitPersonalCallback(self):
		print("Last Step")

		for key, value in self.sin.items():
			print(key, value)
		
		# Insert into vehicle table
		self.updateVehicle()
		
		# Insert into people table
		self.updatePeople()

		# Insert into Owner table
		self.updateOwner()

		session.db.curs.connection.commit()
		self.successor = 0; # Go back home after
		self.quit()
	
	def displayText(self, text, row, column):
		resultText = text
		self.searchResults = Label(self.frame, text=resultText)
		self.searchResults.grid(row=row, column=column)

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

	def quit(self):
		self.frame.destroy()

	def makeForm(self, parent):
		baseRow = 2
		self.entries = []
		for text in self.formText:
			self.entries.append(self.makeentry(parent, text, 40, baseRow, [0,1]),)
			baseRow += 1
	
	def makePersonalForm(self, parent, baseRow):
		self.personalFormText = ["sin", "name", "height", "weight", "eyecolor", "haircolor", "addr", "gender", "birthday"]
		
		baseRow = 30
		for text in self.personalFormText:
			self.personalEntries.append(self.makeentry(parent, text, 40, baseRow, [0,1]),)
			baseRow += 1  

		self.nextButton = self.makeButton(self.frame, "Finalize", 10, 50, 2)
		if self.numForms > 0:
			self.nextButton.config(command=self.saveAndClear, text="Next")
		else:
			self.nextButton.config(command=self.submitPersonalCallback)

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
			self.nextButton.config(command=self.submitPersonalCallback, text="Finalize")

			for entry in self.personalEntries:
				entry.config(state=DISABLED)		
		else:
			#clear forms
			self.numForms -= 1
		
		for entry in self.personalEntries:
			entry.delete(0,END)


	def makeOwnerForm(self, parent):
		self.ownerFormText = ["owner_id", "vehicle_id"]
		baseRow = 20
		self.ownerEntries = []
		for text in self.ownerFormText:
			self.ownerEntries.append(self.makeentry(parent, text, 40, baseRow, [0,1]),)
			baseRow += 1       

	def AddNewOwner(self):
		print("Owner Added")
		text = "Additional Owner " + str(self.newOwnerIndex-19)
		self.addOwnerFormText.append(text)
		self.addOwnerEntries.append(self.makeentry(self.frame, text, 40, self.newOwnerIndex, [3,4])) 
		self.newOwnerIndex += 1

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
	def updateOwner(self):
		for key in self.sin.keys():
			if (self.primarySin == key):
				data = [(key, self.ownerFormData["vehicle_id"], "y")]
			else:
				data = [(key, self.ownerFormData["vehicle_id"], "n")]

			session.db.curs.executemany("INSERT INTO owner( owner_id, vehicle_id, is_primary_owner) " 
						"VALUES(:1, :2, :3)", data )

	def updateVehicle(self):
		data = [(self.formData["serial_no"], self.formData["maker"], self.formData["model"], self.formData["year"], self.formData["color"],self.formData["type_id"])]
		print("vehicle data: " + str(data))
		session.db.curs.executemany("INSERT INTO vehicle( serial_no, maker, model, year, color, type_id) " 
					"VALUES(:1, :2, :3, :4, :5, :6)", data )

	def fetchOwnerFormData(self):
		n=0
		for entry in self.ownerEntries:
			self.ownerFormData[self.ownerFormText[n]] = entry.get()
			n+=1

	def fetchAdditionalOwnerFormData(self):
		n=0
		for entry in self.addOwnerEntries:
			self.additionalOwnerFormData[self.addOwnerFormText[n]] = entry.get()
			n+=1

	def fetchPersonalFormData(self):
		n=0
		for entry in self.personalEntries:
			self.personalFormData[self.personalFormText[n]] = entry.get()			
			if not entry.get():
				entry.insert(0,"null")
			n+=1

	def addPersonalData(self):
		self.submitOwnerButton.config(state=DISABLED)

		self.makePersonalForm(self.frame, 30)
		self.displayText("Please Enter Personal Information", 39, 1)

		#Copy owner_id to SIN field of people 
		self.personalEntries[0].insert(0, self.ownerFormData["owner_id"])

		self.submitButton2 = Button(self.frame, text="Submit Personal Data", command=self.submitPersonalCallback)
		self.submitButton2.grid(row=50, column=1)		

	def validateOwner(self):
		for key in self.sin.keys():
			query = "SELECT sin from people where sin = " + str(key)
			if (self.validateForm(query)):
				self.sin[key].append(False) # not in database
			else:
				self.sin[key].append(True) # in database
		
