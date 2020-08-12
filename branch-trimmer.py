from __future__ import print_function
from signal import signal, SIGINT
from sys import exit
import time
import subprocess
import os

# To Do:
#---------------------------------------------
#  - Display basic stats                      
#  -> printBranchStats                        
#  -> numb of branches left                   
#  -> numb of branches deleted                
#                                             
#  - Include better summary upon completion   
#  -> numb of branches spared                 
#                                             
#  - Show any new commits on branches         
#  -> let users view unmerged commits         
#  -> git cherry -v master escapist\'s        
#  -> maybe show snippet (first 2 - 3)        
#  --> then include a v option to view all    
#                                             
#  - Make flags for:                          
#  -> https://stackoverflow.com/questions/11604653/add-command-line-arguments-with-flags-in-python3                                    
#  -> changing default master branch          
#  -> auto selecting local or remote          
#---------------------------------------------

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
  print("________________________")
  print("|  Git Branch Trimmer  |")
  print("| ^^^^^^^^^^^^^^^^^^^^ |")
  print("| [  EXIT |> Ctrl-c  ] |")
  print("------------------------\n")

def sheep(s):
  top()
  print(s)
  print("""
   \\
       __
      UooU\.'@@@@@@`.
      \__/(@@@@@@@@@@)
           `YY~~~~YY'
            ||    ||
  """)

def exitHandler(signal_received, frame):
  subprocess.call(['clear'])
  print("Ctrl-c detected. Exiting...\n")
  outro()
  exit(0)

def intro():
  sheep("Would you like to trim your remote or local branches?")

  user_response = raw_input("Trim remote or local? [r|l] >> ")
  envState["isLocal"] = False if (user_response == "r" or user_response == "remote") else True
  envState["git_get_branches"] = ["git", "branch", "-r"] if (user_response == "r" or user_response == "remote") else ["git", "branch"]
  envState["git_delete_branch"] = ["git", "push", "origin", '--delete'] if (user_response == "r" or user_response == "remote") else ["git", "branch", "--delete"]

  if (not envState["isLocal"]):
    sheep("Fetching Remote Branches...")
    print("-------- Output --------\n")
    subprocess.call(['git', 'fetch', '-p'])
    time.sleep(2)

  branchOutput = subprocess.check_output(envState["git_get_branches"])

  sheep("Would you like to filter the branches?\n -ENTER to skip this")
  keyword = raw_input("Keyword to filter by >> ")
  envState["userFilter"] = False if keyword == "" else keyword

  envState["allBranches"] = branchOutput.split()

  filteredBranches = envState["allBranches"] if (keyword == "") else filter(lambda s: s.find(keyword) > -1, envState["allBranches"])
  # -- Map list of remote branches -- No need to do this for local
  envState["userBranches"] = filteredBranches if envState["isLocal"] else map(lambda s: s.split("origin/")[1], filteredBranches)

  sheep("I found " + str(len(envState["userBranches"])) + " branches" + ". It's Time for a Trim!")
  time.sleep(2)

def outro():
  numbBranchesTrimmed = envState["number_of_branches_trimmed"]
  b = "branches" if numbBranchesTrimmed > 1 or numbBranchesTrimmed == 0 else "branch"
  sheep("Results:\n\nYou have trimmed " + str(numbBranchesTrimmed) + " " + b)

def printBranchStats():
  print("Branches Left    : " + str((len(envState["userBranches"]) - envState["number_of_branches_trimmed"]) - envState["number_of_branches_spared"]))
  print("Branches Trimmed : " + str(envState["number_of_branches_trimmed"]))
  print("Branches Spared  : " + str(envState["number_of_branches_spared"]))
  print("\n")

def trimBranches():
  currentBranch = subprocess.check_output(['git', 'branch', '--show-current']).strip()
  for branch in envState["userBranches"]:
    if (branch == "master" or branch == '*' or branch == currentBranch):
      continue

    top()
    #printBranchStats()

    sheep("Branch: " + branch)
    user_response = raw_input("Delete this branch? [y|n] >> ")

    if (user_response.lower() == "q" or user_response.lower() == "quit"):
      break

    if (user_response.lower() == "y" or user_response.lower() == "yes"):
      print("------ Output ------\n")
      subprocess.call(envState["git_delete_branch"] + [branch])

      if (envState["isLocal"]):
        branchOutput = subprocess.check_output(envState["git_get_branches"])
        leftOverBranch = filter(lambda b: b == branch, branchOutput.split())
        if (len(leftOverBranch) > 0):
          sheep("{} has not been fully merged yet.\n -You'll need force delete it".format(branch))
          forceDelete = raw_input("Force delete branch? [y|n]) >> ")
          if (forceDelete == "y" or forceDelete == "yes"):
            print("------ Output ------\n")
            subprocess.call(["git", "branch", "-D", branch])
            envState["number_of_branches_trimmed"] += 1
            time.sleep(2)
        else:
          envState["number_of_branches_trimmed"] += 1
          time.sleep(2)
      else:
        envState["number_of_branches_trimmed"] += 1
        time.sleep(2)

    else:
      envState["number_of_branches_spared"] += 1
      continue

def main():
  signal(SIGINT, exitHandler)
  top()
  intro()
  trimBranches()
  outro()

main()
