import random, sys, os
from typing import Any, Optional 



class variable:
    """A toolkit for editing variables"""

    @staticmethod
    def deleteInd(var: str, var_ind: int = -1) -> str:
        """
        Delete a specific letter by index

        var -- the text
        var_ind -- the index of the letter, defaulted by -1 (last letter)
            
        >>> variable.Idelete("aktm", 1) → 'atm'
        """
        if var_ind < 0:
        	var_ind += len(var)
        return var[:var_ind] + var[var_ind+1:]


    @staticmethod
    def delete(var: str, letter: str, occurrences: int = 1) -> str:
        """
        Delete a letter by given occurrences
        
        arguments:
        var -- the text
        letter -- the targeted letter
        occurrences -- the occurrences of deleting the letter, defaulted by 1
            
        >>> variable.delete("messssy", "s", 2) → 'messy'
        """
        return var.replace(letter, "", occurrences)

    @staticmethod
    def insert(char: str, var: str, var_ind: int = -1) -> str:
        """
        Add a specific letter at a specific index.
        
        arguments:
        char -- the character
        var -- the text
        var_ind -- the index(placement) of the letter
        
        >>> variable.insert("d", "car", -1) → 'card'
        """
        return var[:var_ind] + char + var[var_ind:]

    @staticmethod
    def replace(var: str, var_ind: int, replacement: str) -> str:
        """
        Replace a letter by index.
        
        arguments:
        var -- the text
        var_ind -- the index of targeted letter
        replacement -- the replacer letter
        
        >>> variable.replace("burn", 1, "o") → 'born'
        """
        return var[:var_ind] + replacement + var[var_ind + 1:]

    @staticmethod
    def random_int(minimum: int, maximum: int) -> int:
        """Generates a random integer between two values"""
        return random.randint(minimum, maximum)

