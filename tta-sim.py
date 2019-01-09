

mem = [
	# word
	#   S  D I        Mem
	#  {-}{-}|{-----------------------}
	#0b00010011111111111111111111111111,
	#0b00010000000000000000000000000001, 0xffffffff
	0b00000110000000000000000000000001, 0b00001111111111111111111111111111, 0xffffffff
]


R = {
	0: 0,
	"RA" : 0,
	"RB" : 0,
	"RC" : 0,
	"RD" : 0, # dummy, not really needed
	"PC" : 0,
}


# Instruction: S[3], D[3], I, Mem
mask_32 = 0xffffffff
mask_s = 0xe0000000
mask_d = 0x1c000000
mask_m = 0x01ffffff
mask_i = 0x02000000
mask_m_sign = 0x01000000
sign_m = 0xfe000000

# S: 0, RC, PC, 
# D: RA, RB, RD, PC
index_s = [0, "RC", "PC"]
index_d = [0, "RA", "RB", "RD", "PC"]

### pipeline
source_ppl = 0
destination_ppl = 0
mem_ppl = 0
write_flag = 0
stage2 = False
ppl_stall = False
ppl_stall_next = False
while True:
	PC_next = R["PC"] + 1
	##########################
	# Pipeline stage 2
	if stage2:
		if write_flag:
			# write
			mem[mem_ppl] = source_ppl
		else:
			if index_d[destination_ppl] == "PC":
				print "PC"
				PC_next = mem[mem_ppl]
			else:
				R[index_d[destination_ppl]] = mem[mem_ppl]
				R["RC"] = R["RB"] - R["RA"]
			if ppl_stall:
				ppl_stall_next = False
	##########################
	# Pipeline stage 1
	if ppl_stall:
		print "stall"
		stage2 = False
		#R["RC"] = R["RB"] - R["RA"]
		ppl_stall = ppl_stall_next
		R["PC"] = PC_next
		continue
	if R["PC"] == 0xffffffff:
		break
	instruction = mem[R["PC"]] & mask_32
	
	S = (instruction & mask_s) >> 29
	D = (instruction & mask_d) >> 26
	M = instruction & mask_m
	I = instruction & mask_i > 0
	
	if (M & mask_m_sign) > 0:
		M += sign_m
	#print R["PC"], instruction, S, index_s[S], D, index_d[D], M, I, PC_next
	if S == 0:
		# if S == 0, D != 0
		if I:
			# instance mode
			if index_d[D] == "RD":
				#print "C:", R["RC"]
				if not I:
					raise Exception
				R["RD"] = M # can be ommited
				stage2 = False
				if R["RC"] < 0:
					PC_next = M
				#print "PC_next:", PC_next, M, R["RC"] < 0
			elif index_d[D] == "PC":
				PC_next = M
				stage2 = False
			else:
				R[index_d[D]] = M
				stage2 = False
		else:
			# memory access mode
			stage2 = True
			write_flag = False
			mem_ppl = M
			destination_ppl = D
			if index_d[D] == "PC":
				ppl_stall_next = True
	else:
		if D == 0:
			# reg write memory
			if I:
				raise Exception
				
			stage2 = True
			write_flag = True
			
			source_ppl = R[index_s[S]]
			mem_ppl = M
		else:
			# reg write reg
			R[index_d[D]] = R[index_s[S]]
			stage2 = False
	
	R["RC"] = R["RB"] - R["RA"]
	ppl_stall = ppl_stall_next
	R["PC"] = PC_next

print R
print mem
	




"""
# sample program mult
L000:
0, $A
arg1, $B
$C, a
arg2, $B
$C, b
1, $A
a, $B
L010, $D
0, $A
0, $B
$C, sign
L020, $PC
L010:
a, $A
0, $B
$C, a
1, $B
$C, sign
L020:
1, $A
b, $B
L030, $D
0, $A
-32, $B
$C, count,
L050, $PC
L030:
b, $A
0, $B
$C, b
sign, $A
-1, $B
$C, sign
L040:
32, $A
0, $B
$C, count
L050:
0, $A
0, $B
$C, hi
$C, lo
L100:
hi, $A
0, $B
$C, $A
hi, $B
$C, hi
lo, $A
-1, $B
L110, $D
-1, $A
hi, $B
$C, hi
L110:
lo, $A
0, $B
$C, $A
lo, $B
$C, lo
a, $A
-1, $B
L800, $D
L200:
b, $A
0, $B
$C, $A
lo, $B
$C, lo
L300, $D
0, $A
b, $B
L500, $D
b, $A
lo, $B
L500, $D
L800, $PC
L300:
b, $A
-1, $B
L800, $D
b, $A
lo, $B
L800, $D
L500:
-1, $A
hi, $B
$C, hi
L800:
a, $A
0, $B
$C, $A
a, $B
$C, a
-1, $A
count, $B
$C, count
L100, $D
L900:
sign, $A
-1, $B
L990, $D
lo, $A
0, $B
$C, lo
hi, $A
$C, hi
L990:
HALT, $PC

arg1: 2147483647
arg2: -2147483648

count:0
a:0
b:0
hi:0
lo:0
sign:0


"""