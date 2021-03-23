package main

import (
	"os"

	humbug "github.com/bugout-dev/humbug/go/pkg"
)

func main() {
	// RECIPE: The consent flow here is an opt-out flow in which a user can set the RECIPE_REPORTING_ENABLED
	// environment variable to 0, "no", "false", "f", or "n" to signify that they opt out of reporting.
	// If a user has opted out, no reports will be published to the backend. Otherwise, publication is
	// attempted.
	consent := humbug.CreateHumbugConsent(humbug.EnvironmentVariableConsent("RECIPE_REPORTING_ENABLED", humbug.No, true))

	clientID := "test-client"
	sessionID := "test-session"

	// You can get this access token and journal ID by following the setup instructions at:
	// https://github.com/bugout-dev/humbug
	// In short, you have to create a "Bugout Usage Reports" integration to get these parameters.
	// There is no need to define them as environment variables. If you want, you can just hard-code
	// them here.
	bugoutAccessToken := os.Getenv("BUGOUT_ACCESS_TOKEN")
	bugoutJournalID := os.Getenv("BUGOUT_JOURNAL_ID")

	reporter, _ := humbug.CreateHumbugReporter(consent, clientID, sessionID, bugoutAccessToken, bugoutJournalID)
	// RECIPE: This is how you record panics from your go routines.
	defer func() {
		message := recover()
		if message != nil {
			report := humbug.PanicReport(message)
			reporter.Publish(report)
			// recovery code goes here
		}
	}()

	// RECIPE: This is how you record system information
	report := humbug.SystemReport()

	reporter.Publish(report)

	// And now we panic to show how the panic is reported.
	panic("OH NOES!!!")
}
