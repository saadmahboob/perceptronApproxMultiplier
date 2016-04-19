#=========================================================================
# CGRA PERCEPTRON
#=========================================================================

from pymtl           import *
from pclib.ifcs      import InValRdyBundle, OutValRdyBundle
from utils           import *
from pe              import PeRTL
from pclib.rtl       import SingleElementBypassQueue, SingleElementNormalQueue, NormalQueue

class Cgra_perceptron( Model):

  def __init__( s ):

    # interface
    s.x0    = InValRdyBundle ( nWid       )
    s.x1    = InValRdyBundle ( nWid       )
    s.instr_neuron    = InValRdyBundle ( inst_msg() )
    s.instr_step_func = InValRdyBundle ( inst_msg() )

    s.neuron    = PeRTL()
    s.step_func = PeRTL()

    #s.ctr_q = SingleElementNormalQueue(inst_msg())
    #s.ctr_q = SingleElementBypassQueue(inst_msg())
    s.comp_result = SingleElementBypassQueue( nWid )

    s.connect( s.x0, s.neuron.in_neighbor[leftNbrL1])
    s.connect( s.x1, s.neuron.in_neighbor[rightNbrL1])
    s.connect( s.instr_neuron,    s.neuron.in_control)
    s.connect( s.instr_step_func, s.step_func.in_control)

    s.connect( s.neuron.out_neighbor[rightNbrL1], s.comp_result.enq    )
    s.connect( s.comp_result.deq,   s.step_func.in_neighbor[leftNbrL1] )



  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    # return s.fsm.line_trace() + \
    #        " | " + "i={},len_mj={}".format(s.fsm.i.out.value, s.fsm.arr_len_mj.out.value) + \
    #        " | {},val={},rdy={}".format(s.cgra.memreq.msg.value, s.cgra.memreq.val.value, s.cgra.memreq.rdy.value) + \
    #        " | {},val={},rdy={}".format(s.cgra.memresp.msg.value, s.cgra.memresp.val.value, s.cgra.memresp.rdy.value)


    return s.neuron.line_trace_neuron() + " | " + s.step_func.line_trace_step_func()
