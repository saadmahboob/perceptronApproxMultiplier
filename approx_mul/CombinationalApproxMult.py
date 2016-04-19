#===============================================================
#Combinational Approximate Multiplier
#===============================================================

from pymtl            import *
from LeadingOne       import LeadingOne
from CombMultNStage   import CombMultNStage
from truncationStep   import truncationStep
from Combinational    import LeftLogicalShifter, ZeroExtender
from pclib.ifcs       import InValRdyBundle, OutValRdyBundle
from MymultReqMsg     import MymultReqMsg
from pclib.rtl        import RegEn, RegRst

class CombinationalApproxMult( Model ):
  
  # Constructor

  def __init__( s, nBits, k): 

    #Interface
    s.req     = InValRdyBundle (MymultReqMsg(nBits))
    s.resp    = OutValRdyBundle(nBits*2)

    s.approxNStage  = CombMultNStage(kBits = k)
    s.truncation1   = truncationStep(nBits, k)
    s.truncation2   = truncationStep(nBits, k)
    s.LOD1          = LeadingOne(nBits, k)  
    s.LOD2          = LeadingOne(nBits, k)
    s.LeftShift1    = LeftLogicalShifter(nBits*2, 10, 10)
    s.zeroExt       = ZeroExtender(k*2 , nBits*2)

    # input register to LOD
    s.connect( s.req.val  , s.LOD1.in_val )
    s.connect( s.req.msg.a , s.LOD1.msg_in )
    s.connect( s.req.val  , s.LOD2.in_val )
    s.connect( s.req.msg.b , s.LOD2.msg_in )
    
    # LOD to trunc unit
    s.connect( s.LOD1.out_val  , s.truncation1.in_val)
    s.connect( s.LOD1.msg_out  , s.truncation1.msg_in)
    s.connect( s.LOD1.pos_out  , s.truncation1.lod_in)
    
    s.connect( s.LOD2.out_val  , s.truncation2.in_val)
    s.connect( s.LOD2.msg_out  , s.truncation2.msg_in)
    s.connect( s.LOD2.pos_out  , s.truncation2.lod_in)
    
    # trunc unit to multiplier
    s.connect( s.truncation1.msg_out, s.approxNStage.a)
    s.connect( s.truncation2.msg_out, s.approxNStage.b)
    
    # trunc unit to left shifter
    s.connect(s.truncation2.trunc_out, s.LeftShift1.shamt )
    s.connect(s.truncation1.trunc_out, s.LeftShift1.shamt2 )
    
    # trunc unit to zero extender
    s.connect( s.truncation1.out_val,  s.zeroExt.in_val )
    
    # multiplier to zero extender
    s.connect(s.approxNStage.resp , s.zeroExt.in_ )
    
    # zero extender to left shifter
    s.connect( s.zeroExt.out_val , s.LeftShift1.in_val )
    s.connect( s.zeroExt.out     , s.LeftShift1.in_    )
    
    # left shifter to resp
    s.connect( s.LeftShift1.out    , s.resp.msg         )
    s.connect( s.LeftShift1.out_val,  s.resp.val        )
    
    s.connect( s.resp.rdy, s.req.rdy)
