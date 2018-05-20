import glob
import os
import matplotlib.pyplot as plt
%matplotlib inline

#Process Name/ID
processName = 'ALND1'

#Is this a transmission, absorption, or reflection measurement
mType = 'Transmission'

#SEM File extension
SEMExt = 'jpg'

# File extension for data plot image (.jpg, .jpeg, .png, etc.)
plotExt = 'png'

# Where is the data for plotting located
dataFilePath = "/home/etucks2/Desktop/Research/AUND-ALND/ALND"

partText = 'ALND/ALND/' #non-repeated text in file path before desired dataDict key
dataKeys = ['wavelength', mType]

#Open all two-column text files (containing spectral data) make a dictionary of data for each
i = 0
for filename in glob.glob(os.path.join(dataFilePath, '*.txt')): 
    with open (filename) as f:
        #Obtain array id
        arrayId = filename.partition(partText)[2][:-4]
        #Columnate transmission and wavelength Data
        colData = f.read().split()
        #Create individual array dictionary
        dataSubDict = dict([(dataKeys[0], colData[0::2]), (dataKeys[1], colData[1::2])])
        #Implant array data in master dictionary
        if i == 0:
            dataDict = dict([(arrayId, dataSubDict)])
        else:
            dataDict[arrayId] = dataSubDict
    i+=1

# Plot All Data and Save Images
print("processing...")
numTicks = 8
plotList = []

for array, data in dataDict.items():
    plotList.append(array)
    # Figure/Plot Setup
    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(plt.MaxNLocator(numTicks))
    ax.yaxis.set_major_locator(plt.MaxNLocator(numTicks))
    
    # Format data to float list
    wavelength, transmission = list(map(float, data['wavelength'])), list(map(float, data[mType]))

    # Plotting
    ax.plot(wavelength[-2600:], transmission[-2600:])
    ax.set_xlabel('Wavelength')
    ax.set_ylabel(mType)
    ax.set_title(array + ' ' + mType + ' Spectra')

    # File Save
    plt.savefig(dataFilePath + '/' + array + '_plot' + '.' + plotExt)
    #Clear figure for next plot
    plt.clf()

# Create pdf report document
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Desired Report Title
reportTitle = processName + ' Report'

#Obtain list of SEM images
SEMList = list(set(map(lambda x: x.partition(partText)[2].split('_')[0],glob.glob(dataFilePath + '/*.jpg'))))
# Find data with existing SEM images
dataFilledList = list(set(SEMList) & set(plotList))

# Create report pdf
doc = SimpleDocTemplate(reportTitle + '.pdf', pagesize=letter, rightMargin=18, leftMargin=18, topMargin=18, bottomMargin=18)

# Document elements conatiner and info
Story=[]
formatted_time = time.ctime()

# Image size (x,y) in inches
xSize = 3
ySize = 3

# Give report a title
ptext = '<font size=12>%s</font>' % reportTitle
Story.append(Paragraph(ptext, styles["Normal"]))

# Print time of report creation
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
ptext = '<font size=12>%s</font>' % formatted_time
Story.append(Paragraph(ptext, styles["Normal"]))

#Load images and accompanying text information to report
for dataPair in dataFilledList:
    plotImgs = []
    # Collect all image paths into variables, lists
    plotImg = dataFilePath + '/' + dataPair + '_plot' + '.' + plotExt
    pairImgs = glob.glob(dataFilePath + '/' + dataPair + '*.jpg')
    pairImgs[:0] = [plotImg]
    
    for image in pairImgs:
        im = Image(image, xSize*inch, ySize*inch)
        Story.append(im)
    #Space between each array's data
    Story.append(Spacer(1, 75))

# Make file and move to project directory
doc.build(Story)
os.rename(os.getcwd() + '/' + reportTitle + '.pdf', dataFilePath + '/' + reportTitle + '.pdf')
