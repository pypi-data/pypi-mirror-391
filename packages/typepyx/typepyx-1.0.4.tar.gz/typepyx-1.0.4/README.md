# TypePyX

TypePyX is a Python module similar to TypeScript, providing strong type checking, constant variables, and array/dictionary types.

## Installation

```bash
pip install typepyx
```
## Features
- It supports
- Constant Variables
- Strong Type Checking
- Array Types like int[], str[] or list
- Dictionary Types like dict[str, int]
- Arithmetic operations
- Union Types support (int | str)

## Usage 
1. Variable with Types
2. Data Types
3. Basics around Arrays and Dictionary
4. Operations
5. Union Types

### Variable with Types
**Creating the variable**
```py
from typepyx import setType
'''
Creates an variable with type string
'''
string = setType(value="Hello, World!", type="str")

print(string) # prints Hello, World!
```

**Creating an Constant Variable**
```py
from typepyx import setType
'''
Creates an variable with type string and constant is True
'''
string = setType(value="Hello, World!", type="str", const=True)

print(string) # prints Hello, World!
```

**Changing Value to Variables**
```py
from typepyx import setType

string = setType(value="Hello, World!", type="str")
string2 = setType(value="Hi", type="str", const=True)
# Changes the string variable value (but make sure its same type as the new value)
string.value = "Hello"
# The Constant Variable cannot be changed if you do change it will give you an error
string2.value = "Const" # Error!
print(string) # prints Hello
```

### Data Types
**TypePyX** supports the following types:
- int - integer numbers
- float - decimal numbers
- str - string values **(e.g., "Hello")**
- bool - boolean values **(e.g., True, False)**
- list - arrays **(e.g., int[], str[])** *(Special Type)*
- dict - dictionaries **(e.g., dict[str, int])** *(Special Type)*
- any - any type

### Basics around Arrays and Dictionary
**To create an Typed Array**
```py
from typepyx import setType
# To create an typed array you must include an normal type and add [] after you typed an data type you want

ls = setType(value=[1,2,3], type="int[]")
print(ls) # [1,2,3]
```

**To create an Typed Dictionary**
```py
from typepyx import setType
'''
To create an typed dictionary
use this in setType type parameter dict[key_type, value_type]
key_type - the type of dictionary keys
value_type - the type of dictionary values
here is example of that down here
'''
dc = setType(value={"a": 1}, type="dict[str, int]")
print(dc)
```

### Operations 
**Here is an example of operations**
```py
from typepyx import setType

a = setType(5, "int")
b = setType(3, "int")

print(a + b)  # 8
print(a - b)  # 2
print(a * b)  # 15
print(a / b)  # 1.6666666667
```
**Arrays also support element-wise operations if both arrays have a same type and length**
```py
from typepyx import setType
arr1 = setType([1, 2, 3], "int[]")
arr2 = setType([4, 5, 6], "int[]")
print(arr1 + arr2)  # [5, 7, 9]
```

### Union Types
**Example of Union Types**
```py
import typepyx as tp
'''
To use Union Types use this in setType type parameters
type1 | type2 | ... 
type1 - type 1 to allow
type2 - type 2 to allow
... - more to allow
'''
# Variable can be either int or str
value = tp.setType(10, "int | str")
print(value)  # Output: 10

value.value = "Hello"
print(value)  # Output: Hello

value.value = 3.14  # ❌ Raises TypeError, because float is not allowed
```

Union Types work on arrays as well
```py
import typepyx as tp

# Variable can be either int or str array
value = tp.setType([10,"90"], "int | str[]")
print(value) # Prints [10, "90"]
value.append(7)
value.append("80")
print(value) # Prints [10, "90", 7, "80"]
value.append(3.14) # Error because the parameter type is float not int or str
```
