pstFiles = []
ostFiles = []
emlFiles = []
msgFiles = []

for _file in files:
    if _file.getName().endswith(".pst"):# or _file.getName().endswith(".ost"):
        pstFiles.append(_file.getLocalPath())
    
    if _file.getName().endswith(".ost"): #or _file.getName().endswith(".ost"):
        ostFiles.append(_file.getLocalPath())

    if _file.getName().endswith(".eml"):
        emlFiles.append(_file.getLocalPath())
    
    if _file.getName().endswith(".msg"):
        msgFiles.append(_file.getLocalPath())





exit(1)                    

        """
        pyEngine = ScriptEngineManager().getEngineByName("python")
        sw = StringWriter()
        pyEngine.getContext().setWriter(sw)
        #pyEngine.eval("-C import subprocess; subprocess.call('C:/Users/2151580/AppData/Roaming/autopsy/python_modules/test_ES/numbers.py', shell=True)")
        #pyEngine.eval("import subprocess; subprocess.call('numbers.py', shell=True)")
        pyEngine.eval("print('x')")
        
        f = open("C:/Users/2151580/AppData/Roaming/autopsy/python_modules/test_ES/d.txt", "a")
        f.write(sw.toString())
        f.close()

        exit(1)
        """
        for file in files:

            # Check if the user pressed cancel while we were busy
            if self.context.isJobCancelled():
                return IngestModule.ProcessResult.OK

            self.log(Level.INFO, "Processing file: " + file.getName())
            fileCount += 1

            filePath = file.getLocalPath()	
            
            # Get file name without extention
            fileName = os.path.basename(filePath).split('.')[0]
            
            # Temp directory path to write extated emails
            output = str(self.tempDir + TEMP_FOLDER + "/" + fileName)

            #if not os.path.exists(output):
            try:
                os.makedirs(output)
            #else:
            except:
                self.log(Level.INFO, "Directory '" + fileName + "' already exists!")
            
            try:
                proc = Runtime.getRuntime().exec(
                    ("py %s/test_ES/run.py %s %s %s")
                    % (self.pythonModulesPath, filePath, output, "-j 8"))
            except:
                proc = Runtime.getRuntime().exec(
                    ("python3 %s/test_ES/run.py %s %s %s")
                    % (self.pythonModulesPath, filePath, output, "-j 8"))
            finally:
                proc.waitFor()
                        
            proc = Runtime.getRuntime().exec(
                ("py %s/test_ES/process_email.py %s")
                % (self.pythonModulesPath, output))
            proc.waitFor()

            with open("C:/Users/2151580/AppData/Roaming/autopsy/python_modules/test_ES/data.txt") as fp:
                
                line = json.loads(str(fp.readline()))

                while line:
                    
                    path = line['path']

                    sender = line['sender']['email']

                    receivers = ", ".join([emails['email'] for emails in line['receiver']])

                    body = line['body']

                    date = int(line['date'])

                    subject = line['subject']

                    senderAccount = self.getAccount(self.skCase, file, line['sender']['email'])
                    
                    otherAccounts = [self.getAccount(self.skCase, file, receiver['email']) for receiver in line['receiver']]
                    
                    # Make an artifact on the blackboard.  TSK_INTERESTING_FILE_HIT is a generic type of
                    # artfiact.  Refer to the developer docs for other examples.
                    artEmail = file.newArtifact(artIdEmail)
                    artEmail.addAttributes((
                        (BlackboardAttribute(
                            BlackboardAttribute.ATTRIBUTE_TYPE.TSK_PATH.getTypeID(), self.getName(), path)),
                        (BlackboardAttribute(
                            BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_TO.getTypeID(), self.getName(), receivers)),
                        (BlackboardAttribute(
                            BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_FROM.getTypeID(), self.getName(), sender)),
                        (BlackboardAttribute(
                            BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL_CONTENT_PLAIN.getTypeID(), self.getName(), body)),
                        (BlackboardAttribute(
                            BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME_RCVD.getTypeID(), self.getName(), date)),
                        (BlackboardAttribute(
                            BlackboardAttribute.ATTRIBUTE_TYPE.TSK_SUBJECT.getTypeID(), self.getName(), subject))
                        ))
                    #TSK_EMAIL_CONTENT_HTML

                    self.skCase.getCommunicationsManager().addRelationships(senderAccount, otherAccounts, artEmail, Relationship.Type.MESSAGE, date)

                    try:
                        # index the artifact for keyword search
                        blackboard.indexArtifact(artEmail)
                    except Blackboard.BlackboardException as e:
                        self.log(Level.SEVERE, "Error indexing artifact " + artEmail.getDisplayName())

                    # Fire an event to notify the UI and others that there is a new artifact  
                    IngestServices.getInstance().fireModuleDataEvent(
                        ModuleDataEvent(self.getName(), artIdEmailType, None))
                   
                    try:
                        line = json.loads(str(fp.readline()))
                    except:
                        break
            fp.close()

            os.remove("C:/Users/2151580/AppData/Roaming/autopsy/python_modules/test_ES/data.txt")           