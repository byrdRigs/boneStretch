'''
Bone Stretch Tool
Description
	Tool to make the stretchy system for nurbsSufaces aka bones and locators/spheres
	
How to run:
	import BR_boneStretch as bSt
	reload (bSt)
	bSt.gui()
'''

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel


tab_bgc=(0.4718592, 0.13568, 239)
subTab_bgc = (0.4915200, 0.32256, 241)
window_bgc = (.2,.2,.2)
color_1	= (0, .51, .612)
color_2	= (.008, .6, .706)


def gui():
	if pm.window('Bone_Stretch_Window', q=1, exists=1):
		pm.deleteUI('Bone_Stretch_Window')
		#Bone_Stretch_Window

	win_width = 240
	window_object = pm.window('Bone_Stretch_Window', title="ByrdRigs' Bone Stretch", w=win_width, bgc=window_bgc)
	main_layout = pm.columnLayout()
	pm.text(l='Select the starting locator, ending locator, and the bone.', w=win_width, ww=1)
	pm.frameLayout(l='Manual', w=win_width, bgc=color_1, cl=1, cll=1, cc=windowResize)
	pm.button(l='Selection', w=win_width, c=getSelection)
	pm.button(l='Bone Rename', w=win_width, c=boneRename)
	pm.button(l='Start Loc', w=win_width, c=startLoc)
	pm.button(l='Distance Node', w=win_width, c=distanceNode)
	pm.button(l='Mult Node', w=win_width, c=multNode)
	pm.button(l='Condition Node', w=win_width, c=conditionNode)
	pm.button(l='Locator Connection', w=win_width, c=locConnection)
	pm.button(l='Distance Connection', w=win_width, c=distanceConnection)
	pm.button(l='Mult Connection', w=win_width, c=multConnection)
	pm.button(l='Condition Connection', w=win_width, c=conConnection)
	pm.button(l='Clean Up', w=win_width, c=cleanUp)
	pm.setParent(main_layout)
	pm.frameLayout(l='Auto', w=win_width, bgc=color_2, cl=1, cll=1, cc=windowResize)	
	pm.button(l='All in one', w=win_width, c=completeSystem)


	pm.window('Bone_Stretch_Window', e=1, wh=(240, 70), rtf=1)
	pm.showWindow(window_object)

	print('Window Created:', window_object)

def getSelection(*args):
	global og_sLocT, og_sLocS, eLocT, eLocS, boneT, boneS
	selection = pm.ls(sl=1, dag=1)
	print('Selected:', selection)
	og_sLocT = selection[0]
	og_sLocS = selection[1]
	eLocT = selection[3]
	eLocS = selection[4]
	boneT = selection[6]
	boneS = selection[7]
	print('OG Start Loc Transform:', og_sLocT)
	print('OG Start Loc Shape:', og_sLocS)
	print('End Loc Transform:', eLocT)
	print('End Loc Shape:', eLocS)
	print('Bone Transform:', boneT)
	print('Bone Shape:', boneS)

def boneRename(*args):
	bone_name = og_sLocT.replace('loc', 'bone')
	# print('Bone Name:', bone_name)
	boneT.rename(bone_name)

def startLoc(*args):
	global sLocT, sLocS
	'''
	Make the start loc
	'''
	pm.spaceLocator(p=[0, 0, 0])
	selection = pm.ls(sl=1, dag=1)
	sLocT = selection[0]
	sLocS = selection[1]
	# print('Start Loc Transform:', sLocT)
	# print('Start Loc Shape:', sLocS)

	'''
	Rename loc
	'''
	loc_name = boneT.replace('bone', 'sLoc')
	sLocT.rename(loc_name)

	'''
	Move the loc to the bone
	'''
	temp_cons = pm.parentConstraint(boneT, sLocT, mo=0)
	pm.delete(temp_cons)

def distanceNode(*args):
	global distT, distS
	'''
	Create the distance node
	'''
	dist_node = pm.createNode('distanceDimShape')
	print('Distance Node:', dist_node)
	pm.pickWalk(d='up')
	selection = pm.ls(sl=1, dag=1)
	distT = selection[0]
	distS = selection[1]
	print('Dist Transform:', distT)
	print('Dist Shape:', distS)

	'''
	Rename the node
	'''
	node_name = boneT.replace('bone', 'dist')
	distT.rename(node_name)

def multNode(*args):
	global mult
	'''
	Create the mult node
	'''
	mult = pm.createNode('multiplyDivide')
	
	'''
	Rename the node
	'''
	node_name = distT.replace('dist', 'mult')
	mult.rename(node_name)

def conditionNode(*args):
	global con
	'''
	Create the condition node
	'''
	con = pm.createNode('condition')
	
	'''
	Rename the node
	'''
	node_name = mult.replace('mult', 'con')
	con.rename(node_name)

def locConnection(*args):
	'''
	Connect the sLocS.worldPosition to the distS.startPoint
	'''
	pm.connectAttr(sLocS + '.worldPosition', distS + '.startPoint')

	'''
	Connect the eLocS.worldPosition to the distS.endPoint
	'''
	pm.connectAttr(eLocS + '.worldPosition', distS + '.endPoint')

def distanceConnection(*args):
	global length
	'''
	Connect the distS.distance to the mult.input1Z
	'''
	pm.connectAttr(distS + '.distance', mult + '.input1Z')

	'''
	Get the distance value
	'''
	length = pm.getAttr(distS + '.distance')
	print('Length:', length)

def multConnection(*args):
	'''
	Set the mult.input2Z to length
	'''
	mult.input2Z.set(length)

	'''
	Set the mult.operation to 2
	'''
	mult.operation.set(2)

	'''
	Connect the mult.outputZ to con.firstTerm
	'''
	pm.connectAttr(mult + '.outputZ', con + '.firstTerm')

	'''
	Set the con.secondTerm to length
	'''
	con.secondTerm.set(length)

	'''
	Connect the mult.outputZ to con.colorIfTrueB
	'''
	pm.connectAttr(mult + '.outputZ', con + '.colorIfTrueB')

	'''
	Connect the mult.outputZ to con.colorIfFalseB
	'''
	pm.connectAttr(mult + '.outputZ', con + '.colorIfFalseB')

	'''
	Set the con.operation to 3
	'''
	con.operation.set(3)

def conConnection(*args):
	'''
	Connect the con.outColorB to boneT.sz
	'''
	pm.connectAttr(con + '.outColorB', boneT + '.sz')

def cleanUp(*args):
	'''
	Aim Constrain the eLocT and the boneT
	'''
	pm.aimConstraint(eLocT, boneT, wut='scene', aim=(0, 0, 1), upVector=(0, 1, 0), mo=1)

	'''
	Point Constrain the og_sLocT and the boneT
	'''
	pm.pointConstraint(og_sLocT, boneT, mo=1)

	'''
	Parent Constrain the og_sLocT and the sLocT
	'''
	pm.parentConstraint(og_sLocT, sLocT, mo=1)

	'''
	Hide the sLocT and the distT
	'''
	sLocT.v.set(0)

	distT.v.set(0)

def completeSystem(*args):
	getSelection()
	boneRename()
	startLoc()
	distanceNode()
	multNode()
	conditionNode()
	locConnection()
	distanceConnection()
	multConnection()
	conConnection()
	cleanUp()

def windowResize(*args):
	if pm.window('Bone_Stretch_Window', q=1, exists=1):
		pm.window('Bone_Stretch_Window', e=1, wh=(240, 70), rtf=1)
	else:
		pm.warning('Bone Stretch Window does not exist')

def deleteUI(*args):
	# print('Closing UI')
	pm.deleteUI('Bone_Stretch_Window')















