package com.bugout.humbug;

/**
 * Represents system information and JVM properties
 */
public class SystemInformation {
    private final String os;
    private final String os_release;
    private final String arch;
    private final String java_version;
    private final String java_vm_name;

    public SystemInformation() {
        this(
                System.getProperty("os.name"),
                System.getProperty("os.arch"),
                System.getProperty("os.version"),
                System.getProperty("java.vm.name"),
                System.getProperty("java.version")
        );
    }

    public SystemInformation(String os, String os_release, String arch, String java_vm_name, String java_version) {
        this.os = os;
        this.os_release = os_release;
        this.arch = arch;
        this.java_version = java_version;
        this.java_vm_name = java_vm_name;
    }

    public String getOs() {
        return os;
    }

    public String getOs_release() {
        return os_release;
    }

    public String getArch() {
        return arch;
    }

    public String getJava_version() {
        return java_version;
    }

    public String getJava_vm_name() {
        return java_vm_name;
    }

    public static SystemInformation generateSystemInformation() {
        return new SystemInformation();
    }

}
