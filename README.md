# humbug

Humbug helps you understand what keeps users coming back to your developer tool as well as any
friction they experience.

Humbug lets you collect basic system information and crash reports while respecting your users'
privacy. In addition to getting reports, you get to be [GDPR](https://gdpr-info.eu/)-compliant from
day one.

Humbug is currently available in the following programming languages:

1. [Python](./python)

   - System information report
   - Error traceback report
   - Packages available in the current Python process report
   - Logs report
   - Environment variables report
   - Custom report with full content control

2. [Go](./go)

   - System information report
   - Panic report
   - Custom report with full content control

3. [Javascript](./javascript)

   - System information report
   - Error traceback report

If you would like support for another programming language, please [create an issue](https://github.com/bugout-dev/humbug/issues/new).

---

## Using Humbug

### Setup

Follow the instructions in the [Getting started with usage and crash reporting](https://bugout.dev/app/public/d550eb09-7c85-4fdc-b687-9f04b730f6e1/07b21356-2e3f-4fa9-bd77-764fe903a640) guide.

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
