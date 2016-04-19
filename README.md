*Approximate Multiplier Perceptron for Coarse Grain Reconfigurable Array Architecture*



This project is part of my Master of Engineering project that explores coarse-grained reconfigurable array (CGRA) architecture. This particular repo implements a perceptron (https://en.wikipedia.org/wiki/Perceptron) that integrates with an approximate multiplier using CGRA.

**see perceptron_result_documentation.pdf for a summary**

Detailed description of my overall project:
With the increasing popularity of modern computing applications such as image processing and machine learning, there arises a need for finding platforms that excel in performance, low power consumption, and flexibility. One of the most challenging design choice on selecting suitable architectures has often been balancing programmability and performance. On the spectrum of suitable hardware platforms for modern computing applications, ASIC design dominates the high efficiency low programmability end. On the opposite spectrum, general- purpose microcontroller dominates on the low efficiency and high programmability end. The alternative choice to those traditional architectures is coarse-grained reconfigurable array (CGRA), which well balances the trade off of performance, area, power consumption efficiency and programmability.

This design project aims to develop and explore the computational unit—processing element (PE), which are building blocks of the CGRA architecture. This project also explores utilizing the CGRA networks to perform sorting operations as well as constructing micro-processing engines for accelerating machine learning algorithms using artificial neural networks.
The primary tool used in the project is PyMTL, a Python-based hardware design language developed at Cornell’s Computer Systems Lab. PyMTL exhibits more concise syntax than traditional HDL language such as Verilog, and allows rapid development to create various models. Over the course of the project we have followed the development cycle of functional level, cycle level and register-transfer-level modeling for both the PE and CGRA network.
