from pymtl        import *
from pclib.test   import TestVectorSimulator
from LeadingOne   import LeadingOne

def  test_LeadingOne( test_verilog, dump_vcd ):

   test_vectors = [
      # msg_in            , pos_out , msg_out
      [ 0b0111111111111111, 0b001110, 0b0111111111111111 ],
      [ 0b0000001110000000, 0b001001, 0b0000001110000000 ],
      [ 0b0000010000000000, 0b001010, 0b0000010000000000 ],
      [ 0b0000000000000000, 0b000000, 0b0000000000000000 ],
      [ 0b0000000000001000, 0b000011, 0b0000000000001000 ],
      [ 0b0000110000000010, 0b001001, 0b0000110000000010 ],
   ]

  # Instantiate and elaborate the model

   model = LeadingOne(16,6)
   model.vcd_file = dump_vcd
   if test_verilog:
     model = TranslationTool( model )
   model.elaborate()

  # Define functions mapping the test vector to ports in model

   def tv_in( model, test_vector ):
     model.msg_in.value = test_vector[0]

   def tv_out( model, test_vector ):
     assert model.pos_out.value     == test_vector[1]
     assert model.msg_out.value == test_vector[2]

  # Run the test

   sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
   sim.run_test()
