from pydicom import dcmread
from os import system
from math import floor
from sys import argv

source = argv[1]
ds = dcmread(source, force=True)

# ####################################################################
# #ds-
# # (300a, 00b0)  Beam Sequence  n item(s)
# # (300a, 0111)  Control Point Sequence  n item(s)
# # (300a, 011a)  Beam Limiting Device Position Sequence  n item(s) 
# # (300a, 011c) Leaf/Jaw Positions                  DS: Array of 160 elements
# # print(ds[0x300a, 0x00b0][0][0x300a, 0x0111][0][0x300a, 0x011a][1][0x300a, 0x011c][0]) # wydruk pozycji 1 listka
# # ds[0x300a, 0x00b0][0][0x300a, 0x0111][0][0x300a, 0x011a][1][0x300a, 0x011c].value[0]=-20.0 #edycja położenia listka
# #len(ds[0x300a, 0x00b0].value) - liczba wiązek
# #len(ds[0x300a, 0x00b0][0][0x300a, 0x0111].value) - liczba control pointów
# # print(len(ds[0x300a, 0x00b0].value))
# # print(len(ds[0x300a, 0x00b0][0][0x300a, 0x0111].value))
# # print(ds[0x300a, 0x00b0][0][0x300a, 0x0111][1])
#######################################################################

#MLC CONVERT###################################################################################################################################
BEAM_count = len(ds[0x300a, 0x00b0].value)
for beam in range(len(ds[0x300a, 0x00b0].value)): #iteracja po wiązkach
    CP_count = len(ds[0x300a, 0x00b0][beam][0x300a, 0x0111].value)
    for cp in range(len(ds[0x300a, 0x00b0][beam][0x300a, 0x0111].value)): #iteracja po control pointach
        for leaf in range(len(ds[0x300a, 0x00b0][beam][0x300a, 0x0111][cp][0x300a, 0x011a][1][0x300a, 0x011c].value)): #iteracja po listkach
            polozenie_listka = ds[0x300a, 0x00b0][beam][0x300a, 0x0111][cp][0x300a, 0x011a][1][0x300a, 0x011c][leaf]
            
            #BANK A - LISTKI OD 1-80 (W DICOM OD 0-79) 
            #BANK B - LISTKI OD 81-160 (W DICOM OD 80-159)

            if (leaf>=14 and leaf<=65): #BANK A
                if polozenie_listka<-120:
                    ds[0x300a, 0x00b0][beam][0x300a, 0x0111][cp][0x300a, 0x011a][1][0x300a, 0x011c].value[leaf] = -120.0
                elif polozenie_listka>=120:
                    ds[0x300a, 0x00b0][beam][0x300a, 0x0111][cp][0x300a, 0x011a][1][0x300a, 0x011c].value[leaf] = 119.0
                
            elif (leaf>=94 and leaf<=145): #BANK B
                if polozenie_listka>120:
                    ds[0x300a, 0x00b0][beam][0x300a, 0x0111][cp][0x300a, 0x011a][1][0x300a, 0x011c].value[leaf] = 120.0
                elif polozenie_listka<=-120:
                    ds[0x300a, 0x00b0][beam][0x300a, 0x0111][cp][0x300a, 0x011a][1][0x300a, 0x011c].value[leaf] = -119.0
           
        #PROGRESS BAR
        if cp%10==0:
            system('cls')
            print("\033[92m {}\033[00m".format("################################   CONVERTING MLC beam: "+str(beam+1)+" from "+str(BEAM_count)+" ########################################### \n"))
            bar_text =""
            for i in range(floor(cp/10)):
                bar_text+=chr(0x258c)
                #bar_text+=chr(0x2588)+"\033[98m {}\033[00m" .format(chr(0x2502))
            print(bar_text+" "+str(cp)+"/"+str(CP_count))


#JAWS CONVERT ########################################################################################################################
for beam in range(len(ds[0x300a, 0x00b0].value)):
    ##ds[0x300a, 0x00b0][0][0x300a, 0x0111][0][0x300a, 0x011a][0][0x300a, 0x011c].value[0]
    for cp in range(len(ds[0x300a, 0x00b0][beam][0x300a, 0x0111].value)): 
        JawA = ds[0x300a, 0x00b0][beam][0x300a, 0x0111][cp][0x300a, 0x011a][0][0x300a, 0x011c][0]
        JawB = ds[0x300a, 0x00b0][beam][0x300a, 0x0111][cp][0x300a, 0x011a][0][0x300a, 0x011c][1]
        if JawA <-120:
            ds[0x300a, 0x00b0][beam][0x300a, 0x0111][cp][0x300a, 0x011a][0][0x300a, 0x011c].value[0]=-120.0
        if JawB >120:
            ds[0x300a, 0x00b0][beam][0x300a, 0x0111][cp][0x300a, 0x011a][0][0x300a, 0x011c].value[1]=120.0
    
        #PROGRESS BAR
        if cp%10==0:
                system('cls')
                print("\033[92m {}\033[00m".format("\n################################   CONVERTING JAWS beam: "+str(beam+1)+" from "+str(BEAM_count)+" ###########################################\n"))
                bar_text =""
                for i in range(floor(cp/10)):
                    bar_text+=chr(0x258c)
                    #bar_text+=chr(0x2588)+"\033[98m {}\033[00m" .format(chr(0x2502))
                print(bar_text+" "+str(cp)+"/"+str(CP_count))
#SAVE DICOM FILE#####################################################################################################################
ds.save_as(source[0:-4]+"-converted.dcm")

system('cls')
print("\n\nDONE!\n")

input("Press ENTER for exit...")





