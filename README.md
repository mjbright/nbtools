
# nbtools
Tools for working with Jupyter notebooks

# Pragmas implemented by nbtool.*

#### Warnings:
Produces text in a dark red box
```
# __WARN: You should have the environment variable STUDENT set in your environment, verify with env | grep STUDENT
```

#### Info:
Produces text in a dark green box
```
# __INFO: Some info
```

#### Error:
Produces text in a light red box
```
# __ERROR: She's gonna blow captain !
```

#### Details:
Produces summary/details in a box - can be used for interactive questions in labs

Also produces list of questions/answers at end (for non-interactive PDF)

```
# __DETAIL(summary question-1): the solution
```

```
# __DETAIL(summary question-2): another solution
```

