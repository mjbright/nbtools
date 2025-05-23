#!/usr/bin/env python3

# Split FULL.md output markdown into separate mardown files

import os,sys

from inspect import currentframe, getframeinfo
from inspect import stack

VERBOSE=False

BLACK='\x1B[00;30m'
RED='\x1B[00;31m';      B_RED='\x1B[01;31m';      BG_RED='\x1B[07;31m'
GREEN='\x1B[00;32m';    B_GREEN='\x1B[01;32m';    BG_GREEN='\x1B[07;32m'
YELLOW='\x1B[00;33m';   B_YELLOW='\x1B[01;33m';   BG_YELLOW='\x1B[07;33m'
NORMAL='\x1B[00m'

def die(msg):
    sys.stdout.write(f"die: {sys.argv[0]} {RED}{msg}{NORMAL}\n")
    function = stack()[1].function
    lineno   = stack()[1].lineno
    #fname = stack()[1].filename
    #DEBUG_FD.write(f'[fn {function} line {lineno} {msg}'.rstrip()+'\n')
    print(f'... called from [fn {function}] line {lineno} {msg}')
    #DEBUG_FD.close()
    sys.exit(1)

def readfile(ipfile):
    if not os.path.exists(ipfile):
        die(f'No such input notebook {ipfile}')

    with open(ipfile, encoding='utf-8-sig') as json_file:
        return json_file.readlines()

def writefile(path, text='hello world\n', mode='w'):
    ofd = open(path, mode)
    ofd.write(text)
    ofd.close()

def split_markdown(arg):
    content = readfile(arg)

    frontMatter = True
    frontMatterText = [ content[0] ]
    currentLabText = ''

    for line in content[1:]:
        if frontMatter:
            frontMatterText.append(line)
            if line.startswith('---'):
                frontMatter=False
            continue

        if '#END:'   in line:
            currentLabText = ''.join(frontMatterText) + currentLabText
            writefile(opfile, currentLabText)
            currentLabText = ''
            continue


        if '#START:' in line:
            #START 1.InstallTerraform/IP_TF_Lab1.ipynb: . ~/scripts/nbtool.rc 10 Terraform "OP_TF_Lab1.InstallTerraform"
            print(f'START LINE={line}')
            startBits = line.split(' ')
            print(f'startBits={startBits}')
            #ipfile=startBits[1][:-1]
            ipfile=startBits[2].rstrip()
            print(f'ipfile={ipfile}')
            ipfileDir=ipfile[ : ipfile.find("/") ]
            print(f'ipfileDir={ipfileDir}')
            weight=startBits[5]
            print(f'weight={weight}')
            mode=startBits[6]
            print(f'mode={mode}')
            opfile=startBits[7].replace('"', "").replace('\n','') + '.md'
            print(f'opfile={mode}')
            #['<!--', '#START:', '10.Revision/IP_TF_Lab10.Revision.ipynb', '.', '~/scripts/nbtool.rc', '100', 'OpenTofu', 'OP_TF_Lab10.OpenTofuRevision', '-->\n']

            # If using tofu (based on variable exported in ~/.tool) rename output file:
            if os.getenv('TOOL','') == 'tofu':
                opfile = opfile.replace("_TF_", "_OTF_")
                print(f'Modified output file name for Tofu: {opfile}')
            #if os.path.exists("/home/student/.opentofu"):
            #    opfile = opfile.replace("_TF_", "_OTF_")
            #if os.path.exists("/home/student/.tofu"):
            #    opfile = opfile.replace("_TF_", "_OTF_")

            opfile = ipfileDir + '/' + opfile
            frontMatterText[1] = f'title: {opfile}\n'
            frontMatterText[3] = f'weight: {weight}\n'

            #if mode = "Tofu":
            #    opfile = opfile.replace("_TF_", "_OTF_")
            # frontMatterText = ''.join(frontMatterText)

            #print(f'IP={ipfile} mode={mode} OP={opfile}')
            #print(f'FRONTMATTER={frontMatterText}')
            currentLabText = ''
            line = ''
            continue
            #die("OK")

        currentLabText += line

def main():
    #global MODE, OP_NOTEBOOK, SAVE_MLINE_JSON

    PROG=sys.argv[0]
    a=1

    if len(sys.argv) == 1:
        die("Missing arguments")

    while a < len(sys.argv):
        arg = sys.argv[a]
        a += 1

        if arg == '-v':
            VERBOSE=True
            continue

        if arg.endswith(".md"):
            split_markdown(arg)
            sys.exit(0)

        die(f'Unknown argument: {arg}')


if __name__ == "__main__":
    main()

sys.exit(1)
