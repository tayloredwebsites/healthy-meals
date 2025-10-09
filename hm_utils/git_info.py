'''utils/git_info.py

methods to exract and store information about a git repository such as status, remotes, etc.
'''

from typing import Final, Tuple

import git # https://gitpython.readthedocs.io/en/stable/index.html

import logging
logger = logging.getLogger(__name__)

class GitInfo:
    '''Class to retrieve, store, and validate the git repo being used.

    We are using a class to provides a single place to find and store git repo information (DRY).
    - DRY (Don't Repeat Yourself) to simplify coding, reduce bugs, simplify testing.

    Validations include:
    - Confirm this repo was created as a clone of a fork of a particular github repo:
        - has an 'origin' remote that points to (upstream_repo_url).
    - Confirm that there is an 'upstream' remote pointing to the upstream_git.
    - Help validate the 'origin' tracking/upstream of the current local branch.
      - note: new branches cannot have a tracking/upstream branch until pushed to 'origin'
    - Help ensure that pushes will go to an 'origin' branch that will be good for a pull request to an 'upstream' branch.
    - Check for matching commits and pull request between local and 'origin' branch.
      - Philosophy:  Maintain a clean linear history, so history and pull requests are kept separate
        - Use git pull --rebase always on local branches.  When in doubt do 'git pull --rebase upstream main'
        - The standard merge of pull requests are linear, because the local repo has history separated from new code

    .. ToDo::
        GitInfo class consider/research annotated tag messages to help ensure commits go to appropriate pull requests
            - see: https://git-scm.com/docs/git-tag
            - see: https://github.com/gitpython-developers/GitPython/blob/main/git/refs/tag.py
        GitInfo class enhancements:
            - enable fetching remotes when it can handle password protected ssh keys
            - detect when remotes need to be fetched, and ask user to do a 'git fetch --prune'
            - add --prune to fetch, to remove obsolete branches, (...?)
        GitInfo DRY refactor:
            - define a function in GitInfo to replace the 4 blocks of code that
                get pull request and later commits from the remote branches

    using GitPython (git.Repo)

    Attributes:
        repo: the local git repo.
        upstream_git: the git connection string that points to the original repo that was forked.
        upstream_repo_url: the url for the original repo that was forked.
        unique_hexsha: hexsha in main branch that must exist in the repo (to ensure we have the same repo)

    Note:
        - this class makes no updates to the repo, so you need not worry about bad code ruining your repo.
        - this class depends upon having an up to date and pruned fetch (using git on your terminal).
          - in the root of your repo, please run the following console command:
            git fetch --prune

    Example::
        # get repo at current directory
        repo_info = GitInfo(git.Repo(.))
        # to get the number of files that have been updated
        #  i.e. the number modified files, untracked changed files, and staged files
        num_updates: int = repo_info.get_num_updates()
    '''
    repo: Final[git.Repo | None]

    err_strs: Tuple[str] # tuple of errors from initialization
    cur_branch: Final[str | None] # curent branch in repo

    num_mods: Final[int | None] # number of modifications in this branch
    num_untracked: Final[int | None] # number of untracked changes
    num_staged: Final[int | None] # number of staged changes in this branch
    num_updates: Final[int | None] # number of all updates in this branch

    local_commit_sha: Final[str | None] # latest local commit message in this branch
    local_commits_after_pr: Tuple[str] # latest local commit message in this branch
    local_pr_sha: Final[str | None] # most recent local pull request message in this branch

    remote_names: Tuple[str] # Tuple of remote repos
    up_git: Final[str | None] # url of 'upstream' repo
    origin_branches: Tuple[str] # branches in the 'origin' remote
    up_branches: Tuple[str] # branches in the 'upstream' remote

    origin_main_commit_sha: Final[str | None] # latest 'origin' commit hexsha in 'main' branch
    origin_main_commits_after_pr: Tuple[str] # commit hexshas since pull request in 'origin/main' branch
    origin_main_pr_sha: Final[str | None] # most recent 'origin' pull request hexsha in 'main' branch

    origin_starter_commit_sha: Final[str | None] # latest 'origin' commit hexsha in 'starter' branch
    origin_starter_commits_after_pr: Tuple[str] # commit hexshas since pull request in 'origin/starter' branch
    origin_starter_pr_sha: Final[str | None] # most recent 'origin' pull request hexsha in 'starter' branch

    up_main_commit_sha: Final[str | None] # latest 'upstream' commit hexsha in 'main' branch
    up_main_commits_after_pr: Tuple[str] # commit hexshas since pull request in 'upstream/main' branch
    up_main_pr_sha: Final[str | None] # most recent 'upstream' pull request hexsha in 'main' branch

    up_starter_commit_sha: Final[str | None] # latest 'upstream' commit hexsha in 'starter' branch
    up_starter_commits_after_pr: Tuple[str] # commit hexshas since pull request in 'upstream/starter' branch
    up_starter_pr_sha: Final[str | None] # most recent 'upstream' pull request hexsha in 'main' starter

    def __init__(cls, repo, upstream_git, upstream_repo_url, unique_hexsha):
        '''Create the GitInfo class with an existing GitPython git.Repo'''

        cls.repo = repo
        cls.up_git = upstream_git # git connection string to clone code or connect to remote
        cls.up_repo_url = upstream_repo_url # https url to github repo

        logger.debug(f'unique_hexsha: {unique_hexsha}')
        if len(unique_hexsha) == 0:
            logger.info('empty unique_hexsha, must be an empty repo')
            num_commits = len(repo.iter_commits())
            logger.debug(f'number of local commits: {num_commits}')
            if num_commits != 0:
                msg = 'repo has commits, but no unique_hexsha was given'
                tmp_err_strs.append(msg)
                logger.error(msg)
        elif len(unique_hexsha) != 40:
            msg = 'unique_hexsha length must be 40 characters'
            tmp_err_strs.append(msg)
            logger.error(msg)
        else:
            logger.debug(f'repo.commit(unique_hexsha[:6]).hexsha: {repo.commit(unique_hexsha[:6]).hexsha}')
            logger.debug(f'repo.commit(unique_hexsha).hexsha: {repo.commit(unique_hexsha).hexsha}')
            if repo.commit(unique_hexsha).hexsha != unique_hexsha:
                msg = f'commit with the unique_hexsha {unique_hexsha} is not found in this repo.'
                tmp_err_strs.append(msg)
                logger.error(msg)

        tmp_err_strs: list[str] = []
        tmp_local_commits_after_pr: list[str] = []
        tmp_origin_main_commits_after_pr: list[str] = []
        tmp_up_main_commits_after_pr: list[str] = []
        tmp_origin_starter_commits_after_pr: list[str] = []
        tmp_up_starter_commits_after_pr: list[str] = []

        try:
            cls.cur_branch = repo.head.ref.name
            logger.debug(f'cur_branch: {cls.cur_branch}')
        except Exception as ex:
            msg = f'{repr(ex)} on cur_branch'
            tmp_err_strs.append(msg)
            logger.error(msg)

        try:
            cls.num_mods = len(repo.git.diff(None))
            logger.debug(f'num_mods: {cls.num_mods}')
        except Exception as ex:
            msg = f'{repr(ex)} on num_mods'
            tmp_err_strs.append(msg)
            logger.error(msg)

        try:
            cls.num_untracked = len(repo.untracked_files)
            logger.debug(f'num_untracked: {cls.num_untracked}')
        except Exception as ex:
            msg = f'{repr(ex)} on num_untracked'
            tmp_err_strs.append(msg)
            logger.error(msg)

        try:
            cls.num_staged = len(repo.index.diff("HEAD"))
            logger.debug(f'num_staged: {cls.num_staged}')
        except Exception as ex:
            msg = f'{repr(ex)} on num_staged'
            tmp_err_strs.append(msg)
            logger.error(msg)

        try:
            cls.num_updates = cls.num_mods + cls.num_untracked + cls.num_staged
            logger.debug(f'num_updates: {cls.num_updates}')
        except Exception as ex:
            msg = f'{repr(ex)} on num_updates'
            tmp_err_strs.append(msg)
            logger.error(msg)

        try:
            cls.local_commit_sha = repo.head.commit.hexsha
            logger.debug(f'local_commit_sha: {cls.local_commit_sha}')
        except Exception as ex:
            msg = f'{repr(ex)} on latest_commit_msg'
            tmp_err_strs.append(msg)
            logger.error(msg)

        # initialize local_pr_sha and local_commits_after_pr
        try:
            for commit in repo.iter_commits():
                logger.debug(f'commit: {commit.hexsha}: {commit.message}')
                if commit.message.startswith("Merge pull request #"):
                    cls.local_pr_sha = commit.hexsha
                    logger.debug(f'local_pr_sha: {cls.local_pr_sha}')
                    break
                else:
                    tmp_local_commits_after_pr.append(commit.hexsha)
                    logger.debug(f'appended tmp_local_commits_after_pr: {commit.hexsha}')
        except Exception as ex:
            msg = f'{repr(ex)} on initialize local_pr_sha and tmp_local_commits_after_pr'
            tmp_err_strs.append(msg)
            logger.error(msg)

        # get the list of remotes
        try:
            cls.remote_names = list(map(lambda r: r.name, repo.remotes))
            logger.debug(f'remote names: {cls.remote_names}')
        except Exception as ex:
            msg = f'{repr(ex)} on remote_names'
            tmp_err_strs.append(msg)
            logger.error(msg)

        # check: make sure that 'origin' remote has been defined
        if 'origin' not in cls.remote_names:
            msg = "remotes do not have a remote named 'origin' configured"
            tmp_err_strs.append(msg)
            logger.error(msg)
        else:
            # get the git connection string of the 'origin' remote
            try:
                cls.origin_git = repo.remotes.origin.url
                logger.debug(f'origin_git: {cls.origin_git}')
                # confirm we have the main branch on the origin url
            except Exception as ex:
                msg = f'{repr(ex)} on up_git'
                tmp_err_strs.append(msg)
                logger.error(msg)
            cls.origin_branches = list(map(lambda b: b.name, repo.remotes.origin.refs))
        logger.debug(f'branches on origin remote: {cls.origin_branches}')

        # check: make sure that 'upstream' remote has been defined
        if 'upstream' not in cls.remote_names:
            msg = 'remotes do not have an upstream configured'
            tmp_err_strs.append(msg)
            logger.error(msg)
        else:
            # get the URL of the 'upstream' remote
            try:
                cls.up_git = repo.remotes.upstream.url
                logger.debug(f'up_git: {cls.up_git}')
                # confirm we have the main branch on the upstream url
            except Exception as ex:
                msg = f'{repr(ex)} on up_git'
                tmp_err_strs.append(msg)
                logger.error(msg)
            cls.up_branches = list(map(lambda b: b.name, repo.remotes.upstream.refs))
        logger.debug(f'branches on upstream remote: {cls.up_branches}')


        ''' fetch 'origin' and 'upstream' remotes

        see todo above for GitInfo class enhancements:
        - enable fetching remotes when it can handle password protected ssh keys
        - detect when remotes need to be fetched, and ask user to do a 'git fetch --prune'
        - add --prune to fetch, to remove obsolete branches, (...?)

        for remote in repo.remotes
            if remote.name in ['origin', 'upstream']
                try:
                    remote.fetch()
                except: Exception as ex:
                    tmp_err_strs.append(f'{repr(ex)} on remote.fetch on {remote.name}')
                    logger.error(f'{repr(ex)} on remote.fetch on {remote.name}')
        '''

        # get pull request and later commits from the remote branch: origin/main
        if 'origin' in cls.remote_names and 'origin/main' in cls.origin_branches:
            # Get origin/main commits
            try:
                cls.origin_main_commit_sha = repo.remotes.origin.refs.main.commit.hexsha
                logger.debug(f'origin_main_commit_sha: {cls.origin_main_commit_sha}')
            except Exception as ex:
                msg = f'{repr(ex)} on origin_main_commit_msg'
                tmp_err_strs.append(msg)
                logger.error(msg)

            #  initialize origin_main_pr_sha and origin_main_commits_after_pr
            try:
                remote_commit = repo.remotes.origin.refs.main.commit
                for commit in remote_commit.iter_items(remote_commit.repo, 'origin/main'):
                    logger.debug(f'origin/main commit: {commit.hexsha}: {commit.message}')
                    if commit.message.startswith("Merge pull request #"):
                        cls.origin_main_pr_sha = commit.hexsha
                        logger.debug(f'origin_main_pr_sha: {cls.origin_main_pr_sha}')
                        break
                    else:
                        tmp_origin_main_commits_after_pr.append(commit.hexsha)
                        logger.debug(f'appended tmp_origin_main_commits_after_pr: {commit.hexsha}')
            except Exception as ex:
                msg = f'{repr(ex)} on initialize origin_main_pr_sha and tmp_origin_main_commits_after_pr'
                tmp_err_strs.append(msg)
                logger.error(msg)
        else:
            msg = f'''System Error!!! - You are missing your origin/main branch!!!!
            Did you create this repo doing a git clone of your fork of {cls.up_repo_url} ?
            To Do this,
                1) go to {cls.up_repo_url}
                2) click the fork button (upper right below top navigation)
                3) unclick the 'copy the main branch only' checkbox
                4) click Create fork button
                6) from your forked copy, get the git connection string by:
                    6a) click the green Code button on the upper right
                    6b) click the copyToClipboard icon next to the SSH (or other if you prefer) clone git connection string
                5) in the console of your computer
                    5a) navigate to the directory where you keep github cloned repos
                    5b) run the following command (note <paste> is where to past the git connection string)
                        git clone <paste>
                    5c) cd into the newly created directory
                    5d) add the upstream remote with the following command:
                        git remote add {cls.up_git}
                    5e) refresh all remotes and their branches with the following command:
                        git fetch --all --prune
            '''
            tmp_err_strs.append(msg)
            logger.error(msg)

        # # get pull request and later commits from the remote branch: origin/starter
        # if 'origin' in cls.remote_names and 'starter' in cls.origin_branches:
        #     # Get origin/starter commits
        #     try:
        #         cls.origin_starter_commit_sha = repo.remotes.origin.refs.starter.commit.hexsha
        #         logger.debug(f'origin_starter_commit_sha: {cls.origin_starter_commit_sha}')
        #     except Exception as ex:
        #         tmp_err_strs.append(f'{repr(ex)} on origin_starter_commit_sha')
        #         logger.error(f'{repr(ex)} on origin_starter_commit_sha')

        #     #  initialize origin_starter_pr_sha and origin_starter_commits_after_pr
        #     try:
        #         remote_commit = repo.remotes.origin.refs.starter.commit
        #         for commit in remote_commit.iter_items(remote_commit.repo, 'origin/starter'):
        #             logger.debug(f'origin/main commit: {commit.hexsha}: {commit.message}')
        #             if commit.message.startswith("Merge pull request #"):
        #                 cls.up_main_pr_sha = commit.hexsha
        #                 logger.debug(f'origin_starter_pr_sha: {cls.origin_starter_pr_sha}')
        #                 break
        #             else:
        #                 tmp_origin_starter_commits_after_pr.append(commit.hexsha)
        #                 logger.debug(f'appended tmp_origin_starter_commits_after_pr: {commit.hexsha}')
        #     except Exception as ex:
        #         tmp_err_strs.append(f'{repr(ex)} on initialize origin_starter_pr_sha and tmp_origin_starter_commits_after_pr')
        #         logger.error(f'{repr(ex)} on initialize origin_starter_pr_sha and tmp_origin_starter_commits_after_pr')
        # else
        #     msg = f'''You are missing your origin/starter branch.
        #     you will not be able to make changes to the web app starter branch of this repo unless you:
        #         fetch the starter branch.  To do this, in the root of the website, enter the console command:
        #             git fetch --prune
        #     '''
        #     tmp_err_strs.append(msg)
        #     logger.warning(msg)

        # # get pull request and later commits from the remote branch: upstream/main
        if 'upstream' not in cls.remote_names:
            msg = f'''You are missing your upstream remote
            Please enter the following console command in the website rood directory:
                git remote add upstream {cls.up_git}
            When done, please also do a clean fetch of all of your remotes and their branches:
                git fetch --all --prune
            Then please try again.
            '''
            tmp_err_strs.append(msg)
            logger.error(msg)
        else:
            if 'upstream/main' in cls.up_branches:
                # Get upstream/main commits
                try:
                    cls.up_main_commit_sha = repo.remotes.upstream.refs.main.commit.hexsha
                    logger.debug(f'up_main_commit_sha: {cls.up_main_commit_sha}')
                except Exception as ex:
                    tmp_err_strs.append(f'{repr(ex)} on up_main_commit_sha')
                    logger.error(f'{repr(ex)} on up_main_commit_sha')

                #  initialize upstream_main_pr_sha and upstream_main_commits_after_pr
                try:
                    remote_commit = repo.remotes.upstream.refs.main.commit
                    for commit in remote_commit.iter_items(remote_commit.repo, 'upstream/main'):
                        logger.debug(f'upstream/main commit: {commit.hexsha}: {commit.message}')
                        if commit.message.startswith("Merge pull request #"):
                            cls.up_main_pr_sha = commit.hexsha
                            logger.debug(f'upstream_main_pr_sha: {cls.up_main_pr_sha}')
                            break
                        else:
                            tmp_up_main_commits_after_pr.append(commit.hexsha)
                            logger.debug(f'appended tmp_up_main_commits_after_pr: {commit.hexsha}')
                except Exception as ex:
                    tmp_err_strs.append(f'{repr(ex)} on initialize up_main_pr_sha and tmp_up_main_commits_after_pr')
                    logger.error(f'{repr(ex)} on initialize up_main_pr_sha and tmp_up_main_commits_after_pr')
            else:
                msg = f'''System Error!!! - You are missing your upstream/main branch!!!!
                Did you create this repo doing a git clone of your fork of {cls.up_git} ???
                '''
                tmp_err_strs.append(msg)
                logger.error(msg)

        # # get pull request and later commits from the remote branch: upstream/starter
        # if 'upstream' in cls.remote_names and 'starter' in cls.origin_branches:
        #     # Get upstream/starter commits
        #     try:
        #         cls.up_starter_commit_sha = repo.remotes.upstream.refs.starter.commit.hexsha
        #         logger.debug(f'up_starter_commit_sha: {cls.up_starter_commit_sha}')
        #     except Exception as ex:
        #         tmp_err_strs.append(f'{repr(ex)} on up_starter_commit_sha')
        #         logger.error(f'{repr(ex)} on up_starter_commit_sha')

        #     #  initialize up_starter_pr_sha and up_starter_commits_after_pr
        #     try:
        #         remote_commit = repo.remotes.upstream.refs.starter.commit
        #         for commit in remote_commit.iter_items(remote_commit.repo, 'upstream/starter'):
        #             logger.debug(f'origin/main commit: {commit.hexsha}: {commit.message}')
        #             if commit.message.startswith("Merge pull request #"):
        #                 cls.up_starter_pr_sha = commit.hexsha
        #                 logger.debug(f'up_starter_pr_sha: {cls.up_starter_pr_sha}')
        #                 break
        #             else:
        #                 tmp_up_main_commits_after_pr.append(commit.hexsha)
        #                 logger.debug(f'appended tmp_up_main_commits_after_pr: {commit.hexsha}')
        #     except Exception as ex:
        #         tmp_err_strs.append(f'{repr(ex)} on initialize up_starter_pr_sha and tmp_up_main_commits_after_pr')
        #         logger.error(f'{repr(ex)} on initialize up_starter_pr_sha and tmp_up_main_commits_after_pr')
        # else
        #     msg = f'''You are missing your upstream/starter branch.
        #     you will not be able to make changes to the web app starter branch of this repo unless you:
        #         fetch the starter branch.  To do this, in the root of the website, enter the console command:
        #             git fetch --prune
        #     '''
        #     tmp_err_strs.append(msg)
        #     logger.warning(msg)


        # set Final[Tuple[str]] values from temporary string lists
        cls.err_strs = tuple(tmp_err_strs)
        cls.local_commits_after_pr = tuple(tmp_local_commits_after_pr)
        cls.origin_main_commits_after_pr = tuple(tmp_origin_main_commits_after_pr)
        cls.origin_starter_commits_after_pr = tuple(tmp_origin_starter_commits_after_pr)
        cls.up_main_commits_after_pr = tuple(tmp_up_main_commits_after_pr)
        cls.up_starter_commits_after_pr = tuple(tmp_up_starter_commits_after_pr)


    def get_num_updates():
        pass

    def is_ready_for_pr():
        pass

    def is_ready_for_commit():
        pass

    def is_ready_for_new_work():
        pass

    def junk():

        # sanity check: the first iter_commits is the same as head.commit.hexsha
        if tmp_local_commits_after_pr[0] != cls.local_commit_sha:
            tmp_err_strs.append(f'first commit sha mismatch: {tmp_local_commits_after_pr[0]} != {cls.local_commit_sha}')
            logger.error(f'first commit sha mismatch: {tmp_local_commits_after_pr[0]} != {cls.local_commit_sha}')


        # make sure that upstream remote points to tws/hm
        if 'upstream' not in cls.remote_names:
            tmp_err_strs.append(f"""You are missing your 'upstream' remote.  The following console command should fix it:
                git remote add upstream git@github.com:tayloredwebsites/healthy-meals.git
            """)
        else:
            if repo.remotes.upstream.url != 'git@github.com:tayloredwebsites/healthy-meals.git':
                tmp_err_strs.append(f"""Your 'upstream' remote is not pointing to 'git@github.com:tayloredwebsites/healthy-meals.git'
                It is currently pointing to: '{upstream_url}'
                The following console commands should fix it:
                    git remote remove upstream
                    git remote add upstream git@github.com:tayloredwebsites/healthy-meals.git
                """)

            logger.debug(f'last commit on main branch:\n{remote_commit_msg}')
            latest_commit_msg
            cls.local_cur_branch
            '''make sure that we have the last pr in upstream main in our current branch:
            compare strings of commit messages from beginning to from(if it exists - should if from pr)
            use for commit in repo.iter_commits to get commits
            break on match of text up to # in Merge pull request #23 from
            fail if not correct pr id -> tell user to do git pull --rebase upstream main
            '''

        # is the last pull request commit matching the last pull request on upstream (tws/hm)
        # - else a git pull --rebase upstream main is required
        # - also confirm at least one commmit in history matches

        # make sure that goodToGo runs successfully

        # if making changes to main or starter branches
        # - if number of commits since last tws/hm  pull request is 0
        #   - then instruct to do a checkout -b (or switch?)
        # - else get a branch with lastst commits
        #   - Instructions to make a headless branch, name it, then check it.
        #   - will not be able to do a pull on main/starter branch till the commits it has are incorporated or removed.

        # make sure
