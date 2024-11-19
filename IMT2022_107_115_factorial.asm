jal input_int
move $t3,$t4 

addi $t1, $0, 10
addi $t2, $0, 1
sw $t2, 0($t3)

calculateFactorials:

	beq $t2, $t1, endfunction
		
	addi $t2, $t2, 1
	lw $s0, 0($t3)
	addi $t3, $t3, 4
	
	mul $s1, $s0, $t2 
	sw $s1, 0($t3)
		
	j calculateFactorials
	
endfunction: 
	li $v0,10
      	syscall

#input from command line(takes input and stores it in $t4)
input_int: li $v0,5
	   syscall
	   move $t4,$v0
	   jr $ra