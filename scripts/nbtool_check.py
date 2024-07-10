#!/usr/bin/env python3

import json, sys, re, os

''' MAIN PATH FLOW: (filter mode):
   new_data = filter_nb( read_json(ipfile), DEBUG )
   opfile=ipfile+'.filtered.ipynb'
   write_nb(opfile, new_data)
'''

from inspect import currentframe, getframeinfo
from inspect import stack

BLACK='\x1B[00;30m'
RED='\x1B[00;31m';      B_RED='\x1B[01;31m';      BG_RED='\x1B[07;31m'
GREEN='\x1B[00;32m';    B_GREEN='\x1B[01;32m';    BG_GREEN='\x1B[07;32m'
YELLOW='\x1B[00;33m';   B_YELLOW='\x1B[01;33m';   BG_YELLOW='\x1B[07;33m'
NORMAL='\x1B[00m'

#frameinfo = getframeinfo(currentframe())
#print(frameinfo.filename, frameinfo.lineno)
#currentframe().f_back
#call_frameinfo = getframeinfo(currentframe().f_back)
#from inspect: stack()

def die(msg):
    sys.stdout.write(f"die: {RED}{msg}{NORMAL}\n")
    function = stack()[1].function
    lineno   = stack()[1].lineno
    #fname = stack()[1].filename
    #DEBUG_FD.write(f'[fn {function} line {lineno} {msg}'.rstrip()+'\n')
    print(f'... called from [fn {function} line {lineno} {msg}')
    #DEBUG_FD.close()
    sys.exit(1)

DEFAULT_MAX_LINE_LEN=100
MAX_LINE_LEN=int(os.getenv('MAX_LINE_LEN', DEFAULT_MAX_LINE_LEN))

def writefile(path, mode='w', text='hello world\n'):
    ofd = open(path, mode)
    ofd.write(text)
    ofd.close()

def read_json(ipfile):
    if not os.path.exists(ipfile):
        die(f'No such input notebook {ipfile}')

    with open(ipfile, encoding='utf-8-sig') as json_file:
        return json.load(json_file)

def pp_json(json_data):
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
          
def main():
    MODE='info'
    PROG=sys.argv[0]
    a=1

    #print(sys.argv)
    for ipfile in sys.argv[a:]:
        if not '.ipynb_checkpoints' in ipfile:
            summarize_nb(ipfile)
    sys.exit(0)
          
def PRESS(label):
    print(f'DEBUG[{label} - press enter to continue')
    input()

def summarize_nb(ipfile, DEBUG=False):
    json_data = read_json(ipfile)

    #__regex = re.compile(r"\|?\&?\s*__.*$") #, re.IGNORECASE)
    cells=[]
    cells_data = json_data['cells']
    #print(f'i/p file={ ipfile } has { len(cells_data) } cells')
    seen = {}
    for cell in cells_data:
          cell_type=cell['cell_type']
          if cell_type in seen:
              seen[ cell_type ] += 1
          else:
              seen[ cell_type ] = 1

    cell_info=f'{ len(cells_data) } cells:'
    for cell_type in seen:
        cell_info += f' { seen[cell_type] } { cell_type },'
    cell_info = cell_info[:-1]
    print(f'[{ cell_info }] { ipfile }')
    return

    #cell_type=cells_data[cell_no]['cell_type']
    
    sys.exit(0)

    toc_cell_no=-1
    count_sections=False
    current_sections=[]
    toc_text='<div id="TOC" >\n'
    In_cell_no='unknown'
    section_title=''

    exclude_cells=[]
    incl_code_cells=[]
    incl_md_cells=[]

    # BEGINNING of filter_nb:
    for cell_no in range(nb_cells(json_data)):
          sec_cell_no+=1
          #print(cell_no)
          cell_type=cells_data[cell_no]['cell_type']
          In_cell_no='unknown'
          source_lines = cells_data[cell_no]['source']
          if cell_type == 'code':
              In_cell_no=cells_data[cell_no]['execution_count']

              if 'NB_SET_VAR' in ' '.join(source_lines):
                  DEBUG(f"[cell={cell_no} section={section_title}] NB_SET_VAR variables seen in cell source_lines")

              source_lines.append(f'\n# Code-Cell[{cell_no}] In[{In_cell_no}]\n')

              # CHECK for empty code cells:
              if len(source_lines) == 0:
                  DEBUG(f"[cell={cell_no} section={section_title}] CONTINUE - no source lines")
                  continue

          if len(source_lines) == 0: source_lines = ['']

          # Pragma --INCLUDE--SECTION--
          if '--INCLUDE--SECTION--' in source_lines[0]: 
              include=True
              # BUT THIS CELL IS EXCLUDED:

              exclude_cells.append(cell_no)
              DEBUG(f"[cell={cell_no} section={section_title}] CONTINUE - START INCLUDE--SECTION")
              continue
          # Pragma --EXCLUDE--SECTION--
          if '--EXCLUDE--SECTION--' in source_lines[0]:
              include=False
              exclude_cells.append(cell_no)

              DEBUG(f"[cell={cell_no} section={section_title}] CONTINUE - START EXCLUDE--SECTION")
              continue

          if not include:
              exclude_cells.append(cell_no)
              DEBUG(f"[cell={cell_no} section={section_title}] CONTINUE - not include")
              continue

          # Detect TableOfContents Cell No:
          if len(source_lines) > 0 and source_lines[0].find('<div id="TOC"') == 0:
              toc_cell_no=cell_no
              DEBUG(f"ToC cell detected at cell_no[{cell_no}]")
              count_sections=True
              current_sections.append(0)
              current_sections.append(1)
              current_sections.append(1)
              current_sections.append(1)
              cells.append(cell_no)
              DEBUG(f"[cell={cell_no} section={section_title}] CONTINUE - TOC CELL found")
              continue

          EXCLUDED_CODE_CELL=False
          if cell_type == 'code':
              if source_lines[0].find('#EXCLUDE') == 0:
                  EXCLUDED_CODE_CELL=True
                  exclude_cells.append(cell_no)
                  # NOTE: Code will be excluded but continue to parse/search for variables settings
                  DEBUG(f"[cell={cell_no} section={section_title}] EXCLUDED_CODE_CELL - #EXCLUDE found")

              # Pragma | QUIET: just quietly/rebuild notebook/markdown - exclude this cell
              if source_lines[0].find('__QUIET') == 0:
                  EXCLUDED_CODE_CELL=True
                  exclude_cells.append(cell_no)
                  DEBUG(f"[cell={cell_no} section={section_title}] EXCLUDED_CODE_CELL - __QUIET found")

          # EXCLUDED_CODE_CELL for markdown ??
          if cell_type == 'markdown' and not EXCLUDED_CODE_CELL:
              for slno in range(len(source_lines)):
                  TAG='Note:'; O_TAG='Note: '
                  if source_lines[slno].find(TAG) == 0:
                       source_lines[slno]=info_box(source_lines[slno][len(TAG):], '#0000AA', '#ffffff', O_TAG, full_page_width=False)
                  TAG='**Note:**'; O_TAG='Note: '
                  if source_lines[slno].find(TAG) == 0:
                       source_lines[slno]=info_box(source_lines[slno][len(TAG):], '#0000AA', '#ffffff', O_TAG, full_page_width=False)
                  TAG='**Stretch:**'; O_TAG='Stretch Goal: '
                  if source_lines[slno].find(TAG) == 0:
                       source_lines[slno]=info_box(source_lines[slno][len(TAG):], '#0000AA', '#00aaaa', O_TAG, full_page_width=False)
                  TAG='# __INFO:'; O_TAG='Info: '
                  if source_lines[slno].find(TAG) == 0:
                       source_lines[slno]=info_box(source_lines[slno][len(TAG):], '#00AA00', '#eeffee', O_TAG)
                  TAG='# __WARN:'; O_TAG='Warning: '
                  if source_lines[slno].find(TAG) == 0:
                       source_lines[slno]=info_box(source_lines[slno][len(TAG):], '#AA0000', '#ffeeee', O_TAG)
                  TAG='# __ERROR:'; O_TAG='Error: '
                  if source_lines[slno].find(TAG) == 0:
                       source_lines[slno]=info_box(source_lines[slno][len(TAG):], '#FF0000', '#ffeeee', O_TAG)
                  if source_lines[slno].find('# __DETAIL(') == 0:
                       summary=source_lines[slno][ 9+source_lines[slno].find('__DETAIL(') : source_lines[slno].find('):') ]
                       details=source_lines[slno][ source_lines[slno].find('):') + 2 : ]
                       source_lines[slno]=details_box(summary, details, '#0000FF', '#ffffff', 'Info: ')

                  if source_lines[slno].find('SSH_SET ') == 0:
                       SSH_NODE=source_lines[slno][8:]
                       source_lines[slno] = ''
                  elif source_lines[slno].find('SSH ') == 0:
                       source_lines[slno] = source_lines[slno][4:]

                  if source_lines[slno].find('# __Q(') == 0:
                       summary=source_lines[slno][ 9+source_lines[slno].find('__Q(') : source_lines[slno].find('):') ]
                       details=source_lines[slno][ source_lines[slno].find('):') + 2 : ]
                       source_lines[slno]=question_box(summary, details, '#0000FF', 'Question: ')
                       QUESTIONS.append([summary, details])
                       NUM_QUESTIONS+=1

                  if ( source_lines[slno].find('**Red**') != -1 or \
                     source_lines[slno].find('**Green**') != -1 or \
                     source_lines[slno].find('**Blue**') != -1 or \
                     source_lines[slno].find('**Yellow**') != -1):
                     source_lines[slno]=source_lines[slno].replace("**Red**", "<div class='alert alert-danger'> ")
                     source_lines[slno]=source_lines[slno].replace("**Green**", "<div class='alert alert-success'> ")
                     source_lines[slno]=source_lines[slno].replace("**Blue**", "<div class='alert alert-info'> ")
                     source_lines[slno]=source_lines[slno].replace("**Yellow**", "<div class='alert alert-warning'> ")
                     source_lines[slno]=source_lines[slno] + "</div>"
                     cells_data[cell_no]['source'][slno] = source_lines[slno]
              incl_md_cells.append(cell_no)


          if cell_type == 'code' and not EXCLUDED_CODE_CELL:
              incl_code_cells.append(cell_no)

              # Pragma | NB_FILE | NB_FILE_M | NB_FILE_A
              DEBUG(f'len(source_lines)={len(source_lines)} source_lines="{source_lines}"')
              source_line0 = source_lines[0]
              if source_line0.find("NB_FILE") == 0:
                  replace_EOF_backticks( section_title, cell_no, cells_data[cell_no]['source'] )
                  replace_code_cell_by_markdown( cells_data[cell_no], 
                      "Create a new file __FILE__ with the following content:")

              if source_line0.find("NB_FILE_M") == 0:
                  replace_EOF_backticks( section_title, cell_no, cells_data[cell_no]['source'] )
                  replace_code_cell_by_markdown( cells_data[cell_no], 
                      "Modify the file __FILE__ replacing with the following content:")

              if source_line0.find("NB_FILE_A") == 0:
                  replace_EOF_backticks( section_title, cell_no, cells_data[cell_no]['source'] )
                  replace_code_cell_by_markdown( cells_data[cell_no], 
                      "Append the following content to file __FILE__:")

          include_cell=True

          # Pragma | __DOCKER(command)
          for slno in range( len( source_lines ) ):
              if source_lines[slno].find("__DOCKER") != -1:
                  source_lines[slno] = source_lines[slno].replace("__DOCKER", "ssh vm-linux-docker docker")

          # Pragma | __CURL(command)
          for slno in range( len( source_lines ) ):
              if source_lines[slno].find("__CURL") != -1:
                  source_lines[slno] = source_lines[slno].replace("__CURL", "ssh vm-linux-docker curl")

          source_line_0=source_lines[0]

          # TODO: REMOVE/REPLACE/CHANGE-NAME?? Pragma | CODE(command)
          if source_line_0.find("__CODE") == 0 and len(cells_data[cell_no]['outputs']) != 0:
              nl='\n'
              print('---- BEFORE ------------------')
              print(f"{YELLOW}No source_lines={len(cells_data[cell_no]['source'])}")
              print(f"   source_lines={''.join( cells_data[cell_no]['source'])}")
              print(f"No outputs={len(cells_data[cell_no]['outputs'][0]['text'])}")
              print(f"   outputs     ={ cells_data[cell_no]['outputs'][0]['text']}")

              cells_data[cell_no]['source']  = [ cells_data[cell_no]['outputs'][0]['text'][0] ]
              source_lines = cells_data[cell_no]['source']
              cells_data[cell_no]['outputs'][0]['text'] = cells_data[cell_no]['outputs'][0]['text'][1:]
              source_lines.append(f'# Code-Cell[{cell_no}]\n')

              print('---- AFTER  ------------------')
              print(f"No source_lines={len(cells_data[cell_no]['source'])}")
              print(f"   source_lines={''.join( cells_data[cell_no]['source'])}")
              print(f"No outputs={len(cells_data[cell_no]['outputs'][0]['text'])}")
              print(f"   outputs     ={ cells_data[cell_no]['outputs'][0]['text']}")
              print(f"{NORMAL}")

          if cell_type == 'code':
              process_code_cell(source_lines, cells_data, cell_no, EXCLUDED_CODE_CELL, section_title, include_cell, cells)
          elif cell_type == 'markdown':
              process_markdown_cell(source_lines, cells_data, cell_no, section_title, include_cell, cells, count_sections)
          else:
              die(f'Unknown cell_type "{cell_type}"')

    # Patch TableOfContents:
    toc_text+='</div>'
    DEBUG(f"ToC set to <{toc_text}>")
    if INCLUDE_TOC:
        cells_data[toc_cell_no]['source'] = [ toc_text ]
    else:
        cells_data[toc_cell_no]['source'] = [ '' ]

    DEBUG()
    DEBUG(f"cells to include[#{len(cells)}]=[{cells}]")
    cells.reverse()
    
    # END of filter_nb: remove deleted (EXCLUDED?) cells
    for cell_no in range(nb_cells(json_data)-1, -1, -1):
        #print(cell_no)
        if not cell_no in cells:
            DEBUG(f"del(cells[{cell_no}])")
            del(cells_data[cell_no])

    if NUM_QUESTIONS > 0:
        questions_text = '<hr><h1> Answers to Questions:</h1>'
        id = 'eof-questions'
        q=0
        for question_entry in QUESTIONS:
            q+=1
            summary = question_entry[0]
            detail = question_entry[1]
            questions_text += f'\n<b>{q}. {summary}</b>\n\n{detail}\n\n'

        cells_data.append( markdown_cell( id, [ questions_text ] ) )

    DEBUG(f"cells to include[#{len(cells)}]=[{cells}]")
    DEBUG(f"included markdown cells={incl_md_cells}")
    DEBUG(f"included code     cells={incl_code_cells}")
    DEBUG(f"excluded          cells={exclude_cells}")
    DEBUG()
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

    sec_cell_no=0

    div_sec='<div id="sec'
    len_div_sec=len( div_sec )
    for cell_no in range(nb_cells(json_data)):
          sec_cell_no+=1
          cell_type=json_data['cells'][cell_no]['cell_type']
          source_lines=json_data['cells'][cell_no]['source']
          if len(source_lines) == 0:
              if DEBUG: print("empty")
              continue

          if cell_type == 'code': current_section_text+='\n```'

          EXCLUDED_CODE_CELL=False
          if source_lines[0].find('#EXCLUDE') == 0 and cell_type == 'code':
              EXCLUDED_CODE_CELL=True
              # NOTE: Code will be excluded but continue to parse/search for variables settings

          for slno in range(len(source_lines)):
              source_line=source_lines[slno]

              if cell_type == 'code' and not EXCLUDED_CODE_CELL:
                  inc_source_line = source_line
                  if '| NB_' in source_line:
                      inc_source_line = source_line[ : source_line.find('| NB_') ]
                      source_lines[slno] = inc_source_line

                  if len(inc_source_line) > MAX_LINE_LEN:
                      show_long_code_line( 'SPLIT', inc_source_line, MAX_LINE_LEN, cell_no, section_title, EXCLUDED_CODE_CELL )
                  if len(source_line) > MAX_LINE_LEN:
                      DEBUG(f"[split_nb]: len={len(inc_source_line)} > {MAX_LINE_LEN} in cell {sec_cell_no} section={section_title} in line '{source_line}'")

              if div_sec in source_line:
                  start_pos = source_line.find( div_sec )
                  end_pos = start_pos + len_div_sec + source_line[ start_pos + len_div_sec : ].find('"')
                  next_section_no=source_line[ start_pos + len_div_sec : end_pos ]

                  close_div_pos = end_pos + source_line[ end_pos : ].find('</div')
                  next_section_title=source_line[ end_pos : close_div_pos ]

                  DEBUG(f"LINE[0]: <<<{source_line}>>>")
                  DEBUG(f"pos[{start_pos}:{end_pos}]")

                  if div_sec in source_line[ start_pos + len_div_sec : ]: die("OOPS")
    
                  if next_section_no.count('.') < SPLIT_ON_SECTIONS:
                      if current_section_text != '':
                          write_markdown(markdown_file_path, cell_no+1, cell_type, section_title, current_section_text)
                          current_section_text='' 
                      section_no=next_section_no
                      section_title=next_section_title
                      sec_cell_no=0
                      markdown_file=f'section_{section_no}.md'
                      markdown_file_path=f'md/{markdown_file}'
                      DEBUG(f"New section {section_no} seen")
                      md_files_index+=markdown_file+'\n'

              current_section_text+=source_line

          if cell_type == 'code': current_section_text+='\n```\n'

    if current_section_text != '':
        write_markdown(markdown_file_path, cell_no+1, cell_type, section_title, current_section_text)

    writefile('md/index.txt', 'w', md_files_index)


if __name__ == "__main__":
    main()

