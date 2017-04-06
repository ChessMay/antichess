#Kevin Wang
#12/8/2016

#####################
#AI
#####################

import random

def aiMoveList(data):
    moveList = []
    checkLimit = 10
    moveablePieces = findMoveablePieces(data)
    for moveablePiece in moveablePieces:
        #iterate through all moveable pieces
        color = moveablePiece[0]
        piece = moveablePiece[1]
        row = moveablePiece[2]
        col = moveablePiece[3]
        for legalMove in getLegalMoves(data,color,piece,row,col):
            #iterate through all legal moves of piece
            trgtRow = legalMove[0]
            trgtCol = legalMove[1]
            if ((getCapturableMoves(data) == [] or 
                legalMove in getCapturableMoves(data)) and
                (trgtRow != row or trgtCol != col)):
                moveList += [(row,col,trgtRow,trgtCol)]
    random.shuffle(moveList)
    if len(moveList) >= checkLimit:
        moveList = moveList[:checkLimit+1]
        #limit move list to improve runtime and semi-randomize moves
    return moveList

def aiMakeMove(data,row,col,trgtRow,trgtCol):
    if trgtRow == data.rows-1 and data.board[row][col]=='bp':
        #black pawn promotion
        data.board[row][col] = 'e'
        data.board[trgtRow][trgtCol] = 'bn'
        #knights minimize the number of squares a side must capture
        data.aiPromoted = (row,col,trgtRow,trgtCol)
        changeTurns(data)
    elif trgtRow == 0 and data.board[row][col]=='wp':
        #white pawn promotion
        data.board[row][col] = 'e'
        data.board[trgtRow][trgtCol]='wn'
        data.aiPromoted = (row,col,trgtRow,trgtCol)
        changeTurns(data)
    elif data.aiPromoted == (trgtRow,trgtCol,row,col):
        #unpromote
        color = data.board[row][col][0]
        data.board[trgtRow][trgtCol] ='%sp'%(color)
        data.board[row][col] = 'e'
        data.aiPromoted = False
        changeTurns(data)
    else:
        makeMove(data,row,col,trgtRow,trgtCol)

def aiMove(data):
    bestScore = 0
    (bestStartRow,bestStartCol) = (None,None)
    (bestTrgtRow,bestTrgtCol) = (None,None)
    bestTemp = None
    moveList = aiMoveList(data)
    random.shuffle(moveList)
    for move in moveList:
        (row,col) = (move[0],move[1])
        (trgtRow,trgtCol) = (move[2],move[3])
        if (row < 0 or row >= data.rows or col < 0 or col >= data.cols or
            trgtRow < 0 or trgtRow >= data.rows or
            trgtCol < 0 or trgtCol >= data.cols):
            continue
        temp = data.board[trgtRow][trgtCol]
        #store the target square to unmake move later
        aiMakeMove(data,row,col,trgtRow,trgtCol)
        score = alphaBetaMax(data,2,-float('inf'),float('inf'))
        #smarter AI could be made with deeper depth at cost of runtime
        aiMakeMove(data,trgtRow,trgtCol,row,col)
        #unmake move to preserve board state
        data.board[trgtRow][trgtCol] = temp
        #determine score for move then unmake move
        if bestScore == 0 or score > bestScore:
            bestScore = score
            (bestStartRow,bestStartCol) = (row,col)
            (bestTrgtRow,bestTrgtCol) = (trgtRow,trgtCol)
    aiMakeMove(data,bestStartRow,bestStartCol,bestTrgtRow,bestTrgtCol)
    data.aiPromoted = (None,None,None,None)
    #if best turn is promotion, reset aiPromoted for next turn
    if getCapturableMoves(data) == []:
        data.capturablePiece = False

def alphaBetaMax(data,depth,alpha,beta):
#adapted from pseudo-code from:
#https://chessprogramming.wikispaces.com/Alpha-Beta
#Max determines moves for the AI
    if depth == 0:
        return len(getCapturableMoves(data))
        #score determined by the number of pieces put in jeopardy
    moveList = aiMoveList(data)
    for move in moveList:
        (row,col) = (move[0],move[1])
        (trgtRow,trgtCol) = (move[2],move[3])
        if (row < 0 or row >= data.rows or col < 0 or col >= data.cols or
            trgtRow < 0 or trgtRow >= data.rows or
            trgtCol < 0 or trgtCol >= data.cols):
            continue
        temp = data.board[trgtRow][trgtCol]
        #store square for unmoving in case it has a piece being captured
        aiMakeMove(data,row,col,trgtRow,trgtCol)
        score = alphaBetaMin(data,depth-1,alpha,beta)
        aiMakeMove(data,trgtRow,trgtCol,row,col)
        data.board[trgtRow][trgtCol] = temp
        #return board to original state
        if score >= beta:
            return beta #beta cutoff, prune search tree
        if score > alpha:
            alpha = score
        #maximize the number of AI pieces put in jeopardy
    return alpha

def alphaBetaMin(data,depth,alpha,beta):
#adapted from pseudo-code from:
#https://chessprogramming.wikispaces.com/Alpha-Beta
#Min determines counter-moves by the human player
    if depth == 0:
        return len(getCapturableMoves(data))
    moveList = aiMoveList(data)
    for move in moveList:
        (row,col) = (move[0],move[1])
        (trgtRow,trgtCol) = (move[2],move[3])
        if (row < 0 or row >= data.rows or col < 0 or col >= data.cols or
            trgtRow < 0 or trgtRow >= data.rows or
            trgtCol < 0 or trgtCol >= data.cols):
            continue
        temp = data.board[trgtRow][trgtCol]
        aiMakeMove(data,row,col,trgtRow,trgtCol)
        score = alphaBetaMin(data,depth-1,alpha,beta)
        aiMakeMove(data,trgtRow,trgtCol,row,col)
        data.board[trgtRow][trgtCol] = temp
        if score <= alpha:
            return alpha #alpha cutoff, prune search tree
        if score < beta:
            beta = score
        #minimize number of pieces put in jeopardy by human player
    return beta

#####################
#piece classes
#####################

class Piece(object):
    def __init__(self, data, row, col):
        self.row = row
        self.col = col
        self.color = data.board[self.row][self.col][0]
        self.moved = False
        self.drowList = [-1,0,1]
        self.dcolList = [-1,0,1]
    def getChessPiece(data, color, piece):
        colorOffset = 0
        if color == 'w':
            colorOffset = 6
        pieceLabels = 'prnbqk'
        piece = pieceLabels.index(piece)
        return data.chessPiece[colorOffset+piece]
    def drawPiece(canvas, data, color, piece, x0, y0):
        pieceImage = Piece.getChessPiece(data, color, piece)
        canvas.create_image(x0,y0,anchor=NW,image=pieceImage)
    def legalMoves(self,data):
        #return legal moves as a list of tuples
        #super class is queen by default
        self.pieceMoves = [(self.row,self.col)]
        for drow in self.drowList:
            for dcol in self.dcolList:
                row = self.row
                col = self.col
                while ((col+dcol>=0 and col+dcol<data.cols) and
                    (row+drow>=0 and row+drow<data.rows) and
                    (data.board[row+drow][col+dcol]=='e')):
                    #check for legal empty squares
                    row += drow
                    col += dcol
                    self.pieceMoves += [(row,col)]
                if ((col+dcol>=0 and col+dcol<data.cols) and
                    (row+drow>=0 and row+drow<data.rows)):
                    if data.board[row+drow][col+dcol][0]!=self.color:
                        #check for capturable pieces
                        self.pieceMoves += [(row+drow,col+dcol)]
        return self.pieceMoves
class WPawn(Piece):
    #white and black pawns must be different b/c of different directions
    def legalMoves(self, data):
        self.pieceMoves = [(self.row,self.col)]
        startRow = 6
        startCols = range(0,8)
        if (self.row==startRow and self.col in startCols
            and data.board[self.row-2][self.col]=='e' and 
            data.board[self.row-1][self.col]=='e'):
            self.pieceMoves += [(self.row-2, self.col)]
        if self.col != 0 and self.col != 7:
            if data.board[self.row-1][self.col+1][0]=='b':
                self.pieceMoves += [(self.row-1, self.col+1)]
            if data.board[self.row-1][self.col-1][0]=='b':
                self.pieceMoves += [(self.row-1, self.col-1)]
        elif self.col == 0:
            if data.board[self.row-1][self.col+1][0]=='b':
                self.pieceMoves += [(self.row-1, self.col+1)]
        elif self.col == 7:
            if data.board[self.row-1][self.col-1][0]=='b':
                self.pieceMoves += [(self.row-1, self.col-1)]
        if data.board[self.row-1][self.col]=='e':
            self.pieceMoves += [(self.row-1, self.col)]
        return self.pieceMoves
class BPawn(Piece):
    def legalMoves(self, data):
        self.pieceMoves = [(self.row,self.col)]
        startRow = 1
        startCols = range(0,8)
        if (self.row==startRow and self.col in startCols
            and data.board[self.row+2][self.col]=='e' and
            data.board[self.row+1][self.col]=='e'):
            self.pieceMoves += [(self.row+2,self.col)]
        if self.col != 0 and self.col != data.cols-1:
            if data.board[self.row+1][self.col+1][0]=='w':
                self.pieceMoves += [(self.row+1,self.col+1)]
            if data.board[self.row+1][self.col-1][0]=='w':
                self.pieceMoves += [(self.row+1,self.col-1)]
        elif self.col==0:
            if data.board[self.row+1][self.col+1][0]=='w':
                self.pieceMoves += [(self.row+1,self.col+1)]
        elif self.col==data.cols-1:
            if data.board[self.row+1][self.col-1][0]=='w':
                self.pieceMoves += [(self.row+1,self.col-1)]
        if data.board[self.row+1][self.col]=='e':
            self.pieceMoves += [(self.row+1,self.col)]
        return self.pieceMoves
class Knight(Piece):
    def legalMoves(self, data):
        self.pieceMoves = [(self.row,self.col)]
        delta = [-2,-1,1,2]
        for drow in delta:
            for dcol in delta:
                if abs(drow) != abs(dcol):
                    if (self.row+drow<data.rows and self.row+drow>=0 and
                        self.col+dcol<data.rows and self.col+dcol>=0):
                        if (data.board[self.row+drow][self.col+dcol][0] != 
                            self.color):
                            self.pieceMoves += [(self.row+drow,self.col+dcol)]
        return self.pieceMoves
class Queen(Piece):
    def legalMoves(self, data):
        super().legalMoves(data)
        return self.pieceMoves
class Bishop(Piece):
    def legalMoves(self, data):
        self.dcolList = self.drowList = [-1,1]
        #change the dLists for only diagonals
        super().legalMoves(data)
        return self.pieceMoves
class Rook(Piece):
    wKRookMoved = False
    wQRookMoved = False
    bKRookMoved = False
    bQRookMoved = False
    #attributes concern castling rules
    def legalMoves(self, data):
        self.pieceMoves = [(self.row,self.col)]
        for drow in [-1,0,1]:
            for dcol in [-1,0,1]:
                if drow == 0 or dcol == 0:
                    #limit rook moves to vertical and diagonal
                    row = self.row
                    col = self.col
                    while ((col+dcol>=0 and col+dcol<data.cols) and
                        (row+drow>=0 and row+drow<data.rows) and
                        (data.board[row+drow][col+dcol]=='e')):
                        #check for legal empty squares
                        row += drow
                        col += dcol
                        self.pieceMoves += [(row,col)]
                    if ((col+dcol>=0 and col+dcol<data.cols) and
                        (row+drow>=0 and row+drow<data.rows)):
                        if data.board[row+drow][col+dcol][0]!=self.color:
                            #check for capturable pieces
                            self.pieceMoves += [(row+drow,col+dcol)]
        return self.pieceMoves
class King(Piece):
    wKingMoved = False
    bKingMoved = False
    def legalMoves(self, data):
        self.pieceMoves = [(self.row,self.col)]
        for drow in [-1,0,1]:
            for dcol in [-1,0,1]:
                if ((self.col+dcol>=0 and self.col+dcol<data.cols) and
                    (self.row+drow>=0 and self.row+drow<data.rows) and
                    (data.board[self.row+drow][self.col+dcol][0]!=self.color)):
                    if data.board[self.row+drow][self.col+dcol]!='e':
                        self.pieceMoves += [(self.row+drow,self.col+dcol)]
                    self.pieceMoves += [(self.row+drow,self.col+dcol)]
        #white castling
        if self.color=='w' and King.wKingMoved == False:
            #kingside
            if Rook.wKRookMoved == False:
                wKClear = True
                for dcol in [1,2]:
                    if (self.col+dcol < data.cols and
                        data.board[self.row][self.col+dcol] != 'e'):
                        wKClear = False
                if wKClear == True:
                    self.pieceMoves += [(self.row,self.col+2)]
            #queenside
            if Rook.wQRookMoved == False:
                wQClear = True
                for dcol in [-1,-2,-3]:
                    if (self.col+dcol>=0 and
                        data.board[self.row][self.col+dcol] != 'e' ):
                        wQClear = False
                if wQClear == True:
                    self.pieceMoves += [(self.row,self.col-2)]
        #black castling
        elif self.color == 'b' and King.bKingMoved == False:
            #kingside
            if Rook.bKRookMoved == False:
                bKClear = True
                for dcol in [1,2]:
                    if (self.col+dcol < data.cols and
                        data.board[self.row][self.col+dcol] != 'e'):
                        bKClear = False
                if bKClear == True:
                    self.pieceMoves += [(self.row,self.col+2)]
            #queenside
            if Rook.bQRookMoved == False:
                bQClear = True
                for dcol in [-1,-2,-3]:
                    if (self.col+dcol >= 0 and 
                        data.board[self.row][self.col+dcol] != 'e'):
                        bQClear = False
                if bQClear == True:
                    self.pieceMoves += [(self.row,self.col-2)]
        return self.pieceMoves

###############################
#tkinter draw and UI functions
###############################

import copy
from time import sleep
from tkinter import *

def init(data):
    data.mode = 'splash'
    data.rows = 8
    data.cols = 8
    data.margin = 10
    data.boardWidth = 480
    data.boardHeight = 480
    data.rowHeight = data.boardHeight / data.rows
    data.columnWidth = data.boardWidth / data.cols
    data.selection = None
    data.selectedPiece = 'e'
    data.prevRow = None
    data.prevCol = None
    data.board =(
        [['br','bn','bb','bq','bk','bb','bn','br'],
         ['bp','bp','bp','bp','bp','bp','bp','bp'],
         ['e','e','e','e','e','e','e','e'],
         ['e','e','e','e','e','e','e','e'],
         ['e','e','e','e','e','e','e','e'],
         ['e','e','e','e','e','e','e','e'],
         ['wp','wp','wp','wp','wp','wp','wp','wp'],
         ['wr','wn','wb','wq','wk','wb','wn','wr']])
    data.legalList = []
    data.turn = 'w'
    data.promotable = False
    data.promoList = [(3,3),(3,4),(4,3),(4,4)]
    data.tempPieceStore = []
    data.capturablePiece = False
    data.end = None
    data.quit = False
    data.aiOn = True
    data.aiTurn = False
    data.aiPromoted = (None,None,None,None)
    data.aiMoved = False
    data.movedFrom = []
    data.fireTimer = False
    King.wKingMoved = King.wKRookMoved = King.wQRookMoved = False
    King.bKingMoved = King.bKRookMoved = King.bQRookMoved = False
    loadChessPieces(data)

def reinit(data):
    #for resetting some variables after moving a piece
    data.legalList = []
    data.selectedPiece = 'e'
    data.selection = None
    (data.prevRow, data.prevCol) = (None,None)

def squareBounds(data, row, col):
    #based on week 5 notes
    x0 = data.margin + col * data.columnWidth
    x1 = data.margin + (col + 1) * data.columnWidth
    y0 = data.margin + row * data.rowHeight
    y1 = data.margin + (row + 1) * data.rowHeight
    return (x0, y0, x1, y1)

def getSquare(data, x, y):
    #based on getCell from week 5 notes
    row = (y - data.margin) // data.rowHeight
    col = (x - data.margin) // data.columnWidth
    return (int(row), int(col))

def loadChessPieces(data):
    pieces = 6
    data.chessPiece = []
    for color in ['b','w']:
        for piece in ['p','r','n','b','q','k']:
            pieceName = color + piece
            filename = "chess-piece-gifs/%s%s.gif"%(color,piece)
    #chess images converted from png to gif from:
    #commons.wikimedia.org/wiki/Category:PNG_chess_pieces/Standard_transparent
            data.chessPiece.append(PhotoImage(file=filename))

def getLegalMoves(data, color, piece, row, col):   
    if color + piece == 'wp':
        return WPawn(data,row,col).legalMoves(data)
    elif color + piece == 'bp':
        return BPawn(data,row,col).legalMoves(data)
    elif piece == 'n':
        return Knight(data,row,col).legalMoves(data)
    elif piece == 'q':
        return Queen(data,row,col).legalMoves(data)
    elif piece == 'b':
        return Bishop(data,row,col).legalMoves(data)
    elif piece == 'r':
        return Rook(data,row,col).legalMoves(data)
    elif piece == 'k':
        return King(data,row,col).legalMoves(data)

def findPossibleMoves(data):
    #for determining capturable moves and draws
    possibleMoves = []
    for moveablePiece in findMoveablePieces(data):
            tempMoves = []
            color = moveablePiece[0]
            piece = moveablePiece[1]
            row = moveablePiece[2]
            col = moveablePiece[3]
            tempMoves += getLegalMoves(data,color,piece,row,col)
            if len(tempMoves)>1:
                for move in tempMoves:
                    moveRow = move[0]
                    moveCol = move[1]
                    if (moveRow < data.rows and moveRow >= 0 and
                        moveCol < data.cols and moveCol >= 0):
                        if (data.board[moveRow][moveCol] == 'e' or
                            data.board[moveRow][moveCol][0] != data.turn or
                            (moveRow, moveCol) == (row,col)):
                            possibleMoves.append(move)
    return possibleMoves

def getCapturableMoves(data):
    moveList = findPossibleMoves(data)
    capturableMoves = []
    for move in moveList:
        row = move[0]
        col = move[1]
        if (data.board[row][col][0] != data.turn and
            data.board[row][col] != 'e'):
            data.capturablePiece = True
            if [move] not in capturableMoves:
                capturableMoves += [move]
    return capturableMoves

def makeMove(data, startRow, startCol, trgtRow, trgtCol):
    data.board[trgtRow][trgtCol] = data.board[startRow][startCol]
    data.board[startRow][startCol] = 'e'
    data.movedFrom = [(startRow,startCol),(trgtRow,trgtCol)]
    changeTurns(data)

def checkCastleRules(data):
    if (data.prevRow == 0 and (data.prevRow,data.prevCol)!=data.selection):
        #black rook/king
            if data.prevCol == 0:
                Rook.bQRookMoved = True
            elif data.prevCol == data.cols - 1:
                Rook.bKRookMoved = True
            elif data.prevCol == 4:
                King.bKingMoved = True
    if (data.prevRow==data.rows-1 and 
        (data.prevRow,data.prevCol)!=data.selection):
        #white rook/king
        if data.prevCol == 0:
            Rook.wQRookMoved = True
        elif data.prevCol == data.cols - 1:
            Rook.wKRookMoved = True
        elif data.prevCol == 4:
            King.wKingMoved = True

def castle(data, kingside, row, col):
    if kingside:
        (data.board[row][col-1],data.board[row][col+1])=(data.board[row][col+1],
            data.board[row][col-1])
    else:
        (data.board[row][col-2],data.board[row][col+1])=(data.board[row][col+1],
            data.board[row][col-2])

def changeTurns(data):
    if data.turn == 'w':
        data.turn = 'b'
    else:
        data.turn = 'w'

def promote(data,currRow,currCol):
    if (currRow,currCol) not in data.promoList:
            return
    else:
        if 'wp' in data.board[0]:
            pawnCol = data.board[0].index('wp')
            data.board[0][pawnCol] = data.board[currRow][currCol]
            promoReset(data)
        elif 'bp' in data.board[data.rows-1]:
            if data.aiOn == False:
                pawnCol = data.board[data.rows-1].index('bp')
                data.board[data.rows-1][pawnCol]=data.board[currRow][currCol]
                promoReset(data)
            else:
                data.board[data.rows-1][pawnCol] = data.board[4][3]

def promoReset(data):
    for row in [4,3]:
        for col in [4,3]:
            data.board[row][col] = data.tempPieceStore.pop()
            data.promotable = False

def checkEnd(data):
    #checks for wins or draws
    blackWin = True
    whiteWin = True
    for row in range(len(data.board)):
        for col in range(len(data.board)):
            if data.board[row][col][0] == 'b':
                blackWin = False
            elif data.board[row][col][0] == 'w':
                whiteWin = False
    if blackWin == True: data.end = 'blackWin'
    elif whiteWin == True: data.end = 'whiteWin'
    elif findPossibleMoves(data) == []:
        data.end = 'draw'

def keyPressed(event, data):
    if data.quit == True:
        if event.keysym == 'y':
            init(data)
        elif event.keysym == 'n':
            data.quit = False
    elif data.end != None:
        if event.keysym == 'space':
            init(data)
        elif event.keysym == 'r':
            if data.aiOn == True:
                init(data)
                data.mode = 'game'
                data.aiOn = True
            elif data.aiOn == False:
                init(data)
                data.mode = 'game'
                data.aiOn = False

def mousePressed(event, data):
    if data.mode=='splash' or data.end != None or data.quit == True:
        if data.quit == True:
            data.legalList = []
        return
    if (event.x > data.boardWidth or event.y > data.boardHeight or 
        event.x <= 0 or event.y <= 0):
        return
    (currRow, currCol) = getSquare(data, event.x, event.y)
    data.selection = (currRow, currCol)
    if ((data.prevRow,data.prevCol) == data.selection):
        if data.capturablePiece == False:
            reinit(data)
        return
    if data.selectedPiece != 'e':
        #moving a piece
        if ((currRow, currCol) in data.legalList and
            (currRow, currCol) in getLegalMoves(data,data.selectedPiece[0],
                data.selectedPiece[1],data.prevRow, data.prevCol)):
            #checks if move is legal
            if data.board[currRow][currCol] != 'e':
                data.capturablePiece = False
            #check if rook or king moved
            checkCastleRules(data)
            if data.selectedPiece[1] == 'k':
                #castling
                if currCol == data.prevCol + 2:
                    #kingside
                    castle(data,True,currRow,currCol)
                elif currCol == data.prevCol - 2:
                    #queenside
                    castle(data,False,currRow,currCol)
            #check for promotable pawns
            if data.prevRow != None and data.prevCol != None:
                makeMove(data,data.prevRow,data.prevCol,currRow,currCol)
                checkEnd(data)
                if 'wp' in data.board[0] or 'bp' in data.board[data.rows-1]:
                    data.promotable = True
                    data.fireTimer = True
            if data.aiOn==True and data.end==None and data.promotable!=True:
                #move ai when no promotion available
                aiMove(data)
                checkEnd(data)
                data.aiMoved = True
    if data.promotable == True:
        #promote a piece
        if (currRow,currCol) not in data.promoList:
            return
        else:
            if 'wp' in data.board[0]:
                pawnCol = data.board[0].index('wp')
                data.board[0][pawnCol] = data.board[currRow][currCol]
                promoReset(data)
            elif 'bp' in data.board[data.rows-1]:
                if data.aiOn == False:
                    pawnCol = data.board[data.rows-1].index('bp')
                    data.board[data.rows-1][pawnCol]=(data.board[currRow]
                        [currCol])
                    promoReset(data)
                else:
                    data.board[data.rows-1][pawnCol] = data.board[4][3]
        data.fireTimer = False
        if data.aiOn == True:
            #move ai after promoting
            aiMove(data)
    #reinitialize selection for empty clicks
    reinit(data)
    #limit legal moves to capturable pieces
    data.legalList += getCapturableMoves(data)
    if data.aiMoved == True:
        #don't draw the legal moves of the piece just moved
        data.aiMoved = False
        return
    if data.board[currRow][currCol] != 'e':
        #selecting a piece
        color = data.board[currRow][currCol][0]
        piece = data.board[currRow][currCol][1]
        if data.board[currRow][currCol][0] != data.turn:
            #check if piece is for the current player
            return
        if data.board[currRow][currCol][0] == data.selectedPiece[0]:
            data.legalList = []
            return
        if data.capturablePiece == False:
            data.legalList += getLegalMoves(data,color,piece,currRow,currCol)
            data.selectedPiece = data.board[currRow][currCol]
            (data.prevRow, data.prevCol) = (currRow, currCol)
        elif data.capturablePiece == True:
            legalListCopy = copy.deepcopy(data.legalList)
            for square in legalListCopy:
                if square in getLegalMoves(data,color,piece,currRow,currCol):
                    data.legalList += [(currRow,currCol)]
                    data.selectedPiece = data.board[currRow][currCol]
                    (data.prevRow, data.prevCol) = (currRow, currCol)
    return

def timerFired(data):
    pass

def drawBG(canvas,data):
    bgMargin = 3
    canvas.create_rectangle(bgMargin,bgMargin,data.width,
        data.height,fill='light blue')

def drawBoard(canvas, data):
    for row in range(data.rows):
        for col in range(data.cols):
            (x0, y0, x1, y1) = squareBounds(data, row, col)
            if (row, col) in data.legalList:
                #legal moves
                fill = "orange"
            elif (row, col) in data.movedFrom:
                fill = "light green"
            elif (row+col)%2 == 0:
                fill = "white"
            else:
                fill = "light grey"
            canvas.create_rectangle(x0,y0,x1,y1,fill=fill)
            if data.board[row][col] != 'e':
                color = data.board[row][col][0]
                piece = data.board[row][col][1]
                Piece.drawPiece(canvas, data, color, piece, x0, y0)

def drawTurn(canvas, data):
    side = 50
    left = data.boardWidth + data.margin + side/2
    top = data.boardHeight/2 - (side/2)
    right = left + side
    bot = top + side
    if data.turn == 'b':
        color = 'black'
    else:
        color = 'white'
    canvas.create_rectangle(left,top,right,bot,fill=color,width=1)
    canvas.create_text(left,top,text="TURN:",anchor='sw',
        font='Arial 24 bold')

def drawEnd(canvas, data):
    if data.end == 'draw':
        endText = 'DRAW'
    elif data.end == 'whiteWin':
        endText = 'WHITE WINS!'
    elif data.end == 'blackWin':
        endText = 'BLACK WINS!'
    endInstruct = "Press space to return to menu"
    endInstruct2 = "or 'r' to restart"
    offset = 50
    part2Offset = 35
    canvas.create_text(data.width/2-offset, data.height/2, text=endInstruct,
        font='Arial 32 bold', fill='dark orange', anchor='n')
    canvas.create_text(data.width/2-offset, data.height/2+part2Offset,
        text=endInstruct2,font='Arial 32 bold', fill='dark orange', anchor='n')
    canvas.create_text(data.width/2-offset, data.height/2, text=endText,
        font='Times 64 bold', fill='blue', anchor='s')

def drawSplash(canvas, data):
    titleText = 'ANTICHESS'
    rareChange = random.randint(1,100)
    if rareChange == 1:
        titleText = 'ANITCHESS'
    textList = ['Play alone or with friends!',
                'Now with 20% less sodium!',
                'Gluten free!',
                'May contain nuts!',
                'The one with the chess!',
                '42!',
                'Carpe Diem!',
                '...!',
                'NP Complete!',
                'Halts!',
                'Bees?',
                'As seen on TV!',
                '90% bug free!',
                'Exterminate!',
                'Foo Bar!'
    ]
    canvas.create_text(data.width/2,data.height/4, text=titleText,
            font='Times 76 bold', anchor='s')
    canvas.create_text(data.width/2,data.height/4,text=random.choice(textList),
            font = 'Cambria 24 bold', anchor='n', fill='blue')
    leftImageX = data.width/2 - 200
    rightImageX = data.width/2 + 140
    imageY = data.height/2 + 15
    pieceColors = ['w','b']
    pieces = ['p','b','n','q','k']
    Piece.drawPiece(canvas,data,random.choice(pieceColors),
        random.choice(pieces),leftImageX,imageY)
    Piece.drawPiece(canvas,data,random.choice(pieceColors),
        random.choice(pieces),rightImageX,imageY)

def drawHelp(canvas,data):
    textOff = 110
    helpText = """
        \t               All the pieces move like regular chess.\n
            Click on a piece to select it then click on one of its legal moves.

        If a piece can capture another piece on your turn, it has to capture.\n
        \t\t First side to lose all their pieces wins.\n\n
        \t\t\t     NOTE:\n
        \t      The AI may be slow at times, please be patient!"""
    headerText = "RULES:"
    canvas.create_text(data.width/2,data.height/2-textOff,text=headerText,
        font='Times 16 bold', anchor='s')
    canvas.create_text(data.width/2,data.height/2,text=helpText,
        font='Times 16', anchor='center')

def drawPromotion(canvas,data,color):
    pieces = ['q','r','n','b']
    for row in [3,4]:
        for col in [3,4]:
            if len(data.tempPieceStore) != 4:
                data.tempPieceStore += [data.board[row][col]]
            data.board[row][col] = '%s%s'%(color, pieces.pop())

def drawQuit(canvas,data):
    offset = 50
    questionText = "Are you sure?"
    responseText = "Press Y/N"
    canvas.create_text(data.width/2-offset, data.height/2, text=questionText,
        font="Arial 32 bold", anchor='s', fill='blue')
    canvas.create_text(data.width/2-offset, data.height/2, text=responseText,
        font="Arial 28 bold", anchor='n', fill='blue')

def redrawAll(canvas, data):
    drawBG(canvas,data)
    if data.mode == 'splash':
        drawSplash(canvas,data)
        buttonOffset = 50
        singlePlayerButton = canvas.data['singlePlayerButton']
        canvas.create_window(data.width/2,data.height/2,
            window=singlePlayerButton)
        multiPlayerButton = canvas.data['multiPlayerButton']
        canvas.create_window(data.width/2,data.height/2+buttonOffset,
            window=multiPlayerButton)
        helpButton = canvas.data['helpButton']
        canvas.create_window(data.width/2,data.height/2+2*buttonOffset,
            window=helpButton)
    elif data.mode == 'help':
        menuOff = 150
        drawHelp(canvas, data)
        menuButton = canvas.data['menuButton']
        canvas.create_window(data.width/2, data.height/2+menuOff,
            window=menuButton)
    else:
        drawBoard(canvas, data)
        if data.aiOn == False:
            drawTurn(canvas, data)
        quitButton = canvas.data['quitButton']
        buttonOffset = 61
        canvas.create_window(data.boardWidth+buttonOffset,
            data.boardHeight/2+buttonOffset,window=quitButton)
        if data.end != None:
            drawEnd(canvas, data)
        elif data.quit == True:
            drawQuit(canvas,data)
        elif data.promotable == True:
            if 'wp' in data.board[0]:
                drawPromotion(canvas,data,'w')
            else:
                drawPromotion(canvas,data,'b')

def singlePlayerPressed(canvas,data):
    data.mode = 'game'
    reinit(data)
    canvas.delete(ALL)
    redrawAll(canvas,data)
    canvas.update()

def multiPlayerPressed(canvas,data):
    data.mode = 'game'
    data.aiOn = False
    reinit(data)
    canvas.delete(ALL)
    redrawAll(canvas,data)
    canvas.update()

def helpPressed(canvas,data):
    data.mode = 'help'
    canvas.delete(ALL)
    redrawAll(canvas,data)
    canvas.update()

def menuPressed(canvas,data):
    init(data)
    canvas.delete(ALL)
    redrawAll(canvas,data)
    canvas.update()

def quitPressed(canvas,data):
    if data.end != None:
        return
    data.quit = True
    canvas.delete(ALL)
    redrawAll(canvas,data)
    canvas.update()

def buttonInit(root, canvas, data):
    singlePlayerButton = Button(root,text='Single Player',width=10,
        command=lambda:singlePlayerPressed(canvas,data))
    canvas.data['singlePlayerButton'] = singlePlayerButton
    multiPlayerButton = Button(root,text='Multiplayer', width=10,
        command=lambda:multiPlayerPressed(canvas,data))
    canvas.data['multiPlayerButton'] = multiPlayerButton
    helpButton = Button(root,text='Help',width=10,
        command=lambda:helpPressed(canvas,data))
    canvas.data['helpButton'] = helpButton
    menuButton = Button(root,text='Menu',width=10,
        command=lambda:menuPressed(canvas,data))
    canvas.data['menuButton'] = menuButton
    quitButton = Button(root,text='Quit',width=5,
        command=lambda:quitPressed(canvas,data))
    canvas.data['quitButton'] = quitButton
    canvas.pack()
    redrawAll(canvas,data)

###############################################
#run function from notes with minor adjustments
###############################################
def run(width=300, height=300):#from notes with minor changes
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas,data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        if data.mode != 'splash':
            mousePressed(event, data)
            redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        if data.quit == True or data.end != None:
            keyPressed(event, data)
            redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas,data):
        timerFired(data)
        if data.fireTimer != False:
            redrawAllWrapper(canvas,data)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Create root before calling init (so we can create images in init)
    root = Tk()
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 250 # milliseconds
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    # set up events
    root.canvas = canvas.canvas = canvas
    canvas.data = {}
    buttonInit(root, canvas,data)
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(600, 500)

