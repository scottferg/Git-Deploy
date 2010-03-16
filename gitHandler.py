import git
import sys, os
import getopt
import time

try:
    repo = git.Repo(os.getcwd())
    cmd = git.Git(os.getcwd())
except git.errors.InvalidGitRepositoryError:
    print 'Error: Not a git repository'

fetch = lambda: cmd.execute('git fetch')
activeBranch = lambda: repo.active_branch

def findParentCommit(commit):
    '''
    Returns parents of a commit
    '''
    return repo.commit(commit).parents[0].id

def findCommitAuthor(commit): 
    '''
    Gets author of a commit
    '''
    return str(repo.commit(commit).author)

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

    try:
        return ['%s' % diff.a_path for diff in repo.commit(commit).diffs]
    except AttributeError:
        return []

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
        commitList = repo.commits(start = branch, max_count = 20)

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

    return result

def getCurrentRef():
    '''
    Returns the current ref which HEAD is pointed to
    '''
    return repo.active_branch

def prepareBranch():
    if repo.is_dirty: 
        cmd.execute('git stash')

    return

def restoreBranch():
    try:
        cmd.execute('git stash apply')
    except git.errors.GitCommandError:
        cleanBranch(True)

    return

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
    '''
    Resets a branch with unstaged changes
    '''
    if repo.is_dirty or force:
        cmd.execute('git reset --hard')

def checkoutBranch(branch):
    '''
    Checks out a new branch
    '''
    try:
        # head = open('.git/HEAD', 'w')
        # head.write('ref: refs/heads/%s' % branch)
        # head.close()
        cmd.execute('git checkout %s' % branch)
    except git.errors.GitCommandError:
        return False

    return

def getFileList(tag):
    '''
    Returns the file list of all changed files since the given tag
    '''
    result = []
    
    commitList = getCommitsSinceTag(tag)

    for commit in commitList:
        fileList = findChangedFiles(commit)

        # Don't add the same file twice
        for file in fileList:
            try:
                result.index(file)
            except ValueError:
                result.append(file)

    return result
    
def main():
    options, remainder = getopt.getopt(sys.argv[1:], 'c:t:', ['commit=','tag=']);

    for opt, arg in options:
        target = arg

        if (opt in ('-c', '--commit')):
            option = 'commit'
        if (opt in ('-t', '--tag')):
            option = 'tag'

    try:
        if not target or not option:
            raise UnboundLocalError

        if option == 'commit':
            print '\n'.join(['%s' % x for x in findChangedFiles(target)])
        elif option == 'tag':
            print '\n'.join(['%s' % x for x in getFileList(target)])
    except UnboundLocalError:
        print 'Usage: git_handler.py ([-c|--commit][-t|--tag]) <commit|tag>'
    except TypeError:
        print 'Commit not found'

if __name__ == '__main__':
    main()
