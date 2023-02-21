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

You can follow the recipes below to integrate Humbug into your codebase:

1. [Error reporting](./recipes/error_reporting.py)
1. [System reporting](./recipes/system_reporting.py)

All reports are generated (and published) by a Humbug reporter. By default, Humbug publishes all
reports asynchronously and in the background. If you would like to publish selected reports
synchronously, all reporter methods take a `wait=True` argument.

If you plan to _only_ use a reporter synchronously or to do your own thread management, you can
instantiate the reporter in synchronous mode:

```python
from humbug.report import Reporter, Modes

reporter = Reporter(
    "<name>",
    client_id="<client_id>",
    session_id="<session_id>",
    bugout_token="<bugout_token>",
    bugout_journal_id="<bugout_journal_id>",
    mode=Modes.SYNCHRONOUS,
)
```

Using Modes.SYNCHRONOUS in this manner skips the creation of the thread from which the reporter
publishes reports.

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
    bugout_token="<your Bugout token>",
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

### Blacklisting parameters in feature reports

Arguments to functions and other callables can sometimes contain sensitive information which you may
not want to include in Humbug reports.

Blacklist functions allow you to specify which parameters from an argument list to filter out of your
feature reports.

#### `blacklist.generate_filter_parameters_by_key_fn`

If you would just like to filter out all paramters with a given name, you can use the `blacklist.generate_filter_parameters_by_key_fn`.

For example, to ignore all parameters named `token` (case insensitive), you would instantiate your
`HumbugReporter` as follows:

```python
reporter = HumbugReporter(
    ...,
    blacklist_fn=blacklist.generate_filter_parameters_by_key_fn(["token"]),
)
```

#### Custom blacklist functions

You could also implement a custom blacklist function to remove all parameters that contained the substring
`token` (case insensitive):

```python
def blacklist_token_parameters_fn(params: Dict[str, Any]) -> Dict[str, Any]:
    admissible_params = {k:v for k, v in params.items() if "token" not in k}
    return admissible_params

reporter = HumbugReporter(
    ...,
    blacklist_fn=blacklist_token_parameters_fn
)
```

### Case study: activeloopai/deeplake

[This pull request](https://github.com/activeloopai/deeplake/pull/624) shows how
[Activeloop](https://www.activeloop.ai/) integrated Humbug into their popular
[`deeplake`](https://github.com/activeloopai/deeplake) tool.

This example shows how to use Humbug to record consent in a configuration file that the user
can modify at will. It also shows how to add custom tags to your Humbug reports.
