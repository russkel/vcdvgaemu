This Python script draws VGA frames from a VCD dump (likely from Icarus Verilog).

It requires python 3, matplotlib, numpy and pyparsing libraries. (`pip install matplotlib numpy pyparsing`)

You need to modify (make a copy of) your test bench file and modify it so only the required signals are dumped, otherwise the resulting dump will be a few hundred megabyte dump. Large VCD files will take a long time for Python to parse:
 
```vhdl
`timescale 1ns / 1ps

module TB_yourproject;
	// Inputs
    // snip snip

	// Instantiate the Unit Under Test (UUT)
	yourproject uut (
		//snip snip
	);

    initial begin
       $dumpfile("vga_data.vcd");
       $dumpvars(0, 
               uut.vga.vert_sync,
               uut.vga.horiz_sync,
               uut.image_generator.pixel_R,
               uut.image_generator.pixel_G,
               uut.image_generator.pixel_B
        );
    end
	
	initial begin: stopat
	    #34000000; $finish; // 1x Vert scan = 416800 clocks * 40n = 16672000 ns
	end
      
endmodule

```

Compile and run your modified test bench to generate the VGA signal only VCD.

You must specify the full path to the VSYNC, Red, Blue and Green variables when calling `vcdvga.py`. Using the above testbench as an example, noting that the VCD dump will be written to `vga_data.vcd`:

```python3 vcdvga.py -V "TB_yourproject.uut.vga.vert_sync" -R "TB_yourproject.uut.image_generator.pixel_R" -G "TB_yourproject.uut.image_generator.pixel_G" -B "TB_yourproject.uut.image_generator.pixel_B" path/to/vga_data.vcd```

And then the frame will draw to the screen.