
# TODO:
# look at python3 option as mentioned here:
# - https://community.checkpoint.com/t5/API-CLI-Discussion/How-to-parse-from-nested-arrays-API-JQ/td-p/81172
#
# jq substrings:
# - https://stackoverflow.com/questions/61012699/jq-substr-equivalent-to-format-a-value

# Show 1st source line of each cell:
# jq -rc '.cells[].source[0]' $1

# Brutal dump of all outputs/source lines:
if [ "$1" = "-a" ]; then
    shift
    jq -rc '.cells[]? |
        { cell_type, outputs, source }' $1
    exit $?
fi

# Show first source line of every code cell:
if [ "$1" = "-c-s1" ]; then
    shift
    jq -rc '.cells[]? | select(.cell_type=="code") | .source[0]//.source? }' $1
    exit $?
fi

# Show keys & cell_type:
if [ "$1" = "-k-t" ]; then
    shift
    jq -rc '.cells[] | { keys: keys, type: .cell_type }'  $1
    exit $?
fi

# Count cells:
if [ "$1" = "-#" ]; then
    shift
    echo "Code     Cells: " $( jq -rc 'def count(stream): reduce stream as $i (0; .+1); count(.cells[]? | select(.cell_type=="code")) ' $1)
    echo "Markdown Cells: " $( jq -rc 'def count(stream): reduce stream as $i (0; .+1); count(.cells[]? | select(.cell_type=="markdown")) ' $1)
    echo "TOTAL    Cells: " $( jq -rc '.cells    | length' $1 )
    exit $?
fi

# Show code cells:
if [ "$1" = "-code" ]; then
    shift
    #jq -rc '.cells[]? | to_entries | map({name:.value, index:.key}) | select(.cell_type=="code") |
    jq -rc '.cells[]? | select(.cell_type=="code") | {
         type: .cell_type,
         source0: .source[]?,
         outputs0: .outputs[0].text[0]? |.[0:80]
    } '  $1
    exit $?
fi

# Show metadata
if [ "$1" = "-meta" ]; then
    shift
    jq -rc '.metadata' $1
    exit $?
fi

# Show markdown cells:
if [ "$1" = "-md" ]; then
    shift
    #jq -rc '.cells[]? | select(.cell_type=="markdown") | { type: .cell_type, markdown0: .source[]? }'  $1
    jq -rc '.cells[]? | select(.cell_type=="markdown") | { md: .source[]? }'  $1
    exit $?
fi

# TEST
if [ "$1" = "-t" ]; then
    shift
    set -x
    jq -rc '.cells[]? | select(.cell_type=="code") | { cell_type, source[0]//.source? }' $1
    jq -rc '.cells[]? | select(.cell_type=="code") | { cell_type, source[0]? }' $1
    jq -rc '.cells[]? | select(.cell_type=="code") | { cell_type, source[]? }' $1
    jq -rc '.cells[]? | select(.cell_type=="code") | { cell_type, source? }' $1
    jq -rc '.cells[]? | select(.cell_type=="code") | { cell_type, source }' $1
    jq -rc '.cells[]? | { cell_type, source }' $1
    jq -rc '.cells[]? | { cell_type, source\[0] }' $1
    jq -rc '.cells[]? | .source[0]//.source? }' $1
    #jq -rc '.cells[]? | { type: .cell_type, source0: .source[0]//.source? }' $1
    jq -rc '.cells[]? | { type: .cell_type, source0: .source[0] }' $1
    #jq -rc '.cells[]? | { type: .cell_type, keys: .keys() }' $1
    #jq -rc '.cells[]? | keys_unsorted }' $1
    jq -rc '.cells[] | { keys: keys, type: .cell_type }'  $1
    # LATEST TEST:
    #jq -rc '.cells[] | { keys: keys, type: .cell_type, source0: .source[]? }'  $1
    jq -rc '.cells[] | { keys: keys, type: .cell_type, source0: .source[]?, outputs: .outputs[]? }'  $1
    exit $?
fi

#jq -rc '.cells[] | { type: .cell_type, source0: .source[]?, outputs: .outputs[]? }'  $1
# Show keys & cell_type & beg. source/output:
#if [ "$1" = "-k-t" ]; then
    #shift
# DEFAULT:
    jq -rc '.cells[]? | {
        keys:     keys,
        type:     .cell_type,
        id:     .id,
        source0:  .source[0]? | .[0:40],
        #".cell_type": .outputs[0].text[0]? |.[0:40],
        outputs0: .outputs[0].text[0]? |.[0:40]
    }'  $1
    exit $?
#fi


exit
## --------------------------------------------------------------------------------

# Seen here:
# - https://gist.github.com/nishadhka/8b381af02662130e9adf877678d32548

 OUTPUT=$(jq '.cells[]? | select(.cell_type=="code") | .source[]?//.source' $f \
            | sed 's/^"//g;s/"$//g;s/\\n$//g;s/\\"/"/g;s/\\\\/\\/g;s/\\n/\n/g' \
            | pygmentize -l python 2>/dev/null \
            | grep $PATTERN)


jq -rc '.cells[] |
    { cell_type, outputs, source }' $1
    #{ cell_type, outputs, source }' $1
    #{ cell_type, outputs, source[] | first }' $1
    #cell_type, outputs, source' $1
    #cell_type, outputs, source[0]' $1
    # BAD{ cell_type, outputs, source } | join(" ")' $1

