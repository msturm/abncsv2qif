abncsv2qif
==========

Convert ABN Amro CSV bank statements to QIF, which is supported by YNAB (http://www.youneedabudget.com) so you can relatively easy import your financial data from your bank account into YNAB.

Usage
=====

Go to Internet bankieren of ABN Amro (http://www.abnamro.nl) and login with your e.Identifier2. When you are in the digital banking environment, you can go to 'bij- en afschrijvingen' in the 'downloaden' section (the menu on the left). There you can select the period of which you want to download your transactions and in the dropdown select the format of the file you want to download. It is important that you choose _TXT_ there.

After you have downloaded the file, you go to a commandline (for example using the Terminal app) and locate the file. Then enter (in the directory where you checked out this project):
  
    $ abncsv2qif <filename> > newfile.qif

After this, newfile.qif will be a QIF file containing all the data of the downloaded file. This file can be imported in YNAB by going to your ABN checking account and then click the 'Import' button at the top and select your generaged file.

Known issues
============

The conversion is not flawless, mainly because there is no documentation available on the structure of the files you can download from ABN Amro, so I created the tool mostly by trail-and-error. 

Future Improvements
===================

I'm planning to create a simple userinterface for this tool, in order to make it more userfriendly. However, the priority for this is rather low at the moment.

For questions, suggestions or comments, please create a Github issue, or create a pull request if you have improvements!
