/*
This module implements methods related to retrieving information about
the user's operating system, computer, and Node.js runtime.
*/
import * as os from 'os'
import * as process from 'process'


export type SystemInformation = {
    os: string
    os_release: string
    arch: string
    nodeVersion: string
}

export function generateSystemInformation(): SystemInformation {
    const systemInfo: SystemInformation = {
        os: os.platform(),
        os_release: os.release(),
        arch: os.arch(),
        nodeVersion: process.versions.node
    }
    return systemInfo
}
