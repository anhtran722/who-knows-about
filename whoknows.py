#!/usr/bin/env python
# -*- coding: utf-8 -*-

###
#
# Quick and dirty util to figure out who's worked on
# something and has knowledge of it. This util takes
# into account how long ago the person has worked on it
# and is based on their commit messages.
#
# @author: Anh Tran
# atran.wynd@gmail.com
#
###

from datetime import datetime
from dateutil.parser import parse
from heapq import nsmallest
from math import exp
from time import mktime
import json
import subprocess
import sys

# colors in console
GREEN = "\033[92m"
YELLOW = "\033[93m"
END = "\033[0m"

def color(s, color):
  return color + s + END if color else s

def whoKnowsAbout(thing, data):
  committers = {}

  # split message, since it could be a phrase
  thingList = thing.lower().split(" ")

  for commit in data:
    # author will contain name and email
    author = commit["author"]

    # grab date and turn it into a timestamp
    date = parse(commit["date"])
    timestamp = mktime(date.timetuple())

    # JSON returns message hyphen separated
    message = commit["message"].lower().split("-")

    # prioritize commits that were more recent
    increment = determineDecayFactor(timestamp)

    # keep track of the score and how many words matched
    score = 0

    if author not in committers:
      committers[author] = 0

    for word in thingList:
      if word in message:
        score += increment

    # use a multiplier for how much of phrase matched
    committers[author] += score

  # remove committers that have 0 score
  return cleanCommitters(committers)

###
# Use a max heap to determine the top `n` committers
###
def getMostRelevant(dict, topN):
  heap = [(-value, key) for key,value in dict.items()]
  nMax = nsmallest(topN, heap)
  nMax = [(key, -value) for value, key in nMax]
  return nMax

###
# Convert the timestamp so that it is on a scale as close to
# 0 -> 1 as possible. Use a year as a standard relevance timeframe.
# Then, apply an exponential decay model to figure out the proper
# score increment.
###
def determineDecayFactor(ts):
  year = 31556952000;
  proportional = (1 - (float(ts)/year))

  # https://en.wikipedia.org/wiki/Exponential_decay#/media/File:Plot-exponential-decay.svg
  return exp(-5*proportional)

###
# Parse out all the committers that received a 0 score :(
###
def cleanCommitters(committers):
  dict = {}
  for key, value in committers.items():
    if value != 0.0:
      dict[key] = value
  return dict

def getGitLog():
  p = subprocess.Popen("""git log --pretty=format:'{%n  "commit": "%H",%n  "author": "%an <%ae>",%n  "date": "%ad",%n  "message": "%f"%n},' $@ | perl -pe 'BEGIN{print "["}; END{print "]\n"}' | perl -pe 's/},]/}]/'""",
      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
  return p.communicate()[0]

###
# Print out the people relevant to the phrase
###
def printRelevance(relevance):
  if not relevance:
    print(color("Uh oh, you're on your own.\n", YELLOW))
    return

  print(color("Reach out to these people:\n", GREEN))
  for relevant in relevance:
    print(relevant[0] + ": " + str(round(relevant[1], 2)))
  print("\n")

if __name__ == "__main__":
  committers = whoKnowsAbout(" ".join(sys.argv[1:]), json.loads(getGitLog()))
  relevance = getMostRelevant(committers, 3)
  printRelevance(relevance)
  sys.exit(0)