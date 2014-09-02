# -*- coding: utf-8 -*-
"""
    GROM.PDB_tableview
    ~~~~~~~~~~~~~

    Custom  TableView

    :copyright: (c) 2014 by Hovakim Grabski.
    :license: GPL, see LICENSE for more details.
"""""


from PyQt5.QtCore import (Qt, QFileInfo)
#from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QTableView, QFileDialog)


try:
    from PyQt5.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QString = str

import PDB_parse
import pdb_model_0_88 as pdb_model
from undoCommands import * #CommandRename, CommandAddRow,CommandRemoveRow
import frTableEdit

(ATOM, serial, name, resName,
 ChainID, resNum,X,Y,Z, occupancy, charge, element) = range(12)


def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True




class TableEdit(QTableView):


    def __init__(self, filename= '', parent=None):
        """
        Method defines  Custom QTableView
        Args:
             filename (str) file to oepn if there is any
        """
        super(TableEdit, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.filename = filename
        print("self.filename at start is ",self.filename)
        self.setWindowTitle(QFileInfo(self.filename).fileName())

        #: Create Model Instant
        self.model = pdb_model.PDBTableModel(filename)
        #: sets model
        self.setModel(self.model)
        self.delegate = pdb_model.PDBDelegate(self)
        self.setItemDelegate(self.delegate)

        self.clicked.connect(self.updateSelectionValues)

        self.undo_Stack = self.delegate.undoStack

        #: Create Search Instance for this Widget
        self.frTableObject = frTableEdit.frTableObject(self)

    def updateSelectionValues(self):
        values = self.selectedIndexes()[0]
        row = values.row()
        column  = values.column()
        self.frTableObject.updateCurrentSelectionDown(row,column)
        self.frTableObject.updateCurrentSelectionUp(row,column)


    def updateToZero(self):
        self.frTableObject.updateCurrentSelectionUp(0,0)
        self.frTableObject.updateCurrentSelectionDown(0,0)

    def setSearchTextValue(self,val1,val2):
        self.frTableObject.setFindVal(val1,val2)

    def getSearchTextValue(self):
        return  self.frTableObject.getFindText()

    def upMove(self):
        self.frTableObject.upSearch()

    def downMove(self):
        self.frTableObject.downSearch()

    def findAll(self,findText):
        self.frTableObject.findAllItems(findText)


    def updateSearchText(self):
        self.frTableObject.updateTextContent()

    def search(self,findText,replaceText,syntaxCombo = None,caseCheckBox = False,wholeCheckBox = False):
        self.frTableObject.search(findText,replaceText,syntaxCombo)



    def replaceAll(self,findText,replaceAllText,syntaxCombo = None,caseCheckBox = False,wholeCheckBox = False):
        self.frTableObject.findAllItems(findText)
        indexes = self.selectedIndexes()
        indexes = self.selectedIndexes()
        command = CommandRename(self, self.model, indexes,replaceAllText,
                             "Multirename values")
        self.undo_Stack.push(command)
        self.clearSelection()








    def replace(self,value,syntaxCombo = None,caseCheckBox = False,wholeCheckBox = False): #this one needs to add a lot
        indexes = self.selectedIndexes()
        command = CommandRename(self, self.model, indexes,value,
                             "Multirename values")
        self.undo_Stack.push(command)
        self.clearSelection()


    def multi_rename(self,value): #this one needs to add a lot
        indexes = self.selectedIndexes()
        command = CommandRename(self, self.model, indexes,value,
                             "Multirename values",tableAdress = self)
        self.undo_Stack.push(command)

    def editCut(self):
        self.data_copy= self.buffer_temp()
        command = CommandCut(self.model,self.data_copy,'',
                             "Cut value",tableAdress = self)
        self.undo_Stack.push(command)





    def editPaste(self):
        self.to_modify = self.buffer_temp()


        command = CommandPaste(self.model,self.data_copy,self.to_modify,
                             "Paste value",tableAdress = self)
        self.undo_Stack.push(command)

    def getModel(self):
        return self.model




    def undo(self):
        print("undo man")
        self.undo_Stack.undo()


    def redo(self):
        self.undo_Stack.redo()


    def  AddRow(self,rows):
        command = CommandAddRow(self, self.model, rows,
                             "Add Row")
        self.undo_Stack.push(command)


    def RemoveRow(self,rows):
        command = CommandRemoveRow(self, self.model, rows,
                             "Remove Row")
        self.undo_Stack.push(command)
        #self.resizeColumns()



    def initialLoad(self):
        try:
            self.model.load(self.filename)
            self.frTableObject.rowCount = self.model.rowCount()
            self.model.endResetModel()
            self.model.dirty = False
        except IOError as e:
            QMessageBox.warning(self, "PDB file load  - Error",
                    "Failed to load: {}".format(e))
        self.resizeColumns()

    def resizeColumns(self):
        self.resizeColumnsToContents()



    def editCopy(self):
        self.data_copy= self.buffer_temp()

    #: This function hasn't been implemented yet
    def ResNumFixer(self):
        ''' Need to make comparison between ATOM Names
        '''
        rows = self.model.rowCount()
        cols = self.model.columnCount()
        #print('rows ',rows)
        #print('columns ',cols)
        res_now = 1
        temp_name = self.model.PDB_rows[0].access[2]
        temp_resName = self.model.PDB_rows[0].access[3]
        temp_resNum = self.model.PDB_rows[0].access[5]



    #: Function copies indexes and its values
    def buffer_temp(self):
        data = []
        for item in self.selectedIndexes():
                row =  int(item.row())
                column = int(item.column())
                color_data = None
                item_val = self.model.PDB_rows[row].access[column]
                if column == 0:
                    color_data = self.model.PDB_rows[row].ATOM_TextColor
                elif column == 4:
                    color_data = self.model.PDB_rows[row].ChainID_color
                elif column == 5:
                    color_data = self.model.PDB_rows[row].resNum_color
                data.append([[row,column,item],[item_val,color_data]])
        return data



    def save(self):
        try:
            if 'Untitled' in self.filename:
                filename = QFileDialog.getSaveFileName(self,
                        "GROM Editor -- Save File ", self.filename,
                        "MD files (*.pdb *.*)")
                if len(filename[0]) == 0:
                    return
                self.filename = filename[0]
                #Now need to extract the data and save it
            self.model.save(self.filename)
        except Exception as e:
            print("Coudn't save ",e)


    def saveAs(self):
        try:
            filename = QFileDialog.getSaveFileName(self,
                    "GROM Editor -- Save File ", self.filename,
                    "MD files (*.pdb *.*)")
            if len(filename[0]) == 0:
                return
            self.filename = filename[0]
            print('self.filename is ',self.filename)
            #Now need to extract the data and save it
            self.setWindowTitle(QFileInfo(self.filename).fileName())
            self.model.save(self.filename)
        except Exception as e:
            print("Coudn't save ",e)


