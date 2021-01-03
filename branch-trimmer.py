#!/usr/bin/env python
from __future__ import print_function
from signal import signal, SIGINT
from sys import exit
import time
import subprocess
import os
import argparse

# Point to the correct git directory
currentDir = os.getcwd()
os.chdir(currentDir)
# Args
parser = argparse.ArgumentParser()
parser.add_argument("-master", "--master", dest = "master", default = "master", help="The master branch | default = master")
parser.add_argument("-trim", "--trim", dest = "trim", default = "auto", help="local, remote, or auto | default = auto")
parser.add_argument("-filter", "--filter", dest = "filter", default = " ", help="string to filter branches by | empty string \"\" for no filter | default = \" \" -> space is auto")
args = parser.parse_args()

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

def sheep(s, run_top):
  if (run_top):
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
  outro("Exiting...\n\n")
  exit(0)

def intro():
  # sheep("Would you like to trim your remote or local branches?", True)

  # - Currently only supports removal of local branches
  user_response = "l"

  # if (args.trim == "local"):
    # user_response = "l"
  # elif (args.trim == "remote"):
    # user_response = "r"
  # else:
    # user_response = raw_input("Trim remote or local? [r|l] >> ")

  envState["isLocal"] = False if (user_response == "r" or user_response == "remote") else True
  envState["git_get_branches"] = ["git", "branch", "-r"] if (user_response == "r" or user_response == "remote") else ["git", "branch"]
  envState["git_delete_branch"] = ["git", "push", "origin", '--delete'] if (user_response == "r" or user_response == "remote") else ["git", "branch", "--delete"]

  if (not envState["isLocal"]):
    sheep("Fetching Remote Branches...", True)
    print("-------- Output --------\n")
    subprocess.call(['git', 'fetch', '-p'])
    time.sleep(2)

  branchOutput = subprocess.check_output(envState["git_get_branches"])

  if (args.filter == " "):
    sheep("Would you like to filter the branches?\n -ENTER to skip this", True)
    keyword = raw_input("Keyword to filter by >> ")
  else:
    keyword = args.filter

  envState["userFilter"] = False if keyword == "" else keyword
  envState["allBranches"] = branchOutput.split()

  filteredBranches = envState["allBranches"] if (keyword == "") else filter(lambda s: s.find(keyword) > -1, envState["allBranches"])
  # -- Map list of remote branches -- No need to do this for local
  envState["userBranches"] = filteredBranches if envState["isLocal"] else map(lambda s: s.split("origin/")[1], filteredBranches)

  sheep("I found " + str(len(envState["userBranches"])) + " branches" + ". It's Time for a Trim!", True)
  time.sleep(2)

def outro(text):
  numbBranchesTrimmed = envState["number_of_branches_trimmed"]
  numbBranchesLeft = len(envState["allBranches"]) - (numbBranchesTrimmed + 2)
  # b = "branches" if numbBranchesTrimmed > 1 or numbBranchesTrimmed == 0 else "branch"
  subprocess.call(['clear'])
  sheep(text + "Results\n\n- Branches Trimmed: " + str(numbBranchesTrimmed) + "\n- Branches Existing: " + str(numbBranchesLeft), False)

def printBranchStats():
  if (envState["isLocal"]):
    print("> Local Branches\n")
  else:
    print("> Remote Branches\n")

  print("  Total # Branches : " + str(len(envState["allBranches"])-2))
  print("  Branches Trimmed : " + str(envState["number_of_branches_trimmed"]))
  print("  Branches To Trim : " + str((len(envState["userBranches"]) - envState["number_of_branches_trimmed"]) - envState["number_of_branches_spared"]-2))
  # print("Branches Spared  : " + str(envState["number_of_branches_spared"]))
  print("")

def trimBranches():
  currentBranch = subprocess.check_output(['git', 'branch', '--show-current']).strip()
  for branch in envState["userBranches"]:
    if (branch == args.master or branch == '*' or branch == currentBranch):
      continue

    top()

    printBranchStats()
    print("------------------------\n")
    print("> Current Branch\n\n  " + branch + "\n")
    user_response = raw_input("Delete branch? [y|n] >> ")

    if (user_response.lower() == "q" or user_response.lower() == "quit"):
      break

    if (user_response.lower() == "y" or user_response.lower() == "yes"):
      print("------ Output ------\n")
      subprocess.call(envState["git_delete_branch"] + [branch])

      if (envState["isLocal"]):
        branchOutput = subprocess.check_output(envState["git_get_branches"])
        leftOverBranch = filter(lambda b: b == branch, branchOutput.split())
        if (len(leftOverBranch) > 0):
          sheep("{} has not been fully merged yet.\n -You'll need force delete it".format(branch), True)
          subprocess.check_output(["git", "cherry", "-v", args.master, branch])
          forceDelete = raw_input("Force delete branch? [y|n]) >> ")
          while True:
            if (forceDelete == "y" or forceDelete == "yes"):
              print("------ Output ------\n")
              subprocess.call(["git", "branch", "-D", branch])
              envState["number_of_branches_trimmed"] += 1
              time.sleep(2)
              break
            elif (forceDelete == "v" or forceDelete == "view"):
              subprocess.call(["git", "cherry", "-v", args.master, branch])
              continue
            else:
              break
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
  outro("")

main()
