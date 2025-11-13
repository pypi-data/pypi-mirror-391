from typing import Any, Optional 




class strings:
    """String-related utilities."""
    
    lower_letters: tuple[str, ...] = tuple(chr(i) for i in range(97, 123))
    
    upper_letters: tuple[str, ...] = tuple(chr(i).upper() for i in range(97, 123))
    
    ascii_symbols: tuple[str, ...] = tuple(chr(i) for i in range(33, 123) if not chr(i).isalnum())
    
    digits: tuple[int, ...] = tuple(range(10))

    @staticmethod
    def remove_letters(text: str, *letters: str) -> str:
        """
        Remove specific letters from a string.
        
        arguments:
        text -- the text to filter
        *letters -- unlimited amount of letters to delete

        >>> strings.remove_letters("wlatlchi", "i", "l") → 'watch'
        """
        filtered = [l for l in text if l not in letters]
        return ''.join(filtered)


