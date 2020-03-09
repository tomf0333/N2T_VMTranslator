import os
import sys
from pathlib import Path

label_counter = 0
return_counter = 0
function_name = "main"
VM_FILE = 1
PUSH = "push"
POP = "pop"
ADD = "add"
SUBTRUCT = "sub"
NEGATE = "neg"
EQUALS = "eq"
GREATER_THEN = "gt"
LOWER_THEN = "lt"
AND = "and"
OR = "or"
NOT = "not"
LABEL = "label"
GOTO = "goto"
IFGOTO = "if-goto"
FUNCTION = "function"
CALL = "call"
RETURN = "return"
CONSTANT = "constant"
LOCAL = "local"
THIS = "this"
THAT = "that"
ARGUMENT = "argument"
STATIC = "static"
TEMP = "temp"
POINTER = "pointer"


def first_pass(lines):
    """
    goes over the lines given and omits whitespace and comments
    for convenience.
    :param lines: (list) the lines we go through.
    :return: (list) the new lines, without whitespace and comments.
    """
    new_lines = list()
    for line in lines:
        if line.startswith(FUNCTION) or line.startswith(CALL):
            if "/" in line:
                line = line[0:line.index("/")]
            if len(line) == 0:
                continue
            else:
                new_lines.append(line)
        else:
            line = "".join(line.split())
            if "/" in line:
                line = line[0:line.index("/")]
            if len(line) == 0:
                continue
            else:
                if line != "\n" and line[0] != "/":
                    new_lines.append(line)
    return new_lines


def read_file_in_args(file_name):
    """
    reads for the file given and stores each line in a list.
    :param file_name: (str) the name of the file we read.
    :return: (list) the list that stores the lines.
    """
    with open(file_name, "r") as file:
        lines = list()
        for line in file:
            lines.append(line)
    return lines


def convert_lines(lines, file_name):
    """
    receives a list of lines in vm code and converts each one to hack
    Assembly language.
    :param lines: (list) the lines in vm code.
    :param file_name: (str) the vm file name (for static).
    :return: (list) the same lines in hack Assembly.
    """
    assembly_lines = list()
    for line in lines:
        # for each line in vm code the convert line will produce a few lines,
        # represented in a list so we must go over them all.
        converted_list = convert_line(line, file_name)
        for converted_line in converted_list:
            assembly_lines.append(converted_line)
    return assembly_lines


def convert_line(line, file_name):
    """
    converts a single line of vm code to however many lines it is in the
    hack assembly language.
    :param line: (str) the vm line.
    :param file_name: (str) the vm file name (for static).
    :return: (list) a list of assembly commands that represent the one line
    of vm code.
    """
    assembly_lines = list()
    global return_counter
    global function_name
    # first check if it is a push/pop/arithmetic/logic command.
    if line.startswith(PUSH):
        # we will look at the line without the "push" start, named line 2 for
        # the "second part" of the line, then we will break its second part
        # as well for the number, named line3 for the "third part" of the
        # command.
        line2 = line[len(PUSH):]
        if line2.startswith(CONSTANT):
            line3 = line2[len(CONSTANT):]
            assembly_lines = convert_constant(line3)
        elif line2.startswith(LOCAL):
            line3 = line2[len(LOCAL):]
            assembly_lines = convert_push_local(line3)
        elif line2.startswith(THIS):
            line3 = line2[len(THIS):]
            assembly_lines = convert_push_this(line3)
        elif line2.startswith(THAT):
            line3 = line2[len(THAT):]
            assembly_lines = convert_push_that(line3)
        elif line2.startswith(ARGUMENT):
            line3 = line2[len(ARGUMENT):]
            assembly_lines = convert_push_argument(line3)
        elif line2.startswith(STATIC):
            line3 = line2[len(STATIC):]
            assembly_lines = convert_push_static(line3, file_name)
        elif line2.startswith(TEMP):
            line3 = line2[len(TEMP):]
            assembly_lines = convert_push_temp(line3)
        elif line2.startswith(POINTER):
            line3 = line2[len(POINTER):]
            assembly_lines = convert_push_pointer(line3)
    elif line.startswith(POP):
        # we will look at the line without the "pop" start, same as with push.
        line2 = line[len(POP):]
        if line2.startswith(LOCAL):
            line3 = line2[len(LOCAL):]
            assembly_lines = convert_pop_local(line3)
        elif line2.startswith(THIS):
            line3 = line2[len(THIS):]
            assembly_lines = convert_pop_this(line3)
        elif line2.startswith(THAT):
            line3 = line2[len(THAT):]
            assembly_lines = convert_pop_that(line3)
        elif line2.startswith(ARGUMENT):
            line3 = line2[len(ARGUMENT):]
            assembly_lines = convert_pop_argument(line3)
        elif line2.startswith(STATIC):
            line3 = line2[len(STATIC):]
            assembly_lines = convert_pop_static(line3, file_name)
        elif line2.startswith(TEMP):
            line3 = line2[len(TEMP):]
            assembly_lines = convert_pop_temp(line3)
        elif line2.startswith(POINTER):
            line3 = line2[len(POINTER):]
            assembly_lines = convert_pop_pointer(line3)
    elif line.startswith(LABEL):
        line2 = line[len(LABEL):]
        assembly_lines = convert_label(line2, function_name)
    elif line.startswith(GOTO):
        line2 = line[len(GOTO):]
        assembly_lines = convert_goto(line2, function_name)
    elif line.startswith(IFGOTO):
        line2 = line[len(IFGOTO):]
        assembly_lines = convert_ifgoto(line2, function_name)
    elif line.startswith(FUNCTION):
        func_line = line.split(" ")
        # 1 is the function name and 2 is the number of variables.
        assembly_lines = convert_function(func_line[1], func_line[2])
    elif line.startswith(CALL):
        return_counter += 1
        call_line = line.split(" ")
        # 1 is the function name and 2 is the number of arguments.
        assembly_lines = convert_call(call_line[1], call_line[2],
                                      return_counter)
    elif line.startswith(RETURN):
        assembly_lines = convert_return()
    else:
        # for better code understanding i chose to use a function for each
        # translation as each adds many separate lines.
        if line.startswith(ADD):
            assembly_lines = convert_add()
        elif line.startswith(SUBTRUCT):
            assembly_lines = convert_sub()
        elif line.startswith(NEGATE):
            assembly_lines = convert_neg()
        elif line.startswith(EQUALS):
            assembly_lines = convert_eq()
        elif line.startswith(GREATER_THEN):
            assembly_lines = convert_gt()
        elif line.startswith(LOWER_THEN):
            assembly_lines = convert_lt()
        elif line.startswith(AND):
            assembly_lines = convert_and()
        elif line.startswith(OR):
            assembly_lines = convert_or()
        elif line.startswith(NOT):
            assembly_lines = convert_not()
    return assembly_lines


def convert_return():
    lines = list()
    # save return address
    lines.append("@5")
    lines.append("D=A")
    lines.append("@LCL")
    lines.append("A=M-D")
    lines.append("D=M")
    lines.append("@return_address")
    lines.append("M=D")
    # *ARG = pop()
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("@ARG")
    lines.append("A=M")
    lines.append("M=D")
    # SP = ARG + 1
    lines.append("@ARG")
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=D+1")
    # reposition that
    lines.append("@1")
    lines.append("D=A")
    lines.append("@LCL")
    lines.append("A=M-D")
    lines.append("D=M")
    lines.append("@THAT")
    lines.append("M=D")
    # reposition this
    lines.append("@2")
    lines.append("D=A")
    lines.append("@LCL")
    lines.append("A=M-D")
    lines.append("D=M")
    lines.append("@THIS")
    lines.append("M=D")
    # reposition arg
    lines.append("@3")
    lines.append("D=A")
    lines.append("@LCL")
    lines.append("A=M-D")
    lines.append("D=M")
    lines.append("@ARG")
    lines.append("M=D")
    # reposition lcl
    lines.append("@4")
    lines.append("D=A")
    lines.append("@LCL")
    lines.append("A=M-D")
    lines.append("D=M")
    lines.append("@LCL")
    lines.append("M=D")
    # goto ret
    lines.append("@return_address")
    lines.append("A=M")
    lines.append("0;JMP")
    return lines


def convert_call(func_name, n_args, ret_counter):
    lines = list()
    # push return address
    lines.append("@" + func_name + "$ret" + str(ret_counter))
    lines.append("D=A")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    # push LCL
    lines.append("@LCL")
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    # push ARG
    lines.append("@ARG")
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    # push THIS
    lines.append("@THIS")
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    # push THAT
    lines.append("@THAT")
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    # ARG = SP - n - 5
    lines.append("@" + str(int(n_args) + 5))
    lines.append("D=A")
    lines.append("@SP")
    lines.append("D=M-D")
    lines.append("@ARG")
    lines.append("M=D")
    # LCL = SP
    lines.append("@SP")
    lines.append("D=M")
    lines.append("@LCL")
    lines.append("M=D")
    # goto function
    lines.append("@" + func_name)
    lines.append("0;JMP")
    # set return address label
    lines.append(
        "(" + func_name + "$ret" + str(ret_counter) + ")")
    ret_counter += 1
    return lines


def convert_function(func_name, n_vars):
    lines = list()
    lines.append("(" + func_name + ")")
    for i in range(int(n_vars)):
        lines.append("@SP")
        lines.append("M=M+1")
        lines.append("A=M-1")
        lines.append("M=0")
    return lines


def convert_ifgoto(label_name, func_name):
    lines = list()
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@" + func_name + "$" + label_name)
    lines.append("D;JNE")
    return lines


def convert_goto(label_name, func_name):
    lines = list()
    lines.append("@" + func_name + "$" + label_name)
    lines.append("0;JMP")
    return lines


def convert_label(label_name, func_name):
    lines = list()
    lines.append(
        "(" + func_name + "$" + label_name + ")")
    return lines


def convert_constant(num):
    """
    the function for converting a push constant num command.
    :param num: (str) the number of the constant we want to add to the stack,
    as a string.
    :return: (list) a list of Assembly commands that produce the push
    constant num command.
    """
    lines = list()
    lines.append("@" + num)
    lines.append("D=A")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    return lines


def convert_push_local(i):
    """
    the function for converting a push local i command.
    :param i: (str) the index location in the local segment of the item we
    want to add to the stack, as a string.
    :return: (list) a list of Assembly commands that produce the push
    local i command.
    """
    lines = list()
    lines.append("@" + i)
    lines.append("D=A")
    lines.append("@LCL")
    lines.append("A=D+M")
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    return lines


def convert_pop_local(i):
    """
    the function for converting a pop local i command.
    :param i: (str) the index location in the local segment where we will add
    the stack top to, as a string.
    :return: (list) a list of Assembly commands that produce the pop
    local i command.
    """
    lines = list()
    lines.append("@" + i)
    lines.append("D=A")
    lines.append("@LCL")
    lines.append("D=D+M")
    lines.append("@local" + i)
    lines.append("M=D")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@local" + i)
    lines.append("A=M")
    lines.append("M=D")
    return lines


def convert_push_argument(i):
    """
    the function for converting a push argument i command.
    :param i: (str) the index location in the argument segment of the item we
    want to add to the stack, as a string.
    :return: (list) a list of Assembly commands that produce the push
    argument i command.
    """
    lines = list()
    lines.append("@" + i)
    lines.append("D=A")
    lines.append("@ARG")
    lines.append("A=D+M")
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    return lines


def convert_pop_argument(i):
    """
    the function for converting a pop argument i command.
    :param i: (str) the index location in the argument segment where we will
    add the stack top to, as a string.
    :return: (list) a list of Assembly commands that produce the pop
    argument i command.
    """
    lines = list()
    lines.append("@" + i)
    lines.append("D=A")
    lines.append("@ARG")
    lines.append("D=D+M")
    lines.append("@argument" + i)
    lines.append("M=D")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@argument" + i)
    lines.append("A=M")
    lines.append("M=D")
    return lines


def convert_push_this(i):
    """
    the function for converting a push this i command.
    :param i: (str) the index location in the this segment of the item we
    want to add to the stack, as a string.
    :return: (list) a list of Assembly commands that produce the push
    this i command.
    """
    lines = list()
    lines.append("@" + i)
    lines.append("D=A")
    lines.append("@THIS")
    lines.append("A=D+M")
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    return lines


def convert_pop_this(i):
    """
    the function for converting a pop this i command.
    :param i: (str) the index location in the this segment where we will
    add the stack top to, as a string.
    :return: (list) a list of Assembly commands that produce the pop
    this i command.
    """
    lines = list()
    lines.append("@" + i)
    lines.append("D=A")
    lines.append("@THIS")
    lines.append("D=D+M")
    lines.append("@this" + i)
    lines.append("M=D")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@this" + i)
    lines.append("A=M")
    lines.append("M=D")
    return lines


def convert_push_that(i):
    """
    the function for converting a push that i command.
    :param i: (str) the index location in the that segment of the item we
    want to add to the stack, as a string.
    :return: (list) a list of Assembly commands that produce the push
    that i command.
    """
    lines = list()
    lines.append("@" + i)
    lines.append("D=A")
    lines.append("@THAT")
    lines.append("A=D+M")
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    return lines


def convert_pop_that(i):
    """
    the function for converting a pop that i command.
    :param i: (str) the index location in the that segment where we will
    add the stack top to, as a string.
    :return: (list) a list of Assembly commands that produce the pop
    that i command.
    """
    lines = list()
    lines.append("@" + i)
    lines.append("D=A")
    lines.append("@THAT")
    lines.append("D=D+M")
    lines.append("@that" + i)
    lines.append("M=D")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@that" + i)
    lines.append("A=M")
    lines.append("M=D")
    return lines


def convert_push_temp(i):
    """
    the function for converting a push temp i command.
    :param i: (str) the index location in the temp segment of the item we
    want to add to the stack, as a string.
    :return: (list) a list of Assembly commands that produce the push
    temp i command.
    """
    lines = list()
    lines.append("@" + str(int(i) + 5))
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    return lines


def convert_pop_temp(i):
    """
    the function for converting a pop temp i command.
    :param i: (str) the index location in the temp segment where we will
    add the stack top to, as a string.
    :return: (list) a list of Assembly commands that produce the pop
    temp i command.
    """
    lines = list()
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@" + str(int(i) + 5))
    lines.append("M=D")
    return lines


def convert_push_pointer(i):
    """
    the function for converting a push pointer i command.
    :param i: (str) the index location in the pointer segment of the item we
    want to add to the stack (1/0), as a string.
    :return: (list) a list of Assembly commands that produce the push
    pointer i command.
    """
    global label_counter
    lines = list()
    lines.append("@" + i)
    lines.append("D=A")
    lines.append("@NOT_THIS" + str(label_counter))
    lines.append("D;JNE")
    lines.append("@THIS")
    lines.append("D=M")
    lines.append("@WRITE" + str(label_counter))
    lines.append("0;JMP")
    lines.append("(NOT_THIS" + str(label_counter) + ")")
    lines.append("@THAT")
    lines.append("D=M")
    lines.append("(WRITE" + str(label_counter) + ")")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    label_counter += 1
    return lines


def convert_pop_pointer(i):
    """
    the function for converting a pop pointer i command.
    :param i: (str) the index location in the pointer segment where we will
    add the stack top to, as a string.
    :return: (list) a list of Assembly commands that produce the pop
    pointer i command.
    """
    global label_counter
    lines = list()
    lines.append("@" + i)
    lines.append("D=A")
    lines.append("@NOT_THIS" + str(label_counter))
    lines.append("D;JNE")
    lines.append("@THIS")
    lines.append("D=A")
    lines.append("@WRITE" + str(label_counter))
    lines.append("0;JMP")
    lines.append("(NOT_THIS" + str(label_counter) + ")")
    lines.append("@THAT")
    lines.append("D=A")
    lines.append("(WRITE" + str(label_counter) + ")")
    lines.append("@pointer" + i)
    lines.append("M=D")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@pointer" + i)
    lines.append("A=M")
    lines.append("M=D")
    label_counter += 1
    return lines


def convert_push_static(i, file_name):
    """
    the function for converting a push static i command.
    :param file_name: (str) the vm file name (without the .vm).
    :param i: (str) the index location in the static segment of the item we
    want to add to the stack, as a string.
    :return: (list) a list of Assembly commands that produce the push
    static i command.
    """
    lines = list()
    lines.append("@" + file_name + "" + i)
    lines.append("D=M")
    lines.append("@SP")
    lines.append("M=M+1")
    lines.append("A=M-1")
    lines.append("M=D")
    return lines


def convert_pop_static(i, file_name):
    """
    the function for converting a pop static i command.
    :param file_name: (str) the vm file name (without the .vm).
    :param i: (str) the index location in the static segment where we will
    add the stack top to, as a string.
    :return: (list) a list of Assembly commands that produce the pop
     static i command.
    """
    lines = list()
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@" + file_name + "" + i)
    lines.append("M=D")
    return lines


def convert_add():
    """
    the function for converting an add command.
    :return: (list) a list of Assembly commands that produce the add command.
    """
    lines = list()
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("A=A-1")
    lines.append("M=D+M")
    return lines


def convert_sub():
    """
    the function for converting a sub command.
    :return: (list) a list of Assembly commands that produce the sub command.
    """
    lines = list()
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A+1")
    lines.append("D=D-M")
    lines.append("A=A-1")
    lines.append("M=D")
    return lines


def convert_neg():
    """
    the function for converting a neg command.
    :return: (list) a list of Assembly commands that produce the neg command.
    """
    lines = list()
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("M=-M")
    return lines


def convert_eq():
    """
    the function for converting a eq command.
    :return: (list) a list of Assembly commands that produce the eq command.
    """
    lines = list()
    global label_counter
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A-1")
    lines.append("D=D-M")
    lines.append("@NOT_EQUALS" + str(label_counter))
    lines.append("D;JNE")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("A=A-1")
    lines.append("M=-1")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("@END_EQ" + str(label_counter))
    lines.append("0;JMP")
    lines.append("(NOT_EQUALS" + str(label_counter) + ")")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("A=A-1")
    lines.append("M=0")
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("(END_EQ" + str(label_counter) + ")")
    label_counter += 1
    return lines


def convert_gt():
    """
    the function for converting a gt command.
    :return: (list) a list of Assembly commands that produce the gt command.
    """
    lines = list()
    global label_counter
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A+1")
    lines.append("@FIRST_POSITIVE" + str(label_counter))
    lines.append("D;JGT")
    lines.append("@SP")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@PUSH_FALSE" + str(label_counter))
    lines.append("D;JGE")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A+1")
    lines.append("D=D-M")
    lines.append("@PUSH_FALSE" + str(label_counter))
    lines.append("D;JEQ")
    lines.append("@PUSH_FALSE" + str(label_counter))
    lines.append("D;JLT")
    lines.append("@PUSH_TRUE" + str(label_counter))
    lines.append("0;JMP")
    lines.append("(FIRST_POSITIVE" + str(label_counter) + " )")
    lines.append("@SP")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@PUSH_TRUE" + str(label_counter))
    lines.append("D;JLE")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A+1")
    lines.append("D=D-M")
    lines.append("@PUSH_FALSE" + str(label_counter))
    lines.append("D;JEQ")
    lines.append("@PUSH_TRUE" + str(label_counter))
    lines.append("D;JGE")
    lines.append("(PUSH_FALSE" + str(label_counter) + ")")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("M=0")
    lines.append("@END_LT" + str(label_counter))
    lines.append("0;JMP")
    lines.append("(PUSH_TRUE" + str(label_counter) + ")")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("M=-1")
    lines.append("(END_LT" + str(label_counter) + ")")
    label_counter += 1
    return lines


def convert_lt():
    """
    the function for converting a lt command.
    :return: (list) a list of Assembly commands that produce the lt command.
    """
    lines = list()
    global label_counter
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A+1")
    lines.append("@FIRST_POSITIVE" + str(label_counter))
    lines.append("D;JGT")
    lines.append("@SP")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@PUSH_TRUE" + str(label_counter))
    lines.append("D;JGE")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A+1")
    lines.append("D=D-M")
    lines.append("@PUSH_TRUE" + str(label_counter))
    lines.append("D;JLT")
    lines.append("@PUSH_FALSE" + str(label_counter))
    lines.append("0;JMP")
    lines.append("(FIRST_POSITIVE" + str(label_counter) + " )")
    lines.append("@SP")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("@PUSH_FALSE" + str(label_counter))
    lines.append("D;JLE")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("D=M")
    lines.append("A=A+1")
    lines.append("D=D-M")
    lines.append("@PUSH_TRUE" + str(label_counter))
    lines.append("D;JLT")
    lines.append("(PUSH_FALSE" + str(label_counter) + ")")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("M=0")
    lines.append("@END_LT" + str(label_counter))
    lines.append("0;JMP")
    lines.append("(PUSH_TRUE" + str(label_counter) + ")")
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("M=-1")
    lines.append("(END_LT" + str(label_counter) + ")")
    label_counter += 1
    return lines


def convert_and():
    """
    the function for converting an and command.
    :return: (list) a list of Assembly commands that produce the and command.
    """
    lines = list()
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("A=A-1")
    lines.append("M=D&M")
    return lines


def convert_or():
    """
    the function for converting a or command.
    :return: (list) a list of Assembly commands that produce the or command.
    """
    lines = list()
    lines.append("@SP")
    lines.append("M=M-1")
    lines.append("A=M")
    lines.append("D=M")
    lines.append("A=A-1")
    lines.append("M=D|M")
    return lines


def convert_not():
    """
    the function for converting a not command.
    :return: (list) a list of Assembly commands that produce the not command.
    """
    lines = list()
    lines.append("@SP")
    lines.append("A=M-1")
    lines.append("M=!M")
    return lines


def make_boot():
    boot = list()
    boot.append("@256")
    boot.append("D=A")
    boot.append("@SP")
    boot.append("M=D")
    return boot


def main():
    list_of_files = list()
    # check if the path is a directory and fills list_of_files with all the
    # files names
    is_directory = False
    st = sys.argv[VM_FILE]
    if os.path.isdir(st):
        is_directory = True
        dir_name = os.path.basename(os.path.normpath(st))
        for filename in os.listdir(st):
            if filename.endswith(".vm"):
                list_of_files.append(
                    os.path.join(os.path.normpath(st), filename))
    # bootstrap = make_boot()
    # bootstrap.extend(convert_call("Sys.init", 0, 0))
    converted_lines = list()
    if is_directory:
        for file_name in list_of_files:
            base_name = Path(file_name).stem
            lines = read_file_in_args(file_name)
            new_lines = first_pass(lines)
            converted_lines += convert_lines(new_lines, base_name + ".")
        write_file = os.path.join(st, dir_name + ".asm")
        with open(write_file, "w") as file:
            # for line in bootstrap:
            #     file.write(line)
            #     file.write("\r\n")
            for line in converted_lines:
                file.write(line)
                file.write("\r\n")
    else:
        st_norm = Path(os.path.basename(os.path.normpath(st))).stem
        lines = read_file_in_args(st)
        new_lines = first_pass(lines)
        converted_lines = convert_lines(new_lines, st_norm + ".")
        write_file = os.path.join(os.path.dirname(st), Path(st).stem + ".asm")
        with open(write_file, "w") as file:
            # for line in bootstrap:
            #     file.write(line)
            #     file.write("\r\n")
            for line in converted_lines:
                file.write(line)
                file.write("\r\n")


if __name__ == '__main__':
    main()
