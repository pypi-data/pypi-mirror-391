from time import perf_counter


def capitalize(string):
    """
       Capitalizes the first character of the string if it is lowercase.

       Args:
           string (str): The input string.

       Returns:
           str: The string with its first character capitalized.
    """
    lst = list(string)
    if ord(lst[0]) >= 97 and ord(lst[0]) <= 122:
        lst[0] = chr(ord(lst[0]) - 32)
    return "".join(lst)


def count(char, string):
    """
       Counts the number of occurrences of a substring in the given string.

       Args:
           char (str): Substring to search for.
           string (str): The input string.

       Returns:
           int: The number of times `char` appears in `string`.
       """
    count = 0
    str_lst = list(string)
    for x in range(len(str_lst)):
        if x + len(char) <= len(str_lst):
            if "".join(str_lst[x:x + len(char)]) == char:
                count += 1
    return count


def endswith(end_word, string):
    """
        Checks whether the string ends with the given substring.

        Args:
            end_word (str): Substring to check at the end.
            string (str): The input string.

        Returns:
            bool: True if `string` ends with `end_word`, False otherwise.
        """

    string_end_word = list(string)[-len(end_word):]
    if str(string_end_word) == end_word:
        return True
    return False


def find(find_word, string, start_index=0, end_index=None):
    """
       Finds the first occurrence of a substring in the string.

       Args:
           find_word (str): Substring to find.
           string (str): The input string.
           start_index (int, optional): Starting index for search. Default is 0.
           end_index (int, optional): Ending index for search. Default is None (end of string).

       Returns:
           int: Index of the first occurrence of `find_word`, or -1 if not found.
       """

    word_start_index = -1
    if end_index == None: end_index = len(string) - 1

    for x in range(len(string)):
        if x + len(find_word) <= len(string):
            if "".join(string[x + start_index:(x + start_index) + len(find_word)]) == find_word:
                if end_index >= x + start_index:
                    return x + start_index

    return word_start_index


def index(index_word, string, start_index=0, end_index=None):
    """
      Finds the first occurrence of a substring in the string.

      Args:
          index_word (str): Substring to find.
          string (str): The input string.
          start_index (int, optional): Starting index for search. Default is 0.
          end_index (int, optional): Ending index for search. Default is None (end of string).

      Raises:
          ValueError: If the substring is not found.

      Returns:
          int: Index of the first occurrence of `index_word`.
      """

    if end_index == None: end_index = len(string) - 1

    for x in range(len(string)):
        if x + len(index_word) <= len(string):
            if "".join(string[x + start_index:(x + start_index) + len(index_word)]) == index_word:
                if end_index >= x + start_index:
                    return x + start_index

    raise ValueError("substring not found")


def isdigit(string):
    """
      Checks if the string represents an integer number.

      Args:
          string (str): The input string.

      Returns:
          bool: True if `string` can be converted to int, False otherwise.
      """
    try:
        int(string)
        return True
    except Exception as e:
        return False


def islower(string):
    """
      Checks if all alphabetic characters in the string are lowercase.

      Args:
          string (str): The input string.

      Returns:
          bool: True if all letters are lowercase, False otherwise.
      """
    status = bool()
    for x in string:

        if ord(x) >= 65 and ord(x) <= 90:
            status = False
        elif ord(x) >= 97 and ord(x) <= 122:
            status = True

    return status


def isupper(string):
    """
    Checks if all alphabetic characters in the string are uppercase.

    Args:
        string (str): The input string.

    Returns:
        bool: True if all letters are uppercase, False otherwise.
    """
    status = bool()
    for x in string:
        if ord(x) >= 97 and ord(x) <= 122:
            status = False
        elif ord(x) >= 65 and ord(x) <= 90:
            status = True
    return status


def replace(old_word, new_word, string, count=1):
    """
       Replaces occurrences of a substring with a new substring.

       Args:
           old_word (str): Substring to be replaced.
           new_word (str): Substring to replace with.
           string (str): The input string.
           count (int, optional): Maximum number of replacements. Default is 1.

       Raises:
           ValueError: If `count` is not an integer.

       Returns:
           str: The string after replacements.
       """
    str_lst = list(string)

    try:
        count = int(count)
    except:
        raise ValueError("The count value should be integer!!!")

    for x in range(len(str_lst)):
        if x + len(old_word) <= len(str_lst):
            if "".join(str_lst[x:x + len(old_word)]) == old_word:
                if count > 0:
                    str_lst[x: x + len(old_word)] = new_word

                    count -= 1

    return "".join(str_lst)


def rstrip(string):
    """
    Removes trailing spaces from the string.

    Args:
        string (str): The input string.

    Returns:
        str: The string without trailing spaces.
    """
    index_first_letter = 0
    for x in range(len(string)):
        if string[-(x + 1)] != " ":
            index_first_letter = - (x + 1)
            break
    return string[:index_first_letter + 1]


def lstrip(string):
    """
    Removes leading spaces from the string.

    Args:
        string (str): The input string.

    Returns:
        str: The string without leading spaces.
    """

    index_first_letter = 0
    for x in range(len(string)):
        if string[x] != " ":
            index_first_letter = x
            break

    return string[index_first_letter:]


def swapcase(string):
    """
       Swaps the case of all alphabetic characters in the string.

       Args:
           string (str): The input string.

       Returns:
           str: The string with lowercase letters converted to uppercase and vice versa.
       """
    result = ''
    for x in string:
        if ord(x) >= 97 and ord(x) <= 122:
            result += chr(ord(x) - 32)
        elif ord(x) >= 65 and ord(x) <= 90:
            result += chr(ord(x) + 32)
        else:
            result += x
    return result
