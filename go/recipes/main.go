package main

import (
	"os"

	humbug "github.com/bugout-dev/humbug/go/pkg"
)

func main() {
	consent := humbug.CreateHumbugConsent(humbug.True)

	clientID := "test-client"
	sessionID := "test-session"

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
