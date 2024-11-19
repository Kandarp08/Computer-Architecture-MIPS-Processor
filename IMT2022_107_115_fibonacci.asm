#run in linux terminal by java -jar Mars4_5.jar nc filename.asm(take inputs from console)

#system calls by MARS simulator:
#http://courses.missouristate.edu/kenvollmar/mars/help/syscallhelp.html
.data
	next_line: .asciiz "\n"
	inp_statement: .asciiz "No. of fibonacci numbers to be calculated: "
	inp_int_statement: .asciiz "Enter starting address of numbers (in decimal format): "
	out_int_statement: .asciiz "Enter starting address of outputs (in decimal format): "
	enter_int: .asciiz "Enter the integer: "	
.text
#input: N= how many numbers to sort should be entered from terminal. 
#It is stored in $t1
jal print_inp_statement	
jal input_int 
move $t1,$t4			

#input: Y=The Starting address of first n fibonacci numbers 
#(each 32bits) stored in the memory. It is stored in $t2.
jal print_inp_int_statement
jal input_int
move $t2,$t4
       
#############################################################
#Do not change any code above this line
#Occupied registers $t1,$t2. Don't use them in your function.
#############################################################
#function: 

add $s0, $0, $0 # Analogous to a
addi $s1, $0, 1 # Analogous to b

sw $s0, 0($t2)
sw $s1, 4($t2)

addi $t3, $t2, 8 # Memory location where number has to be written
addi $t4, $0, 2 # Iteration variable

calculateNumbers: 

	beq $t4, $t1, endfunction
		
	add $s2, $s0, $s1
	sw $s2, 0($t3)
	add $s0, $s1, $0
	add $s1, $s2, $0
	
	addi $t4, $t4, 1
	addi $t3, $t3, 4

	j calculateNumbers
	
endfunction:
#endfunction
#############################################################
#You need not change any code below this line

#print sorted numbers
move $s7,$zero	#i = 0
loop: beq $s7,$t1,end
      lw $t4,0($t2)
      jal print_int
      jal print_line
      addi $t2,$t2,4
      addi $s7,$s7,1
      j loop 
#end
end:  li $v0,10
      syscall
#input from command line(takes input and stores it in $t6)
input_int: li $v0,5
	   syscall
	   move $t4,$v0
	   jr $ra
#print integer(prints the value of $t6 )
print_int: li $v0,1	
	   move $a0,$t4
	   syscall
	   jr $ra
#print nextline
print_line:li $v0,4
	   la $a0,next_line
	   syscall
	   jr $ra

#print number of inputs statement
print_inp_statement: li $v0,4
		la $a0,inp_statement
		syscall 
		jr $ra
#print input address statement
print_inp_int_statement: li $v0,4
		la $a0,inp_int_statement
		syscall 
		jr $ra
#print output address statement
print_out_int_statement: li $v0,4
		la $a0,out_int_statement
		syscall 
		jr $ra
#print enter integer statement
print_enter_int: li $v0,4
		la $a0,enter_int
		syscall 
		jr $ra
