select * from tblDonor 
INTO OUTFILE 'C:\Users\jonat\Documents\PythonProjects\ChurchManager\Reports\Acknowledgement.txt' 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n';