Stages
1. add premium downloader to package with new Submission() and Document() classes.
2. colab fix for nest asyncio (similar to jupyter)
3. cleanup module organization + remove bulk data downloads (SEC Library is much faster + up to date). keep an eye on initial
load time
4. Use lessons learned from premium downloader to make downloader better / rework Filing.

Prepare for next stage where we write generalized parsers and use sec library to parse almost every form and attachment type