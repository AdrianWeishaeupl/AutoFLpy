"""
This file is created in order to aid testing.
Author: Adrian Weishaeupl
Created 19/02/2020
"""


def check_str_in_content(string, content):
    """Checks that a certain string is present in the content
    provided. This is case sensitive. This is used in the test functions."""
    if string in content:
        # Checks that the string is present in the content
        occurrence = 0
        # Counts the number of occurrences
        for section in range((len(content) - len(string) + 1)):
            if content[section:section + len(string)] == string:
                occurrence = occurrence + 1
            else:
                continue
    else:
        occurrence = 0
    # Returns results
    return occurrence
