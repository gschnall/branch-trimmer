import time
import subprocess
import os

# Point to the correct git directory
currentDir = os.getcwd()
os.chdir(currentDir)

envState = {
  "number_of_branches_trimmed": 0,
  "number_of_branches_spared": 0,
  "isLocal": True,
  "git_get_branches": [],
  "git_delete_branch": [],
  "allBranches": [],
  "userBranches": [],
  "userFilter": ""
}

def top():
  subprocess.call(['clear'])
  subprocess.call(['figlet', "-f", "small", "Git Branch Trimmer"])
  print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
  print "\n"

def sheep(s):
  top()
  subprocess.call(['cowsay', "-f", "sheep", s])

def intro():
  sheep("Would you like to trim your remote or local branches?")

  user_response = raw_input("Enter r (remote) or l (local) >> ")
  envState["isLocal"] = False if (user_response == "r" or user_response == "remote") else True
  envState["git_get_branches"] = ["git", "branch", "-r"] if (user_response == "r" or user_response == "remote") else ["git", "branch"]
  envState["git_delete_branch"] = ["git", "push", "origin", '--delete'] if (user_response == "r" or user_response == "remote") else ["git", "branch", "--delete"]

  if (not envState["isLocal"]):
    sheep("Fetching Remote Branches...")
    print "-------- Output --------\n"
    subprocess.call(['git', 'fetch', '-p'])
    time.sleep(2)

  branchOutput = subprocess.check_output(envState["git_get_branches"])

  sheep("Would you like to filter the branches? Hit ENTER to skip this part.")
  keyword = raw_input("Enter keyword to filter by    >> ")
  envState["userFilter"] = False if keyword == "" else keyword

  envState["allBranches"] = branchOutput.split()

  filteredBranches = envState["allBranches"] if (keyword == "") else filter(lambda s: s.find(keyword) > -1, envState["allBranches"])
  # -- Map list of remote branches -- No need to do this for local
  envState["userBranches"] = filteredBranches if envState["isLocal"] else map(lambda s: s.split("origin/")[1], filteredBranches)

  sheep("I found " + str(len(envState["userBranches"])) + " branches" + ". It's Time for a Trim!")
  time.sleep(2)

def outro():
  sheep("You have trimmed " + str(envState["number_of_branches_trimmed"]) + " branches");

def printBranchStats():
  print "Branches Left    : " + str((len(envState["userBranches"]) - envState["number_of_branches_trimmed"]) - envState["number_of_branches_spared"])
  print "Branches Trimmed : " + str(envState["number_of_branches_trimmed"])
  print "Branches Spared  : " + str(envState["number_of_branches_spared"])
  print "\n"

def trimBranches():
  for branch in envState["userBranches"]:
    if (branch == "master" or branch == "*"):
      continue;

    top()
    printBranchStats()

    subprocess.call(['cowsay', "-f", "sheep", "Branch: " + branch])
    user_response = raw_input("Delete this branch? (y | n) >> ")

    if (user_response.lower() == "q" or user_response.lower() == "quit"):
      break

    if (user_response.lower() == "y" or user_response.lower() == "yes"):
      print "-------- Output --------\n"
      subprocess.call(envState["git_delete_branch"] + [branch])

      if (envState["isLocal"]):
        branchOutput = subprocess.check_output(envState["git_get_branches"])
        leftOverBranch = filter(lambda b: b == branch, branchOutput.split())
        if (len(leftOverBranch) > 0):
          sheep("{} has not been fully merged yet. You can force delete it...".format(branch))
          forceDelete = raw_input("Force delete branch? (y | n) >> ")
          if (forceDelete == "y" or forceDelete == "yes"):
            print "-------- Output --------\n"
            subprocess.call(["git", "branch", "-D", branch])
            envState["number_of_branches_trimmed"] = envState["number_of_branches_trimmed"] + 1
            time.sleep(2)
      else:
        envState["number_of_branches_trimmed"] = envState["number_of_branches_trimmed"] + 1
        time.sleep(2)

    else:
      envState["number_of_branches_spared"] = envState["number_of_branches_spared"] + 1
      continue

def main():
  top()
  intro()
  trimBranches()
  outro()

main()