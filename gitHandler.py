import git
import sys, os
import getopt

findParentCommit = lambda x: x.data[53:93]

repo = git.Repo(os.getcwd())

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
        blob = repo.blob(commit)
        diff = repo.diff(repo.commit(commit), repo.commit(findParentCommit(blob)))
    except git.errors.GitCommandError:
        print 'Error: Not a git repository'
        return

	return parseFileList(diff)

def getCommitMessage(commit):
    '''Finds the commit message for the specified commit'''
    try:
        return repo.commit(commit).message
    except git.errors.GitCommandError:
        print 'Error: Commit not found'
        return False
    
def main():
    options, remainder = getopt.getopt(sys.argv[1:], 'c:', 'commit=');

    for opt, arg in options:
        if (opt in ('-c', '--commit')):
            commit = arg

    try:
    	print "\n".join(["%s" % x for x in findChangedFiles(commit)])
        print "\n" + getCommitMessage(commit)
    except UnboundLocalError:
        print 'Usage: git_handler.py [-c|--commit] <commit>'
    except TypeError:
        print 'Commit not found'

if __name__ == '__main__':
    main()
