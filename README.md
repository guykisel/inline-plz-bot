# inline-plz-bot

Web service version of https://github.com/guykisel/inline-plz - lints your Pull Requests and comments inline on the diffs!

![Inline lint!](inline-plz-bot.png?raw=true =829x562)

# How do I use this?

1. Settings -> Webhooks -> Add Webhook
1. Payload URL: `https://inlineplz.herokuapp.com/`
1. Let me select individual events: select **Pull Request**

# Why do I want to use this?

If you use static analysis with your pull requests, you've probably gotten used to this workflow:

1. Run static analysis locally, fix issues
1. Push up a branch
1. Open a PR
1. Wait for the PR to pass in your CI tool
1. Get a little red X on your PR because you forgot to run one of the static analysis tools
1. Click on the little red X, crawl through console logs, and eventually find a cryptic message referencing a specific line in one of your files
1. Go back to your code, look up the right file and line, and then go back to the error message because you already forgot what it was

This bot gives you the static analysis output directly inlined in your PR diffs so you can understand failures more efficiently.

# How does it work?

1. This repo contains a simple little Flask server that listens for Github webhooks
1. When someone opens a pull request or pushes up some new commits, the repo's webhook POSTs to the Flask server
1. The Flask server reads the Github PR data (branch, sha, etc.), clones the repo, and shells out to inline-plz
1. inline-plz runs static analysis tools and uses the Github API to comment on the PR with any errors it finds

# This is cool, how can I contribute?

* Report bugs and feature requests!
    * Issues for the webservice/bot should go in this repo (inline-plz-bot)
    * Issues for the core functionality of inline-plz should go in https://github.com/guykisel/inline-plz
* Add support for more static analysis tools
* Add support for other code review tools besides just Github
* Add documentation
* Add unit tests
* Fix bugs
