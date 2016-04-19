from pymtl            import *
from pclib.test       import TestVectorSimulator
from truncationStep   import truncationStep

def  test_truncationStep( test_verilog , dump_vcd ):

  test_vectors = [
     # msg_in            , lod_in      , msg_out , trunc_out
     [ 0b0111111111111111, 0b0000001110, 0b111111, 0x009 ],
     [ 0b0000001110000000, 0b0000001001, 0b111001, 0x004 ],
     [ 0b0000001110010000, 0b0000001001, 0b111001, 0x004 ],
     #[ 0b0111111111111111, 0b0000001110, 0b111111, 0x009 ],
     #[ 0b0000001110000000, 0b0000000111, 0b110000, 0x001 ],
     # [ 0b0000010000000000, 0b0000001010, 0b000000, 0x004 ],
     # [ 0b0000000000000000, 0b0000010000, 0b000000, 0x00a ],
     # [ 0b0000000000001000, 0b0000000111, 0b000100, 0x001 ],
     # [ 0b0000110000000010, 0b0000001001, 0b000000, 0x003 ],
  ]

 # Instantiate and elaborate the model

  model = truncationStep( 16, 6 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

 # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.msg_in.value    = test_vector[0]
    model.lod_in.value    = test_vector[1]
  def tv_out( model, test_vector ):
    assert model.msg_out.value   == test_vector[2]
    assert model.trunc_out.value == test_vector[3]

  def line_trace( s ):
    return s.model.line_trace()

 # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
