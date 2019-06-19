file = "M1231340.19b"
output = "test.ems"

f_output = open(output,'w')

with open(file, 'r') as RINEX_b:
  for line in RINEX_b:
    #find end of header
    if line.strip() == "END OF HEADER": #find end of header
        break
  while True:
    #read blocks of 3
    message=RINEX_b.readline().split()
    if not message: break #EOF
    try:
        if message[10]=='SBA': #SBAS message
            for idx in list(range(2)):
              message += RINEX_b.readline().split()
              #remove 00.1
        else:
          for idx in list(range(2)): RINEX_b.readline() #skip next 2 lines

        #write output in EMS format  SV_ID DATE_TIME MESSAGE_ID MESSAGE
        #seconds format is xx.1, this converts it to EMS one - xx
        seconds = message[6].split(".")[0]
        f_output.write(" ".join(message[0:6]) + " " +
                       seconds + " " + message[11] + " " +
                       "".join(message[12:]) +"\n")
    except:
        print("Reading error, possible EOF or corrupted message")
f_output.close()
