# simex
A really bad simple regular expression engine

```
Characters:
    *       Any character (stops at the first instance of the proceding character or end of string)
```

```py
import se
expression = se.compile('some simex that can end with *')
assert expression.findall("some simex that can end with anything!") == ['some simex that can end with anything!']
```

I'm not sure why this exists. It took me like an hour to make.
