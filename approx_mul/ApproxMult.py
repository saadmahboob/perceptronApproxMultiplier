#===============================================================
# ApproxMult
#===============================================================

from pymtl 			      import *
from LeadingOne 		  import LeadingOne
from ApproxMultNStage	import ApproxMultNStage
from truncationStep		import truncationStep
from Combinational		import LeftLogicalShifter, ZeroExtender
from pclib.ifcs       import InValRdyBundle, OutValRdyBundle
from MymultReqMsg		  import MymultReqMsg
from pclib.rtl        import RegEn

class ApproxMult (Model):
  
  # Constructor

  def __init__( s, nstages, nBits, k): 

	  #Interface
    s.req 		= InValRdyBundle (MymultReqMsg(nBits))
    s.resp 		= OutValRdyBundle(nBits*2)

    s.approxNStage  = ApproxMultNStage(nstages=2, kBits = k)
    s.truncation1   = truncationStep(nBits, k)
    s.truncation2   = truncationStep(nBits, k)
    s.LOD1          = LeadingOne(nBits, nstages)  
    s.LOD2		      = LeadingOne(nBits, nstages)
    s.LeftShift1    = LeftLogicalShifter(nBits*2, 10, 10)
    s.zeroExt	      = ZeroExtender(k*2 , nBits*2)
    s.val_reg1 	    = RegEn(1)
    s.val_reg2	    = RegEn(1)
    s.a_msg_reg 	  = RegEn(nBits)
    s.b_msg_reg	    = RegEn(nBits)
    s.mult_reg1     = RegEn(1)
    s.mult_reg2     = RegEn(1)
    s.delay1        = RegEn(10)
    s.delay2        = RegEn(10)
    s.delay3        = RegEn(10)
    s.delay4        = RegEn(10)

    # rdy signal that goes into multiplier
    s.connect( s.resp.rdy,  s.approxNStage.rdy_in )
	
    # registers for input reqs  
    s.connect( s.req.val,   s.val_reg1.in_ )
    s.connect( s.resp.rdy,  s.val_reg1.en  )
    s.connect( s.req.val,   s.val_reg2.in_ )
    s.connect( s.resp.rdy,  s.val_reg2.en  )
    s.connect( s.req.msg.a, s.a_msg_reg.in_)
    s.connect( s.resp.rdy,  s.a_msg_reg.en )
    s.connect( s.req.msg.b, s.b_msg_reg.in_)
    s.connect( s.resp.rdy,  s.b_msg_reg.en )

    # input register to LOD
    s.connect( s.val_reg1.out  , s.LOD1.in_val )
    s.connect( s.a_msg_reg.out , s.LOD1.msg_in )
    s.connect( s.val_reg2.out  , s.LOD2.in_val )
    s.connect( s.b_msg_reg.out , s.LOD2.msg_in )
    
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
    s.connect(s.truncation2.trunc_out, s.delay1.in_ )
    s.connect(s.truncation1.trunc_out, s.delay3.in_ )
    s.connect(s.resp.rdy             , s.delay1.en  )
    s.connect(s.resp.rdy             , s.delay3.en  )    

    s.connect(s.delay1.out, s.delay2.in_ )
    s.connect(s.delay3.out, s.delay4.in_ )
    s.connect(s.resp.rdy  , s.delay2.en  )
    s.connect(s.resp.rdy  , s.delay4.en  )
   
    s.connect(s.delay2.out, s.LeftShift1.shamt)
    s.connect(s.delay4.out, s.LeftShift1.shamt2)
    
    # trunc unit to zero extender
    s.connect( s.mult_reg1.en,        s.resp.rdy       )
    s.connect( s.mult_reg2.en,        s.resp.rdy       )
    s.connect( s.truncation1.out_val, s.mult_reg1.in_  )
    s.connect( s.mult_reg1.out,       s.mult_reg2.in_  )
    s.connect( s.mult_reg2.out,       s.zeroExt.in_val )
    
    # multiplier to zero extender
    s.connect(s.approxNStage.resp , s.zeroExt.in_ )
    
    # zero extender to left shifter
    s.connect( s.zeroExt.out_val , s.LeftShift1.in_val )
    s.connect( s.zeroExt.out     , s.LeftShift1.in_    )
    
    # left shifter to resp
    s.connect( s.LeftShift1.out    , s.resp.msg         )
    s.connect( s.LeftShift1.out_val,  s.resp.val        )
    
    s.connect( s.resp.rdy, s.req.rdy)


    def line_trace( s ):
      return "in_rdy={},in_val={},in_msg={} > out_rdy={},out_val={},out_msg={}"\
        .format(s.req.rdy, s.req.val, s.req.msg, s.resp.rdy, s.resp.val, s.resp.msg)
