#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 23 nov. 2019

@author: FranDesktop
@title: 'Shirokuro: pasatiempo lógico japonés desarrollado en Python empleando la biblioteca Kivy'
'''
from enum import Enum
import random
from time import perf_counter
from math import floor
import time
import os
from functools import partial
from kivy.clock import Clock
#import Shirokuro
#from Shirokuro import shirokuroGame, table, link, directionLink, gamePiece, colorPiece
from kivy.app import App
import kivy
kivy.require('1.11.0')
from kivy.config import Config
from kivy.uix import widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle, Color
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.storage.jsonstore import JsonStore
from kivy.uix.image import Image


class colorPiece(Enum):
    WHITE = 1
    BLACK = 2

class gamePiece(object):
    
    def __init__(self, posx, posy, color):
        self.__posx = posx
        self.__posy = posy
        self.__position = (posx, posy)
        
        if(not(isinstance(color, colorPiece))):
            raise Exception("color must be colorPiece type")
        self.__color = color
        
        self.__link = None
        
    """ Getters """
    @property
    def posx(self):
        return self.__posx
    
    @property
    def posy(self):
        return self.__posy
    
    @property
    def position(self):
        return self.__position
    
    @property
    def color(self):
        return self.__color
    
    @property
    def link(self):
        return self.__link
    
    def connectToTable(self, table):
        table[self.__position] = self
    
    def disconnectFromTable(self, table):
        table[self.__position] = None
    
    """ Setters """
    #Si le pones @property al set, da error y dice que falta el argumento.
    def setLink(self, link):
        self.__link = link
        
    """ toString """
    @property
    def str(self):
        return self.__color.name[0]
    
    def __repr__(self):
        return self.str

class directionLink(Enum):
    HORIZONTAL = 1
    VERTICAL = 2
    HORIZONTAL_RIGHT = 3
    HORIZONTAL_LEFT = 4
    VERTICAL_UP = 5
    VERTICAL_DOWN = 6

class link(object):
        
    def __init__(self, piece1, piece2):
        self.__white = piece1 if piece1.color is colorPiece.WHITE else piece2
        self.__black = piece1 if piece1.color is colorPiece.BLACK else piece2
        self.__directionLink = directionLink.HORIZONTAL if (self.__white.posx - self.__black.posx == 0) else directionLink.VERTICAL
        self.__linkedCells = self.getLinkedCells()
        self.__intermediateCells = self.__linkedCells[1:(len(self.__linkedCells)-1)]
        
    def getLinkedCells(self):
        res = []
        
        if(self.__white.posx > self.__black.posx): #Blanca sobre negra en vertical
            for i in range(self.__black.posx, self.__white.posx+1):
                res.append((i, self.__white.posy))
            
        elif(self.__white.posx < self.__black.posx): #Negra sobre blanca en vertical
            for i in range(self.__white.posx, self.__black.posx+1):
                res.append((i, self.__white.posy))
            
        elif(self.__white.posy > self.__black.posy): #Blanca sobre negra en horizontal
            for j in range(self.__black.posy, self.__white.posy+1):
                res.append((self.__white.posx, j))
            
        elif(self.__white.posy < self.__black.posy): #Negra sobre blanca en horizontal
            for j in range(self.__white.posy, self.__black.posy+1):
                res.append((self.__white.posx, j))
            
        return res
    
    def getDirectionLink(self):
        if(self.__white.posx - self.__black.posx == 0):
            return directionLink.HORIZONTAL
        else:
            return directionLink.VERTICAL
    
    def connectToTable(self, table):
        self.__white.setLink(link=self)
        self.__black.setLink(link=self)
        for cell in self.__intermediateCells:
            table[cell] = self
        
    def disconnectFromTable(self, table):
        self.__white.setLink(link=None)
        self.__black.setLink(link=None)
        for cell in self.__intermediateCells:
            table[cell] = None
    
    def getOpposite(self, piece):
        if(self.__white is piece):
            return self.__black
        else:
            return self.__white
    
    def getPieces(self):
        ls = list()
        ls.append(self.white)
        ls.append(self.black)
        return ls
    
    """ Getters """
    @property
    def white(self):
        return self.__white
    
    @property
    def black(self):
        return self.__black
    
    @property
    def linkedCells(self):
        return self.__linkedCells
    
    @property
    def intermediateCells(self):
        return self.__intermediateCells
    
    def directionLink(self):
        return self.__directionLink
    
    def equal(self, link):
        white = link.white
        black = link.black
        linkedCells = link.getLinkedCells()
        
        return (True if (self.__white.position == white.position and 
                self.__black.position == black.position and 
                all(self.__linkedCells[i] == linkedCells[i] for i in range(0, len(linkedCells)))) else 
                False)

    """ Setters """
    @property
    def setWhite(self, white):
        if(not(isinstance(white, gamePiece) and isinstance(white.color, type(colorPiece.WHITE)))):
            raise Exception("white must be gamePiece type and WHITE type")
        self.__white = white
        
    @property
    def setBlack(self, black):
        if(not(isinstance(black, gamePiece) and isinstance(black.color, type(colorPiece.BLACK)))):
            raise Exception("black must be gamePiece type and BLACK type")
        self.__black = black
    
    """ toString """
    @property
    def str(self):
        return "["+str(self.__linkedCells[0])+" to "+str(self.__linkedCells[-1])+"]"
    
    def __repr__(self):
        return self.str

class chronoStatus(Enum):
    STARTED = 1
    PAUSED = 2

class timeKeeper(object):
    
    def __init__(self):
        self.__start = 0
        self.__end = 0
        self.__timeElapsed = 0
        self.__counterTimes = []
        self.__status = chronoStatus.PAUSED
        
    def startTimeKeeper(self):
        self.__start = perf_counter()
        self.__status = chronoStatus.STARTED
        
    def pauseTimeKeeper(self):
        self.__end = perf_counter()
        self.__counterTimes.append(self.__end - self.__start)
        self.__status = chronoStatus.PAUSED
    
    @property
    def getTimeElapsed(self):
        """ Consulta con el cronÃ³metro en funcionamiento. """
        if(self.__status == chronoStatus.STARTED):
            """ Lo paro """
            self.pauseTimeKeeper()
            """ Calculo el time elapsed """
            self.__timeElapsed = sum(self.__counterTimes)
            """ Lo vuelvo a encender """
            self.startTimeKeeper()
            
            """ Consulta con el cronÃ³metro parado. """
        elif(self.__status == chronoStatus.PAUSED):
            self.__timeElapsed = sum(self.__counterTimes)
        
        return self.__timeElapsed
    
    def reset(self):
        self.__init__()
        self.startTimeKeeper()
        
    """ toString """
    @property
    def str(self):
        return str(self.getTimeElapsed)
    
    def __repr__(self):
        return self.str

class table(object):
    
    def __init__(self, numRows, numColumns, hasUniqueSolution, hasClues, aidPercentage, percentageLevel, linkDifficulty):
        
        """ Dimensions """
        self.__numRows = numRows
        self.__numColumns = numColumns
        
        self.__hasUniqueSolution = hasUniqueSolution
        self.__hasClues = hasClues
        self.__aidPercentage = aidPercentage
        self.__percentageLevel = percentageLevel
        self.__linkDifficulty = linkDifficulty
        
        """ State """
        self.__statusTable = None
        
        """ data structures for a faster heuristic searching solutions during backtracking. """
        self.__linksPerPiece = None
        self.__originalLinksPerPiece = None

        self.__linksPerCell = None
        self.__originalLinksPerCell = None
        
        self.__directNeighborsPerPiece = None
        self.__originalDirectNeighborsPerPiece = None
        
        self.__piecesPerRow = None
        self.__piecesPerColumn = None
        
        self.__settedLinks = None
        self.__protectedLinks = None
    
    def loadState(self, numRows, numColumns, hasUniqueSolution, hasClues, aidPercentage, percentageLevel, linkDifficulty,
                  statusTable=None, linksPerPiece=None, originalLinksPerPiece=None, linksPerCell=None, originalLinksPerCell=None,
                  directNeighborsPerPiece=None, originalDirectNeighborsPerPiece=None, piecesPerRow=None, piecesPerColumn=None,
                  settedLinks=None, protectedLinks=None):
        
        """ Dimensions """
        self.__numRows = numRows
        self.__numColumns = numColumns
        
        self.__hasUniqueSolution = hasUniqueSolution
        self.__hasClues = hasClues
        self.__aidPercentage = aidPercentage
        self.__percentageLevel = percentageLevel
        self.__linkDifficulty = linkDifficulty
        
        """ State """
        self.__statusTable = statusTable
        
        self.__linksPerPiece = linksPerPiece
        self.__originalLinksPerPiece = originalLinksPerPiece
        
        self.__linksPerCell = linksPerCell
        self.__originalLinksPerCell = originalLinksPerCell
        
        self.__directNeighborsPerPiece = directNeighborsPerPiece
        self.__originalDirectNeighborsPerPiece = originalDirectNeighborsPerPiece
        
        self.__piecesPerRow = piecesPerRow
        self.__piecesPerColumn = piecesPerColumn
        
        self.__settedLinks = settedLinks
        self.__protectedLinks = protectedLinks
        
    def getAllLinks(self):
        res = []
        for lsDicts in self.getAllOriginalLinksPerPiece().values():
            for dicc in lsDicts:
                for gameLink in dicc.values():
                    res.append(gameLink)
        return list(set(res))
            
    def getNumRows(self):
        return self.__numRows
    
    def getNumColumns(self):
        return self.__numColumns
    
    def hasUniqueSolution(self):
        return self.__hasUniqueSolution
    
    def linkDifficulty(self):
        return self.__linkDifficulty
    
    def hasClues(self):
        return self.__hasClues
    
    def aidPercentage(self):
        return self.__aidPercentage
    
    def percentageLevel(self):
        return self.__percentageLevel
    
    def getAllLinksPerPiece(self):
        return self.__linksPerPiece
    
    def getAllOriginalLinksPerPiece(self):
        return self.__originalLinksPerPiece
    
    def getAllLinksPerCell(self):
        return self.__linksPerCell
    
    def getAllOriginalLinksPerCell(self):
        return self.__originalLinksPerCell
    
    def getAllDirectNeighborsPerPiece(self):
        return self.__directNeighborsPerPiece
    
    def getAllOriginalDirectNeighborsPerPiece(self):
        return self.__originalDirectNeighborsPerPiece
    
    def getPiecesPerRow(self, row=None):
        if(row==None):
            return self.__piecesPerRow
        else:
            return self.__piecesPerRow[row]
    
    def getPiecesPerColumn(self, column=None):
        if(column==None):
            return self.__piecesPerColumn
        else:
            return self.__piecesPerColumn[column]
    
    def linksPerPiece(self):
        return self.__linksPerPiece
    
    def getLinksPerPiece(self, piece):
        tupla = self.__linksPerPiece[piece]
        possibleLinks = tupla[0]
        return [possibleLink for (oppositePiece, possibleLink) in possibleLinks.items()]

    def getMatchedNeighbors(self, piece):
        return [neighbor for (neighbor, possibleLink) in self.__linksPerPiece[piece][0].items()]
        
    def getNonMatchedNeighbors(self, piece):
        return [neighbor for (neighbor, nonPossibleLink) in self.__linksPerPiece[piece][1].items()]
    
    def setLink(self, inputLink):
        inputLink.connectToTable(self.__statusTable)
    
    def removeLink(self, inputLink):
        inputLink.disconnectFromTable(self.__statusTable)
    
    def setPiece(self, inputPiece):
        inputPiece.connectToTable(self.__statusTable)
        
    def removePiece(self, inputPiece):
        inputPiece.disconnectFromTable(self.__statusTable)
    
    def update_DS_DueToRemoveLink(self, input_link):
        
        for piece in input_link.getPieces():
            nonPlaceableLinks = [possibleLink for possibleLink in list(self.__linksPerPiece[piece][1].values()) if possibleLink is not input_link]
            for possibleLink in nonPlaceableLinks:
                oppositePiece = possibleLink.getOpposite(piece)
                if(all([self.__statusTable[cell] is None for cell in possibleLink.intermediateCells]) and oppositePiece.link is None):
                    self.__linksPerPiece[piece][0][oppositePiece] = possibleLink
                    del self.__linksPerPiece[piece][1][oppositePiece]
                    
                    self.__linksPerPiece[oppositePiece][0][piece] = possibleLink
                    del self.__linksPerPiece[oppositePiece][1][piece]
                    
                    for cell in possibleLink.intermediateCells:
                        self.__linksPerCell[cell][1].append(possibleLink)
                        self.__linksPerCell[cell][2].remove(possibleLink)
        
        
        for cell in input_link.intermediateCells:
            terna = self.__linksPerCell[cell]
            terna[0] = None
            terna[1].append(input_link)
        
            if(len(terna[2]) > 0):
                possibleLink = terna[2][0]
                if(all([self.__statusTable[cell] is None for cell in possibleLink.intermediateCells]) and all([piece.link is None for piece in possibleLink.getPieces()])):

                    possibleLink = terna[2].pop()
                    for piece in possibleLink.getPieces():
                    
                        tupla = self.__linksPerPiece[piece]
                        oppositePiece = possibleLink.getOpposite(piece)
                        tupla[0][oppositePiece] = possibleLink
                        del tupla[1][oppositePiece]
            
                    for cell2 in possibleLink.intermediateCells:
                        if(cell2 != cell):
                            self.__linksPerCell[cell2][1].append(possibleLink)
                            self.__linksPerCell[cell2][2].remove(possibleLink)
                    
                    terna[1].append(possibleLink)
        
    def update_DS_DueToSetLink(self, input_link):
        poda = False
        for piece in input_link.getPieces():
            try:
                b = list(self.__linksPerPiece[piece][0].keys())[0]
            except:
                pass
            possibleLinks = [possibleLink for possibleLink in list(self.__linksPerPiece[piece][0].values()) if possibleLink is not input_link]
            for possibleLink in possibleLinks:
                oppositePiece = possibleLink.getOpposite(piece)
                
                del self.__linksPerPiece[piece][0][oppositePiece]
                self.__linksPerPiece[piece][1][oppositePiece] = possibleLink
                
                del self.__linksPerPiece[oppositePiece][0][piece]
                if(len(self.__linksPerPiece[oppositePiece][0]) == 0):poda = True
                self.__linksPerPiece[oppositePiece][1][piece] = possibleLink
                
                for cell in possibleLink.intermediateCells:
                    self.__linksPerCell[cell][1].remove(possibleLink)
                    self.__linksPerCell[cell][2].append(possibleLink)
                
        for cell in input_link.intermediateCells:
            terna = self.__linksPerCell[cell]
            terna[0] = input_link
            terna[1].remove(input_link)
            
            if(len(terna[1]) > 0):
                
                nonPossibleLink = terna[1].pop()
                for piece in nonPossibleLink.getPieces():
                    tupla = self.__linksPerPiece[piece]
                    oppositePiece = nonPossibleLink.getOpposite(piece)

                    del tupla[0][oppositePiece]
                    if(len(tupla[0]) == 0):poda = True
                    tupla[1][oppositePiece] = nonPossibleLink
            
                for cell2 in nonPossibleLink.intermediateCells:
                    if(cell2 != cell):
                        self.__linksPerCell[cell2][1].remove(nonPossibleLink)
                        self.__linksPerCell[cell2][2].append(nonPossibleLink)
                
                terna[2].append(nonPossibleLink)
            
        return poda
            
    def updateLinksPerPiece(self, input_piece, input_link, duringTableGeneration=False):
        self.__linksPerPiece[input_piece][0][input_link.getOpposite(input_piece)] = input_link
        if(duringTableGeneration):
            pass

    def updateLinksPerCell(self, input_link):
        for cell in input_link.intermediateCells:
            terna = self.__linksPerCell[cell]
            terna[1].append(input_link)

    def initDS(self):
        """ State """
        self.__statusTable = {(i, j):None for i in range(self.__numRows) for j in range(self.__numColumns)}
        
        """ data structures for a faster heuristic searching solutions during backtracking. """
        self.__linksPerPiece = {}
        self.__originalLinksPerPiece = {}
        
        self.__linksPerCell = {(i, j):[None, [], []] for i in range(self.__numRows) for j in range(self.__numColumns)}
        self.__originalLinksPerCell = {}
                
        self.__directNeighborsPerPiece = {}
        self.__originalDirectNeighborsPerPiece = {}
        
        self.__piecesPerRow = {i:[] for i in range(0, self.__numRows)}
        self.__piecesPerColumn = {j:[] for j in range(0, self.__numColumns)}
        
        self.__settedLinks = []
        self.__protectedLinks = []
    
    def prepareBoardToPlay(self):
        b = True
        while(b):
            try:
                settedLink = self.__settedLinks.pop()
                self.removeLink(settedLink)
            except:
                b = False
    
    def randomisedPopulateTable(self):
        
        def updateDirectNeighborsPerPiece(input_piece):
        
            def update(condition, input_piece, piece):
                if(condition):
                    
                    if(piece not in self.__directNeighborsPerPiece[input_piece] and input_piece not in self.__directNeighborsPerPiece[piece]):
                        newLink = link(input_piece, piece)
                        self.updateLinksPerPiece(input_piece, newLink, duringTableGeneration=True)
                        self.updateLinksPerPiece(piece, newLink, duringTableGeneration=True)
                        self.updateLinksPerCell(newLink)
                    
                    try:
                        if(piece not in self.__directNeighborsPerPiece[input_piece]):
                            self.__directNeighborsPerPiece[input_piece].append(piece)
                    except:
                        self.__directNeighborsPerPiece[input_piece] = [piece]
                    try:
                        if(input_piece not in self.__directNeighborsPerPiece[piece]):
                            self.__directNeighborsPerPiece[piece].append(input_piece)
                    except:
                        self.__directNeighborsPerPiece[piece] = [input_piece]
                    
                else:
                    pass
            
            row = input_piece.posx
            column = input_piece.posy
            
            ls = [piece for piece in self.__piecesPerRow[row] if (piece is not input_piece) and (piece not in self.__directNeighborsPerPiece[input_piece])]
            for piece in ls:
                if(piece.color is not input_piece.color):
                    if(piece.posy < input_piece.posy):
                        b = all([not(isinstance(self.__statusTable[(piece.posx, col)], gamePiece)) for col in range(piece.posy+1, input_piece.posy)])
                        update(b, input_piece, piece)
                    elif(piece.posy > input_piece.posy):
                        b = all([not(isinstance(self.__statusTable[(piece.posx, col)], gamePiece)) for col in range(input_piece.posy+1, piece.posy)])
                        update(b, input_piece, piece)
                    else:
                        pass
            
            ls = [piece for piece in self.__piecesPerColumn[column] if (piece is not input_piece) and (piece not in self.__directNeighborsPerPiece[input_piece])]
            for piece in ls:
                if(piece.color is not input_piece.color):
                    if(piece.posx < input_piece.posx):
                        b = all([not(isinstance(self.__statusTable[(fil, piece.posy)], gamePiece)) for fil in range(piece.posx+1, input_piece.posx)])
                        update(b, input_piece, piece)
                    elif(piece.posx > input_piece.posx):
                        b = all([not(isinstance(self.__statusTable[(fil, piece.posy)], gamePiece)) for fil in range(input_piece.posx+1, piece.posx)])
                        update(b, input_piece, piece)
                    else:
                        pass
            
        def getNeighborsFreeCells(cell):
            
            def update(res, i, j):
                b = True
                neighborCell = self.__statusTable[(i, j)]
                if(neighborCell is None):
                    res.append((i, j))
                else:
                    b = False
                return (res, b)

            res = []
            """ Derecha """
            i = cell[0]
            for j in range(cell[1]+1, self.__numColumns):
                res, b = update(res, i, j)
                if(not b):break
            """ Izquierda """
            i = cell[0]
            for j in reversed(range(0, cell[1])):
                res, b = update(res, i, j)
                if(not b):break
            """ Arriba """
            j = cell[1]
            for i in range(cell[0]+1, self.__numRows):
                res, b = update(res, i, j)
                if(not b):break
            """ Abajo """
            j = cell[1]
            for i in reversed(range(0, cell[0])):
                res, b = update(res, i, j)
                if(not b):break
            return res
        
        def checkOlderHypotheticalLinkViolation(input_link):
            
            def update(linkList):
                for forbiddenLink in linkList:

                    del self.__linksPerPiece[forbiddenLink.white][0][forbiddenLink.black]
                    del self.__linksPerPiece[forbiddenLink.black][0][forbiddenLink.white]
                    
                    self.__directNeighborsPerPiece[forbiddenLink.white].remove(forbiddenLink.black)
                    self.__directNeighborsPerPiece[forbiddenLink.black].remove(forbiddenLink.white)

                    for intermediateCell in forbiddenLink.intermediateCells:
                        terna = self.__linksPerCell[intermediateCell]
                        terna[1].remove(forbiddenLink)
                    
            piece1_position = input_link.white.position
            piece2_position = input_link.black.position
            
            linkList = list(self.__linksPerCell[piece1_position][1])
            update(linkList)

            linkList = list(self.__linksPerCell[piece2_position][1])
            update(linkList)
            
        def getAllCombinations(randomCell, neighborsFreeCells):
            lls = [[{randomCell: colorPiece.WHITE, neighborCell: colorPiece.BLACK}, {neighborCell: colorPiece.WHITE, randomCell: colorPiece.BLACK}] 
                   for neighborCell in neighborsFreeCells]
            return [dicc for lista_dicc in lls for dicc in lista_dicc]
        
        def selectCombinationByDifficulty(allCombinations):
            linkByDifficulty = list()
            for dicc in allCombinations:
                countDifferentColorNeighbor_bySide = [0, 0] 
                bothSides = list(dicc.keys())
                for (idx ,(piecePosition, pieceColor)) in enumerate(dicc.items()):
                    
                    acum = countDifferentColorNeighbor_bySide[idx]
                    
                    row = piecePosition[0]
                    column = piecePosition[1]
                    
                    otherSide = bothSides[0] if bothSides[0] != piecePosition else bothSides[1]
                    otherSide_row = otherSide[0]
                    otherSide_column = otherSide[1]
                                        
                    numNeighbors = 0
                    
                    ls = [piece for piece in self.__piecesPerRow[row] if 
                          not(piece.posy > column and otherSide_column > column and otherSide_column < piece.posy) and 
                          not(piece.posy < column and piece.posy < otherSide_column and otherSide_column < column)]
                    
                    for piece in ls:
                        if(piece.posy < column):
                            b = all([not(isinstance(self.__statusTable[(piece.posx, col)], gamePiece)) for col in range(piece.posy+1, column)])
                            if(b):
                                numNeighbors += 1
                                if(piece.color is not pieceColor):
                                    acum +=1
                        
                        elif(piece.posy > column):
                            b = all([not(isinstance(self.__statusTable[(piece.posx, col)], gamePiece)) for col in range(column+1, piece.posy)])
                            if(b):
                                numNeighbors += 1
                                if(piece.color is not pieceColor):
                                    acum +=1
                    
                    ls = [piece for piece in self.__piecesPerColumn[column] if 
                          not(piece.posx > row and otherSide_row > row and otherSide_row < piece.posx) and 
                          not(piece.posx < row and piece.posx < otherSide_row and otherSide_row < row)]
                    
                    for piece in ls:
                        
                        if(piece.posx < row):
                            b = all([not(isinstance(self.__statusTable[(fil, piece.posy)], gamePiece)) for fil in range(piece.posx+1, row)])
                            if(b):
                                numNeighbors += 1
                                if(piece.color is not pieceColor):
                                    acum +=1
                                    
                        elif(piece.posx > row):
                            b = all([not(isinstance(self.__statusTable[(fil, piece.posy)], gamePiece)) for fil in range(row+1, piece.posx)])
                            if(b):
                                numNeighbors += 1
                                if(piece.color is not pieceColor):
                                    acum +=1
                    
                    acum += 1
                    numNeighbors += 4

                    countDifferentColorNeighbor_bySide[idx] = acum/numNeighbors
                    
                lengthLink = -1 #La longitud del enlace ha de penalizar cuánto más largo es.
                
                if(bothSides[0][0] == bothSides[1][0]):
                    lengthLink = abs(bothSides[0][1] - bothSides[1][1])
                elif(bothSides[0][1] == bothSides[1][1]):
                    lengthLink = abs(bothSides[0][0] - bothSides[1][0])
                
                if(self.__linkDifficulty == 1.0):
                    lengthLinkWeight = ((self.__linkDifficulty + (self.__linkDifficulty - self.__percentageLevel))/2) #0.875
                else:
                    lengthLinkWeight = self.__linkDifficulty
                
                non_lengthLinkWeight = (1 - lengthLinkWeight)
                linkDifficulty = (non_lengthLinkWeight/2)*countDifferentColorNeighbor_bySide[0] + (non_lengthLinkWeight/2)*countDifferentColorNeighbor_bySide[1] + lengthLinkWeight*(1/lengthLink)
                linkByDifficulty.append((dicc, linkDifficulty))

            linkByDifficulty = sorted(linkByDifficulty, key=lambda tupla : tupla[1], reverse = False)
            return linkByDifficulty

        def generate():
            self.initDS()
            listCells = list(self.__statusTable.keys())
            
            while(len(listCells) > 0):
                                
                randomCell = listCells.pop(random.randint(0, len(listCells)-1))
                neighborsFreeCells = getNeighborsFreeCells(randomCell)
                allCombinations = getAllCombinations(randomCell, neighborsFreeCells)
                
                allCombinations = [tupla[0] for tupla in selectCombinationByDifficulty(allCombinations)]                
                since = self.__linkDifficulty - self.__percentageLevel
                idx_since = floor(len(allCombinations)*since)
                to = self.__linkDifficulty
                idx_to = floor(len(allCombinations)*to)
                allCombinations = list(allCombinations[idx_since:idx_to])
                
                random.shuffle(allCombinations)
                try:
                    choice = allCombinations.pop()
                except:
                    continue
                                
                position_dictKeys = list(choice.keys())
                color_dictValues = list(choice.values())            
                
                try:
                    listCells.remove(position_dictKeys[0] if position_dictKeys[0] != randomCell else position_dictKeys[1])
                except:
                    pass
                
                piece1 = gamePiece(posx=position_dictKeys[0][0], posy=position_dictKeys[0][1], color=color_dictValues[0])
                self.setPiece(piece1)
                
                self.__piecesPerRow[piece1.posx].append(piece1)
                self.__piecesPerColumn[piece1.posy].append(piece1)
                    
                piece2 = gamePiece(posx=position_dictKeys[1][0], posy=position_dictKeys[1][1], color=color_dictValues[1])
                self.setPiece(piece2)
                
                self.__piecesPerRow[piece2.posx].append(piece2)
                self.__piecesPerColumn[piece2.posy].append(piece2)
                
                self.__directNeighborsPerPiece[piece1] = []
                self.__directNeighborsPerPiece[piece2] = []
                
                self.__linksPerPiece[piece1] = [{}, {}]
                self.__linksPerPiece[piece2] = [{}, {}]
                
                newLink = link(piece1, piece2)
                
                self.__directNeighborsPerPiece[piece1].append(piece2)
                self.__directNeighborsPerPiece[piece2].append(piece1)
                self.updateLinksPerPiece(piece1, newLink, duringTableGeneration=True)
                self.updateLinksPerPiece(piece2, newLink, duringTableGeneration=True)
                self.updateLinksPerCell(newLink)
                
                for intermediateCell in newLink.intermediateCells:
                    try:
                        listCells.remove(intermediateCell)
                    except:
                        pass
                
                self.setLink(newLink)                

                checkOlderHypotheticalLinkViolation(newLink)
                
                updateDirectNeighborsPerPiece(input_piece=piece1)
                updateDirectNeighborsPerPiece(input_piece=piece2)
                
                self.__settedLinks.append(newLink)
                            
            self.saveOriginalLinksPerPiece()
            self.saveOriginalLinksPerCell()
            
        def generateUniqueSolution():
            self.initDS()
            
            self.saveOriginalDirectNeighborsPerPiece()
            self.saveOriginalLinksPerPiece()
            self.saveOriginalLinksPerCell()
            
            listCells = list(self.__statusTable.keys())
            while(len(listCells) > 0):
                
                randomCell = listCells.pop(random.randint(0, len(listCells)-1))
                neighborsFreeCells = getNeighborsFreeCells(randomCell)
                allCombinations = getAllCombinations(randomCell, neighborsFreeCells)

                allCombinations = [tupla[0] for tupla in selectCombinationByDifficulty(allCombinations)]                
                since = self.__linkDifficulty - self.__percentageLevel
                idx_since = floor(len(allCombinations)*since)
                to = self.__linkDifficulty
                idx_to = floor(len(allCombinations)*to)
                allCombinations = list(allCombinations[idx_since:idx_to])

                random.shuffle(allCombinations)
                
                stopCondition = False
                
                while(stopCondition == False):
                
                    try:
                        choice = allCombinations.pop()
                    except:
                        break
            
                    position_dictKeys = list(choice.keys())
                    color_dictValues = list(choice.values())            
                    
                    piece1 = gamePiece(posx=position_dictKeys[0][0], posy=position_dictKeys[0][1], color=color_dictValues[0])
                    self.setPiece(piece1)
                    
                    self.__piecesPerRow[piece1.posx].append(piece1)
                    self.__piecesPerColumn[piece1.posy].append(piece1)
                        
                    piece2 = gamePiece(posx=position_dictKeys[1][0], posy=position_dictKeys[1][1], color=color_dictValues[1])
                    self.setPiece(piece2)
                    
                    self.__piecesPerRow[piece2.posx].append(piece2)
                    self.__piecesPerColumn[piece2.posy].append(piece2)
                    
                    self.__directNeighborsPerPiece[piece1] = []
                    self.__directNeighborsPerPiece[piece2] = []
                    
                    self.__linksPerPiece[piece1] = [{}, {}]
                    self.__linksPerPiece[piece2] = [{}, {}]
                    
                    newLink = link(piece1, piece2)
                    
                    self.__directNeighborsPerPiece[piece1].append(piece2)
                    self.__directNeighborsPerPiece[piece2].append(piece1)
                    self.updateLinksPerPiece(piece1, newLink, duringTableGeneration=True)
                    self.updateLinksPerPiece(piece2, newLink, duringTableGeneration=True)
                    self.updateLinksPerCell(newLink)
                    
                    self.setLink(newLink)

                    checkOlderHypotheticalLinkViolation(newLink)
                    
                    updateDirectNeighborsPerPiece(input_piece=piece1)
                    updateDirectNeighborsPerPiece(input_piece=piece2)

                    aux = [settedLink for settedLink in self.__settedLinks]
                    self.__settedLinks.append(newLink)
                                        
                    self.prepareBoardToPlay()

                    valueReturnBackTracking = self.instantiateBackTracking()
                    for settedLink in aux:
                        self.setLink(settedLink)
                        self.__settedLinks.append(settedLink)
                    
                    if(len(valueReturnBackTracking) == 1):
                        stopCondition = True

                        try:
                            listCells.remove(position_dictKeys[0] if position_dictKeys[0] != randomCell else position_dictKeys[1])
                        except:
                            pass
                        
                        for intermediateCell in newLink.intermediateCells:
                            try:
                                listCells.remove(intermediateCell)
                            except:
                                pass
                            
                        self.__settedLinks.append(newLink)

                        self.saveOriginalLinksPerPiece()
                        self.saveOriginalLinksPerCell()
                        self.saveOriginalDirectNeighborsPerPiece()
                        
                    else:
                        
                        self.removeLink(newLink)
                        self.removePiece(piece1)
                        
                        self.__piecesPerRow[piece1.posx].remove(piece1)
                        self.__piecesPerColumn[piece1.posy].remove(piece1)
                            
                        self.removePiece(piece2)
                        
                        self.__piecesPerRow[piece2.posx].remove(piece2)
                        self.__piecesPerColumn[piece2.posy].remove(piece2)
                                                
                        self.loadOriginalDirectNeighborsPerPiece()
                        self.loadOriginalLinksPerPiece()
                        self.loadOriginalLinksPerCell()
                        
            self.saveOriginalLinksPerPiece()
            self.saveOriginalLinksPerCell()
                        
        if(self.__hasUniqueSolution==1):
            generateUniqueSolution()
        else:
            generate()
        
    def getObjByCellPosition(self, cellPosition):
        return self.__statusTable[cellPosition]
    
    def getAllPieces(self):
        return [v for (_, v) in self.__statusTable.items() if isinstance(v, gamePiece)]       
    
    def getStatusTable(self):
        return self.__statusTable
    
    def getSettedLinks(self):
        return self.__settedLinks
    
    def dropFromSettedLinks(self, settedLink):
        self.__settedLinks.remove(settedLink)
    
    def addToSettedLinks(self, input_link):
        self.__settedLinks.append(input_link)
    
    def addProtectedLink(self, input_link):
        self.__protectedLinks.append(input_link)
    
    def getProtectedLinks(self):
        return self.__protectedLinks
    
    def checkAllPiecesLinked(self):
        return (True if all(piece.link is not None for piece in self.getAllPieces()) else False)
    
    def saveOriginalDirectNeighborsPerPiece(self):
        res = {}
        for (piece, ls) in self.__directNeighborsPerPiece.items():
            newLs = list()
            for elem in ls:
                newLs.append(elem)
            res[piece] = newLs
        self.__originalDirectNeighborsPerPiece = res
        
    def loadOriginalDirectNeighborsPerPiece(self):
        res = {}
        for (piece, ls) in self.__originalDirectNeighborsPerPiece.items():
            newLs = list()
            for elem in ls:
                newLs.append(elem)
            res[piece] = newLs
        self.__directNeighborsPerPiece = res        
    
    def saveOriginalLinksPerPiece(self):
        res = {}
        for (piece, ls) in self.__linksPerPiece.items():
            newLs = list()
            for dicc in ls:
                newDicc = {}
                for (oppositePiece, gameLink) in dicc.items():
                    newDicc[oppositePiece] = gameLink
                newLs.append(newDicc)
            res[piece] = newLs
        self.__originalLinksPerPiece = res

    def loadOriginalLinksPerPiece(self):
        res = {}
        for (piece, ls) in self.__originalLinksPerPiece.items():
            newLs = list()
            for dicc in ls:
                newDicc = {}
                for (oppositePiece, gameLink) in dicc.items():
                    newDicc[oppositePiece] = gameLink
                newLs.append(newDicc)
            res[piece] = newLs
        self.__linksPerPiece = res
            
    def saveOriginalLinksPerCell(self):
        res = {}
        for (cell, ls) in self.__linksPerCell.items():
            newLs = list()
            for elem in ls:
                if(isinstance(elem, list)):
                    linkLs = list()
                    for gameLink in elem:
                        linkLs.append(gameLink)
                    newLs.append(linkLs)
                else:
                    NoneObj = elem
                    newLs.append(NoneObj)
            res[cell] = newLs
        self.__originalLinksPerCell = res
    
    def loadOriginalLinksPerCell(self):
        res = {}
        for (cell, ls) in self.__originalLinksPerCell.items():
            newLs = list()
            for elem in ls:
                if(isinstance(elem, list)):
                    linkLs = list()
                    for gameLink in elem:
                        linkLs.append(gameLink)
                    newLs.append(linkLs)
                else:
                    NoneObj = elem
                    newLs.append(NoneObj)
            res[cell] = newLs
        self.__linksPerCell = res
    
    def instantiateBackTrackingWithoutHeuristic(self):
        pieces = [piece for piece in self.__linksPerPiece.keys() if piece.link is None]
        return self.backTrackingWithoutHeuristic(pieceList=pieces, 
                                                 settedLinks=self.getSettedLinks(), 
                                                 solutions=list())
        
    def backTrackingWithoutHeuristic(self, pieceList, settedLinks, solutions):
        
        pendientes = [piece for piece in pieceList]
        res = solutions
        try:
            piece = pendientes.pop(0)
        except:
            res.append(settedLinks)
            return res
        lsDicc = self.__linksPerPiece[piece]
        allPossibilitiesDicc = dict()
        for dicc in lsDicc:
            for oppositePiece, gameLink in dicc.items():
                allPossibilitiesDicc[oppositePiece] = gameLink
        """ key: oppositePiece, value: gameLink """
        
        for oppositePiece, possibleLink in allPossibilitiesDicc.items():
            
            """ Comprobamos que la pieza opuesta no esté linkeada """
            if(oppositePiece.link is not None):
                continue
            
            """ Comprobamos que el camino entre piece y neighborPiece está despejado """
            allClear = True
            for cell in possibleLink.intermediateCells:
                if(self.__statusTable[cell] is not None):
                    allClear = False
                    break
            if(allClear is not True):
                continue
            
            self.setLink(possibleLink)
            
            newPieceList = [piece for piece in pendientes]
            newPieceList.remove(oppositePiece)
            
            newAcum = [settedLink for settedLink in settedLinks]
            newAcum.append(possibleLink)
            
            res = self.backTrackingWithoutHeuristic(newPieceList, newAcum, res)
            
            self.removeLink(possibleLink)
            
        return res
        
    def instantiateBackTracking(self):
        a = [(piece, dict_list[0]) for (piece, dict_list) in self.__linksPerPiece.items() if piece.link is None]
        pieces = sorted(a, key=lambda tupla : len(tupla[1]), reverse = False)
        pieces = [tupla[0] for tupla in pieces]
        
        return self.backTracking(pieceList=pieces, 
                                 settedLinks=self.getSettedLinks(), 
                                 solutions=list())

    def backTracking(self, pieceList, settedLinks, solutions):
        
        def poda(input_link):
            self.setLink(input_link)
            poda = self.update_DS_DueToSetLink(input_link)
            return poda

        pendientes = [piece for piece in pieceList]
        res = solutions
        try:
            piece = pendientes.pop(0)
        except:
            res.append(settedLinks)
            return res

        ls = [(opposite, possibleLink) for (opposite, possibleLink) in self.__linksPerPiece[piece][0].items()]
        for (opposite, possibleLink) in ls:

            if(poda(possibleLink)):
                self.removeLink(possibleLink)
                self.update_DS_DueToRemoveLink(possibleLink)
                continue
            else:
                newPieceList = [piece for piece in pendientes]

                newPieceList.remove(opposite)
                
                a = [(piece, dict_list[0]) for (piece, dict_list) in self.__linksPerPiece.items() if piece in newPieceList]
                pieces = sorted(a, key=lambda tupla : len(tupla[1]), reverse = False)
                newPieceList = [tupla[0] for tupla in pieces]
                
                newAcum = [settedLink for settedLink in settedLinks]
                newAcum.append(possibleLink)

                res = self.backTracking(newPieceList, newAcum, res)

                self.removeLink(possibleLink)
                self.update_DS_DueToRemoveLink(possibleLink)
                
        return res
                
    """ toString """
    def drawTable(self, entryTable=None):
        table = ""
        for i in range(self.__numRows):
            row = ""
            for j in range(self.__numColumns):
                cell = ""
                if(entryTable is not None):
                    obj = entryTable[(i, j)]
                else:
                    obj = self.__statusTable[(i, j)]
                if(isinstance(obj, gamePiece)):
                    if(obj.link is None):
                        """
                        |       |
                        | W  OR | B
                        |___    |___
                        """
                        cell = ["|   ", "| "+str(obj.str)+" ", "|___"]
                        for k in range(1, 3+1):
                            row = row[:(4*j*k+4*(k-1))]+cell[k-1]+row[(4*j*k+4*(k-1)):]
                    else:
                        directionLink = obj.link.directionLink()
                        linkedCells = obj.link.getLinkedCells()
                        sense = "-" if linkedCells.index((obj.posx, obj.posy)) == 0 else "+"
                        if(directionLink is directionLink.HORIZONTAL):
                            """
                            |       |
                            | W- OR --W 
                            |___    |___
                            """
                            cell = ["|   ", "| "+str(obj.str)+"-", "|___"] if sense == "-" else ["|   ", "--"+str(obj.str)+" ", "|___"]
                            for k in range(1, 3+1):
                                row = row[:(4*j*k+4*(k-1))]+cell[k-1]+row[(4*j*k+4*(k-1)):]
                        elif(directionLink is directionLink.VERTICAL):
                            """
                            | |     |   
                            | W  OR | W 
                            |___    |_|_
                            """
                            row = row[:(4*j)] + cell + row[(4*j):]
                            cell = ["| | ", "| "+str(obj.str)+" ", "|___"] if sense == "-" else ["|   ", "| "+str(obj.str)+" ", "|_|_"]
                            for k in range(1, 3+1):
                                row = row[:(4*j*k+4*(k-1))]+cell[k-1]+row[(4*j*k+4*(k-1)):]
                elif(isinstance(obj, link)):
                    directionLink = obj.directionLink()
                    if(directionLink is directionLink.HORIZONTAL):
                        """
                        |   
                        ----
                        |___
                        """
                        cell = ["|   ", "----", "|___"]
                        for k in range(1, 3+1):
                            row = row[:(4*j*k+4*(k-1))]+cell[k-1]+row[(4*j*k+4*(k-1)):]
                    elif(directionLink is directionLink.VERTICAL):
                        """
                        | | 
                        | | 
                        |_|_
                        """
                        cell = ["| | ", "| | ", "|_|_"]
                        for k in range(1, 3+1):
                            row = row[:(4*j*k+4*(k-1))]+cell[k-1]+row[(4*j*k+4*(k-1)):]
                else:
                    """
                    |
                    |
                    |___
                    """
                    cell = ["|   ", "|   ", "|___"]
                    for k in range(1, 3+1):
                        row = row[:(4*j*k+4*(k-1))]+cell[k-1]+row[(4*j*k+4*(k-1)):]

            sizeRow = len(row)
            for k in range(1, 3+1):
                right_end_wall = "|\n"
                row = row[:((sizeRow//3)*k + len(right_end_wall)*(k-1))]+right_end_wall+row[((sizeRow//3)*k + len(right_end_wall)*(k-1)):]
            table = row + table
        """
         ___ ___ ___ ___ ___ ___ ___ ___ 
        |   |   |   |   |   |   |   |   |
        """
        roof = ""
        for j in range(self.__numColumns):
            if(j==self.__numColumns-1):
                roof += " ___ \n"
            else:
                roof += " ___"
        table = roof+table
        return table
    
    @property
    def str(self):
        return self.drawTable()
    
    def __repr__(self):
        return self.str

class shirokuroGame(object):
    
    def __init__(self):
        self.preconditionSetDefaultValues()
        
    def preconditionSetDefaultValues(self):
        
        self.__maxNumRowsPerTable = 15
        self.__minNumRowsPerTable = 5
        self.__maxNumColumnsPerTable = 15
        self.__minNumColumnsPerTable = 5
        
        self.__difficultyLevels = {1:'easy', 2:'normal', 3:'hard', 4:'very hard'}
        self.__difficultyLevel = None
        
        self.__table = None
        self.__chrono = None
        
        self.__chronoStatus = None
        
        """ Ranking Score """
        self.__numHelps = None
        self.__timeDuration = None
        self.__score = None
        
        """ Solutions """
        self.__originalSolution = None
        self.__allSolutions = None
        self.__fromCurrentStateAllSolutions = None
        self.__calledResolutor = None
        
        """ Next State/Previous State """
        self.__currentState = None
        self.__savedState = None
        self.__path = None
        
        """ GamePassed """
        self.__gamePassed = None
    
    def loadState(self, maxNumRowsPerTable, minNumRowsPerTable, maxNumColumnsPerTable, minNumColumnsPerTable, difficultyLevels, difficultyLevel,
                  table, chrono, chronoStatus, numHelps, timeDuration, score, originalSolution, allSolutions, calledResolutor, currentState, savedState, path, gamePassed):
        
        self.__maxNumRowsPerTable = maxNumRowsPerTable
        self.__minNumRowsPerTable = minNumRowsPerTable
        self.__maxNumColumnsPerTable = maxNumColumnsPerTable
        self.__minNumColumnsPerTable = minNumColumnsPerTable
        
        self.__difficultyLevels = difficultyLevels
        self.__difficultyLevel = difficultyLevel
        
        self.__table = table
        self.__chrono = chrono
        
        self.__chronoStatus = chronoStatus
        
        """ Ranking Score """
        self.__numHelps = numHelps
        self.__timeDuration = timeDuration
        self.__score = score
        
        """ Solutions """
        self.__originalSolution = originalSolution
        self.__allSolutions = allSolutions
        self.__calledResolutor = calledResolutor
        
        """ Next State/Previous State """
        self.__currentState = currentState
        self.__savedState = savedState
        self.__path = path
        
        """ GamePassed """
        self.__gamePassed = gamePassed
    
    def maxNumRowsPerTable(self):
        return self.__maxNumRowsPerTable
    
    def minNumRowsPerTable(self):
        return self.__minNumRowsPerTable
    
    def maxNumColumnsPerTable(self):
        return self.__maxNumColumnsPerTable
    
    def minNumColumnsPerTable(self):
        return self.__minNumColumnsPerTable
    
    def difficultyLevels(self):
        return self.__difficultyLevels
    
    def difficultyLevel(self):
        return self.__difficultyLevel
    
    def chrono(self):
        return self.__chrono
    
    def chronoStatus(self):
        return self.__chronoStatus
    
    def numHelps(self):
        return self.__numHelps
    
    def setNumHelps(self, numHelps):
        self.__numHelps = numHelps
    
    def timeDuration(self):
        return self.__timeDuration
    
    def setTimeDuration(self, timeDuration):
        self.__timeDuration = timeDuration
    
    def score(self):
        return self.__score
    
    def setScore(self, score):
        self.__score = score
    
    def originalSolution(self):
        return self.__originalSolution
    
    def setOriginalSolution(self, originalSolution):
        self.__originalSolution = originalSolution
    
    def allSolutions(self):
        return self.__allSolutions
    
    def resetAllSolutions(self):
        self.__allSolutions = None
    
    def calledResolutor(self):
        return self.__calledResolutor
    
    def currentState(self):
        return self.__currentState
    
    def savedState(self):
        return self.__savedState
    
    def path(self):
        return self.__path
    
    def isGamePassed(self):
        self.setGamePassed(boolean_value=self.__table.checkAllPiecesLinked())
        return self.__gamePassed
    
    def setGamePassed(self, boolean_value):
        self.__gamePassed = boolean_value
    
    def saveState(self):
        self.__savedState = [elem for elem in self.path()]
        
    def goSavedState(self):
        self.restartGame()
        """ Cargamos la traza guardada """
        for elem in self.__savedState:
            if(elem is None):
                pass
            else:
                self.commitMove(choicedLink=elem)
    
    def saveState2(self):
        self.__savedState = self.__currentState
    
    def goSavedState2(self):
        """ Coloco al jugador donde estaba originalmente. """
        while(self.__currentState != self.__savedState):
            self.getPreviousState()
    
    def getCurrentBoard(self):
        return self.__table
    
    def defineGame2(self, numRows, numColumns, hasUniqueSolution, difficulty, hasClues, aidPercentage):
        self.preconditionSetDefaultValues()
        
        self.__difficultyLevel = difficulty
        
        percentageLevel = (1/len(self.__difficultyLevels))
        linkDifficulty = self.__difficultyLevel*percentageLevel
        
        self.__table = table(numRows, numColumns, hasUniqueSolution, hasClues, aidPercentage, percentageLevel, linkDifficulty)
        
        self.__numHelps = 0
        
        self.__table.randomisedPopulateTable()
        self.__originalSolution = [settedLink for settedLink in self.__table.getSettedLinks()]
        self.__table.prepareBoardToPlay()
        self.__currentState = 0
        self.__path = [None]
        
        self.__chrono = timeKeeper()
        self.__chrono.startTimeKeeper()
    
    def defineGame(self):
        self.preconditionSetDefaultValues()
        
        numRows = self.toChooseOption(selectorSwitch={rows: str(rows)+" filas" for rows in range(self.__minNumRowsPerTable, self.__maxNumRowsPerTable+1)},
                                      context="Seleccione el nÃºmero de filas para el tablero:\n")
        
        numColumns = self.toChooseOption(selectorSwitch={columns: str(columns)+" columnas" for columns in range(self.__minNumColumnsPerTable, self.__maxNumColumnsPerTable+1)},
                                         context="Seleccione el nÃºmero de columnas para el tablero:\n")

        hasUniqueSolution = self.toChooseOption(selectorSwitch={0:'No', 1:'SÃ­'}, 
                                                context="Â¿Tablero con soluciÃ³n Ãºnica?\n")
        
        self.__difficultyLevel = self.toChooseOption(selectorSwitch=self.__difficultyLevels,
                                                     context="Elija el nivel de dificultad\n")
        percentageLevel = (1/len(self.__difficultyLevels))
        linkDifficulty = self.__difficultyLevel*percentageLevel
        
        hasClues = int(input("With clues?(1:Yes/0:No)\n"))
        if(hasClues==1): 
            "Porcentaje de ayudas"
            aidPercentage = float(input("number between 0.0 and 0.5, represents board percentage gonna be resolved with helps, given by the system"))
        else:
            aidPercentage = 0.0
        
        self.__numHelps = 0
        
        self.__table = table(numRows, numColumns, hasUniqueSolution, hasClues, aidPercentage, percentageLevel, linkDifficulty)
        self.__table.randomisedPopulateTable()
        self.__originalSolution = [settedLink for settedLink in self.__table.getSettedLinks()]
        self.__table.prepareBoardToPlay()
        
        self.__currentState = 0
        self.__path = [None]
    
    def computeScore(self):
        
        def func_inverso(x):
            if(x > 0):
                return(1/x)
            else:
                return 0

        x = (self.__numHelps*(1000) + (self.__timeDuration) + 1)
        self.__score = func_inverso(x)
    
    def computeScore1(self, numHelps, timeDuration, difficulty=None, numRows=None, numColumns=None, numPieces=None):
        
        def func_inverso(x):
            if(x > 0):
                return(1/x)
            else:
                return 0

        x = (numHelps*(1000) + (timeDuration) + 1)
        self.__score = func_inverso(x)
    
    def computeScore2(self, numHelps, timeDuration, difficulty=None, numRows=None, numColumns=None):
        if(self.__calledResolutor==True):
            self.__score = float('-inf')
        else:
            x = (numHelps*(-1000) + (-1)*(timeDuration))
            self.__score = (x)
    
    def commitMove(self, choicedLink):
        
        self.__table.setLink(choicedLink)
        self.__table.update_DS_DueToSetLink(choicedLink)
        self.__table.addToSettedLinks(choicedLink)
        
        idx = self.__currentState+1
        while(len(self.__path) != idx):
            self.__path.pop(idx)
        
        self.__currentState += 1
        self.__path.append(choicedLink)
    
    def commitUndoMove(self, linkFromChoice):
                
        self.__table.removeLink(linkFromChoice)
        
        self.__table.update_DS_DueToRemoveLink(linkFromChoice)
        self.__table.dropFromSettedLinks(linkFromChoice)
        
        idx = self.__currentState+1
        while(len(self.__path) != idx):
            self.__path.pop(idx)
            
        self.__currentState -= 1
        self.__path.remove(linkFromChoice)
        
    def getHelp(self):
        self.__numHelps += 1
        self.auxGetHelp()
    
    def auxGetHelp(self):
        
        def method1():
            while(len(self.__fromCurrentStateAllSolutions) == 0):
                self.getPreviousState()
                self.__fromCurrentStateAllSolutions = self.__table.instantiateBackTracking()
            self.auxGetHelp()

        def method2():
            pila = [list() for settedLink in self.__table.getSettedLinks()]
            b = False
            while(len(pila) > 0 or b == False):
                ls = pila.pop()
                for gameLink in ls:
                    self.commitUndoMove(gameLink)
                
                lsSettedLinks = [elem for elem in self.__table.getSettedLinks()]
                for settedLink in lsSettedLinks:
                    self.commitUndoMove(settedLink)
                    
                    self.__fromCurrentStateAllSolutions = self.__table.instantiateBackTracking()
                    if(len(self.__fromCurrentStateAllSolutions) > 0):
                        self.auxGetHelp()
                        b = True
                        
                        break
                    else:
                        newLs = list(ls)
                        newLs.append(settedLink)
                        pila.append(newLs)
                    
                    self.commitMove(settedLink)
                
                if(b):
                    break
                else:
                    for gameLink in reversed(ls):
                        self.commitMove(gameLink)

        self.__fromCurrentStateAllSolutions = self.__table.instantiateBackTracking()
        if(len(self.__fromCurrentStateAllSolutions) > 0):
            randomSolution = random.choice(self.__fromCurrentStateAllSolutions)
            allNonSettedLinks = [gameLink for gameLink in randomSolution if gameLink not in self.__table.getSettedLinks()]
            randomLink = random.choice(allNonSettedLinks)
            self.commitMove(randomLink)
            self.__table.addProtectedLink(randomLink)
            return randomLink
        else:
            #method1()
            method2()

    def restartGame(self):

        self.__table.prepareBoardToPlay()
        
        self.__currentState = 0
        self.__path = [None]
        
        self.__table.loadOriginalLinksPerPiece()
        self.__table.loadOriginalLinksPerCell()
    
    def computeMean(self):
        i = 1
        ls = list()
        while(i <= 3):
            (tiempo_ejecucion1, tiempo_ejecucion2) = self.compareBackTrackings()
            ls.append((tiempo_ejecucion1, tiempo_ejecucion2))
            i = i + 1
        mean1 = 0
        mean2 = 0
        for tupla in ls:
            mean1 = mean1 + tupla[0]
            mean2 = mean2 + tupla[1]
        res1 = mean1/len(ls)
        res2 = mean2/len(ls)
        print(ls)
        print("mean w/ Heur: "+str(res1)+", mean w/o Heur: "+str(res2))
            
    def compareBackTrackings(self):

        tiempo_inicial = time.time()
        allSolutions = len(self.__table.instantiateBackTracking())
        tiempo_final = time.time()
        tiempo_ejecucion1 = tiempo_final - tiempo_inicial
        self.restartGame()
        print("w/ Heur. nº solutions: "+str(allSolutions)+", time: "+str(tiempo_ejecucion1))
        
        time.sleep(10)

        tiempo_inicial = time.time()
        allSolutionsWithoutHeuristic = len(self.__table.instantiateBackTrackingWithoutHeuristic())
        tiempo_final = time.time()
        tiempo_ejecucion2 = tiempo_final - tiempo_inicial
        self.restartGame()
        print("w/o Heur. nº solutions: "+str(allSolutionsWithoutHeuristic)+", time: "+str(tiempo_ejecucion2))
        
        time.sleep(10)
        
        if(not(allSolutions - allSolutionsWithoutHeuristic == 0)):
            raise Exception("Different number solutions")
        else:
            return (tiempo_ejecucion1, tiempo_ejecucion2)
    
    def getPreviousState(self):
        if(self.__currentState > 0):
            linkToDropFromTable = self.__path[self.__currentState]
            self.__table.removeLink(linkToDropFromTable)
            self.__table.update_DS_DueToRemoveLink(linkToDropFromTable)
            self.__table.dropFromSettedLinks(linkToDropFromTable)
            self.__currentState -= 1
    
    def getNextState(self):
        if(self.__currentState < (len(self.__path)-1)):
            self.__currentState += 1
            linkToAddToTable = self.__path[self.__currentState]
            self.__table.setLink(linkToAddToTable)
            self.__table.update_DS_DueToSetLink(linkToAddToTable)
            self.__table.addToSettedLinks(linkToAddToTable)
    
    def getSolutionFromCurrentStatus(self):
        self.__calledResolutor = True
        while(self.isGamePassed() == False):
            self.auxGetHelp()
    
    def getOriginalSolution(self):
        self.__calledResolutor = True
        self.buildOriginalSolution()
    
    def buildOriginalSolution(self):
        self.buildSolution(self.__originalSolution)
    
    def buildSolution(self, solutionLinkList):
        settedLinks = list(self.__table.getSettedLinks())
        for settedLink in settedLinks:
            if(settedLink not in solutionLinkList):
                self.__table.removeLink(settedLink)
                self.__table.dropFromSettedLinks(settedLink)
            else:
                solutionLinkList.remove(settedLink)
        for linkFromSolution in solutionLinkList:
            self.__table.setLink(linkFromSolution)
            self.__table.addToSettedLinks(linkFromSolution)
    
    def getNumberOfSolutions(self):
        if(self.__allSolutions is None):
            self.__allSolutions = self.__table.instantiateBackTracking()
        return len(self.__allSolutions)
    
    def getAllSolutions(self):
        self.__calledResolutor = True
        self.__score = 0
        if(self.__allSolutions is None):
            self.restartGame()
            self.__allSolutions = self.__table.instantiateBackTracking()
        return self.__allSolutions
    
    def getSolutionByInputNumber(self, input_number):
        self.buildSolution(list(self.__allSolutions[input_number]))
    
    def showAllSolutions(self):
        
        self.getAllSolutions()
            
        selectorSwitch = {1: "Anterior",
                          2: "Siguiente",
                          3: "Introducir número",
                          4: "Salir"}
        
        i = 0
        self.buildSolution(list(self.__allSolutions[i]))
        choice = self.toChooseOption(selectorSwitch, context=self.__table.drawTable()+"\nSolución (Actual: "+str(i+1)+"/"+str(len(self.__allSolutions))+")\nSeleccione una opción:\n")
        stopCondition = len(selectorSwitch)
        while(choice != stopCondition):
            if(choice == 1):
                i = (i - 1) if i > 0 else 0
            elif(choice == 2):
                i = (i + 1) if i < (len(self.__allSolutions)-1) else (len(self.__allSolutions)-1)
            elif(choice == 3):
                i = int(input("Introduzca el número de la solución: de 1 a "+str(len(self.__allSolutions))+"\n"))
            self.getSolutionByInputNumber(i)
            choice = self.toChooseOption(selectorSwitch, context=self.__table.drawTable()+"\nSolución (Actual: "+str(i+1)+"/"+str(len(self.__allSolutions))+")\nSeleccione una opción:\n")
    
    def fromOriginalStateGuideSolution(self):
        
        self.__calledResolutor = True
        idx = self.__currentState
        
        while(self.isGamePassed() == False):
            self.auxGetHelp()
        
        while(self.__currentState != idx):
            self.getPreviousState()
        
    def helpingLoop(self):
        self.__calledResolutor = True
        while(self.isGamePassed() == False):
            self.auxGetHelp()
            
    def returnToGivenState(self, idx):
        
        while(self.__currentState != idx):
            self.getPreviousState()
        
    def getGuideSolution(self):
                
        def operatorSwitch(op):
            
            if(op == 1):
                self.getNextState()
            elif(op == 2):
                self.getPreviousState()
        
        selectorSwitch = {1: "Siguiente",
                          2: "Anterior",
                          3: "Salir"}
        
        self.fromOriginalStateGuideSolution()
        
        choice = self.toChooseOption(selectorSwitch, context=self.__table.drawTable()+"\Seleccione una opción: \n")
        stopCondition = len(selectorSwitch)
        while(choice != stopCondition):
            operatorSwitch(choice)
            choice = choice = self.toChooseOption(selectorSwitch, context=self.__table.drawTable()+"\Seleccione una opción: \n")
    
    def getTableSameMetrics(self):
        self.__numHelps = 0
        self.__table.randomisedPopulateTable()
        self.__originalSolution = [settedLink for settedLink in self.__table.getSettedLinks()]
        self.__table.prepareBoardToPlay()
        self.__currentState = 0
        self.__path = [None]
        try:
            self.__chrono.reset()
        except:
            """ type(self.__chrono) == int """
            """ getTableSameMetrics from load game"""
            self.__chrono = timeKeeper()
            self.__chrono.startTimeKeeper()
    
    def playMenu(self):

        def playAlgorithm():
            
            lss = [[gameLink.white, gameLink.black] for gameLink in self.__table.getProtectedLinks()]
            piecesFromHelpLinks = [pieceFromHelpLink for ls in lss for pieceFromHelpLink in ls]
            pieceList = [piece for piece in self.__table.getAllPieces() if piece not in piecesFromHelpLinks]
            
            b = False
            choice = None
            while(b == False):
                i = 1
                txt = ""
                txt += "Seleccione una pieza:\n"
                for piece in pieceList:
                    if(i%10==0):
                        txt += "    Pieza "+str(i)+": "+str(piece)+": "+str(piece.position)+"\n"
                    else:
                        txt += "    Pieza "+str(i)+": "+str(piece)+": "+str(piece.position)
                    i += 1
                txt += "    \nOpción "+str(i)+": Salir\n"
                i += 1
                try:
                    choice = int(input(txt))
                except:
                    print("Escoja un número")
                    continue
                if(choice not in [num_choice for num_choice in range(1, i+1)]):
                    print("Escoja una opción vÃ¡lida")
                    continue
                elif(choice == i-1):
                    break
                else:
                    choice = pieceList[choice-1]
                    linkFromChoice = choice.link
                    if(linkFromChoice is not None):
                        linkFromChoiceDeletion = int(input("Esta pieza ya estÃ¡ enlazada, Â¿Quiere borrar el enlace previo?(1:Yes/0:No)\n"))
                        if(linkFromChoiceDeletion == 1):
                            self.commitUndoMove(linkFromChoice)
                            print(self.__table)
                    if(choice.link is None):
                        while(b == False):
                            i = 1
                            txt = ""
                            txt += "Seleccione un vecino con el cual enlazar la ficha:\n"
                            linkSelector = [possibleLink for possibleLink in self.__table.getLinksPerPiece(choice)]
                            for possibleLink in linkSelector:
                                oppositePiece = possibleLink.getOpposite(choice)
                                txt += "    Pieza "+str(i)+": "+str(oppositePiece)+": "+str(oppositePiece.position)
                                i += 1
                            txt += "    Pieza "+str(i)+": Cambiar de pieza\n"
                            choicedLink = int(input(txt))
                            if(choicedLink not in [num_choice for num_choice in range(1, i+1)]):
                                raise Exception("Escoja un vecino vÃ¡lido")
                            elif(choicedLink == [num_choice for num_choice in range(1, i+1)][-1]):
                                b = "Cambiar de pieza"
                                break
                            else:
                                b = True
                                choicedLink = linkSelector[choicedLink-1]
                        if(b == "Cambiar de pieza"):
                            b = False
                            continue
                        elif(b):
                            self.commitMove(choicedLink)
                            break
                
        def operatorSwitch(op):
            
            if(op == 1):
                playAlgorithm()
            elif(op == 2):
                self.getHelp()
            elif(op == 3):
                self.getPreviousState()
            elif(op == 4):
                self.getNextState()
            elif(op == 5):
                game.saveState()
            elif(op == 6):
                game.goSavedState()
            elif(op == 7):
                self.getOriginalSolution()
                print(self.__table)
            elif(op == 8):
                self.getSolutionFromCurrentStatus()
                print(self.__table)
            elif(op == 9):
                self.restartGame()
            elif(op == 10):
                self.showAllSolutions()
            elif(op == 11):
                self.__chrono.pauseTimeKeeper()
            elif(op == 12):
                print(self.__chrono)
            elif(op == 13):
                self.__chrono.startTimeKeeper()
            elif(op == 14):
                self.getTableSameMetrics()
            elif(op == 15):
                print("Guardar partida")
                pass
            elif(op == 16):
                print("SoluciÃ³n guiada")
                self.getGuideSolution()
            elif(op == 17):
                print("Otro tablero con distintas dimensiones")
                self.defineGame()
                self.__chrono.reset()
            elif(op == 18):
                self.getInstructions()
            elif(op == 19):
                print("Listar ayudas utilizadas hasta el momento ")
                for protectedLink in self.__table.getProtectedLinks():
                    print(protectedLink)
            elif(op == 20):
                print("Ranking")
                pass
            elif(op == 21):
                print("Cargar partida")
                pass
            elif(op == 22):
                print("Comparar BackTrackings")
                self.computeMean()
            elif(op == 23):
                print("Quiere guardar la partida antes de salirÂ¿?")
                pass
        
        selectorSwitch = {1: "Mover ?",
                          2: "Ayuda",
                          3: "Volver al estado anterior ?",
                          4: "Volver al estado posterior ?",
                          5: "Guardar estado",
                          6: "Volver al estado guardado",
                          7: "SoluciÃ³n original del tablero ?",
                          8: "Solucionar tablero respetando la disposiciÃ³n actual",
                          9: "Reiniciar juego ?",
                          10: "Todas las soluciones ?",
                          11: "Pausar ?",
                          12: "Tiempo transcurrido ?",
                          13: "Reanudar ?",
                          14: "Otro tablero con iguales dimensiones ?",
                          15: "Guardar partida",
                          16: "SoluciÃ³n guiada",
                          17: "Otro tablero con distintas dimensiones ?",
                          18: "Instrucciones ?",
                          19: "Listar ayudas utilizadas hasta el momento ",
                          20: "Ranking",
                          21: "Cargar partida",
                          22: "Comparar BackTrackings",
                          23: "Salir ?"}
        
        print(self.__table)
        choice = self.toChooseOption(selectorSwitch)
        
        stopCondition = max(list(selectorSwitch.keys()))
        
        while(choice != stopCondition):
            operatorSwitch(choice)
            if(self.isGamePassed()):
                self.__chrono.pauseTimeKeeper()
                self.__timeDuration = self.__chrono.getTimeElapsed
                if(self.__calledResolutor):
                    print("Game Passed and resolutor was called")
                    self.__score = 0
                else:
                    self.computeScore()
                    print("Partida superada, Â¡enhorabuena!")
                    print("Guardar en ranking.")
                choice = stopCondition
            else:
                print(self.__table)
                choice = self.toChooseOption(selectorSwitch)
    
    def getInstructions(self):
        print("Instrucciones del juego:\n")
    
    def toChooseOption(self, selectorSwitch, context=None):
        
        def getMenuOptions(selectorSwitch):
            options = ""
            for (k, v) in selectorSwitch.items():
                options += "Opción "+str(k)+": "+v+"\n"
            options += "Selección: "
            return options
        
        options = context if context is not None else ""
        options += getMenuOptions(selectorSwitch)
        b = False
        choice = None
        while(b == False):
            try:
                order = int(input(options))
                selectorSwitch[order]
                choice = order
                b = True
            except:
                pass
        return choice
        
    def boardGenerationTime(self):
        
        def boardGeneration(nRows, nCols, unitarySolution, level):
            """ Preparamos el tablero """
            self.preconditionSetDefaultValues()
            numRows = nRows
            numColumns = nCols
            hasUniqueSolution = unitarySolution
            self.__difficultyLevel = level
            percentageLevel = (1/len(self.__difficultyLevels))
            linkDifficulty = self.__difficultyLevel*percentageLevel
            hasClues = 0
            aidPercentage = 0.0
            self.__numHelps = 0
            self.__table = table(numRows, numColumns, hasUniqueSolution, hasClues, aidPercentage, percentageLevel, linkDifficulty)
            self.__table.randomisedPopulateTable()
            self.__originalSolution = [settedLink for settedLink in self.__table.getSettedLinks()]
            self.__table.prepareBoardToPlay()
            self.__currentState = 0
            self.__path = [None]
        
        f = open("./results.txt", "w+")
        f.close()
        f = open("./results.txt", "a+")
        f.write("#########"+"\n")
        """ Dimensiones: desde 5x5 hasta 15x15 """
        for i in range(5, 15+1):
            
            ls_means_nonUnitary = list()
            ls_means_unitary = list()
            """ 5 tableros de dimensión ixi """
            for j in range(1, 5+1):
                
                ls = list()
                seed = random.randint(1, 20)
                for k in range(1, 3+1):
                    """ Reiniciamos la semilla a valor 1 en cada generación del tablero"""
                    random.seed(seed)
                    tiempo_inicial = time.time()
                    boardGeneration(i, i, 0, 4)
                    tiempo_final = time.time()
                    tiempo_ejecucion1 = tiempo_final - tiempo_inicial
                    ls.append(tiempo_ejecucion1)

                    f.write("dimensión: "+str(i)+"x"+str(i)+", unitary: "+str(0)+", board nº: "+str(j)+", repetición: "+str(k)+", time: "+str(tiempo_ejecucion1)+"\n")
                    time.sleep(10)
                
                f.write("Mean time board nº "+str(j)+", nonUnitary: "+str(sum(ls)/3)+"\n")
                ls_means_nonUnitary.append(sum(ls)/3)
                f.write("#########"+"\n")
                
                ls = list()
                seed = random.randint(1, 20)
                for k in range(1, 3+1):
                    """ Reiniciamos la semilla a valor 1 en cada generación del tablero"""
                    random.seed(seed)
                    tiempo_inicial = time.time()
                    boardGeneration(i, i, 1, 4)
                    tiempo_final = time.time()
                    tiempo_ejecucion2 = tiempo_final - tiempo_inicial
                    ls.append(tiempo_ejecucion2)

                    f.write("dimensión: "+str(i)+"x"+str(i)+", unitary: "+str(1)+", board nº: "+str(j)+", repetición: "+str(k)+", time: "+str(tiempo_ejecucion2)+"\n")
                    time.sleep(10)
                
                f.write("Mean time board nº "+str(j)+", unitary: "+str(sum(ls)/3)+"\n")
                ls_means_unitary.append(sum(ls)/3)
                f.write("#########"+"\n")
            
            f.write("Mean board "+str(i)+"x"+str(i)+", nonUnitary: "+str(sum(ls_means_nonUnitary)/5)+"\n")
            f.write("Mean board "+str(i)+"x"+str(i)+", unitary: "+str(sum(ls_means_unitary)/5)+"\n")
                    
        f.close()
        
    def mainMenu(self):
        
        def initNewGame():
            self.defineGame()
            self.__chrono = timeKeeper()
            self.__chrono.startTimeKeeper()
            self.playMenu()
            
        def loadGame():
            self.playMenu()
        
        def deleteGame():
            print("Borrar partida anterior")
        
        def operatorSwitch(op):
            
            if(op == 1):
                initNewGame()
            elif(op == 2):
                loadGame()
            elif(op == 3):
                deleteGame()
            elif(op == 4):
                self.getInstructions()
            elif(op == 5):
                pass
            
        selectorSwitch = {1: "Jugar nueva partida ?",
                          2: "Cargar partida anterior",
                          3: "Borrar partida anterior",
                          4: "Instrucciones ?",
                          5: "Salir ?"}
        
        choice = self.toChooseOption(selectorSwitch, context="Seleccione una opciÃ³n del menÃº principal:\n")
        stopCondition = len(selectorSwitch)
        while(choice != stopCondition):
            operatorSwitch(choice)
            choice = self.toChooseOption(selectorSwitch, context="Seleccione una opciÃ³n del menÃº principal:\n")




class saver(object):
    
    def __init__(self):
        pass
    
    def getNamePiece(self, piece):
        str_posx = str(piece.posx)
        str_posy = str(piece.posy)
        str_color = "White" if piece.color is colorPiece.WHITE else "Black"
        namePiece = "piece"+"_"+str_posx+"_"+str_posy+"_"+str_color
        return namePiece
    
    def buildSTRdiccStatusTable(self):
        
        diccStatusTable = dict()
        for k, v in game.getCurrentBoard().getStatusTable().items():
            str_k = str(k)
            str_v = None
            if(v is None):
                str_v = str(None)
            elif(isinstance(v, gamePiece)):
                namePiece = self.getNamePiece(v)
                str_v = namePiece
            elif(isinstance(v, link)):
                nameLink = v.str
                str_v = nameLink
            else:
                raise Exception("Bug")
            diccStatusTable[str_k] = str_v
        return diccStatusTable
    
    def buildSTRdiccLinksPerPiece(self):
        
        diccLinksPerPiece = dict()
        for piece, ls in game.getCurrentBoard().getAllLinksPerPiece().items():
            namePiece = self.getNamePiece(piece)
            key_ls = list()
            for dicc in ls:
                newDicc = dict()
                for k, v in dicc.items():
                    oppositeNamePiece = self.getNamePiece(k)
                    nameLink = v.str
                    newDicc[oppositeNamePiece] = nameLink
                key_ls.append(newDicc)
            diccLinksPerPiece[namePiece] = key_ls
        return diccLinksPerPiece
    
    def buildSTRdiccOriginalLinksPerPiece(self):
        
        diccOriginalLinksPerPiece = dict()
        for piece, ls in game.getCurrentBoard().getAllOriginalLinksPerPiece().items():
            namePiece = self.getNamePiece(piece)
            key_ls = list()
            for dicc in ls:
                newDicc = dict()
                for k, v in dicc.items():
                    oppositeNamePiece = self.getNamePiece(k)
                    nameLink = v.str
                    newDicc[oppositeNamePiece] = nameLink
                key_ls.append(newDicc)
            diccOriginalLinksPerPiece[namePiece] = key_ls
        return diccOriginalLinksPerPiece
    
    def buildSTRdiccLinksPerCell(self):
        
        diccLinksPerCell = dict()
        for cell, ls in game.getCurrentBoard().getAllLinksPerCell().items():
            key = str(cell)
            value_ls = list()
            for elem in ls:
                if(elem is None):
                    value_ls.append(None)
                elif(isinstance(elem, link)):
                    value_ls.append(elem.str)
                elif(isinstance(elem, list)):
                    newLs = list()
                    for gameLink in elem:
                        newLs.append(gameLink.str)
                    value_ls.append(newLs)
            diccLinksPerCell[key] = value_ls
        return diccLinksPerCell
    
    def buildSTRdiccOriginalLinksPerCell(self):
        
        diccOriginalLinksPerCell = dict()
        for cell, ls in game.getCurrentBoard().getAllOriginalLinksPerCell().items():
            key = str(cell)
            value_ls = list()
            for elem in ls:
                if(elem is None):
                    value_ls.append(None)
                elif(isinstance(elem, link)):
                    value_ls.append(elem.str)
                elif(isinstance(elem, list)):
                    newLs = list()
                    for gameLink in elem:
                        newLs.append(gameLink.str)
                    value_ls.append(newLs)
            diccOriginalLinksPerCell[key] = value_ls
        return diccOriginalLinksPerCell
    
    def buildSTRdiccDirectNeighborsPerPiece(self):
        
        diccDirectNeighborsPerPiece = dict()
        for piece, neighborLs in game.getCurrentBoard().getAllDirectNeighborsPerPiece().items():
            namePiece = self.getNamePiece(piece)
            value_ls = list()
            for elem in neighborLs:
                neighborName = self.getNamePiece(elem)
                value_ls.append(neighborName)
            diccDirectNeighborsPerPiece[namePiece] = value_ls
        return diccDirectNeighborsPerPiece
    
    def buildSTRdiccOriginalDirectNeighborsPerPiece(self):
        
        diccOriginalDirectNeighborsPerPiece = dict()
        for piece, neighborLs in game.getCurrentBoard().getAllOriginalDirectNeighborsPerPiece().items():
            namePiece = self.getNamePiece(piece)
            value_ls = list()
            for elem in neighborLs:
                neighborName = self.getNamePiece(elem)
                value_ls.append(neighborName)
            diccOriginalDirectNeighborsPerPiece[namePiece] = value_ls
        return diccOriginalDirectNeighborsPerPiece
    
    def buildSTRdiccPiecesPerRow(self):
        
        diccPiecesPerRow = dict()
        for i in range(game.getCurrentBoard().getNumRows()):
            value_ls = list()
            for piece in game.getCurrentBoard().getPiecesPerRow(row=i):
                namePiece = self.getNamePiece(piece)
                value_ls.append(namePiece)
            diccPiecesPerRow[i] = value_ls
        return diccPiecesPerRow
    
    def buildSTRdiccPiecesPerColumn(self):
        
        diccPiecesPerColumn = dict()
        if(len(game.getCurrentBoard().getPiecesPerColumn(column=None))==0):
            pass
        else:
            for j in range(game.getCurrentBoard().getNumColumns()):
                value_ls = list()
                for piece in game.getCurrentBoard().getPiecesPerColumn(column=j):
                    namePiece = self.getNamePiece(piece)
                    value_ls.append(namePiece)
                diccPiecesPerColumn[j] = value_ls
        return diccPiecesPerColumn
    
    def buildSTRlsSettedLinks(self):
        
        lsSettedLinks = list()
        for gameLink in game.getCurrentBoard().getSettedLinks():
            strGameLink = gameLink.str
            lsSettedLinks.append(strGameLink)
        return lsSettedLinks
    
    def buildSTRlsProtectedLinks(self):
        
        lsProtectedLinks = list()
        for gameLink in game.getCurrentBoard().getProtectedLinks():
            strGameLink = gameLink.str
            lsProtectedLinks.append(strGameLink)
        return lsProtectedLinks
    
    def saveGameData(self, slot=None):
    
        final_dicc = dict()
        
        pieceDict = dict()
        for piece in game.getCurrentBoard().getAllPieces():
            str_color = "White" if piece.color is colorPiece.WHITE else "Black"
            namePiece = self.getNamePiece(piece)
            pieceDict[namePiece] = {'posx':piece.posx, 'posy':piece.posy, 'color':str_color, 'link':None}
        
        linkDict = dict()
        for gameLink in game.getCurrentBoard().getAllLinks():
            
            str_white = self.getNamePiece(gameLink.white)
            str_black = self.getNamePiece(gameLink.black)
            
            str_direction = "Horizontal" if gameLink.directionLink() is directionLink.HORIZONTAL else "Vertical"
            nameLink = gameLink.str
    
            linkDict[nameLink] = {'white':str_white, 'black':str_black, 'direction':str_direction, 'linkedCells':gameLink.linkedCells, 'intermediateCells':gameLink.intermediateCells}
            
            if((gameLink.white.link is not None) and (gameLink.black.link is not None) and (gameLink.white.link is gameLink) and (gameLink.black.link is gameLink) and (gameLink.white.link is gameLink.black.link)):
    
                dicc_white = {k:v for k, v in pieceDict[str_white].items()}
                dicc_black = {k:v for k, v in pieceDict[str_black].items()}
                
                dicc_white['link'] = nameLink
                pieceDict[str_white] = dicc_white
                dicc_black['link'] = nameLink
                pieceDict[str_black] = dicc_black
            
        final_dicc['allPieces'] = pieceDict
        final_dicc['allLinks'] = linkDict
        
        diccStatusTable = self.buildSTRdiccStatusTable()
        diccLinksPerPiece = self.buildSTRdiccLinksPerPiece()
        diccOriginalLinksPerPiece = self.buildSTRdiccOriginalLinksPerPiece()
        diccLinksPerCell = self.buildSTRdiccLinksPerCell()
        diccOriginalLinksPerCell = self.buildSTRdiccOriginalLinksPerCell()
        diccDirectNeighborsPerPiece = self.buildSTRdiccDirectNeighborsPerPiece()
        diccOriginalDirectNeighborsPerPiece = self.buildSTRdiccOriginalDirectNeighborsPerPiece()
        diccPiecesPerRow = self.buildSTRdiccPiecesPerRow()
        diccPiecesPerColumn = self.buildSTRdiccPiecesPerColumn()
        lsSettedLinks = self.buildSTRlsSettedLinks()
        lsProtectedLinks = self.buildSTRlsProtectedLinks()

        value_dicc = dict()
        
        value_dicc['numRows'] = game.getCurrentBoard().getNumRows()
        value_dicc['numColumns'] = game.getCurrentBoard().getNumColumns()
        value_dicc['hasUniqueSolution'] = game.getCurrentBoard().hasUniqueSolution()
        value_dicc['linkDifficulty'] = game.getCurrentBoard().linkDifficulty()
        value_dicc['hasClues'] = game.getCurrentBoard().hasClues()
        value_dicc['aidPercentage'] = game.getCurrentBoard().aidPercentage()
        value_dicc['percentageLevel'] = game.getCurrentBoard().percentageLevel()
        value_dicc['statusTable'] = diccStatusTable
        value_dicc['linksPerPiece'] = diccLinksPerPiece
        value_dicc['originalLinksPerPiece'] = diccOriginalLinksPerPiece
        value_dicc['linksPerCell'] = diccLinksPerCell
        value_dicc['originalLinksPerCell'] = diccOriginalLinksPerCell
        value_dicc['directNeighborsPerPiece'] = diccDirectNeighborsPerPiece
        value_dicc['originalDirectNeighborsPerPiece'] = diccOriginalDirectNeighborsPerPiece
        value_dicc['piecesPerRow'] = diccPiecesPerRow
        value_dicc['piecesPerColumn'] = diccPiecesPerColumn
        value_dicc['settedLinks'] = lsSettedLinks
        value_dicc['protectedLinks'] = lsProtectedLinks
        
        final_dicc['table'] = value_dicc
    
        value_dicc = dict()
        
        value_dicc['maxNumRowsPerTable'] = game.maxNumRowsPerTable()
        value_dicc['minNumRowsPerTable'] = game.minNumRowsPerTable()
        value_dicc['maxNumColumnsPerTable'] = game.maxNumColumnsPerTable()
        value_dicc['minNumColumnsPerTable'] = game.minNumColumnsPerTable()
        value_dicc['difficultyLevels'] = game.difficultyLevels()
        value_dicc['difficultyLevel'] = game.difficultyLevel()
        value_dicc['table'] = "table"
        value_dicc['chrono'] = chronometer.getCounter()
        
        value_dicc['chronoStatus'] = chronometer.getStatus()
        
        value_dicc['numHelps'] = game.numHelps()
        value_dicc['timeDuration'] = game.timeDuration()
        
        if(store.get('currentSlot')['value']==0):
            game.computeScore2(numHelps=game.numHelps(), timeDuration=chronometer.getCounter())
            value_dicc['score'] = game.score()
        else:
            savedGamePassed = store.get('saveGame'+str(store.get('currentSlot')['value']))['toBuild']['shirokuroGame']['gamePassed']
            savedScore = store.get('saveGame'+str(store.get('currentSlot')['value']))['toBuild']['shirokuroGame']['score']
            if(savedGamePassed and not(savedScore == float('-inf'))):
                value_dicc['score'] = savedScore
            else:
                game.computeScore2(numHelps=game.numHelps(), timeDuration=chronometer.getCounter())
                value_dicc['score'] = game.score()
        
        value_dicc['originalSolution'] = str(game.originalSolution())
        value_dicc['allSolutions'] = str(game.allSolutions())
    
        value_dicc['calledResolutor'] = game.calledResolutor()
        value_dicc['currentState'] = game.currentState()

        value_dicc['savedState'] = str(game.savedState())
        value_dicc['path'] = str(game.path())
        
        value_dicc['gamePassed'] = game.isGamePassed()
        
        final_dicc['shirokuroGame'] = value_dicc
        
        if(slot=="currentSlot" or slot==None):
            if(store.get('currentSlot')['value']==0 and store.get('lastSlot')['value']==0):
                store.put('saveGame'+str(store.get('currentSlot')['value']+1), toBuild=final_dicc)
                store.put('lastSlot', value=store.get('lastSlot')['value']+1)
                store.put('currentSlot', value=store.get('currentSlot')['value']+1)
            elif(store.get('currentSlot')['value']==0 and store.get('lastSlot')['value']!=0):
                store.put('saveGame'+str(store.get('lastSlot')['value']+1), toBuild=final_dicc)
                store.put('lastSlot', value=store.get('lastSlot')['value']+1)
                store.put('currentSlot', value=store.get('lastSlot')['value'])
            else:
                store.put('saveGame'+str(store.get('currentSlot')['value']), toBuild=final_dicc)
        elif(slot=="newSlot"):
            if(store.get('currentSlot')['value']==0 and store.get('lastSlot')['value']==0):
                store.put('saveGame'+str(store.get('lastSlot')['value']+1), toBuild=final_dicc)
                store.put('lastSlot', value=store.get('lastSlot')['value']+1)
                store.put('currentSlot', value=store.get('currentSlot')['value']+1)
            else:
                store.put('saveGame'+str(store.get('lastSlot')['value']+1), toBuild=final_dicc)
                store.put('lastSlot', value=store.get('lastSlot')['value']+1)

class loader(object):
    
    def __init__(self):
        pass
    
    def loadSaveGame(self, input_nameSaveGame):
        
        nameSaveGame = input_nameSaveGame

        allInfo = store.get(nameSaveGame)['toBuild']
        allInfoLinks = allInfo['allLinks']
        allInfoPieces = allInfo['allPieces']
        
        objectPieceDict = dict()
        objectLinkDict = dict()
        for nameLink, diccInfoLink in allInfoLinks.items():
            gL = self.buildLink(nameLink, diccInfoLink, allInfoPieces, objectPieceDict)
            objectLinkDict[nameLink] = gL

        param_numRows = allInfo['table']['numRows']
        param_numColumns = allInfo['table']['numColumns']
        param_hasUniqueSolution = allInfo['table']['hasUniqueSolution']
        param_linkDifficulty = allInfo['table']['linkDifficulty']
        param_hasClues = allInfo['table']['hasClues']
        param_aidPercentage = allInfo['table']['aidPercentage']
        param_percentageLevel = allInfo['table']['percentageLevel']
        
        diccStatusTable = allInfo['table']['statusTable']
        param_statusTable = self.buildStatusTable(diccStatusTable, objectLinkDict, objectPieceDict)
        
        diccLinksPerPiece = allInfo['table']['linksPerPiece']
        param_linksPerPiece = self.buildLinksPerPiece(diccLinksPerPiece, objectLinkDict, objectPieceDict)
        
        diccOriginalLinksPerPiece = allInfo['table']['originalLinksPerPiece']
        param_originalLinksPerPiece = self.buildOriginalLinksPerPiece(diccOriginalLinksPerPiece, objectLinkDict, objectPieceDict)
        
        diccLinksPerCell = allInfo['table']['linksPerCell']
        param_linksPerCell = self.buildLinksPerCell(param_numRows, param_numColumns, diccLinksPerCell, objectLinkDict)
        
        diccOriginalLinksPerCell = allInfo['table']['originalLinksPerCell']
        param_originalLinksPerCell = self.buildOriginalLinksPerCell(param_numRows, param_numColumns, diccOriginalLinksPerCell, objectLinkDict)
        
        diccDirectNeighborsPerPiece = allInfo['table']['directNeighborsPerPiece']
        param_directNeighborsPerPiece = self.buildDirectNeighborsPerPiece(diccDirectNeighborsPerPiece, objectPieceDict)
        
        diccOriginalDirectNeighborsPerPiece = allInfo['table']['originalDirectNeighborsPerPiece']
        param_originalDirectNeighborsPerPiece = self.buildOriginalDirectNeighborsPerPiece(diccOriginalDirectNeighborsPerPiece, objectPieceDict)
        
        diccPiecesPerRow = allInfo['table']['piecesPerRow']
        param_piecesPerRow = self.buildPiecesPerRow(diccPiecesPerRow, objectPieceDict)
        
        diccPiecesPerColumn = allInfo['table']['piecesPerColumn']
        param_piecesPerColumn = self.buildPiecesPerColumn(diccPiecesPerColumn, objectPieceDict)
        
        lsSettedLinks = allInfo['table']['settedLinks']
        param_settedLinks = self.buildSettedLinks(lsSettedLinks, objectLinkDict)
        
        lsProtectedLinks = allInfo['table']['protectedLinks']
        param_protectedLinks = self.buildProtectedLinks(lsProtectedLinks, objectLinkDict)

        tableObject = table(param_numRows, param_numColumns, param_hasUniqueSolution, param_hasClues, param_aidPercentage, param_percentageLevel, param_linkDifficulty)
        tableObject.loadState(param_numRows, param_numColumns, param_hasUniqueSolution, param_hasClues, param_aidPercentage, param_percentageLevel, param_linkDifficulty,
                              param_statusTable, param_linksPerPiece, param_originalLinksPerPiece, param_linksPerCell, param_originalLinksPerCell,
                              param_directNeighborsPerPiece, param_originalDirectNeighborsPerPiece, param_piecesPerRow, param_piecesPerColumn,
                              param_settedLinks, param_protectedLinks)
        
        maxNumRowsPerTable = int(allInfo['shirokuroGame']['maxNumRowsPerTable'])
        minNumRowsPerTable = int(allInfo['shirokuroGame']['minNumRowsPerTable'])
        maxNumColumnsPerTable = int(allInfo['shirokuroGame']['maxNumColumnsPerTable'])
        minNumColumnsPerTable = int(allInfo['shirokuroGame']['minNumColumnsPerTable'])
        
        difficultyLevels = allInfo['shirokuroGame']['difficultyLevels']
        difficultyLevels = {int(k):str(v) for k, v in difficultyLevels.items()}
        
        difficultyLevel = int(allInfo['shirokuroGame']['difficultyLevel'])

        numHelps = int(allInfo['shirokuroGame']['numHelps'])
        
        timeDuration = allInfo['shirokuroGame']['timeDuration']
        
        score = allInfo['shirokuroGame']['score']
        
        originalSolution = self.buildOriginalSolution(objectLinkDict, allInfo['shirokuroGame']['originalSolution'])
        allSolutions = self.buildAllSolutions(objectLinkDict, allInfo['shirokuroGame']['allSolutions'])
        calledResolutor = allInfo['shirokuroGame']['calledResolutor']
        currentState = int(allInfo['shirokuroGame']['currentState'])
        
        savedState = None if allInfo['shirokuroGame']['savedState'] == "None" else self.buildPath(allInfo['shirokuroGame']['savedState'], objectLinkDict)
        path = self.buildPath(allInfo['shirokuroGame']['path'], objectLinkDict)
        
        gamePassed = allInfo['shirokuroGame']['gamePassed']
        
        chrono = int(allInfo['shirokuroGame']['chrono'])
        
        chronoStatus = str(allInfo['shirokuroGame']['chronoStatus'])
        
        game.loadState(maxNumRowsPerTable, minNumRowsPerTable, maxNumColumnsPerTable, minNumColumnsPerTable, difficultyLevels, difficultyLevel, 
                       tableObject, chrono, chronoStatus, numHelps, timeDuration, score, originalSolution, allSolutions, calledResolutor, currentState, savedState, path, gamePassed)
        
        store.put('currentSlot', value=int(input_nameSaveGame.split("saveGame")[1]))

    def deleteSaveGame(self, input_nameSaveGame):
        if store.exists(input_nameSaveGame):
            store.delete(input_nameSaveGame)
        
        idx = 1
        for i in range(1, store.get('lastSlot')['value']+1):
            if(store.exists('saveGame'+str(i))):
                
                if(idx==i):
                    idx += 1
                else:
                    value_dicc = store.get('saveGame'+str(i))['toBuild']
                    store.put('saveGame'+str(idx), toBuild=value_dicc)
                    store.delete('saveGame'+str(i))
                    idx += 1
        
        store.put('lastSlot', value=(store.get('lastSlot')['value']-1))
        
        if(int(input_nameSaveGame.split("saveGame")[1]) < int(store.get('currentSlot')['value'])):
            store.put('currentSlot', value=(store.get('currentSlot')['value']-1))
    
    def getNamePiece(self, piece):
            str_posx = str(piece.posx)
            str_posy = str(piece.posy)
            str_color = "White" if piece.color is colorPiece.WHITE else "Black"
            namePiece = "piece"+"_"+str_posx+"_"+str_posy+"_"+str_color
            return namePiece
        
    def buildPiece(self, namePiece, diccInfoPiece):
        pieceDict = diccInfoPiece
        gP = gamePiece(posx=pieceDict['posx'], posy=pieceDict['posy'], color=colorPiece.WHITE if pieceDict['color']=='White' else colorPiece.BLACK)
        return gP
        
    def buildLink(self, nameLink, diccInfoLink, allInfoPieces, objectPieceDict=None):

        nameWhitePiece = diccInfoLink['white']
        if(nameWhitePiece in list(objectPieceDict.keys())):
            white = objectPieceDict[nameWhitePiece]
            diccInfoWhitePiece = allInfoPieces[nameWhitePiece]
        else:
            diccInfoWhitePiece = allInfoPieces[nameWhitePiece]
            white = self.buildPiece(nameWhitePiece, diccInfoWhitePiece)
            objectPieceDict[nameWhitePiece] = white
        
        nameBlackPiece = diccInfoLink['black']
        if(nameBlackPiece in list(objectPieceDict.keys())):
            black = objectPieceDict[nameBlackPiece]
            diccInfoBlackPiece = allInfoPieces[nameBlackPiece]
        else:
            diccInfoBlackPiece = allInfoPieces[nameBlackPiece]
            black = self.buildPiece(nameBlackPiece, diccInfoBlackPiece)
            objectPieceDict[nameBlackPiece] = black
        
        gL = link(white, black)
        
        if(diccInfoWhitePiece['link'] is None):
            pass
        else:
            if(isinstance(diccInfoWhitePiece['link'], str)):
                if(diccInfoWhitePiece['link'] == gL.str):
                    white.setLink(gL)
            else:
                raise Exception("Bug")
        
        if(diccInfoBlackPiece['link'] is None):
            pass
        else:
            if(isinstance(diccInfoBlackPiece['link'], str)):
                if(diccInfoBlackPiece['link'] == gL.str):
                    black.setLink(gL)
            else:
                raise Exception("Bug")
        
        return gL
        
    def buildStatusTable(self, diccStatusTable, input_objectLinkDict, input_objectPieceDict):
        res_dict = dict()
        for key, value in diccStatusTable.items():
            newKey = key[1:-1]
            ls = newKey.split(", ")
            newLs = list()
            for elem in ls:
                newLs.append(int(elem))
            newKey = (newLs[0], newLs[1])
            if(value == 'None'):
                res_dict[newKey] = None
            else:
                try:
                    piece = input_objectPieceDict[value]
                    res_dict[newKey] = piece
                except:
                    try:
                        gameLink = input_objectLinkDict[value]
                        res_dict[newKey] = gameLink
                    except:
                        raise Exception("Bug")
        return res_dict
    
    def buildOriginalSolution(self, objectLinkDict, solution=None):
        if(solution==None):
            raise Exception("Corregir buildOriginalSolution method")
        else:
            strOriginalSolution = solution
        strOriginalSolution = strOriginalSolution[1:-1]
        strOriginalSolution = strOriginalSolution.replace("], [", "]  [")
        ls = strOriginalSolution.split("  ")
        linkDict = dict()
        for elem in ls:
            linkDict[elem] = objectLinkDict[elem]
        originalSolution = list(linkDict.values())
        return originalSolution
    
    def buildAllSolutions(self, objectLinkDict, allSolutions):
        if(allSolutions=='None'):
            return None
        else:
            strAllSolutions = allSolutions
            strAllSolutions = strAllSolutions[1:-1]
            strAllSolutions = strAllSolutions.replace("]], [[", "]]  [[")
            ls = strAllSolutions.split("  ")
            res_ls = list()
            for solution in ls:
                res_ls.append(self.buildOriginalSolution(objectLinkDict, solution))
            return res_ls
    
    def buildLinksPerPiece(self, diccLinksPerPiece, input_objectLinkDict, input_objectPieceDict):
        jsonLinksPerPiece = diccLinksPerPiece
        res_dict = dict()
        for namePiece, ls in jsonLinksPerPiece.items():
            key = input_objectPieceDict[namePiece]
            value_ls = list()
            for dicc in ls:
                newDicc = dict()
                for _, v in dicc.items():
                    gameLink = input_objectLinkDict[v]
                    oppositePiece = gameLink.getOpposite(key)
                    newDicc[oppositePiece] = gameLink
                value_ls.append(newDicc)    
            res_dict[key] = value_ls
        return res_dict
        
    def buildOriginalLinksPerPiece(self, diccOriginalLinksPerPiece, input_objectLinkDict, input_objectPieceDict):
        jsonLinksPerPiece = diccOriginalLinksPerPiece
        res_dict = dict()
        for namePiece, ls in jsonLinksPerPiece.items():
            key = input_objectPieceDict[namePiece]
            value_ls = list()
            for dicc in ls:
                newDicc = dict()
                for k, v in dicc.items():
                    oppositePiece = input_objectPieceDict[k]
                    gameLink = input_objectLinkDict[v]
                    newDicc[oppositePiece] = gameLink
                value_ls.append(newDicc)    
            res_dict[key] = value_ls
        return res_dict
    
    def buildLinksPerCell(self, numRows, numColumns, diccLinksPerCell, input_objectLinkDict):
        jsonLinksPerCell = diccLinksPerCell
        res_dict = dict()
        for i in range(numRows):
            for j in range(numColumns):
                key = (i, j)
                value_ls = list()
                v = jsonLinksPerCell[str(key)]
                for elem in v:
                    if(elem is None):
                        value_ls.append(None)
                    elif(isinstance(elem, str)):
                        gameLink = input_objectLinkDict[elem]
                        value_ls.append(gameLink)
                    elif(isinstance(elem, list)):
                        newLs = list()
                        for strGameLink in elem:
                            gameLink = input_objectLinkDict[strGameLink]
                            newLs.append(gameLink)
                        value_ls.append(newLs)
                res_dict[key] = value_ls
        return res_dict
                
    def buildOriginalLinksPerCell(self, numRows, numColumns, diccOriginalLinksPerCell, input_objectLinkDict):
        jsonLinksPerCell = diccOriginalLinksPerCell
        res_dict = dict()
        for i in range(numRows):
            for j in range(numColumns):
                key = (i, j)
                value_ls = list()
                v = jsonLinksPerCell[str(key)]
                for elem in v:
                    if(elem is None):
                        value_ls.append(None)
                    elif(isinstance(elem, str)):
                        gameLink = input_objectLinkDict[elem]
                        value_ls.append(gameLink)
                    elif(isinstance(elem, list)):
                        newLs = list()
                        for strGameLink in elem:
                            gameLink = input_objectLinkDict[strGameLink]
                            newLs.append(gameLink)
                        value_ls.append(newLs)
                res_dict[key] = value_ls
        return res_dict
    
    def buildDirectNeighborsPerPiece(self, diccDirectNeighborsPerPiece, input_objectPieceDict):
        jsonDirectNeighborsPerPiece = diccDirectNeighborsPerPiece
        res_dict = dict()
        for namePiece, neighborsLs in jsonDirectNeighborsPerPiece.items():
            key = input_objectPieceDict[namePiece]
            value_ls = list()
            for neighborName in neighborsLs:
                neighborPiece = input_objectPieceDict[neighborName]
                value_ls.append(neighborPiece)
            res_dict[key] = value_ls
        return res_dict
            
    def buildOriginalDirectNeighborsPerPiece(self, diccOriginalDirectNeighborsPerPiece, input_objectPieceDict):
        jsonOriginalDirectNeighborsPerPiece = diccOriginalDirectNeighborsPerPiece
        res_dict = dict()
        for namePiece, neighborsLs in jsonOriginalDirectNeighborsPerPiece.items():
            key = input_objectPieceDict[namePiece]
            value_ls = list()
            for neighborName in neighborsLs:
                neighborPiece = input_objectPieceDict[neighborName]
                value_ls.append(neighborPiece)
            res_dict[key] = value_ls
        return res_dict
    
    def buildPiecesPerRow(self, diccPiecesPerRow, input_objectPieceDict):
        jsonPiecesPerRow = diccPiecesPerRow
        res_dict = dict()
        for row, ls in jsonPiecesPerRow.items():
            value_ls = list()
            for namePiece in ls:
                piece = input_objectPieceDict[namePiece]
                value_ls.append(piece)
            res_dict[int(row)] = value_ls
        return res_dict
    
    def buildPiecesPerColumn(self, diccPiecesPerColumn, input_objectPieceDict):
        jsonPiecesPerColumn = diccPiecesPerColumn
        res_dict = dict()
        for column, ls in jsonPiecesPerColumn.items():
            value_ls = list()
            for namePiece in ls:
                piece = input_objectPieceDict[namePiece]
                value_ls.append(piece)
            res_dict[int(column)] = value_ls
        return res_dict
    
    def buildSettedLinks(self, lsSettedLinks, input_objectLinkDict):
        jsonSettedLinks = lsSettedLinks
        res_ls = list()
        for strGameLink in jsonSettedLinks:
            gameLink = input_objectLinkDict[strGameLink]
            res_ls.append(gameLink)
        return res_ls
    
    def buildProtectedLinks(self, lsProtectedLinks, input_objectLinkDict):
        jsonProtectedLinks = lsProtectedLinks
        res_ls = list()
        for strGameLink in jsonProtectedLinks:
            gameLink = input_objectLinkDict[strGameLink]
            res_ls.append(gameLink)
        return res_ls
    
    def buildPath(self, strPath, input_objectLinkDict):
        res_ls = list()
        states = strPath[1:-1]
        states = states.replace(", [", "  [")
        ls = states.split("  ")
        for elem in ls:
            if(elem == "None"):
                res_ls.append(None)
            else:
                nameLink = elem
                res_ls.append(input_objectLinkDict[nameLink])
        return res_ls

class mainMenu(GridLayout):
    def __init__(self, **kwargs):
        super(mainMenu, self).__init__(**kwargs)
        
        self.cols = 1
        self.rows = 2
        
        """ Intro """
        self.intro = GridLayout()
        self.intro.cols = 1
        self.intro.rows = 3
        
        self.label1 = Label(text="Shirokuro v1.0, created by F. J. Belmonte Pintre", size_hint_y=0.2)
        self.label1.halign = 'center'
        self.label1.valign = 'middle'
        self.label1.bind(size=self.label1.setter('text_size'))   
        
        self.intro.add_widget(self.label1)
        """
        self.label1 = Label(text="Shirokuro v1.0, creado por F.J. Belmonte", size_hint_y=0.2, font_size=20)
        self.label1.halign = 'center'
        self.label1.valign = 'middle'
        self.label1.bind(size=self.label1.setter('text_size'))   
        
        self.intro.add_widget(self.label1)
        """
        
        """ Imagenes """        
        self.imagenes = GridLayout(size_hint_y=0.6)
        self.imagenes.cols = 2
        self.imagenes.rows = 1
        
        self.imagenes.add_widget(Image(source='shirokuroWelcome1.png'))
        self.imagenes.add_widget(Image(source='shirokuroWelcome2.png'))
        
        self.intro.add_widget(self.imagenes)
        
        self.label2 = Label(text="Connect the white pieces to the black ones", size_hint_y=0.2)
        self.label2.halign = 'center'
        self.label2.valign = 'middle'
        self.label2.bind(size=self.label2.setter('text_size'))   
        
        self.intro.add_widget(self.label2)
        """
        self.label2 = Label(text="Conecte las piezas blancas con las negras", size_hint_y=0.2, font_size=20)
        self.label2.halign = 'center'
        self.label2.valign = 'middle'
        self.label2.bind(size=self.label2.setter('text_size'))   
        
        self.intro.add_widget(self.label2)
        """     
        
        self.add_widget(self.intro)
        
        """ Botones """
        self.buttons = GridLayout(size_hint_y = 0.5)
        self.buttons.cols = 1
        self.buttons.rows = 6
        
        self.submit1 = Button(text="New Game")
        self.submit1.halign = 'center'
        self.submit1.valign = 'middle'
        self.submit1.bind(size=self.submit1.setter('text_size'))
        self.submit1.bind(on_press=self.button_defineNewGame)
        """
        self.submit1 = Button(text="Nueva partida", font_size=20)
        self.submit1.halign = 'center'
        self.submit1.valign = 'middle'
        self.submit1.bind(size=self.submit1.setter('text_size'))
        self.submit1.bind(on_press=self.button_defineNewGame)
        """
        
        self.submit2 = Button(text="Load Game")
        self.submit2.halign = 'center'
        self.submit2.valign = 'middle'
        self.submit2.bind(size=self.submit2.setter('text_size'))
        self.submit2.bind(on_press=self.button_loadGame)
        """
        self.submit2 = Button(text="Cargar partida", font_size=20)
        self.submit2.halign = 'center'
        self.submit2.valign = 'middle'
        self.submit2.bind(size=self.submit2.setter('text_size'))
        self.submit2.bind(on_press=self.button_loadGame)
        """
        self.submit3 = Button(text="Wipe BBDD")
        self.submit3.halign = 'center'
        self.submit3.valign = 'middle'
        self.submit3.bind(size=self.submit3.setter('text_size'))
        self.submit3.bind(on_press=self.button_dataWipe)
        """
        self.submit3 = Button(text="Borrar BBDD", font_size=20)
        self.submit3.halign = 'center'
        self.submit3.valign = 'middle'
        self.submit3.bind(size=self.submit3.setter('text_size'))
        self.submit3.bind(on_press=self.button_dataWipe)
        """
        self.submit4 = Button(text="Instructions")
        self.submit4.halign = 'center'
        self.submit4.valign = 'middle'
        self.submit4.bind(size=self.submit4.setter('text_size'))
        self.submit4.bind(on_press=self.button_getInstructions)
        """
        self.submit4 = Button(text="Instrucciones", font_size=20)
        self.submit4.halign = 'center'
        self.submit4.valign = 'middle'
        self.submit4.bind(size=self.submit4.setter('text_size'))
        self.submit4.bind(on_press=self.button_getInstructions)
        """
        self.submit5 = Button(text="Ranking")
        self.submit5.halign = 'center'
        self.submit5.valign = 'middle'
        self.submit5.bind(size=self.submit5.setter('text_size'))
        self.submit5.bind(on_press=self.button_ranking)
        """
        self.submit5 = Button(text="Ranking", font_size=20)
        self.submit5.halign = 'center'
        self.submit5.valign = 'middle'
        self.submit5.bind(size=self.submit5.setter('text_size'))
        self.submit5.bind(on_press=self.button_ranking)
        """
        self.submit6 = Button(text="Exit")
        self.submit6.halign = 'center'
        self.submit6.valign = 'middle'
        self.submit6.bind(size=self.submit6.setter('text_size'))
        self.submit6.bind(on_press=self.button_leaveGame)
        """
        self.submit6 = Button(text="Salir", font_size=20)
        self.submit6.halign = 'center'
        self.submit6.valign = 'middle'
        self.submit6.bind(size=self.submit6.setter('text_size'))
        self.submit6.bind(on_press=self.button_leaveGame)
        """
        self.buttons.add_widget(self.submit1)
        self.buttons.add_widget(self.submit2)
        self.buttons.add_widget(self.submit3)
        self.buttons.add_widget(self.submit4)
        self.buttons.add_widget(self.submit5)
        self.buttons.add_widget(self.submit6)

        self.add_widget(self.buttons)

    def button_defineNewGame(self, instance):
        shirokuroApp.root.get_screen('defineMetricas').children[0].updateFromScreen(input_FromScreen="menuPrincipal")
        shirokuroApp.screen_manager.current = "defineMetricas"
        shirokuroApp.screen_manager.transition.direction = "left"
    
    def button_loadGame(self, instance):
        if(not(shirokuroApp.screen_manager.has_screen(name="menuCargar"))):
            screen = Screen(name="menuCargar")
            screen.add_widget(loadMenu())
            shirokuroApp.screen_manager.add_widget(screen)
        else:
            screen = shirokuroApp.root.get_screen('menuCargar')
            loadMenuObj = screen.children[0]
            screen.remove_widget(loadMenuObj)
            screen.add_widget(loadMenu())
        shirokuroApp.root.get_screen('menuCargar').children[0].updateFromScreen(input_FromScreen="menuPrincipal")
        shirokuroApp.screen_manager.current = "menuCargar"
        shirokuroApp.screen_manager.transition.direction = "left"
    
    def button_dataWipe(self, instance):
        
        box = BoxLayout(orientation='vertical')
        buttons = BoxLayout()
        
        button_dataWipe = Button(text="Wipe data base")
        button_dataWipe.halign = 'center'
        button_dataWipe.valign = 'middle'
        button_dataWipe.bind(size=button_dataWipe.setter('text_size'))
        button_dataWipe.bind(on_press=self.commit_dataWipe)

        buttons.add_widget(button_dataWipe)
        
        box.add_widget(buttons)

        button_popDataWipeWindow = Button(text="Back")
        button_popDataWipeWindow.halign = 'center'
        button_popDataWipeWindow.valign = 'middle'
        button_popDataWipeWindow.bind(size=button_popDataWipeWindow.setter('text_size'))
        button_popDataWipeWindow.bind(on_press=self.popDataWipeWindow)
        box.add_widget(button_popDataWipeWindow)
        
        self.pop = Popup(title="Wipe BBDD", content=box)
        self.pop.open()
 
    def commit_dataWipe(self, instance):
        for i in range(1, store.get('lastSlot')['value']+1):
            if(store.exists('saveGame'+str(i))):
                store.delete('saveGame'+str(i))
                store.put('lastSlot', value=(store.get('lastSlot')['value']-1))
        store.put('currentSlot', value=0)
        self.pop.dismiss()
    
    def popDataWipeWindow(self, instance):
        self.pop.dismiss()
    
    def button_getInstructions(self, instance):
        shirokuroApp.root.get_screen('instrucciones').children[0].updateFromScreen(input_FromScreen="menuPrincipal")
        shirokuroApp.screen_manager.current = "instrucciones"
        shirokuroApp.screen_manager.transition.direction = "left"
        
    def button_ranking(self, instance):
        if(not(shirokuroApp.screen_manager.has_screen(name="clasificacion"))):
            screen = Screen(name="clasificacion")
            screen.add_widget(Ranking())
            shirokuroApp.screen_manager.add_widget(screen)
        else:
            screen = shirokuroApp.root.get_screen('clasificacion')
            rankingObj = screen.children[0]
            screen.remove_widget(rankingObj)
            screen.add_widget(Ranking())
        shirokuroApp.screen_manager.current = "clasificacion"
        shirokuroApp.screen_manager.transition.direction = "left"
    
    def button_leaveGame(self, instance):
        shirokuroApp.stop()

class instructionsDisplay(GridLayout):
    fromScreen = ObjectProperty("")
    
    def __init__(self, **kwargs):
        super(instructionsDisplay, self).__init__(**kwargs)
        
        self.cols = 1
        self.rows = 2
        
        """ Intro """
        self.intro = GridLayout()
        self.intro.cols = 2
        self.intro.rows = 1
        
        """ Imagenes"""
        self.imagenes = GridLayout()
        self.imagenes.cols = 1
        self.imagenes.rows = 2
        
        self.imagenes.add_widget(Image(source='shirokuroNoResuelto.png'))
        self.imagenes.add_widget(Image(source='shirokuroResuelto.png'))
        
        self.intro.add_widget(self.imagenes)
        
        """ Instrucciones """
        self.instrucciones = GridLayout()
        self.instrucciones.cols = 1
        self.instrucciones.rows = 6
        
        self.label_instructions_title = Label(text="RULES")
        """
        self.label_instructions_title = Label(text="RULES", font_size=40)
        """
        self.label_instructions_title.halign = 'left'
        self.label_instructions_title.valign = 'middle'
        self.label_instructions_title.bind(size=self.label_instructions_title.setter('text_size'))    
        
        self.instrucciones.add_widget(self.label_instructions_title)
        
        self.label1 = Label(text="1.    Connect each black circle with a white circle by a straight horizontal or vertical line.")
        """
        self.label1 = Label(text="1.    Cada ficha se ha de enlazar con otra del color opuesto a la suya.", font_size=20)
        """
        self.label1.halign = 'left'
        self.label1.valign = 'middle'
        self.label1.bind(size=self.label1.setter('text_size'))   
        
        self.instrucciones.add_widget(self.label1)
        
        self.label2 = Label(text="2.    Each circle must be part of a line.")
        """
        self.label2 = Label(text="2.    No pueden quedar fichas sin enlazar.", font_size=20)
        """
        self.label2.halign = 'left'
        self.label2.valign = 'middle'
        self.label2.bind(size=self.label2.setter('text_size'))   
        
        self.instrucciones.add_widget(self.label2)
        
        self.label3 = Label(text="3.    Lines do not pass through other circles.")
        """
        self.label3 = Label(text="3.    Los enlaces no pueden atravesar piezas.", font_size=20)
        """
        self.label3.halign = 'left'
        self.label3.valign = 'middle'
        self.label3.bind(size=self.label3.setter('text_size'))  
        
        self.instrucciones.add_widget(self.label3)
        
        self.label4 = Label(text="4.    Lines do not cross other lines.")
        """
        self.label4 = Label(text="4.    Los enlaces no pueden cruzarse.", font_size=20)
        """
        self.label4.halign = 'left'
        self.label4.valign = 'middle'
        self.label4.bind(size=self.label4.setter('text_size')) 
        
        self.instrucciones.add_widget(self.label4)
        
        self.label5 = Label(text="5.    Not necessarily each cell is visited by a line.")
        """
        self.label5 = Label(text="5.    No necesariamente cada celda es visitada por un enlace.", font_size=20)
        """
        self.label5.halign = 'left'
        self.label5.valign = 'middle'
        self.label5.bind(size=self.label5.setter('text_size')) 
        
        self.instrucciones.add_widget(self.label5)

        self.intro.add_widget(self.instrucciones)
        
        self.add_widget(self.intro)
        
        """ Botones"""
        self.buttons = GridLayout(size_hint_y = 0.1)
        
        self.buttons.cols = 1
        self.buttons.rows = 1
        
        self.submit = Button(text="Back")
        """
        self.submit = Button(text="Atras", font_size=20)
        """
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size')) 
        self.submit.bind(on_press=self.goBack)
        
        self.buttons.add_widget(self.submit)
        
        self.add_widget(self.buttons)
        
    def updateFromScreen(self, input_FromScreen):
        self.fromScreen = input_FromScreen

    def getFromScreen(self):
        return self.fromScreen
    
    def goBack(self, instance):
        if(self.getFromScreen() == "menuPrincipal"):
            store.put('currentSlot', value=0)
        shirokuroApp.screen_manager.current = self.getFromScreen()
        shirokuroApp.screen_manager.transition.direction = "right"
    
class defineGameMenu(GridLayout):
    fromScreen = ObjectProperty("")
    numRows = StringProperty('5')
    numColumns = StringProperty('5')
    hasUniqueSolution = StringProperty('0')
    difficulty = StringProperty('1')
    hasClues = StringProperty('0')
    aidPercentage = StringProperty('0.0')
    
    def __init__(self, **kwargs):
        super(defineGameMenu, self).__init__(**kwargs)
        self.cols = 1
        
        """ Numero de filas """
        self.label1 = Label(text="Number of rows["+str(game.minNumRowsPerTable())+"-"+str(game.maxNumRowsPerTable())+"]:")
        self.label1.halign = 'center'
        self.label1.valign = 'middle'
        self.label1.bind(size=self.label1.setter('text_size'))   
        self.add_widget(self.label1)
        self.field_numRows = TextInput(text=self.numRows, multiline=False)
        self.add_widget(self.field_numRows)
        """
        self.label1 = Label(text="Numero de filas["+str(game.minNumRowsPerTable())+"-"+str(game.maxNumRowsPerTable())+"]:", font_size=20)
        self.label1.halign = 'center'
        self.label1.valign = 'middle'
        self.label1.bind(size=self.label1.setter('text_size'))   
        self.add_widget(self.label1)
        
        self.field_numRows = TextInput(text=self.numRows, multiline=False)
        self.add_widget(self.field_numRows)
        """
        
        """ Numero de columnas """
        self.label2 = Label(text="Number of columns["+str(game.minNumColumnsPerTable())+"-"+str(game.maxNumColumnsPerTable())+"]:")
        self.label2.halign = 'center'
        self.label2.valign = 'middle'
        self.label2.bind(size=self.label2.setter('text_size'))  
        self.add_widget(self.label2)
        self.field_numColumns = TextInput(text=self.numColumns, multiline=False)
        self.add_widget(self.field_numColumns)
        """
        self.label2 = Label(text="Numero de columnas["+str(game.minNumColumnsPerTable())+"-"+str(game.maxNumColumnsPerTable())+"]:", font_size=20)
        self.label2.halign = 'center'
        self.label2.valign = 'middle'
        self.label2.bind(size=self.label2.setter('text_size'))   
        self.add_widget(self.label2)
        
        self.field_numColumns = TextInput(text=self.numColumns, multiline=False)
        self.add_widget(self.field_numColumns)
        """
        
        """ Solucion unica """
        self.label3 = Label(text="Unitary solution[0:No, 1:Yes]:")
        self.label3.halign = 'center'
        self.label3.valign = 'middle'
        self.label3.bind(size=self.label3.setter('text_size'))   
        self.add_widget(self.label3)
        self.field_hasUniqueSolution = TextInput(text=self.hasUniqueSolution, multiline=False)
        self.add_widget(self.field_hasUniqueSolution)
        """
        self.label3 = Label(text="Solucion unica[0:No, 1:Si]:", font_size=20)
        self.label3.halign = 'center'
        self.label3.valign = 'middle'
        self.label3.bind(size=self.label3.setter('text_size'))   
        self.add_widget(self.label3)
        
        self.field_hasUniqueSolution = TextInput(text=self.hasUniqueSolution, multiline=False)
        self.add_widget(self.field_hasUniqueSolution)
        """
        
        """ Dificultad """
        t1 = str(game.difficultyLevels())
        t= t1.replace(", 4: 'very hard'", "")
        t = t.replace("{", "[")
        t = t.replace("}", "]")
        self.label4 = Label(text="Difficulty"+t+":")
        self.label4.halign = 'center'
        self.label4.valign = 'middle'
        self.label4.bind(size=self.label4.setter('text_size')) 
        self.add_widget(self.label4)
        self.field_difficulty = TextInput(text=self.difficulty, multiline=False)
        self.add_widget(self.field_difficulty)
        """
        t = str(game.difficultyLevels())
        t = t.replace("{", "[")
        t = t.replace("}", "]")
        self.label4 = Label(text="Dificultad"+t+":", font_size=20)
        self.label4.halign = 'center'
        self.label4.valign = 'middle'
        self.label4.bind(size=self.label4.setter('text_size'))   
        self.add_widget(self.label4)
        
        self.field_difficulty = TextInput(text=self.difficulty, multiline=False)
        self.add_widget(self.field_difficulty)
        """
        self.inside = GridLayout()
        
        self.inside.cols = 2
        
        self.submit1 = Button(text="Back")
        self.submit1.halign = 'center'
        self.submit1.valign = 'middle'
        self.submit1.bind(size=self.submit1.setter('text_size')) 
        self.submit1.bind(on_press=self.goBack)
        self.inside.add_widget(self.submit1)
        
        self.submit2 = Button(text="Build")
        self.submit2.halign = 'center'
        self.submit2.valign = 'middle'
        self.submit2.bind(size=self.submit2.setter('text_size')) 
        self.submit2.bind(on_press=self.buildBoard)
        self.inside.add_widget(self.submit2)
        
        self.add_widget(self.inside)
        
    def updateFromScreen(self, input_FromScreen):
        self.fromScreen = input_FromScreen

    def getFromScreen(self):
        return self.fromScreen
    
    def goBack(self, instance):
        shirokuroApp.screen_manager.current = self.getFromScreen()
        if(self.fromScreen == "menuPrincipal"):
            store.put('currentSlot', value=0)
        shirokuroApp.screen_manager.transition.direction = "right"
        
    def buildBoard(self, instance):
        try:
            choicedNumRows = int(self.field_numRows.text)
            choicedNumColumns = int(self.field_numColumns.text)
            choicedHasUniqueSolution = int(self.field_hasUniqueSolution.text)
            choicedDifficulty = int(self.field_difficulty.text)
            
            b1 = choicedNumRows in [i for i in range(game.minNumRowsPerTable(), game.maxNumRowsPerTable()+1)]
            b2 = choicedNumColumns in [i for i in range(game.minNumColumnsPerTable(), game.maxNumColumnsPerTable()+1)]
            b3 = choicedHasUniqueSolution in [0, 1]
            
            lsDiffLevels = list(game.difficultyLevels().keys())
            lsDiffLevels.remove(4)
            b4 = choicedDifficulty in lsDiffLevels
            
            if(b1 and b2 and b3 and b4):
                
                if(self.fromScreen == "menuJugar"):
                    shirokuroApp.root.get_screen('menuJugar').children[0].removeCurrentBoard()
                
                game.defineGame2(choicedNumRows,
                                 choicedNumColumns,
                                 choicedHasUniqueSolution,
                                 choicedDifficulty,
                                 int(self.hasClues),
                                 float(self.aidPercentage))
                
                if(shirokuroApp.screen_manager.has_screen(name="tablero")):
                    screen = shirokuroApp.screen_manager.get_screen(name="tablero")
                    shirokuroApp.screen_manager.remove_widget(screen)
                
                screen = Screen(name="tablero")
                #screen.add_widget(Board(id="board"))  
                screen.add_widget(Board())      
                shirokuroApp.screen_manager.add_widget(screen)
                
                if(not(shirokuroApp.screen_manager.has_screen(name="menuJugar"))):
                    screen = Screen(name="menuJugar")
                    screen.add_widget(playMenu())
                    shirokuroApp.screen_manager.add_widget(screen)
                
                self.reset
                
                chronometer.parent = None
                chronometer.start()
                
                shirokuroApp.screen_manager.current = "tablero"
                shirokuroApp.screen_manager.transition.direction = "left"
                
            else:
                print("pass if-else")
                pass
            
        except Exception as e:
            print(e)
            pass

    def reset(self, instance):
        self.field_numRows.text = ''
        self.field_numColumns.text = ''
        self.field_hasUniqueSolution.text = ''
        self.field_difficulty.text = ''
        self.field_hasClues.text = ''
        self.field_aidPercentage.text = ''

class Chrono(Label):
    counter = StringProperty("0")
    clockObj = None
    chronoStatus = "resume"
    
    def __init__(self, **kwargs):
        super(Chrono,self).__init__(**kwargs)
        self.text = "Time: "+str(self.counter)
        
    def toCount(self, dt):
        self.counter = str(int(self.counter)+1)
        self.text = "Time: "+str(self.counter)
        
    def start(self):
        if(self.clockObj == None):
            self.clockObj = Clock.schedule_interval(self.toCount, 1)
        else:
            self.reset()
        
    def startSinceCurrentCount(self, currentCount):
        if(self.clockObj == None):
            self.clockObj = Clock.schedule_interval(self.toCount, 1)
        self.pause()
        self.counter = str(currentCount)
        self.text = "Time: "+str(self.counter)
        if(game.chronoStatus() == "resume"):
            self.resume()
    
    def pause(self):
        self.text = "Time: "+str(self.counter)
        self.clockObj.cancel()
        self.chronoStatus = "pause"
    
    def resume(self):
        self.clockObj()
        self.chronoStatus = "resume"
        
    def reset(self):
        self.pause()
        self.counter = "0"
        self.text = "Time: "+str(self.counter)
        self.resume()
        
    def uncouple(self):
        self.parent = None
        
    def getCounter(self):
        return int(self.counter)

    def getStatus(self):
        return str(self.chronoStatus)

""" Amarillo Enlace """
class YellowLayout(GridLayout):

    def __init__(self, **kwargs):
        super(YellowLayout, self).__init__(**kwargs)
        
        with self.canvas.before:
            Color(255/255.0, 255/255.0, 0/255.0, .5, mode='rgba')
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

""" Marron Tablero """
class BrownLayout(FloatLayout):

    def __init__(self, **kwargs):
        super(BrownLayout, self).__init__(**kwargs)
        
        self.cols = 1
        self.rows = 1
        
        with self.canvas.before:
            Color(139/255.0, 69/255.0, 19/255.0, .5, mode='rgba')
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class BoardRepr(GridLayout):
    
    layoutDict = dict()
    yellowLayout_Dict = dict()
    buttonPressed = None
    backgroundColor_buttonPressed = None
    neighborButtons = None
    allButtons = []

    def __init__(self, **kwargs):
        super(BoardRepr, self).__init__(**kwargs)
        
        self.allButtons = []
        
        self.cols = game.getCurrentBoard().getNumColumns()
        self.rows = game.getCurrentBoard().getNumRows()
        
        statusTableDict = game.getCurrentBoard().getStatusTable()
        newOrderStatusTableDict = dict()
        for i in reversed(range(self.rows)):
            for j in range(self.cols):
                newOrderStatusTableDict[(i, j)] = statusTableDict[(i, j)]
         
        for k, v in newOrderStatusTableDict.items():

            inside_GL = BrownLayout()
            self.add_widget(inside_GL)
            self.layoutDict[k] = inside_GL
            
        for piece in game.getCurrentBoard().getAllPieces():
            
            v = piece
            k = piece.position
            inside_GL = self.layoutDict[k]
            
            button_pos = k
            button_name="button_"+str(button_pos[0])+"_"+str(button_pos[1])
            
            if(v.color is colorPiece.WHITE):
                """ Boton blanco """
                white_rgb=[1,1,1,1]
                #button_ids_dict = {"id": button_name}
                btn = Button(ids={"id": button_name}, background_color=white_rgb, size_hint = (.5, .5), pos_hint = {'x': .25, 'y': .25})
                self.allButtons.append(btn)
                #btn = Button(background_color=white_rgb, size_hint = (.5, .5), pos_hint = {'x': .25, 'y': .25})
                btn.bind(on_press=self.choicedPiece)
                inside_GL.add_widget(btn)
                
            elif(v.color is colorPiece.BLACK):
                """ Boton negro """
                black_rgb=[0,0,0,1]
                #button_ids_dict = {"id": button_name}
                btn = Button(ids={"id": button_name}, background_color=black_rgb, size_hint = (.5, .5), pos_hint = {'x': .25, 'y': .25})
                self.allButtons.append(btn)
                #btn = Button(background_color=black_rgb, size_hint = (.5, .5), pos_hint = {'x': .25, 'y': .25})
                btn.bind(on_press=self.choicedPiece)
                inside_GL.add_widget(btn)
            
            else:
                raise Exception("Button Color Bug")
            
        for settedLink in game.getCurrentBoard().getSettedLinks():
            choicedLink = settedLink
            self.drawLink(choicedLink)

    def getYellowLayoutDict(self):
        return self.yellowLayout_Dict
    
    def resetYellowLayoutDict(self):
        self.yellowLayout_Dict = dict()
    
    def playMenuPressed(self, instance):
        if(shirokuroApp.screen_manager.has_screen(name="menuJugar")):
            shirokuroApp.screen_manager.current = "menuJugar"
            shirokuroApp.screen_manager.transition.direction = "left"
        else:
            screen = Screen(name="menuJugar")
            screen.add_widget(playMenu())        
            shirokuroApp.screen_manager.add_widget(screen)            
            shirokuroApp.screen_manager.current = "menuJugar"
            shirokuroApp.screen_manager.transition.direction = "left"
    
    def removeLink(self, choicedLink):
        self.unDrawLink(choicedLink)
        game.commitUndoMove(choicedLink)
    
    def unDrawLink(self, choicedLink):
        cell = choicedLink.white.position
        self.layoutDict[cell].remove_widget(self.yellowLayout_Dict[cell])
        cell = choicedLink.black.position
        self.layoutDict[cell].remove_widget(self.yellowLayout_Dict[cell])
        
        for cell in choicedLink.intermediateCells:
            self.layoutDict[cell].remove_widget(self.yellowLayout_Dict[cell])
    
    def drawLink(self, choicedLink):
        
        if(choicedLink.white.posy < choicedLink.black.posy):
            
            #W --- B
            yL = YellowLayout(size_hint = (0.25, 0.2), pos_hint = {'x': 0.75, 'y': 0.4})
            self.layoutDict[choicedLink.white.position].add_widget(yL)
            self.yellowLayout_Dict[choicedLink.white.position] = yL
            
            yL = YellowLayout(size_hint = (0.25, 0.2), pos_hint = {'x': 0.0, 'y': 0.4})
            self.layoutDict[choicedLink.black.position].add_widget(yL)
            self.yellowLayout_Dict[choicedLink.black.position] = yL
            
        elif(choicedLink.white.posy > choicedLink.black.posy):
            
            #B --- W
            yL = YellowLayout(size_hint = (0.25, 0.2), pos_hint = {'x': 0.75, 'y': 0.4})
            self.layoutDict[choicedLink.black.position].add_widget(yL)
            self.yellowLayout_Dict[choicedLink.black.position] = yL
            
            yL = YellowLayout(size_hint = (0.25, 0.2), pos_hint = {'x': 0.0, 'y': 0.4})
            self.layoutDict[choicedLink.white.position].add_widget(yL)
            self.yellowLayout_Dict[choicedLink.white.position] = yL
            
        elif(choicedLink.white.posx < choicedLink.black.posx):
            
            yL = YellowLayout(size_hint = (0.2, 0.25), pos_hint = {'x': 0.4, 'y': 0.75})
            self.layoutDict[choicedLink.white.position].add_widget(yL)
            self.yellowLayout_Dict[choicedLink.white.position] = yL
            
            yL = YellowLayout(size_hint = (0.2, 0.25), pos_hint = {'x': 0.4, 'y': 0.0})
            self.layoutDict[choicedLink.black.position].add_widget(yL)
            self.yellowLayout_Dict[choicedLink.black.position] = yL
            
        elif(choicedLink.white.posx > choicedLink.black.posx):
            
            yL = YellowLayout(size_hint = (0.2, 0.25), pos_hint = {'x': 0.4, 'y': 0.75})
            self.layoutDict[choicedLink.black.position].add_widget(yL)
            self.yellowLayout_Dict[choicedLink.black.position] = yL
            
            yL = YellowLayout(size_hint = (0.2, 0.25), pos_hint = {'x': 0.4, 'y': 0.0})
            self.layoutDict[choicedLink.white.position].add_widget(yL)
            self.yellowLayout_Dict[choicedLink.white.position] = yL
        """ W --- B """
        for cell in choicedLink.intermediateCells:

            if(choicedLink.directionLink() is directionLink.HORIZONTAL):
                yL = YellowLayout(size_hint = (1.0, 0.2), pos_hint = {'x': 0.0, 'y': 0.4})
                self.layoutDict[cell].add_widget(yL)
                self.yellowLayout_Dict[cell] = yL
            
            elif(choicedLink.directionLink() is directionLink.VERTICAL):
                yL = YellowLayout(size_hint = (0.2, 1.0), pos_hint = {'x': 0.4, 'y': 0.0})
                self.layoutDict[cell].add_widget(yL)
                self.yellowLayout_Dict[cell] = yL
                
            else:
                raise Exception("Bug")
    
    def choicedPiece(self, instance):
        
        def getGamePieceByNameButton(nameButton):

            row = int(nameButton.split("_")[1])
            column = int(nameButton.split("_")[2])
            obj = game.getCurrentBoard().getObjByCellPosition((row, column))
            return obj
        
        if(shirokuroApp.screen_manager.current == "tablero"):
            print(instance)
                    
            obj = getGamePieceByNameButton(nameButton=instance.ids["id"])
    
            if(obj.link is not None):
                """ Quito el enlace """
                self.removeLink(choicedLink=obj.link)
            else:
                
                if(self.neighborButtons is None):
                    self.neighborButtons = list()
                else:
                    """ Reestablezco los colores originales de los botones vecinos """
                    for tupla in self.neighborButtons:
                        neighbor_button = tupla[0]
                        color_button = tupla[1]
                        neighbor_button.background_color = color_button
                        
                    self.neighborButtons = list()
                
                if(self.buttonPressed is None):
                    """ Guardo la informacion previa del boton seleccionado """
                    self.backgroundColor_buttonPressed = instance.background_color
                    self.buttonPressed = instance
                    
                    """ Azul: pieza seleccionada """
                    instance.background_color = [0,0,1,1]
                    
                    """ Verde: piezas con las que se puede conectar """
                    for neighbor in list(game.getCurrentBoard().linksPerPiece()[obj][0].keys()):
                        button_name = "button_"+str(neighbor.posx)+"_"+str(neighbor.posy)
                        
                        """ Encuentro el boton con el siguiente algoritmo """
                        neighbor_widget = None
                        #for widget in self.walk():
                        for widget in self.allButtons:
                            if(widget.ids["id"] == button_name):
                                neighbor_widget = widget
                                break
                        
                        """ Guardo el boton vecino y su color original, en forma de tupla, por si tengo que restablecerlo posteriormente """
                        tupla = (neighbor_widget, neighbor_widget.background_color)
                        self.neighborButtons.append(tupla)
                        
                        green = [0,1,0,1]
                        neighbor_widget.background_color = green
                
                elif(self.buttonPressed is instance):
                    """ Has vuelto a pulsar el mismo boton que la vez anterior, invalido la antigua seleccion """
                    self.buttonPressed.background_color = self.backgroundColor_buttonPressed
                    
                    self.buttonPressed = None
                    self.backgroundColor_buttonPressed = None
                    self.neighborButtons = None
                else:
                    """ El nuevo boton pulsado es distinto del anterior, puede ser un hermano conectable o no serlo. """
                    pieceBefore = getGamePieceByNameButton(nameButton=self.buttonPressed.ids["id"])
                    if(obj in list(game.getCurrentBoard().linksPerPiece()[pieceBefore][0].keys())):
                        """ Como si es un vecino conectable, tenemos que materializar el enlace """
                        
                        self.buttonPressed.background_color = self.backgroundColor_buttonPressed
                        
                        self.buttonPressed = None
                        self.backgroundColor_buttonPressed = None
                        self.neighborButtons = None
    
                        choicedLink = game.getCurrentBoard().linksPerPiece()[pieceBefore][0][obj]
                        
                        game.commitMove(choicedLink)
                        
                        self.drawLink(choicedLink)
                    
                    else:
                        """ reestablecemos el color del original pulsado """
                        self.buttonPressed.background_color = self.backgroundColor_buttonPressed
                        
                        """ Guardo la informacion previa del boton seleccionado """
                        self.backgroundColor_buttonPressed = instance.background_color
                        self.buttonPressed = instance
                
                        """ Azul: pieza seleccionada """
                        instance.background_color = [0,0,1,1]
                        
                        """ Verde: piezas con las que se puede conectar """
                        for neighbor in list(game.getCurrentBoard().linksPerPiece()[obj][0].keys()):
                            button_name = "button_"+str(neighbor.posx)+"_"+str(neighbor.posy)
                            
                            """ Encuentro el boton con el siguiente algoritmo """
                            neighbor_widget = None
                            #for widget in self.walk():
                            for widget in self.allButtons:
                                if(widget.ids["id"] == button_name):
                                    neighbor_widget = widget
                                    break
                            
                            """ Guardo el boton vecino y su color original, en forma de tupla, por si tengo que restablecerlo posteriormente """
                            tupla = (neighbor_widget, neighbor_widget.background_color)
                            self.neighborButtons.append(tupla)
                            
                            green = [0,1,0,1]
                            neighbor_widget.background_color = green
            
            if(game.isGamePassed()):
                shirokuroApp.root.get_screen('menuJugar').children[0].removeCurrentBoard()
                chronometer.pause()
                game.computeScore2(game.numHelps(), chronometer.getCounter())
                
                """  Dado que te has pasado la partida, se hace un guardado en el currentSlot  """
                shirokuroApp.root.get_screen('menuJugar').children[0].saveInJSON()
                
                if(not(shirokuroApp.screen_manager.has_screen(name="resultados"))):
                    screen = Screen(name="resultados")
                    screen.add_widget(ResumeDisplay())
                    shirokuroApp.screen_manager.add_widget(screen)
                else:
                    screen = shirokuroApp.root.get_screen('resultados')
                    obj = screen.children[0]
                    screen.remove_widget(obj)
                    screen.add_widget(ResumeDisplay())
                
                shirokuroApp.screen_manager.current = "resultados"
                shirokuroApp.screen_manager.transition.direction = "left"

class Board(GridLayout):
    
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        
        self.cols = 1
        self.rows = 2
        
        self.add_widget(BoardRepr())
        
        self.subMenu = GridLayout(size_hint_y=.1)
        
        self.subMenu.cols = 2
        self.subMenu.rows = 1
        
        self.chronometer = chronometer
        self.subMenu.add_widget(self.chronometer)
        
        self.submit = Button(text='Options')
        self.submit.bind(on_press=self.playMenuPressed)
        self.subMenu.add_widget(self.submit)
        
        self.add_widget(self.subMenu)
    
    def playMenuPressed(self, instance):
        if(shirokuroApp.screen_manager.has_screen(name="menuJugar")):
            shirokuroApp.screen_manager.current = "menuJugar"
            shirokuroApp.screen_manager.transition.direction = "left"
        else:
            screen = Screen(name="menuJugar")
            screen.add_widget(playMenu())        
            shirokuroApp.screen_manager.add_widget(screen)            
            shirokuroApp.screen_manager.current = "menuJugar"
            shirokuroApp.screen_manager.transition.direction = "left"

""" Pantalla con los resultados. """
class ResumeDisplay(GridLayout):
    
    def __init__(self, **kwargs):
        super(ResumeDisplay, self).__init__()

        self.cols = 1
        self.rows = 2
        
        self.add_widget(BoardRepr())
        self.subMenu = GridLayout(size_hint_y=.3)
        
        self.subMenu.cols = 1
        self.subMenu.rows = 2

        self.results = GridLayout()
        self.results.cols = 3
        self.results.rows = 2
        
        indexSaveGame = store.get("currentSlot")['value']
        nameSaveGame = 'saveGame'+str(indexSaveGame)
        
        shirokuroGameInfo = store.get(nameSaveGame)['toBuild']['shirokuroGame']
        tableInfo = store.get(nameSaveGame)['toBuild']['table']
        
        self.label1 = Label(text="Rows: "+str(tableInfo['numRows']))
        self.label1.halign = 'center'
        self.label1.valign = 'middle'
        self.label1.bind(size=self.label1.setter('text_size'))   
        self.results.add_widget(self.label1)
        #self.label1 = Label(text="    Filas: "+str(tableInfo['numRows']), font_size=20)
        
        
        self.label2 = Label(text="Columns: "+str(tableInfo['numColumns']))
        self.label2.halign = 'center'
        self.label2.valign = 'middle'
        self.label2.bind(size=self.label2.setter('text_size'))   
        self.results.add_widget(self.label2)
        #self.label2 = Label(text="    Columnas: "+str(tableInfo['numColumns']), font_size=20)
        
        
        self.label3 = Label(text="Difficulty: "+str(shirokuroGameInfo['difficultyLevel']))
        self.label3.halign = 'center'
        self.label3.valign = 'middle'
        self.label3.bind(size=self.label3.setter('text_size'))
        self.results.add_widget(self.label3)
        #self.label3 = Label(text="    Dificultad: "+str(shirokuroGameInfo['difficultyLevel']), font_size=20)
        
        
        self.label4 = Label(text="Helps: "+str(shirokuroGameInfo['numHelps']))
        self.label4.halign = 'center'
        self.label4.valign = 'middle'
        self.label4.bind(size=self.label4.setter('text_size'))  
        self.results.add_widget(self.label4)
        #self.label4 = Label(text="    Ayudas: "+str(shirokuroGameInfo['numHelps']), font_size=20)
         
        
        self.label5 = Label(text="Time: "+str(shirokuroGameInfo['chrono']))
        self.label5.halign = 'center'
        self.label5.valign = 'middle'
        self.label5.bind(size=self.label5.setter('text_size')) 
        self.results.add_widget(self.label5)
        #self.label5 = Label(text="    Tiempo: "+str(shirokuroGameInfo['chrono']), font_size=20)
          
        
        self.label6 = Label(text="Score: "+str(shirokuroGameInfo['score']))
        self.label6.halign = 'center'
        self.label6.valign = 'middle'
        self.label6.bind(size=self.label6.setter('text_size'))   
        self.results.add_widget(self.label6)
        #self.label6 = Label(text="    Score: "+str(shirokuroGameInfo['score']), font_size=20)
        
        
        
        self.subMenu.add_widget(self.results)
        
        self.submit = Button(text="Next", size_hint_y=.33)
        """
        self.submit = Button(text="Continuar", font_size=20, size_hint_y=.33)
        """
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_continue)
        self.subMenu.add_widget(self.submit)

        self.add_widget(self.subMenu)
        
    def button_continue(self, instance):
        store.put('currentSlot', value=0)
        shirokuroApp.screen_manager.current = "menuPrincipal"
        shirokuroApp.screen_manager.transition.direction = "left"

class solution(GridLayout):
    def __init__(self, **kwargs):
        super(solution, self).__init__(**kwargs)
        
        self.cols = 1
        self.rows = 1
        
        self.board = BoardRepr()
        self.add_widget(self.board)

class solutionDisplay(GridLayout):
    def __init__(self, **kwargs):
        super(solutionDisplay, self).__init__(**kwargs)
        
        self.cols = 1
        self.rows = 2

        self.add_widget(solution())
        
        self.submit = Button(text="Menu", size_hint_y=.1)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_goMenu)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Menu", font_size=20, size_hint_y=.1)
        self.submit.bind(on_press=self.button_goMenu)
        self.add_widget(self.submit)
        """
        
    def button_goMenu(self, instance):
        store.put('currentSlot', value=0)
        shirokuroApp.screen_manager.current = "menuPrincipal"
        shirokuroApp.screen_manager.transition.direction = "left"

class guideSolution(GridLayout):
    def __init__(self, **kwargs):
        super(guideSolution, self).__init__(**kwargs)
        
        self.cols = 1
        self.rows = 2
        
        self.board = BoardRepr()
        self.add_widget(self.board)
        
        self.subMenu = GridLayout(size_hint_y=0.1)
        self.subMenu.cols = 2
        self.subMenu.rows = 1
        
        self.submit = Button(text="Previous")
        """
        self.submit = Button(text="Anterior", font_size=20)
        """
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_goPreviousState)
        self.subMenu.add_widget(self.submit)
        
        self.submit = Button(text="Next")
        """
        self.submit = Button(text="Siguiente", font_size=20)
        """
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_goNextState)
        self.subMenu.add_widget(self.submit)
        
        self.add_widget(self.subMenu)
        
    def button_goNextState(self, instance):

        for settedLink in game.getCurrentBoard().getSettedLinks():
            choicedLink = settedLink
            self.board.unDrawLink(choicedLink)
                
        game.getNextState()

        for obj in game.getCurrentBoard().getSettedLinks():
            self.board.drawLink(obj)
        
        shirokuroApp.screen_manager.transition.direction = "left"
        
    def button_goPreviousState(self, instance):
        
        for settedLink in game.getCurrentBoard().getSettedLinks():
            choicedLink = settedLink
            self.board.unDrawLink(choicedLink)
        
        game.getPreviousState()
        
        for obj in game.getCurrentBoard().getSettedLinks():
            self.board.drawLink(obj)
        
        shirokuroApp.screen_manager.transition.direction = "right"
        
class guideSolutionDisplay(GridLayout):    
    def __init__(self, **kwargs):
        super(guideSolutionDisplay, self).__init__(**kwargs)
        
        self.cols = 1
        self.rows = 2

        self.add_widget(guideSolution())
        
        self.submit = Button(text="Menu", size_hint_y=0.1)
        """
        self.submit = Button(text="Menu", font_size=20, size_hint_y=0.1)
        """
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_goMenu)

        self.add_widget(self.submit)
    
    def button_goMenu(self, instance):
        store.put('currentSlot', value=0)
        shirokuroApp.screen_manager.current = "menuPrincipal"
        shirokuroApp.screen_manager.transition.direction = "left"

class allSolution(GridLayout):
    i = 0
    
    def __init__(self, **kwargs):
        super(allSolution, self).__init__(**kwargs)
        
        self.cols = 1
        self.rows = 2
        
        self.board = BoardRepr()
        self.add_widget(self.board)
        
        self.subMenu = GridLayout(size_hint_y=.1)
        
        self.subMenu.cols = 2
        self.subMenu.rows = 1
        
        """ Saltar a otra solucion """
        self.jump_to_solution = GridLayout()
        self.jump_to_solution.cols = 2
        self.jump_to_solution.rows = 1
        
        """ Info. solucion actual"""
        self.current_solution = GridLayout()
        self.current_solution.cols = 1
        self.current_solution.rows = 2
        
        self.label_solution = Label(text="Current: "+str(self.i+1)+"/"+str(game.getNumberOfSolutions()))
        """ En la versión móvil se evita que el texto del botón, si es largo, se salga de éste. """
        self.label_solution.halign = 'left'
        self.label_solution.valign = 'middle'
        self.label_solution.bind(size=self.label_solution.setter('text_size'))
        
        self.current_solution.add_widget(self.label_solution)
        
        self.field_inputSolutionNumber = TextInput(text="1", multiline=False, size_hint_y = 0.8)
        self.current_solution.add_widget(self.field_inputSolutionNumber)
        
        self.jump_to_solution.add_widget(self.current_solution)
        
        self.submit = Button(text='Go', size_hint_x = 0.2)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        """
        self.submit = Button(text='Enviar', font_size=20)
        """
        self.submit.bind(on_press=self.button_inputSolutionNumber)
        
        self.jump_to_solution.add_widget(self.submit)
        
        self.subMenu.add_widget(self.jump_to_solution)
        
        """ Botones Anterior y Siguiente """
        self.secuential_buttons = GridLayout()
        self.secuential_buttons.cols = 2
        self.secuential_buttons.rows = 1
        
        self.submit = Button(text='Previous')
        """
        self.submit = Button(text='Anterior', font_size=20)
        """
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_goPreviousSolution)
        self.secuential_buttons.add_widget(self.submit)
        
        self.submit = Button(text='Next')
        """
        self.submit = Button(text='Siguiente', font_size=20)
        """
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_goNextSolution)
        self.secuential_buttons.add_widget(self.submit)
        
        self.subMenu.add_widget(self.secuential_buttons)
        
        self.add_widget(self.subMenu)
        
    def button_goPreviousSolution(self, instance):
        self.i = (self.i - 1) if self.i > 0 else 0

        for settedLink in game.getCurrentBoard().getSettedLinks():
            choicedLink = settedLink
            self.board.unDrawLink(choicedLink)
        
        self.board.resetYellowLayoutDict()
        
        game.getSolutionByInputNumber(self.i)
        
        for obj in game.getCurrentBoard().getSettedLinks():
            self.board.drawLink(obj)
            
        self.label_solution.text = "Current: "+str(self.i+1)+"/"+str(game.getNumberOfSolutions())
        self.field_inputSolutionNumber.text = str(self.i+1)
        
        shirokuroApp.screen_manager.transition.direction = "right"
    
    def button_goNextSolution(self, instance):
        self.i = (self.i + 1) if self.i < (len(game.getAllSolutions())-1) else (len(game.getAllSolutions())-1)

        for settedLink in game.getCurrentBoard().getSettedLinks():
            choicedLink = settedLink
            self.board.unDrawLink(choicedLink)
        
        self.board.resetYellowLayoutDict()
        
        game.getSolutionByInputNumber(self.i)
        
        for obj in game.getCurrentBoard().getSettedLinks():
            self.board.drawLink(obj)

        self.label_solution.text = "Current: "+str(self.i+1)+"/"+str(game.getNumberOfSolutions())
        self.field_inputSolutionNumber.text = str(self.i+1)
        
        shirokuroApp.screen_manager.transition.direction = "left"
        
    def button_inputSolutionNumber(self, instance):
        try:
            i = int(self.field_inputSolutionNumber.text)
            if(i >= 1 and i <= game.getNumberOfSolutions()):
                
                self.i = i-1
                
                for settedLink in game.getCurrentBoard().getSettedLinks():
                    choicedLink = settedLink
                    self.board.unDrawLink(choicedLink)
                
                self.board.resetYellowLayoutDict()
                
                game.getSolutionByInputNumber(self.i)
                
                for obj in game.getCurrentBoard().getSettedLinks():
                    self.board.drawLink(obj)

                self.label_solution.text = "Current: "+str(self.i+1)+"/"+str(game.getNumberOfSolutions())
                self.field_inputSolutionNumber.text = str(self.i+1)
                
                shirokuroApp.screen_manager.transition.direction = "left"
                                
            else:
                pass
        except:
            pass

class allSolutionDisplay(GridLayout):    
    def __init__(self, **kwargs):
        super(allSolutionDisplay, self).__init__(**kwargs)
        
        self.cols = 1
        self.rows = 2
        
        self.allSolutionObj = allSolution()
        self.add_widget(self.allSolutionObj)
        
        self.submit = Button(text="Menu", size_hint_y=0.1)
        """
        self.submit = Button(text="Menu", font_size=20, size_hint_y=0.1)
        """
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_goMenu)

        self.add_widget(self.submit)

    def button_goMenu(self, instance):
        
        for settedLink in game.getCurrentBoard().getSettedLinks():
            choicedLink = settedLink
            self.allSolutionObj.board.unDrawLink(choicedLink)
        
        self.allSolutionObj.board.resetYellowLayoutDict()
        
        store.put('currentSlot', value=0)
        shirokuroApp.screen_manager.current = "menuPrincipal"
        shirokuroApp.screen_manager.transition.direction = "left"

class solutionMenu(GridLayout):
    currentOption = "originalSolution"
    
    def __init__(self, **kwargs):
        super(solutionMenu, self).__init__()
        
        self.cols = 1
        self.rows = 2
        
        for key, value in kwargs.items():
            if(str(key)=="currentOption"):
                self.currentOption=value
                
        if(self.currentOption == "originalSolution"):
            game.restartGame()
            game.getOriginalSolution()
            self.solutionDisplay = solution()
        elif(self.currentOption == "guideSolution"):
            game.restartGame()
            idx = int(game.currentState())
            game.helpingLoop()            
            game.returnToGivenState(idx)
            self.solutionDisplay = guideSolution()
        elif(self.currentOption == "allSolution"):
            game.restartGame()
            game.getAllSolutions()
            game.getSolutionByInputNumber(0)
            self.solutionDisplay = allSolution()
                    
            nameSaveGame = 'saveGame'+str(store.get('currentSlot')['value'])
            
            if(store.get(nameSaveGame)['toBuild']['shirokuroGame']['allSolutions']=='None'):
                
                shirokuroApp.root.get_screen('menuJugar').children[0].saveInJSON()
        
        self.add_widget(self.solutionDisplay)
        
        self.subMenu = GridLayout(size_hint_y = 0.1)
        self.subMenu.cols = 3
        self.subMenu.rows = 1
        
        self.button_originalSolution = Button(text="Original solution")
        """
        self.button_originalSolution = Button(text="Solucion original", font_size=20)
        """
        self.button_originalSolution.halign = 'center'
        self.button_originalSolution.valign = 'middle'
        self.button_originalSolution.bind(size=self.button_originalSolution.setter('text_size'))
        self.button_originalSolution.bind(on_press=self.button_goOriginalSolution)
        self.subMenu.add_widget(self.button_originalSolution)
        
        self.button_guideSolution = Button(text="Guide solution")
        """
        self.button_guideSolution = Button(text="Solucion guiada", font_size=20)
        """
        self.button_guideSolution.halign = 'center'
        self.button_guideSolution.valign = 'middle'
        self.button_guideSolution.bind(size=self.button_guideSolution.setter('text_size'))
        self.button_guideSolution.bind(on_press=self.button_goGuideSolution)
        self.subMenu.add_widget(self.button_guideSolution)
        
        self.button_allSolution = Button(text="All solutions")
        """
        self.button_allSolution = Button(text="Todas las soluciones", font_size=20)
        """
        """ En la versión móvil se evita que el texto del botón, si es largo, se salga de éste. """
        self.button_allSolution.halign = 'center'
        self.button_allSolution.valign = 'middle'
        self.button_allSolution.bind(size=self.button_allSolution.setter('text_size'))
        
        self.button_allSolution.bind(on_press=self.button_goAllSolution)
        self.subMenu.add_widget(self.button_allSolution)
        
        self.add_widget(self.subMenu)
        
    def button_goOriginalSolution(self, instance):
        
        screen = shirokuroApp.root.get_screen('menuSolucion')
        solutionMenuObj = screen.children[0]
        oldFromScreen = solutionMenuObj.getFromScreen()

        newSolutionMenu = solutionMenuDisplay(fromScreen=str(oldFromScreen), currentOption="originalSolution")
        
        screen.remove_widget(solutionMenuObj)
        
        screen.add_widget(newSolutionMenu)
        
        shirokuroApp.screen_manager.current = "menuSolucion"
            
    def button_goGuideSolution(self, instance):
        
        screen = shirokuroApp.root.get_screen('menuSolucion')
        solutionMenuObj = screen.children[0]
        oldFromScreen = solutionMenuObj.getFromScreen()

        newSolutionMenu = solutionMenuDisplay(fromScreen=str(oldFromScreen), currentOption="guideSolution")
        
        screen.remove_widget(solutionMenuObj)
        
        screen.add_widget(newSolutionMenu)
        
        shirokuroApp.screen_manager.current = "menuSolucion"
            
    def button_goAllSolution(self, instance):

        screen = shirokuroApp.root.get_screen('menuSolucion')
        solutionMenuObj = screen.children[0]
        oldFromScreen = solutionMenuObj.getFromScreen()

        newSolutionMenu = solutionMenuDisplay(fromScreen=str(oldFromScreen), currentOption="allSolution")
        
        screen.remove_widget(solutionMenuObj)
        
        screen.add_widget(newSolutionMenu)
        
        shirokuroApp.screen_manager.current = "menuSolucion"

class solutionMenuDisplay(GridLayout):
    currentOption = "originalSolution"
    fromScreen = ObjectProperty("")
    
    def __init__(self, **kwargs):
        super(solutionMenuDisplay, self).__init__()
        
        for key, value in kwargs.items():
            if(str(key)=="fromScreen"):
                self.fromScreen=value
            elif(str(key)=="currentOption"):
                self.currentOption=value
        
        self.cols = 1
        self.rows = 2
        
        self.solution_menu = solutionMenu(currentOption=str(self.currentOption))
        self.add_widget(self.solution_menu)
        
        buttonText = ""
        if(self.getFromScreen()=="menuJugar"):
            buttonText = "Menu"
        else:
            buttonText = "Back"
        
        self.submit = Button(text=buttonText, size_hint_y=0.1)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_go)
        self.add_widget(self.submit)
        
    def button_go(self, instance):
        if(self.getFromScreen()=="menuJugar"):
            store.put('currentSlot', value=0)
            shirokuroApp.screen_manager.current = "menuPrincipal"
            shirokuroApp.screen_manager.transition.direction = "left"
        elif(self.getFromScreen()=="clasificacion"):
            store.put('currentSlot', value=0)
            shirokuroApp.screen_manager.current = "clasificacion"
            shirokuroApp.screen_manager.transition.direction = "right"
        elif(self.getFromScreen()=="menuCargar"):
            store.put('currentSlot', value=0)
            shirokuroApp.screen_manager.current = "menuCargar"
            shirokuroApp.screen_manager.transition.direction = "right"
    
    def updateFromScreen(self, input_FromScreen):
        self.fromScreen = input_FromScreen

    def getFromScreen(self):
        return self.fromScreen
    
class Ranking(GridLayout):
    fromScreen = ObjectProperty("")
    difficulty = "1"
    numRows = "5"
    numColumns = "5"
    
    def __init__(self, **kwargs):
        super(Ranking, self).__init__()
        
        for key, value in kwargs.items():
            if(str(key)=="difficulty"):
                self.difficulty=value
            elif(str(key)=="numRows"):
                self.numRows=value
            elif(str(key)=="numColumns"):
                self.numColumns=value
            else:
                raise Exception("Bug inside Ranking Init Method")
        
        self.cols = 1
        self.rows = 3
        
        """ Filtro """
        self.filter = GridLayout(size_hint_y=0.3)
        self.filter.cols = 1
        self.filter.rows = 2
        
        """ 3 Secciones del filtro """
        self.filter_sections = GridLayout()
        self.filter_sections.cols = 3
        self.filter_sections.rows = 1
        
        """ Filtro dificultad: Label y textInput """
        self.difficulty_section = GridLayout()
        self.difficulty_section.rows = 2
        
        self.label1 = Label(text="Difficulty[1-3]")
        #self.label1 = Label(text="Dificultad[1-3]", font_size=20)
        self.label1.halign = 'center'
        self.label1.valign = 'middle'
        self.label1.bind(size=self.label1.setter('text_size'))   
        self.difficulty_section.add_widget(self.label1)
        
        self.field_difficulty = TextInput(text=self.difficulty, multiline=False)
        self.difficulty_section.add_widget(self.field_difficulty)
        
        self.filter_sections.add_widget(self.difficulty_section)
        
        """ Filtro filas: Label y textInput """
        self.rows_section = GridLayout()
        self.rows_section.rows = 2

        self.label2 = Label(text="Nº Rows")
        #self.label2 = Label(text="Nº Filas", font_size=20)
        self.label2.halign = 'center'
        self.label2.valign = 'middle'
        self.label2.bind(size=self.label2.setter('text_size'))   
        self.rows_section.add_widget(self.label2)
        
        self.field_numRows = TextInput(text=self.numRows, multiline=False)
        self.rows_section.add_widget(self.field_numRows)
        
        self.filter_sections.add_widget(self.rows_section)
        
        """ Filtro columnas: Label y textInput """
        self.columns_section = GridLayout()
        self.columns_section.rows = 2

        self.label3 = Label(text="Nº Columns")
        #self.label3 = Label(text="Nº Columnas", font_size=20)
        self.label3.halign = 'center'
        self.label3.valign = 'middle'
        self.label3.bind(size=self.label3.setter('text_size'))   
        self.columns_section.add_widget(self.label3)
        
        self.field_numColumns = TextInput(text=self.numColumns, multiline=False)
        self.columns_section.add_widget(self.field_numColumns)
        
        self.filter_sections.add_widget(self.columns_section)
        
        self.filter.add_widget(self.filter_sections)
        
        """ Boton de filtrar """
        self.toFilter = GridLayout(size_hint_y=0.33)
        self.toFilter.rows = 1
        
        self.submit = Button(text="Filter")
        #self.submit = Button(text="Enviar", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))   
        self.submit.bind(on_press=self.button_filter)
        self.toFilter.add_widget(self.submit)
        
        self.filter.add_widget(self.toFilter)
        
        self.add_widget(self.filter)

        """ ScrollView """
        self.sv = ScrollView()
        
        self.layout = GridLayout()
        self.layout.size_hint_y=None
        self.layout.cols=1
        self.layout.spacing=10
        
        self.layout.row_default_height = self.height*0.2
        self.layout.height = self.minimum_height
        
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        orderedDicc = dict()
        for i in range(1, store.get('lastSlot')['value']+1):
            nameSaveGame = "saveGame"+str(i)
            if(store.exists(nameSaveGame)):
                gamePassed = store.get(nameSaveGame)['toBuild']['shirokuroGame']['gamePassed']
                if(gamePassed == True):
                    orderedDicc[nameSaveGame] = store.get(nameSaveGame)['toBuild']['shirokuroGame']['score']
        orderedDicc = {k: v for k, v in sorted(orderedDicc.items(), key=lambda item: item[1], reverse=True)}
        
        i=0
        for key in orderedDicc.keys():
            
            nameSaveGame = key
            
            if(store.exists(nameSaveGame)):
                
                difficultyLevel = store.get(nameSaveGame)['toBuild']['shirokuroGame']['difficultyLevel']
                numRows = store.get(nameSaveGame)['toBuild']['table']['numRows']
                numColumns = store.get(nameSaveGame)['toBuild']['table']['numColumns']
                gamePassed = store.get(nameSaveGame)['toBuild']['shirokuroGame']['gamePassed']
                
                if(difficultyLevel == int(self.difficulty) and numRows == int(self.numRows) and numColumns == int(self.numColumns) and gamePassed == True):
                    
                    
                    
                    
                    
                    """ Fila: partida"""
                    self.partida = GridLayout(size_hint_y=None, height=400)
                    
                    self.partida.cols = 2
                    self.partida.rows = 1
                    
                    self.inside1 = GridLayout()
                    
                    #self.inside1.cols = 1 + 6 
                    self.inside1.rows = 1 + 6 
    
                    shirokuroGameInfo = store.get(nameSaveGame)['toBuild']['shirokuroGame']
                    tableInfo = store.get(nameSaveGame)['toBuild']['table']
                    
                    i=i+1
                    self.label0 = Label(text="Position: "+str(i))
                    self.label0.halign = 'left'
                    self.label0.valign = 'middle'
                    self.label0.bind(size=self.label0.setter('text_size'))   
                    self.inside1.add_widget(self.label0)
    
                    self.label1 = Label(text="Rows: "+str(tableInfo['numRows']))
                    self.label1.halign = 'left'
                    self.label1.valign = 'middle'
                    self.label1.bind(size=self.label1.setter('text_size'))   
                    self.inside1.add_widget(self.label1)
                    
                    self.label2 = Label(text="Columas: "+str(tableInfo['numColumns']))
                    self.label2.halign = 'left'
                    self.label2.valign = 'middle'
                    self.label2.bind(size=self.label2.setter('text_size'))   
                    self.inside1.add_widget(self.label2)
                    
                    self.label3 = Label(text="Difficulty: "+str(shirokuroGameInfo['difficultyLevel']))
                    self.label3.halign = 'left'
                    self.label3.valign = 'middle'
                    self.label3.bind(size=self.label3.setter('text_size'))   
                    self.inside1.add_widget(self.label3)
                    
                    self.label4 = Label(text="Helps: "+str(shirokuroGameInfo['numHelps']))
                    self.label4.halign = 'left'
                    self.label4.valign = 'middle'
                    self.label4.bind(size=self.label4.setter('text_size'))   
                    self.inside1.add_widget(self.label4)
                    
                    self.label5 = Label(text="Time: "+str(shirokuroGameInfo['chrono']))
                    self.label5.halign = 'left'
                    self.label5.valign = 'middle'
                    self.label5.bind(size=self.label5.setter('text_size'))   
                    self.inside1.add_widget(self.label5)
                    
                    self.label6 = Label(text="Score: "+str(shirokuroGameInfo['score']))
                    self.label6.halign = 'left'
                    self.label6.valign = 'middle'
                    self.label6.bind(size=self.label6.setter('text_size'))   
                    self.inside1.add_widget(self.label6)
                    
                    self.partida.add_widget(self.inside1)
                    
                    
                    
                    
                    
                    
                    
                    
                    """ Fila: partida """
                    """
                    self.partida = GridLayout(size_hint_y=None, height=40)
                    
                    self.partida.cols = 1+6+1
                    self.partida.rows = 1

                    shirokuroGameInfo = store.get(nameSaveGame)['toBuild']['shirokuroGame']
                    tableInfo = store.get(nameSaveGame)['toBuild']['table']
                    
                    i=i+1
                    self.label0 = Label(text="Posicion: "+str(i))
                    self.label0.halign = 'left'
                    self.label0.valign = 'middle'
                    self.label0.bind(size=self.label0.setter('text_size'))   
                    self.partida.add_widget(self.label0)

                    self.label1 = Label(text="Filas: "+str(tableInfo['numRows']))
                    self.label1.halign = 'left'
                    self.label1.valign = 'middle'
                    self.label1.bind(size=self.label1.setter('text_size'))   
                    self.partida.add_widget(self.label1)
                    
                    self.label2 = Label(text="Columnas: "+str(tableInfo['numColumns']))
                    self.label2.halign = 'left'
                    self.label2.valign = 'middle'
                    self.label2.bind(size=self.label2.setter('text_size'))   
                    self.partida.add_widget(self.label2)
                    
                    self.label3 = Label(text="Dificultad: "+str(shirokuroGameInfo['difficultyLevel']))
                    self.label3.halign = 'left'
                    self.label3.valign = 'middle'
                    self.label3.bind(size=self.label3.setter('text_size'))   
                    self.partida.add_widget(self.label3)
                    
                    self.label4 = Label(text="Ayudas: "+str(shirokuroGameInfo['numHelps']))
                    self.label4.halign = 'left'
                    self.label4.valign = 'middle'
                    self.label4.bind(size=self.label4.setter('text_size'))   
                    self.partida.add_widget(self.label4)
                    
                    self.label5 = Label(text="Tiempo: "+str(shirokuroGameInfo['chrono']))
                    self.label5.halign = 'left'
                    self.label5.valign = 'middle'
                    self.label5.bind(size=self.label5.setter('text_size'))   
                    self.partida.add_widget(self.label5)
                    
                    self.label6 = Label(text="Puntos: "+str(shirokuroGameInfo['score']))
                    self.label6.halign = 'left'
                    self.label6.valign = 'middle'
                    self.label6.bind(size=self.label6.setter('text_size'))   
                    self.partida.add_widget(self.label6)
                    """
                    
                    
                    """ Boton cargar y borrar """
                    """
                    self.buttons = GridLayout()
    
                    self.submit = Button(text="Ver")
                    self.submit.halign = 'center'
                    self.submit.valign = 'middle'
                    self.submit.bind(size=self.submit.setter('text_size'))
                    self.submit.bind(on_press=partial(self.view_results, nameSaveGame))
                    self.buttons.add_widget(self.submit)
                    
                    self.partida.add_widget(self.buttons)
                    self.layout.add_widget(self.partida)
                    """
                    
                    
                    
                    self.submit = Button(text="Go")
                    self.submit.halign = 'center'
                    self.submit.valign = 'middle'
                    self.submit.bind(size=self.submit.setter('text_size'))
                    self.submit.bind(on_press=partial(self.view_results, nameSaveGame))
                    
                    self.partida.add_widget(self.submit)
                    
                    self.layout.add_widget(self.partida)
                    
                    """Separador"""
                    self.submit = Button(text="")
                    self.layout.add_widget(self.submit)

                    
                else:
                    pass
            
        self.sv.add_widget(self.layout)
        self.add_widget(self.sv)
        
        self.submit = Button(text="Back", size_hint_y = 0.1)
        #self.submit = Button(text="Atras", font_size=20, size_hint_y = 0.1)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))  
        self.submit.bind(on_press=self.goBack)

        self.add_widget(self.submit)
        
    def view_results(self, nameSaveGame, instance):

        loaderObj.loadSaveGame(nameSaveGame)
        
        if(not(shirokuroApp.screen_manager.has_screen(name="menuSolucion"))):
            screen = Screen(name="menuSolucion")
            screen.add_widget(solutionMenuDisplay(fromScreen="clasificacion"))
            shirokuroApp.screen_manager.add_widget(screen)
        else:
            screen = shirokuroApp.root.get_screen('menuSolucion')
            solutionMenuObj = screen.children[0]
            screen.remove_widget(solutionMenuObj)
            screen.add_widget(solutionMenuDisplay(fromScreen="clasificacion"))
        
        shirokuroApp.screen_manager.current = "menuSolucion"
        shirokuroApp.screen_manager.transition.direction = "left"
        
    def button_filter(self, instance):

        try:
            newDifficulty = str(int(self.field_difficulty.text))
            newNumRows = str(int(self.field_numRows.text))
            newNumColumns = str(int(self.field_numColumns.text))
            
            screen = shirokuroApp.root.get_screen('clasificacion')
            rankingObj = screen.children[0]

            newRanking = Ranking(difficulty=newDifficulty, numRows=newNumRows, numColumns=newNumColumns)

            screen.remove_widget(rankingObj)
            
            screen.add_widget(newRanking)
            
            shirokuroApp.screen_manager.current = "clasificacion"

        except:
            pass
            
    def setDifficultyField(self, difficulty):
        self.difficulty = difficulty
    
    def setNumRowsField(self, numRows):
        self.numRows = numRows
    
    def setNumColumnsField(self, numColumns):
        self.numColumns = numColumns
        
    def goBack(self, instance):
        store.put('currentSlot', value=0)
        shirokuroApp.screen_manager.current = "menuPrincipal"
        shirokuroApp.screen_manager.transition.direction = "right"

class loadMenu(GridLayout):
    fromScreen = ObjectProperty("")
    gameType = "pendientes"
    buttonPressed = None
    
    def __init__(self, **kwargs):
        super(loadMenu, self).__init__()
        
        for key, value in kwargs.items():
            if(str(key)=="gameType"):
                self.gameType = value
        
        self.cols = 1
        self.rows = 3
        
        """ Pestanyas: pendientes y completadas """
        self.pestanyas = GridLayout(size_hint_y=0.1)
        self.pestanyas.cols = 2
        self.pestanyas.rows = 1
        
        self.submit1 = Button(text="Pending")
        #self.submit1 = Button(text="Pendientes", font_size=20)
        self.submit1.halign = 'center'
        self.submit1.valign = 'middle'
        self.submit1.bind(size=self.submit1.setter('text_size'))
        self.submit1.bind(on_press=self.button_goPendientes)
        
        self.submit2 = Button(text="Completed")
        #self.submit2 = Button(text="Completadas", font_size=20)
        self.submit2.halign = 'center'
        self.submit2.valign = 'middle'
        self.submit2.bind(size=self.submit2.setter('text_size'))
        self.submit2.bind(on_press=self.button_goCompletadas)
        
        if(self.gameType == "pendientes"):
            self.buttonPressed = self.submit1
        elif(self.gameType == "completadas"):
            self.buttonPressed = self.submit2
        else:
            raise Exception("ButtonPressed LoadMenu Bug")
        
        green = [0,1,0,1]
        self.buttonPressed.background_color = green
        
        self.pestanyas.add_widget(self.submit1)
        self.pestanyas.add_widget(self.submit2)
        
        self.add_widget(self.pestanyas)
        
        """ ScrollView """
        self.sv = ScrollView()

        self.layout = GridLayout()
        self.layout.size_hint_y=None
        self.layout.cols=1
        self.layout.spacing=10
        
        self.layout.row_default_height = self.height*0.2
        self.layout.height = self.minimum_height
        
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        for i in range(1, store.get('lastSlot')['value']+1):
            
            nameSaveGame = 'saveGame'+str(i)
            
            if(store.exists(nameSaveGame)):
                
                gamePassed = store.get(nameSaveGame)['toBuild']['shirokuroGame']['gamePassed']
                
                if((self.gameType == "pendientes" and not(gamePassed)) or (self.gameType == "completadas" and gamePassed)):
                    
                    """ Fila: partida"""
                    self.partida = GridLayout(size_hint_y=None, height=400)
                    
                    self.partida.cols = 2
                    self.partida.rows = 1
                    
                    self.inside1 = GridLayout()
                    
                    #self.inside1.cols = 1 + 6 
                    self.inside1.rows = 1 + 6 
    
                    shirokuroGameInfo = store.get(nameSaveGame)['toBuild']['shirokuroGame']
                    tableInfo = store.get(nameSaveGame)['toBuild']['table']                    
    
                    self.label0 = Label(text="Slot: "+str(i))
                    self.label0.halign = 'left'
                    self.label0.valign = 'middle'
                    self.label0.bind(size=self.label0.setter('text_size'))   
                    self.inside1.add_widget(self.label0)
    
                    self.label1 = Label(text="Rows: "+str(tableInfo['numRows']))
                    self.label1.halign = 'left'
                    self.label1.valign = 'middle'
                    self.label1.bind(size=self.label1.setter('text_size'))   
                    self.inside1.add_widget(self.label1)
                    
                    self.label2 = Label(text="Columns: "+str(tableInfo['numColumns']))
                    self.label2.halign = 'left'
                    self.label2.valign = 'middle'
                    self.label2.bind(size=self.label2.setter('text_size'))   
                    self.inside1.add_widget(self.label2)
                    
                    self.label3 = Label(text="Difficulty: "+str(shirokuroGameInfo['difficultyLevel']))
                    self.label3.halign = 'left'
                    self.label3.valign = 'middle'
                    self.label3.bind(size=self.label3.setter('text_size'))   
                    self.inside1.add_widget(self.label3)
                    
                    self.label4 = Label(text="Helps: "+str(shirokuroGameInfo['numHelps']))
                    self.label4.halign = 'left'
                    self.label4.valign = 'middle'
                    self.label4.bind(size=self.label4.setter('text_size'))   
                    self.inside1.add_widget(self.label4)
                    
                    self.label5 = Label(text="Time: "+str(shirokuroGameInfo['chrono']))
                    self.label5.halign = 'left'
                    self.label5.valign = 'middle'
                    self.label5.bind(size=self.label5.setter('text_size'))   
                    self.inside1.add_widget(self.label5)
                    
                    self.label6 = Label(text="Score: "+str(shirokuroGameInfo['score']))
                    self.label6.halign = 'left'
                    self.label6.valign = 'middle'
                    self.label6.bind(size=self.label6.setter('text_size'))   
                    self.inside1.add_widget(self.label6)
                    
                    self.partida.add_widget(self.inside1)
                    
                    """ Boton cargar y borrar """
                    self.buttons = GridLayout()
                    self.buttons.rows = 2
    
                    self.submit = Button(text="Load")
                    self.submit.halign = 'center'
                    self.submit.valign = 'middle'
                    self.submit.bind(size=self.submit.setter('text_size'))
                    self.submit.bind(on_press=partial(self.button_loadSaveGame, nameSaveGame))
                    self.buttons.add_widget(self.submit)
                    
                    self.submit = Button(text="Delete")
                    self.submit.halign = 'center'
                    self.submit.valign = 'middle'
                    self.submit.bind(size=self.submit.setter('text_size'))
                    self.submit.bind(on_press=partial(self.button_deleteSaveGame, nameSaveGame))
                    self.buttons.add_widget(self.submit)
                    
                    self.partida.add_widget(self.buttons)
                    self.layout.add_widget(self.partida)
                    
                    """Separador"""
                    self.submit = Button(text="")
                    self.layout.add_widget(self.submit)
        
        self.sv.add_widget(self.layout)
        self.add_widget(self.sv)
        
        """ Boton retroceder """
        self.submit = Button(text="Back", size_hint_y=0.1)
        #self.submit = Button(text="Atras", font_size=20, size_hint_y=0.1)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.goBack)

        self.add_widget(self.submit)

    def button_goPendientes(self, instance):
        
        if(self.gameType == "pendientes"):
            pass
        else:
            screen = shirokuroApp.root.get_screen('menuCargar')
            loadMenuObj = screen.children[0]

            newloadMenu = loadMenu()
            
            screen.remove_widget(loadMenuObj)
            
            screen.add_widget(newloadMenu)
            
            if(self.getFromScreen() == "menuPrincipal"):
                shirokuroApp.root.get_screen('menuCargar').children[0].updateFromScreen(input_FromScreen="menuPrincipal")
            elif(self.getFromScreen() == "menuJugar"):
                shirokuroApp.root.get_screen('menuCargar').children[0].updateFromScreen(input_FromScreen="menuJugar")
            
            shirokuroApp.screen_manager.current = "menuCargar"
            
    def button_goCompletadas(self, instance):
        
        if(self.gameType == "completadas"):
            pass
        else:
            screen = shirokuroApp.root.get_screen('menuCargar')
            loadMenuObj = screen.children[0]

            newloadMenu = loadMenu(gameType="completadas")
            
            screen.remove_widget(loadMenuObj)
            
            screen.add_widget(newloadMenu)
            
            if(self.getFromScreen() == "menuPrincipal"):
                shirokuroApp.root.get_screen('menuCargar').children[0].updateFromScreen(input_FromScreen="menuPrincipal")
            elif(self.getFromScreen() == "menuJugar"):
                shirokuroApp.root.get_screen('menuCargar').children[0].updateFromScreen(input_FromScreen="menuJugar")
            
            shirokuroApp.screen_manager.current = "menuCargar"
    
    def button_deleteSaveGame(self, input_nameSaveGame, instance):
        
        currentSlotValue = int(store.get('currentSlot')['value'])
        
        """ llamada a metodo de clase """
        loaderObj.deleteSaveGame(input_nameSaveGame)

        screen = shirokuroApp.root.get_screen('menuCargar')
        loadMenuObj = screen.children[0]
        newLoadMenu = loadMenu(gameType=str(self.gameType))
        
        target = ""
        if(self.getFromScreen() == "menuJugar" and int(input_nameSaveGame.split("saveGame")[1]) == currentSlotValue):
            """ Lo derivamos al menu """
            target = "menuPrincipal"
            store.put('currentSlot', value=0)
            newLoadMenu.updateFromScreen(target)
        else:
            """ Lo mantenemos donde está """
            target = "menuCargar"
            newLoadMenu.updateFromScreen(self.fromScreen)
        
        screen.remove_widget(loadMenuObj)
        screen.add_widget(newLoadMenu)
        
        shirokuroApp.screen_manager.current = target
        shirokuroApp.screen_manager.transition.direction = "left"
    
    def button_loadSaveGame(self, input_nameSaveGame, instance):
        
        gamePassed = store.get(input_nameSaveGame)['toBuild']['shirokuroGame']['gamePassed']
        
        if(self.fromScreen == "menuJugar"):
            shirokuroApp.root.get_screen('menuJugar').children[0].removeCurrentBoard()
        
        loaderObj.loadSaveGame(input_nameSaveGame)
        
        if(gamePassed):
                        
            if(not(shirokuroApp.screen_manager.has_screen(name="menuSolucion"))):
                screen = Screen(name="menuSolucion")
                screen.add_widget(solutionMenuDisplay(fromScreen="menuCargar"))
                shirokuroApp.screen_manager.add_widget(screen)
            else:
                screen = shirokuroApp.root.get_screen('menuSolucion')
                solutionMenuObj = screen.children[0]
                screen.remove_widget(solutionMenuObj)
                screen.add_widget(solutionMenuDisplay(fromScreen="menuCargar"))
            
            shirokuroApp.screen_manager.current = "menuSolucion"
            shirokuroApp.screen_manager.transition.direction = "left"
            
        else:
                        
            if(shirokuroApp.screen_manager.has_screen(name="tablero")):
                screen = shirokuroApp.screen_manager.get_screen(name="tablero")
                shirokuroApp.screen_manager.remove_widget(screen)
            
            screen = Screen(name="tablero")
            #screen.add_widget(Board(id="board"))
            screen.add_widget(Board())        
            shirokuroApp.screen_manager.add_widget(screen)
            
            if(not(shirokuroApp.screen_manager.has_screen(name="menuJugar"))):
                screen = Screen(name="menuJugar")
                screen.add_widget(playMenu())
                shirokuroApp.screen_manager.add_widget(screen)
            
            chronometer.parent = None
            chronometer.startSinceCurrentCount(currentCount=game.chrono())
            
            shirokuroApp.screen_manager.current = "tablero"
            shirokuroApp.screen_manager.transition.direction = "left"

    def goBack(self, instance):
        
        nameSaveGame = "saveGame"+str(store.get('currentSlot')['value'])
        if(nameSaveGame == "saveGame0"):
            if(self.getFromScreen() == "menuPrincipal"):
                store.put('currentSlot', value=0)
                shirokuroApp.screen_manager.current = self.getFromScreen()
                shirokuroApp.screen_manager.transition.direction = "right"
            else:
                try:
                    shirokuroApp.root.get_screen('tablero').children[0]
                    shirokuroApp.screen_manager.current = self.getFromScreen()
                    shirokuroApp.screen_manager.transition.direction = "right"
                except:
                    store.put('currentSlot', value=0)
                    shirokuroApp.screen_manager.current = "menuPrincipal"
                    shirokuroApp.screen_manager.transition.direction = "left"
        else:
            gamePassed = store.get(nameSaveGame)['toBuild']['shirokuroGame']['gamePassed']
            if(gamePassed and not(self.getFromScreen() == "menuPrincipal")):
                self.updateFromScreen(input_FromScreen="menuPrincipal")
                store.put('currentSlot', value=0)
                shirokuroApp.screen_manager.current = self.getFromScreen()
                shirokuroApp.screen_manager.transition.direction = "left"
            else:
                if(self.getFromScreen() == "menuPrincipal"):
                    store.put('currentSlot', value=0)
                shirokuroApp.screen_manager.current = self.getFromScreen()
                shirokuroApp.screen_manager.transition.direction = "right"
        
    def updateFromScreen(self, input_FromScreen):
        self.fromScreen = input_FromScreen

    def getFromScreen(self):
        return self.fromScreen

class playMenu(GridLayout):    
    def __init__(self, **kwargs):
        super(playMenu, self).__init__(**kwargs)
        
        self.cols = 1
        
        self.submit = Button(text="Move")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_move)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Mover", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_move)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Help")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getHelp)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Ayuda", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getHelp)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Previous state")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getPreviousState)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Volver al estado anterior", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getPreviousState)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Next state")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getNextState)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Volver al estado posterior", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getNextState)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Save state")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_saveState)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Guardar estado", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_saveState)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Load state")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_goSavedState)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Volver al estado guardado", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_goSavedState)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Original solution")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getOriginalSolution)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Solucion original del tablero", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getOriginalSolution)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Solution from current state")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getSolutionFromCurrentStatus)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Solucionar tablero respetando la disposicion actual", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getSolutionFromCurrentStatus)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Reset")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_restartGame)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Reiniciar juego", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_restartGame)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="All solutions")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getAllSolutions)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Todas las soluciones", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getAllSolutions)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Pause")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_pause)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Pausar", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_pause)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Resume")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_resume)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Reanudar", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_resume)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Another board with same metrics")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getTableSameMetrics)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Otro tablero con iguales metricas", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getTableSameMetrics)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Save game")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_saveGame)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Guardar partida", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_saveGame)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Guide solution")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getGuideSolution)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Solucion guiada", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getGuideSolution)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Another board with different metrics")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getTableDifferentMetrics)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Otro tablero con distintas metricas", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getTableDifferentMetrics)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Instructions")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getInstructions)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Instrucciones", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_getInstructions)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Load game")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_loadGame)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Cargar partida", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_loadGame)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Solution menu")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_solutionMenu)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Menu de soluciones", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_solutionMenu)
        self.add_widget(self.submit)
        """
        
        self.submit = Button(text="Exit")
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_leaveGame)
        self.add_widget(self.submit)
        """
        self.submit = Button(text="Salir", font_size=20)
        self.submit.halign = 'center'
        self.submit.valign = 'middle'
        self.submit.bind(size=self.submit.setter('text_size'))
        self.submit.bind(on_press=self.button_leaveGame)
        self.add_widget(self.submit)
        """

    def removeCurrentBoard(self):
        screen = shirokuroApp.root.get_screen('tablero')
        boardObj = screen.children[0]
        chronometer.uncouple()
        screen.remove_widget(boardObj)
    
    def button_move(self, instance):
        shirokuroApp.screen_manager.current = "tablero"
        shirokuroApp.screen_manager.transition.direction = "right"
        
    def button_getHelp(self, instance):

        game.getHelp()
        self.removeCurrentBoard()
        
        if(game.isGamePassed()):

            chronometer.pause()
            game.computeScore2(game.numHelps(), chronometer.getCounter())
            
            """  Dado que te has pasado la partida, se hace un guardado en el currentSlot  """
            self.saveInJSON()
            
            if(not(shirokuroApp.screen_manager.has_screen(name="resultados"))):
                screen = Screen(name="resultados")
                screen.add_widget(ResumeDisplay())
                shirokuroApp.screen_manager.add_widget(screen)
            else:
                screen = shirokuroApp.root.get_screen('resultados')
                obj = screen.children[0]
                screen.remove_widget(obj)
                screen.add_widget(ResumeDisplay())
            
            shirokuroApp.screen_manager.current = "resultados"
            shirokuroApp.screen_manager.transition.direction = "left"
        
        else:
            #shirokuroApp.root.get_screen('tablero').add_widget(Board(id="board"))
            shirokuroApp.root.get_screen('tablero').add_widget(Board())
            shirokuroApp.screen_manager.current = "tablero"
            shirokuroApp.screen_manager.transition.direction = "right"

    def button_getPreviousState(self, instance):
        self.removeCurrentBoard()
        game.getPreviousState()
        #shirokuroApp.root.get_screen('tablero').add_widget(Board(id="board"))
        shirokuroApp.root.get_screen('tablero').add_widget(Board())
        shirokuroApp.screen_manager.current = "tablero"
        shirokuroApp.screen_manager.transition.direction = "right"
    
    def button_getNextState(self, instance):
        self.removeCurrentBoard()
        game.getNextState()
        #shirokuroApp.root.get_screen('tablero').add_widget(Board(id="board"))
        shirokuroApp.root.get_screen('tablero').add_widget(Board())
        shirokuroApp.screen_manager.current = "tablero"
        shirokuroApp.screen_manager.transition.direction = "right"
    
    def button_saveState(self, instance):
        game.saveState()
        shirokuroApp.screen_manager.current = "tablero"
        shirokuroApp.screen_manager.transition.direction = "right"
        
    def button_goSavedState(self, instance):
        game.goSavedState()
        self.removeCurrentBoard()
        #shirokuroApp.root.get_screen('tablero').add_widget(Board(id="board"))
        shirokuroApp.root.get_screen('tablero').add_widget(Board())
        shirokuroApp.screen_manager.current = "tablero"
        shirokuroApp.screen_manager.transition.direction = "right"
        
    def button_getOriginalSolution(self, instance):
        self.removeCurrentBoard()
        if(shirokuroApp.screen_manager.has_screen(name="solucion")):
            screen = shirokuroApp.root.get_screen('solucion')
            boardObj = screen.children[0]
            screen.remove_widget(boardObj)
            game.getOriginalSolution()
            screen.add_widget(solutionDisplay())
        else:
            game.getOriginalSolution()
            self.solution_display = solutionDisplay()
            screen = Screen(name="solucion")
            screen.add_widget(self.solution_display)
            shirokuroApp.screen_manager.add_widget(screen)

        self.saveInJSON()
        shirokuroApp.screen_manager.current = "solucion"
        shirokuroApp.screen_manager.transition.direction = "left"
        
    def button_getSolutionFromCurrentStatus(self, instance):
        self.removeCurrentBoard()
        if(shirokuroApp.screen_manager.has_screen(name="solucion")):
            screen = shirokuroApp.root.get_screen('solucion')
            boardObj = screen.children[0]
            screen.remove_widget(boardObj)
            game.getSolutionFromCurrentStatus()
            screen.add_widget(solutionDisplay())
        else:
            game.getSolutionFromCurrentStatus()
            self.solution_display = solutionDisplay()
            screen = Screen(name="solucion")
            screen.add_widget(self.solution_display)
            shirokuroApp.screen_manager.add_widget(screen)

        self.saveInJSON()
        shirokuroApp.screen_manager.current = "solucion"
        shirokuroApp.screen_manager.transition.direction = "left"
    
    def button_restartGame(self, instance):
        self.removeCurrentBoard()
        game.restartGame()
        #shirokuroApp.root.get_screen('tablero').add_widget(Board(id="board"))
        shirokuroApp.root.get_screen('tablero').add_widget(Board())
        shirokuroApp.screen_manager.current = "tablero"
        shirokuroApp.screen_manager.transition.direction = "right"
        
    def button_getAllSolutions(self, instance):
        self.removeCurrentBoard()
        if(shirokuroApp.screen_manager.has_screen(name="menuTodasSoluciones")):
            screen = shirokuroApp.root.get_screen('menuTodasSoluciones')
            boardObj = screen.children[0]
            screen.remove_widget(boardObj)
            game.getAllSolutions()
            game.getSolutionByInputNumber(0)
            screen.add_widget(allSolutionDisplay())
        else:
            game.getAllSolutions()
            game.getSolutionByInputNumber(0)
            self.allSolution_display = allSolutionDisplay()
            screen = Screen(name="menuTodasSoluciones")
            screen.add_widget(self.allSolution_display)
            shirokuroApp.screen_manager.add_widget(screen)

        self.saveInJSON()
        shirokuroApp.screen_manager.current = "menuTodasSoluciones"
        shirokuroApp.screen_manager.transition.direction = "left"
    
    def button_pause(self, instance):
        chronometer.pause()
        shirokuroApp.screen_manager.current = "tablero"
        shirokuroApp.screen_manager.transition.direction = "right"
        
    def button_resume(self, instance):
        chronometer.resume()
        shirokuroApp.screen_manager.current = "tablero"
        shirokuroApp.screen_manager.transition.direction = "right"
    
    def button_getTableSameMetrics(self, instance):
        self.removeCurrentBoard()
        game.getTableSameMetrics()
        #shirokuroApp.root.get_screen('tablero').add_widget(Board(id="board"))
        shirokuroApp.root.get_screen('tablero').add_widget(Board())
        chronometer.reset()
        shirokuroApp.screen_manager.current = "tablero"
        shirokuroApp.screen_manager.transition.direction = "right"
        
    def button_saveGame(self, instance):
                
        box = BoxLayout(orientation='vertical')
        buttons = BoxLayout()
        
        button_saveInCurrentSlot = Button(text="Save in current slot")
        button_saveInCurrentSlot.halign = 'center'
        button_saveInCurrentSlot.valign = 'middle'
        button_saveInCurrentSlot.bind(size=button_saveInCurrentSlot.setter('text_size'))
        button_saveInCurrentSlot.bind(on_press=partial(self.saveInSlot, "currentSlot"))
        
        button_saveInNewSlot = Button(text="Save in new slot")
        button_saveInNewSlot.halign = 'center'
        button_saveInNewSlot.valign = 'middle'
        button_saveInNewSlot.bind(size=button_saveInNewSlot.setter('text_size'))
        button_saveInNewSlot.bind(on_press=partial(self.saveInSlot, "newSlot"))
        
        buttons.add_widget(button_saveInCurrentSlot)
        buttons.add_widget(button_saveInNewSlot)
        
        box.add_widget(buttons)
        
        button_popSaveDataWindow = Button(text="Back")
        button_popSaveDataWindow.halign = 'center'
        button_popSaveDataWindow.valign = 'middle'
        button_popSaveDataWindow.bind(size=button_popSaveDataWindow.setter('text_size'))
        button_popSaveDataWindow.bind(on_press=self.popSaveDataWindow)
        box.add_widget(button_popSaveDataWindow)

        self.pop = Popup(title="Save game", content=box)
        self.pop.open()
    
    def popSaveDataWindow(self, instance):
        self.pop.dismiss()
    
    def saveInSlot(self, slot, instance):
        self.saveInJSON(slot)
        self.pop.dismiss()
    
    def saveInJSON(self, slot=None):
        saverObj.saveGameData(slot)
            
    def button_getGuideSolution(self, instance):
        chronometer.pause()
        self.removeCurrentBoard()
        idx = int(game.currentState())
        game.helpingLoop()
        self.saveInJSON()
        game.returnToGivenState(idx)
        
        if(shirokuroApp.screen_manager.has_screen(name="solucionGuiada")):
            screen = shirokuroApp.root.get_screen('solucionGuiada')
            boardObj = screen.children[0]
            screen.remove_widget(boardObj)
            screen.add_widget(guideSolutionDisplay())
        else:
            self.guideSolution_display = guideSolutionDisplay()
            screen = Screen(name="solucionGuiada")
            screen.add_widget(self.guideSolution_display)
            shirokuroApp.screen_manager.add_widget(screen)

        shirokuroApp.screen_manager.current = "solucionGuiada"
        shirokuroApp.screen_manager.transition.direction = "left"
    
    def button_getTableDifferentMetrics(self, instance):
        shirokuroApp.root.get_screen('defineMetricas').children[0].updateFromScreen(input_FromScreen="menuJugar")
        shirokuroApp.screen_manager.current = "defineMetricas"
        shirokuroApp.screen_manager.transition.direction = "left"
    
    def button_getInstructions(self, instance):
        shirokuroApp.root.get_screen('instrucciones').children[0].updateFromScreen(input_FromScreen="menuJugar")
        shirokuroApp.screen_manager.current = "instrucciones"
        shirokuroApp.screen_manager.transition.direction = "left"
        
    def button_loadGame(self, instance):
        if(not(shirokuroApp.screen_manager.has_screen(name="menuCargar"))):
            screen = Screen(name="menuCargar")
            screen.add_widget(loadMenu())
            shirokuroApp.screen_manager.add_widget(screen)
        else:
            screen = shirokuroApp.root.get_screen('menuCargar')
            loadMenuObj = screen.children[0]
            screen.remove_widget(loadMenuObj)
            screen.add_widget(loadMenu())
        shirokuroApp.root.get_screen('menuCargar').children[0].updateFromScreen(input_FromScreen="menuJugar")
        shirokuroApp.screen_manager.current = "menuCargar"
        shirokuroApp.screen_manager.transition.direction = "left"
        
    def button_solutionMenu(self, instance):
        chronometer.pause()
        self.removeCurrentBoard()
        if(not(shirokuroApp.screen_manager.has_screen(name="menuSolucion"))):
            screen = Screen(name="menuSolucion")
            screen.add_widget(solutionMenuDisplay(fromScreen="menuJugar"))
            shirokuroApp.screen_manager.add_widget(screen)
        else:
            screen = shirokuroApp.root.get_screen('menuSolucion')
            solutionMenuObj = screen.children[0]
            screen.remove_widget(solutionMenuObj)
            screen.add_widget(solutionMenuDisplay(fromScreen="menuJugar"))
        self.saveInJSON()
        shirokuroApp.screen_manager.current = "menuSolucion"
        shirokuroApp.screen_manager.transition.direction = "left"
    
    def button_leaveGame(self, instance):
        self.removeCurrentBoard()
        store.put('currentSlot', value=0)
        shirokuroApp.screen_manager.current = "menuPrincipal"
        shirokuroApp.screen_manager.transition.direction = "left"
    
class MyApp(App):
    
    """ Para desactivar el menu de desarrollador de F1 """
    def open_settings(self):
        pass

    def build(self):
        
        self.screen_manager = ScreenManager()
        
        self.main_menu = mainMenu()
        screen = Screen(name="menuPrincipal")
        screen.add_widget(self.main_menu)
        self.screen_manager.add_widget(screen)
        
        self.defineGame_menu = defineGameMenu()
        screen = Screen(name="defineMetricas")
        screen.add_widget(self.defineGame_menu)
        self.screen_manager.add_widget(screen)
        
        self.instructions_display = instructionsDisplay()
        screen = Screen(name="instrucciones")
        screen.add_widget(self.instructions_display)
        self.screen_manager.add_widget(screen)
        
        self.playMenu_display = playMenu()
        screen = Screen(name="menuJugar")
        screen.add_widget(self.playMenu_display)
        self.screen_manager.add_widget(screen)
        
        return self.screen_manager

if(os.path.isfile('./mySaves.json')):
    store = JsonStore('mySaves.json')
    store.put('currentSlot', value=0)
else:
    store = JsonStore('mySaves.json')
    store.put('lastSlot', value=0)
    store.put('currentSlot', value=0)
game = shirokuroGame()
loaderObj = loader()
saverObj = saver()
chronometer = Chrono()
shirokuroApp = MyApp()
 
if __name__ == '__main__':
    shirokuroApp.run()