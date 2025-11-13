import pkgutil
__path__ = pkgutil.extend_path(__path__,__name__)
__path__.reverse()

__all__ = ['table','config','equal','expr','sym','context','flow','meta','multi','domain']
from pprint import pformat

"""
Open Assembly Tools (OASM) Core Module

This module provides a comprehensive set of fundamental data structures and utility classes
for advanced configuration management, expression processing, and assembly operations.

Key features include:
- Hybrid container types combining list and dictionary functionality
- Configuration management with JSON persistence capabilities
- Advanced expression evaluation system with operator overloading
- Context management for state preservation and manipulation
- Flow control utilities for programmatic assembly operations
- Metaprogramming capabilities for dynamic code generation
- Domain-specific language (DSL) constructs for custom assembly logic

Module structure:
- table: A flexible container that combines list and dictionary functionality
- config: Extends table with JSON file loading and saving capabilities
- equal: Deep equality comparison function for complex data structures
- expr: Expression evaluation system with comprehensive operator support
- sym: Symbolic expression constructor
- context: Context management for maintaining and switching execution states
- flow: Control flow management for assembly operations
- meta: Metaprogramming utilities for dynamic code generation
- multi: Multi-node assembly support for distributed operations
- domain: DSL decorator for custom assembly language constructs
"""

class table(list):
    """
    A flexible container that combines list and dictionary functionality.
    
    The table class extends the built-in list type while adding dictionary-like
    attribute access. This hybrid design allows for both sequential access by index
    and named access by attribute/key.
    
    Key features:
    - Supports list operations (append, extend, indexing)
    - Supports dictionary-like attribute and key access
    - Methods for deep copying and conversion to/from dictionaries
    - Callable interface that supports custom functions or method chaining
    
    Examples:
        t = table(1, 2, 3, a=4, b=5)
        print(t[0])  # Output: 1
        print(t.a)   # Output: 4
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize a new table instance.
        
        Parameters:
            *args: Positional arguments to be stored as list items
            **kwargs: Keyword arguments to be stored as attributes
            
        The initialization process:
        1. Stores all positional arguments as items in the list
        2. Stores all keyword arguments as attributes in the instance dictionary
        """
        super().__init__(args)
        self.__dict__.update(kwargs)
    def __getitem__(self, key=None):
        """
        Get an item from the table.
        
        Parameters:
            key: The key or index to retrieve. If a string, it accesses an attribute;
                otherwise, it accesses a list item.
                
        Returns:
            The requested item from the list or attribute from the dictionary.
            
        Raises:
            KeyError: If the key is a string and not found in __dict__
            IndexError: If the key is an integer and out of range for the list
            
        This method provides dual functionality:
        - String keys access attributes stored in __dict__
        - Other keys (typically integers) access list items
        """
        if type(key) is str:
            return self.__dict__[key]
        return super().__getitem__(key)
    def __setitem__(self, key, val):
        """
        Set an item in the table.
        
        Parameters:
            key: The key or index to set. If a string, it sets an attribute;
                otherwise, it sets a list item.
            val: The value to store at the specified key or index.
                
        This method provides dual functionality:
        - String keys set attributes in __dict__
        - Other keys (typically integers) set list items
        """
        if type(key) is str:
            self.__dict__[key] = val
        else:
            super().__setitem__(key, val)
    def __delitem__(self, key):
        """
        Delete an item from the table.
        
        Parameters:
            key: The key or index to delete. If a string, it deletes an attribute;
                otherwise, it deletes a list item.
                
        Raises:
            KeyError: If the key is a string and not found in __dict__
            IndexError: If the key is an integer and out of range for the list
            
        This method provides dual functionality:
        - String keys delete attributes from __dict__
        - Other keys (typically integers) delete list items
        """
        if type(key) is str:
            del self.__dict__[key]
        else:
            super().__delitem__(key)
    def __call__(self, *args, **kwargs):
        """
        Call method for the table class, supporting multiple operational modes.
        
        Parameters:
            *args: Positional arguments for the call
            **kwargs: Keyword arguments for the call
            
        Returns:
            - Result of the custom __call__ function if defined
            - Self if no arguments provided (identity operation)
            - Self after modification if arguments are provided (for method chaining)
            
        The method operates in three modes:
        1. Custom function execution: If a '__call__' attribute exists and is callable,
           it is executed with the table as the first argument
        2. Identity operation: If no arguments are provided, returns self
        3. Modification mode: If arguments are provided:
           - Positional arguments extend the list part
           - Keyword arguments update the dictionary part
           - Returns self to support method chaining
        """
        func = self.__dict__.get('__call__',None)
        if func is not None:
            return func(self,*args,**kwargs)
        if len(args) == 0 and len(kwargs) == 0:
            return self
        super().extend(args)
        self.__dict__.update(kwargs)
        return self
    def __repr__(self):
        """
        Return a string representation of the table.
        
        Returns:
            str: A string representation combining list items and dictionary attributes
                in a format similar to '[item1,item2,...,key1=value1,key2=value2,...]'
                
        The representation includes:
        1. All list items formatted with pformat for readability
        2. All dictionary attributes in key=value format
        3. Removes trailing commas for cleaner output
        """
        r = ''
        for i in self[:]:
            r += pformat(i) + ','
        for k,v in self.__dict__.items():
            r += f'{k}={pformat(v)},'
        if len(r) > 0 and r[-1] == ',':
            r = r[:-1]
        return '[' + r + ']'
    def __neg__(self):
        """
        Implement the unary negation operation for the table class.
        
        Returns:
            table: Returns self unchanged. This is a placeholder implementation
                to ensure the table class works smoothly with expression systems.
                
        This implementation makes the table class compatible with expression
        systems that may apply unary negation operations. By returning self,
        it effectively ignores the negation operation while maintaining compatibility.
        """
        return self
    def copy(self):
        """
        Create a shallow copy of the table.
        
        Returns:
            table: A new table instance with copies of the list items and dictionary attributes.
                
        This method creates a new table instance where:
        1. The list portion is populated with the items from the original table
        2. The dictionary portion is populated with the attributes from the original table
        3. The copies are shallow - nested mutable objects will still reference the same instances
        """
        return self.__class__(*self[:],**self.__dict__)
    @staticmethod
    def to_dict(x):
        """
        Convert a table or other data structure to a serializable dictionary.
        
        Parameters:
            x: The object to convert to a dictionary. This can be a table, list,
                tuple, dict, or any other serializable value.
                
        Returns:
            dict: A dictionary representation of the input object, with all nested
                objects also converted to dictionaries.
                
        The conversion process:
        1. For table instances: Creates a dictionary with a special class marker
           and converts both list items and dictionary attributes recursively
        2. For lists/tuples: Converts each element recursively and returns as a list
        3. For dictionaries: Converts each value recursively while preserving keys
        4. For other types: Returns the value unchanged
        
        This method is particularly useful for serialization purposes, allowing
        complex table structures to be converted to a format suitable for JSON.
        """
        if isinstance(x, table):
            return {f'__{x.__class__.__name__}__':table.to_dict(x[:])}|table.to_dict(x.__dict__)
        elif isinstance(x,(tuple,list)):
            return [table.to_dict(v) for v in x]
        elif isinstance(x,dict):
            return {k:table.to_dict(v) for k,v in x.items()}
        else:
            return x
    @classmethod
    def from_dict(cls,dct):
        """
        Reconstruct a table or derived class instance from a dictionary representation.
        
        Parameters:
            dct (dict): A dictionary containing the serialized representation of
                a table or derived class instance. The dictionary should include
                a special class marker key (__ClassName__) if it represents a table subclass.
                
        Returns:
            table or type: A reconstructed table instance if the dictionary contains
                a class marker, or the original dictionary otherwise.
                
        The reconstruction process:
        1. Checks for known table-derived classes in a predefined set
        2. Searches for a special class marker in the dictionary
        3. If found, extracts the list items, removes the marker, and instantiates
           the appropriate class with the list items and remaining dictionary attributes
        4. If no class marker is found, returns the original dictionary
        
        This method works as the complement to to_dict, allowing serialized
        table structures to be reconstructed from their dictionary representations.
        """
        cls = {table,config,expr,flow._tbl}|{cls}
        for i in cls:
            if f'__{i.__name__}__' in dct:
                lst = dct.pop(f'__{i.__name__}__')
                return i(*lst,**dct)
        return dct

class config(table):
    """
    Configuration management class with JSON file persistence capabilities.
    
    The config class extends the table container with methods for loading and
    saving configuration data to JSON files. This provides a convenient way to
    manage application settings, preferences, and other configurable data that
    needs to persist between sessions.
    
    Key features:
    - Inherits all the flexible container capabilities of the table class
    - JSON file loading and saving functionality
    - Support for hierarchical configuration inheritance
    - Deep copying with attribute modification for temporary configuration changes
    
    Class Attributes:
        root (str): Default directory path for configuration files (default: '../json')
    """
    # Default directory path for storing and retrieving configuration JSON files
    root = '../json'

    @classmethod
    def load(cls, name=None):
        """
        Load configuration data from a JSON file.
        
        Parameters:
            name (str, optional): The name of the configuration file to load.
                If not provided, the class name is used.
                
        Returns:
            config: A new config instance populated with the loaded data.
                
        Raises:
            FileNotFoundError: If the specified configuration file does not exist
            json.JSONDecodeError: If the file contains invalid JSON
            
        The loading process:
        1. Collects configuration data from parent classes (excluding table and config)
        2. Loads data from the specified JSON file
        3. Merges the parent class data with the file data
        4. Reconstructs and returns a config instance using from_dict
        
        The file path is constructed as: {config.root}/{cls.__module__}.{name or cls.__name__}.json
        """
        import json
        dct = {}
        for i in cls.__bases__:
            if i not in (table,config):
                dct |= i.load().__dict__
        with open(f'{config.root}/{cls.__module__}.{name or cls.__name__}.json') as f:
            val = json.load(f)
            if type(val) is dict:
                dct |= val
                return cls.from_dict(dct)
            else:
                val.__dict__ = dct | val.__dict__
                return val
            
    def save(self, *args):
        """
        Save configuration data to JSON files.
        
        Parameters:
            *args: Classes or instances to save. If not provided, saves for all
                parent classes and the instance itself.
                
        Raises:
            IOError: If there are issues writing to the file system
            TypeError: If the data cannot be serialized to JSON
            
        The saving process:
        1. If no arguments are provided, determines the save targets from the
           class hierarchy (excluding object, type, and immediate parents)
        2. Creates a copy of the instance dictionary
        3. For each target class/instance:
           - Constructs the file path based on module and class/instance name
           - For class targets: Only saves attributes defined in class annotations
           - For instance targets: Saves all attributes
           - Adds a special class marker for potential future reconstruction
           - Writes the data to a JSON file
        
        The file path format is: {config.root}/{target.__module__}.{target_name}.json
        """
        import json
        if len(args) == 0:
            args = self.__class__.__mro__[::-1][4:-1] + (self,)
        dct = self.__dict__.copy()
        for i in args:
            with open(f"{config.root}/{i.__module__}.{getattr(i,'__name__',i.__class__.__name__)}.json",'w') as f:
                if type(i) is type:
                    json.dump({k:dct.pop(k) for k in i.__annotations__}|{f'__{i.__name__}__':[]},f)
                else:
                    json.dump(dct|{f'__{i.__class__.__name__}__':[]},f)
    
    def __call__(self,*args,**kwargs):
        """
        Create a modified deep copy of the configuration or execute a custom callable.
        
        Parameters:
            *args: Positional arguments for the custom callable
            **kwargs: Keyword arguments to modify in the copied configuration
            
        Returns:
            - Result of the custom __call__ function if defined
            - A deep copy of the configuration with modified attributes if no custom callable exists
                
        The method operates in two modes:
        1. Custom function execution: If a '__call__' attribute exists and is callable,
           it is executed with the configuration as the first argument
        2. Deep copy mode: Creates a deep copy of the configuration and updates its
           attributes with the provided keyword arguments
           
        This method is particularly useful for creating temporary configuration
        variations while preserving the original configuration intact.
        """
        func = self.__dict__.get('__call__',None)
        if func is not None:
            return func(self,*args,**kwargs)
        import copy
        r = copy.deepcopy(self)
        for k,v in kwargs.items():
            setattr(r,k,v)
        return r

import operator

def equal(x, y):
    """
    Deep equality comparison for complex data structures.
    
    Parameters:
        x: First object to compare
        y: Second object to compare
        
    Returns:
        bool: True if x and y are deeply equal, False otherwise
        
    This function performs a recursive deep comparison between two objects,
    handling nested structures like lists, tuples, dictionaries, and table instances.
    
    The comparison process:
    1. Checks if x and y are of the same type
    2. For objects with __getitem__ method (like tables), gets their items
    3. For tuples, lists, and dictionaries, performs element-wise recursive comparison:
       - For dictionaries: Checks that all keys in x exist in y and have equal values
       - For sequences: Checks that all corresponding elements are equal
    4. For other types, falls back to the standard == operator
    
    This function is particularly useful for comparing complex nested data structures
    where shallow comparison (using ==) would not be sufficient.
    """
    if type(x) != type(y):
        return False
    if getattr(x,'__getitem__',None) is not None:
        x = x[:]
        y = y[:]
    if type(x) in (tuple,list,dict):
        if len(x) != len(y):
            return False
        if type(x) is dict:
            for k,v in x.items():
                if not equal(v,y.get(k,None)):
                    return False
        else:
            for i in range(len(x)):
                if not equal(x[i],y[i]):
                    return False
        return True
    return x == y
            
class expr(table):
    """
    Expression evaluation system with comprehensive operator support.
    
    The expr class extends the table container to provide a powerful expression
    evaluation system. It allows for the construction and evaluation of symbolic
    expressions with support for attribute access, item access, method calls,
    and a wide range of operators.
    
    Key features:
    - Chainable attribute and item access for building complex expressions
    - Comprehensive operator overloading for arithmetic and comparison operations
    - Lazy evaluation of expressions
    - Support for nested expressions and function calls
    - Self-referential expression handling
    
    This class forms the core of the expression evaluation system, enabling
    concise and powerful expression building for various assembly and configuration tasks.
    """
    def __getitem__(self, key):
        """
        Get an item from the expression or extend the expression chain.
        
        Parameters:
            key: The key/index to access or add to the expression chain.
                If a slice, it accesses list items; otherwise, it extends the expression.
                
        Returns:
            - List items if key is a slice
            - A new expr instance with the key appended to the expression chain
                
        This method has dual functionality:
        1. If the key is a full slice (:), it returns the underlying list items
        2. Otherwise, it creates a new expression by appending the key to the current expression
        
        Special handling for self-references:
        - If the expression contains a 'self' attribute, it preserves this attribute
          in the new expression while temporarily removing it during construction
        """
        if type(key) is slice and key == slice(None,None,None):
            return super().__getitem__(key)
        dct = self.__dict__
        if 'self' in dct:
            this = dct.pop('self')
            r = self.__class__(*self,key,**dct)
            r.__dict__['self'] = this
            dct['self'] = this
            return r
        else:
            return self.__class__(*self,key,**dct)
    def __getattr__(self, key):
        """
        Extend the expression chain with attribute access or handle special cases.
        
        Parameters:
            key: The attribute name to access
                
        Returns:
            - None if the key starts with '_' or is one of the special method names
            - A new expr instance with the attribute name appended to the expression chain otherwise
            
        This method handles attribute access for the expression system, with special behavior for:
        1. Special methods and attributes (starting with '_'): Returns None to avoid conflicts
        2. Known special method names: Returns None for methods like 'compute', 'getdoc', etc.
        3. Regular attribute access: Extends the expression chain by calling self[key]
            
        This allows for elegant expression building with attribute chaining while avoiding
        conflicts with Python's internal methods and handling special method cases appropriately.
        """
        return None if key.startswith('_') or key in ('compute','getdoc','size','shape') else self[key]
    def __repr__(self):
        """
        Return a string representation of the expression.
        
        Returns:
            str: A string representation of the expression in a human-readable format
                that shows the expression's structure and components.
                
        The representation depends on the expression's content:
        - Empty expressions return 'expr()'
        - Symbolic expressions (starting with None) begin with 'sym'
        - Regular expressions begin with 'expr(value)'
        - String components are appended with dot notation (e.g., '.attribute')
        - Table components are appended as function calls (e.g., '(args)')
        - Other components are appended as index access (e.g., '[index]')
        
        This method helps with debugging and visualization of complex expressions
        by creating a clear textual representation of the expression chain.
        """
        if len(self) == 0:
            return 'expr()'
        line = 'sym' if self[:][0] is None else 'expr('+pformat(self[:][0])+')'
        for i in self[:][1:]:
            if type(i) is str:
                line += f'.{i}'
            elif type(i) is table:
                line += '(' + repr(i)[1:-1] + ')'
            else:
                line += f'[{i}]'
        return line[1:] if line.startswith('.') else line
    def __call__(self, *args, **kwargs):
        """
        Evaluate the expression with the provided arguments.
        
        Parameters:
            *args: Arguments to be used during evaluation (not used in the current implementation)
            **kwargs: Keyword arguments to be used during evaluation (not used in the current implementation)
                
        Returns:
            The result of evaluating the expression chain
            
        This method evaluates the expression by processing each element in the expression chain:
        1. Starts with the initial value (first element of the chain)
        2. For each subsequent element in the chain:
           - Evaluates any nested expressions in the current element
           - Applies the appropriate operation based on the element type:
             - If string: Performs attribute access
             - If table: Performs function call with arguments from the table
             - Otherwise: Performs item/index access
        3. Handles self-referential expressions through the 'self' attribute
        4. Provides error recovery by converting exceptions into new expression nodes when appropriate
        
        The evaluation process supports complex nested expressions and maintains proper context for
        expressions that reference themselves through the 'self' attribute.
        """
        r = self[:][0]
        body = self[:][1:]
        body.append(table(*args,**kwargs))
        for i in range(len(body)):
            key = body[i]
            if type(key) is table:
                t = table(*key[:],**key.__dict__)
                for k in range(len(key)):
                    v = t[k]
                    if type(v) is self.__class__:
                        dct = self.__dict__|v.__dict__
                        if 'self' in dct:
                            this = dct.pop('self')
                            v = self.__class__(*v[:],**dct)
                            v.__dict__['self'] = this
                            t[k] = v() 
                        else:
                            t[k] = self.__class__(*v[:],**dct)()
                for k,v in key.__dict__.items():
                    if type(v) is self.__class__:
                        dct = self.__dict__|v.__dict__
                        if 'self' in dct:
                            this = dct.pop('self')
                            v = self.__class__(*v[:],**dct)
                            v.__dict__['self'] = this
                            t.__dict__[k] = v()
                        else:
                            t.__dict__[k] = self.__class__(*v[:],**dct)()
                if type(r) is self.__class__:
                    try:
                        v = r[:][0]
                        if v is None:
                            v = self.__dict__
                        for k in r[:][1:-1]:
                            geti = getattr(v,'__getitem__',None)
                            v = getattr(v,k) if geti is None else geti(k)
                        k = r[:][-1]
                        f = getattr(v,k,None) if type(k) is str else None 
                        if callable(f):
                            r = f(*t[:],**t.__dict__)
                        else:
                            if len(t) == 0 and len(t.__dict__) == 0:
                                geti = getattr(v,'__getitem__',None)
                                try:
                                    r = getattr(v,k) if geti is None else geti(k)
                                except:
                                    if r[:][0] is None:
                                        v = None
                                    r = v[k] if type(v) is self.__class__ else self.__class__(v,k)
                            else:
                                seti = getattr(v,'__setitem__',None)
                                if len(t) == 1 and len(t.__dict__) == 0:
                                    t = t[0]
                                setattr(v,k,t) if seti is None else seti(k,t)
                                r = expr(r[:][0])
                    except:
                        if not (i == len(body) - 1 and len(args) == 0 and len(kwargs) == 0):
                            r = r[t] if type(r) is self.__class__ else self.__class__(r,t)
                elif callable(r):
                    try:
                        r = r(*t[:],**t.__dict__)
                    except:
                        if not (i == len(body) - 1 and len(args) == 0 and len(kwargs) == 0):
                            r = self.__class__(r,t)
                else:
                    if not (i == len(body) - 1 and len(args) == 0 and len(kwargs) == 0):
                        r = self.__class__(r,t)
            else:
                r = r[key] if type(r) is self.__class__ else self.__class__(r,key)
        #print(self[:],args,kwargs,self.__dict__,r)
        return r
    def __lt__(a, b):
        """
        Create a new expression representing less than comparison of a and b.
        
        Parameters:
            a: The left operand for comparison
            b: The right operand for comparison
                
        Returns:
            expr: A new expression that evaluates to a < b
        """
        return a.__class__(operator.__lt__,table(a,b))
    def __le__(a, b):
        """
        Create a new expression representing less than or equal comparison of a and b.
        
        Parameters:
            a: The left operand for comparison
            b: The right operand for comparison
                
        Returns:
            expr: A new expression that evaluates to a <= b
        """
        return a.__class__(operator.__le__,table(a,b))
    def __eq__(a, b):
        """
        Create a new expression representing equality comparison of a and b.
        
        Parameters:
            a: The left operand for comparison
            b: The right operand for comparison
                
        Returns:
            expr: A new expression that evaluates to a == b
        """
        return a.__class__(operator.__eq__,table(a,b))
    def __ne__(a, b):
        """
        Create a new expression representing inequality comparison of a and b.
        
        Parameters:
            a: The left operand for comparison
            b: The right operand for comparison
                
        Returns:
            expr: A new expression that evaluates to a != b
        """
        return a.__class__(operator.__ne__,table(a,b))
    def __ge__(a, b):
        """
        Create a new expression representing greater than or equal comparison of a and b.
        
        Parameters:
            a: The left operand for comparison
            b: The right operand for comparison
                
        Returns:
            expr: A new expression that evaluates to a >= b
        """
        return a.__class__(operator.__ge__,table(a,b))
    def __gt__(a, b):
        """
        Create a new expression representing greater than comparison of a and b.
        
        Parameters:
            a: The left operand for comparison
            b: The right operand for comparison
                
        Returns:
            expr: A new expression that evaluates to a > b
        """
        return a.__class__(operator.__gt__,table(a,b))
    def __not__(a):
        """
        Create a new expression representing logical NOT of a.
        
        Parameters:
            a: The operand for logical NOT
                
        Returns:
            expr: A new expression that evaluates to not a
        """
        return a.__class__(operator.__not__,table(a))
    def __abs__(a):
        """
        Create a new expression representing absolute value of a.
        
        Parameters:
            a: The operand for absolute value
                
        Returns:
            expr: A new expression that evaluates to abs(a)
        """
        return a.__class__(operator.__abs__,table(a))
    def __round__(a):
        """
        Create a new expression representing rounding of a.
        
        Parameters:
            a: The operand for rounding
                
        Returns:
            expr: A new expression that evaluates to round(a)
        """
        return a.__class__(round,table(a))
    def __add__(a, b):
        """
        Create a new expression representing addition of a and b.
        
        Parameters:
            a: The left operand for addition
            b: The right operand for addition
                
        Returns:
            expr: A new expression that evaluates to a + b
        """
        return plus(a,b)
    def __radd__(a, b):
        """
        Create a new expression representing reverse addition of b and a.
        
        Parameters:
            a: The right operand for addition
            b: The left operand for addition
                
        Returns:
            expr: A new expression that evaluates to b + a
        """
        return plus(b,a)
    def __iadd__(a, b):
        """
        Create a new expression representing in-place addition of a and b.
        
        Parameters:
            a: The left operand for addition
            b: The right operand for addition
                
        Returns:
            expr: A new expression that evaluates to a + b
        """
        return plus(a,b)
    def __and__(a, b):
        """
        Create a new expression representing bitwise AND of a and b.
        
        Parameters:
            a: The left operand for bitwise AND
            b: The right operand for bitwise AND
                
        Returns:
            expr: A new expression that evaluates to a & b
        """
        return a.__class__(operator.__and__,table(a,b))
    def __rand__(a, b):
        """
        Create a new expression representing reverse bitwise AND of b and a.
        
        Parameters:
            a: The right operand for bitwise AND
            b: The left operand for bitwise AND
                
        Returns:
            expr: A new expression that evaluates to b & a
        """
        return a.__class__(operator.__and__,table(b,a))
    def __floordiv__(a, b):
        """
        Create a new expression representing floor division of a by b.
        
        Parameters:
            a: The dividend
            b: The divisor
                
        Returns:
            expr: A new expression that evaluates to a // b
        """
        return a.__class__(operator.__floordiv__,table(a,b))
    def __rfloordiv__(a, b):
        """
        Create a new expression representing reverse floor division of b by a.
        
        Parameters:
            a: The divisor
            b: The dividend
                
        Returns:
            expr: A new expression that evaluates to b // a
        """
        return a.__class__(operator.__floordiv__,table(b,a))
    def __inv__(a):
        """
        Create a new expression representing bitwise inversion of a.
        
        Parameters:
            a: The operand for bitwise inversion
                
        Returns:
            expr: A new expression that evaluates to ~a
        """
        return a.__class__(operator.__inv__,table(a))
    def __invert__(a):
        """
        Create a new expression representing bitwise NOT of a.
        
        Parameters:
            a: The operand for bitwise NOT
                
        Returns:
            expr: A new expression that evaluates to ~a
        """
        return a.__class__(operator.__invert__,table(a))
    def __lshift__(a, b):
        """
        Create a new expression representing bitwise left shift of a by b.
        
        Parameters:
            a: The value to be shifted
            b: The number of positions to shift
                
        Returns:
            expr: A new expression that evaluates to a << b
        """
        return a.__class__(operator.__lshift__,table(a,b))
    def __rlshift__(a, b):
        """
        Create a new expression representing reverse bitwise left shift of b by a.
        
        Parameters:
            a: The number of positions to shift
            b: The value to be shifted
                
        Returns:
            expr: A new expression that evaluates to b << a
        """
        return a.__class__(operator.__lshift__,table(b,a))
    def __mod__(a, b):
        """
        Create a new expression representing modulo operation of a by b.
        
        Parameters:
            a: The dividend
            b: The divisor
                
        Returns:
            expr: A new expression that evaluates to a % b
        """
        return a.__class__(operator.__mod__,table(a,b))
    def __rmod__(a, b):
        """
        Create a new expression representing reverse modulo operation of b by a.
        
        Parameters:
            a: The divisor
            b: The dividend
                
        Returns:
            expr: A new expression that evaluates to b % a
        """
        return a.__class__(operator.__mod__,table(b,a))
    def __mul__(a, b):
        """
        Create a new expression representing multiplication of a and b.
        
        Parameters:
            a: The left operand for multiplication
            b: The right operand for multiplication
                
        Returns:
            expr: A new expression that evaluates to a * b
        """
        return a.__class__(operator.__mul__,table(a,b))
    def __rmul__(a, b):
        """
        Create a new expression representing reverse multiplication of b and a.
        
        Parameters:
            a: The right operand for multiplication
            b: The left operand for multiplication
                
        Returns:
            expr: A new expression that evaluates to b * a
        """
        return a.__class__(operator.__mul__,table(b,a))
    def __matmul__(a, b):
        """
        Create a new expression representing matrix multiplication of a and b.
        
        Parameters:
            a: The left operand for matrix multiplication
            b: The right operand for matrix multiplication
                
        Returns:
            expr: A new expression that evaluates to a @ b
        """
        return a.__class__(operator.__matmul__,table(a,b))
    def __rmatmul__(a, b):
        """
        Create a new expression representing reverse matrix multiplication of b and a.
        
        Parameters:
            a: The right operand for matrix multiplication
            b: The left operand for matrix multiplication
                
        Returns:
            expr: A new expression that evaluates to b @ a
        """
        return a.__class__(operator.__matmul__,table(b,a))
    def __neg__(a):
        """
        Create a new expression representing unary negation of a.
        
        Parameters:
            a: The operand for unary negation
                
        Returns:
            expr: A new expression that evaluates to -a
        """
        return uminus(a)
    def __or__(a, b):
        """
        Create a new expression representing bitwise OR of a and b.
        
        Parameters:
            a: The left operand for bitwise OR
            b: The right operand for bitwise OR
                
        Returns:
            expr: A new expression that evaluates to a | b
        """
        return a.__class__(operator.__or__,table(a,b))
    def __ror__(a, b):
        """
        Create a new expression representing reverse bitwise OR of b and a.
        
        Parameters:
            a: The right operand for bitwise OR
            b: The left operand for bitwise OR
                
        Returns:
            expr: A new expression that evaluates to b | a
        """
        return a.__class__(operator.__or__,table(b,a))
    def __pos__(a):
        """
        Create a new expression representing unary plus of a.
        
        Parameters:
            a: The operand for unary plus
                
        Returns:
            expr: A new expression that evaluates to +a
        """
        return uplus(a)
    def __pow__(a, b):
        """
        Create a new expression representing exponentiation of a to the power of b.
        
        Parameters:
            a: The base
            b: The exponent
                
        Returns:
            expr: A new expression that evaluates to a ** b
        """
        return a.__class__(operator.__pow__,table(a,b))
    def __rpow__(a, b):
        """
        Create a new expression representing reverse exponentiation of b to the power of a.
        
        Parameters:
            a: The exponent
            b: The base
                
        Returns:
            expr: A new expression that evaluates to b ** a
        """
        return a.__class__(operator.__pow__,table(b,a))
    def __rshift__(a, b):
        """
        Create a new expression representing bitwise right shift of a by b.
        
        Parameters:
            a: The value to be shifted
            b: The number of positions to shift
                
        Returns:
            expr: A new expression that evaluates to a >> b
        """
        return a.__class__(operator.__rshift__,table(a,b))
    def __rrshift__(a, b):
        """
        Create a new expression representing reverse bitwise right shift of b by a.
        
        Parameters:
            a: The number of positions to shift
            b: The value to be shifted
                
        Returns:
            expr: A new expression that evaluates to b >> a
        """
        return a.__class__(operator.__rshift__,table(b,a))
    def __sub__(a, b):
        """
        Create a new expression representing subtraction of b from a.
        
        Parameters:
            a: The minuend
            b: The subtrahend
                
        Returns:
            expr: A new expression that evaluates to a - b
        """
        return minus(a,b)
    def __rsub__(a, b):
        """
        Create a new expression representing reverse subtraction of a from b.
        
        Parameters:
            a: The subtrahend
            b: The minuend
                
        Returns:
            expr: A new expression that evaluates to b - a
        """
        return minus(b,a)
    def __truediv__(a, b):
        """
        Create a new expression representing true division of a by b.
        
        Parameters:
            a: The dividend
            b: The divisor
                
        Returns:
            expr: A new expression that evaluates to a / b (floating point)
        """
        return a.__class__(operator.__truediv__,table(a,b))
    def __rtruediv__(a, b):
        """
        Create a new expression representing reverse true division of b by a.
        
        Parameters:
            a: The divisor
            b: The dividend
                
        Returns:
            expr: A new expression that evaluates to b / a (floating point)
        """
        return a.__class__(operator.__truediv__,table(b,a))
    def __xor__(a, b):
        """
        Create a new expression representing bitwise XOR of a and b.
        
        Parameters:
            a: The left operand for bitwise XOR
            b: The right operand for bitwise XOR
                
        Returns:
            expr: A new expression that evaluates to a ^ b
        """
        return a.__class__(operator.__xor__,table(a,b))
    def __rxor__(a, b):
        """
        Create a new expression representing reverse bitwise XOR of b and a.
        
        Parameters:
            a: The right operand for bitwise XOR
            b: The left operand for bitwise XOR
                
        Returns:
            expr: A new expression that evaluates to b ^ a
        """
        return a.__class__(operator.__xor__,table(b,a))
    
# Root symbolic expression for creating symbolic references
sym = expr(None)  # Symbolic expression root used for creating attribute-based symbol paths

class plus_minus:
    """Plus and Minus operation handler for symbolic and numeric expressions.
    
    This class handles both unary and binary arithmetic operations (addition and subtraction)
    for symbolic expressions and numeric values. It implements intelligent expression
    simplification and proper handling of mixed symbolic and numeric operands.
    
    Key features:
    - Handles unary operations (uplus, uminus) with single arguments
    - Handles binary operations (plus, minus) with two arguments
    - Supports mixed operand types (int, float, expr)
    - Performs expression simplification by combining numeric terms
    - Properly propagates unary minus through nested expressions
    - Maintains symbolic structure for non-numeric operations
    
    The class is instantiated as four global instances:
    - plus: Binary addition operator
    - minus: Binary subtraction operator
    - uplus: Unary plus operator (identity)
    - uminus: Unary minus operator (negation)
    """
    def __init__(self,name):
        self._name = name
    def __repr__(self):
        return self._name
    def __call__(self,*args):
        if len(args) == 1:
            x = args[0]
            if self._name == 'uplus':
                return x
            if type(x) is expr:
                if len(x) > 0 and x[:][0] is uminus:
                    return x[:][1][0]
                elif len(x) > 0 and x[:][0] is plus:
                    return expr(plus,table(uminus(x[:][1][0]),uminus(x[:][1][1])))
                else:
                    return expr(uminus,table(x))
            return -x
        if type(args[0]) not in (int,float,expr) or type(args[1]) not in (int,float,expr):
            if type(args[0]) is expr or type(args[1]) is expr:
                return expr(plus if self._name == 'plus' else minus,table(*args))
            return args[0]+args[1] if self._name == 'plus' else args[0]-args[1] 
        atom = []
        term = []
        for i in range(2):
            x = args[i]
            sub = i == 1 and self._name == 'minus'
            if type(x) is expr:
                if len(x) > 0 and x[:][0] is plus:
                    t = x[:][1]
                    (term if type(t[0]) is expr else atom).append(-t[0] if sub else t[0])
                    (term if type(t[1]) is expr else atom).append(-t[1] if sub else t[1])
                else:
                    term.append(-x if sub else x)
            else:
                atom.append(-x if sub else x)
        if len(atom) == 0:
            r = 0
        else:
            r = sum(atom)
        for i in term:
            if type(r) is not expr and r == 0:
                r = i
            else:
                r = expr(plus,table(r,i))
        return r

plus = plus_minus('plus')
minus = plus_minus('minus')
uplus = plus_minus('uplus')
uminus = plus_minus('uminus')

class context_switch:
    def __init__(self, ctx, tbl):
        self.ctx = ctx
        self.tbl = tbl
    def __enter__(self):
        self.top = self.ctx <= self.tbl
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ctx <= self.top

class context:
    """
    Context management class with stack-based scoping and attribute forwarding.
    
    The context class provides a stack-based scoping mechanism that allows
    for pushing and popping context frames. It forwards attribute and item
    access operations to the top of the stack, while maintaining a stack of
    context objects for nested scoping.
    
    Key features:
    - Stack-based context management with push/pop functionality
    - Attribute and item forwarding to the top context frame
    - Context switching support via operator overloading
    - Automatic context creation and cleanup with __enter__/__exit__
    - Customizable table type for context frames
    
    This class is particularly useful for creating nested scopes where
    variables can be temporarily shadowed or modified, with automatic
    restoration when exiting the scope.
    """
    def __init__(self,*args,**kwargs):
        tbl = kwargs.pop('table',table)
        object.__setattr__(self,'_tbl',tbl)
        object.__setattr__(self,'_new',lambda:tbl(*args,**kwargs))
        object.__setattr__(self,'_stk',[])
        self.__enter__()
    def __getattr__(self, key):
        return getattr(self._stk[-1],key)
    def __setattr__(self, key, val):
        setattr(self._stk[-1],key,val)
    def __getitem__(self,key):
        return self._stk[-1][key]
    def __setitem__(self,key,val):
        self._stk[-1][key] = val
    def __delitem__(self,key):
        del self._stk[-1][key]
    def __len__(self):
        return len(self._stk[-1])
    def __repr__(self):
        return repr(self._stk[-1])
    def __call__(self, *args, **kwargs):
        return self._stk[-1] if len(args) == 0 and len(kwargs) == 0 else self._stk[-1](*args,**kwargs)
    def __le__(self,val):
        top = self._stk[-1]
        self._stk[-1] = val
        return top
    def __lt__(self, other):
        return context_switch(self, other)
    def __enter__(self):
        top = self._new()
        self._stk.append(top)
        return top
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stk.pop()

class flow(table):
    """
    Flow control container with dynamic attribute and item access.
    
    The flow class extends the table container to provide a specialized
    container for managing flow control structures. It features dynamic
    attribute and item access with auto-vivification - creating new flow
    instances on-demand when accessing non-existent keys.
    
    Key features:
    - Auto-vivification: Creates new flow instances for non-existent keys
    - Unified attribute and item access
    - String-based key normalization
    - Special handling for reserved attributes
    - Compatibility with table operations
    
    This class is designed to facilitate the creation of tree-like structures
    for flow control, where nodes can be dynamically created as needed.
    """
    def __getitem__(self, key):
        if type(key) is slice:
            return super().__getitem__(key)
        key = str(key)
        val = self.__dict__.get(key,None)
        if val is None:
            val = self.__class__()
            self.__dict__[key] = val
        return val
    def __getattr__(self, key):
        return None if key.startswith('_') or key in ('compute','getdoc','size','shape') else self[key]
    def __call__(self, *args, **kwargs):
        if not (len(args) == 0 and len(kwargs) == 0):
            super().append(self.__class__(*args,**kwargs))
        return self
    def clear(self):
        super().clear()
        self.__dict__.clear()

flow = context(table=flow)

class meta:
    """
    Metadata container for tracking hierarchical information and enabling function calls.
    
    The meta class provides a hierarchical container that stores metadata as a tuple
    (__meta__) and supports dynamic attribute and item access. When accessing non-existent
    keys, it creates new meta instances with extended metadata tuples.
    
    Key features:
    - Hierarchical metadata storage as tuples
    - Dynamic creation of child meta instances on attribute/item access
    - Function call delegation to the first metadata element
    - Unified attribute and item access patterns
    - Special handling for None keys (returns self)
    
    This class is primarily used to create hierarchical function call patterns,
    where metadata forms a path that can be traversed and eventually executed as a function call.
    """
    def __init__(self, *args):
        self.__meta__ = args
    def __getattr__(self, key):
        return None if key.startswith('_') or key in ('compute','getdoc','size','shape') else self[key]
    def __getitem__(self, key):
        if key is None:
            return self        
        hashable = getattr(key,'__hash__',None)
        val = None if hashable is None else self.__dict__.get(key,None)
        if val is None:
            val = self.__class__()
            val.__dict__['__meta__'] = self.__meta__ + (key,)
            if hashable is not None:
                self.__dict__[key] = val
        return val
    def __call__(self, *args, **kwargs):
        return self.__meta__[0](*args,*self.__meta__[1:],**kwargs)

class multi(meta):
    """
    Multi-target container for managing multiple instances or operations.
    
    The multi class extends meta to provide specialized functionality for managing
    multiple targets or performing operations across multiple instances. It enhances
    the meta class with multi-target function call behavior and special handling for
    collections of nodes.
    
    Key features:
    - Extended metadata tracking from meta class
    - Multi-target function call delegation
    - Special handling for node collections (lists, tuples, ranges)
    - Support for single-target and multi-target modes
    - Automatic conversion of range objects to lists
    
    This class is designed to facilitate operations that need to be applied to multiple
    targets, providing a unified interface for both single and multiple target scenarios.
    """
    def __call__(self, *args, **kwargs):
        if len(self.__meta__) == 1:
            val = self.__class__()
            val.__dict__['__meta__'] = self.__meta__ + args
            return val
        elif len(self.__meta__) == 2:
            nodes = getattr(self.__meta__[0],'multi',None)
            if nodes is None:
                return self.__meta__[1](*args,**kwargs)
        else:
            nodes = self.__meta__[2]
            if type(nodes) is range:
                nodes = list(nodes)
            if type(nodes) not in (tuple,list):
                nodes = [nodes]
            if len(nodes) == 0:
                return self.__meta__[1](*args,*self.__meta__[3:],**kwargs)
        env = self.__meta__[0]()
        for node in nodes:
            tbl = getattr(env,str(node),None)
            if tbl is None:
                with self.__meta__[0] as tbl:
                    pass
                env[str(node)] = tbl
            self.__meta__[0] <= tbl
            self.__meta__[1](*args,*self.__meta__[3:],**kwargs)
        self.__meta__[0] <= env
                        
import ast, inspect, copy

class FindReg(ast.NodeVisitor):
    def __init__(self, regq):
        self.regq = regq
        self.found = False
    def visit_Name(self, node):
        if self.regq(node.id):
            self.found = True
            
def RegQ(node, regq):
    visitor = FindReg(regq)
    visitor.visit(node)
    return visitor.found
    
class WithPass(ast.NodeTransformer):
    def __init__(self, regq, env={}):
        self.regq = regq
        self.env = env
    def visit_If(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        If = self.env['If']
        if type(If) is not str:
            If = 'If'
        Else = self.env['Else']
        if type(Else) is not str:
            Else = 'Else'
        if isinstance(node.test, ast.Call) and node.test.func.id == '_':
            node.test.func.id = If
        elif RegQ(node.test, self.regq):
            node.test = ast.Call(func=ast.Name(id=If, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset), args=[node.test], keywords=[], lineno=node.lineno, col_offset = node.col_offset)
        if isinstance(node.test, ast.Call) and node.test.func.id == If:
            withs = [ast.With(items=[ast.withitem(context_expr = node.test)], body=node.body, lineno=node.lineno, col_offset = node.col_offset)]
            if len(node.orelse):
                withs.append(ast.With(items=[\
                ast.withitem(context_expr = \
                ast.Call(func=ast.Name(id=Else, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset),\
                args=[], keywords=[], lineno=node.lineno, col_offset = node.col_offset),\
                lineno=node.lineno, col_offset = node.col_offset)], \
                body=node.orelse, lineno=node.lineno, col_offset = node.col_offset))
            return withs
        return node
    def visit_While(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        While = self.env['While']
        if type(While) is not str:
            While = 'While'
        if isinstance(node.test, ast.Name) and node.test.id == '_':
            node.test = ast.Call(func=ast.Name(id=While, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset), args=[], keywords=[], lineno=node.lineno, col_offset = node.col_offset)
        elif isinstance(node.test, ast.Call) and node.test.func.id == '_':
            node.test.func.id = While
        elif RegQ(node.test, self.regq):
            node.test = ast.Call(func=ast.Name(id=While, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset), args=[node.test], keywords=[], lineno=node.lineno, col_offset = node.col_offset)
        if isinstance(node.test, ast.Call) and node.test.func.id == While:
            return ast.With(items=[ast.withitem(context_expr = node.test)], body=node.body, lineno=node.lineno, col_offset = node.col_offset)
        return node
    def visit_For(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        For = self.env['For']
        if type(For) is not str:
            For = 'For'
        if isinstance(node.iter, ast.Call) and node.iter.func.id == '_':
            node.iter.func.id = For
        elif RegQ(node.target, self.regq):
            node.iter = ast.Call(func=ast.Name(id=For, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset), args=[node.iter], keywords=[], lineno=node.lineno, col_offset = node.col_offset)
        if isinstance(node.iter, ast.Call) and node.iter.func.id == For:
            node.target.ctx = ast.Load()
            if len(node.iter.args) == 1 and isinstance(node.iter.args[0], ast.Call) and node.iter.args[0].func.id == 'range':
                node.iter.args[0] = ast.Tuple(node.iter.args[0].args, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset)
            node.iter.args = [node.target] + node.iter.args
            return ast.With(items=[ast.withitem(context_expr = node.iter)], body=node.body, lineno=node.lineno, col_offset = node.col_offset)
        return node
    def visit_Assign(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        Set = self.env['Set']
        if type(Set) is not str:
            Set = 'Set'
        if isinstance(node.targets[0], ast.Name) and isinstance(node.targets[0], ast.Name) and self.regq(node.targets[0].id):
            node.targets[0].ctx = ast.Load()
            return ast.Expr(value=ast.Call(func=ast.Name(id=Set, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset), args=[node.targets[0], node.value], keywords=[], lineno=node.lineno, col_offset = node.col_offset), lineno=node.lineno, col_offset = node.col_offset)
        return node
    def visit_Call(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        Call = self.env['Call']
        if type(Call) is not str:
            Call = 'Call'
        func = getattr(node.func, 'id', None)
        if func is not None and self.env.get('#'+func, None) is not None:
            return ast.Call(func=ast.Name(id=Call,ctx=ast.Load(),lineno=node.lineno,col_offset=node.col_offset),args=[ast.Constant(value=node.func.id,lineno=node.lineno,col_offset=node.col_offset)]+node.args,keywords=[],lineno=node.lineno,col_offset=node.col_offset)
        return node
    def visit_Return(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        Return = self.env['Return']
        if type(Return) is not str:
            Return = 'Return'
        return ast.Expr(value=ast.Call(func=ast.Name(id=Return,ctx=ast.Load(),lineno=node.lineno,col_offset=node.col_offset),args=\
            node.value.elts if type(node.value) is ast.Tuple else ([] if node.value is None else [node.value]),keywords=[],lineno=node.lineno,col_offset=node.col_offset), lineno=node.lineno, col_offset = node.col_offset)
                           
class SubPass(ast.NodeTransformer):
    def __init__(self, env={}):
        self.env = env
        self.regs = {}
    def visit_FunctionDef(self, node):
        #print(ast.dump(node))
        self.regs = {'_':[]}
        reg = -1
        kws = len(node.args.defaults)
        for arg in node.args.args[:(-kws or None)]:
            if arg.annotation is None:
                reg += 1
            else:
                reg = arg.annotation.value
                self.regs['_'].append(reg)
                arg.annotation = None
            self.regs[arg.arg] = ast.Subscript(value=ast.Name(id='R',ctx=ast.Load(),lineno=node.lineno,col_offset=node.col_offset), \
            slice=ast.Index(value=ast.Constant(value=reg,lineno=node.lineno,col_offset=node.col_offset)), \
            lineno=node.lineno,col_offset=node.col_offset)
        self.regs['_'].append(reg)
        node.regs = self.regs['_']
        self.generic_visit(node)
        self.env['#'+node.name] = self.regs['_']
        self.regs = {}
        Func = self.env['Func']
        if type(Func) is not str:
            Func = 'Func'
        node.args.args = node.args.args[-kws:] if kws else []
        node.body = [ast.With(items=[ast.withitem(context_expr=ast.Call(func=ast.Name(id=Func,ctx=ast.Load(),lineno=node.lineno, col_offset = node.col_offset), \
            args=[ast.Constant(value=node.name,lineno=node.lineno,col_offset=node.col_offset)]+ \
                [ast.Constant(value=i,lineno=node.lineno,col_offset=node.col_offset) for i in node.regs], \
                keywords=[],lineno=node.lineno,col_offset=node.col_offset))],body=node.body, lineno=node.lineno,col_offset=node.col_offset)]
        return node
    def visit_Name(self, node):
        #print(ast.dump(node))
        if node.id != '_':
            value = self.regs.get(node.id, None)
            if value is not None:
                value = copy.copy(value)
                value.ctx = node.ctx
                return value
        return node
    def visit_Assign(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        if isinstance(node.targets[0], ast.Name):
            value = self.regs.get(node.targets[0].id, None)
            if value is not None:
                value = copy.copy(value)
                value.ctx = ast.Store()
                node.targets[0] = value
        return node

def domain(ctx={}, regq=None, sub=None, dump=False):
    """Domain-specific language (DSL) decorator for custom assembly language constructs.
    
    This decorator enables the creation of domain-specific assembly languages by transforming
    function source code through AST manipulation. It provides a framework for customizing
    and extending assembly-like syntax for specific hardware or application domains.
    
    Args:
        ctx (dict, optional): Context dictionary containing variables and symbols available
            in the DSL environment. Defaults to empty dict.
        regq (callable, optional): Register query function used to identify and process
            register references in the DSL code. If provided, triggers the WithPass AST
            transformation.
        sub (bool/callable, optional): AST transformation option:
            - True: Apply SubPass transformation with the provided context
            - ast.NodeTransformer instance: Apply custom transformer class with context
            - callable: Apply custom callable transformation directly to the AST
            - None: No substitution transformation (default)
        dump (bool, optional): If True and regq is provided, prints the unparsed transformed
            AST for debugging purposes. Defaults to False.
    
    Returns:
        callable: A decorator that transforms the decorated function's source code via AST
            manipulation and returns a wrapper that executes the transformed code in the
            augmented environment.
    
    Process flow:
        1. Extracts the source code of the decorated function
        2. Normalizes indentation to process the code correctly
        3. Parses the code into an Abstract Syntax Tree (AST)
        4. Removes existing decorators from the AST
        5. Applies specified AST transformations (substitution and/or register query)
        6. Compiles the transformed AST into executable code
        7. Creates a wrapped function that executes in the augmented environment
    
    This decorator is particularly useful for creating hardware-specific assembly languages,
    instruction set simulators, and domain-specific compilation passes within the oasm framework.
    """
    def decorator(func):
        src = inspect.getsourcelines(func)[0]
        indent = len(src[0]) - len(src[0].lstrip())
        src = ''.join([line[indent:] for line in src])
        node = ast.parse(src)
        node.body[0].decorator_list = []
        if sub is True:
            node = SubPass(ctx).visit(node)
        elif isinstance(sub, ast.NodeTransformer):
            node = sub(ctx).visit(node)
        elif callable(sub):
            node = sub(node)
        if callable(regq):
            node = WithPass(regq,ctx).visit(node)
            if dump:
                unparse = getattr(ast, 'unparse', None)
                if unparse is not None:
                    print(unparse(node))
        env = func.__globals__.copy()
        env.update(ctx)
        exec(compile(node, filename='', mode='exec'), env)
        def wrap(*args, **kwargs):
            env.update(ctx)
            return eval(func.__name__, env)(*args, **kwargs)
        return wrap
    return decorator