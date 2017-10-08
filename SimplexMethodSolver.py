import numpy as np

#rows are stored as dictionaries in an array 2D array 1st dimension is iteration, second dimension is rows
class SimplexMethodSolver():
	SLACK_VAR_NAMES = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10"]
	def __init__(self, constraints, objectiveFunction):
		self.constraints = constraints

		#if the objective function does not contain a right side (RHS) then set it to zero
		if "RHS" not in objectiveFunction:
			objectiveFunction["RHS"] = 0
		self.objectiveFunction = objectiveFunction

		self.numSlack = 0

		self.table = []
		self.table.append([])
		self.table[0].append(objectiveFunction)
		
		for rowIndex, constraint in enumerate(constraints):
			self.table[0].append(constraint)

		#NEED: normalize function that add zero columns to non existant variables
		self.addSlackVariables()

		print(self.table[0])
	


	#should be run before anything else
	def addSlackVariables(self):
		#add slack variables to every row except for objective row
		for constraint in range(1, len(self.table[0])):
			self.table[0][constraint][self.SLACK_VAR_NAMES[self.numSlack]] = 1
			self.numSlack += 1

		for i in range(0, self.numSlack):
			for rowIndex, row in enumerate(self.table[0]):
				#if the given slack variable is not in the row, create a column for that slack variable
				#and set the value to 0
				if self.SLACK_VAR_NAMES[i] not in row:
					self.table[0][rowIndex][self.SLACK_VAR_NAMES[i]] = 0

	def simplexSolve(self):
		iteration = 0
		optimal = self.isOptimal(iteration)
		while not optimal:
			print("-------------NEW ITERATION-------------")
			print(iteration)
			print(self.table[iteration])

			#find both the entering and leaving basic variables
			#also known as the pivot column and row
			#NEED TO STORE ALL BVs
			enteringBV = self.findEnteringBV(iteration) #this is a column (string)
			leavingBV = self.minRatio(enteringBV, iteration) #this is a row (int)

			print("Pivot Element")
			print(self.table[iteration][leavingBV][enteringBV])
			print("Entering BV:")
			print(enteringBV)
			#print("Row")
			#print(leavingBV)
			print("\r\n")

			#create new iteration array for each loop
			self.table.append([])

			#transfer all rows to below, normalizing the leavingBV row
			for rowIndex, row in enumerate(self.table[iteration]):
				if leavingBV == rowIndex: #if we are transferring the the leaving BV row then normalize it to 1 in the pivot column
					self.table[iteration+1].append(self.makeRowOneInColumn(self.table[iteration][leavingBV], enteringBV))
				else:
					self.table[iteration+1].append(row) #all regular rows are copied directly
			#self.table[iteration][leavingBV] = self.makeRowOneInColumn(self.table[iteration][leavingBV], enteringBV)

			#now make the remainder of the pivot column be zero
			self.zeroColumUsingRow(enteringBV, leavingBV, iteration+1)
			
			#new iteration has begun
			iteration += 1

			optimal = self.isOptimal(iteration)
		return self.table[iteration]


	#Takes the pivotColumn and the iteration
	#runs the ratio test on each row and returns the 
	#smalles non-zero ratio
	#also creates a column in the iteration for each row with the ratio
	#(Ratio test determines Leaving BV)
	#shouldn't be called before any thing that iterates through
	#all columns
	def minRatio(self, pivotColumn, iteration):
		minRatio = 2000.0000
		minRatioRow = None

		for rowIndex, row in enumerate(self.table[iteration]):
			#only run on rows that have a RHS (non-objective row)
			#and make sure that division by 0 doesn't happen
			if "RHS" in row and row[pivotColumn] != 0:
				rowRatio = row["RHS"]/row[pivotColumn]

				if rowRatio < minRatio and rowRatio > 0:
					minRatio = rowRatio
					minRatioRow = rowIndex
			#self.table[iteration][row]["Ratio"] = ratio #this should be added back if the loops are made smarter
		return minRatioRow

	#returns the key (String) of the entering BV
	def findEnteringBV(self, iteration):
		mostNegative = 0
		mostNegativeColumn = None

		for column in self.table[iteration][0]:
			if self.table[iteration][0][column] < mostNegative:
				mostNegative = self.table[iteration][0][column]
				mostNegativeColumn = column

		return mostNegativeColumn

	#for passing pivot row 
	def makeRowOneInColumn(self, row, pivotColumn):
		denominator = row[pivotColumn]
		for item in row:
			row[item] = row[item]/denominator #not the best way of dealing with fractions, but pray for whole numbers
		return row

	#the row passed should already have a 1 in the pivot column
	#zeros the element of the pivot element of each row using the pivot row
	def zeroColumUsingRow(self, column, pivotRow, iteration):
		for currRowIndex, currRow in enumerate(self.table[iteration]):
			#makes sure not to destroy the pivot row
			if currRowIndex == pivotRow:
				continue
			#find the value to multiply the pivot row by and add to 
			#current row to zero elements in the pivot column 
			#for every row
			multiplier = currRow[column] *-1

			for currColumn in currRow:
				self.table[iteration][currRowIndex][currColumn] += self.table[iteration][pivotRow][currColumn]*multiplier 

	#determines if the passed iteration is an optimal iteration by
	#checking for negative values in the objective row
	def isOptimal(self, iteration):
		for column in self.table[iteration][0]:
			if self.table[iteration][0][column] < 0:
				return False
		return True

def main():
	objectiveFunction = {}
	print("Please enter your objective function")
	read = raw_input()

	coefficient = 0
	negative = False
	for i, c in enumerate(read):
		if c == '-' : negative = True #then the next coefficient will be negative

		if c.isdigit(): 
			if negative:
				coefficient = float(c)*-1 + 10*coefficient
				negative = False
			else:
				coefficient = float(c) + 10*coefficient

		if c.isalpha(): #if it is a variable character
			objectiveFunction[c] = coefficient
			coefficient = 0

		if i+1 == len(read): #then it is RHS
			if negative:
				objectiveFunction["RHS"] = coefficient*-1
			else:
				objectiveFunction["RHS"] = coefficient
	print("Objective function entered: ")
	print(objectiveFunction)



	print("Please enter your constraint functions using single character letters as variables and include >/< for less/greater than or equal to. All variables assumed to be >= 0")
	read = raw_input().split(";")
	
	constraints = []
	for constraintIndex, constraint in enumerate(read):
		coefficient = 0
		
		constraints.append({}) #create new empty constraint dictionary

		negative = False
		for i, c in enumerate(constraint):
			if c == '-' : negative = True #then the next coefficient will be negative

			if c.isdigit(): 
				if negative:
					coefficient = float(c)*-1 + 10*coefficient
					negative = False
				else:
					coefficient = float(c) + 10*coefficient

			if c.isalpha(): #if it is a variable character
				constraints[constraintIndex][c] = coefficient
				coefficient = 0

			if i+1 == len(constraint): #then it is RHS
				if negative:
					constraints[constraintIndex]["RHS"] = coefficient*-1
				else:
					constraints[constraintIndex]["RHS"] = coefficient
	print("Constraints Entered:")
	print constraints

	print("Now solving")
	solve = SimplexMethodSolver(constraints, objectiveFunction)
	print(solve.simplexSolve())

if __name__ == '__main__':
	main()