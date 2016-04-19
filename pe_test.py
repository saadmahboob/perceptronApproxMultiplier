#=========================================================================
# test for pe.py
#=========================================================================

import pytest
import struct

from pymtl                        import *
from pclib.ifcs                   import MemMsg
from pclib.test.TestMemoryFuture  import TestMemory
from pclib.test                   import TestSource, TestSink
from pe                           import PeRTL
from utils                        import *

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, pe_model, src_ctr_in_msgs, src_nbr_in_msgs, sink_fsm_out_msgs, sink_nbr_out_msgs, src_delay, sink_delay ):

    # Instantiate models
    
    #s.src_mem_in = TestSource (nWid,       src_mem_in_msgs, src_delay)
    s.src_ctr_in = TestSource (inst_msg(), src_ctr_in_msgs, src_delay)
    s.src_nbr_in = [ TestSource (nWid,     src_nbr_in_msgs[i], src_delay) for i in range(6)]

    #s.sink_mem_out = TestSink (nWid,       sink_mem_out_msgs, sink_delay)
    s.sink_fsm_out = TestSink (1,          sink_fsm_out_msgs, sink_delay)
    s.sink_nbr_out = [ TestSink (nWid,     sink_nbr_out_msgs[i], sink_delay) for i in range(6)]

    # 32 bit mem_addr, 16 bit data
    # Potentially, addr format: 0x01230000, 0x01230002, 0x01230004. each bit in addr corresponds
    # to 1 byte of data. Since data is 16 bit = 2 bytes, address incr by 2 bits.
    s.mem = TestMemory( MemMsg(32,nWid), 1, 0, 0 )  # nports, stall_prob, latency, mem_nbytes
    s.pe  = pe_model

  def elaborate_logic( s ):

    # Connect

    s.connect( s.mem.resps[0],     s.pe.memresp          )
    s.connect( s.src_ctr_in.out,   s.pe.in_control       )

    s.connect( s.mem.reqs[0],      s.pe.memreq           )
    s.connect( s.sink_fsm_out.in_, s.pe.out_fsm          )

    for i in range(6):
      s.connect( s.src_nbr_in[i].out,   s.pe.in_neighbor[i]  )
      s.connect( s.sink_nbr_out[i].in_, s.pe.out_neighbor[i] )

  def done( s ):
    done = 1
    for i in range(6):
      if not s.src_nbr_in[i].done:   done = 0
      if not s.sink_nbr_out[i].done: done = 0
    if (not s.src_ctr_in.done) or (not s.sink_fsm_out.done): done = 0
    return done

  def line_trace( s ):
    return s.mem.line_trace() + "> " + s.pe.line_trace() + "> "\
       + s.sink_nbr_out[1].line_trace() + ">" + s.sink_nbr_out[3].line_trace()


def inst(opcode, src0, src1, des):
  msg = inst_msg()
  msg.ctl  = opcode
  msg.src0 = src0
  msg.src1 = src1
  msg.des  = des
  return msg


#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

mini = [0xaaaa, 0xbbbb, 0xcccc, 0xdddd, 0xffff]


def run_sel_test( ModelType, src_delay, sink_delay, dump_vcd, test_verilog, max_cycles=30  ):

  # test operands

  src_nbr_in_msgs   = [[] for _ in range(6)]
  sink_nbr_out_msgs = [[] for _ in range(6)]

  #src_ctr_in_msgs      = [inst(LOAD, 4, 0, 8), inst(STORE, 4, 5, 0), inst(LOAD, 4, 0, 16 + 1), inst(STORE, 4, 1, 0), inst(LOAD, 4, 0, 8), inst(ADDI, 7, 4, 8), inst(LOAD, 0, 0, 16 + 1), inst(LOAD, 0, 0, 16 + 1)]
  #src_nbr_in_msgs[0]   = [0x0004, 0x0000, 0x0000, 0x0002, 0x0002, 0x0001]
  #src_nbr_in_msgs[1]   = [0xbeef]

  #sink_fsm_out_msgs    = []
  #sink_nbr_out_msgs[0] = []
  #sink_nbr_out_msgs[1] = [0xcccc, 0xbeef, 0x0008]

  rightNbrL1 = 0
  leftNbrL1  = 1
  rightNbrL2 = 2
  leftNbrL2  = 3
  rightNbrL4 = 4
  leftNbrL4  = 5

  src_ctr_in_msgs      = [ # LD, mem_addr(0x0008) which should be 0xffff
                          inst(LOAD, inRightNbrL1, 0, outLeftNbrL1),
                          inst(ADD, inLeftNbrL1, inRightNbrL1, outLeftNbrL2),
                          inst(ADD, inRightNbrL4, inRightNbrL2, outRightNbrL1),
                          inst(ADDI, 5, inRightNbrL2, outRightNbrL1),  
                          inst(LOAD, inRightNbrL1, 0, outLeftNbrL1),
                          inst(LOAD, inRightNbrL1, 0, outLeftNbrL1 + RegEn + 1),
                          inst(LOADNB, inRightNbrL1, 0, outLeftNbrL1),
                          inst(LOADNB, inRightNbrL1, 0, outLeftNbrL1),
                          inst(ADD, inLeftNbrL1, 1, outLeftNbrL1),
                          # new instructions added below
                          inst(MUL, inLeftNbrL2, inLeftNbrL4, outLeftNbrL1),
                          inst(MUL, inLeftNbrL2, inLeftNbrL4, outLeftNbrL1),
                          inst(SUB, inLeftNbrL2, inLeftNbrL4, outLeftNbrL1),
                          inst(MUL, inLeftNbrL2, inLeftNbrL4, outLeftNbrL1),
                          ]

  src_nbr_in_msgs[rightNbrL1] = [0x0008, 0x0001, 0x0000, 0x0002, 0x0004, 0x0006]
  src_nbr_in_msgs[leftNbrL1]  = [0x0002, 0x0001]
  src_nbr_in_msgs[rightNbrL2] = [0x0004,0x0005]
  #src_nbr_in_msgs[leftNbrL2]  = [0x0006]
  src_nbr_in_msgs[leftNbrL2]  = [0x0006, 0x0001, 0x0002, 0x56] #for the newly added
  src_nbr_in_msgs[rightNbrL4] = [0x0003]
  #src_nbr_in_msgs[leftNbrL4]  = [0x0004]
  src_nbr_in_msgs[leftNbrL4]  = [0x0004, 0x0004, 0x0001, 0x14] # for the newly added

  sink_fsm_out_msgs    = []
  sink_nbr_out_msgs[rightNbrL1] = []
  sink_nbr_out_msgs[rightNbrL1] = [0x0007,0x000a]              #added output here to print out.
  #sink_nbr_out_msgs[leftNbrL1]  = [0xffff, 0xaaaa,0xbbbb,0xcccc,0xbbbc, 0x0018, 0xfffd]
  sink_nbr_out_msgs[leftNbrL1]  = [0xffff, 0xaaaa,0xbbbb,0xcccc,0xbbbc,0x0023, 0x0005, 0x0001, 0x640]
  sink_nbr_out_msgs[rightNbrL2] = []
  sink_nbr_out_msgs[leftNbrL2]  = [0x0003]
  sink_nbr_out_msgs[rightNbrL4] = []
  sink_nbr_out_msgs[leftNbrL4]  = []


  # Instantiate and elaborate the model

  model_under_test = ModelType()

  if dump_vcd:
    model_under_test.vcd_file = dump_vcd

  if test_verilog:
    model_under_test = TranslationTool( model_under_test )

  model = TestHarness( model_under_test, src_ctr_in_msgs, src_nbr_in_msgs, sink_fsm_out_msgs, sink_nbr_out_msgs, src_delay, sink_delay )

  data_bytes = struct.pack("<{}H".format(len(mini)),*mini)

  model.mem.write_mem( 0x0000, data_bytes )

  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()

  while ((not model.done()) and sim.ncycles < max_cycles):
    sim.print_line_trace()
    sim.cycle()

  assert sim.ncycles < max_cycles
  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# test_gcd
#-------------------------------------------------------------------------
@pytest.mark.parametrize( 'src_delay, sink_delay', [
  ( 0,  0),
])
def test( src_delay, sink_delay, dump_vcd, test_verilog ):
  run_sel_test( PeRTL, src_delay, sink_delay, dump_vcd, test_verilog )
