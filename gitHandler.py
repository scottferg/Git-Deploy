import git
import sys, os
import getopt

findParentCommit = lambda x: x.data[53:93]

def parseFileList(diff):
    '''Parses filenames out of a diff'''
    result = []

    while True:
        try:
            index = diff.index('---')
            # Arbitrary offset of 67 characters to pull out just the filename from the 
            # string. Add it to the result.
            result.append(diff[index:index + 67].split(' ')[1].split('a/')[1].split('\n')[0])
            # Remove the first occurrence of '---' so we can loop back and do it
            # again
            diff = diff.replace('---', '+++', 1)
        except ValueError:
            break

    return result

def findChangedFiles(commit):
    '''Finds all of the affected files within a given commit'''
    try:
        repo = git.Repo(os.getcwd())
        blob = repo.blob(commit)
        diff = repo.diff(repo.commit(commit), repo.commit(findParentCommit(blob)))
    except git.errors.GitCommandError:
        print 'Error: Not a git repository'
        return

	return parseFileList(diff)

def main():
    options, remainder = getopt.getopt(sys.argv[1:], 'c:', 'commit=');

    for opt, arg in options:
        if (opt in ('-c', '--commit')):
            commit = arg

    try:
    	print "\n".join(["%s" % x for x in findChangedFiles(commit)])
    except UnboundLocalError:
        print 'Usage: git_handler.py [-c|--commit] <commit>'

if __name__ == '__main__':
    main()
