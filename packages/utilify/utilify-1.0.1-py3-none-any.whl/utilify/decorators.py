import time, os, contextlib, base64
from typing import Any, Optional 


def timer(func: Any) -> Any:
    """A decorator returning functions' elapsing time
    • Note: any function with this decorator won't return the code in the function, only the time taken.
    
    >>>
    	@timer
    	def timed():
    		for i in range(999999):
    			print(i)
    	
    	timed() → 6.5043
    """

    def wrapper(*args: Any, **kwargs: Any) -> None:
        start = time.time()
        with open(os.devnull, "w") as devnull:
            with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                try:
                    func(*args, **kwargs)
                except Exception:
                    end = time.time()
                    print(f"{end - start:.4f}")
                    raise
        end = time.time()
        print(f"{end - start:.4f}")

    return wrapper



def run_once(func: Any) -> Any | None:
    """A decorator preventing calling a function more than once
    >>>
    	@run_once
    	def temp():
    		print("Hello world")
    		
    	temp() → 'Hello world'
    	temp() → Exception: Function 'temp' can only run once.
    """
    called = False
    result = None
    def wrapper(*args, **kwargs):
        nonlocal called, result
        if not called:
            result = func(*args, **kwargs)
            called = True
        else:
            raise Exception(f"Function '{func.__name__}' can only run once.")
        return result
    return wrapper



def delayed(seconds: int) -> Any | None:
    """Delays the function when called for the given time."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            time.sleep(seconds)
            func(*args, **kwargs)
        return wrapper
    return decorator
    
    

def encrypted(func: Any) -> Any | None:
    """Encrypts the function to the base64 cipher.
    
    >>>
    	@encrypted
    	def example():
    		print("Hello world")
    	
    	example() → 'SGVsbG8gd29ybGQ='
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        try:
        	encoded = base64.b64encode(result.encode()).decode()
        except AttributeError:
        	return None
        return encoded
    return wrapper
 
 