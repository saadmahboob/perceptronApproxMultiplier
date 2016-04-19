#=========================================================================
# PE model for hybrid FSM-CGRA
#=========================================================================

from pymtl           import *
from pclib.ifcs      import InValRdyBundle, OutValRdyBundle
from pclib.ifcs      import MemMsg, MemReqMsg, MemRespMsg
from utils           import *
from pclib.rtl       import RegisterFile, RegRst
from pclib.rtl       import SingleElementBypassQueue, SingleElementPipelinedQueue, NormalQueue
from approx_mul.CombinationalApproxMult  import CombinationalApproxMult
from approx_mul.MymultReqMsg import MymultReqMsg


class PeRTL( Model):

  def __init__( s ):

    # interface
    
    s.in_control   = InValRdyBundle     (inst_msg() ) # control word
    s.memresp      = InValRdyBundle     (MemMsg(32,nWid).resp)
    # 0,1: right/left neighbors
    # 2,3: length-2 right/left PEs
    # 4,5: length-4 right/left PEs
    s.in_neighbor  = InValRdyBundle[6]  (nWid)

    s.memreq       = OutValRdyBundle    (MemMsg(32,nWid).req)
    s.out_fsm      = OutValRdyBundle    (1)    # response to FSM
    s.out_neighbor = OutValRdyBundle[6] (nWid)

    # Queues

    s.memreq_q = SingleElementBypassQueue( MemReqMsg(32,nWid) )
    s.connect( s.memreq, s.memreq_q.deq )

    #s.memresp_q = SingleElementPipelinedQueue( MemRespMsg(16) )
    s.memresp_q = SingleElementBypassQueue( MemRespMsg(nWid) )
    s.connect( s.memresp, s.memresp_q.enq )

    # temporarily store destination for non-blocking loads
    s.memdes_q = NormalQueue(nMemInst, nDesField)

    # PE local register file
    s.rf = RegisterFile( nWid, nReg, 2 ) # 2 read ports

    # approx_mul
    # input is done by reqMsg(src0, src1) done in control plane.
    s.approx_mul = CombinationalApproxMult(nWid/2, 4)
    s.mul_msg = MymultReqMsg(nWid/2)

    # temporary variables

    s.src0_tmp = Wire( nWid )
    s.src1_tmp = Wire( nWid )
    s.des_tmp  = Wire( nWid )
    s.go       = Wire( 1 )
    s.go_req   = Wire( 1 )
    s.go_resp  = Wire( 1 )
    s.go_mul   = Wire( 1 )

    s.reqsent  = RegRst(1, 0)

  def elaborate_logic( s ):

    @s.combinational
    def logic():

      # initializing outputs
      s.in_control.rdy.value      = 0
      s.memresp_q.deq.rdy.value   = 0
      for i in range(6):
        s.in_neighbor[i].rdy.value  = 0

      s.memreq_q.enq.val.value    = 0
      s.memreq_q.enq.msg.value    = 0
      s.out_fsm.val.value         = 0      
      s.out_fsm.msg.value         = 0
      #s.approx_mul.req.val.value  = 0
      s.approx_mul.req.rdy.value = 1
      #s.approx_mul.resp.val.value = 0

      for i in range(6):
        s.out_neighbor[i].val.value = 0
        s.out_neighbor[i].msg.value = 0

      s.rf.wr_en.value            = 0
      s.go.value                  = 0
      s.go_req.value              = 0
      s.go_resp.value             = 0
      s.reqsent.in_.value         = s.reqsent.out
      s.go_mul.value              = 0

      #=========================================================================
      # pre-processing
      #=========================================================================
      # handle memory response
      if s.memresp_q.deq.val:

        s.go_resp.value = 1
        s.des_tmp.value = s.memresp_q.deq.msg.data

        # valid bit for local register
        if s.memdes_q.deq.msg[nDesField - 1]:
          s.rf.wr_addr.value = s.memdes_q.deq.msg[0:nLogReg]
          s.rf.wr_data.value = s.des_tmp

        for i in range(nLogReg, nDesField-1):
          if s.memdes_q.deq.msg[i]:
            s.out_neighbor[i-nLogReg].msg.value = s.des_tmp
            if not s.out_neighbor[i-nLogReg].rdy: s.go_resp.value = 0

      else:
        s.go_resp.value = 0

      if s.go_resp: # go_resp was set to one when memresp_q.deq happens.
        s.memdes_q.deq.rdy.value  = 1
        s.memresp_q.deq.rdy.value = 1

        for i in range(nLogReg, nDesField-1):
          if s.memdes_q.deq.msg[i]: s.out_neighbor[i-nLogReg].val.value = 1

        if s.memdes_q.deq.msg[nDesField - 1]: s.rf.wr_en.value = 1


      if s.in_control.val:
        #=========================================================================
        # load
        #=========================================================================
        if s.in_control.msg.ctl == LOAD:

          # send out memory request
          if s.memreq_q.enq.rdy and (s.reqsent.out == 0):
            s.go_req.value = 1
            s.memreq_q.enq.msg.type_.value  = MemReqMsg.TYPE_READ

            if s.in_control.msg.src0 < nReg:

              s.rf.rd_addr[0].value  = s.in_control.msg.src0
              s.src0_tmp.value       = s.rf.rd_data[0]

            elif s.in_control.msg.src0 >= nReg:
              # if neighbor is ready
              if s.in_neighbor[s.in_control.msg.src0 - nReg].val:

                s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0 - nReg].msg

              else: s.go_req.value = 0 # if neighbor not ready
              
            s.memreq_q.enq.msg.addr.value   = s.src0_tmp
            s.memreq_q.enq.msg.len.value    = 0

          # the go signal is primarily for if we cant get src0 or src1.
          else:
            s.go_req.value = 0
          # ---------------------------------------------

          # by now you should populated src0 and src1 of the instruction.
          if s.go_req: # check if ready to send out the request
            s.reqsent.in_.value = 1
            s.memreq_q.enq.val.value  = 1
            if s.in_control.msg.src0 >= nReg:
              s.in_neighbor[s.in_control.msg.src0 - nReg].rdy.value = 1

          # handle memory response
          if s.memresp_q.deq.val:
            s.go_resp.value = 1
            s.des_tmp.value = s.memresp_q.deq.msg.data

            if s.in_control.msg.des[nDesField - 1]:
              s.rf.wr_addr.value = s.in_control.msg.des[0:nLogReg]
              s.rf.wr_data.value = s.des_tmp

            for i in range(nLogReg, nDesField - 1):
              if s.in_control.msg.des[i]:
                s.out_neighbor[i - nLogReg].msg.value = s.des_tmp
                if not s.out_neighbor[i - nLogReg].rdy: s.go_resp.value = 0

          else:
            s.go_resp.value = 0

          if s.go_resp:
            s.in_control.rdy.value = 1
            s.reqsent.in_.value    = 0
            s.memresp_q.deq.rdy.value    = 1

            for i in range(nLogReg, nDesField - 1):
              if s.in_control.msg.des[i]:
                s.out_neighbor[i - nLogReg].val.value = 1
            if s.in_control.msg.des[nDesField - 1]:
              s.rf.wr_en.value = 1


        #=========================================================================
        # load-nonblocking
        #=========================================================================
        if s.in_control.msg.ctl == LOADNB:

          # send out memory request
          if s.memreq_q.enq.rdy:
            s.go.value = 1
            s.memreq_q.enq.msg.type_.value  = MemReqMsg.TYPE_READ

            if s.in_control.msg.src0 < nReg:

              s.rf.rd_addr[0].value  = s.in_control.msg.src0
              s.src0_tmp.value       = s.rf.rd_data[0]

            elif s.in_control.msg.src0 >= nReg:

              if s.in_neighbor[s.in_control.msg.src0 - nReg].val:

                s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0 - nReg].msg

              else: s.go.value = 0

            s.memreq_q.enq.msg.addr.value   = s.src0_tmp
            s.memreq_q.enq.msg.len.value    = 0

          else:
            s.go.value = 0

          if s.go:
            s.memdes_q.enq.val.value   = 1
            s.memdes_q.enq.msg.value   = s.in_control.msg.des
            s.memreq_q.enq.val.value = 1
            s.in_control.rdy.value   = 1
            if s.in_control.msg.src0 >= nReg:
              s.in_neighbor[s.in_control.msg.src0 - nReg].rdy.value = 1


        #=========================================================================
        # store
        #=========================================================================
        if s.in_control.msg.ctl == STORE:

          if s.memreq_q.enq.rdy and (s.reqsent.out == 0):
            s.go.value = 1
            s.memreq_q.enq.msg.type_.value = MemReqMsg.TYPE_WRITE
            s.memreq_q.enq.msg.len.value   = 0

            # src0: address
            if s.in_control.msg.src0 < nReg:
              s.rf.rd_addr[0].value   = s.in_control.msg.src0
              s.memreq_q.enq.msg.addr.value = s.rf.rd_data[0]

            elif s.in_control.msg.src0 >= nReg:
              if s.in_neighbor[s.in_control.msg.src0 - nReg].val:
                s.memreq_q.enq.msg.addr.value = s.in_neighbor[s.in_control.msg.src0 - nReg].msg
              else: s.go.value = 0

            # src1: data
            if s.in_control.msg.src1 < nReg:
              s.rf.rd_addr[1].value   = s.in_control.msg.src1
              s.memreq_q.enq.msg.data.value = s.rf.rd_data[1]

            elif s.in_control.msg.src1 >= nReg:
              if s.in_neighbor[s.in_control.msg.src1 - nReg].val:
                s.memreq_q.enq.msg.data.value = s.in_neighbor[s.in_control.msg.src1 - nReg].msg
              else: s.go.value = 0

          else:
            s.go.value = 0

          if s.go:
            s.reqsent.in_.value    = 1
            s.memreq_q.enq.val.value     = 1
            if s.in_control.msg.src0 >= nReg:
              s.in_neighbor[s.in_control.msg.src0 - nReg].rdy.value = 1
            if s.in_control.msg.src1 >= nReg:
              s.in_neighbor[s.in_control.msg.src1 - nReg].rdy.value = 1

          if s.memresp_q.deq.val:
            s.reqsent.in_.value    = 0
            s.memresp_q.deq.rdy.value    = 1
            s.in_control.rdy.value = 1


        #=========================================================================
        # store-sink
        #=========================================================================
        if s.in_control.msg.ctl == STORES:
          if s.memreq_q.enq.rdy:
            s.in_control.rdy.value  = 1
            s.rf.rd_addr[0].value   = s.in_control.msg.src0
            s.memreq_q.enq.val.value      = 1
            s.memreq_q.enq.msg.type_.value = MemReqMsg.TYPE_WRITE
            s.memreq_q.enq.msg.len.value   = 0
            s.memreq_q.enq.msg.data.value = s.rf.rd_data[0]


        #=========================================================================
        # compare-equal
        #=========================================================================

        if s.in_control.msg.ctl == CEQ:
          if s.out_fsm.rdy:
        
            s.go.value = 1

            # src0
            if s.in_control.msg.src0 < nReg:
              s.rf.rd_addr[0].value  = s.in_control.msg.src0
              s.src0_tmp.value       = s.rf.rd_data[0]

            elif s.in_control.msg.src0 >= nReg:
              if s.in_neighbor[s.in_control.msg.src0 - nReg].val:
                s.memreq_q.enq.msg.addr.value = s.in_neighbor[s.in_control.msg.src0 - nReg].msg
              else: s.go.value = 0
              
            # src1
            if s.in_control.msg.src1 < nReg:
              s.rf.rd_addr[1].value  = s.in_control.msg.src1
              s.src1_tmp.value       = s.rf.rd_data[1]

            elif s.in_control.msg.src1 >= nReg:
              if s.in_neighbor[s.in_control.msg.src1 - nReg].val:
                s.memreq_q.enq.msg.data.value = s.in_neighbor[s.in_control.msg.src1 - nReg].msg
              else: s.go.value = 0

            # compute
            if s.src0_tmp == s.src1_tmp: s.out_fsm.msg.value = 1
            else: s.out_fsm.msg.value = 0
       
            # set control signals
            if s.go:
              s.in_control.rdy.value = 1
              s.out_fsm.val.value    = 1
              if s.in_control.msg.src0 >= nReg:
                s.in_neighbor[s.in_control.msg.src0 - nReg].rdy.value = 1
              if s.in_control.msg.src1 >= nReg:
                s.in_neighbor[s.in_control.msg.src1 - nReg].rdy.value = 1


        #=========================================================================
        # compare-great-than
        #=========================================================================
        # We assume the result of CGT always goes to out_fsm. 
        # this is because CGT generates 1-bit control signal, which we assume will 
        # be handled by the FSM

        if (s.in_control.msg.ctl == CGT):
          s.go.value = 1
          # src0
          if s.in_control.msg.src0 < nReg:
            s.rf.rd_addr[0].value  = s.in_control.msg.src0
            s.src0_tmp.value       = s.rf.rd_data[0]

          elif s.in_control.msg.src0 >= nReg:
            if s.in_neighbor[s.in_control.msg.src0 - nReg].val:
              s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0 - nReg].msg
            else:
              s.go.value = 0


          # src1
          if s.in_control.msg.src1 < nReg:
            s.rf.rd_addr[1].value  = s.in_control.msg.src1
            s.src1_tmp.value       = s.rf.rd_data[1]

          elif s.in_control.msg.src1 >= nReg:
            if s.in_neighbor[s.in_control.msg.src1 - nReg].val:
              s.src1_tmp.value = s.in_neighbor[s.in_control.msg.src1 - nReg].msg
            else:
              s.go.value = 0

          # compute
          if s.src0_tmp > s.src1_tmp:
            s.des_tmp.value = 1
          else:
            s.des_tmp.value = 0

          # output
          # check msb of des to see if it is a write to its own registers
          if s.in_control.msg.des[nDesField - 1]:
            #signifies what register to write to, return list [0 < nLogReg] in [, , ,] format
            s.rf.wr_addr.value = s.in_control.msg.des[0:nLogReg]
            s.rf.wr_data.value = s.des_tmp

          # And check to see if outputing to neighboring ports. could be writing
          # to its own register as well as broadcasting the value to neighbors
          for i in range(nLogReg, nDesField - 1):
            if s.in_control.msg.des[i]:
              s.out_neighbor[i - nLogReg].msg.value = s.des_tmp
              if not s.out_neighbor[i - nLogReg].rdy:
                s.go.value = 0 # do not send to neighbor

          # set control signals. if s.go, means finished executing old, ready to
          # send out new instructions
          if s.go:
            # ready to receive new instruction
            s.in_control.rdy.value = 1
            # rdy for its own ports to accept neighboring values
            if s.in_control.msg.src0 >= nReg:
              s.in_neighbor[s.in_control.msg.src0 - nReg].rdy.value = 1
            if s.in_control.msg.src1 >= nReg:
              s.in_neighbor[s.in_control.msg.src1 - nReg].rdy.value = 1

            # for the output port, now outputting data.
            for i in range(nLogReg, nDesField - 1):
              # old instruction if there is to output to its neighbors
              if s.in_control.msg.des[i]:
                # set the output data to valid
                s.out_neighbor[i - nLogReg].val.value = 1

            # handles writing to its own internal register. check msb.
            if s.in_control.msg.des[nDesField - 1]:
              s.rf.wr_en.value = 1

        #=========================================================================
        # compare-equal-zero
        #=========================================================================
        if s.in_control.msg.ctl == CEZ:
          if s.out_fsm.rdy:
        
            s.go.value = 1

            # src0
            if s.in_control.msg.src0 < nReg:
              s.rf.rd_addr[0].value  = s.in_control.msg.src0
              s.src0_tmp.value       = s.rf.rd_data[0]

            elif s.in_control.msg.src0 >= nReg:
              if s.in_neighbor[s.in_control.msg.src0 - nReg].val:
                s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0 - nReg].msg
              else: s.go.value = 0
      
            # compute
            if s.src0_tmp == 0: s.out_fsm.msg.value = 1
            else: s.out_fsm.msg.value = 0
            
            # set control signals
            if s.go:
              s.in_control.rdy.value = 1
              s.out_fsm.val.value    = 1
              if s.in_control.msg.src0 >= nReg:
                s.in_neighbor[s.in_control.msg.src0 - nReg].rdy.value = 1


        #=========================================================================
        # copy
        #=========================================================================
        if s.in_control.msg.ctl == COPY:

          s.go.value = 1

          # src0
          if s.in_control.msg.src0 < nReg:
            s.rf.rd_addr[0].value  = s.in_control.msg.src0
            s.src0_tmp.value       = s.rf.rd_data[0]

          elif s.in_control.msg.src0 >= nReg:
            if s.in_neighbor[s.in_control.msg.src0 - nReg].val:
              s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0 - nReg].msg
            else:
              s.go.value = 0
      
          # compute
          s.des_tmp.value = s.src0_tmp


          # output
          if s.in_control.msg.des[nDesField - 1]:
            s.rf.wr_addr.value = s.in_control.msg.des[0:nLogReg]
            s.rf.wr_data.value = s.des_tmp

          for i in range(nLogReg, nDesField - 1):
            if s.in_control.msg.des[i]:
              s.out_neighbor[i - nLogReg].msg.value = s.des_tmp
              if not s.out_neighbor[i - nLogReg].rdy: s.go.value = 0


          # set control signals
          if s.go:
            s.in_control.rdy.value = 1
            if s.in_control.msg.src0 >= nReg:
              s.in_neighbor[s.in_control.msg.src0 - nReg].rdy.value = 1
            
            for i in range(nLogReg, nDesField - 1):
              if s.in_control.msg.des[i]:
                s.out_neighbor[i - nLogReg].val.value = 1
            if s.in_control.msg.des[nDesField - 1]:
              s.rf.wr_en.value = 1


        #=========================================================================
        # DEC
        #=========================================================================
        if s.in_control.msg.ctl == DEC:

          s.go.value = 1

          # src0
          if s.in_control.msg.src0 < nReg:
            s.rf.rd_addr[0].value  = s.in_control.msg.src0
            s.src0_tmp.value       = s.rf.rd_data[0]

          elif s.in_control.msg.src0 >= nReg:
            if s.in_neighbor[s.in_control.msg.src0 - nReg].val:
              s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0 - nReg].msg
            else:
              s.go.value = 0
      
          # compute
          s.des_tmp.value = s.src0_tmp - 1


          # output
          if s.in_control.msg.des[nDesField - 1]:
            s.rf.wr_addr.value = s.in_control.msg.des[0:nLogReg]
            s.rf.wr_data.value = s.des_tmp

          for i in range(nLogReg, nDesField):
            if s.in_control.msg.des[i]:
              s.out_neighbor[i - nLogReg].msg.value = s.des_tmp
              if not s.out_neighbor[i - nLogReg].rdy: s.go.value = 0


          # set control signals
          if s.go:
            s.in_control.rdy.value = 1
            if s.in_control.msg.src0 >= nReg:
              s.in_neighbor[s.in_control.msg.src0 - nReg].rdy.value = 1
            if s.in_control.msg.src1 >= nReg:
              s.in_neighbor[s.in_control.msg.src1 - nReg].rdy.value = 1
            
            for i in range(nLogReg, nDesField):
              if s.in_control.msg.des[i]:
                s.out_neighbor[i - nLogReg].val.value = 1
            if s.in_control.msg.des[nDesField - 1]:
              s.rf.wr_en.value = 1

        #=========================================================================
        # MUL
        #=========================================================================
        if (s.in_control.msg.ctl == MUL):
          # set the go.value temporarily to 1.
          s.go.value = 1
          s.go_mul.value = 1

          # getting src values
          # src0
          # print "grabbing src values"
          if s.in_control.msg.src0 < nReg:
            s.rf.rd_addr[0].value  = s.in_control.msg.src0
            s.src0_tmp.value       = s.rf.rd_data[0]

          elif s.in_control.msg.src0 >= nReg:
            if s.in_neighbor[s.in_control.msg.src0 - nReg].val:
              s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0 - nReg].msg
            else:
              s.go_mul.value = 0
              # print "src0.val:{}".format(s.in_neighbor[leftNbrL2].val)

          # src1
          if s.in_control.msg.src1 < nReg:
            s.rf.rd_addr[1].value  = s.in_control.msg.src1
            s.src1_tmp.value       = s.rf.rd_data[1]

          elif s.in_control.msg.src1 >= nReg:
            if s.in_neighbor[s.in_control.msg.src1 - nReg].val:
              s.src1_tmp.value = s.in_neighbor[s.in_control.msg.src1 - nReg].msg
            else:
              s.go_mul.value = 0
              # print "src1.val:{}".format(s.in_neighbor[leftNbrL4].val)

          #print "go:{},rdy:{}".format(s.go.value, s.approx_mul.req.rdy)
          if (s.go_mul.value and s.approx_mul.req.rdy): # successfully have src0 and src1
            s.mul_msg.set_msg(s.src0_tmp&0x00ff, s.src1_tmp&0x00ff)
            s.approx_mul.req.val.value = 1
            s.approx_mul.req.msg.value = s.mul_msg
            # print "s.req.msg:{}".format(s.approx_mul.req.msg)


          # output
          s.approx_mul.resp.rdy.value = 1

          if (s.approx_mul.resp.val):
            s.go.value = 1
            # check msb of des to see if it is a write to its own registers
            if s.in_control.msg.des[nDesField - 1]:
              #signifies what register to write to, return list [0 < nLogReg] in [, , ,] format
              s.rf.wr_addr.value = s.in_control.msg.des[0:nLogReg]
              s.rf.wr_data.value = s.approx_mul.resp.msg

            # And check to see if outputing to neighboring ports. could be writing
            # to its own register as well as broadcasting the value to neighbors
            for i in range(nLogReg, nDesField - 1):
              if s.in_control.msg.des[i]:
                s.out_neighbor[i - nLogReg].msg.value = s.approx_mul.resp.msg
                if not s.out_neighbor[i - nLogReg].rdy:
                  s.go.value = 0 # do not send to neighbor
          else:
            s.go.value = 0

          # set control signals. if s.go, means finished executing old, ready to
          # send out new instructions
          #print "s.go:{}".format(s.go)
          if (s.go): # could potentially, not ready to accept new instrs. but still
            #print "output"
            # ready to receive new instruction. the ports are not occupied any longer
            s.in_control.rdy.value = 1
            # rdy for its old input ports to accept new values
            if s.in_control.msg.src0 >= nReg:
              s.in_neighbor[s.in_control.msg.src0 - nReg].rdy.value = 1
            if s.in_control.msg.src1 >= nReg:
              s.in_neighbor[s.in_control.msg.src1 - nReg].rdy.value = 1

            # for the output port, now outputting data.
            for i in range(nLogReg, nDesField - 1):
              # old instruction if there is to output to its neighbors
              if s.in_control.msg.des[i]:
                # set the output data to valid
                s.out_neighbor[i - nLogReg].val.value = 1

            # handles writing to its own internal register. check msb.
            if s.in_control.msg.des[nDesField - 1]:
              s.rf.wr_en.value = 1
              #s.approx_mul.req.val.value = 0


        #=========================================================================
        # two-operand arithmetic
        #=========================================================================
        if (s.in_control.msg.ctl == ADD) \
            or (s.in_control.msg.ctl == SUB):
          s.go.value = 1
          # src0
          if s.in_control.msg.src0 < nReg:
            s.rf.rd_addr[0].value  = s.in_control.msg.src0
            s.src0_tmp.value       = s.rf.rd_data[0]

          elif s.in_control.msg.src0 >= nReg:
            if s.in_neighbor[s.in_control.msg.src0 - nReg].val:
              s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0 - nReg].msg
            else:
              s.go.value = 0
      
            
          # src1
          if s.in_control.msg.src1 < nReg:
            s.rf.rd_addr[1].value  = s.in_control.msg.src1
            s.src1_tmp.value       = s.rf.rd_data[1]

          elif s.in_control.msg.src1 >= nReg:
            if s.in_neighbor[s.in_control.msg.src1 - nReg].val:
              s.src1_tmp.value = s.in_neighbor[s.in_control.msg.src1 - nReg].msg
            else:
              s.go.value = 0

          # compute
          if s.in_control.msg.ctl == ADD:
            s.des_tmp.value = s.src0_tmp + s.src1_tmp
          elif s.in_control.msg.ctl == SUB:
            s.des_tmp.value = s.src0_tmp - s.src1_tmp

          # output
          # check msb of des to see if it is a write to its own registers
          if s.in_control.msg.des[nDesField - 1]:
            #signifies what register to write to, return list [0 < nLogReg] in [, , ,] format
            s.rf.wr_addr.value = s.in_control.msg.des[0:nLogReg]
            s.rf.wr_data.value = s.des_tmp

          # And check to see if outputing to neighboring ports. could be writing
          # to its own register as well as broadcasting the value to neighbors
          for i in range(nLogReg, nDesField - 1):
            if s.in_control.msg.des[i]:
              s.out_neighbor[i - nLogReg].msg.value = s.des_tmp
              if not s.out_neighbor[i - nLogReg].rdy:
                s.go.value = 0 # do not send to neighbor

          # set control signals. if s.go, means finished executing old, ready to
          # send out new instructions
          if s.go:
            # ready to receive new instruction
            s.in_control.rdy.value = 1
            # rdy for its own ports to accept neighboring values
            if s.in_control.msg.src0 >= nReg:
              s.in_neighbor[s.in_control.msg.src0 - nReg].rdy.value = 1
            if s.in_control.msg.src1 >= nReg:
              s.in_neighbor[s.in_control.msg.src1 - nReg].rdy.value = 1

            # for the output port, now outputting data.
            for i in range(nLogReg, nDesField - 1):
              # old instruction if there is to output to its neighbors
              if s.in_control.msg.des[i]:
                # set the output data to valid
                s.out_neighbor[i - nLogReg].val.value = 1

            # handles writing to its own internal register. check msb.
            if s.in_control.msg.des[nDesField - 1]:
              s.rf.wr_en.value = 1


        #=========================================================================
        # addition/multiplication-immediate
        #=========================================================================
        if (s.in_control.msg.ctl == ADDI)\
            or (s.in_control.msg.ctl == MULI):

          s.go.value = 1

          # src0: immediate
          s.src0_tmp.value = s.in_control.msg.src0

          # src1
          if s.in_control.msg.src1 < nReg:
            s.rf.rd_addr[1].value  = s.in_control.msg.src1
            s.src1_tmp.value       = s.rf.rd_data[1]

          elif s.in_control.msg.src1 >= nReg:
            if s.in_neighbor[s.in_control.msg.src1 - nReg].val:
              s.src1_tmp.value = s.in_neighbor[s.in_control.msg.src1 - nReg].msg
            else:
              s.go.value = 0 # if the src data is not ready change s.go back

          # compute
          if s.in_control.msg.ctl == ADDI:
            s.des_tmp.value = s.src0_tmp + s.src1_tmp
          elif s.in_control.msg.ctl == MULI:
            s.des_tmp.value = s.src0_tmp * s.src1_tmp


          # output
          if s.in_control.msg.des[nDesField - 1]:
            s.rf.wr_addr.value = s.in_control.msg.des[0:nLogReg]
            s.rf.wr_data.value = s.des_tmp

          for i in range(nLogReg, nDesField):
            if s.in_control.msg.des[i]:
              s.out_neighbor[i - nLogReg].msg.value = s.des_tmp
              if not s.out_neighbor[i - nLogReg].rdy: s.go.value = 0


          # set control signals
          if s.go:
            s.in_control.rdy.value = 1
            if s.in_control.msg.src1 >= nReg:
              s.in_neighbor[s.in_control.msg.src1 - nReg].rdy.value = 1
            
            for i in range(nLogReg, nDesField):
              if s.in_control.msg.des[i]:
                s.out_neighbor[i - nLogReg].val.value = 1
            if s.in_control.msg.des[nDesField - 1]:
              s.rf.wr_en.value = 1



  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace_neuron( s ):

    inst2char = {
      0 : "LD  ",
      1 : "ST  ",
      2 : "CGT ",
      3 : "SUB ",
      4 : "CEZ ",
      5 : "ADD ",
      6 : "MUL ",
      7 : "COPY",
      8 : "DEC ",
      9 : "CEQ ",
      10: "ADDI",
      11: "MULI",
      12: "STS ",
      13: "LDNB",
    }

    #s.inst_str = inst2char[s.in_control.msg.ctl.uint()]

    if s.in_control.rdy:
      s.inst_str = inst2char[s.in_control.msg.ctl.uint()]
    else: s.inst_str = "#   "

    return " {}   {},{} > {}" \
      .format( s.inst_str, s.src0_tmp, s.src1_tmp, s.out_neighbor[rightNbrL1])

  def line_trace_step_func( s ):
    inst2char = {
      0 : "LD  ",
      1 : "ST  ",
      2 : "CGT ",
      3 : "SUB ",
      4 : "CEZ ",
      5 : "ADD ",
      6 : "MUL ",
      7 : "COPY",
      8 : "DEC ",
      9 : "CEQ ",
      10: "ADDI",
      11: "MULI",
      12: "STS ",
      13: "LDNB",
    }

    #s.inst_str = inst2char[s.in_control.msg.ctl.uint()]

    if s.in_control.rdy:
      s.inst_str = inst2char[s.in_control.msg.ctl.uint()]
    else:
      s.inst_str = "#   "

    # write to file
    if (s.inst_str == "CGT "):
      # write to a file
      step_func_result.append(int(s.des_tmp))

    return " {} {} > {}" \
      .format( s.inst_str, s.src0_tmp, s.des_tmp)

