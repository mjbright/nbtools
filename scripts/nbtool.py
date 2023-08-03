#!/usr/bin/env python3

import json, sys, re, os

# TODO:
# - add option to put cell_no/type as a comment in cell (only for code cells)

# For converting output form code blocks form ANSI codes to HTML:
from ansi2html import Ansi2HTMLConverter
ansi2html_conv = Ansi2HTMLConverter()

from inspect import currentframe, getframeinfo
from inspect import stack

#frameinfo = getframeinfo(currentframe())
#print(frameinfo.filename, frameinfo.lineno)
#currentframe().f_back
#call_frameinfo = getframeinfo(currentframe().f_back)
#from inspect: stack()

def getenvBOOLEAN(NAME, DEFAULT):
    if DEFAULT:
        value = os.getenv(NAME, '1')
    else:
        value = os.getenv(NAME, '0')

    if value == '0': return False
    return True

DEBUG         = getenvBOOLEAN('DEBUG', False)
DEBUG_LINES   = getenvBOOLEAN('DEBUG_LINES', False)
DEBUG_CELLNOS = getenvBOOLEAN('DEBUG_CELLNOS', False)

# Max length for code-cell lines:
#MAX_LINE_LEN=110
#MAX_LINE_LEN=100
#MAX_LINE_LEN=80

DEFAULT_MAX_LINE_LEN=85
MAX_LINE_LEN=int(os.getenv('MAX_LINE_LEN', DEFAULT_MAX_LINE_LEN))

VARS_SEEN={}

REPLACE_COMMANDS={
    'TF_INIT':    'terraform init',
    'TF_PLAN':    'terraform plan',
    'TF_APPLY':   'terraform apply',
    'TF_DESTROY': 'terraform destroy',
    'K_GET':      'kubectl get',
    'K_CREATE':   'kubectl create',
}

def raw_ansi2text(ansi):
    return ansi.replace('\u001b[0m', ''). \
                replace('\u001b[1m', ''). \
                replace('\u001b[2m', ''). \
                replace('\u001b[30m', ''). \
                replace('\u001b[31m', ''). \
                replace('\u001b[32m', ''). \
                replace('\u001b[33m', ''). \
                replace('\u001b[34m', ''). \
                replace('\u001b[35m', ''). \
                replace('\u001b[36m', ''). \
                replace('\u001b[37m', '')

def writefile(path, mode='w', text='hello world\n'):
    ofd = open(path, mode)
    ofd.write(text)
    ofd.close()

def read_json(ipfile):
    #with open(ipfile, 'r') as f:

    if not os.path.exists(ipfile):
        die(f'No such input notebook {ipfile}')

    with open(ipfile, encoding='utf-8-sig') as json_file:
        #text = json_file.read()
        #json_data = json.loads(text)
        return json.load(json_file)

def pp_json(json_data):
    #print(json_data)
    print(json.dumps(json_data, indent = 4, sort_keys=True))

def pp_nb(json_data):
    print(f"Number of cells: {len(json_data['cells'])} kernel: {json_data['metadata']['kernelspec']['display_name']} nb_format: v{json_data['nbformat']}.{json_data['nbformat_minor']}")
    pp_json(json_data)

def nb_cells(json_data, type=None):
    return len(json_data['cells'])

def write_nb(opfile, json_data):
    with open(opfile, 'w') as json_file:
        json.dump(json_data, json_file)
          
def get_cell(json_data, cell_no):
    return json_data['cells'][cell_no]   
          
def nb_dump1sourceLine(ipfile):
    json_data = read_json(ipfile)
    print(f"{ipfile}: #cells={nb_cells(json_data)}")
    for cell_no in range(nb_cells(json_data)):
          #print(cell_no)
          source=json_data['cells'][cell_no]['source']
          if len(source) == 0:
              #print("empty")
              continue
          print(f"  cell[{cell_no}]source[0]={source[0]}")

def show_vars_seen(context, source_line, cell_no ):
    global VARS_SEEN

    if len(VARS_SEEN) == 0:
        print("---- no VARS_SEEN ----")
        return False

    DEBUG=False
    if context.find('nb') == 0: DEBUG=True
    '''
    if context == 'nb':
        print("---- VARS_SEEN: start ----")
    else:
        print(f"---- VARS_SEEN[{context} cell[{cell_no}]: start ---- {source_line}")
    '''
    show_exit_marker=False
    if DEBUG:
        if context.find('nb') == 0:
            nbfile=context[2:]
            print(f'----- VARS_SEEN [{nbfile}] ------')
            ctxt="nb"
            show_exit_marker=True
        else:
            ctxt=f"[{context} cell[{cell_no}] line '{source_line}'"

        for var in VARS_SEEN:
            value = VARS_SEEN[var]
            if value != "":
                value=f' (last value: "{value}")'
            print(f'{ctxt} __{var}\t{value}')

    if show_exit_marker: print(f'---------------------------------')
    return True

'''
    if context == 'nb':
        print("---- VARS_SEEN: end ----")
    else:
        print(f"---- VARS_SEEN[{context} cell[{cell_no}]: end ----")
'''

def nb_info(ip_or_op, ipfile):
    json_data = read_json(ipfile)

    any_vars_seen = show_vars_seen(f'nb{ipfile}','','')
    if not any_vars_seen:
        if ip_or_op == 'ip':
            print(f'i/p nb [{ipfile}] has 0 variables')
        else:
            print(f'o/p nb [{ipfile}] has 0 variables')
    
    return f"{ipfile}:\n\t#cells={nb_cells(json_data)}"
          
def die(msg):
    sys.stdout.write(f"die: {msg}\n")
    sys.exit(1)

def main():
    MODE='info'
    PROG=sys.argv[0]
    a=1
          
    if len(sys.argv) == 1:
          die("Missing arguments")
          
    if sys.argv[a] == '-f':
          a+=1
          MODE='filter'

    if sys.argv[a] == '-s':
          a+=1
          MODE='split'

    if sys.argv[a] == '-1':
          a+=1
          MODE='dump1l'

    if MODE=='dump1l':
        for ipfile in sys.argv[a:]:
            nb_dump1sourceLine(ipfile)

    if MODE=='info':
        for ipfile in sys.argv[a:]:
            print(nb_info('ip', ipfile))

    if MODE=='filter':
        for ipfile in sys.argv[a:]:
            print(nb_info('ip', ipfile))
            new_data = filter_nb( read_json(ipfile), DEBUG )
            opfile=ipfile+'.filtered.ipynb'
            write_nb(opfile, new_data)
            print(nb_info('op', opfile))

    if MODE=='split':
        for ipfile in sys.argv[a:]:
            print(nb_info('ip', ipfile))
            split_nb( read_json(ipfile), DEBUG )
            print("DONE")

def findInSource(source_lines, match):
    for line in source_lines:
          if match in line:
              print("True:" + line)
              return True
    return False

def next_section(current_sections, level, source_line):
    section_num=""
    #break_line=""
    #start_hl=''
    #end_hl=''
    if level == 0:
        current_sections[0]+=1
        current_sections[1]=1
        current_sections[2]=1
        current_sections[3]=1
        #break_line="\n<br />"
        #start_hl='<b>'
        #end_hl='</b>'
        section_num=f"{current_sections[0]}"
    if level == 1:
        current_sections[1]+=1
        current_sections[2]=1
        current_sections[3]=1
        section_num=f"{current_sections[0]}.{current_sections[1]}"
    if level == 2:
        current_sections[2]+=1
        current_sections[3]=1
        section_num=f"{current_sections[0]}.{current_sections[1]}.{current_sections[2]}"
    if level == 3:
        current_sections[3]+=1
        section_num=f"{current_sections[0]}.{current_sections[1]}.{current_sections[2]}.{current_sections[3]}"

    # Remove '#* '
    source_line=source_line[ source_line.find(' '):].lstrip()
    SE_regex = re.compile(r"([\d,\.]+) ") 
    source_line = SE_regex.sub("", source_line)
    return_line = section_num + ' ' + source_line.rstrip() # Remove new-line
    #return_line = break_line + start_hl + section_num + ' ' + source_line + end_hl
    return (level, section_num, return_line)
          
# TODO: convert output to be separate markdown cells
#print(f'DEBUG: cell_no:{cell_no}')
def CONVERT_ANSI_CODES2TXT(json_data, cell_no):
    #return
    op=json_data['cells'][cell_no]['outputs']
    #die(op)
    #print(f'cell_no[{cell_no}] op={op}')
    #ansi = json_data['cells'][cell_no]['outputs'][opno]['text'][textno]
    #print(f"cell{cell_no} has { len(json_data['cells'][cell_no]['outputs']) } elements")
    for opno in range(len(json_data['cells'][cell_no]['outputs'])):
        if 'text' in json_data['cells'][cell_no]['outputs'][opno]:
            #print(f"cell{cell_no} has 'text' element in element {opno}")
            for textno in range(len(json_data['cells'][cell_no]['outputs'][opno]['text'])):
                ansi = json_data['cells'][cell_no]['outputs'][opno]['text'][textno]
                #### if cell_no == 20 and textno == 91: print(f"BEFORE: cell{cell_no} has 'text' element {textno} '{ansi}' in element {opno}")
                text = raw_ansi2text(ansi)
                #### if cell_no == 20 and textno == 91: print(f"AFTER2: cell{cell_no} has 'text' element {textno} '{text}' in element {opno}")

                # print("Press <enter>")
                # sys.stdin.readline()
                json_data['cells'][cell_no]['outputs'][opno]['text'][textno] = text
                #### if text != ansi: print(f"cell{cell_no} has output element {opno} changed\n    text={text}')

def UNUSED_CONVERT_ANSI_CODES2HTML(json_data, cell_no):
    return
    op=json_data['cells'][cell_no]['outputs']
    #print(f'cell_no[{cell_no}] op={op}')
    #ansi = json_data['cells'][cell_no]['outputs'][opno]['text'][textno]
    for opno in range(len(json_data['cells'][cell_no]['outputs'])):
        if 'text' in json_data['cells'][cell_no]['outputs'][opno]:
            for textno in range(len(json_data['cells'][cell_no]['outputs'][opno]['text'])):
                ansi = json_data['cells'][cell_no]['outputs'][opno]['text'][textno]
                html = ansi2html_conv.convert(ansi)
                print(f'Converting {ansi} to {html}')
                # print("Press <enter>")
                # sys.stdin.readline()
                json_data['cells'][cell_no]['outputs'][opno]['text'][textno] = html

def substitute_vars_in_line(source_line, slno, VARS_SEEN):
    new_line=source_line
    vars_seen=[]
    for var in VARS_SEEN:
        if '$__'+var in source_line:
            vars_seen.append('__'+var)
            #if DEBUG:
                #print(json_data['cells'][cell_no]['source'][slno])
            #json_data['cells'][cell_no]['source'][slno]=json_data['cells'][cell_no]['source'][slno].replace('$__'+var, VARS_SEEN[var])
            new_line=new_line.replace('$__'+var, VARS_SEEN[var])
            #if DEBUG:
                #print("=>")
                #print(json_data['cells'][cell_no]['source'][slno])
                #print(json_data['cells'][cell_no]['source'][slno])

    if new_line != source_line:
        if DEBUG:
            print(f"[line{slno}]: {var} seen in '{source_line}' will replace vars [{vars_seen}]")
            #print(f"{var} seen in '{source_line}' will replace '$__{var}'")
            #print(f"'{source_line}'\n===> '{new_line}'")
            print(f"===> '{new_line}'")
    return new_line

def replace_vars_in_line(line, vars_seen):
    return substitute_vars_in_line(line, -1, vars_seen)

def replace_vars_in_cell_output_lines(json_data, cell_no, vars_seen):
    op=json_data['cells'][cell_no]['outputs']

    for opno in range(len(json_data['cells'][cell_no]['outputs'])):
        if 'text' in json_data['cells'][cell_no]['outputs'][opno]:
            for textno in range(len(json_data['cells'][cell_no]['outputs'][opno]['text'])):
                line = json_data['cells'][cell_no]['outputs'][opno]['text'][textno]
                line = replace_vars_in_line(line, vars_seen)
                json_data['cells'][cell_no]['outputs'][opno]['text'][textno] = line


def get_var_defs_in_cell_output_lines(output_lines):
    vars_seen={}

    for opno in range(len(output_lines)):
        if 'text' in output_lines[opno]:
            for textno in range(len(output_lines[opno]['text'])):
                line = output_lines[opno]['text'][textno]
                if 'VAR __' in line:
                    VAR_NAME=line[ line.find('VAR __') + 6: line.find('=') ]
                    #DEBUG=True
                    VAR_SET='VAR __'+VAR_NAME+'='
                    if output_lines[opno]['text'][textno].find(VAR_SET)==0:
                        VAR_VALUE=output_lines[opno]['text'][textno][len(VAR_SET):].rstrip()
                        #if DEBUG: print(f"VAR {VAR_NAME}={VAR_VALUE}")
                        if DEBUG: print(f"<<<<<<<<DEBUG>>>>>>>> VAR {VAR_NAME}={VAR_VALUE}")
                        vars_seen[VAR_NAME]=VAR_VALUE
                        #print(f"VAR {VAR_NAME}={VAR_VALUE}")
                        #print(VAR_VALUE)

                        #output_lines'][opno]['texts'][textno].replace('$'+VAR_NAME, VAR_VALUE)
              #if "SET_VAR" in source_line:
    return vars_seen

def show_long_line( label, source_line, MAX_LINE_LEN, cell_no, cell_type, section_title, EXCLUDED_CODE_CELL ):
    RED='\x1B[00;31m'
    NORMAL='\x1B[00m'

    caller_info=stack()[1]
    calling_line=caller_info[2]
    calling_function=caller_info[3]
    print()
    print(f'{label} func {calling_function} line {calling_line} {RED}[{cell_type} cell {cell_no}] LONG LINE length={len(source_line)} > {MAX_LINE_LEN}{NORMAL} in section "{section_title}"')
    print(f'  line="{source_line.rstrip()}"')
    if EXCLUDED_CODE_CELL:
        print(f'  excluded_code_cell={EXCLUDED_CODE_CELL}')
    if len(source_line) != 1+len(source_line.rstrip()):
        print(f'  len(line)={len(source_line)} != {len(source_line.rstrip())}')

def filter_nb(json_data, DEBUG=False):
    global VARS_SEEN

    EXCL_FN_regex = re.compile(r"\|?\&?\s*EXCL_FN_.*$") #, re.IGNORECASE)
    include=False
    cells=[]

    toc_cell_no=-1
    count_sections=False
    current_sections=[]
    toc_text='<div id="TOC" >\n'
    sec_cell_no=0
    In_cell_no='unknown'
    section_title=''

    exclude_cells=[]
    incl_code_cells=[]
    incl_md_cells=[]

    for cell_no in range(nb_cells(json_data)):
          sec_cell_no+=1
          #print(cell_no)
          cell_type=json_data['cells'][cell_no]['cell_type']
          In_cell_no='unknown'
          if cell_type == 'code':
              In_cell_no=json_data['cells'][cell_no]['execution_count']

          source_lines=json_data['cells'][cell_no]['source']
          if len(source_lines) == 0:
              if DEBUG: print("empty")
              continue

          if DEBUG_CELLNOS:
              source_lines.append( f'\n\n#### Cell[{cell_no}]\n')

          # Pragma --INCLUDE--SECTION--
          if '--INCLUDE--SECTION--' in source_lines[0]: 
              include=True
              # BUT THIS CELL IS EXCLUDED:

              # TODO: PLACE THICK LINE HERE:
              exclude_cells.append(cell_no)
              continue
          # Pragma --EXCLUDE--SECTION--
          if '--EXCLUDE--SECTION--' in source_lines[0]:
              include=False
              exclude_cells.append(cell_no)

              # TODO: PLACE THICK LINE HERE:
              continue

          if not include:
              exclude_cells.append(cell_no)
              continue

          # Detect TableOfContents Cell No:
          if len(source_lines) > 0 and source_lines[0].find('<div id="TOC"') == 0:
              toc_cell_no=cell_no
              print(f"ToC cell detected at cell_no[{cell_no}]")
              count_sections=True
              current_sections.append(0)
              current_sections.append(1)
              current_sections.append(1)
              current_sections.append(1)
              cells.append(cell_no)
              continue

          EXCLUDED_CODE_CELL=False
          if source_lines[0].find('#EXCLUDE') == 0 and cell_type == 'code':
              EXCLUDED_CODE_CELL=True
              exclude_cells.append(cell_no)
              # NOTE: Code will be excluded but continue to parse/search for variables settings

          if cell_type == 'markdown' and not EXCLUDED_CODE_CELL:
              incl_md_cells.append(cell_no)

          if cell_type == 'code' and not EXCLUDED_CODE_CELL:
              incl_code_cells.append(cell_no)

          include_cell=True
          for slno in range(len(source_lines)):
              source_line=source_lines[slno]
              if DEBUG_LINES:
                  s_line=source_line.rstrip()
                  print(f'[{cell_type}][{cell_no} l{slno}] "{s_line}"')

              if cell_type == 'code' and not EXCLUDED_CODE_CELL:
                  inc_source_line = source_line
                  if '| EXCL_FN' in source_line:
                      inc_source_line = source_line[ : source_line.find('| EXCL_FN') ]
                  if len(inc_source_line) > MAX_LINE_LEN:
                      show_long_line( 'inc_code', inc_source_line, MAX_LINE_LEN, cell_no, cell_type, section_title, EXCLUDED_CODE_CELL )

              insert_line_image=''
              if source_line.find("# STRETCH-GOALS") == 0 and cell_type == "markdown":
                  # PLACE THICK LINE HERE: Start of Stretch Goals
                  # insert_line_image='<img align="left" src="../images/Thick120BlueBar.png" height="200" /><br/>'
                  insert_line_image='<img align="left" src="../images/Thick240BlueBar.png" height="200" /><br/>'
                  insert_line_image+='<img align="left" src="../images/Thick240BlueBar.png" height="200" /><br/>'
                  source_line="# Stretch Goals"
              elif source_line.find("# ") == 0 and cell_type == "markdown":
                  # PLACE MEDIUM LINE HERE:
                  insert_line_image='<img align="left" src="../images/ThinBlueBar.png" /><br/>'
                  #ThickBlueBar.png
                  #ThinBlueBar.png
              elif source_line.find("## ") == 0 and cell_type == "markdown":
                  # PLACE THIN LINE HERE:
                  insert_line_image='<img align="left" src="../images/ThinBlueBar.png" width="400" /><br/>'

              # Build up TableOfContents - Count sections headers and retain list for ToC text
              if source_line.find("#") == 0 and count_sections and cell_type == "markdown":
                  toc_line=''
                  level=0
                  if source_line.find("# ") == 0:    (level, section_num, toc_line) = next_section(current_sections, 0, source_line)
                  if source_line.find("## ") == 0:   (level, section_num, toc_line) = next_section(current_sections, 1, source_line)
                  if source_line.find("### ") == 0:  (level, section_num, toc_line) = next_section(current_sections, 2, source_line)
                  if source_line.find("#### ") == 0: (level, section_num, toc_line) = next_section(current_sections, 3, source_line)
                  sec_cell_no=0
                  section_title=toc_line

                  toc_link = f'<a href="#sec{section_num}" /> {toc_line} </a>'
                  if level == 0:
                      toc_text += f'\n<br /> <div id="TOC{section_num}" > <b> {toc_link} </b></div>\n'
                  else:
                      toc_text += f'* {toc_link}\n'

                  if "." in section_num:
                      top_section_num = section_num[ : section_num.find(".") ]
                  else:
                      top_section_num = section_num 

                  json_data['cells'][cell_no]['source'][slno] =\
                          f'<a href="#TOC{top_section_num}" > Return to INDEX </a>\n' + \
                          source_line[ :1+source_line.find(' ') ] + f'<div id="sec{section_num}" > '+toc_line+' </div>'

              if insert_line_image != '':
                  json_data['cells'][cell_no]['source'][slno] = f'\n\n{insert_line_image}\n\n' + json_data['cells'][cell_no]['source'][slno]
                  insert_line_image=''

              if cell_type == "markdown" and \
                 (source_line.find("**Red**") != -1 or \
                  source_line.find("**Green**") != -1 or \
                  source_line.find("**Blue**") != -1 or \
                  source_line.find("**Yellow**") != -1):
                     #print(source_line)
                     source_line=source_line.replace("**Red**", "<div class='alert alert-danger'> ")
                     source_line=source_line.replace("**Green**", "<div class='alert alert-success'> ")
                     source_line=source_line.replace("**Blue**", "<div class='alert alert-info'> ")
                     source_line=source_line.replace("**Yellow**", "<div class='alert alert-warning'> ")
                     source_line=source_line + "</div>"
                     # source_line=source_line.replace("**RedNote", "<div class='red_bold_text'>Note")
                     # source_line=source_line.replace("**BlueNote", "<div class='blue_bold_text'>Note")
                     # source_line=source_line.replace("**GreenNote", "<div class='green_bold_text'>Note")
                     # source_line=source_line.replace("**", "</div>")
                     #print(source_line)
                     json_data['cells'][cell_no]['source'][slno] = source_line
                     #die(" ===================  OK  ===================")

              if cell_type == "markdown" and '__' in source_line:
                  o = source_line
                  source_line = replace_vars_in_line(source_line, VARS_SEEN)
                  show_vars_seen(cell_type, source_line, cell_no)

                  json_data['cells'][cell_no]['source'][slno] = source_line
                  #print(f"MARKDOWN[cell{cell_no}] {source_line.rstrip()}")
                  #if o != source_line: print(o); die("GOT HERE")

              # Pragma FOREACH (use singular form of variable e.g. __POD_IP which will be populated form __POD_IPS)
              if source_line.find("FOREACH __") == 0:
                  rest_line=source_line[ len("FOREACH __"): ].lstrip()
                  space_pos=rest_line.find(" ")
                  if space_pos > 1:
                      VAR_NAME=rest_line[:space_pos]
                      VAR_NAME_S=VAR_NAME+'S'

                      cmd_line=rest_line[space_pos:].lstrip()
                      new_line=''

                      #print(f"Vars seen so far={VARS_SEEN.keys()}")
                      if not VAR_NAME_S in VARS_SEEN:
                          print(f"Vars seen so far={VARS_SEEN.keys()}")
                          die(f"Var <{VAR_NAME_S}> not seen")
                      values=VARS_SEEN[VAR_NAME_S].split()
                      for value in values:
                          new_line+=cmd_line\
                              .replace('\$__', '$__')\
                                  .replace('\<', '<')\
                                  .replace('\>', '>')\
                                  .replace('$__'+VAR_NAME, value)+'\n'
                      #new_line=substitute_vars_in_line(cmd, slno, VARS_SEEN)

                      json_data['cells'][cell_no]['source'][slno]=new_line
                      if new_line != source_line: print(new_line)
                  continue

              if 'outputs' in json_data['cells'][cell_no]:
                  CONVERT_ANSI_CODES2TXT(json_data, cell_no)
                  #replace_vars_in_cell_output_lines(json_data, cell_no, VARS_SEEN)
                  #UNUSED_CONVERT_ANSI_CODES2HTML(json_data, cell_no)
                      
              # Pragma $__ variables ...
              # If $__variables seen in source then we modify the source to replace $_var by it's value
              for var in VARS_SEEN:
                  if '$__'+var in source_line:
                      new_line=substitute_vars_in_line(source_line, slno, VARS_SEEN)
                      show_vars_seen(f'{cell_type}[$__{var}]', source_line, cell_no)
                      #if DEBUG:
                      #    print(f"{var} seen in {source_line} will replace '$__{var}'")
                      #    print(json_data['cells'][cell_no]['source'][slno])
                      #json_data['cells'][cell_no]['source'][slno]=json_data['cells'][cell_no]['source'][slno].replace('$__'+var, VARS_SEEN[var])
                      #if DEBUG:
                      #    print("=>")
                      #    print(json_data['cells'][cell_no]['source'][slno])
                      json_data['cells'][cell_no]['source'][slno]=new_line

                      # TODO: generalize line length checking after all replacements (how to hook i on 'continue' ??
                      show_long_line('vars_replaced', new_line, MAX_LINE_LEN, cell_no, cell_type, section_title, EXCLUDED_CODE_CELL )

                      #if not findInSource(source_lines, "SET_VAR_"):

              # Pragma | NO_EXEC(command)
              if "NO_EXEC" in source_line:
                  pos=json_data['cells'][cell_no]['source'][slno].find("NO_EXEC")+len("NO_EXEC")
                  json_data['cells'][cell_no]['source'][slno] = json_data['cells'][cell_no]['source'][slno][pos:]

              for REPLACE_CMD in REPLACE_COMMANDS:
                  if REPLACE_CMD in source_line:
                      pos=json_data['cells'][cell_no]['source'][slno].find(REPLACE_CMD)+len(REPLACE_CMD)
                      json_data['cells'][cell_no]['source'][slno] = \
                          REPLACE_COMMANDS[REPLACE_CMD] + ' ' + json_data['cells'][cell_no]['source'][slno][pos:]

              # Pragma | EXEC(command)
              if source_line.find("EXEC ") == 0:
                  json_data['cells'][cell_no]['source'][slno]=''

              # Pragma #EXCLUDE (cell):
              if source_line.find("#EXCLUDE") == 0:
                  include_cell=False
                  continue

              # Pragma | EXCL_FN_(HIDE_|HIGHLIGHT*)
              if "EXCL_FN_" in source_line:
                  if DEBUG:
                      orig=json_data['cells'][cell_no]['source'][slno]
                  json_data['cells'][cell_no]['source'][slno] = \
                      EXCL_FN_regex.sub("", json_data['cells'][cell_no]['source'][slno])
                  if DEBUG:
                      new=json_data['cells'][cell_no]['source'][slno]
                      if new != orig:
                          print(f"{orig.rstrip()} => {new.rstrip()}")
           
              # Pragma WAIT:
              if source_line.find("WAIT")     == 0:
                  include_cell=False
                  continue

              # Pragma RETURN:
              if source_line.find("RETURN")     == 0:
                  json_data['cells'][cell_no]['source'][slno]=''
                  continue

              # NOT Pragma SET_VAR:
              # NOT Pragma SET_VAR and NOT K_GET_* 
              #if source_line.find("SET_VAR_") == -1: continue
              #if source_line.find("K_GET_") == -1: continue
              #if source_line.find("SET_VAR") != -1: print(f'======== {source_line} ========')
              #if source_line.find("SET_VAR_") == -1 and source_line.find("K_GET_") == -1: continue
              if source_line.find("SET_VAR") == -1 and source_line.find("K_GET_") == -1: continue

              #print(f"EXCLUDING var setting cell - SEEN {source_line}")
              # Pragma SET_VAR:
              include_cell=False
              #if source_line.find("SET_VAR") != -1: print(f'======== {source_line} ========')

              # If SET_VAR seen in source, we exclude **this cell** and set the variable
              #if source_line.find("SET_VAR_") == 0:
                  #VAR_NAME=source_line[len("SET_VAR_"):].rstrip()

              #if " " in VAR_NAME: VAR_NAME=VAR_NAME[:VAR_NAME.find(" ")]
              #VAR_VALUE="var_value"
              #VARS_SEEN[VAR_NAME]=VAR_VALUE
              #if DEBUG: print(f"SET_VAR {VAR_NAME}={VAR_VALUE}")
              #print(f"VAR_NAME={VAR_NAME}")
              #outputs = json_data['cells'][cell_no]['outputs']

              if json_data['cells'][cell_no]['outputs']:
                  op_vars_seen = get_var_defs_in_cell_output_lines( json_data['cells'][cell_no]['outputs'] )
                  if len(op_vars_seen) > 0:
                      #print(f'NEW VARS_SEEN: "{op_vars_seen}"')
                      VARS_SEEN.update( op_vars_seen )
                      show_vars_seen('output', source_line, cell_no)
                  #replace_vars_in_cell_output_lines( json_data['cells'][cell_no]['outputs'], VARS_SEEN )
                  replace_vars_in_cell_output_lines(json_data, cell_no, VARS_SEEN)

          if include_cell:
              cells.append(cell_no)
          
    #            #if source_lines[0].find("SET_VAR_") == -1:
    #             if not findInSource(source_lines, "SET_VAR_"):
    #                 cells.append(cell_no)
    #                 continue

           
    # Patch TableOfContents:
    toc_text+='</div>'
    if DEBUG:
        print(f"ToC set to <{toc_text}>")
    json_data['cells'][toc_cell_no]['source'] = [ toc_text ]

    print()
    print(f"cells to include[#{len(cells)}]=[{cells}]")
    cells.reverse()
    
    for cell_no in range(nb_cells(json_data)-1, -1, -1):
        #print(cell_no)
        if not cell_no in cells:
            #print(f"del(cells[{cell_no}])")
            del(json_data['cells'][cell_no])

    print(f"cells to include[#{len(cells)}]=[{cells}]")
    print(f"included markdown cells={incl_md_cells}")
    print(f"included code     cells={incl_code_cells}")
    print(f"excluded          cells={exclude_cells}")
    print()
    return json_data

def write_markdown(markdown_file, cell_num, cell_type, section_title, current_section_text):
    print(f'writefile({markdown_file})')
    current_section_text = f'<!-- cell_num: {cell_num} -->\n' + \
                        f'<!-- cell_type: {cell_type} -->\n' + \
                        f'<!-- section_title:<<<{section_title}>>>-->\n' + \
                        current_section_text
    writefile(f'{markdown_file}', 'w', current_section_text)

def split_nb(json_data, DEBUG=False):
    cells=[]
    global VARS_SEEN
    print("-- split_nb: resetting VARS_SEEN !!")
    VARS_SEEN={}

    md_files_index=''

    toc_cell_no=-1
    count_sections=False
    current_sections=[]
    toc_text='<div id="TOC" >\n'

    SPLIT_ON_SECTIONS=-1 # Split on any level
    SPLIT_ON_SECTIONS=1 # Split only on 1st-level i.e. 1, 2, ..
    SPLIT_ON_SECTIONS=2 # Split only 1st, 2nd-level i.e. 1, 1.1, 1.2, 2, 2.1, ...

    current_section_text='' 
    section_no='1'
    section_title='UNKNOWN'
    os.mkdir('md')
    markdown_file=f'section_{section_no}.md'
    markdown_file_path=f'md/{markdown_file}'
    # md_files_index+=markdown_file+'\n'

    sec_cell_no=0

    div_sec='<div id="sec'
    len_div_sec=len( div_sec )
    for cell_no in range(nb_cells(json_data)):
          sec_cell_no+=1
          #print(cell_no)
          cell_type=json_data['cells'][cell_no]['cell_type']
          source_lines=json_data['cells'][cell_no]['source']
          if len(source_lines) == 0:
              if DEBUG: print("empty")
              continue

          # current_cell_text='' 
          if cell_type == 'code': current_section_text+='\n```'
          # current_cell_text='' 

          EXCLUDED_CODE_CELL=False
          if source_lines[0].find('#EXCLUDE') == 0 and cell_type == 'code':
              EXCLUDED_CODE_CELL=True
              # NOTE: Code will be excluded but continue to parse/search for variables settings

          for slno in range(len(source_lines)):
              source_line=source_lines[slno]
              if cell_type == 'code' and not EXCLUDED_CODE_CELL:
                  inc_source_line = source_line
                  if '| EXCL_FN' in source_line:
                      inc_source_line = source_line[ : source_line.find('| EXCL_FN') ]
                  #if len(inc_source_line) > MAX_LINE_LEN:
                      #print(f'[split_nb]: long {inc_source_line} > {MAX_LINE_LEN} {EXCLUDED_CODE_CELL}' )

                  show_long_line( 'slno', inc_source_line, MAX_LINE_LEN, cell_no, cell_type, section_title, EXCLUDED_CODE_CELL )
                  #if len(source_line) > MAX_LINE_LEN:
                      #print(f"[split_nb]: len={len(inc_source_line)} > {MAX_LINE_LEN} in cell {sec_cell_no} of section {section_title} in line '{source_line}'")


              if div_sec in source_line:
                  start_pos = source_line.find( div_sec )
                  end_pos = start_pos + len_div_sec + source_line[ start_pos + len_div_sec : ].find('"')
                  next_section_no=source_line[ start_pos + len_div_sec : end_pos ]

                  ## <div id="sec1.2" > 1.2 This Lab Cluster </div>
                  close_div_pos = end_pos + source_line[ end_pos : ].find('</div')
                  next_section_title=source_line[ end_pos : close_div_pos ]

                  print(f"LINE[0]: <<<{source_line}>>>")
                  print(f"pos[{start_pos}:{end_pos}]")

                  if div_sec in source_line[ start_pos + len_div_sec : ]: die("OOPS")
    
                  if next_section_no.count('.') < SPLIT_ON_SECTIONS:
                      if current_section_text != '':
                          write_markdown(markdown_file_path, cell_no+1, cell_type, section_title, current_section_text)
                          current_section_text='' 
                      section_no=next_section_no
                      section_title=next_section_title
                      sec_cell_no=0
                      #section_title=section_title.replace(" ", "")
                      markdown_file=f'section_{section_no}.md'
                      markdown_file_path=f'md/{markdown_file}'
                      print(f"New section {section_no} seen")
                      md_files_index+=markdown_file+'\n'

              #current_section_text+='\n'+source_line
              current_section_text+=source_line

          if cell_type == 'code': current_section_text+='\n```\n'

    if current_section_text != '':
        #print(f'writefile({markdown_file})')
        #writefile(f'{markdown_file}', 'w', current_section_text)
        write_markdown(markdown_file_path, cell_no+1, cell_type, section_title, current_section_text)

    writefile('md/index.txt', 'w', md_files_index)


if __name__ == "__main__":
    main()

