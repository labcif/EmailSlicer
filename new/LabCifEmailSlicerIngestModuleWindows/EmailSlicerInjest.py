# Sample module in the public domain. Feel free to use this as a template
# for your modules (and you can remove this header and take complete credit
# and liability)
#
# Contact: Brian Carrier [carrier <at> sleuthkit [dot] org]
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# Simple data source-level ingest module for Autopsy.
# Search for TODO for the things that you need to change
# See http://sleuthkit.org/autopsy/docs/api-docs/4.6.0/index.html for documentation

from org.sleuthkit.datamodel import TskData
from java.lang import Runtime
from org.sleuthkit.autopsy.coreutils import PlatformUtil
import os, base64
import datetime
import re
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.datamodel import Relationship
from org.sleuthkit.datamodel import Account
import json
import subprocess, sys
from java.io import StringWriter, FileReader, ByteArrayOutputStream
from javax.script import ScriptEngineManager, SimpleScriptContext
import mailparser
from org.sleuthkit.autopsy.report.ReportProgressPanel import ReportStatus

from java.sql import DriverManager, SQLException
import jarray
import inspect
from java.lang import System
from java.util.logging import Level
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import FileIngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleContentEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.casemodule.services import Blackboard
from java.lang import Class

FOLDER_PATH = "/LabCifEmailSlicer"

# Factory that defines the name and details of the module and allows Autopsy
# to create instances of the modules that will do the analysis.
# TODO: Rename this to something more specific. Search and replace for it because it is used a few times
class EmailSlicerDataSourceIngestModuleFactory(IngestModuleFactoryAdapter):

    # TODO: give it a unique name.  Will be shown in module list, logs, etc.
    moduleName = "LabCif - Email Slicer"

    def getModuleDisplayName(self):
        return self.moduleName

    # TODO: Give it a description
    def getModuleDescription(self):
        return "Module regarding extraction of emails from PST/OST files and indexing EML/MSG files."

    def getModuleVersionNumber(self):
        return "1.2"

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, ingestOptions):
        # TODO: Change the class name to the name you'll make below
        return EmailSlicerDataSourceIngestModule()


# Data Source-level ingest module.  One gets created per data source.
# TODO: Rename this to something more specific. Could just remove "Factory" from above name.
class EmailSlicerDataSourceIngestModule(DataSourceIngestModule):

    _logger = Logger.getLogger(EmailSlicerDataSourceIngestModuleFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)


    def __init__(self):
        self.context = None


    def createTempDir(self, dir):
        try:
            os.mkdir(self.tempDir + dir)
        except:
            self.log(Level.INFO, "Directory '" + dir + "' already exists!")


    def getName(self):
        return EmailSlicerDataSourceIngestModuleFactory.moduleName


    def manageAttachments(self, attachments, file):
        files = []
        for att in attachments:
            fileManager = Case.getCurrentCase().getServices().getFileManager()
            df = fileManager.addDerivedFile(att['fn'], att['rp'], att['sz'], 0, 0, 0, 0, True, file, "", self.getName(), EmailSlicerDataSourceIngestModuleFactory().getModuleVersionNumber(), "")
            files.append(df)
        return files


    # Where any setup and configuration is done
    # 'context' is an instance of org.sleuthkit.autopsy.ingest.IngestJobContext.
    # See: http://sleuthkit.org/autopsy/docs/api-docs/4.6.0/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_ingest_job_context.html
    # TODO: Add any setup code that you need here.
    def startUp(self, context):
        
        # Throw an IngestModule.IngestModuleException exception if there was a problem setting up
        # raise IngestModuleException("Oh No!")
        self.context = context

        self.tempDir = Case.getCurrentCase().getModuleDirectory() #getTempDirectory()

        self.createTempDir(FOLDER_PATH)

        self.skCase = Case.getCurrentCase().getSleuthkitCase()

        # Use blackboard class to index blackboard artifacts for keyword search
        self.blackboard = Case.getCurrentCase().getServices().getBlackboard()

        self.pythonModulesPath = PlatformUtil().getUserPythonModulesPath().replace("\\", "/")


    # Where the analysis is done.
    # The 'dataSource' object being passed in is of type org.sleuthkit.datamodel.Content.
    # See: http://www.sleuthkit.org/sleuthkit/docs/jni-docs/4.6.0/interfaceorg_1_1sleuthkit_1_1datamodel_1_1_content.html
    # 'progressBar' is of type org.sleuthkit.autopsy.ingest.DataSourceIngestModuleProgress
    # See: http://sleuthkit.org/autopsy/docs/api-docs/4.6.0/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_data_source_ingest_module_progress.html
    # TODO: Add your analysis code in here.
    def process(self, dataSource, progressBar):

        # we don't know how much work there is yet
        ###progressBar.switchToIndeterminate()
        # Setup the progress bar
        ###progressBar.setIndeterminate(True)
        ###progressBar.start()
        # progressBar.setMaximumProgress(len(files))

        # For our example, we will use FileManager to get all
        # files with the word "test"
        # in the name and then count and read them
        # FileManager API: http://sleuthkit.org/autopsy/docs/api-docs/4.6.0/classorg_1_1sleuthkit_1_1autopsy_1_1casemodule_1_1services_1_1_file_manager.html
        
        fileManager = Case.getCurrentCase().getServices().getFileManager()
        
        pstFiles = fileManager.findFiles(dataSource, "%.pst%")
        ostFiles = fileManager.findFiles(dataSource, "%.ost%")
        emlFiles = fileManager.findFiles(dataSource, "%.eml%")
        msgFiles = fileManager.findFiles(dataSource, "%.msg%")

        numFiles = int(len(pstFiles) + len(ostFiles) + len(emlFiles) + len(msgFiles))
        ###progressBar.setMaximumProgress(4)
        
        self.log(Level.INFO, "found " + str(numFiles) + " files")
        ###progressBar.switchToDeterminate(numFiles)
        
        ### Processing email files

        ###progressBar.increment()
        ###progressBar.updateStatusLabel("Processing PST files")
        self.processPstOstEmails(self.skCase, pstFiles)

        self.processPstOstEmails(self.skCase, ostFiles)

        ###progressBar.increment()
        ###progressBar.updateStatusLabel("Processing EML files")
        self.processEmlEmails(self.skCase, emlFiles)
        
        ###progressBar.increment()
        ###progressBar.updateStatusLabel("Processing MSG files")
        self.processMsgEmails(self.skCase, msgFiles)

        ### Processing email files

        # Update the progress bar
        #progressBar.complete(ReportStatus.COMPLETE)

        #Post a message to the ingest messages in box.
        message = IngestMessage.createMessage(IngestMessage.MessageType.DATA,
            "LabCif - EmailSlicer Data Source Ingest Module", "Found %d files" % numFiles)
        IngestServices.getInstance().postMessage(message)

        return IngestModule.ProcessResult.OK


    def processPstOstEmails(self, skCase, pstFiles):

        for singleFile in pstFiles:

            # Temp directory path to write extated emails
            output = (str(str(self.tempDir + FOLDER_PATH).replace("\\", "/") + "/%s_output") % (singleFile.getName()))
            output = re.sub(r'\s+', '', output)

            try:
                proc = Runtime.getRuntime().exec(
                    ("python3 %s/LabCifEmailSlicerIngestModuleWindows/EmailSlicer/EmailSlicer.py %s %s %s %s %s")
                    % (self.pythonModulesPath, singleFile.getLocalPath(), output, "-j 8", "-t \"%s\"", "-o") % (""))
            except:
                proc = Runtime.getRuntime().exec(
                    ("py %s/LabCifEmailSlicerIngestModuleWindows/EmailSlicer/EmailSlicer.py %s %s %s %s %s")
                    % (self.pythonModulesPath, "\"" +singleFile.getLocalPath() + "\"", output, "-j 8", "-t \"%s\"", "-o") % (""))
            finally:
                proc.waitFor()
                ###progressBar.increment()
                ###progressBar.updateStatusLabel("Adding artifacts to blackboard")
            
            for dbFile in os.listdir(output):
                if dbFile.endswith('.db'):
                    dbPath = os.path.join(output, dbFile)
                    #self.log(Level.INFO, "Path to the mail database is ==> " + lclDbPath)
                    try:
                        Class.forName("org.sqlite.JDBC").newInstance()
                        dbConn = DriverManager.getConnection("jdbc:sqlite:%s" % dbPath)
                    except SQLException:
                        #self.log(Level.INFO, "Could not open database file (not SQLite) " + lclDbPath + " (" + e.getMessage() + ")")
                        return IngestModule.ProcessResult.OK
                    finally:
                        break

            query = '''
                SELECT 
                    relations.email_id as EMAIL_ID,
                    se.id as SENDER_USER_ID, 
                    se.email as TSK_EMAIL_FROM, 
                    re.email as TSK_EMAIL_TO, 
                    e.subject as TSK_SUBJECT, 
                    e.body as TSK_PLAIN, 
                    e.body_html as TSK_HTML, 
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
            except SQLException:
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

                    prevSenderAccount = self.getAccount(skCase, singleFile, prevSender)
                    
                    if prevEmailID == "" or prevEmailID == currEmailID:

                        receivers.append(currReceiver)
                        otherAccounts.append(self.getAccount(skCase, singleFile, currReceiver))

                    else:

                        receivers = ", ".join(receivers)

                        path = resultSet.getString("TSK_PATH")

                        """
                        fileManager = Case.getCurrentCase().getServices().getFileManager()
                        df = fileManager.addDerivedFile(
                            "teste", 
                            path, 
                            long(os.path.getsize(path)), 
                            long(os.path.getctime(path)), 
                            long(os.path.getctime(path)), 
                            long(os.path.getatime(path)), 
                            long(os.path.getmtime(path)), 
                            True,
                            singleFile, 
                            "", 
                            self.getName(), 
                            EmailSlicerDataSourceIngestModuleFactory().getModuleVersionNumber(), 
                            "")#TskData.EncodingType.NONE)

                        artEmail = df.newArtifact(artIdEmail)
                        """

                        artEmail = singleFile.newArtifact(artIdEmail)
                        artEmail.addAttributes((
                            (BlackboardAttribute(
                                BlackboardAttribute.ATTRIBUTE_TYPE.TSK_PATH.getTypeID(), self.getName(), path)),
                            (BlackboardAttribute(
                                BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_TO.getTypeID(), self.getName(), receivers)),
                            (BlackboardAttribute(
                                BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_FROM.getTypeID(), self.getName(), prevSender)),
                            (BlackboardAttribute(
                                BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME_RCVD.getTypeID(), self.getName(), resultSet.getInt("TSK_DATETIME_RCVD"))),
                            (BlackboardAttribute(
                                BlackboardAttribute.ATTRIBUTE_TYPE.TSK_SUBJECT.getTypeID(), self.getName(), resultSet.getString("TSK_SUBJECT")))
                        ))
                        
                        if resultSet.getString("TSK_PLAIN"):
                            artEmail.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_CONTENT_PLAIN.getTypeID(), self.getName(), resultSet.getString("TSK_PLAIN")))
                        
                        if resultSet.getString("TSK_HTML"):
                            artEmail.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_CONTENT_HTML.getTypeID(), self.getName(), resultSet.getString("TSK_HTML")))

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
                            otherAccounts.append(self.getAccount(skCase, singleFile, currReceiver))                    
                    
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


    def processEmlEmails(self, skCase, emlFiles):
        artIdEmail = skCase.getArtifactTypeID("TSK_EMAIL_MSG")
        artIdEmailType = skCase.getArtifactType("TSK_EMAIL_MSG")

        for singleEmlFile in emlFiles:

            path = singleEmlFile.getLocalPath()
            mail = mailparser.parse_from_file(path)
                
            for sender in mail.from_:
                senderAccount = self.getAccount(skCase, singleEmlFile, sender[1])

            receivers = []
            otherAccounts = []
            for receiver in mail.to:
                receivers.append(receiver[1])
                otherAccounts.append(self.getAccount(skCase, singleEmlFile, receiver[1]))

            receivers = ", ".join(receivers)

            subject = mail.subject

            date = self.getDateEpoch(mail.date)         

            """ handle attachments
            attachs = mail.attachments

            attachList = []
            for attach in attachs:
                att = {}
                att['fn'] = attach['filename']
                
                # TSK_FILE_TYPE_SIG ?
                att['ct'] = attach['mail_content_type']
                
                # TSK_FILE_TYPE_EXT ?
                att['pl'] = attach['payload']
                
                with open('C:/Users/2151580/Desktop/' + att['fn'], 'wb') as f:
                    f.write(base64.b64decode(att['pl']))
                    att['rp'] = os.path.realpath(f.name)
                    att['sz'] = os.path.getsize(att['rp'])
                    f.close()
                attachList.append(att)
                

            files = self.manageAttachments(attachList, file)         
            if files:
                for f in files:
                    services = IngestServices.getInstance()
                    services.fireModuleContentEvent(ModuleContentEvent(f))
            """
            
            artEmail = singleEmlFile.newArtifact(artIdEmail)
            artEmail.addAttributes((
                (BlackboardAttribute(
                    BlackboardAttribute.ATTRIBUTE_TYPE.TSK_PATH.getTypeID(), self.getName(), path)),
                (BlackboardAttribute(
                    BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_TO.getTypeID(), self.getName(), receivers)),
                (BlackboardAttribute(
                    BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_FROM.getTypeID(), self.getName(), sender[1])),
                (BlackboardAttribute(
                    BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME_RCVD.getTypeID(), self.getName(), date)),
                (BlackboardAttribute(
                    BlackboardAttribute.ATTRIBUTE_TYPE.TSK_SUBJECT.getTypeID(), self.getName(), subject))
            ))
            
            #ecompleteBody = "".join(mail.body).encode('utf-8')
            eplainBody = "".join(mail.text_plain).encode('utf-8')
            ehtmlBody = "".join(mail.text_html).encode('utf-8')

            #dcompleteBody = ecompleteBody.decode('utf-8')
            dplainBody = eplainBody.decode('utf-8')
            dhtmlBody = ehtmlBody.decode('utf-8')
            
            if dplainBody:
                artEmail.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_CONTENT_PLAIN.getTypeID(), self.getName(), dplainBody))
            
            if dhtmlBody:
                artEmail.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_CONTENT_HTML.getTypeID(), self.getName(), dhtmlBody))

            
            skCase.getCommunicationsManager().addRelationships(senderAccount, otherAccounts, artEmail, Relationship.Type.MESSAGE, date)

            try:
                # index the artifact for keyword search
                self.blackboard.indexArtifact(artEmail)
            except Blackboard.BlackboardException:
                self.log(Level.SEVERE, "Error indexing artifact " + artEmail.getDisplayName())

            # Fire an event to notify the UI and others that there is a new artifact  
            IngestServices.getInstance().fireModuleDataEvent(
                        ModuleDataEvent(self.getName(), artIdEmailType, None))


    def processMsgEmails(self, skCase, msgFiles):
        artIdEmail = self.skCase.getArtifactTypeID("TSK_EMAIL_MSG")
        artIdEmailType = self.skCase.getArtifactType("TSK_EMAIL_MSG")

        for singleMsgFile in msgFiles:

            path = singleMsgFile.getLocalPath()
            mail = mailparser.parse_from_file_msg(path)
                
            for sender in mail.from_:
                senderAccount = self.getAccount(skCase, singleMsgFile, sender[1])

            receivers = []
            otherAccounts = []
            for receiver in mail.to:
                receivers.append(receiver[1])
                otherAccounts.append(self.getAccount(skCase, singleMsgFile, receiver[1]))

            receivers = ", ".join(receivers)

            subject = mail.subject

            date = self.getDateEpoch(mail.date)         
            
            artEmail = singleMsgFile.newArtifact(artIdEmail)
            artEmail.addAttributes((
                (BlackboardAttribute(
                    BlackboardAttribute.ATTRIBUTE_TYPE.TSK_PATH.getTypeID(), self.getName(), path)),
                (BlackboardAttribute(
                    BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_TO.getTypeID(), self.getName(), receivers)),
                (BlackboardAttribute(
                    BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_FROM.getTypeID(), self.getName(), sender[1])),
                (BlackboardAttribute(
                    BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME_RCVD.getTypeID(), self.getName(), date)),
                (BlackboardAttribute(
                    BlackboardAttribute.ATTRIBUTE_TYPE.TSK_SUBJECT.getTypeID(), self.getName(), subject))
            ))
            
            #ecompleteBody = "".join(mail.body).encode('utf-8')
            eplainBody = "".join(mail.text_plain).encode('utf-8')
            ehtmlBody = "".join(mail.text_html).encode('utf-8')

            #dcompleteBody = ecompleteBody.decode('utf-8')
            dplainBody = eplainBody.decode('utf-8')
            dhtmlBody = ehtmlBody.decode('utf-8')
            
            if dplainBody:
                artEmail.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_CONTENT_PLAIN.getTypeID(), self.getName(), dhtmlBody))
            
            if dhtmlBody:
                artEmail.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_CONTENT_HTML.getTypeID(), self.getName(), dhtmlBody))

            
            skCase.getCommunicationsManager().addRelationships(senderAccount, otherAccounts, artEmail, Relationship.Type.MESSAGE, date)

            try:
                # index the artifact for keyword search
                self.blackboard.indexArtifact(artEmail)
            except Blackboard.BlackboardException:
                self.log(Level.SEVERE, "Error indexing artifact " + artEmail.getDisplayName())

            # Fire an event to notify the UI and others that there is a new artifact  
            IngestServices.getInstance().fireModuleDataEvent(
                        ModuleDataEvent(self.getName(), artIdEmailType, None))


    def getDateEpoch(self, date):
        try:
            return int((date - datetime.datetime.utcfromtimestamp(0)).total_seconds())
        except:
            return 0        


    def getAccount(self, skCase, _file, emailAddress):
        return skCase.getCommunicationsManager().createAccountFileInstance(Account.Type.EMAIL, emailAddress, self.getName(), _file)