package humbug

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
)

defaultBaseUrl = "https://spire.bugout.dev"

type reportRequest struct {
	Title       string   `json:"title"`
	Content     string   `json:"content"`
	Tags        []string `json:"tags"`
}

type Reporter interface {
	Tag(key string, modifier string)
	Untag(key string, modifier string)
	Tags() []string
	Publish(report Report) error
}

type HumbugReporter struct {
	clientID          string
	sessionID         string
	consent           Consent
	bugoutAccessToken string
	tags              map[string]bool
}

func (reporter *HumbugReporter) Tag(key, modifier string) {
	if reporter.tags == nil {
		reporter.tags = make(map[string]bool)
	}
	tag := key
	if modifier != "" {
		tag = fmt.Sprintf("%s:%s", key, modifier)
	}
	reporter.tags[tag] = true
}

func (reporter *HumbugReporter) Untag(key, modifier string) {
	if reporter.tags == nil {
		reporter.tags = make(map[string]bool)
	}
	tag := key
	if modifier != "" {
		tag = fmt.Sprintf("%s:%s", key, modifier)
	}
	reporter.tags[tag] = false
}

func (reporter *HumbugReporter) Tags() []string {
	tags := make([]string, len(reporter.tags))
	i := 0
	for tag, value := range reporter.tags {
		if value {
			tags[i] = tag
			i++
		}
	}
	return tags[:i]
}

func MergeTags(tags0, tags1 []string) []string {
	tagSet := make(map[string]bool)
	for _, tag := range tags0 {
		tagSet[tag] = true
	}
	for _, tag := range tags1 {
		tagSet[tag] = true
	}
	mergedTags := make([]string, len(tagSet))
	i := 0
	for tag := range tagSet {
		mergedTags[i] = tag
		i++
	}
	return mergedTags
}

func (reporter *HumbugReporter) Publish(report Report) error {
	defer func() {
		// TODO(zomglings): For now, we only recover here so panicked Publish calls do not have an
		// effect on any program using the Humbug library. In the future, there should be an option
		// of writing log messages if an environment variable (e.g. HUMBUG_LOG_LEVEL) has been
		// set appropriately.
		recover()
	}()
	var err error
	userHasConsented := reporter.consent.Check()
	if userHasConsented {
		tags := MergeTags(report.Tags, reporter.Tags())
		entriesRoute := ("%s/humbug/reports", reporter.baseUrl)
		requestBody := reportRequest{
			{
			Title:   report.title,
			Content: report.content,
			Tags:    report.tags,
		}
		requestBuffer := new(bytes.Buffer)
		encodeErr := json.NewEncoder(requestBuffer).Encode(requestBody)
		
		if encodeErr != nil {
			return Entry{}, encodeErr
		}
		request, requestErr := http.NewRequest("POST", entriesRoute, requestBuffer)
		if requestErr != nil {
			return Entry{}, requestErr
		}
		request.Header.Add("Content-Type", "application/json")
		request.Header.Add("Accept", "application/json")
		request.Header.Add("Authorization", fmt.Sprintf("Bearer %s", reporter.token))
	
		response, responseErr := client.HTTPClient.Do(request)

	}
	return responseErr
}

func CreateHumbugReporter(baseUrl string, consent Consent, clientID string, sessionID string, bugoutAccessToken string) (*HumbugReporter, error) {
	reporter := HumbugReporter{
		consent:           consent,
		clientID:          clientID,
		sessionID:         sessionID,
		bugoutAccessToken: bugoutAccessToken
	}

	reporter.Tag("session", sessionID)
	if baseUrl != "" {
		reporter.baseUrl := baseUrl
	} else {
		reporter.baseUrl := defaultBaseUrl
	}
	if clientID != "" {
		reporter.Tag("client", clientID)
	}
	return &reporter, nil
}
