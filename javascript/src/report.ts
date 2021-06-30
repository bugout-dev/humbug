/*
This module implements all Humbug methods related to generating reports and publishing them to
Bugout knowledge bases.
*/
import axios, { AxiosInstance } from "axios"

import { generateSystemInformation, SystemInformation } from "./information"
import HumbugConsent from "./consent"


type Report = {
    title: string
    content: string
    tags: string[]
}

export default class Reporter {
    private clientAPI: AxiosInstance

    systemInformation: SystemInformation

    constructor(
        public name: string,
        public consent: HumbugConsent,
        public clientId?: string,
        public sessionId?: string,
        public bugoutToken?: string,
        systemInformation?: SystemInformation
    ) {
        this.clientAPI = axios.create({ baseURL: "https://spire.bugout.dev" })

        if (systemInformation === undefined) {
            this.systemInformation = generateSystemInformation()
        } else {
            this.systemInformation = systemInformation
        }
    }

    private systemTags(): string[] {
        const tags: string[] = [
            "humbug",
            `source:${this.name}`,
            `os:${this.systemInformation.os}`,
            `arch:${this.systemInformation.arch}`,
            `node:${this.systemInformation.nodeVersion}`,
            `session:${this.sessionId}`
        ]
        if (this.clientId !== undefined) {
            tags.push(`client:${this.clientId}`)
        }
        return tags
    }
    /**
     * Publish given report to bugout.dev
     * @param report Report to publish
     */
    async publish(report: Report): Promise<any> {
        if (this.consent.check() === false) {
            return null
        }
        if (this.bugoutToken === undefined) {
            return null
        }

        const publishURL = "/humbug/reports"
        const headers = {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${this.bugoutToken}`
        }
        const data = {
            title: report.title,
            content: report.content,
            tags: report.tags,
        }
        try {
            return await Promise.all<any>(
                [this.clientAPI.post(publishURL, JSON.stringify(data), { headers })]
            )
        } catch { return null }
    }

    /**
     * Sends report to bugout.dev with system information,
     * includes os and node params
     * @param tags optional tags to include in report
     * @param publish flag, will not be published if not set true
     */
    async systemReport(
        tags?: string[], publish: boolean = true
    ): Promise<Report> {
        const time = new Date().toISOString()
        const title = `${this.name} - System information`
        const content =
            `
### User timestamp
\`\`\`
${time}
\`\`\`

### OS
\`\`\`
${this.systemInformation.os}
\`\`\`

Release: \`${this.systemInformation.os_release}\`

### Processor
\`\`\`
${this.systemInformation.arch}
\`\`\`

### Node.js
\`\`\`
${this.systemInformation.nodeVersion}
\`\`\`
`

        const report: Report = { title, content, tags: this.systemTags() }
        if (tags !== undefined) {
            report.tags.push(...tags)
        }
        report.tags.push(...["type:system"])

        if (publish) {
            await this.publish(report)
        }

        return report
    }
    /**
     * Publish caught error to bugout.dev
     * @param error error that is cought
     * @param tags  optional reports to include in the report
     * @param publish flag, will not be published if not set true
     */
    async errorReport(
        error: Error, tags?: string[], publish: boolean = true
    ): Promise<Report> {
        const time = new Date().toISOString()
        const title = `${this.name} - ${error.name}`
        const content =
            `
### User timestamp
\`\`\`
${time}
\`\`\`

### Exception summary
\`\`\`
${error.message}
\`\`\`

### Traceback
\`\`\`
${error.stack}
\`\`\`
`
        const report: Report = { title, content, tags: this.systemTags() }
        if (tags !== undefined) {
            report.tags.push(...tags)
        }
        report.tags.push(...["type:error", `error:${error.name}`])
        if (publish) {
            await this.publish(report)
        }

        return report
    }

}

export { HumbugConsent as HumbugConsent }
