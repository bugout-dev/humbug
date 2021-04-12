# humbug

Humbug helps you understand what keeps users coming back to your developer tool as well as any
friction they experience.

Humbug lets you collect basic system information and crash reports while respecting your users'
privacy. In addition to getting reports, you get to be [GDPR](https://gdpr-info.eu/)-compliant from
day one.

Humbug is currently available in the following programming languages and supproted types of errors:

1. [Python](./python)
- Error traceback report
- System information report
- Packages available in the current Python process report
- Python logging module report
- Environment variables report
- Custom report with full content control

2. [Go](./go)
- Panic report
- System infromtation report

3. [Javascript] (./javascript)
- Error traceback report
- System information report

If you would like support for another programming language, please
[create an issue](https://github.com/bugout-dev/humbug/issues/new).

---

## Using Humbug

### Trying it out

First, sign up for an account at https://bugout.dev.

Once you have created your account, go to the [`Account > Teams`](https://bugout.dev/account/teams)
page and create a team:

![Create a team](https://s3.amazonaws.com/static.simiotics.com/humbug-demo/create-a-team-0.png)

Once you have created a team, you should see something like this:

![Team created!](https://s3.amazonaws.com/static.simiotics.com/humbug-demo/create-a-team-1.png)

Click on the `Usage Reports` button on your new team to set up reporting:

![Set up usage reports](https://s3.amazonaws.com/static.simiotics.com/humbug-demo/usage-reports-0.png)

Enter a name for your project:

![Create project for usage reporting](https://s3.amazonaws.com/static.simiotics.com/humbug-demo/usage-reports-1.png)

This should result in a view like this one:

![Project created!](https://s3.amazonaws.com/static.simiotics.com/humbug-demo/usage-reports-2.png)

Now, create a new token that you can use for reporting:

![Create token](https://s3.amazonaws.com/static.simiotics.com/humbug-demo/usage-reports-3.png)

Which should get you to a view like this one:

![All set!](https://s3.amazonaws.com/static.simiotics.com/humbug-demo/usage-reports-4.png)

Make special note of the `Journal ID` and the `Token`. You will need them in the next step, where
you will instrument your application to register usage reports with Bugout.

Here are some examples of how to do this in:

1. [Python](./python/README.md#integration)

#### Using the demo journal and token

If you would like to try things out with the demo integration from above, just email
[me](mailto:neeraj@bugout.dev) ([zomglings](https://github.com/zomglings)) with your Bugout
username and I will add you to the demo team.
You can also reach me on the [Bugout.dev community slack](https://join.slack.com/t/bugout-dev/shared_invite/zt-fhepyt87-5XcJLy0iu702SO_hMFKNhQ).

#### From development to production

We recommend generating one token for development and testing and using different tokens for each
version of your production library or application.

### Accessing reports

You can access your Bugout knowledge base at https://bugout.dev, via the Bugout API, or using the
`bugout` command line tool.

Bugout client libraries:

1. [Python](https://pypi.org/project/bugout/)
2. [Go](https://github.com/bugout-dev/bugout-go)
3. [Javascript](https://github.com/bugout-dev/bugout-js)

The `bugout` command line tool can be installed from:
https://github.com/bugout-dev/bugout-go/releases/latest

You can use [`humbug.bash`](https://gist.github.com/zomglings/a82ea32e8533afe62278bb2056e95621)
to download your Humbug reports to your filesystem in an easy to analyze JSON format.

### Getting help

You can get help by:

1. [Creating an issue](https://github.com/bugout-dev/humbug/issues/new)
2. [Asking for help on the Bugout.dev community Slack](https://join.slack.com/t/bugout-dev/shared_invite/zt-fhepyt87-5XcJLy0iu702SO_hMFKNhQ)
3. [Emailing zomglings](mailto:neeraj@bugout.dev)
4. [Scheduling a meeting with zomglings](https://calendly.com/neeraj-simiotics/bugout-30)
