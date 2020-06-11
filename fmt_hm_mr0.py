#Noesis Python model import+export test module, imports/exports some data from/to a made-up format

from inc_noesis import *
import struct

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
   handle = noesis.register("Playstation Home Beta", ".mr0")
   noesis.setHandlerTypeCheck(handle, noepyCheckType)
   noesis.setHandlerLoadModel(handle, noepyLoadModel) #see also noepyLoadModelRPG
       #noesis.setHandlerWriteModel(handle, noepyWriteModel)
       #noesis.setHandlerWriteAnim(handle, noepyWriteAnim)
   noesis.logPopup()
       #print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
   return 1

NOEPY_HEADER = "MR04"

#check if it's this type based on the data
def noepyCheckType(data):
   bs = NoeBitStream(data, NOE_BIGENDIAN)
   return 1  


#load the model
class sampleFile: 
         
	def __init__(self, bs):
		#rapi.rpgSetPosScaleBias(NoeVec3((-1,1,1)),NoeVec3((0,0,0)))
		#rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
		rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
		self.texList   = []
		self.vtxList   = []
		self.matList   = []
		self.boneList  = []
		self.loadAll(bs)


	def loadAll(self, bs):
		baseName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
		bs.seek(0x1c,NOESEEK_ABS)
		numMeshes = bs.read(">i")[0]
		print((numMeshes))
		dpos = bs.tell ()
		pointer = bs.read(">i")[0]
		bs.seek(dpos + pointer + 4,NOESEEK_ABS)
		mypos = bs.tell()
		for i in range(0, numMeshes):
                   rapi.rpgSetName(str(i))
                   bs.seek(mypos,NOESEEK_ABS)
                   numFCT = bs.read(">i")[0]
                   fPos = bs.tell()
                   fOffset = bs.read(">i")[0]
                   fAddress = (fOffset + fPos)
                   numVCT = bs.read(">i")[0]
                   numVB = bs.read(">i")[0]
                   vPos = bs.tell()
                   vOffset = bs.read(">i")[0]
                   vAddress = (vOffset + vPos)
                   bs.seek(0x08,NOESEEK_REL)
                   MPos = bs.tell()
                   MOffset1 = bs.read(">i")[0]
                   MAddress1 = (MOffset1 + MPos + 0x20)
                   mypos += 0x34
                   #print(hex(fAddress))
                   bs.seek(MAddress1,NOESEEK_ABS)
                   MPos2 = bs.tell()
                   MOffset2 = bs.read(">i")[0]
                   MAddress2 = (MOffset2 + MPos2)
                   bs.seek(MAddress2,NOESEEK_ABS)
                   MPos3 = bs.tell()
                   MOffset3 = bs.read(">i") [0]
                   MatAddress = (MOffset3 + MPos3)
                   bs.seek(MatAddress,NOESEEK_ABS)
                   matList = bs.readString()
                   matIndex = matList.split('textures\\')[-1]
                   texture = rapi.loadExternalTex(matList)
                   #if rapi.checkFileExists(matList):
                      #texture.name = rapi.getLocalFileName(matList)
                      #self.texList.append(texture)
                   rapi.rpgSetMaterial(matIndex)
                   bs.seek(vAddress,NOESEEK_ABS)
                   positions = bs.readBytes(numVCT * numVB)
                   bs.seek(fAddress,NOESEEK_ABS)
                   triangles = bs.readBytes(numFCT * 2)
                   #bs.seek(nAddress,NOESEEK_ABS)
                   #normals = bs.readbytes(nCT * 2)
                   rapi.rpgBindPositionBufferOfs(positions, noesis.RPGEODATA_FLOAT, numVB, 0)
                   rapi.rpgBindUV1BufferOfs(positions, noesis.RPGEODATA_FLOAT, numVB, 12)
                   rapi.rpgBindUV2BufferOfs(positions, noesis.RPGEODATA_FLOAT, numVB, 20)
                   #rapi.rpgBindNormalBufferOfs(normals, noesis.RPGEODATA_FLOAT, nCT, 0)
                   ##rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, len(positions) // numVB, noesis.RPGEO_POINTS, 1)
                   rapi.rpgCommitTriangles(triangles, noesis.RPGEODATA_USHORT, numFCT, noesis.RPGEO_TRIANGLE_STRIP, 1)
                   #rapi.rpgClearBufferBinds() #reset in case a subsequent mesh doesn't have the same components
		
classLoaderDict = {

	}
	
def dataAlign(pos,pad):
	if (pos % pad) > 0:
		return((pad - (pos) % pad))
	else:
		return(0)	


def noepyLoadModel(data, mdlList):
	ctx = rapi.rpgCreateContext()
	sample = sampleFile(NoeBitStream(data))
	try:
		mdl = rapi.rpgConstructModel()
	except:
		mdl = NoeModel()
	mdl.setModelMaterials(NoeModelMaterials(sample.texList, sample.matList))
	mdlList.append(mdl); mdl.setBones(sample.boneList)	
	return 1
