# Red_Aluminum

A utility script to convert a folder of text files into a single key-value text file.

Point it at a watch folder. Every .txt file in that folder will be watched and their contents copied into an output text file as a set of key-value lines. Any line breaks in the source file will be converted into spaces.

## Example

Given:

`foo.txt`:
``` Text 
Lorem
ipsum
```

`bar.txt`:
``` Text
dolor
```

The output file will be:

``` Text
foo = Lorem ipsum
bar = dolor
```

