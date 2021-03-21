package humbug

import (
	"time"

	bugout "github.com/bugout-dev/bugout-go/pkg"
)

type Report struct {
	Title   string
	Tags    []string
	Content string
}

type Reporter interface {
	Tags() []string
	Publish(Report) error
	SetTimeout(time.Duration)
}

type HumbugReporter struct {
	clientID          string
	sessionID         string
	consent           Consent
	bugoutClient      bugout.BugoutClient
	bugoutAccessToken string
	bugoutJournalID   string
	tags              []string
}

func (reporter HumbugReporter) Tags() []string {
	return []string{}
}
