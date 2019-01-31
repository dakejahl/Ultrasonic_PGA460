import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.patches as mpatches
import glob

surfaceType = ['A', 'B', 'C']

fig = plt.figure()

length1 = len(surfaceType)
for i in range (0, length1):

    length2 = len(os.listdir(surfaceType[i]))
    for j in range (2, length2+1):
	#fig = plt.figure(j)
	ax = fig.gca()
	ax.set_xticks(np.arange(0, 24, 2))
	ax.set_yticks(np.arange(0, 260, 10))

	plt.grid(b=True, which='minor', color='0.65', linestyle='-', linewidth=0.2)
	plt.grid(b=True, which='major', color='0.65', linestyle='-', linewidth=0.2)
        plt.xlabel('Time (ms)')
        plt.ylabel('Amplitude (dB)')
        #plt.legend(surfaceType[i])

        length3 = len(os.listdir(os.getcwd() + '/' + surfaceType[i] + '/' + 'Pos' + `j`))
        for k in range (0, length3):
            path = os.getcwd() + '/' + surfaceType[i] + '/' + 'Pos' + `j` + '/'

            fileIndex = os.listdir(path)
	    
	    theFile = path + fileIndex[k] 	
      
            x, y = np.genfromtxt(theFile, delimiter=',',skip_header=1, skip_footer=82, usecols=(1,2), unpack=True)
	    #plt.figure(j)
	    plt.subplot(2,3,j-1)
            plt.title('Position ' + `j`)

	    if i==0: my_patch1 = mpatches.Patch(color=('C' + `i`), label=`surfaceType[i]`)
	    if i==0: my_patch2 = mpatches.Patch(color=('C' + `i`), label=`surfaceType[i]`)
	    if i==0: my_patch3 = mpatches.Patch(color=('C' + `i`), label=`surfaceType[i]`)
	    #if i==0: my_patch4 = mpatches.Patch(color=('C' + `i`), label=`surfaceType[i]`)
	    #if i==0: my_patch5 = mpatches.Patch(color=('C' + `i`), label=`surfaceType[i]`)


	    if i==0 : my_patch1 = mpatches.Patch(color=('C' + `i`), label=`surfaceType[i]`)
	    if i==1 : my_patch2 = mpatches.Patch(color=('C' + `i`), label=`surfaceType[i]`)
	    if i==2 : my_patch3 = mpatches.Patch(color=('C' + `i`), label=`surfaceType[i]`)
	    #if i==3 : my_patch4 = mpatches.Patch(color=('C' + `i`), label=`surfaceType[i]`)
	    #if i==4 : my_patch5 = mpatches.Patch(color=('C' + `i`), label=`surfaceType[i]`)
	    plt.legend(handles=[my_patch1, my_patch2, my_patch3])
	    #plt.legend(handles=[my_patch1])

	    x_l = [0,0.8,1.4,2.2,3.6,5.6,13.6,21.6,29.6]
	    y_l = [223,223,207,55,47,39,39,39,39]
	    plt.plot(x,y, color=('C'+`i`), linewidth=0.5, marker='o', markersize=3)
	    plt.plot(x_l,y_l, color='k', linewidth=0.5, marker='o', markersize=3)

plt.show()
