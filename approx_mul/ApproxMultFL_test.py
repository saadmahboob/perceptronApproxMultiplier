#========================================================================
#ApproxMultFL_test
#=========================================================================
import pytest
import random

random.seed(0xdeadbeef)

from pymtl         import *
from pclib.test    import mk_test_case_table, run_sim
from pclib.test    import TestSource, TestSink
from IntMulFL      import IntMulFL

from MymultReqMsg  import MymultReqMsg

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, imul, src_msgs, sink_msgs,
                src_delay, sink_delay,
                dump_vcd=False, test_verilog=False ):

    # Instantiate models

    s.src  = TestSource ( MymultReqMsg(16), src_msgs,  src_delay  )
    s.imul = imul
    s.sink = TestSink   ( Bits(32),       sink_msgs, sink_delay )

    # Dump VCD

    if dump_vcd:
      s.imul.vcd_file = dump_vcd

    # Translation

    if test_verilog:
      s.imul = TranslationTool( s.imul )

    # Connect
    
    s.connect( s.src.out,  s.imul.req )
    s.connect( s.imul.resp, s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.imul.line_trace()  + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_req_msg
#-------------------------------------------------------------------------

def req( a, b ):
  msg = MymultReqMsg(16)
  msg.a = Bits( 16, a, trunc=True )
  msg.b = Bits( 16, b, trunc=True )
  return msg

def resp( a ):
  return Bits( 32, a, trunc=True )

#----------------------------------------------------------------------
# Test Case: small positive * positive
#----------------------------------------------------------------------

small_pos_pos_msgs = [
  req(  2,  3 ), resp(   6 ),
  req(  4,  5 ), resp(  20 ),
  req(  3,  4 ), resp(  12 ),
  req( 10, 13 ), resp( 130 ),
  req(  8,  7 ), resp(  56 ),
]

#----------------------------------------------------------------------
# Test Case: small negative * positive
#----------------------------------------------------------------------

small_neg_pos_msgs = [
  req(  -2,  3 ), resp(   -6 ),
  req(  -4,  5 ), resp(  -20 ),
  req(  -3,  4 ), resp(  -12 ),
  req( -10, 13 ), resp( -130 ),
  req(  -8,  7 ), resp(  -56 ),
]

#----------------------------------------------------------------------
# Test Case: small positive * negative
#----------------------------------------------------------------------

small_pos_neg_msgs = [
  req(  2,  -3 ), resp(   -6 ),
  req(  4,  -5 ), resp(  -20 ),
  req(  3,  -4 ), resp(  -12 ),
  req( 10, -13 ), resp( -130 ),
  req(  8,  -7 ), resp(  -56 ),
]

#----------------------------------------------------------------------
# Test Case: small negative * negative
#----------------------------------------------------------------------

small_neg_neg_msgs = [
  req(  -2,  -3 ), resp(   6 ),
  req(  -4,  -5 ), resp(  20 ),
  req(  -3,  -4 ), resp(  12 ),
  req( -10, -13 ), resp( 130 ),
  req(  -8,  -7 ), resp(  56 ),
]

#----------------------------------------------------------------------
# Test Case: large positive * positive
#----------------------------------------------------------------------

# modified new correct test cases.
large_pos_pos_msgs = [
  req( 0xef46, 0x6614 ), resp( 0x5e080000 ),
  req( 0xef56, 0xabcd ), resp( 0x9e900000 ),
  req( 0xef46, 0x6614 ), resp( 0x5e080000 ),
  req( 0xdefc, 0xcdef ), resp( 0xaf500000 ),
  req( 0xabcd, 0xabcd ), resp( 0x73900000 ),
  req( 0xef46, 0x6614 ), resp( 0x5e080000 ),
  req( 0x01f8, 0x0fc0 ), resp( 0x001f0200 ),
  req( 5965,   346    ), resp( 0x001f9400 ),  # correct value
]

#----------------------------------------------------------------------
# Test Case: large negative * negative
#----------------------------------------------------------------------

large_neg_neg_msgs = [
  req( 0x80000001, 0x80000001 ), resp( 0x00000001 ),
  req( 0x8000abcd, 0x8000ef00 ), resp( 0x20646300 ),
  req( 0x80340580, 0x8aadefc0 ), resp( 0x6fa6a000 ),
]

#----------------------------------------------------------------------
# Test Case: zeros
#----------------------------------------------------------------------

zeros_msgs = [
  req(  0,  0 ), resp(   0 ),
  req(  0,  1 ), resp(   0 ),
  req(  1,  0 ), resp(   0 ),
  req(  0, -1 ), resp(   0 ),
  req( -1,  0 ), resp(   0 ),
]

#----------------------------------------------------------------------
# Test Case: random small
#----------------------------------------------------------------------

random_small_msgs = []
for i in xrange(50):
  a = random.randint(0,100)
  b = random.randint(0,100)
  random_small_msgs.extend([ req( a, b ), resp( a * b ) ])

#----------------------------------------------------------------------
# Test Case: random large
#----------------------------------------------------------------------

random_large_msgs = []
for i in xrange(50):
  a = random.randint(0,0xffff)
  b = random.randint(0,0xffff)
  random_large_msgs.extend([ req( a, b ), resp( a * b ) ])

#----------------------------------------------------------------------
# Test Case: lomask
#----------------------------------------------------------------------

random_lomask_msgs = []
for i in xrange(50):

  shift_amount = random.randint(0,16)
  a = random.randint(0,0xffff) << shift_amount

  shift_amount = random.randint(0,16)
  b = random.randint(0,0xffff) << shift_amount

  random_lomask_msgs.extend([ req( a, b ), resp( a * b ) ])

#----------------------------------------------------------------------
# Test Case: himask
#----------------------------------------------------------------------

random_himask_msgs = []
for i in xrange(50):

  shift_amount = random.randint(0,16)
  a = random.randint(0,0xffff) >> shift_amount

  shift_amount = random.randint(0,16)
  b = random.randint(0,0xffff) >> shift_amount

  random_himask_msgs.extend([ req( a, b ), resp( a * b ) ])

#----------------------------------------------------------------------
# Test Case: lohimask
#----------------------------------------------------------------------

random_lohimask_msgs = []
for i in xrange(50):

  rshift_amount = random.randint(0,12)
  lshift_amount = random.randint(0,12)
  a = (random.randint(0,0xffff) >> rshift_amount) << lshift_amount

  rshift_amount = random.randint(0,12)
  lshift_amount = random.randint(0,12)
  b = (random.randint(0,0xffff) >> rshift_amount) << lshift_amount

  random_lohimask_msgs.extend([ req( a, b ), resp( a * b ) ])

#----------------------------------------------------------------------
# Test Case: sparse
#----------------------------------------------------------------------

random_sparse_msgs = []
for i in xrange(50):

  a = random.randint(0,0xffff)

  for i in xrange(32):
    is_masked = random.randint(0,1)
    if is_masked:
      a = a & ( (~(1 << i)) & 0xffff )

  b = random.randint(0,0xffff)

  for i in xrange(32):
    is_masked = random.randint(0,1)
    if is_masked:
      b = b & ( (~(1 << i)) & 0xffff )

  random_sparse_msgs.extend([ req( a, b ), resp( a * b ) ])

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                      "msgs                 src_delay sink_delay"),
#  [ "small_pos_pos",     small_pos_pos_msgs,   0,        0          ],
  [ "large_pos_pos",     large_pos_pos_msgs,   0,        0          ],
#  [ "zeros",             zeros_msgs,           0,        0          ],
#  [ "random_small",      random_small_msgs,    0,        0          ],
#  [ "random_large",      random_large_msgs,    0,        0          ],
])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( IntMulFL(),
                        test_params.msgs[::2], test_params.msgs[1::2],
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

