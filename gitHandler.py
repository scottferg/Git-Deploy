import git
import sys, os
import getopt
import time

try:
    repo = git.Repo(os.getcwd())
    cmd = git.Git(os.getcwd())
except git.errors.InvalidGitRepositoryError:
    print 'Error: Not a git repository'

<<<<<<< HEAD
def findParentCommit(commit):
    '''
    Returns parents of a commit
    '''
    return repo.commit(commit).parents[0].id
=======
def parseFileList(diff):
    '''
    Parses filenames out of a diff
    '''
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
>>>>>>> e47e1ca... Add command line option to display all commits since a particular tag

def findCommitAuthor(commit): 
    '''
    Gets author of a commit
    '''
    return str(repo.commit(commit).author)

<<<<<<< HEAD
def findCommitCommitter(commit): 
    '''
    Gets committer of a commit
    '''
    return str(repo.commit(commit).committer)

def findCommitAuthoredDate(commit):
    '''
    Gets commit authored date
    '''
    return time.strftime("%a, %d %b %Y %H:%M", repo.commit(commit).authored_date)
=======
def findChangedFiles(commit):
    '''
    Finds all of the affected files within a given commit
    '''
    try:
        blob = repo.blob(commit)
        diff = repo.diff(repo.commit(commit), repo.commit(findParentCommit(blob)))
    except git.errors.GitCommandError:
        print 'Error: Not a git repository'
        return
>>>>>>> e47e1ca... Add command line option to display all commits since a particular tag

def findCommitCommittedDate(commit): 
    '''
    Gets commit committed date
    '''
    return time.strftime("%a, %d %b %Y %H:%M", repo.commit(commit).committed_date)

def getCommitDiff(commit):
    '''
    Returns the diff for a specific commit
    '''
    return repo.diff(findParentCommit(commit),
                     repo.commit(commit))

def findChangedFiles(commit):
    '''
    Finds all of the affected files within a given commit
    '''
    return ['%s' % diff.a_path for diff in repo.commit(commit).diffs]

def getCommitMessage(commit):
    '''
    Finds the commit message for the specified commit
    '''
    try:
        commit = repo.commit(commit)

        return {'hash': commit.id,
                'author': commit.author,
                'date': time.strftime("%a, %d %b %Y %H:%M", commit.committed_date),
                'message': commit.message}
    except git.errors.GitCommandError:
        print 'Error: Commit not found'
        return False

def getBranch(branch):
    '''
    Returns all commits for the given branch
    '''
    try:
        commitList = repo.commits(start=branch, max_count=20)

        result = [commit.id for commit in commitList]
    except git.errors.GitCommandError:
        print 'Error: branch not found'
        return false

    return result

def getCommitsSinceTag(tag):
    '''
    Returns all commits since the given tag
    '''
    try:
        commitList = repo.commits_between(tag, 'HEAD')
        result = [commit.id for commit in commitList]
    except git.errors.GitCommandError:
        print 'Error: Commit not found'
        return False

<<<<<<< HEAD
    return result

def getCurrentRef():
    '''
    Returns the current ref which HEAD is pointed to
    '''
    return repo.active_branch

def cherryPickCommit(hash, noCommit = False):
    '''
    Cherry picks the specified commit
    '''
    try:
        cleanBranch()

        cmd.execute('git cherry-pick %s %s' % (noCommit and '-n' or '', hash))
    except git.errors.GitCommandError:
        return False

    return True

def cleanBranch(force = False):
    if repo.is_dirty or force:
        cmd.execute('git reset --hard')
=======
def getCommitsSinceTag(tag):
    '''
    Returns all commits since the given tag
    '''
    try:
        commitList = repo.commits_between(tag, 'HEAD')
        result = [commit.id for commit in commitList]
    except git.errors.GitCommandError:
        print 'Error: Commit not found'
        return False

    return result
>>>>>>> e47e1ca... Add command line option to display all commits since a particular tag
    
def main():
    options, remainder = getopt.getopt(sys.argv[1:], 'c:', 'commit=');

    for opt, arg in options:
        if (opt in ('-c', '--commit')):
            commit = arg

    try:
    	print "\n".join(["%s" % x for x in findChangedFiles(commit)])
    except UnboundLocalError:
        print 'Usage: git_handler.py ([-c|--commit][-t|--tag]) <commit|tag>'
    except TypeError:
        print 'Commit not found'

if __name__ == '__main__':
    main()
