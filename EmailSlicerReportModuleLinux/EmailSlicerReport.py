import os
from java.lang import System
from java.util.logging import Level
import java.nio.file.Paths
from org.sleuthkit.datamodel import TskData
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.report import GeneralReportModuleAdapter
from org.sleuthkit.autopsy.report.ReportProgressPanel import ReportStatus
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.coreutils import PlatformUtil
import org.sleuthkit.datamodel.BlackboardArtifact
import org.sleuthkit.datamodel.BlackboardAttribute
import org.sleuthkit.autopsy.casemodule.services.Blackboard
import org.sleuthkit.autopsy.casemodule.services.FileManager
import jarray
import inspect
import os
import time
from subprocess import Popen, PIPE

from java.lang import Class
from java.lang import System
from java.sql import DriverManager, SQLException
from java.util.logging import Level
from java.io import File
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.coreutils import PlatformUtil
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.datamodel import ContentUtils
from org.sleuthkit.datamodel import CommunicationsManager
from org.sleuthkit.datamodel import Relationship
from org.sleuthkit.datamodel import Account


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

    services = IngestServices.getInstance()
    moduleName = "EmailSlicer Report"
    dirName = "ES"
    _logger = Logger.getLogger(moduleName)
    #_logger.log(Level.SEVERE, "Starting of report")

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__,
                          inspect.stack()[1][3], msg)

    def getName(self):
        return self.moduleName

    def getDirName(self):
        return self.dirName

    def getDescription(self):
        return "Report regarding extraction of emails from PST/OST files"

    def getRelativeFilePath(self):
        return "ES_" + Case.getCurrentCase().getName() + ".html"

    def createTempDir(self, dir):
        try:
            os.mkdir(self.temp_dir + dir)
        except:
            self.log(Level.INFO, "[ERROR] Directory '" +
                     dir + "' already exists!")

    def createDir(self, dir):
        try:
            os.mkdir(dir)
        except:
            self.log(Level.INFO, "[ERROR] Directory '" +
                     dir + "' already exists!")

    # TODO: Update this method to make a report
    # The 'baseReportDir' object being passed in is a string with the directory that reports are being stored in.   Report should go into baseReportDir + getRelativeFilePath().
    # The 'progressBar' object is of type ReportProgressPanel.
    #   See: http://sleuthkit.org/autopsy/docs/api-docs/4.6.0/classorg_1_1sleuthkit_1_1autopsy_1_1report_1_1_report_progress_panel.html
    def generateReport(self, baseReportDir, progressBar):
        #start_time = time.time()
        # we don't know how much work there is yet
        # progressBar.switchToIndeterminate()

        # Open the output file.
        #fileName = os.path.join(baseReportDir, self.getRelativeFilePath())
        #report = open(fileName, 'w')

         # File to extract
        try:
            selected = self.configPanel.cbSelectedItemWithPath()
            selected_name = self.configPanel.cbSelectedItem()
            selected_name = selected_name.replace(".pst", "") if selected_name.endswith(
                ".pst") else selected_name.replace(".ost", "")
        except:
            selected = ""
            selected_name = ""

        # Query the database for the files (ignore the directories)
        # get current case and the store.vol abstract file information
        #skc = Case.getCurrentCase().getServices().getBlackboard()
        sleuthkitCase = Case.getCurrentCase().getSleuthkitCase()

        # Setup the progress bar
        progressBar.setIndeterminate(False)
        progressBar.start()
        # progressBar.setMaximumProgress(len(files))
        progressBar.setMaximumProgress(3)

        #Runtime.getRuntime().exec("python C:/Users/2151580/AppData/Roaming/autopsy/python_modules/EmailSlicerReportModule/write.py")

        self.temp_dir = Case.getCurrentCase().getTempDirectory()

        # Temp directory to store extracted files
        self.createTempDir(FOLDER_PATH)

        # Skip option
        skip = self.configPanel.getSkipEmailExtraction()

        #extractionWithPath = str(self.temp_dir + FOLDER_PATH + str(selected.replace(os.path.splitext(selected)[1], "")))
        #extractionWithPath = str(self.temp_dir + FOLDER_PATH + selected)
        #output = "C:/Users/2151580/Desktop/TestExtractFolderAutopsy/Temp/ES_TEST/output"

        reportName = (str("%s Report") % (selected_name))

        # Temp directory path to write extated emails
        output = (str(str(self.temp_dir + FOLDER_PATH).replace("\\",
                                                               "/") + "/%s_output") % (selected_name))
        
        pythonModulesPath = PlatformUtil().getUserPythonModulesPath().replace("\\", "/")
        
        

        progressBar.increment()
        progressBar.updateStatusLabel("Extracting files")

        proc = Runtime.getRuntime().exec(
            ("python3 %s/EmailSlicerReportModuleLinux/EmailSlicer/EmailSlicer.py %s %s %s %s")
            % (pythonModulesPath, selected, output, "-j 8", "-t \"%s\"") % (reportName))
    
        proc.waitFor()
        progressBar.increment()
        progressBar.updateStatusLabel("Adding artifacts to blackboard")

        for dbFile in os.listdir(output):
            if dbFile.endswith('.db'):
                dbPath = os.path.join(output, dbFile)
                #self.log(Level.INFO, "Path to the mail database is ==> " + lclDbPath)
                try:
                    Class.forName("org.sqlite.JDBC").newInstance()
                    dbConn = DriverManager.getConnection(
                        "jdbc:sqlite:%s" % dbPath)
                except SQLException as e:
                    #self.log(Level.INFO, "Could not open database file (not SQLite) " + lclDbPath + " (" + e.getMessage() + ")")
                    return IngestModule.ProcessResult.OK
                finally:
                    break

        # should only be one
        pureFile = self.configPanel.cbSelectedPureFiles()
        self.processEmails(dbConn, sleuthkitCase, pureFile)

        #'python3 EmailSlicer.py ../EmailSamples/ipleiria.pst output_files -j 8 -t "TESTE REPORT" -e "2151580@my.ipleiria.pt" "2161795@my.ipleiria.pt'

        # For testing
        '''
        for _file in files:
            #report.write(file.getUniquePath() + "\n")
            report.write(_file.getName() + "\n")
            progressBar.increment()
            progressBar.updateStatusLabel("Creating report(s)")
        '''

        # report.close()

        try:
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
        except:
            pass

        progressBar.complete(ReportStatus.COMPLETE)

        """
        end_time = time.time()
        execution_time = end_time - start_time
        msg = ('Execution time: {} ({} min)'
            .format(execution_time, execution_time/60))
        f = open("C:/Users/2151580/AppData/Roaming/autopsy/python_modules/EmailSlicerReportModule/time.txt", "w")
        #f.write(str(self.temp_dir + FOLDER_PATH))
        f.write(msg)
        f.close()
        """

    def processEmails(self, dbConn, skCase, file):

        query = '''
            SELECT 
                relations.email_id as EMAIL_ID,
                se.id as SENDER_USER_ID, 
                se.email as TSK_EMAIL_FROM, 
                re.email as TSK_EMAIL_TO, 
                e.subject as TSK_SUBJECT, 
                e.body as TSK_EMAIL_CONTENT_PLAIN, 
                e.date as TSK_DATETIME_RCVD, 
                e.location as TSK_PATH
            FROM relations 
                JOIN users s ON s.id = relations.sender_user_id
                JOIN users r ON r.id = relations.receiver_user_id 
                JOIN users_emails se ON r.email_id = re.id
                JOIN users_emails re ON s.email_id = se.id
                JOIN emails e ON e.id = relations.email_id;
        '''

        #self.log(Level.INFO, "SQL Statement ==> ")
        # Query the contacts table in the database and get all columns.
        try:
            stmt = dbConn.createStatement()
            resultSet = stmt.executeQuery(query)
            #self.log(Level.INFO, "query message table")
        except SQLException as e:
            #self.log(Level.INFO, "Error querying database for message table (" + e.getMessage() + ")")
            #return IngestModule.ProcessResult.OK
            pass

        artIdEmail = skCase.getArtifactTypeID("TSK_EMAIL_MSG")
        artIdEmailType = skCase.getArtifactType("TSK_EMAIL_MSG")

        prevEmailID = ""
        currEmailID = ""
        prevSender = ""
        receivers = []
        otherAccounts = []

        # Cycle through each row and create artifacts
        while resultSet.next():
            
            try:

                currEmailID = resultSet.getString("EMAIL_ID")
                currSender = resultSet.getString("TSK_EMAIL_FROM")
                currReceiver = resultSet.getString("TSK_EMAIL_TO")

                prevSenderAccount = self.getAccount(skCase, file, prevSender)
                
                if prevEmailID == "" or prevEmailID == currEmailID:

                    receivers.append(currReceiver)
                    otherAccounts.append(self.getAccount(skCase, file, currReceiver))

                else:

                    receivers = ", ".join(receivers)

                    artEmail = file.newArtifact(artIdEmail)
                    artEmail.addAttributes((
                        (BlackboardAttribute(
                            BlackboardAttribute.ATTRIBUTE_TYPE.TSK_PATH.getTypeID(), self.getName(), resultSet.getString("TSK_PATH"))),
                        (BlackboardAttribute(
                            BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_TO.getTypeID(), self.getName(), receivers)),
                        (BlackboardAttribute(
                            BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_FROM.getTypeID(), self.getName(), prevSender)),
                        (BlackboardAttribute(
                            BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_CONTENT_PLAIN.getTypeID(), self.getName(), resultSet.getString("TSK_EMAIL_CONTENT_PLAIN")
                        )),
                        (BlackboardAttribute(
                            BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME_RCVD.getTypeID(), self.getName(), resultSet.getInt("TSK_DATETIME_RCVD")
                        )),
                        (BlackboardAttribute(
                            BlackboardAttribute.ATTRIBUTE_TYPE.TSK_SUBJECT.getTypeID(), self.getName(), resultSet.getString("TSK_SUBJECT")
                        ))))

                    skCase.getCommunicationsManager().addRelationships(prevSenderAccount, otherAccounts, artEmail, Relationship.Type.MESSAGE, resultSet.getInt("TSK_DATETIME_RCVD"))
                    
                    try:

                        # index the artifact for keyword search
                        blackboard.indexArtifact(artEmail)
        
                    except:
                        pass

                    finally:
                        receivers = []
                        otherAccounts = []
                        
                        receivers.append(currReceiver)
                        otherAccounts.append(self.getAccount(skCase, file, currReceiver))                    
                
                prevEmailID = currEmailID
                prevSender = currSender

            except SQLException as e:
                self.log(
                    Level.INFO, "Error getting values from message table (" + e.getMessage() + ")")
        
        # Fire an event to notify the UI and others that there is a new artifact  
        IngestServices.getInstance().fireModuleDataEvent(
            ModuleDataEvent(self.getName(), artIdEmailType, None))
        
        # Close the database statement
        stmt.close()    


    def getAccount(self, skCase, _file, emailAddress):

        return skCase.getCommunicationsManager().createAccountFileInstance(Account.Type.EMAIL, emailAddress, self.getName(), _file)
   

    def getConfigurationPanel(self):

        self.configPanel = EmailSlicerReportModuleConfigPanel()
        return self.configPanel



class EmailSlicerReportModuleConfigPanel(JPanel):

    skipEmailExtraction = False
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
        self.panel.add(self.emptyLabel0)


        sleuthkitCase = Case.getCurrentCase().getSleuthkitCase()
        #files = sleuthkitCase.findAllFilesWhere("NOT meta_type = " + str(TskData.TSK_FS_META_TYPE_ENUM.TSK_FS_META_TYPE_REG.getValue()))
        files = sleuthkitCase.findAllFilesWhere(
            "NOT meta_type = " + str(TskData.TSK_FS_META_TYPE_ENUM.TSK_FS_META_TYPE_DIR.getValue()))
        pstFiles = []
        pstFilesWithPath = []
        pureFiles = []
        for _file in files:
            if _file.getName().endswith(".pst") or _file.getName().endswith(".ost"):
                # pstFiles.append(_file.getName())
                pstFiles.append(_file.getName())
                # pstFilesWithPath.append(_file.getUniquePath())
                pstFilesWithPath.append(_file.getLocalPath())
                pureFiles.append(_file)

        self.cbData = pstFiles
        self.cbDataWithPath = pstFilesWithPath
        self.cbPureFiles = pureFiles

        # ComboBox label
        self.label = JLabel('Select a file (OST/PST)')
        self.panel.add(self.label, BorderLayout.LINE_START)

        # ComboBox items
        self.cb = JComboBox(self.cbData)
        self.panel.add(self.cb)
        #self.panel.add(self.emptyLabel1)

        # Skip email extraction
        #self.cbSkipEmailExtraction = JCheckBox(
        #    "Skip email extraction", actionPerformed=self.cbSkipEmailExtractionActionPerformed)
        #self.cbSkipEmailExtraction.setSelected(False)
        #self.panel.add(self.cbSkipEmailExtraction)
        #self.panel.add(self.emptyLabel2)

        #self.panel.add(self.labelQuery)
        #self.area = JTextArea(5, 25)
        # self.area.getDocument().addDocumentListener(self.area)
        # self.area.addKeyListener(listener)
        #self.area.setBorder(BorderFactory.createEmptyBorder(0, 0, 0, 0))
        #self.pane = JScrollPane()
        #self.pane.getViewport().add(self.area)
        # self.pane.addKeyListener(self.area)
        # self.add(self.area)
        #self.panel.add(self.pane)
        # self.add(self.pane)
        if len(pstFiles):
            self.add(self.panel)

    def cbSkipEmailExtractionActionPerformed(self, event):
        self.skipEmailExtraction = event.getSource().isSelected()

    def cbSelectedItem(self):
        if self.cb.selectedIndex >= 0:
            return self.cbData[self.cb.selectedIndex]
    
    def cbSelectedPureFiles(self):
        if self.cb.selectedIndex >= 0:
            return self.cbPureFiles[self.cb.selectedIndex]

    def cbSelectedItemWithPath(self):
        if self.cb.selectedIndex >= 0:
            return self.cbDataWithPath[self.cb.selectedIndex]
        #selected = self.cb.selectedIndex
        # if selected >= 0:
        #    data = self.data[selected]
        #    self.label.text = data + " selected"
