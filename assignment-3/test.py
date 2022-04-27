from ftplib import FTP

 

# Create an FTP object and connect to the server

# as anonymous user

ftpObject = FTP(host="anftpserverhost");

ftpResponseMessage = ftpObject.storbinary(ftpCommand, fp=fileObject);