from git import Repo


def push_new_results(results_dir="results/"):
    """
    Push new results to the Git repository.
    
    This function checks for untracked files in the 'results/' directory,
    adds them to the repository, commits with a message, and pushes the changes.
    
    Returns:
        None
    """
    repo = Repo(".")
    origin = repo.remotes.origin

    # Check for untracked files in results/
    untracked = [f for f in repo.untracked_files if f.startswith(results_dir)]

    if not untracked:
        print("No new files in results/")
        return

    # Add and commit
    repo.index.add(untracked)
    msg = "Add new results"
    repo.index.commit(msg)

    # Push
    origin.push()
    print("Pushed:", msg)
