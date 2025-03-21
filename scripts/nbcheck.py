#!/usr/bin/env python3

import json, sys, re, os
import uuid

from inspect import currentframe, getframeinfo
from inspect import stack

import subprocess

BLACK='\x1B[00;30m'
RED='\x1B[00;31m';      B_RED='\x1B[01;31m';      BG_RED='\x1B[07;31m'
GREEN='\x1B[00;32m';    B_GREEN='\x1B[01;32m';    BG_GREEN='\x1B[07;32m'
YELLOW='\x1B[00;33m';   B_YELLOW='\x1B[01;33m';   BG_YELLOW='\x1B[07;33m'
NORMAL='\x1B[00m'

VERBOSE=False

OP_NOTEBOOK = 'FULL.ipynb'
OP_HEADER_NOTEBOOK = None
OP_FOOTER_NOTEBOOK = None
SAVE_MLINE_JSON=False

'''
EXAMPLE cells from notebook json:

    {
      "cell_type": "markdown",
      "id": "present-plastic",
      "metadata": {},
      "source": [
        "<hr/>\n",
        "\n",
        "<!-- Why does this no longer work ??\n",
        "<img src=\"../../../static/images/ThickBlueBar.png\" />\n",
        "<img src=\"../../../static/images/LOGO.jpg\" width=200 />\n",
        "-->\n",
        "\n",
        "<img src=\"../images/ThickBlueBar.png\" />\n",
        "<img src=\"../images/LOGO.jpg\" width=200 />"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "id": "bbeb14a5",
      "metadata": {
        "tags": []
      },
      "outputs": [],
      "source": [
        "NB_QUIET"
      ]
    }

'''

def die(msg):
    sys.stdout.write(f"die: {sys.argv[0]} {RED}{msg}{NORMAL}\n")
    function = stack()[1].function
    lineno   = stack()[1].lineno
    #fname = stack()[1].filename
    #DEBUG_FD.write(f'[fn {function} line {lineno} {msg}'.rstrip()+'\n')
    print(f'... called from [fn {function}] line {lineno} {msg}')
    #DEBUG_FD.close()
    sys.exit(1)

def system(cmd):
    print(f'system({cmd})')
    if VERBOSE: print(f'system({cmd})')
    l_cmd = cmd.split(' ')

    proc = subprocess.Popen( l_cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return (out, err)

def writefile(path, text='hello world\n', mode='w'):
    ofd = open(path, mode)
    ofd.write(text)
    ofd.close()

def write_nb(opfile, json_data):
    with open(opfile, 'w') as json_file:
        json.dump(json_data, json_file)
          
def readfile(ipfile):
    if not os.path.exists(ipfile):
        die(f'No such input notebook {ipfile}')

    with open(ipfile, encoding='utf-8-sig') as json_file:
        return json_file.readlines()

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

def get_cell(json_data, cell_no):
    return json_data['cells'][cell_no]   
          
def count_cells(content, cell_type=None):
    count=0

    if cell_type == 'markdown':
        for cell in content["cells"]:
            if cell["cell_type"] == "markdown": count+=1
        return count

    if cell_type == 'code':
        for cell in content["cells"]:
            if cell["cell_type"] == "code": count+=1
        return count

    if cell_type == None:
        count = len(content["cells"])
        return count

    die(f'Unrecognized cell type {cell_type}')

def create_code_cell(nb,    cell_id=None, source_lines=[], metadata={}, execution_count=None, outputs=None):
    __create_cell(nb, 'code',     cell_id, source_lines, metadata, execution_count, outputs)

def create_markdown_cell(nb,cell_id=None, source_lines=[], metadata={}):
    __create_cell(nb, 'markdown', cell_id, source_lines, metadata)

def __create_cell(nb, cell_type, source_lines=[], metadata={}, execution_count=None, cell_id=None, outputs=None):
    #if not cell_id: cell_id = uuid.uuid4()
    if not cell_id: cell_id = uuid.UUID('{12345678-1234-5678-1234-567812345678}')

    if cell_type == 'markdown':
        return { "cell_type": "markdown", "id": cell_id, "metadata": metadata, "source": source_lines }
        
    if cell_type == 'code':
      # ?? "metadata": { "tags": [] },
        return { "nb": "f{nb}", "cell_type": "code", "id": cell_id, "metadata": metadata,
                 "source": source_lines,
                 "execution_count": execution_count, "outputs": outputs
               }
    die(f'Unknown cell type "{cell_type}"')

def main():
    global MODE, OP_NOTEBOOK, SAVE_MLINE_JSON

    PROG=sys.argv[0]
    a=1

    notebooks=[]
          
    if len(sys.argv) == 1:
        die("Missing arguments")

    while a < len(sys.argv):
        arg = sys.argv[a]
        a += 1

        # Change MODE: NBTOOL_COPY
        #if arg == '-mode':
            #arg = sys.argv[a]
            #a += 1
            #MODE=arg
            #continue
        if arg == '-v':
            VERBOSE=True
            continue

        if os.path.exists(arg) and os.path.isdir(arg):
            die(f"TODO: read folder of .ipynb files")

        if not arg.endswith(".ipynb"):
            die(f"Expected only .ipynb files - got {arg}")
          
        if not os.path.exists(arg):
            die(f"No such file - {arg}")

        notebooks.append(arg)

    print(f'notebooks={ notebooks }')
    print(f'Using OP_NOTEBOOK={OP_NOTEBOOK}')
    print()
    nb=0

    for notebook in notebooks:
        nb+=1
        content = read_json(notebook)

        #print(f'NOTEBOOK {notebook} keys: { keys( content ) }')
        num_cells = count_cells(content)
        num_markdown_cells = count_cells(content, cell_type='markdown')
        num_code_cells = count_cells(content, cell_type='code')
        #num_cells_info = f'number of cells: code={num_code_cells} markdown={num_markdown_cells} total={ num_cells }'
        num_cells_info = f'[cells: code={num_code_cells} markdown={num_markdown_cells} total={ num_cells }]'
        print(f'NOTEBOOK{nb} {num_cells_info} {notebook}')
        #print(f'\tkeys: { content.keys() }')
        #print(f'\tmetadata: { content["metadata"] }')
        print(f'\tnbformat: {content["nbformat"]} nbformat_minor: {content["nbformat_minor"]}')
        print()
        #print(f'\tcell[0]: { content["cells"][0] }')

        check_notebook( notebook, content )

MANDATORY=None
OPTIONAL=2
NB_KEYS = {
    'cells': MANDATORY,
    'metadata': MANDATORY,
    'nbformat': MANDATORY,
    'nbformat_minor': MANDATORY,
    'optional_test_xx': OPTIONAL,
    #'nosuch': MANDATORY
}

CELL_KEYS = {
    'code':     {
        'metadata':        MANDATORY,
        'execution_count': MANDATORY,
        'source':          MANDATORY,
        'outputs':         MANDATORY,
    },

    'markdown': {
        'metadata':        MANDATORY,
        'source':          MANDATORY,
        'attachments':     OPTIONAL,
    },
}

'''
cell={
    'cell_type': 'markdown',
    'id': 'f8c1e78d-afa4-400d-82cc-91a3765b0083',
    'metadata': {},
    'source': ['# UNUSED: Takeaways\n' ]}
cell={
    'cell_type': 'code',
    'execution_count': None,
    'id': 'f36a1ced-5c17-446b-b397-43dbe920b5b6',
    'metadata': {},
    'outputs': [],
    'source': []}
'''

def get_cellid_location(cellid, notebook_raw):
    #print(notebook_raw)
    #die("OK")
    if cellid != "UNKNOWN":
        #print(f'Looking for cellid {cellid} in notebook_raw')
        lineno=0
        for line in notebook_raw.split('\n'):
            lineno+=1
            #print(f'Line{lines} {line}')
            if cellid in line:
                #print(f'Found {cellid} in line{lines} ==> "{line}"')
                return (lineno, line)

    #die('No match')
    return (-1, '')

def check_notebook( notebook, content ):
    errors=0

    notebook_raw = ''.join(readfile(notebook))
    if len(notebook_raw) == 1:
        notebook_raw = json.dumps(notebook_raw, indent = 2, sort_keys=True)

    for key in list( NB_KEYS.keys() ):
        if not key in content:
            if NB_KEYS[ key ] == MANDATORY:
                errors+=1; print(f'\tERROR - {notebook}: Missing mandatory top-level key {key}')

    for key in content:
        if not key in NB_KEYS:
            errors+=1; print(f'\tERROR - {notebook}: Unknown key {key} seen')

    for cell in content['cells']:
        if VERBOSE: print(f'cell={cell}')

        if 'id' in cell:
            id = cell['id']
        else:
            errors+=1; print(f"\tERROR - missing 'id' in cell")
            id='UNKNOWN'

        if 'cell_type' in cell:
            cell_type = cell['cell_type']
        else:
            errors+=1; print(f"\tERROR - missing 'cell_type' in cell")
            continue
        if errors > 5: sys.exit(1)

        for key in list( CELL_KEYS[cell_type].keys() ):
            if key == 'id':        continue
            if key == 'cell_type': continue

            if not key in cell:
                if CELL_KEYS[cell_type][ key ] == MANDATORY:
                    ( lineno, location ) = get_cellid_location(id, notebook_raw)
                    errors+=1; print(f'\tERROR - {id}: Missing mandatory key {key} at line {lineno} in {cell_type} cell @ {location}')
            if errors > 5: sys.exit(1)

        for key in cell:
            if key == 'id':        continue
            if key == 'cell_type': continue

            if not key in CELL_KEYS[cell_type]:
                ( lineno, location ) = get_cellid_location(id, notebook_raw)
                errors+=1; print(f'\tERROR - {id}: Unknown key {key} at line {lineno} seen in {cell_type} cell @ {location}')
            if errors > 5: sys.exit(1)

    print(f'\nTOTAL - {notebook}: {errors} errors')
    return errors


if __name__ == "__main__":
    main()

sys.exit(0)

