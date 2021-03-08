# Humbug Python

The Humbug Python library.

## Installation

### Using pip

```bash
pip install humbug
```

### From source

Clone this repository and enter this directory. Make sure you are in your desired Python environment
and then run:

```bash
python setup.py install
```

## Integration

To add Humbug to your project, first create a Bugout access token and journal [following these
instructions](../README.md#trying-it-out).

All reports are generated (and published) by a Humbug reporter. Create a file called `report.py`
somewhere in your project and paste the following code in there:

```python
from humbug.consent import HumbugConsent
from humbug.report import Reporter

consent = HumbugConsent(True)
reporter = Reporter(
    "<name of your project>",
    consent,
    bugout_token="<your Bugout access token>",
    bugout_journal_id="<your Bugout journal ID>",
)
```

Now, anywhere in your code, import this report object and use it to publish reports to your
Bugout journal.

For example, to report an error:

```python
def do_something(*args):
    try:
        something(*args)
    except Exception as e:
        reporter.error_report(e)
```

If you want to report system information when a user imports your package, put the following code
in your `__init__.py`:

```python
from .report import reporter

reporter.system_report()
```

All reports have three parameters: `title`, `tags`, `content`. You can create a custom report using
the `humbug.report.Report` class, and you can publish it to your knowledge base using the
`humbug.report.Reporter.publish` method:

```
from humbug.report import Report

report = Report(
    title="<title of report>",
    tags=["report:custom", "test"],
    content="# Custom report\nThis is an example of a custom report, with markdown content.\n",
)
reporter.publish(report)
```

By default, Humbug publishes all reports asynchronously and in the background. If you would like to
publish reports synchronously, set `wait=True` on `error_report`, `system_report`, or `publish`.

For example, to publish the error report from above synchronously:

```python
def do_something(*args):
    try:
        something(*args)
    except Exception as e:
        reporter.error_report(e, wait=True)
```

### Consent

Humbug cares deeply about consent. The innocuous `HumbugConsent` from the snippet above supports
a wide range of consent flows.

#### Opting in with environment variables

For example, if you would like your users to be able to opt in by setting an environment variable
`MY_APP_CONSENT=true`:

```python
from humbug.consent import environment_variable_opt_in, HumbugConsent
from humbug.report import Reporter

consent = HumbugConsent(environment_variable_opt_in("MY_APP_CONSENT", ["true"]))
reporter = Reporter(
    "<name of your project>",
    consent,
    bugout_token="<your Bugout access token>",
    bugout_journal_id="<your Bugout journal ID>",
)
```

If you use this configuration, unless your user uses your tool with `MY_APP_CONSENT=true`, no
reports will ever get sent to your knowledge base.

#### Opting out with environment variables

If, [like `homebrew`](https://docs.brew.sh/Analytics#opting-out), you would like users to be able to
opt out by setting an environment variable `MY_APP_NO_CONSENT=1`:

```python
from humbug.consent import environment_variable_opt_out, HumbugConsent
from humbug.report import Reporter

consent = HumbugConsent(environment_variable_opt_out("MY_APP_NO_CONSENT", ["1"]))
reporter = Reporter(
    "<name of your project>",
    consent,
    bugout_token="<your Bugout access token>",
    bugout_journal_id="<your Bugout journal ID>",
)
```

In this case, reports are sent by default unless the user sets `MY_APP_NO_CONSENT=1` in which
case reports will never be sent.

#### Composing consent mechanisms

Humbug allows you to combine multiple consent mechanisms. For example:

```python
from humbug.consent import environment_variable_opt_in, environment_variable_opt_out, HumbugConsent
from humbug.report import Reporter

consent = HumbugConsent(
    environment_variable_opt_in("MY_APP_CONSENT", ["true"]),
    environment_variable_opt_out("MY_APP_NO_CONSENT", ["1"]),
)
reporter = Reporter(
    "<name of your project>",
    consent,
    bugout_token="<your Bugout access token>",
    bugout_journal_id="<your Bugout journal ID>",
)
```

If your users do not set `MY_APP_CONSENT` or give it a value other than `true`, Humbug won't even
bother to send you any reports. If `MY_APP_CONSENT` is indeed set to `true`, but the user has
set `MY_APP_NO_CONSENT=1`, then again no reports will get sent back.

On the other hand, if the user has set `MY_APP_CONSENT=true` and left `MY_APP_NO_CONSENT` unset or
set to a value other than `1`, Humbug will send you any reports you have configured.

### Example: activeloopai/Hub

[This pull request](https://github.com/activeloopai/Hub/pull/624) shows how
[Activeloop](https://www.activeloop.ai/) integrated Humbug into their popular
[`Hub`](https://github.com/activeloopai/Hub) tool.

This example shows how to use Humbug to record consent in a configuration file that the user
can modify at will. It also shows how to add custom tags to your Humbug reports.
