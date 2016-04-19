#=========================================================================
# IntMulMsg_test
#=========================================================================
# Test suite for the integer multiply message

from pymtl     import *
from IntMulMsg import IntMulReqMsg

#-------------------------------------------------------------------------
# test_fields
#-------------------------------------------------------------------------

def test_fields():

  # Create msg

  msg = IntMulReqMsg()
  msg.a = 1
  msg.b = 2

  # Verify msg

  assert msg.a == 1
  assert msg.b == 2

#-------------------------------------------------------------------------
# test_mk_msg
#-------------------------------------------------------------------------

def test_mk_msg():

  # Create msg

  msg = IntMulReqMsg().mk_msg( 1, 2 )

  # Verify msg

  assert msg.a == 1
  assert msg.b == 2

#-------------------------------------------------------------------------
# test_str
#-------------------------------------------------------------------------

def test_str():

  # Create msg

  msg = IntMulReqMsg()
  msg.a = 0xdeadbeef
  msg.b = 0x0a0b0c0d

  # Verify string

  assert str(msg) == "deadbeef:0a0b0c0d"

