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

	report := humbug.Report{
		Title:   "test",
		Tags:    []string{"test"},
		Content: "This is a test",
	}

	reporter.Publish(report)
}
