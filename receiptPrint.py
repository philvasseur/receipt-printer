#!/usr/bin/python

from Adafruit_Thermal import *
WHERE = "Teddy's"
URLNum = 1
lineLength=24
URL = "https://app.cranburydeliveries.com/retrieve/{}/"
#URL = "http://app.cranburydeliveries.com:8080/retrieve/{}/" # For testing
from urllib2 import urlopen
from urllib2 import HTTPError
from json import loads

def main(orderDictionary): #almost all of the following is just formatting
	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)
	dict = orderDictionary
	printer.feed(4)
	printer.setLineHeightSmall()
	printer.justify("C")
	printer.boldOn()
	printer.setSize("L")
	printer.println(WHERE)
	printer.setSize("M")
	printer.printNoLine("Order ")
	printer.println(dict['number'])
	
	nameNum = dict['custname']+': '+dict['phone']
	finalNameNum = breakIntoLines(nameNum,False,printer) #prints out the name/Number
	printer.println(finalNameNum)
	
	finalAddress = breakIntoLines(dict['address'],False,printer) #prints out the address
	printer.println(finalAddress)
	
	printer.boldOff()
	printer.justify("L")
	printer.setSize("M")
	for item in dict['items']:
		printer.setSize("M")
		printer.setLineHeightSmall()
		finalLine = breakIntoLines(item['name'],False,printer) #prints out the food name
		if item['price']!=0: #If the price isn't $0.00 prints out the item name and then .....s and then the price
			printer.printNoLine(finalLine)
			for i in range(0,lineLength-len(finalLine)):
                       		printer.printNoLine(".")
			printer.printNoLine(" $")
			printer.println('{0:.2f}'.format(round(item['price'],2)))
		else:
			printer.println(finalLine) #If price is $0.00, just prints out the item name
			
		printer.setSize("S")
		for addon in item['addons']: #Printing out the addons
			finalAddonLine = breakIntoLines(addon['name'],True,printer)
                        printer.printNoLine("  "+finalAddonLine)
			for i in range(0,lineLength-len(finalAddonLine)-2): #prints out the ....s before the prie
                       		printer.printNoLine(".")
			printer.printNoLine(" $")
			printer.println('{0:.2f}'.format(round(addon['price'],2)))

		if item['comments']: #Prints out the comments, only if a comment exists
			printer.printNoLine("  (")
                        finalCommentLine = breakIntoLines(item['comments'],True,printer)
                        printer.printNoLine(finalCommentLine)
			printer.println(")")

	printer.setSize("M")
	printer.printNoLine("Sales Tax............... $")
	printer.println(round(dict['tax'],2)) #prints the sales tax, rounds it to two decimals
	printer.setSize("M")
	printer.setSize("M") #to add an extra blank line which all the previous items have
	printer.println("Delivery Fee............ $5.00") #Hardcoded delivery fee, viewed as an item
	printer.println("______________________________")
	printer.feed(2)
	printer.printNoLine("Total")
	for i in range(0,lineLength-len("Total")):
		printer.printNoLine(".")
	printer.printNoLine(" $")
	printer.println('{0:.2f}'.format(round(dict['total'],2))) #rounds the total to 2 decimals
	printer.setLineHeight(32)
	printer.feed(10)
	
	
def breakIntoLines(currentLine,addSpaces,printer): #breaks lines greater than the lineLength set at top into properly sized lines
	#If any words are > lineLength makes them less than lineLength
	tempLineLength = lineLength
	if addSpaces:
		tempLineLength-=2
	words = currentLine.split()
	for i in range(0,len(words)):
		if len(words[i])>tempLineLength:
			words[i]=words[i][:tempLineLength]
	lastLine = ' '.join(words)
	if len(currentLine)>=tempLineLength:	#if the whole line is greater, removes words until it isn't
		firstLine = ' '.join(currentLine.split()[:len(currentLine.split())-1])
		arrayLength = len(currentLine.split())
		wordsRemoved = 1
		while(len(firstLine)>tempLineLength+5):
			firstLine = ' '.join(firstLine.split()[:len(firstLine.split())-1])
			wordsRemoved+=1
		lastLine=' '.join(currentLine.split()[arrayLength-wordsRemoved:])
		if addSpaces:
			printer.printNoLine("  ")
		printer.println(firstLine)
		if len(lastLine)>tempLineLength :
			lastLine = breakIntoLines(lastLine,addSpaces,printer) #if the remaining removed words are still greater, does it again recursively
	return lastLine

def get_one_order(where=WHERE): #Aaron's method to get the order dictionary object, returns false if no objects available
    try:
        fd = urlopen(URL.format(URLNum))
        text = fd.read().decode()
        obj = loads(text)
        return obj
    except HTTPError as err:
        if err.code == 404:
            return None
        else:
            return False

if __name__  == "__main__":
	import sys,time,pygame
	time.sleep(10)
	pygame.init()
	pygame.mixer.init()
	orderSound = pygame.mixer.Sound("/home/pi/git/ReceiptPrinter/sound.wav") #Plays the sound named 'sound.wav' in same printer folder
	
	while(True):
		orderReturn = get_one_order()
		if orderReturn:
			main(orderReturn)
			orderSound.play() #plays the sound when an order comes in
			
		else:
			#print("No open orders currently") #Only seen in console, exists to show that it is running
			time.sleep(25)
		time.sleep(5)
