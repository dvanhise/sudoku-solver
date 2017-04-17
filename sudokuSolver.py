import sys, random, copy

UNIT = 3


# returns true is grid is illegal
def onlyOneSquareInSetCanBe(squareSet):
  for num in range(UNIT*UNIT):
    matchList = list(filter(lambda x: x.canBe[num], squareSet))
    if len(matchList) == 1 and matchList[0].value == None:
      matchList[0].setValue(num)
    elif len(matchList) == 0:
      return True
  return False
  
  
def unsetSet(nonSet, num):
  for square in nonSet:
    if square.value == num:
      return True
    square.unsetValue(num)
    
    
    
def solveSudoku(grid, guessIter):
  iteration = 1
  # continue iterating over the same strategies until the game grid is filled in or we're stuck
  while not grid.isSolved():
    grid.unchangeAll()
    #
    # strat 1: for every known square, all squares in it's row, col, or box can't have that value
    #
    allSquares = grid.getEverythingSet()
    for curSquare in allSquares:
      # nothing in that square's row, col, or box can have that value
      if curSquare.value != None:
        unionSet = grid.getColumnSetOf(curSquare.col).union(grid.getRowSetOf(curSquare.row)).union(grid.getBoxSetOf(curSquare.box))
        unionSet.remove(curSquare)
        if unsetSet(unionSet, curSquare.value):
          grid.legal = False
      
    #
    # strat 2a: In each row/col/box, if all square but one can't be a value, that square must be that value
    #
    # also check for grid legality while we're at it
    for i in range(UNIT*UNIT):
      if onlyOneSquareInSetCanBe(grid.getRowSetOf(i)) or onlyOneSquareInSetCanBe(grid.getColumnSetOf(i)) or onlyOneSquareInSetCanBe(grid.getBoxSetOf( (i%UNIT,i//UNIT) )):
        grid.legal = False
        

        
    #
    # strat 3: if all the squares in a box that can be a value are in the same row/col, the rest of the row/col can't have that value
    #
    # For each box
    for i in range(UNIT*UNIT):
      curBoxSet = grid.getBoxSetOf( (i%UNIT,i//UNIT) )
      # For each number
      for num in range(UNIT*UNIT):
        matchSet = set(filter(lambda x: x.canBe[num], curBoxSet))
        if len(matchSet) > 1 and len(matchSet) <= UNIT:
          # Get the cols and rows that intersect the box
          columnSets = [grid.getColumnSetOf((i%UNIT)*UNIT+x) for x in range(UNIT)]
          rowSets = [grid.getRowSetOf((i//UNIT)*UNIT+x) for x in range(UNIT)]
          # If all the squares in the box that can be a number are in same row/col
          for lineSet in columnSets+rowSets:
            if matchSet.issubset(lineSet):
              unsetSet(lineSet.difference(matchSet), num)
 
    #
    # strat 4: guess and check
    #
    # If no progress has been made since last iteration
    if iteration > 1 and not grid.somethingChanged():
      if guessIter:
        return grid
        
      guessIterNum = 1
      while guessIterNum < 1000:
        guessGrid = copy.deepcopy(grid)
        allSquares = list(guessGrid.getEverythingSet())
        randSquareId = random.randint(0, UNIT**4-1)
        randIter = 0
        goalNum = 2
        while allSquares[randSquareId].canBe.count(True) != goalNum:
          randSquareId = random.randint(0, UNIT**4-1)
          randIter += 1
          if randIter % 50 == 0:
            goalNum = (goalNum + 1) if goalNum < UNIT*UNIT else 2
        
        allSquares[randSquareId].setValue(random.choice(allSquares[randSquareId].getTrueIndices()))
        guessGrid = solveSudoku(guessGrid, True)
        
        if guessGrid.isSolved():
          print("Guess Iterations: %s" % guessIterNum)
          print("Iterations: %s" % iteration)
          return guessGrid
        guessIterNum += 1
    
      # We aren't going to make any progress doing the large loop any more times at this point, so return
      print("Max guess iterations reached")
      return grid
        
    #
    # check for legality
    #
    if not grid.legal:
      # if running a guess and check, return it incomplete
      if guessIter:
        return grid
      else:
        break
        
    iteration += 1
    if iteration > 20:
      break
  # when solved or fail

  if not guessIter: print("Iterations: %s" % iteration)
  return grid
    
    
    
    
class Square(object):

  def __init__(self, initValue, col, row, box):
    if initValue >= 1 and initValue <= UNIT*UNIT:
      self.canBe = [False]*(UNIT*UNIT)
      self.canBe[initValue-1] = True
      self.value = initValue - 1
    else:
      self.canBe = [True]*(UNIT*UNIT)
      self.value = None
      
    self.col = col
    self.row = row
    self.box = box  # tuple of two values
    self.changed = False
    
    
  def checkIfSolved(self):
    if self.canBe.count(True) == 1:
      self.Value = self.canBe.index(True)
    
    
  def setValue(self, num):
    if self.value == None:
      self.canBe = [False]*UNIT*UNIT
      self.canBe[num] = True
      self.value = num
      self.changed = True
    
    
  def unsetValue(self, num):
    if self.canBe[num]:
      self.canBe[num] = False
      self.changed = True
      self.checkIfSolved()
    
  # returns a list of indices where self.canBe is true
  def getTrueIndices(self):
    a = []
    for i in range(UNIT*UNIT):
      if self.canBe[i]:
        a.append(i)
    return a


class Grid(object):
  
  # initState is a UNIT^2 x UNIT^2 array of numbers as read from an input file (list of rows)
  def __init__(self, initState):
    self.legal = True
    self.changed = False
    self.gridState = [[None for x in range(UNIT*UNIT)] for y in range(UNIT*UNIT)]
    for rowNdx, row in enumerate(initState):
      for colNdx, num in enumerate(row):
        self.gridState[colNdx][rowNdx] = Square(num, colNdx, rowNdx, (colNdx//UNIT, rowNdx//UNIT))
        
  def unchangeAll(self):
    for a in self.getEverythingSet():
      a.changed = False
      
  def somethingChanged(self):
    for a in self.getEverythingSet():
      if a.changed:
        return True
    return False
        
  def isSolved(self):
    for column in range(UNIT*UNIT):
      for row in range(UNIT*UNIT):
        if self.gridState[column][row].value == None:
          return False
    return True
      
  
  def getEverythingSet(self):
    allList = []
    for column in range(UNIT*UNIT):
      allList.extend(self.gridState[column])
    return set(allList)
      
  def getColumnSetOf(self, col):
    return set(self.gridState[col])
    
  def getRowSetOf(self, row):
    rowList = []
    for i in range(UNIT*UNIT):
      rowList.append(self.gridState[i][row])
    return set(rowList)
  
  def getBoxSetOf(self, box):
    colList = []
    for column in range(UNIT*UNIT):
      for row in range(UNIT*UNIT):
        if self.gridState[column][row].box == box:
          colList.append(self.gridState[column][row])
    return set(colList)
  

      
  def printOut(self):
    print('\n+-------+-------+-------+')
    for i in range(0, UNIT*UNIT, UNIT):
      for j in range(UNIT):
        line = '| '
        for k in range(0, UNIT*UNIT, UNIT):
          for m in range(UNIT):
            val = self.gridState[k+m][i+j].value
            line += (' ' if val==None else str(val+1)) + ' '
          line += '| '
        print(line)
      print('+-------+-------+-------+')
    print('\n')
    
      
      
def main():
  
  print(' '.join(sys.argv))
  if len(sys.argv) != 2:
    print("Exactly one argument (a file with the puzzle's initial state) expected")
    sys.exit(1)

  infile = open(sys.argv[1], 'r')
    
  startArray = []
  for line in infile:
  
    if len(line.strip()) != UNIT*UNIT:
      print("input file line length error")
      sys.exit(1)
    
    startArray.append([int(x) for x in line.strip()])
    
  infile.close
  
  grid = Grid(startArray)
  
  print("Initial game state:")
  grid.printOut()
  
  finalGrid = solveSudoku(grid, False)
  
  if finalGrid.legal:
    print("Solution:")
    finalGrid.printOut()
  else:
    print("Illegal game state")
  
if __name__ == "__main__":
    main()
