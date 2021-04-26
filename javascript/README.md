# Humbug JavaScript

The Humbug JavaScript library.

## Installation

### Using npm

```bash
npm install --save humbug
```

### From source

Clone this repository and enter this directory. Make sure you have node.js installed and then build javascript library from typescript:
```bash
npm install --save typescript axios
npm install --save-dev tslint @types/node
npm run build
```

## Integrations

Prepare Humbug and fill your token API key:
```javascript
import Reporter from 'bugout-humbug'
import Reporter, HumbugConsent from 'humbug'

const BUGOUT_TOKEN = "06a1a299-c6b4-4709-8ac5-650d5e78e53e"
const BUGOUT_KB_ID = "6a1817c7-9500-4e38-9ab7-ffd858422036"
```

Instantiate the reporter:
```javascript
const consent = HumbugConsent(true)
const reporter = new Reporter(
    "<name>", 
    consent, 
    "<client_id>", 
    "<session_id>", 
    BUGOUT_TOKEN, 
    BUGOUT_KB_ID
)
```

### Unhandled exceptions with process.on

```javascript
tags = ["app_version"]

process.on('uncaughtException', err => {
    console.error('There was an uncaught error', err)
    reporter.systemReport(tags, true)
    reporter.errorReport(err, tags, true)
})
```

### Your customized exceptions

Add to your PersonalError class `errorReport`:
```javascript
class PersonalError extends Error {
    constructor(err: Error) {
        reporter.errorReport(err, [version], true)
        super()
    }
```
