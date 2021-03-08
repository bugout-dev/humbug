# humbug

If you build tools for programmers, you can use Humbug to understand what your users are
experiencing.

From basic system information to crash reports, Humbug helps you understand what keeps users coming
back to your product as well as any friction they experience.

Humbug lets you collect this information while respecting your users' privacy. In addition to
getting reports, you get to be [GDPR](https://gdpr-info.eu/)-compliant from day one.

Humbug is currently available in the following programming languages:

1. [Python](./python)
2. Go (coming soon)
3. Javascript (coming soon)

If you would like support for another programming language, please
[create an issue](https://github.com/bugout-dev/humbug/issues/new).

---

## Using Humbug

### Trying it out

Humbug is a frontend for Bugout.dev, a knowledge base for software teams. Humbug reports feed into
your project's Bugout knowledge base. To use Humbug, you will need to register for a (free) account
at https://bugout.dev.

Once you have created an account, go to your [`tokens`](https://bugout.dev/account/tokens) page and
generate an access token that you can use to try out Humbug.

[Create a journal](https://bugout.dev/journals). This will be the knowledge base that Humbug streams
reports into.

Then, follow the integration instructions for your favorite programming language to start generating
reports:

1. [Python](./python/README.md#integration)
2. Go (coming soon)
3. Javascript (coming soon)

### Taking Humbug to production

We are automating the process of adding Humbug to your production releases. If you would like to
reach your users with Humbug, please reach out to [Neeraj](mailto:neeraj@bugout.dev). He will get
you set up. It is a 5-minute manual process at the moment.

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
