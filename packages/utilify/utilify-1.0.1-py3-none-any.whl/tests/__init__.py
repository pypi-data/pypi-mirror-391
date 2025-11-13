from utilify import *

# Here is a few testings for utilify functions


"""Part 1: Main functions"""
def test_auto_correct():
	assert auto_correct("pytho", ["python"]) == "python"
	assert auto_correct("tree", ("apple", "gold"), "undefined") == "undefined"
	assert auto_correct("manufacture", ("", " ")) == None
	

def test_are_close():
	assert are_close("drama", "trauma", 0.9, 0.7) == None
	assert are_close("drama", "trauma", 0.9, 0.7, True) == "72%"
	assert are_close("dream", "lean", 1, 0.1) == None


def test_Index():
	assert Index("h", "hello") == 0
	assert Index("c", ["a", "b", "c", "d"]) == 2
	assert Index("v", "hello") == None



def test_location():
	assert location(2, ("a", "b", "c", "d")) == "c"
	assert get_location(0, "hello") == "h"
	assert get_location(19, "honor") == None
	
	
def test_countFreq():
	assert countFreq("color", ["o", "l"]) == {'o': 2, 'l': 1}
	assert countFreq("independent", "e") == {'e': 3}
	assert countFreq("", "k") == {'k': 0}
	assert countFreq("Rhine", "l") == {'l': 0}
	
	
def test_getabbr():
	assert getabbr("world health org") == "WHO"
	assert getabbr("united states Of america") == "USA"
	assert getabbr("information & communication tech") == "ICT"

"""Part 2: Classes"""
# Class variable
def test_variableClass():
	assert variable.deleteInd("hellon") == "hello"
	
	assert variable.delete("haunt", "a", 1) == 'hunt'
	
	assert variable.insert("l", "helo", 2) == 'hello'
	
	assert variable.replace("dag", 1, "o") == 'dog'

# Class strings
def test_stringsClass():
	assert strings.lower_letters[2] == 'c'
	
	assert strings.digits[-1] == 9
	
	assert strings.remove_letters("kwaltlchk", "l", "k") == 'watch'
