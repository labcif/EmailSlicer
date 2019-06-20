import os
from java.lang import System
from java.util.logging import Level
from org.sleuthkit.datamodel import TskData
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.report import GeneralReportModuleAdapter
from org.sleuthkit.autopsy.report.ReportProgressPanel import ReportStatus
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.coreutils import PlatformUtil

from javax.swing import JTextArea
from javax.swing import JPanel
from javax.swing import JCheckBox
from javax.swing import JLabel
from javax.swing import BoxLayout
from java.awt import BorderLayout
from java.awt import Dimension
from java.awt import Font
from java.awt import GraphicsEnvironment
from javax.swing import JFrame
from javax.swing import BorderFactory
from javax.swing import JScrollPane
from javax.swing import JList
from javax.swing import JSpinner
from javax.swing import SpinnerListModel
from javax.swing import JComboBox
from java.lang import Runtime
from javax.swing import JComponent

import inspect
import subprocess
import shutil

FOLDER_PATH = "/ES_Temp"

def system(command):
    """system(command) -> exit_status

    Execute the command (a string) in a subshell."""
    Runtime.exec(command).exitValue()

# Class responsible for defining module metadata and logic
class EmailSlicerReportModule(GeneralReportModuleAdapter):

    moduleName = "EmailSlicer Report"
    _logger = None


    def log(self, level, msg):
        if self._logger is None:
            self._logger = Logger.getLogger(self.moduleName)
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def getName(self):
        return self.moduleName

    def getDescription(self):
        return "Report regarding extraction of emails from PST/OST files"

    def getRelativeFilePath(self):
        return "ES_" + Case.getCurrentCase().getName() + ".html"

    def createTempDir(self, dir):
        try:
            os.mkdir(self.temp_dir + dir)
        except:
            self.log(Level.INFO, "[ERROR] Directory '" + dir + "' already exists!")

    # TODO: Update this method to make a report
    # The 'baseReportDir' object being passed in is a string with the directory that reports are being stored in.   Report should go into baseReportDir + getRelativeFilePath().
    # The 'progressBar' object is of type ReportProgressPanel.
    #   See: http://sleuthkit.org/autopsy/docs/api-docs/4.6.0/classorg_1_1sleuthkit_1_1autopsy_1_1report_1_1_report_progress_panel.html
    def generateReport(self, baseReportDir, progressBar):

        # Open the output file.
        #fileName = os.path.join(baseReportDir, self.getRelativeFilePath())
        #report = open(fileName, 'w')
        
        # Query the database for the files (ignore the directories)
        sleuthkitCase = Case.getCurrentCase().getSleuthkitCase()
        files = sleuthkitCase.findAllFilesWhere("NOT meta_type = " + str(TskData.TSK_FS_META_TYPE_ENUM.TSK_FS_META_TYPE_DIR.getValue()))

        # Setup the progress bar
        progressBar.setIndeterminate(False)
        progressBar.start()
        #progressBar.setMaximumProgress(len(files))
        progressBar.setMaximumProgress(2)
        
        #Runtime.getRuntime().exec("python C:/Users/2151580/AppData/Roaming/autopsy/python_modules/EmailSlicerReportModule/write.py")
        
        self.temp_dir = Case.getCurrentCase().getTempDirectory()


        # Temp directory to store extracted files
        self.createTempDir(FOLDER_PATH)

        

        # Skip option
        skip = self.configPanel.getSkipEmailExtraction()

        # File to extract 
        selected = self.configPanel.cbSelectedItemWithPath()

        selected_name = self.configPanel.cbSelectedItem()
        selected_name = selected_name.replace(".pst", "") if selected_name.endswith(".pst") else selected_name.replace(".ost", "")

        #extractionWithPath = str(self.temp_dir + FOLDER_PATH + str(selected.replace(os.path.splitext(selected)[1], "")))
        #extractionWithPath = str(self.temp_dir + FOLDER_PATH + selected)
        #output = "C:/Users/2151580/Desktop/TestExtractFolderAutopsy/Temp/ES_TEST/output"

        reportName = (str("%s Report") % (selected_name))

        # Temp directory path to write extated emails
        output = (str(str(self.temp_dir + FOLDER_PATH).replace("\\", "/") + "/%s_output") % (selected_name))
        progressBar.increment()
        progressBar.updateStatusLabel("Extracting files")
        
        
        pythonModulesPath = PlatformUtil().getUserPythonModulesPath().replace("\\", "/")

        '''
        f = open("C:/Users/2151580/AppData/Roaming/autopsy/python_modules/EmailSlicerReportModule/demofile2.txt", "w")
        #f.write(str(self.temp_dir + FOLDER_PATH))
        f.write(test)
        f.close()
        '''
        
        try:
            proc = Runtime.getRuntime().exec(
                ("python3 %s/EmailSlicerReportModule/EmailSlicer/EmailSlicer.py %s %s %s %s") 
                    % (pythonModulesPath, selected, output, "-j 8", "-t \"%s\"") % (reportName))
        except:
            proc = Runtime.getRuntime().exec(
                ("python %s/EmailSlicerReportModule/EmailSlicer/EmailSlicer.py %s %s %s %s") 
                    % (pythonModulesPath, selected, output, "-j 8", "-t \"%s\"") % (reportName))
        finally:
            proc.waitFor()
            progressBar.increment()

        #'python3 EmailSlicer.py ../EmailSamples/ipleiria.pst output_files -j 8 -t "TESTE REPORT" -e "2151580@my.ipleiria.pt" "2161795@my.ipleiria.pt'
        
        '''
        for _file in files:
            #report.write(file.getUniquePath() + "\n")
            report.write(_file.getName() + "\n")
            progressBar.increment()
            progressBar.updateStatusLabel("Creating report(s)")
        '''

        #report.close()

        progressBar.increment()
        progressBar.updateStatusLabel("Reports created")
        shutil.copy(output + (("/%s1.html") % (reportName)), baseReportDir)
        shutil.copy(output + (("/%s2.html") % (reportName)), baseReportDir)

        # Add the report to the Case, so it is shown in the tree
        #Case.getCurrentCase().addReport(fileName, self.moduleName, "EmailSlicer test")
        Case.getCurrentCase().addReport(
            (baseReportDir + "/%s1.html") % (reportName), 
            self.moduleName, ((str("%s Report")) % (selected_name)))
        Case.getCurrentCase().addReport(
            (baseReportDir + "/%s2.html") % (reportName), 
            self.moduleName, ((str("%s Report")) % (selected_name)))
        #Case.getCurrentCase().addReport(output + "/TEST REPORT1.html", self.moduleName, "EmailSlicer Report")
        #Case.getCurrentCase().addReport(output + "/TEST REPORT2.html", self.moduleName, "EmailSlicer Report")
        

        progressBar.complete(ReportStatus.COMPLETE)

    
    def getConfigurationPanel(self):
        self.configPanel = EmailSlicerReportModuleConfigPanel()
        return self.configPanel

class EmailSlicerReportModuleConfigPanel(JPanel):
    
    skipEmailExtraction = True
    cbSkipEmailExtraction = None
    
    def __init__(self):
        self.initComponents()

    def getSkipEmailExtraction(self):
        return self.skipEmailExtraction

    def initComponents(self):
        
        self.setLayout(BoxLayout(self, BoxLayout.Y_AXIS))
        self.setAlignmentX(JComponent.LEFT_ALIGNMENT)
        self.panel = JPanel()
        self.panel.setLayout(BoxLayout(self.panel, BoxLayout.Y_AXIS))
        self.panel.setAlignmentY(JComponent.LEFT_ALIGNMENT)
        self.emptyLabel0 = JLabel(" ")
        self.emptyLabel1 = JLabel(" ")
        self.emptyLabel2 = JLabel(" ")
        self.labelQuery = JLabel("Query (Separated by \",\")")
        #self.panel.add(self.checkbox)
        self.panel.add(self.emptyLabel0)
        #self.panel.add(self.emptyLabel1)
        #self.panel.add(self.emptyLabel2)
        #self.panel.add(self.labelQuery)
        #self.panel.add(self.label4)

       




        sleuthkitCase = Case.getCurrentCase().getSleuthkitCase()
        #files = sleuthkitCase.findAllFilesWhere("NOT meta_type = " + str(TskData.TSK_FS_META_TYPE_ENUM.TSK_FS_META_TYPE_REG.getValue()))
        files = sleuthkitCase.findAllFilesWhere("NOT meta_type = " + str(TskData.TSK_FS_META_TYPE_ENUM.TSK_FS_META_TYPE_DIR.getValue()))
        pstFiles = []
        pstFilesWithPath = []

        for _file in files:
            if _file.getName().endswith(".pst") or _file.getName().endswith(".ost"):
                #pstFiles.append(_file.getName()) 
                pstFiles.append(_file.getName()) 
                #pstFilesWithPath.append(_file.getUniquePath()) 
                pstFilesWithPath.append(_file.getLocalPath()) 
        
        self.cbData = pstFiles
        self.cbDataWithPath = pstFilesWithPath
        
       

        # ComboBox label
        self.label = JLabel('Select a file (OST/PST)')
        self.panel.add(self.label, BorderLayout.LINE_START)

        # ComboBox items
        self.cb = JComboBox(self.cbData)
        self.panel.add(self.cb)
        self.panel.add(self.emptyLabel1)

        # Skip email extraction
        self.cbSkipEmailExtraction = JCheckBox("Skip email extraction", actionPerformed=self.cbSkipEmailExtractionActionPerformed)
        self.cbSkipEmailExtraction.setSelected(True)
        self.panel.add(self.cbSkipEmailExtraction)
        self.panel.add(self.emptyLabel2)

        self.panel.add(self.labelQuery)
        self.area = JTextArea(5,25)
        #self.area.getDocument().addDocumentListener(self.area)
        #self.area.addKeyListener(listener)
        self.area.setBorder(BorderFactory.createEmptyBorder(0, 0, 0, 0))
        self.pane = JScrollPane()
        self.pane.getViewport().add(self.area)
        #self.pane.addKeyListener(self.area)
        #self.add(self.area)
        self.panel.add(self.pane)
        #self.add(self.pane)
        self.add(self.panel)


    def cbSkipEmailExtractionActionPerformed(self, event):
        self.skipEmailExtraction = event.getSource().isSelected()

    def cbSelectedItem(self):
        return self.cbData[self.cb.selectedIndex]
    
    def cbSelectedItemWithPath(self):
        return self.cbDataWithPath[self.cb.selectedIndex]
        #selected = self.cb.selectedIndex
        #if selected >= 0:
        #    data = self.data[selected]
        #    self.label.text = data + " selected"
    