# Who Knows About
Who Knows About is a simple script for Git Repos. Its goal is to provide a search feature that lets growing teams determine who is most knowledgeable for particular features or projects.

# How to use
Place the script anywhere in your repo and execute it however you may.<br/>
You'll be prompted to enter a search phrase.

# How it works
The entire commit log message is used and searched with the phrase entered.<br/>
A score is given to a developer if s/he has part of the phrase in the commit message.<br/>
Exponential decay is taken into account applied against how long ago the commit was made.<br/>
Commits within the past year will be given highest priority as the projection will be against e^(-5x).

# Future enhancements
Provide phrase proximity matching<br />
More data to crawl through than just commit messages (git blame?)
