package humbug;

/**
 * Represents system information and JVM properties
 */
public abstract class SystemInformation {
    private final String os;
    private final String os_release;
    private final String arch;
    private final String java_version;
    private final String java_vm_name;

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
        String os = System.getProperty("os.name");
        String arch = System.getProperty("os.arch");
        String os_release = System.getProperty("os.version");
        String java_vm_name = System.getProperty("java.vm.name");
        String java_version = System.getProperty("java.version");

        return new SystemInformation(os,  os_release, arch, java_vm_name, java_version) {};
    }

}
