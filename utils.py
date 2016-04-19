from pymtl import *
#=============================================================
# constant definition
#=============================================================

LOAD    = 0
STORE   = 1
CGT     = 2
SUB     = 3
CEZ     = 4
ADD     = 5
MUL     = 6
COPY    = 7
DEC     = 8
CEQ     = 9
ADDI    = 10
MULI    = 11
STORES  = 12
LOADNB  = 13

nWid      = 16
nReg      = 6
nLogReg   = 3
nPE       = 1
nMemInst  = 10
nNeighbor = 6
nLogNbr   = 3

nCtlField = 4
nSrcField = nLogReg + nLogNbr
nDesField = nLogReg + 1 + nNeighbor
RegEn     = 2**(nDesField - 1)

inRightNbrL1  = nReg + 0
inLeftNbrL1   = nReg + 1
inRightNbrL2  = nReg + 2
inLeftNbrL2   = nReg + 3
inRightNbrL4  = nReg + 4
inLeftNbrL4   = nReg + 5

outRightNbrL1 = 2**(nLogReg + 0)
outLeftNbrL1  = 2**(nLogReg + 1)
outRightNbrL2 = 2**(nLogReg + 2)
outLeftNbrL2  = 2**(nLogReg + 3)
outRightNbrL4 = 2**(nLogReg + 4)
outLeftNbrL4  = 2**(nLogReg + 5)

# port namings
rightNbrL1 = 0
leftNbrL1  = 1
rightNbrL2 = 2
leftNbrL2  = 3
rightNbrL4 = 4
leftNbrL4  = 5

# internal register naming
w0 = 0
w1 = 1
x0w0 = 3
x1w1 = 4
offset = 0
store = 1

# keep the result of step function
step_func_result =[]

#=============================================================
# instruction msg
#=============================================================
class inst_msg( BitStructDefinition ):

  def __init__( s ):

    s.ctl  = BitField( nCtlField )
    s.src0 = BitField( nSrcField )
    s.src1 = BitField( nSrcField )

    # for destination, bits 0~1 encodes one of the four local
    # registers, then the other two bits are used as one-hot
    # encoding for neighbors. i.e., if bit 2 is set, then send
    # result to right neighbor, if bit 3 is set, then send
    # result to left neighbor. If both bit 2 and bit 3 are set,
    # then send result to both neighbors.
    s.des  = BitField( nDesField )

def inst(opcode, src0, src1, des):
  msg = inst_msg()
  msg.ctl  = opcode
  msg.src0 = src0
  msg.src1 = src1
  msg.des  = des
  return msg