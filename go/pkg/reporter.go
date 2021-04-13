package humbug

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

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
	BaseURL           string
	clientID          string
	sessionID         string
	consent           Consent
	reporterToken     string
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

func (reporter *HumbugReporter) Publish(report Report) {
	defer func() {
		// TODO(zomglings): For now, we only recover here so panicked Publish calls do not have an
		// effect on any program using the Humbug library. In the future, there should be an option
		// of writing log messages if an environment variable (e.g. HUMBUG_LOG_LEVEL) has been
		// set appropriately.
		recover()
	}()
	userHasConsented := reporter.consent.Check()
	if userHasConsented {
		tags := MergeTags(report.Tags, reporter.Tags())
		entriesRoute := fmt.Sprintf("%s/humbug/reports", reporter.BaseURL)
		requestBody := reportRequest{
			Title:   report.Title,
			Content: report.Content,
			Tags:    tags,
		}
		requestBuffer := new(bytes.Buffer)
		json.NewEncoder(requestBuffer).Encode(requestBody)

		request, _ := http.NewRequest("POST", entriesRoute, requestBuffer)

		client := &http.Client{}
		request.Header.Add("Content-Type", "application/json")
		request.Header.Add("Accept", "application/json")
		request.Header.Add("Authorization", fmt.Sprintf("Bearer %s", reporter.reporterToken))
	
		client.Do(request)

	}
}
func (reporter *HumbugReporter) SetBaseURL(baseURL string) {
    reporter.BaseURL = baseURL
}

func CreateHumbugReporter(consent Consent, clientID string, sessionID string, reporterToken string) (*HumbugReporter, error) {
	reporter := HumbugReporter{
		consent:           consent,
		clientID:          clientID,
		sessionID:         sessionID,
		reporterToken:     reporterToken,
	}
	reporter.Tag("session", reporter.sessionID)
	if reporter.BaseURL == "" {
		reporter.BaseURL = "https://spire.bugout.dev"
	}

	if reporter.clientID != "" {
		reporter.Tag("client", reporter.clientID)
	}
	return &reporter, nil
}
