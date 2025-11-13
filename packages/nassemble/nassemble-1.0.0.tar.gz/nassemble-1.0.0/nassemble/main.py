#
### Importing Modules. ###
#
import os
import argparse


#
### File extensions to read. ###
#
file_extensions_to_read: list[str] = [
    ".txt",
    ".md",
    ".py",
    ".cpp",
    ".hpp",
    ".h",
    ".c",
    "makefile"
]

#
### Keywords to skip. ###
#
keywords_to_skip: list[str] = []


#
### Function to add the content of a given file into the global text. ###
#
def add_file(filepath: str, txt: str) -> str:

    """
    Function to add the content of a given file into the global text.

    Args:
        - filepath (str): File to read content from
        - txt (str): Current global file text

    Returns:
        str: Updated global file text
    """

    #
    file_content: str = ""

    #
    try:

        #
        ### Open the file and gets it content. ###
        #
        with open(filepath, "r", encoding="utf-8") as f:
            #
            file_content = f.read()

    #
    except Exception as e:
        #
        print(f"Warning: Could not read file {filepath}. Error: {e}")
        #
        return txt

    #
    ### Skip if the file is too short. ###
    #
    if len(file_content) < 50:
        #
        return txt

    #
    ### Add the content of the file. ###
    #
    txt += f"""

---------------------------------
FILE: {filepath}
---------------------------------

{file_content}

---------------------------------

"""

    #
    ### Return the updated string. ###
    #
    return txt


#
### Function to recursively explore a folder and for each file adds its content into a global text file. ###
#
def explore_dir(dirpath: str, txt: str, remaining_depth: int = -1) -> str:

    """
    Function to recursively explore a folder and for each file adds its content into a global text file.

    Args:
        - dirpath (str): Current path that we need to recursively explore.
        - txt (str): Updated global file text

    Returns:
        str: Updated global file text
    """

    #
    ### Ensure the dirpath ends with a '/' before adding any file name. ###
    #
    if not dirpath.endswith(os.path.sep):
        #
        dirpath = dirpath + os.path.sep

    #
    ### List of subdirectories to recursively explore. ###
    #
    dirlist: list[str] = []
    #
    ### List of files to read content from. ###
    #
    filelist: list[str] = []

    #
    ###
    #
    subelements: list[str] = []
    #
    try:
        #
        subelements = os.listdir(dirpath)
    #
    except Exception as e:
        #
        print(f"Warning: Could not explore directory {dirpath}. Error: {e}")
        #
        return txt

    #
    ### Explore all the elements from the current folder. ###
    #
    for elt in subelements:

        #
        ### Gets the full element path. ###
        #
        eltpath: str = os.path.join(dirpath, elt)

        #
        ### We will be not sensible to the case for filtering. ###
        #
        elt_low: str = elt.lower()

        #
        ### Automatically filtering files that are meant to be hidden. ###
        #
        if elt.startswith("."):
            #
            continue

        #
        ### Filtering files. ###
        #
        if  os.path.isfile(eltpath) \
            and any([elt_low.endswith(ext) for ext in file_extensions_to_read]) \
            and not any([substring in elt_low for substring in keywords_to_skip]):

            #
            ### Filter is good, and this is a file, so we keep it. ###
            #
            filelist.append(eltpath)

            #
            continue

        #
        ### Filtering folders. ###
        #
        if  os.path.isdir(eltpath) \
            and not any([substring in elt_low for substring in keywords_to_skip]):

            #
            ### Filter is good, and this is a folder, so we will explore it later. ###
            #
            dirlist.append(eltpath + os.path.sep)

    #
    ### Reading the content of all the files that passed the filter. ###
    #
    for filepath in filelist:
        #
        txt = add_file(filepath=filepath, txt=txt)

    #
    ### Exploring recursively all the folders we kept. ###
    #
    if remaining_depth == -1 or remaining_depth > 0:
        #
        new_depth: int = -1 if remaining_depth == -1 else remaining_depth - 1
        #
        for dirpath in dirlist:
            #
            txt = explore_dir(dirpath=dirpath, txt=txt, remaining_depth=new_depth)

    #
    ### Returning the final text file. ###
    #
    return txt


#
### Main Entry Point. ###
#
def main() -> None:

    #
    ### Initialize parser. ###
    #
    parser: argparse.ArgumentParser = argparse.ArgumentParser()

    #
    ### Specify arguments. ###
    #
    parser.add_argument('-p', '--path', type=str, default='.', help='Path to where you want to start the recursive exploration.')
    #
    parser.add_argument('-o', '--output', type=str, default='.all_doc_together.txt', help='Path of the result file combining everything.')
    #
    parser.add_argument('-d', '--depth', type=int, default=-1, help='Maximum recursive depth to explore, else -1 means no limits.')

    #
    ### Get arguments parsed. ###
    #
    args: argparse.Namespace = parser.parse_args()

    #
    ### Initialize with an empty text file. ###
    #
    txt: str = ""

    #
    ### Start the recursive exploration. ###
    #
    txt = explore_dir(dirpath=args.path, txt=txt, remaining_depth=args.depth)

    #
    ### Write the output file. ###
    #
    try:

        #
        with open(args.output, "w", encoding="utf-8") as f:
            #
            f.write(txt)

    #
    except Exception as e:
        #
        print(f"Error: Could not write output file {args.output}. Error: {e}")


#
if __name__ == "__main__":
    #
    main()
