
# nbtool

# ENV VAR BASED filtering / conditionals

## Outside of cells
- EXCLUDE_SECTION & INCLUDE_SECTION to include variable, e.g.  "shared" or "individual"

## Inside code cells
- EXCLUDE
- IF $VAR conditional execution

# integrate environments into nbtool.rc (have default or provide as argument)

Env-specific parameters:
- CLUSTER_NAME, e.g. default
- CLUSTER_TYPE shared, inidividual
- NUM_CONTROL 1
- CONTROL_PREFIX e.g. control
- NUM_WORKER 1
- WORKER_PREFIX e.g. worker
- USER_NAME ??

Variable presence & values checker
functions to check acceptable values
