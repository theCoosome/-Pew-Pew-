import random

def genMetor(difficulty, maxwidth, maxheight,maxdensity):
	meteor = []
	meteor.append(random.randint(1, difficulty + 2))

	'''for i in range(random.randint(1, maxheight) + 2):
		minilist = []
		for k in range(random.randint(1 + maxwidth - i - 1,maxwidth)):
			minilist.append(random.randint(1, maxdensity))
		meteor.append(minilist)'''
	meteor.append([2,2])
	minilist = []
	for i in meteor:
		if i < maxheight / 2:
			for k in range(random.randint(1 + len(str(i)),maxwidth)):

				minilist.append(random.randint(1, maxdensity))

	return meteor

print genMetor(0,5,7,5)
print genMetor(2,5,7,5)
